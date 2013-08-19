"""
An example application using pimote
To run: python chat.py
  this will run it on ip=0.0.0.0 port=8090

"""

import sys, random
from pimote import *

class MyPhone(Phone):
    #Override
    buttonPress = 0
    def buttonPressed(self, id, message, phoneId):
        if id == b3.getId():
            print(str(self.getClientName(phoneId)) + " says: " + message)
            o.append("\n<font color=blue>"+self.getClientName(phoneId)+"</font>: " + message+"")

    def clientConnected(self, phoneId):
        print(str(self.getClientName(phoneId)) + " connected")
        o.append("\n<font color=green>"+self.getClientName(phoneId)+" connected</font>")
    def clientDisconnected(self, phoneId):
        print(str(self.getClientName(phoneId)) + " disconnected")
        o.append("\n<font color=#AA33FF>"+self.getClientName(phoneId)+" disconnected</font>")

# Create the phone object
thisphone = MyPhone()
thisphone.setTitle("Usernames")


b3 = InputText("Input text here") #Text Input
o = ScrolledOutputText("<font color=red>Messages:</font>", 500)

#Add the buttons to the phone
thisphone.add(o)
thisphone.add(b3)

thisphone.setOrientation(Phone.ORIENTATION_PORTRAIT)

#Create the server
myserver = PhoneServer()
#Add the phone
myserver.addPhone(thisphone)
myserver.allowClientNaming()
# Start server
myserver.startServer("0.0.0.0", 8090)
