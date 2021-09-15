import struct
import threading

import pyaudio
import wave

from config import BUFFER_SIZE,SAMPLING_RATE

audio=None
timer = None

def init():
	global  audio
	audio = pyaudio.PyAudio()
def quit():
	audio.terminate()
def __dummy():
	return
def _wait_timer():
	global timer
	if(timer != None):
		timer.join()
	timer = threading.Timer(BUFFER_SIZE / SAMPLING_RATE, __dummy)
	timer.start()

class DummyStream:
	def __init__(self):
		return
	def read(self):
		_wait_timer()
		return [0 for i in range(BUFFER_SIZE)]
	def close(self):
		return

#未実装
class MusicFileStream:
	def __init__(self, filename):
		self.wf = wave.open(filename, 'rb')
		self.__openStr()

	def __openStr(self):
		self.ostream = None
		try:
			get_device_count()
			self.ostream = audio.open(format=pyaudio.paFloat32,
						channels=1,
						rate=SAMPLING_RATE,
						output = True,
						)
			pass
		except OSError:
			print('No available output device!!')
			pass

	def read(self):
		if(self.ostream == None):
			self.__openStr()
			if(self.ostream == None):
				_wait_timer()
				return [0 for i in range(BUFFER_SIZE)]
		try:
			data = self.wf.readframes(BUFFER_SIZE)
			self.ostream.write(struct.pack('f' * int(len(data))))
			return data
		except IOError:
			self.ostream.close()
			self.ostream = None
			_wait_timer()
			return [0 for i in range(BUFFER_SIZE)]

	def close(self):
		if (self.ostream != None):
			self.ostream.stop_stream()
			self.ostream.close()

class MicStream:

	def __init__(self):
		self.__openStr()
		self.th = None

	def __openStr(self):
		self.istream = None
		try:
			self.istream = audio.open(format=pyaudio.paFloat32,
						channels=1,
						rate=SAMPLING_RATE,
						input = True,
						)
			pass
		except OSError:
			print('No available input device!!')
			pass

	def read(self):
		if(self.istream == None):
			self.__openStr()
			if(self.istream == None):
				_wait_timer()
				return [0 for i in range(BUFFER_SIZE)]
		try:
			data=self.istream.read(BUFFER_SIZE)
			data=struct.unpack('f' * int(len(data) / 4), data)
			return data
		except IOError:
			self.istream.close()
			self.istream = None
			_wait_timer()
			return [0 for i in range(BUFFER_SIZE)]

	def close(self):
		if (self.istream != None):
			self.istream.stop_stream()
			self.istream.close()