
try:
	import m5stack
	import m5ui
except Exception:
	pass

class Status:
	@staticmethod
	def init():
		m5stack.lcd.clear(0x000000)
		m5stack.lcd.orient(m5stack.lcd.LANDSCAPE)
		Status.loglabel = m5ui.M5TextBox(0, 0, "", m5stack.lcd.FONT_Ubuntu, 0xffffff, rotate=0)
		Status.statusheader = m5ui.M5TextBox(0, 45, "", m5stack.lcd.FONT_Ubuntu, 0xffffff, rotate=0)
		Status.statuslabel = m5ui.M5TextBox(0, 55, "", m5stack.lcd.FONT_Ubuntu, 0xffffff, rotate=0)
		Status.iplabel = m5ui.M5TextBox(0, 66, "", m5stack.lcd.FONT_Ubuntu, 0xffffff, rotate=0)
		m5stack.lcd.font(m5stack.lcd.FONT_Ubuntu, fixedwidth=True)
		Status.statusheader.setText("FaWiHtSeLe")
		Status.flags = {
			"inFactoryreset": " ",
			"inSensors": " ",
			"inHttpRequest": " ",
			"wifiConnected": " ",
			"inLeds": " "
		}
		Status.inMeasure = "scan"
		Status.log("Init")

	@staticmethod
	def log(msg=False, inFactoryreset=False, inHttpRequest=False, inSensors=False, wifiConnected=False, ip=False, inLeds=False):
		m5stack.lcd.font(m5stack.lcd.FONT_Ubuntu, fixedwidth=False)
		if msg:
			print(msg)
			Status.loglabel.setText(msg)
		if ip:
			Status.iplabel.setText(ip)
		m5stack.lcd.font(m5stack.lcd.FONT_Ubuntu, fixedwidth=True)
		if inFactoryreset:
			Status.flags["inFactoryreset"] = inFactoryreset
		if inHttpRequest:
			Status.flags["inHttpRequest"] = inHttpRequest
		if inSensors:
			Status.flags["inSensors"] = inSensors
		if inLeds:
			Status.flags["inLeds"] = inLeds
		if wifiConnected:
			Status.flags["wifiConnected"] = wifiConnected

		Status.statuslabel.setText("%s %s %s %s %s" % (Status.flags["inFactoryreset"], Status.flags["wifiConnected"], Status.flags["inHttpRequest"], Status.flags["inSensors"], Status.flags["inLeds"]))

