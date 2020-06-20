
import ujson
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
				"1": {
					"mode": "static",
					"pin": 26,
					"size": 7,
					"color": (100, 0, 0)
				}
			}
		}
	@staticmethod
	def init():
		try:
			from _settings import DATA
			Config.data = DATA
			return True
		except Exception:
			Config.data = Config.defaults
			return False

	@staticmethod
	def write():
		s = open("_settings.py", "w")
		if s:
			s.write("DATA=")
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
	def getAll():
		return ujson.dumps(Config.data)
