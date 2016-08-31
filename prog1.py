import numpy as np
from scipy.io.wavfile import write
from subprocess import call
from copy import deepcopy
import matplotlib.pyplot as plt

class Sound:
	Rate=44100#fs
	
	frequency=440#Hz
	frequencyy=440#Hz
	
	MAX=32767#max value of an int16 number
	
	length=2 #s
	
	Amplitude=1#values from 0 to 1
	
	def __init__(self,frequency1=frequency,frequency2=frequencyy,duration=length*1000,amplitude=Amplitude,rate=Rate):
		self.rate=rate
		self.frequency1=frequency1
		self.frequency2=frequency2
		self.duration=duration
		self.amplitude=amplitude
		#arr=np.linspace(0,int(self.frequency1*self.duration/1000)*2*np.pi,self.rate*self.duration/1000)
		#arr1=np.linspace(0,int(self.frequency2*self.duration/1000)*2*np.pi,self.rate*self.duration/1000)
		if not frequency1:
			if not frequency2:
				self.sound=np.int16(np.reshape(np.zeros(2*int(self.rate*self.duration/1000)),(2,-1)).T)
			else:
				arr=np.reshape(np.append(np.zeros(int(self.rate*self.duration/1000)),np.linspace(0,int(self.frequency1*self.duration/1000)*2*np.pi,self.rate*self.duration/1000)),(2,-1)).T
				arr[:,1]=np.sin(arr[:,1]*Sound.MAX*amplitude)
				self.sound=np.int16(arr)
		elif not frequency2:
			arr=np.reshape(np.append(np.linspace(0,int(self.frequency1*self.duration/1000)*2*np.pi,self.rate*self.duration/1000)),np.zeros(int(self.rate*self.duration/1000)),(2,-1)).T
			arr[:,2]=np.sin(arr[:,2]*Sound.MAX*amplitude)
			self.sound=np.int16(arr)
		else:
			arr=np.reshape(np.append(np.linspace(0,int(self.frequency2*self.duration/1000)*2*np.pi,self.rate*self.duration/1000),np.linspace(0,int(self.frequency1*self.duration/1000)*2*np.pi,self.rate*self.duration/1000)),(2,-1)).T
			self.sound=np.int16(np.sin(arr)*Sound.MAX*amplitude)
	
	def __add__(self,oldsound,time=0):#adds created sound on the end of the old sound
		temp=self
		temp.sound=np.append(self.sound,oldsound.sound,axis=0)
		temp.frequency1=None
		temp.frequency2=None
		temp.amplitude=np.amax(temp.sound)/Sound.MAX
		temp.duration=self.duration+oldsound.duration
		return temp
	def __radd__(self,other):
		try:
			if not other.size:#in case somebody tries to add a blank array
				return self
			else:
				return self.__add__(other)
		except AttributeError:
			try:
				if not other.sound.size:#in case somebody tries to add an empty sound
					return self
				else:
					return self.__add__(other)		
			except AttributeError:
				if not other:
					return self
				else:
					print("Unfortunately, the operation didn't succeed")
	"""def __deepcopy__(self, memo):
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result
		for k, v in self.__dict__.items():
			setattr(result, k, deepcopy(v, memo))
		return result"""
	
	def Write(self,path,rrate=None):#writes the sound into a file
		if rrate is None:
			rrate=self.rate
		write(path,rrate,self.sound)
	
	def add(self,nsound):#sums up two sounds
		if self.sound.shape==nsound.sound.shape:
			self.sound=np.float32(self.sound)+np.float32(nsound.sound)
			self.amplitude=np.amax(self.sound)/Sound.MAX#because the signal is sinusoidal and therefore has to be symmetrical in respect to the time axis
			self.frequency1=None
			self.frequency2=None
			return self
		else:
			print("Error: The sounds must have the same rate and duration")
	def radd(self,oldsound,time=0):#adds two sounds so that somewhere on the ''middle'' of the new sound will be the common signal from both sounds (''oldsound'' variable actually represents a ''newer'' sound)
			if not time:
				print("You should better use the __add__ function")
			if not self.sound.size or not oldsound.sound.size:#if at least one of sounds is empty it returns their arrays' logical summ
				temp=deepcopy(self)
				temp.sound = np.array(list(self.sound) or list(oldsound.sound))
				return temp
			elif time>self.sound.size/(2*self.rate)*1000:#in case the self.duration is not assigned correctly, if the older sound is too short
				temp=deepcopy(oldsound)
				temp.sound=temp.sound[:round(time*oldsound.rate/1000)]
				temp.add(self)
				temp.normalize()
				temp.sound=np.append(temp.sound,oldsound.sound[round(time*oldsound.rate/1000):],axis=0)
				return temp
			else:
				temp=deepcopy(self)
				temp.sound=temp.sound[-round(time*self.rate/1000):]
				temp1=deepcopy(oldsound)
				temp1.sound=temp1.sound[:round(time*oldsound.rate/1000)]
				tempsound=temp.add(temp1)
				del(temp1)
				tempsound.normalize()
				temp.sound=np.append(self.sound[:-round(time*self.rate/1000)],tempsound.sound,axis=0)
				temp.sound=np.append(temp.sound,oldsound.sound[round(time*oldsound.rate/1000):],axis=0)
				temp.duration=temp.sound.size/(2*temp.rate)*1000
				return temp
	
	def normalize(self,amplitude=1):#normalizes the sound (i.e. their amplitudes to the int16 format) after it was somehow changed
		if (np.amax(self.sound))>Sound.MAX:
			self.sound[:,0]=self.sound[:,0]*Sound.MAX*amplitude/max(self.sound[:,0])
		if (np.amax(self.sound))>Sound.MAX:
			self.sound[:,1]=self.sound[:,1]*Sound.MAX*amplitude/max(self.sound[:,1])
		self.sound=np.int16(self.sound)
		self.amplitude=np.amax(self.sound)/Sound.MAX
	def Play(self,time=None,stopat=0,startat=0):#plays a sound (or first ''time'' ms of the sound) (NB! may work only on Linux platforms)
		#print("Warning: the procedure may work only on Linux platforms")
		if time is None:
			self.Write("lkvnslmslcmnkjdfgc.wav")
		elif time<0:
			temp=Sound(0,0,0)
			temp.sound=np.copy(self.sound[round(time*self.rate/1000):round(stopat*self.rate/1000)]) if stopat else self.sound[round(time*self.rate/1000):]
			temp.Write("lkvnslmslcmnkjdfgc.wav")
		elif time>0:
			temp=Sound(0,0,0)
			temp.sound=self.sound[round(startat*self.rate/1000):round(time*self.rate/1000)]
			temp.Write("lkvnslmslcmnkjdfgc.wav")
		call(["aplay", "-q", "lkvnslmslcmnkjdfgc.wav"])
		call(["rm", "-f", "lkvnslmslcmnkjdfgc.wav"])
			
			
	def __str__(self):
		return "<Stereo Sound object with the 1st channel frequency={} and second channel frequency={}, duration of {} ms, number of rates equal to {} and with \"{}\" amplitude amplification>".format(self.frequency1,self.frequency2,self.duration,self.rate,self.amplitude)
	def __mul__(self,a):
		temp=deepcopy(self)
		temp.sound=np.tile(self.sound,(a,1))
		temp.duration*=a
		return temp
	__rmul__=__mul__



def areasound(area,dur,amp=0.1,coef=0.025,amin=None):
	if amin is None:
		freq=1092*np.exp(-coef*area)+82
	else:
		freq=1092*np.exp(coef*(amin-area))+82
	return Sound(freq,freq,dur,amp)
"""
a=Sound()
b=Sound(200,200)
c=a.radd(b,500)
plt.plot(c.sound[:,0])
plt.show()
"""
