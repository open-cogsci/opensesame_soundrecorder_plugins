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
		return True

	def run(self):
		if hasattr(self.exp,"soundrecorder"):
			self.exp.soundrecorder.stop()
			del(self.exp.soundrecorder)
		else:
			raise osexception("No sound being recorded. Unable to stop recording")
		return True

class qtsound_stop_recording(sound_stop_recording, qtautoplugin):

	"""
	This class (the class named qt[name of module] handles
	the GUI part of the plugin. For more information about
	GUI programming using PyQt4, see:
	<http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html>
	"""

	def __init__(self, name, experiment, script = None):

		"""
		Constructor.
		
		Arguments:
		name		--	The item name.
		experiment	--	The experiment object.
		
		Keyword arguments:
		script		--	The definition script. (default=None).
		"""

		# Pass the word on to the parents
		sound_stop_recording.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)

	def apply_edit_changes(self):
		
		"""Applies changes to the controls."""
		
		qtautoplugin.apply_edit_changes(self)
		return True


