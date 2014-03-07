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

# Import OpenSesame specific items
from libopensesame import item, debug, generic_response
from libqtopensesame.items.qtautoplugin import qtautoplugin
# The `osexception` class is only available as of OpenSesame 2.8.0. If it is not
# available, fall back to the regular `Exception` class.
try:
	from libopensesame.exceptions import osexception
except:
	osexception = Exception
	
	
import os
import sys
import imp
import time
import threading
import wave
	
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
	import pygst
	pygst.require("0.10")
	import gst
except:
	raise osexception("OpenSesame could not find the GStreamer framework!")


class Soundrecorder(threading.Thread):
	def __init__(self, output_file="default.wav", channels=2, samplerate=44100, filetype="wav"):
		self.output_file = output_file
		self.channels = int(channels)
		self.samplerate = int(samplerate)
		self.filetype = filetype
		self._recording = False
		self._allowed_filetypes = ["wav","mp3"] #ogg to be added
		
		threading.Thread.__init__ ( self )
		
		if os.name == "nt":
			import pyaudio
			pa = pyaudio.PyAudio()
			no_of_devices = pa.get_device_count()
			input_device = "  "
		else:
			input_device = "autoaudiosrc"
			
		if filetype == "wav":
			conversion =  "  "
		elif filetype == "mp3":
			conversion =  "  "
			
		file_saving = "filesink location=" + output_file			
		
		self.pipeline = gst.parse_launch(input_device + " ! " + conversion + " ! " + file_saving ) 
                                               
		

	def run(self):
		if self.filetype in self._allowed_filetypes:	
			if self.filetype == "wav":
				self._writeToWave()
			else:		
				self._encode(self.filetype)
		else:
			raise Exception("Illegal sound file type")
			
		
	def _writeToWave(self):		
		recorded = []
		self._recording = True
		self.input.start()
		while self._recording:
			s = self.input.getData()
			if s and len(s):
				recorded.append(s)
			else:
				time.sleep(0.03)
				
		self.input.stop()
		data = ''.join(recorded)
		
		wf = wave.open(self.output_file, 'wb')
		wf.setparams( (self.channels, 2, self.samplerate, 0, 'NONE','') )
		wf.writeframes(data)
		wf.close()
		
		
	def _encode(self,filetype):
		cparams= { 	'id': acodec.getCodecID( filetype ),
				'bitrate': 128000,
				'sample_rate': self.samplerate,
				'channels': self.channels 
		} 	
							
		out_fp = open(self.output_file, 'wb')
		ac = acodec.Encoder( cparams )									
		
		self._recording = True
		self.input.start()
		while self._recording:
			s = self.input.getData()
			if s and len(s):
				for fr in ac.encode(s):
					out_fp.write(fr)
			else:
				time.sleep(0.03)
		self.input.stop()
		

	def stop(self):
		self._recording = False


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
