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
# The `osexception` class is only available as of OpenSesame 2.8.0. If it is not
# available, fall back to the regular `Exception` class.
try:
	from libopensesame.exceptions import osexception
except:
	osexception = Exception
	
import os
import sys

if os.name == "nt":
	if hasattr(sys,"frozen") and sys.frozen in ("windows_exe", "console_exe"):
		exe_path = os.path.dirname(sys.executable)
		os.environ["PATH"] = os.path.join(exe_path, "gstreamer", "dll") + ';' + os.environ["PATH"]
		os.environ["GST_PLUGIN_PATH"] = os.path.join(exe_path, "gstreamer", "plugins")
		sys.path.append(os.path.join(exe_path, "gstreamer", "python"))		
	else:
		os.environ["PATH"] = os.path.join(os.environ["GSTREAMER_SDK_ROOT_X86"],"bin") + ';' + os.environ["PATH"]
		sys.path.append(os.path.join(os.environ["GSTREAMER_SDK_ROOT_X86"],"lib","python2.7","site-packages"))
if os.name == "posix" and sys.platform == "darwin":
	# For OS X
	# When installed with the GStreamer SDK installers from GStreamer.com
	sys.path.append("/Library/Frameworks/GStreamer.framework/Versions/Current/lib/python2.7/site-packages")
		
# Try to load Gstreamer
try:
	import gobject
	import pygst
	pygst.require("0.10")
	import gst
except:
	raise osexception("OpenSesame could not find the GStreamer framework!")


class Soundrecorder():
	"""
	Constructor. 

	Arguments:
	input device -- the ID string of the device to record from

	Keyword arguments:
	output_file -- the path to the file to save the recording to. (Default = default.wav)
	channels -- the number of channels to record with (1 or 2, Default = 2)
	samplerate -- the default samplerate to record with (44100, 22050 or 11025, Default = 44100)
	filetype -- the type of compression to apply (or none at all) (wav, ogg or mp3, Default = wav)	
	"""
	
	def __init__(self, inputdevice, output_file="default.wav", channels=2, samplerate=44100, filetype="wav"):
		self.output_file = output_file
		self.channels = int(channels)
		self.samplerate = int(samplerate)
		self.filetype = filetype
		self._recording = False
		self._allowed_filetypes = ["wav","ogg"] #mp3 to be added
		
		if os.name == "nt":			
			input_device = 'dshowaudiosrc device-name="' + inputdevice + '"'
		else:
			input_device = 'autoaudiosrc'
			
		if filetype == "wav":
			conversion =  'audioconvert ! audioresample ! wavenc'
		elif filetype == "ogg":
			conversion =  "audioconvert ! audioresample ! vorbisenc ! oggmux"
			
		file_saving = 'filesink location="' + output_file + '"'			
			
		try:
			chain = input_device + ' ! ' + conversion + ' ! ' + file_saving
			print chain
			self.pipeline = gst.parse_launch( chain ) 
			self.pipeline.set_state(gst.STATE_READY)
		except Exception as e:
			raise osexception("The device failed to initialize: " + e)
                                               		
	def record(self):
		self._recording = True
		print "Starting recording"
		self.pipeline.set_state(gst.STATE_PLAYING)		
		
	def stop(self):
		if self._recording:
			self._recording = False
			self.pipeline.set_state(gst.STATE_PAUSED)	
			self.pipeline.set_state(gst.STATE_NULL)	
			print "Ended recording"

	def is_recording(self):
		return self._recording
		

class DummyRecorder():
	""" Dummy class that mimics the SoundRecorder class, but whose methods do nothing """
	def __init__(self):
		pass

	def run(self):
		pass

	def stop(self):
		pass
	
	def start(self):
		pass
	
	def is_recording(self):
		return False
