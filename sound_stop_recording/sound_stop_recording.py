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

__author__ = "Daniel Schreij"
__license__ = "GPLv3"

class sound_stop_recording(item.item):

	"""
	This class (the class with the same name as the module)
	handles the basic functionality of the item. It does
	not deal with GUI stuff.
	"""

	def __init__(self, name, experiment, string = None):
		"""
		Constructor
		"""
		self.item_type = "sound_stop_recording"
		self.exp = experiment

		# Provide a short accurate description of the items functionality
		self.description = "Stop sound recording"
		# The parent handles the rest of the contruction
		item.item.__init__(self, name, experiment, string)


	def prepare(self):
		# Call parent functions.
		item.item.prepare(self)
		
		return True

	def run(self):
		# Record the timestamp of the plug-in execution.
		self.set_item_onset()
		
		if hasattr(self.exp,"soundrecorder"):
			self.exp.soundrecorder.stop()
		else:
			raise exceptions.runtime_error("No sound being recorded. Unable to stop recording")
		return True

class qtsound_stop_recording(sound_stop_recording, qtplugin.qtplugin):
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
		sound_stop_recording.__init__(self, name, experiment, string)
		qtplugin.qtplugin.__init__(self, __file__)

	def init_edit_widget(self):
		
		"""
		This function creates the controls for the edit
		widget.
		"""
		qtplugin.qtplugin.init_edit_widget(self, False)
		
		# Add a stretch to the edit_vbox, so that the controls do not
		# stretch to the bottom of the window.
		self.edit_vbox.addStretch()

	def apply_edit_changes(self):

		"""
		Set the variables based on the controls
		"""
		
		# Report success
		return True

	def edit_widget(self):

		"""
		Set the controls based on the variables
		"""
		return self._edit_widget


