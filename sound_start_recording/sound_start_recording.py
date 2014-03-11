# -*- coding: utf-8 -*-
"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""
__author__ = "Daniel Schreij"
__license__ = "GPLv3"

# Import OpenSesame specific items
from libopensesame import item
from libqtopensesame.items.qtautoplugin import qtautoplugin

# The `osexception` class is only available as of OpenSesame 2.8.0. If it is not
# available, fall back to the regular `Exception` class.
try:
	from libopensesame.exceptions import osexception
except:
	osexception = Exception
	
import os
import re
import imp
import pyaudio


class sound_start_recording(item.item):

	"""
	This class (the class with the same name as the module)
	handles the basic functionality of the item. It does
	not deal with GUI stuff.
	"""

	def __init__(self, name, experiment, string = None):
		"""
		Constructor. 

		Arguments:
		name -- the name of the item
		experiment -- the opensesame experiment

		Keyword arguments:
		string -- a definition string for the item (Default = None)
		"""
	
		# Enumerate audio devices
		pa = pyaudio.PyAudio()
		# Get default audio device for input
		default_device = pa.get_default_input_device_info()
														
		self.item_type = "sound_start_recording"
		self.version = 1.0

		self.recording = "Yes"
		self.input_device = default_device["name"]
		self.channels = "Mono"
		self.samplerate = "44100"		
		self.output_file = "default"
		self.compression = "None (wav)"
		self.file_exists_action = "Overwrite"
		self.exp = experiment

		# Provide a short accurate description of the items functionality
		self.description = "Sound recorder plugin for OpenSesame"

		# The parent handles the rest of the contruction
		item.item.__init__(self, name, experiment, string)

	
	def _generate_suffix(self,path_to_file):		
		"""
		Function that creates a suffix for a filename, taking into account previous suffixes

		Arguments:
		path_to_file -- the path to the file to create the suffix for.
		"""
		pattern = "_[0-9]+$"		
		(filename,ext) = os.path.splitext(path_to_file)
				
		# Keep increasing suffix number if file with the current suffix already exists
		filename_exists = True
		while filename_exists:
			match = re.search(pattern, filename)						
			if match:					
				no = int(filename[match.start()+1:])+1
				filename = re.sub(pattern,"_"+str(no),filename)			
			else:			
				filename = filename + "_1"
			
			new_filename = filename + ext			
			if not os.path.exists(new_filename):
				filename_exists = False
									
		return new_filename
		
		
	def prepare(self):
		# Make sure only one instance of sound recorder records at the same time
		if hasattr(self.exp,"soundrecorder") and self.exp.soundrecorder.is_recording():
			raise osexception("Sound recorder already running")
		
		# Load Soundrecorder class
		path = os.path.join(os.path.dirname(__file__), "Soundrecorder.py")
		soundrecorder = imp.load_source("Soundrecorder", path)
				
		# Create real recorder or dummy recorder (which just passes everything to empty functions)
		if self.recording == "Yes":
			# Process attributes
			if self.get("channels") == "Mono":
				channels = 1
			elif self.get("channels") == "Stereo":
				channels = 2
			
			samplerate = self.get("samplerate")
			
			compression = self.get("compression")
			if compression == "None (wav)":
				filetype = "wav"
			elif compression == "MP3":
				filetype = "mp3"
			# Not yet supported, bug in pymedia when saving ogg files
			elif compression == "Ogg Vorbis":
				filetype = "ogg"
				
			# Make output location relative to location of experiment
			rel_loc = os.path.normpath(self.get("output_file"))						
			
			if self.exp.experiment_path is None:
				raise osexception("Path to experiment not found. Please save the experiment to a file first")
			
			output_file = os.path.normpath(os.path.join(self.exp.experiment_path,rel_loc))						
	
			# Make sure file extension corresponds to audio type
			extension = os.path.splitext(output_file)[1]
			if extension != "":
				ext = extension[1:]
				if ext != filetype:
					output_file += "." + filetype	
			else:
				output_file += "." + filetype
	
			# Check for a subfolder (when it is specified) that it exists and if not, create it
			if os.path.exists(os.path.dirname(output_file)):
				if self.file_exists_action == "Append suffix to filename":
					# Search for underscore/number suffixes								
					output_file = self._generate_suffix(output_file)										
			else:
				if os.path.dirname(rel_loc) != "":
					try:				
						os.makedirs(os.path.dirname(output_file))
					except Exception as e:
						raise osexception.runtime_error("Error creating sound file: " + str(e))
			print output_file

			self.soundrecorder = soundrecorder.Soundrecorder(self.input_device, output_file, channels, samplerate, filetype)
		else:
			self.soundrecorder = soundrecorder.DummyRecorder()
			
		self.exp.cleanup_functions.append(self.soundrecorder.stop)
		return True


	def run(self):
		# Make sure only one instance of sound recorder records at the same time
		if hasattr(self.exp,"soundrecorder") and self.exp.soundrecorder.is_recording():
			raise osexception("Sound recorder already running. Please make sure only one instance of sound recorder is recording at the same time")		
		
		# Make this sound recorder the current sound recorder for sound_stop_recording to operate on later.
		self.exp.soundrecorder = self.soundrecorder
		
		# Start recording
		self.exp.soundrecorder.record()
		return True


class qtsound_start_recording(sound_start_recording, qtautoplugin):
	"""
	This class (the class named qt[name of module] handles
	the GUI part of the plugin. For more information about
	GUI programming using PyQt4, see:
	<http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>
	"""

	def __init__(self, name, experiment, string = None):
		
		"""
		Constructor
		"""

		# Pass the word on to the parents
		sound_start_recording.__init__(self, name, experiment, string)
		qtautoplugin.__init__(self, __file__)

	def init_edit_widget(self):
		
		"""
		This function creates the controls for the edit
		widget.
		"""

		# Lock the widget until we're doing creating it
		self.lock = True
		
		# Pass the word on to the parent
		qtautoplugin.init_edit_widget(self)
		
		# Enumerate audio devices
		pa = pyaudio.PyAudio()
		# Get number of present audio devices
		no_of_devices = pa.get_device_count()
		# Get default audio device for input
		default_device = pa.get_default_input_device_info()
			
		# Create a list of available audio devices
		# Make sure the default one is at the top of the list
		input_devices = []
		for i in range(0,no_of_devices):
			# Get current device info
			dev = pa.get_device_info_by_index(i)
						
			# Check if device is for input
			if dev["maxInputChannels"] > 0:
				# If device is system's default, put at top of list
				if dev == default_device:
					input_devices.insert(0,dev)
				else:					
					input_devices.append(dev)

		# Extract names from dictionary
		input_devices = [str(ip["name"]) for ip in input_devices]	

		self.input_device_selector.addItems(input_devices)		
				
		# Unlock
		self.lock = False

	def apply_edit_changes(self):
		
		"""Applies changes to the controls."""
		
		qtautoplugin.apply_edit_changes(self)
		return True


