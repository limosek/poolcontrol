# System libraries
import machine
import utime
import ujson

try:
	import usocket as socket
except:
	import socket
import gc
import ntpclient
import os

# Local files to import
from status import Status
from config import Config
from wifi import Wifi
from http import HTTP
from sensors import Sensors
from leds import Leds
from relays import Relays


######################## Main

def init():
	gc.enable()
	Status.init()
	if not Config.init():
		Config.factoryReset()
	Config.init()
	Wifi.init()
	Leds.init()
	Sensors.init()
	Relays.init()
	if Config.getParam("time", "ntp"):
		i = 1
		try:
			while i < 5 and not ntpclient.settime(Config.getParam("time", "ntp"), Config.getParam("time", "offset")):
				Status.log("Getting time from NTP... (%s)" % i)
				i += 1
			rtc = machine.RTC()
			t = rtc.datetime()
		except Exception:
			t = utime.localtime(0)
	else:
		t = utime.localtime(0)
	Status.log('Date: {:04d}.{:02d}.{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6]))
	# Init timer
	tim = machine.Timer(0)
	tim.init(period=50, mode=machine.Timer.PERIODIC, callback=tick50mS())


def mainloop():
	Leds.tick50mS()
	if Status.inMeasure == "scan":
		Sensors.scan()
		Status.inMeasure = "idle"
	elif Status.inMeasure == "start":
		Sensors.startMeassure()
		Status.inMeasure = "idle"
	elif Status.inMeasure == "read":
		Sensors.readTemp()
		Status.inMeasure = "idle"

def tick50mS():
	ms = utime.ticks_ms()
	if (ms % 1000) <= 50:
		tick1S()

def tick1S():
		seconds = machine.RTC().datetime()[4]
		if (seconds % 4) == 0:
			Status.inMeasure = "scan"
		elif 	(seconds % 4) == 2:
			Status.inMeasure = "start"
		elif (seconds % 4) == 3:
			Status.inMeasure = "read"

def main():
	Status.log('Runnning HTTP server')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 80))
	s.settimeout(1)
	s.listen(5)

	while True:
		Status.log(inHttpRequest=" ")
		try:
			conn, addr = s.accept()
			HTTP.init(conn, addr)
		except:
			mainloop()
			continue
		Status.log('Got a connection from %s' % (str(addr)), inHttpRequest="o")

		if not HTTP.Valid:
			HTTP.error(400, "Bad request")
			continue

		if Status.flags["inFactoryreset"] == "!" and HTTP.checkRequest('/'):
			if HTTP.checkRequest('/setup'):
				HTTP.redirect("/setup")

		if HTTP.checkRequest('/'):
			HTTP.home()

		if HTTP.checkRequest('/setup'):
			HTTP.setup()
		elif HTTP.checkRequest('/setup', method='POST'):
			Status.log("Setup POST page")
			try:
				cfg = HTTP.getRequestVar("cfg")
				json = HTTP.urlDecode(cfg)
				json = ujson.loads(json)
				Config.load(json)
				Config.write()
				HTTP.OK("Setup OK")
				machine.reset()
			except ValueError:
				HTTP.error(400, "Bad JSON")

		elif HTTP.checkRequest('/flowui', method='GET'):
			Status.log("Reverting to flowUI")
			try:
				s = os.remove("boot.py")
				HTTP.OK("Reverted to FlowUI.")
				machine.reset()
			except ValueError:
				HTTP.error(400, "Cannot remove boot.py")

		elif HTTP.checkRequest('/factory-defaults', method='GET'):
			Status.log("Reverting to factory Defaults")
			try:
				s = os.remove("_settings.py")
				HTTP.OK("Factory defaults done.")
				machine.reset()
			except ValueError:
				HTTP.error(400, "Cannot remove _settings.py")

		elif HTTP.checkRequest('/push-file', method='POST'):
			file = HTTP.getRequestVar("file")
			if file:
				HTTP.begin(200, ctype="text/plain", html=False)
				HTTP.send(file)
				HTTP.end(html=False)
				continue
				if data:
					Status.log("Writing file %s" % file)
					s = open(file, "w")
					s.write(data)
					HTTP.OK("File written OK", msg=data)
					continue
			HTTP.error(400, "Bad request")

		# /led/set/<stripe>/<led>/<color>
		# /led/set/0/1/ffffff
		elif HTTP.checkRequest('/led/set'):
			stripe = HTTP.getRequestVar("stripe")
			led = HTTP.getRequestVar("led")
			color = HTTP.getRequestVar("color")
			if color and Leds.setColor(stripe, led, Leds.fromHtml(color)):
				HTTP.OK()
			else:
				HTTP.error(400, "Error in request")

		else:
			HTTP.error(404, "Not found")


init()
main()
