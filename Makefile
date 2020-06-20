
FILES = config.py http.py leds.py ntpclient.py onewire.py sensors.py status.py wifi.py $(wildcard *.html)
BOOT = boot.py
PORT = COM6
BAUDS = 750000
AMPY=ampy

upload:
	$(foreach file,$(FILES), echo $(AMPY) -b $(BAUDS) -p $(PORT) put $(file) & $(AMPY) -b $(BAUDS) -p $(PORT) put $(file) &)
