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

import imp
import os
import sys
import time

try:
	import pymedia.audio.sound as sound
	import pymedia.audio.acodec as acodec
except:
	try:
		sys.path.append(os.getcwd())
		(f,p,d) = imp.find_module("pymedia",[os.path.dirname(__file__)])
		imp.load_module("pymedia",f,p,d)
		import pymedia.audio.sound as sound
		import pymedia.audio.acodec as acodec
	except Exception as e:
		raise e
	
import threading
import wave

class Soundrecorder(threading.Thread):
	def __init__(self, output_file="default.wav", channels=2, samplerate=44100, filetype="wav"):
		self.output_file = output_file
		self.channels = int(channels)
		self.samplerate = int(samplerate)
		self.filetype = filetype
		self._format = sound.AFMT_S16_LE
		self._recording = False
		self._allowed_filetypes = ["wav","mp3"] #ogg to be added
		
		self.input = sound.Input( self.samplerate, self.channels, self._format )					
		
		threading.Thread.__init__ ( self )
		

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
		self.input = None
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
		ac= acodec.Encoder( cparams )									
		
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
		self.input = None

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
		pass
