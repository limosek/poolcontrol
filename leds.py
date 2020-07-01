try:
	import urandom
	import machine
except Exception:
	import random as urandom

import math

from status import Status
from config import Config

# Copyright public licence and also I don't care.
# 2020 Josh "NeverCast" Lloyd.
from micropython import const
from esp32 import RMT

# The peripheral clock is 80MHz or 12.5 nanoseconds per clock.
# The smallest precision of timing requried for neopixels is
# 0.35us, but I've decided to go with 0.05 microseconds or
# 50 nanoseconds. 50 nanoseconds = 12.5 * 4 clocks.
# By dividing the 80MHz clock by 4 we get a clock every 50 nanoseconds.

# Neopixel timing in RMT clock counts.
T_0H = const(35 // 5)  # 0.35 microseconds / 50 nanoseconds
T_1H = const(70 // 5)  # 0.70 microseconds / 50 nanoseconds
T_0L = const(80 // 5)  # 0.80 microseconds / 50 nanoseconds
T_1L = const(60 // 5)  # 0.60 microseconds / 50 nanoseconds

# Encoded timings for bits 0 and 1.
D_ZERO = (T_0H, T_0L)
D_ONE = (T_1H, T_1L)

# [D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in channels for bit in range(num_bits - 1, -1, -1)]
# Reset signal is low for longer than 50 microseconds.
T_RST = const(510 // 5)  # > 50 microseconds / 50 nanoseconds

# Channel width in bits
CHANNEL_WIDTH = const(8)

class NeoPixel:
	def __init__(self, pin, pixel_count, rmt_channel=1, pixel_channels=3):
		self.rmt = RMT(rmt_channel, pin=pin, clock_div=4)
		# pixels stores the data sent out via RMT
		self.channels = pixel_channels
		single_pixel = (0,) * pixel_channels
		self.pixels = [D_ZERO * (pixel_channels * CHANNEL_WIDTH)] * pixel_count
		# colors is only used for __getitem__
		self.colors = [single_pixel] * pixel_count

	def write(self):
		# The bus should be idle low ( I think... )
		# So we finish low and start high.
		pulses = tuple()
		for pixel in self.pixels:
			pulses += pixel
		pulses += (T_RST,)  # The last low should be long.
		self.rmt.write_pulses(pulses, start=1)
		self.rmt.wait_done()

	def __setitem__(self, pixel_index, colors):
		self_colors = self.colors
		self_pixels = self.pixels
		if isinstance(pixel_index, int):
			# pixels[0] = (r, g, b)
			self_colors[pixel_index] = tuple(colors)
			self_pixels[pixel_index] = tuple(clocks for bit in
			                                 (D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in colors for bit in
			                                  range(CHANNEL_WIDTH - 1, -1, -1)) for clocks in bit)
		elif isinstance(pixel_index, slice):
			start = 0 if pixel_index.start is None else pixel_index.start
			stop = len(self.pixels) if pixel_index.stop is None else pixel_index.stop
			step = 1 if pixel_index.step is None else pixel_index.step
			# Assume that if the first colors element is an int, then its not a sequence
			# Otherwise always assume its a sequence of colors
			if isinstance(colors[0], int):
				# pixels[:] = (r,g,b)
				for index in range(start, stop, step):
					self_colors[index] = tuple(colors)
					self_pixels[index] = tuple(clocks for bit in
					                           (D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in colors for bit in
					                            range(CHANNEL_WIDTH - 1, -1, -1)) for clocks in bit)
			else:
				# pixels[:] = [(r,g,b), ...]
				# Assume its a sequence, make it a list so we know the length
				if not isinstance(colors, list):
					colors = list(colors)
				color_length = len(colors)
				for index in range(start, stop, step):
					color = colors[(index - start) % color_length]
					self_colors[index] = tuple(color)
					self_pixels[index] = tuple(clocks for bit in
					                           (D_ONE if ((channel >> bit) & 1) else D_ZERO for channel in color for bit in
					                            range(CHANNEL_WIDTH - 1, -1, -1)) for clocks in bit)
		else:
			raise TypeError('Unsupported pixel_index {} ({})'.format(pixel_index, type(pixel_index)))

	def __getitem__(self, pixel_index):
		# slice instances are passed through
		return self.colors[pixel_index]

	def __len__(self):
		return len(self.colors)


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
			Status.log("Init stripe %s on pin %s" % (s, pin))
			Leds.np[s] = NeoPixel(machine.Pin(pin), count)
			if "leds" in Leds.data[s]:
				for i in range(1, count):
					if i in Leds.data[s]["leds"]:
						Leds.np[s][i - 1] = tuple(Leds.fromHtml(Leds.data[s]["leds"][i]))
			Leds.np[s].write()
			if mode == "random":
				Leds.random(s)

	@staticmethod
	def write():
		Status.log(inLeds="o")
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
		return (r, g, b)

	@staticmethod
	def toHtml(color):
		color = list(color)
		return "#%.2x%.2x%.2x" % (color[0], color[1], color[2])

	@staticmethod
	def setColor(stripe, led, color):
		if stripe in Leds.data and led < len(Leds.np[stripe]):
			Leds.np[stripe][led] = color
			return True
		else:
			Status.log("Bad stripe or led number")
			return False

	@staticmethod
	def getColor(stripe, led, html=False):
		if stripe in Leds.data and led < len(Leds.np[stripe]):
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
		if led == "all":
			for i in range(len(Leds.np[s])):
				Leds.fadeOut(s, i, step, rgb)
		else:
			t = list(Leds.np[s][led])
			if rgb.find("r") != -1:
				t[0] = t[0] - step
			if rgb.find("g") != -1:
				t[1] = t[1] - step
			if rgb.find("b") != -1:
				t[2] = t[2] - step
			if t[0] < 0:
				t[0] = 0
			if t[0] > 255:
				t[0] = 255
			if t[1] < 0:
				t[1] = 0
			if t[1] > 255:
				t[1] = 255
			if t[2] < 0:
				t[2] = 0
			if t[2] > 255:
				t[2] = 255
			Leds.np[s][led] = tuple(t)

	@staticmethod
	def fadeIn(s, led="all", step=10, rgb="rgb"):
		Leds.fadeOut(s, led, -1 * step, rgb)

	@staticmethod
	def shiftLeft(s, color=(0, 0, 0)):
		tmp = list()
		for i in range(len(Leds.np[s])):
			tmp.append(Leds.np[s][i])
		tmp.insert(-1, color)
		tmp.pop(0)
		for i in range(len(Leds.np[s])):
			Leds.np[s][i] = tmp[i]

	@staticmethod
	def shiftRight(s, color=(0, 0, 0)):
		tmp = list()
		for i in range(len(Leds.np[s])):
			tmp.append(Leds.np[s][i])
		tmp.insert(0, color)
		tmp.pop(-1)
		for i in range(len(Leds.np[s])):
			Leds.np[s][i] = tmp[i]

	@staticmethod
	def random(s, bits=8, base=0):
		for i in range(len(Leds.np[s])):
			Leds.np[s][i] = (
				urandom.getrandbits(bits) + base, urandom.getrandbits(bits) + base, urandom.getrandbits(bits) + base)
		Leds.write()

	@staticmethod
	def wave(s, start, end, period, phase=0, amp=255, rgb="rgb"):
		step = (2 * math.pi) / period
		if rgb.find("r") != -1:
			for i in range(0, end - start):
				r = int(math.sin((i + phase) * step) * amp)
				tmp = list(Leds.np[s][start + i])
				tmp[0] = r
				Leds.np[s][start + i] = tuple(tmp)

	@staticmethod
	def getData(s):
		data = {}
		for l in range(1, len(Leds.np[s]) + 1):
			data[l] = Leds.getColor(s, l - 1, True)
		return data

	@staticmethod
	def tick50mS():
		Leds.write()
