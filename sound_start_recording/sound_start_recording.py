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

from libopensesame import item, exceptions, debug
from libqtopensesame import qtplugin
import os
import re
import imp

# Already try to import required libraries, otherwise the error might occur
# in the other (Soundrecorder) thread and not be caught
try:
	import pymedia.audio.sound as sound
	import pymedia.audio.acodec as acodec
	import wave
except Exception as e:
	exceptions.runtime_error("Failed to import required library: " + str(e))
	

__author__ = "Daniel Schreij"
__license__ = "GPLv3"

class sound_start_recording(item.item):

	"""
	This class (the class with the same name as the module)
	handles the basic functionality of the item. It does
	not deal with GUI stuff.
	"""

	def __init__(self, name, experiment, string = None):
		"""
		Constructor
		"""
		self.item_type = "sound_start_recording"
		self.version = 0.13

		self.recording = "Yes"
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
			raise exceptions.runtime_error("Sound recorder already running")
		
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
						raise exceptions.runtime_error("Error creating sound file: " + str(e))						

			self.soundrecorder = soundrecorder.Soundrecorder(output_file, channels, samplerate, filetype)
		else:
			self.soundrecorder = soundrecorder.DummyRecorder()
			
		self.exp.cleanup_functions.append(self.soundrecorder.stop)
		return True


	def run(self):
		# Make sure only one instance of sound recorder records at the same time
		if hasattr(self.exp,"soundrecorder") and self.exp.soundrecorder.is_recording():
			raise exceptions.runtime_error("Sound recorder already running. Please make sure only one instance of sound recorder is recording at the same time")		
		
		# Make this sound recorder the current sound recorder for sound_stop_recording to operate on later.
		self.exp.soundrecorder = self.soundrecorder
		
		# Start recording
		self.exp.soundrecorder.start()
		return True


class qtsound_start_recording(sound_start_recording, qtplugin.qtplugin):
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
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):
		
		"""
		This function creates the controls for the edit
		widget.
		"""

		# Lock the widget until we're doing creating it
		self.lock = True

		# Pass the word on to the parent
		qtplugin.qtplugin.init_edit_widget(self, False)
		self.add_combobox_control("recording", "Record sound", ["Yes","No"], \
			tooltip = "Indicates if sound should be recorded (No for test-runs)")
		self.add_combobox_control("channels", "Channels", ["Mono","Stereo"], \
			tooltip = "Record in one or two channels")   
		self.add_combobox_control("samplerate", "Sample rate", ["44100","22050","11025"], \
			tooltip = "Sampler ate of recording (higher is better quality)")
		self.add_line_edit_control("output_file", "Output Folder/File", tooltip = "Path to output file")
		self.add_combobox_control("compression", "Compression", ["None (wav)", "MP3"], \
			tooltip = "Compression type of audio output")
		self.add_combobox_control("file_exists_action", "If file exists", ["Overwrite","Append suffix to filename"], \
			tooltip = "Choose what to do if the sound file already exists")
		self.add_text("<small><b>Sound recorder OpenSesame plug-in v%.2f, Copyright (2010-2012) %s </b></small>" % (self.version, __author__))

		# Add a stretch to the edit_vbox, so that the controls do not
		# stretch to the bottom of the window.
		self.edit_vbox.addStretch()

		# Unlock
		self.lock = False

	def apply_edit_changes(self):

		"""
		Set the variables based on the controls
		"""

		# Abort if the parent reports failure of if the controls are locked
		if not qtplugin.qtplugin.apply_edit_changes(self, False) or self.lock:
			return False

		# Refresh the main window, so that changes become visible everywhere
		self.experiment.main_window.refresh(self.name)

		# Report success
		return True

	def edit_widget(self):

		"""
		Set the controls based on the variables
		"""

		# Lock the controls, otherwise a recursive loop might aris
		# in which updating the controls causes the variables to be
		# updated, which causes the controls to be updated, etc...
		self.lock = True

		# Let the parent handle everything
		qtplugin.qtplugin.edit_widget(self)

		# Unlock
		self.lock = False

		# Return the _edit_widget
		return self._edit_widget


