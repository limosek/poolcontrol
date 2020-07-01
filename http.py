from status import Status
from config import Config
from leds import Leds

class HTTP():
	@staticmethod
	def init(conn, addr):
		HTTP.conn = conn
		HTTP.ip = addr
		request = HTTP.conn.recv(16384)
		HTTP.data = request.decode("utf-8").replace("\r", "", 10000).split("\n")
		HTTP._parseRequest()
		if HTTP.Valid and HTTP.Method=='POST' and HTTP.getHeader("Content-Type").find("multipart/form-data")>=0:
			print("Multipart request. Reading body.")
			if (HTTP.getHeader("Expect")):
				HTTP.send("HTTP/1.1 100 Continue\r\n")
			#else:
			#	HTTP.begin(200, "OK", html=False)
			print("Reading...")
			HTTP.postdata = ""
			data = HTTP.conn.recv(32768)
			HTTP.postdata += data.decode("utf-8")
			while len(data)==32768:
				print("Reading...")
				data = HTTP.conn.recv(32768)
				HTTP.postdata += data.decode("utf-8")
			print(HTTP.postdata)
			HTTP.OK("OK")

	@staticmethod
	def urlDecode(s):
		ret = \
			s.replace("%20", " "). \
				replace("%0D", "\r"). \
				replace("%0A", "\n"). \
				replace("%09", "\t"). \
				replace("+", " "). \
				replace("%21", "!"). \
				replace("%22", "\""). \
				replace("%23", "#"). \
				replace("%24", "$"). \
				replace("%25", "%"). \
				replace("%26", "&"). \
				replace("%27", "\'"). \
				replace("%28", "("). \
				replace("%29", ")"). \
				replace("%30", "*"). \
				replace("%31", "+"). \
				replace("%2C", ","). \
				replace("%2E", "."). \
				replace("%2F", "/"). \
				replace("%2C", ","). \
				replace("%3A", ":"). \
				replace("%3B", ";"). \
				replace("%3C", "<"). \
				replace("%3D", "="). \
				replace("%3E", ">"). \
				replace("%3F", "?"). \
				replace("%40", "@"). \
				replace("%5B", "["). \
				replace("%5C", "\\"). \
				replace("%5D", "]"). \
				replace("%5E", "^"). \
				replace("%5F", "-"). \
				replace("%60", "`"). \
				replace("%7B", "{"). \
			  replace("%7D", "}")
		return ret

	@staticmethod
	def getMultiPart(data, name):
		print("multipart: %s" % data)
		ctype = HTTP.getHeader("Content-Type")
		if not ctype:
			return None
		bstart = ctype.find('boundary="')
		if not bstart:
			return None
		if bstart:
			boundary = "--" + ctype[bstart + 10:-1]
			sidx = data.find(boundary)
			bdata = data[sidx:]
			while sidx>0:
				eidx = bdata.find(boundary)
				print(bdata[:eidx])
				return bdata[:eidx]
				sidx = bdata.find(boundary)
				bdata = data[sidx:]

	@staticmethod
	def _parseRequest():
		midx = HTTP.data[0].find(" ")
		rest = HTTP.data[0][midx + 1:]
		if midx >= 0:
			HTTP.Method = HTTP.data[0][0:midx]
		else:
			Status.log("Bad HTTP request %s!" % HTTP.data[0])
			HTTP.Valid = False
		uidx = rest.find(" ")
		if uidx >= 0:
			HTTP.Uri = HTTP.urlDecode(rest[0:uidx])
		HTTP.Version = rest[uidx + 1:]
		ridx = HTTP.Uri.find("?")
		if ridx >= 0:
			HTTP.Request = HTTP.Uri[0:ridx]
			HTTP.Params = HTTP.Uri[ridx + 1:]
		else:
			HTTP.Request = HTTP.Uri
			HTTP.Params = ""
		HTTP.Valid = True

	@staticmethod
	def getRequestVar(var):
		if HTTP.Method == "POST" and HTTP.getHeader("Content-Type") == "application/x-www-form-urlencoded":
			HTTP.Params = HTTP.urlDecode(HTTP.getPostData())
			vars = HTTP.getPostData().split("&")
		elif HTTP.Method == "POST" and HTTP.getHeader("Content-Type").find("multipart/form-data")>=0:
			return HTTP.getMultiPart(HTTP.getPostData(), var)
		else:
			vars = HTTP.Params.split("&")
		for v in vars:
			avidx = v.find("=")
			if avidx > 0:
				an = v[0:avidx]
				av = v[avidx + 1:]
			else:
				an = v
				av = True
			if an == var:
				return av

	@staticmethod
	def checkRequest(uri, method="GET"):
		if HTTP.Method == method and HTTP.Request==uri:
			return True
		else:
			return False

	@staticmethod
	def getHeader(header):
		for h in HTTP.data[1:]:
			if h == "":
				return None
			else:
				ahidx = h.find(":")
				ah = h[0:ahidx]
				av = h[ahidx + 1:]
				if header.upper() == ah.upper():
					return av.lstrip()

	@staticmethod
	def sendHeader(header, value):
		HTTP.send("%s: %s\n" % (header, value))

	@staticmethod
	def send(data):
		try:
			HTTP.conn.sendall(data)
		except:
			Status.log("Error sending data")

	@staticmethod
	def begin(code, title, msg="OK", ctype="text/html", headers=None, flushheaders=True, html=True, bodyparams=""):
		HTTP.send('HTTP/1.1 %s %s\n' % (str(code), msg))
		if headers:
			for h in headers.keys():
				HTTP.sendHeader(h, headers[h])
		else:
			HTTP.sendHeader('Content-Type', ctype)
			HTTP.sendHeader('Connection', 'close')
			HTTP.sendHeader('Accept-Encoding:', '')
			HTTP.sendHeader('Accept-Charset', 'ascii')
			HTTP.sendHeader('Allow', 'GET, POST')
		if flushheaders:
			HTTP.send('\n')
			if html:
				with open("header.html") as f:
					html = f.read()
				HTTP.send(html.format(title=title, bodyparams=bodyparams))

	@staticmethod
	def end(html=True):
		if html:
			with open("footer.html") as f:
				html = f.read()
			HTTP.send(html)
		else:
			HTTP.send('')
		HTTP.conn.close()

	@staticmethod
	def redirect(new):
		HTTP.begin(301, "Redirect", headers={"Location": new})
		HTTP.end()

	@staticmethod
	def getPostData():
		headers = True
		data = ""
		for h in HTTP.data[1:]:
			if h == "" and headers:
				headers = False
				continue
			if not headers:
				data += h + "\n"
		return data

	@staticmethod
	def OK(msg="OK", html=True):
		Status.log("OK page")
		HTTP.begin(200, msg, html=html)
		HTTP.send(msg)
		HTTP.end(html=html)

	@staticmethod
	def home():
		Status.log("Home page")
		HTTP.begin(200, "BathControl home")
		HTTP.send("""
		Bath Control web interface
		""")
		HTTP.end()

	@staticmethod
	def error(code, msg):
		Status.log("Error page")
		HTTP.begin(code, "Error %s" % msg, msg=msg)
		HTTP.send(msg)
		HTTP.end()

	@staticmethod
	def setup():
		Status.log("Setup page")
		HTTP.begin(200, "Setup", bodyparams="onload=javascript:tidy();")
		with open("setup.html", "r") as f:
			html = f.read()
		html = html.format(
			cfg = Config.getAll(Leds)
		)
		HTTP.send(html)
		HTTP.end()
