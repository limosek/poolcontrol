
FILES = config.py http.py leds.py ntpclient.py onewire.py sensors.py status.py wifi.py $(wildcard *.html)
BOOT = boot.py
PORT = COM6
BAUDS = 115200
AMPY = ampy -b $(BAUDS) -p $(PORT)
ESPTOOL = esptool.py -b $(BAUDS) -p $(PORT)
COPY = copy

upload:
	$(foreach file,$(FILES), echo $(AMPY) put $(file) & $(AMPY) put $(file) &)
	$(COPY) boot.py _boot_.py & $(AMPY) put _boot_.py

ls:
	$(AMPY) ls /flash/

#clean:
#	$(ESPTOOL) erase_flash

#flash:
#	$(ESPTOOL) write_flash 0x0 UIFlow-v1.5.4.bin

run:
	$(AMPY) run boot.py

permanent:
	$(AMPY) put boot.py
