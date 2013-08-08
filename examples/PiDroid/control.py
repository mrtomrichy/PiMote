"""
An example application using pimoteutils
To run: python app.py 0.0.0.0 8080

Needs porting into python3 for use with PiFace

"""

import sys
# Import PhoneServer and Phone classes from pimoteutils.
# Button only imported so we can access the variables
from pimoteutils import *


# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Override Phone so you can control what you do with the messages
#   "id" - the ID of the button that has been pressed
#   "message" - the message sent by the phone. If no message it will be ""
class MyPhone(ControllerPhone):
	#Override
	text = "Hello"
	def controlPress(self, type):
		print(str(type))

# Create the phone object
thisphone = MyPhone()

thisphone.setVideo(True)
#Create the server
myserver = PhoneServer()
#Add the phone
myserver.addPhone(thisphone)
# Start server
myserver.start(ip, port)
