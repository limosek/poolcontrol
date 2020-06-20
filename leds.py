
import status
import urandom
import math
import machine
import neopixel
from config import Config
from status import Status

class Leds():
	@staticmethod
	def init():
		Leds.data = Config.getParam("stripes")
		Leds.np = {}
		Leds.cnt = 0
		for s in Leds.data.keys():
			pin = Leds.data[s]["pin"]
			count = Leds.data[s]["size"]
			Leds.cnt += count
			mode = Leds.data[s]["mode"]
			color = Leds.data[s]["color"]
			Status.log("Init stripe %s on pin %s" % (s, pin))
			Leds.np[s] = neopixel.NeoPixel(machine.Pin(pin), count)
			Leds.np[s].fill(color)
			Leds.np[s].write()

	@staticmethod
	def write():
#		Status.log(inLeds="W")
		for s in Leds.data.keys():
			Leds.np[s].write()
		Status.log(inLeds=Leds.cnt)

	@staticmethod
	def fromHtml(color):
		if color[0] == "#":
			color = color[1:7]
		r = int(color[0:2], 16)
		g = int(color[2:4], 16)
		b = int(color[4:6], 16)
		return tuple(r,g,b)

	@staticmethod
	def toHtml(color):
		color = list(color)
		return "#%.2x%.2x%.2x" % (color[0], color[1], color[2])

	@staticmethod
	def setColor(stripe, led, color):
		if stripe in Leds.data and led<Leds.np[stripe].n:
				Leds.np[stripe][led] = color
				return True
		else:
			log("Bad stripe or led number")
			return False

	@staticmethod
	def getColor(stripe, led, html=False):
		if stripe in Leds.data and led<Leds.np[stripe].n:
			if html:
				t = list(Leds.np[stripe][led])
				return Leds.toHtml(t)
			else:
				return Leds.np[stripe][led]
		else:
			Status.log("Bad stripe or led number")
			return False

	@staticmethod
	def fadeOut(s, led="all", step=10, rgb="rgb"):
		if led=="all":
			for i in range(Leds.np[s].n):
				Leds.fadeOut(s, i, step, rgb)
		else:
			t = list(Leds.np[s][led])
			if rgb.find("r")!=-1:
				t[0] = t[0] - step
			if rgb.find("g")!=-1:
				t[1] = t[1] - step
			if rgb.find("b")!=-1:
				t[2] = t[2] - step
			if t[0]<0:
				t[0] = 0
			if t[0]>255:
				t[0] = 255
			if t[1]<0:
				t[1] = 0
			if t[1]>255:
				t[1] = 255
			if t[2]<0:
				t[2] = 0
			if t[2]>255:
				t[2] = 255
			Leds.np[s][led] = tuple(t)

	@staticmethod
	def fadeIn(s, led="all", step=10, rgb="rgb"):
		Leds.fadeOut(s, led, -1*step, rgb)

	@staticmethod
	def shiftLeft(s, color=(0,0,0)):
		tmp = list()
		for i in range(Leds.np[s].n):
			tmp.append(Leds.np[s][i])
		tmp.insert(-1, color)
		tmp.pop(0)
		for i in range(Leds.np[s].n):
			Leds.np[s][i] = tmp[i]

	@staticmethod
	def shiftRight(s, color=(0,0,0)):
		tmp = list()
		for i in range(Leds.np[s].n):
			tmp.append(Leds.np[s][i])
		tmp.insert(0, color)
		tmp.pop(-1)
		for i in range(Leds.np[s].n):
			Leds.np[s][i] = tmp[i]

	@staticmethod
	def random(s, bits=8, base=0):
		for i in range(Leds.np[s].n):
			Leds.np[s][i] = (urandom.getrandbits(bits)+base, urandom.getrandbits(bits)+base, urandom.getrandbits(bits)+base)

	@staticmethod
	def wave(s, start, end, period, phase=0, amp=255, rgb="rgb"):
		step = (2*math.pi)/period
		if rgb.find("r")!=-1:
			for i in range(0, end-start):
				r = int(math.sin((i+phase)*step)*amp)
				tmp = list(Leds.np[s][start+i])
				tmp[0] = r
				Leds.np[s][start + i] = tuple(tmp)

	@staticmethod
	def print(s):
		for i in range(Leds.np[s].n):
			Status.log(Leds.np[s][i])
