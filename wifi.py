import network
from status import Status
from config import Config

class Wifi():
	@staticmethod
	def Client():
		Wifi.wc = network.WLAN(network.STA_IF)
		Wifi.wc.active(True)
		Wifi.wc.connect(Config.getParam("network","ssid"), Config.getParam("network","wpa_password"))
		Status.log("Wifi: Connecting to %s" % (Config.getParam("network","ssid")))
		while Wifi.wc.isconnected() == False:
			pass
		ip = Wifi.wc.ifconfig()[0]
		Status.log("Wifi: Connected, ip:%s" % ip, wifiConnected="o", ip=ip)

	@staticmethod
	def AP():
		Wifi.wc = network.WLAN(network.AP_IF)
		Wifi.wc.active(True)
		Wifi.wc.config(essid=Config.getParam("network","ssid"), password=Config.getParam("network","wpa_password"))
		Wifi.wc.ifconfig((Config.getParam("network","ip"), Config.getParam("network","mask"), Config.getParam("network","gw"), Config.getParam("network","dns")))
		ip = Wifi.wc.ifconfig()[0]
		Status.log("Wifi: AP mode, essid:%s, ip:%s" % (Config.getParam("network","ssid"), ip), wifiConnected="A", ip=ip)

	@staticmethod
	def init():
		if Config.getParam("network", "mode")  == "AP":
			Wifi.AP()
		elif Config.getParam("network", "mode")  == "Client":
			Wifi.Client()

	@staticmethod
	def connected():
		return Wifi.wc.isconnected()
