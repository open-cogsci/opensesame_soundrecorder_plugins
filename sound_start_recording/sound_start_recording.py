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
import os.path
import imp

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
		self.version = 0.1

		self.recording = "Yes"
		self.channels = "Mono"
		self.bitrate = "44100"
		self.output_file = os.path.join("subject_[subject_nr]","[count_trial_sequence]")
		self.exp = experiment

		# Provide a short accurate description of the items functionality
		self.description = "Sound recorder plugin for OpenSesame"

		# The parent handles the rest of the contruction
		item.item.__init__(self, name, experiment, string)


	def prepare(self):
		# Make sure only one instance of sound recorder records at the same time
		if hasattr(self.exp,"soundrecorder") and self.exp.soundrecorder.is_recording():
			raise exceptions.runtime_error("Sound recorder already running")
		
		path = os.path.join(os.path.dirname(__file__), "Soundrecorder.py")
		soundrecorder = imp.load_source("Soundrecorder", path)

		output_file = self.get("output_file")
		if self.get("channels") == "Mono":
			channels = 1
		elif self.get("channels") == "Stereo":
			channels = 2
		bitrate = self.get("bitrate")
		
		
		if self.recording == "Yes":
			self.soundrecorder = soundrecorder.Soundrecorder(output_file, channels, bitrate)
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
		self.add_combobox_control("bitrate", "Bit rate", ["44100","22050","11025"], \
			tooltip = "Bitrate of recording (higher is better quality)")
		self.add_line_edit_control("output_file", "Output Folder/File", tooltip = "Path to output file")
		
		self.add_text("<small><b>Sound recorder OpenSesame plug-in v%.2f</b></small>" % self.version)

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


