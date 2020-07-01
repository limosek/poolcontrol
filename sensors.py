
import machine
import onewire
import ubinascii
from config import Config
from status import Status

class Sensors():
	@staticmethod
	def init():
		sensors = Config.getParam("sensors")
		pin = sensors["onewire_pin"]
		Sensors.data = { "roms": {} }
		for s in sensors["roms"].keys():
			Sensors.addSensor(s, sensors["roms"][s]["rom"])
		Sensors.ow = onewire.OneWire(machine.Pin(pin))
		Sensors.ds = onewire.DS18X20(Sensors.ow)
		Status.log("Init sensors on pin %s" % pin)

	@staticmethod
	def getNextId():
		if len(Sensors.data["roms"])>0:
			nextid = max(Sensors.data["roms"].keys())+1
		else:
			nextid = 1
		return nextid

	@staticmethod
	def get(id):
		if id in Sensors.data["roms"]:
			return Sensors.data["roms"][id]
		else:
			return False

	@staticmethod
	def scan():
		roms = Sensors.ow.scan()
		for rom in roms:
			romid = "".join("%02x" % i for i in rom)
			found = False
			for s in Sensors.data["roms"].keys():
				if romid==Sensors.data["roms"][s]["rom"]:
					found = True
					continue
			if not found:
					nid = Sensors.getNextId()
					Sensors.addSensor(nid, romid)
					Status.log("Adding sensor %s[%s]" % (nid, Sensors.data["roms"][nid]["rom"]))
		for s in Sensors.data["roms"].keys():
			if (Status.loops-Sensors.data["roms"][s]["last"])>60:
				Status.log("Removing stale sensor %s[%s]" % (s, Sensors.data["roms"][s]["rom"]))
				Sensors.removeSensor(s)

	@staticmethod
	def getValue(id):
		if id in Sensors.data["roms"]:
			return Sensors.data["roms"][id]["T"]
		else:
			return None

	def addSensor(id, romid):
		Sensors.data["roms"][id] = {"T": None, "last": Status.loops, "rom": romid}
		Config.data["sensors"]["roms"][id] = {"name": None, "rom": romid}
		Status.log(inSensors=len(Sensors.data["roms"]))

	def removeSensor(id):
		del Sensors.data["roms"][id]
		del Config.data["sensors"]["roms"][id]
		Status.log(inSensors=len(Sensors.data["roms"]))

	def startMeassure(id="all"):
		Status.log(inSensors="M")
		if id=="all":
			for id in Sensors.data["roms"].keys():
				Sensors.startMeassure(id)
			return
		else:
			rom = ubinascii.unhexlify(Sensors.data["roms"][id]["rom"])
			Sensors.ds.start_conversion(rom)
		Status.log(inSensors=len(Sensors.data["roms"]))

	def readTemp(id="all"):
		Status.log(inSensors="R")
		if id=="all":
			for s in Sensors.data["roms"].keys():
				Sensors.readTemp(s)
		else:
			rom = ubinascii.unhexlify(Sensors.data["roms"][id]["rom"])
			try:
				t = Sensors.ds.read_temp_async(rom)
			except Exception:
				t = False
			if t and t>-100 and t<150:
				Sensors.data["roms"][id]["T"] = t
				Sensors.data["roms"][id]["last"] = Status.loops
				print("T[%s]=%s" % (id, t))
			else:
				Status.log(inSensors="!")
		Status.log(inSensors=len(Sensors.data["roms"]))
