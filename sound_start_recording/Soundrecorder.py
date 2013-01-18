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
import pyaudio
import wave
import threading

class Soundrecorder(threading.Thread):
	def __init__(self, output_file, channels=1, bitrate=44100):
		self.output_file = output_file
		self.channels = channels
		self.bitrate = bitrate
		self._format = pyaudio.paInt16
		self._chunk = 1024
		self._recording = False
		self.input = pyaudio.PyAudio()
		threading.Thread.__init__ ( self )

	def run(self):
		print "Starting thread"
		stream = self.input.open(format = self._format,
				channels = self.channels,
				rate = self.bitrate,
				input = True,
				frames_per_buffer = self._chunk)

		recorded = []
		self._recording = True
		while self._recording:
			recorded.append(stream.read(self._chunk))

		stream.close()
		self.input.terminate()

		# write data to WAVE file
		data = ''.join(recorded)

		wf = wave.open(self.output_file, 'wb')
		wf.setnchannels(self.channels)
		wf.setsampwidth(self.input.get_sample_size(self._format))
		wf.setframerate(self.bitrate)
		wf.writeframes(data)
		wf.close()

	def stop(self):
		self._recording = False

	def is_recording(self):
		return self._recording
		

class DummyRecorder():
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
