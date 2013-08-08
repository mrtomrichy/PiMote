'''
	A Python version of the Simon Game using the PiFace and pimote
	Written by Tom Richardson 2013
	To run, type 'python simonsgame.py'. 
		It will run on the local IP of the Pi on port 8090
'''

from pimote import *
import pifacedigitalio as p
import random, time, threading

#Initialize the PiFace
p.init()
pfd = p.PiFaceDigital()

# Variables to be used globally
started = False 		# Has the game begun?
pattern = []			# The current pattern in the game
position = 0			# Where the user is up to with the input
sleeping = False		# Whether to accept input

class MyPhone(Phone):

	def buttonPressed(self, id, message, phoneId):
		# Declare global for access in this method
		global started
		global pattern
		global position
		global sleeping

		if not started and not sleeping:				# If the game has not started, and we are accepting input
			started = True 								# Start
			pattern.append(random.randint(0, 3))		# Add a new random number to the pattern
			sleeping = True								# Stop accepting input
			t1 = threading.Thread(target=flashLeds)		# Flash the LED pattern
			t1.start()
		
		elif not sleeping:								# If the game has begun, and we're accepting input					
			if id == b1.getId() and pattern[position] == 0:
				position += 1							# Correct in the pattern
			elif id == b2.getId() and pattern[position] == 1:
				position += 1							# Correct in the pattern
			elif id == b3.getId() and pattern[position] == 2:
				position += 1							# Correct in the pattern
			elif id == b4.getId() and pattern[position] == 3:
				position += 1							# Correct in the pattern
			else:		# They got the pattern wrong
				o.setText("Incorrect! You reached level <b>" + str(len(pattern))+"</b>.<br>Press any button to start again")
				self.reset()			# Reset the game

			if position == len(pattern) and started:	# If we reached the end of the pattern
				pattern.append(random.randint(0,3))		# Add a new random number to the pattern
				position = 0							# Wait for the whole input again
				sleeping = True							# Stop accepting input
				o.setText("Watch")						# Visual indicator
				t1 = threading.Thread(target=flashLeds)	# Flash the pattern
				t1.start()

	# Used to reset all variables
	def reset(self):
		global position
		global pattern
		global started
		position = 0
		pattern = []
		started = False

	# When a user disconnects from the game
	def clientDisconnected(self, socket):
		self.reset()						#Reset the game
		o.setText("Press any button to start")

# Flash the LED's in the correct pattern
def flashLeds():
	global sleeping
	n = 0 									# So we know when we're on the last one
	for i in pattern:						# Loop through the pattern
		pfd.leds[i].turn_on()				# Switch the LED on
		time.sleep(1)						# Sleep for 1 second
		pfd.leds[i].turn_off()				# Switch the LED off
		if n != len(pattern)-1:				# Check if we are at the end
			time.sleep(1)					# If we're not at the end, sleep for 1 second
		n+=1			
	sleeping = False						# We now accept input
	o.setText("Input the pattern!")			# Visual indicator

# Setting up the phone
thisphone = MyPhone()
thisphone.setTitle("Simons Game")			# Title to be displayed on the phone

# Add the buttons and output
b1 = Button("LED 0")
b2 = Button("LED 1")
b3 = Button("LED 2")
b4 = Button("LED 3")
o = OutputText("Press any button to start")
thisphone.add(b1)
thisphone.add(b2)
thisphone.add(b3)
thisphone.add(b4)
thisphone.add(o)

# Create the server
server = PhoneServer()
server.setMaxClients(1)						# Max clients that can connect
server.addPhone(thisphone)					# Add the phone to the server
server.start("0.0.0.0", 8090)				# Start the server
