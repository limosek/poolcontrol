
try:
	import ujson
except Exception:
	import json as ujson

import sys
from status import Status

class Config:
	defaults = {
			"sensors": {
				"onewire_pin": 0,
				"roms": {
				},
			},
			"network": {
				"mode": "Client",
				"ssid": "SPA",
				"wpa_password": "HtecVjA!3",
				"ip": "DHCP",
				"gw": "DHCP",
				"mask": "DHCP",
				"dns": "DHCP"
			},
			"time": {
				"ntp": "pool.ntp.org",
				"offset": 3600*2
			},
			"stripes": {
				1: {
					"mode": "random",
					"pin": 26,
					"size": 7
				}
			},
			"relays": {
				1: {
					"pin": 32,
					"condition": "{s1}>30} and {s2}<40 and {hod}>10 and {hod}<18"
				}
			}
		}
	@staticmethod
	def init():
		try:
			s = open("_settings.py", "r")
			if s:
				Config.data = ujson.loads(s.read(32768))
			for i in Config.data["stripes"].keys():
				stripedata = Config.data["stripes"][i]
				if "leds" in stripedata:
					for j in stripedata["leds"]:
						leddata = stripedata["leds"][j]
						del stripedata["leds"][j]
						stripedata["leds"][int(j)] = leddata
				del Config.data["stripes"][i]
				Config.data["stripes"][int(i)] = stripedata
			for i in Config.data["sensors"]["roms"].keys():
				romdata = Config.data["sensors"]["roms"][i]
				del Config.data["sensors"]["roms"][i]
				Config.data["sensors"]["roms"][int(i)] = romdata
			return True
		except Exception as e:
			Config.data = Config.defaults
			Status.log("Cannot read config file")
			sys.print_exception(e)
			return False

	@staticmethod
	def write():
		s = open("_settings.py", "w")
		if s:
			ujson.dump(Config.data, s)
			s.close()
		else:
			Status.log("Cannot save config!")

	@staticmethod
	def factoryReset():
		Status.log("Factory reset", inFactoryreset="!")
		Config.data = Config.defaults
		Config.write()

	@staticmethod
	def load(json):
		Status.log("Loading settings")
		Config.data = json

	@staticmethod
	def setParam(section, subsection, param, value):
		if section in Config.data:
			if subsection in Config.data[section]:
				Config.data[section][subsection][param] = value
				return True
		return False

	@staticmethod
	def getParam(section, param=None, subsection=None):
		if section in Config.data:
			if subsection:
				if subsection in Config.data[section]:
					if param:
						return [param]
					else:
						return Config.data[section][subsection]
			else:
				if param:
					return Config.data[section][param]
				else:
					return Config.data[section]
		return None

	@staticmethod
	def getAll(leds):
		data = Config.data
		for s in Config.data["stripes"].keys():
			data["stripes"][s] = Config.data["stripes"][s]
			data["stripes"][s]["leds"] = leds.getData(s)
		return ujson.dumps(data)
