"""
An example application using pimote
To run: python chat.py
  this will run it on ip=0.0.0.0 port=8090

"""

import sys, random
from pimote import *

class MyPhone(Phone):

    def buttonPressed(self, id, message, phoneId):
        if id == input.getId():
            print(str(self.getClientName(phoneId)) + " says: " + message)       # Print on Pi
            output.append("\n<font color=blue>"+self.getClientName(phoneId)+"</font>: "+message+"")   # Set text

    def clientConnected(self, phoneId):
        print(str(self.getClientName(phoneId)) + " connected")                  # Print on Pi
        output.append("\n<font color=green>"+self.getClientName(phoneId)+" connected</font>")         # Set text

    def clientDisconnected(self, phoneId):
        print(str(self.getClientName(phoneId)) + " disconnected")               # Print on Pi
        output.append("\n<font color=#AA33FF>"+self.getClientName(phoneId)+" disconnected</font>")    # Set text


thisphone = MyPhone()                                                       # Create the phone object
thisphone.setTitle("Usernames")

input = InputText("Input text here")                                        # Text Input
output = ScrolledOutputText("<font color=red>Messages:</font>", 500)        # Text Output

#Add the buttons to the phone
thisphone.add(output)
thisphone.add(input)

thisphone.setOrientation(Phone.ORIENTATION_PORTRAIT)                        # Portrait oritentation

myserver = PhoneServer()                                                    # Create the server

myserver.addPhone(thisphone)                                                # Add the phone
myserver.allowClientNaming()                                                # Allow users to register usernames

myserver.startServer("0.0.0.0", 8090)                                       # Start the server