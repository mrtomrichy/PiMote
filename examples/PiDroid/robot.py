from pimote import *
import threading
import subprocess
import cleverbot
cb = cleverbot.Session()

class myPhone(Phone):
	global nxt
	global cb
	global subprocess
	def buttonPressed(self, id, msg, clientId):
		if id == 444:
			if int(msg) == 1: #Left motor forward on
				nxt.leftMotor.run(100)
			elif int(msg) == 0 or int(msg) == 2: #Left motor forward off
				nxt.leftMotor.idle()
			elif int(msg) == 3: #Left motor backwards on
				nxt.leftMotor.run(-100)
			elif int(msg) == 5: #Right motor forwards on
				nxt.rightMotor.run(100)
			elif int(msg) == 4 or int(msg) == 6: #Right motor forwards off
				nxt.rightMotor.idle()
			elif int(msg) == 7: #Right motor backwards on
				nxt.rightMotor.run(-100)
		elif id == rb.getId():
			battery.setText(str(nxt.getBatteryPercentage())+"%")
			ultra.setText(str(nxt.getUltrasonicReading()))
		elif id == voice.getId():
			reply = cb.Ask(msg)
			thread = threading.Thread(target = self.say, args = (msg,))
			thread.start()

	def setup(self, phone, server):
		self.server = server
		phone.setControl("1")
		self.setupComponents(phone, server)

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

import NXTinterface as r
nxt = r.NXTrobot()

rb = RecurringInfo(2000)
battery = OutputText("Battery")
ultra = OutputText("Ultra")
voice = VoiceInput()
phone = myPhone()
phone.add(battery)
phone.add(ultra)
phone.add(rb)
phone.add(voice)

server = PhoneServer()
server.addPhone(phone)
server.setMaxClients(1)
server.startServer("0.0.0.0", 8090)
