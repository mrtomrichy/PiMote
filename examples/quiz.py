"""
	An example application using pimote. This is a quiz that can be played by up to 2 players.
	To edit questions, change the 'qa.txt' file. Ensure the layout is 'Q, A, B, C, AnswerLetter' on separate lines
	Written by Tom Richardson 2013
	To run: python quiz.py
	  It will run on the local IP of the Pi on port 8090

"""

import sys, threading, time
# Import PhoneServer and Phone classes from pimoteutils.
# Button only imported so we can access the variables
from pimote import *

# Override Phone so you can control what you do with the messages
#   "id" - the ID of the button that has been pressed
#   "message" - the message sent by the phone. If no message it will be ""
class MyPhone(Phone):
	#Override
	def buttonPressed(self, id, message, phoneId):
		#########----------------------------------------------###########
		# Your code will go here! Check for the ID of the button pressed #
		# and handle that button press as you wish.                      #
		#########----------------------------------------------###########
		if id == a.getId() and Globals.ready == False:
			Globals.ready = True
			l.start()

		if id == a.getId() and Globals.correct == "A":
			Globals.thisQuestionAnswers[phoneId] = 1
			Globals.answer = True
		elif id == b.getId() and Globals.correct == "B":
			Globals.answer = True
			Globals.thisQuestionAnswers[phoneId] = 1
		elif id == c.getId() and Globals.correct == "C":
			Globals.answer = True
			Globals.thisQuestionAnswers[phoneId] = 1
		else:
			Globals.thisQuestionAnswers[phoneId] = 0

	def clientConnected(self, id):
		Globals.playersConnected+=1
		if Globals.playersConnected > len(Globals.playersTotals):
			Globals.playersTotals.append(0)

		if Globals.playersConnected > len(Globals.thisQuestionAnswers):
			Globals.thisQuestionAnswers.append(0)
		Globals.thisQuestionAnswers[id] = 0

outputQA = OutputText("Quiz: Press A when all players are ready")
a = Button("A")
b = Button("B")
c = Button("C")
s = Spacer(100)
s2 = Spacer(50)
t = OutputText("Time to answer question shown here")

# Create the phone object
thisphone = MyPhone()
thisphone.setTitle("PiQuiz")

thisphone.add(s2)
thisphone.add(outputQA)
thisphone.add(s)
thisphone.add(a)
thisphone.add(b)
thisphone.add(c)
thisphone.add(s)
thisphone.add(t)
#Create the server
myserver = PhoneServer()
myserver.setMaxClients(2)

#Add the phone
myserver.addPhone(thisphone)

class Questioner(threading.Thread):
	def run(self):
		lines = []
		f = open("qa.txt", "r")
		for line in f:
			lines.append(line.strip("\n"))
		lineCount = 0

		while Globals.running and lineCount < len(lines):
			try:
				Globals.answer = False
				q = lines[lineCount]
				a = lines[lineCount+1]
				b = lines[lineCount+2]
				c = lines[lineCount+3]
				k = lines[lineCount+4]
				lineCount += 5
				#display
				que = str(str(q)+"<br><br>"+str(a)+"<br>"+str(b)+"<br>"+str(c))
				outputQA.setText(que)
				Globals.correct = k
				#Wait for answer
				timeLeft = 10
				while timeLeft > 0:
					t.setText(str(timeLeft)+"s")
					timeLeft -= 1
					time.sleep(1)
				x = 0
				while x < len(Globals.thisQuestionAnswers):
					if(Globals.thisQuestionAnswers[x] == 1):
						Globals.playersTotals[x] += 1
					Globals.thisQuestionAnswers[x] = 0
					x+=1
				print(Globals.playersTotals)

			except Exception, e:
				print("Error:" + str(e))
				Globals.running = False

		print("DONE")
		highest = 0
		for x in range(0, len(Globals.playersTotals)):
			if Globals.playersTotals[x] > Globals.playersTotals[highest]:
				highest = x

		outputQA.setText("THE WINNER IS PLAYER " + str(highest))
		timeToExit = 3
		while timeToExit > -1:
			t.setText("Exiting in "+str(timeToExit) +"..")
			time.sleep(1)
			timeToExit-=1
		myserver.stop()
		sys.exit(0)

class Globals:
	ready = False
	playersConnected = 0
	running = True
	answer = False
	correct = ""
	thisQuestionAnswers = []
	playersTotals = []

l = Questioner()
# Start server
myserver.start("0.0.0.0", 8090)
