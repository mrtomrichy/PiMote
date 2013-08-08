"""
An example application using pimoteutils
To run: python app.py 0.0.0.0 8080

Needs porting into python3 for use with PiFace
"""

# System imports
import sys
import threading
import subprocess

# Custom modules imports
import cleverbot
from pimote import *


# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])


# message IDs and used literals
ROBOT_CONTROL = "0"
VOICE_CONTROL = "1"
SENSOR_READ = "2"

LEFT_FORWARDS_OFF  = "0"
LEFT_FORWARDS_ON   = "1"
LEFT_BACKWARDS_OFF = "2"
LEFT_BACKWARDS_ON  = "3"

RIGHT_FORWARDS_OFF  = "4"
RIGHT_FORWARDS_ON   = "5"
RIGHT_BACKWARDS_OFF = "6"
RIGHT_BACKWARDS_ON  = "7"

BOTH_OFF = "-1"

# enable the nxt module: 0 = OFF, 1 == ON
# for testing purposes & battery save
ROBOT_ENABLED = 0


# Override Phone so you can control what you do with the messages
#   "id" - the ID of the button that has been pressed
#   "message" - the message sent by the phone. If no message it will be ""
class PiDroid(ControllerPhone):
	
	# Gets called when you create an instance of PiDroid
	# - initialises variables and creates a cleverbot session
	def __init__(self):
		self.speak = False
		self.conversation = False
		self.PiAI = cleverbot.Session()
		

	# Gets called when PiDroid receives a message
	# - handles the message it receives and dispatches execution to the appropriate function
	# - the functions on PiDroid are run in separate threads
	def controlPress(self, msg):
		# split the received message by commas to distinguish between function and arguments
		(id, sep, message) = msg.strip().partition(",")

		print "received: " + msg

		# a motor nxt command was received
		if id == ROBOT_CONTROL:
			threadMR = threading.Thread(target = self.moveRobot, args = (message, 100,))
			threadMR.start()
			#self.moveRobot(message, power = 100)
		
		# a voice command was received
		elif id == VOICE_CONTROL:
			threadIV = threading.Thread(target = self.interpretVoice, args = (message,))
			threadIV.start()
			#self.interpretVoice(message)

		# a sensor read command was received
		elif id == SENSOR_READ:
			threadSR = threading.Thread(target = self.sensorReadings, args = ())
			threadSR.start()
			#self.sensorReadings()


	# This function turns text-to-speech via a bash script which uses Google Voice
	# - the script cannot handle strings of size >100 so we split the message
	#   into "sentences" that can be spoken via the script
	def say(self, something):
		size = 99
		
		# if the message size is larger than the size we have set above,
		if len(something) > size:
			# split the message into words
			words = something.split()

			toBeSpoken = ""
			# and construnct "sentences" until all words are used
			for word in words:
				if len(toBeSpoken) + len(word) < size:
					toBeSpoken = toBeSpoken + " " + word
				else:
					print toBeSpoken

					# the next three lines are used to execute the speech
					# bash script as if you were running it from a terminal
					cmd = ["./speech.sh", toBeSpoken]
					p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
					p.wait() # wait for the execution to finish
					
					# do not ignore the word you are currently at!
					toBeSpoken = word

			something = toBeSpoken		

		cmd = ["./speech.sh", something]
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
		p.wait()


	# Gets called if a conversation with PiDroid has been set (from interpretVoice())
	# - it uses the imported cleverbot module and the existing session to send
	#   a message to cleverbot and then wait for a reply.
	# - cleverbot's reply is then turned from text-to-speech with the function above
	def reply(self, toSomething):
		answer = self.PiAI.Ask(toSomething)
		print "replied: " + answer
		self.say(answer)


	# Gets called when a command to move the nxt robot was received.
	# - it uses the NXTinterface to enable and disable the motors
	def moveRobot(self, message, power):
		
		# testing purposes
		if ROBOT_ENABLED == 0:
			return

		if   message == LEFT_FORWARDS_OFF:
			nxt.leftMotor.idle()
		
		elif message == LEFT_FORWARDS_ON:
			nxt.leftMotor.run(power)
		
		elif message == LEFT_BACKWARDS_OFF:
			nxt.leftMotor.idle()
		
		elif message == LEFT_BACKWARDS_ON:
			nxt.leftMotor.run(-power)
		

		elif message == RIGHT_FORWARDS_OFF:
			nxt.rightMotor.idle()
		
		elif message == RIGHT_FORWARDS_ON:
			nxt.rightMotor.run(power)
		
		elif message == RIGHT_BACKWARDS_OFF:
			nxt.rightMotor.idle()

		elif message == RIGHT_BACKWARDS_ON:
			nxt.rightMotor.run(-power)

		elif message == BOTH_OFF:
			nxt.leftMotor.idle()
			nxt.rightMotor.idle()

		else:
			print "ERROR: received " + message + " as ROBOT_CONTROL"


	# Gets called when a voice command was received.
	# - if the robot is set to 'speak', then it repeats every voice command
	# - if a conversation was set, then it uses cleverbot to fetch a reply
	def interpretVoice(self, message):

		if self.speak == True and self.conversation == False:
			if message.isdigit() == False:
				self.say(message)	

		elif self.speak == True and self.conversation == True:
			if message.isdigit() == False:
				self.reply(message)			

		# sets the power of the motors when using voice control
		power = 80

		# all voice commands are interpreted here
		# if you want to add more, add elif statements at the end of the function
		
		# move the nxt robot with voice commands
		if message == "forwards" or message == "go forwards":
			self.moveRobot(LEFT_FORWARDS_ON, power)		#
			self.moveRobot(RIGHT_FORWARDS_ON, power)	#

		elif message == "backwards" or message == "go backwards":
			self.moveRobot(LEFT_BACKWARDS_ON, power)	#
			self.moveRobot(RIGHT_BACKWARDS_ON, power)	#
			
		elif message == "turn left" or message == "spin left":
			self.moveRobot(LEFT_BACKWARDS_ON, power)	#
			self.moveRobot(RIGHT_FORWARDS_ON, power)	#

		elif message == "turn right" or message == "spin right":
			self.moveRobot(LEFT_FORWARDS_ON, power)		#
			self.moveRobot(RIGHT_BACKWARDS_ON, power)	#

		elif message == "stop":
			self.moveRobot(BOTH_OFF)	#

		# sets the robot to repeat voice commands
		elif message == "speak to me":
			self.speak = True
			self.say("I can talk! Hooray!")

		# disables the reapeating of voice commands
		elif message == "stop speaking":
			self.self = False
			self.conversation = False
			self.say("You are being mean to me, human.")

		# sets the robot to have a conversation through cleverbot
		elif message == "let's talk":
			self.speak = True
			self.conversation = True
			self.say("Very well, human.")

		# turns the conversation off
		elif message == "goodbye":
			self.conversation = False
			self.say("This has been mildy entertaining. Until next time, human.")


	# Gets called when a sensor readings command was received.
	# - currently, returns a string message ("<battery>,<ultrasonic>")
	# - although this is run in a separate thread, a reasonable polling rate is ADVISED 
	def sensorReadings(self):
		# testing purposes
		if ROBOT_ENABLED == 0:
			return

		self.sendMessage(str(nxt.getBatteryPercentage()) + "," + str(nxt.getUltrasonicReading()))
		



# Create the phone object
PiDroid = PiDroid()
PiDroid.setVideo()
PiDroid.setVoice()
PiDroid.setRecurring(1000) # polling rate (ms)

# Enabling the NXT Lego Robot
if ROBOT_ENABLED == 1:
	import NXTinterface as r
	nxt = r.NXTrobot()

#Create the server
myserver = PhoneServer()
# Request a password from connecting clients
myserver.setPassword("helloworld")
#Add the phone (app)
myserver.addPhone(PiDroid)
# Start server
myserver.start(ip, port)
