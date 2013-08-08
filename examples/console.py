"""
An example application using pimote
To run: python regular.py
  this will run it on ip=0.0.0.0 port=8090

Needs porting into python3 for use with the PiFace interface

"""

import sys
import subprocess
# Import PhoneServer and Phone classes from pimoteutils.
# Button only imported so we can access the variables
from pimote import *


# Parse the IP address and port you wish to listen on.
try:
	ip = sys.argv[1]
	port = int(sys.argv[2])
except:
	ip = "0.0.0.0"
	port = 8090

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
		if id == cmdIn.getId():
			cmd = message
			try:
				process = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
				outputT = process.communicate()
				output = outputT[0]
				if len(output) > 0:
					cmdOut.setText(output)
			except Exception, e:
				cmdOut.setText("Failed command")
				print(str(e))

# Create the phone object
thisphone = MyPhone()
thisphone.setTitle("Example PiMote App")
cmdIn = InputText("Type Command Here")
cmdOut = OutputText("-")

#Add the buttons to the phone
thisphone.add(cmdIn)
thisphone.add(cmdOut)
#Create the server
myserver = PhoneServer()
#Add the phone
myserver.addPhone(thisphone)
# Start server
myserver.start(ip, port)