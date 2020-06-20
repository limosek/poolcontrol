
import machine
import onewire
from config import Config
from status import Status
import sys

class Sensors():
	@staticmethod
	def init():
		Sensors.data = Config.getParam("sensors")
		pin  = Sensors.data["onewire_pin"]
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
				if romid==Sensors.data["roms"][s]["romid"]:
					found = True
					continue
			if not found:
					nid = Sensors.getNextId()
					Sensors.addSensor(nid, rom, romid)
					Status.log("Adding sensor %s[%s]" % (nid, Sensors.data["roms"][nid]["romid"]))
		for s in Sensors.data["roms"].keys():
			if (Status.loops-Sensors.data["roms"][s]["last"])>60:
				Status.log("Removing stale sensor %s[%s]" % (s, Sensors.data["roms"][s]["romid"]))
				Sensors.removeSensor(s)

	def addSensor(id, rom, romid):
		Sensors.data["roms"][id] = {"T": None, "last": Status.loops, "rom": rom, "romid": romid}
		Status.log(inSensors=len(Sensors.data["roms"]))

	def removeSensor(id):
		del Sensors.data["roms"][id]
		Status.log(inSensors=len(Sensors.data["roms"]))

	def startMeassure(id="all"):
		Status.log(inSensors="M")
		if id=="all":
			for s in Sensors.data["roms"].keys():
				Sensors.ds.start_conversion(Sensors.data["roms"][s]["rom"])
		else:
			Sensors.ds.start_conversion(Sensors.data["roms"][id]["rom"])
		Status.log(inSensors=len(Sensors.data["roms"]))

	def readTemp(id="all"):
		Status.log(inSensors="R")
		if id=="all":
			for s in Sensors.data["roms"].keys():
				t = Sensors.ds.read_temp_async(Sensors.data["roms"][s]["rom"])
				if t:
					Sensors.data["roms"][s]["T"] = t
					Sensors.data["roms"][s]["last"] = Status.loops
		else:
			t = Sensors.ds.read_temp_async(Sensors.data["roms"][id]["rom"])
			if t:
				Sensors.data["roms"][id]["T"] = t
				Sensors.data["roms"][id]["last"] = Status.loops
		Status.log(inSensors=len(Sensors.data["roms"]))
