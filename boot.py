
# System libraries
import machine
import utime
try:
	import usocket as socket
except:
	import socket
import gc
import ntpclient

gc.collect()

# Local files to import
from status import Status
from config import Config
from wifi import Wifi
from http import HTTP
from sensors import Sensors
from leds import Leds

######################## Main

Status.init()
#if not Config.init():
Config.factoryReset()
Config.init()
Wifi.init()
Leds.init()
Sensors.init()
if Config.getParam("time", "ntp"):
	i=1
	try:
		while i<5 and not ntpclient.settime(Config.getParam("time", "ntp"), Config.getParam("time", "offset")):
			Status.log("Getting time from NTP... (%s)" % i)
			i += 1
		rtc=machine.RTC()
		t = rtc.datetime()
	except Exception:
		t = utime.localtime(0)
else:
	t = utime.localtime(0)
Status.log('Date: {:04d}.{:02d}.{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6]))

def mainloop():
	Leds.write()
	Sensors.scan()
	Status.log("Timeout")

def timerTick(timer):
	Status.loops += 1
	t = rtc.datetime()
	print("timerTick %s, %s" % (Status.loops, 'Date: {:04d}.{:02d}.{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])))
	if (Status.loops % 2) == 0:
		Sensors.startMeassure()
	if (Status.loops % 2) == 1:
		Sensors.readTemp()
	if Status.loops>pow(2,15):
		Status.loops = 0

# Init timer
#tim = machine.Timer(0)
#tim.init(period=1000, mode=machine.Timer.PERIODIC, callback=timerTick)

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
		HTTP.OK(HTTP.urlDecode(HTTP.getPostData()))

  # /led/set/<stripe>/<led>/<color>
	# /led/set/0/1/ffffff
	elif HTTP.checkRequest('/led/set'):
		stripe = HTTP.getRequestVar("stripe")
		led = HTTP.getRequestVar("led")
		color = HTTP.getRequestVar("color")
		if color and leds.setColor(stripe, led, Leds.fromHtml(color)):
			HTTP.OK()
		else:
			HTTP.error(400, "Error in request")

	else:
		HTTP.error(404, "Not found")
