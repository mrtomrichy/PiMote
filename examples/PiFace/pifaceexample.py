''' An example application to toggle the LED's on a PiFace 
	Written by Tom Richardson 2013
	To run, type 'python pifaceexample.py'
		It will run on the Pi's local IP on port 8090
'''

import pifacedigitalio as p
from pimote import *

# Initialize PiFace
p.init()
pfd = p.PiFaceDigital()

class MyPhone(Phone):
	# Override to get messages sent from phone
	def buttonPressed(self, id, message, phoneId):
		global pfd
		global buttons
		
		j = 0
		# Loop through buttons
		for j in range(0, 8):
			if buttons[j].getId() == id:
				# Change the LED
				self.changeLed(pfd, j, buttons[j])

	#Used to turn an LED on or off depending on input
	def changeLed(self, pfd, led, b):
		if b.getValue():
			pfd.leds[led].turn_on()
		else:
			pfd.leds[led].turn_off()

# Create the phone object
thisphone = MyPhone()
thisphone.setTitle("PiFace Control")

# A list to hold all the buttons (saves 8 variables)
buttons = []

i=0
# Create all buttons (one for each LED) and add to phone
for i in range(0, 8):
	b = ToggleButton("Toggle LED " + str(i), False)
	buttons.append(b)
	thisphone.add(b)

# Create the server
myserver = PhoneServer()
# Add the phone
myserver.addPhone(thisphone)
# Start server
myserver.start("0.0.0.0", 8090)
