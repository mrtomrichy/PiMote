"""
An example application using pimote
To run: python lights.py
  this will run it on ip=0.0.0.0 port=8090

"""

from pimote import *
import pifacedigitalio as p

# Initialize PiFace
p.init()
pfd = p.PiFaceDigital()

class MyPhone(Phone):
	global pfd
	def sensorUpdate(self, x, y, z):
		''' Called whenever there is a change in the accelerometer data
			Accelerometer values are between -10 and 10 (ish. They pick up the acceleration due to gravity 9.81ms)
		'''
		if y < -8:
			self.changeLed(pfd, 7)
		elif y > -8 and y < -6:
			self.changeLed(pfd, 6)
		elif y > -6 and y < -4:
			self.changeLed(pfd, 5)
		elif y > -4 and y < -2:
			self.changeLed(pfd, 4)
		elif y > -2 and y < 2:
			self.changeLed(pfd, 3)
		elif y > 2 and y < 4:
			self.changeLed(pfd, 2)
		elif y > 4 and y < 6:
			self.changeLed(pfd, 1)
		elif y > 6 and y < 8:
			self.changeLed(pfd, 0)

	def changeLed(self, pfd, led):
		''' Turn LED's on and off '''
		for i in range(0, 8):
			if i == led:
				pfd.leds[i].turn_on()
			else:
				pfd.leds[i].turn_off()

# Create the phone object
thisphone = MyPhone()
thisphone.setTitle("Lights!")
title = OutputText("<b>Tilt the phone to make different lights glow!</b>")

#Add the buttons to the phone
thisphone.add(title)
# Tell the phone to take sensor readings, slow
thisphone.setSensor(Phone.SENSOR_SLOW)
thisphone.setOrientation(Phone.ORIENTATION_LANDSCAPE)

#Create the server
myserver = PhoneServer()
myserver.setMaxClients(1)
#Add the phone
myserver.addPhone(thisphone)
# Start server
myserver.start("0.0.0.0", 8090)
