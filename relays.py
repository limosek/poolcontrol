import machine
from status import Status
from config import Config
from sensors import Sensors

class Relays:
	@staticmethod
	def init():
		Relays.data = Config.getParam("relay")
		Status.log("Relays initialised (%s relays)." % len(Relay.data))

	@staticmethod
	def check():
		t = machine.RTC().datetime()
		for r in Relays.data.keys():
			rel = Relays.data[r]
			pin = machine.Pin(rel["pin"], machine.Pin.OUT)
			toreplace = {
				"dow": t[6],
				"hod": t[4],
				"moy": t[1],
				"year": t[0]
			}
			for s in Sensors.data["roms"].keys():
				toreplace["s%s" % s] = Sensors.getValue(s)
			si = rel["condition"]
			for r in toreplace.keys():
				si = si.replace("{%s}" % r, toreplace[r])
			Status.log("Eval condition: %s" % si)
			try:
				if eval(si):
					pin.value(1)
				else:
					pin.value(0)
			except Exception:
				Status.log("Bad condition!")
				pass
