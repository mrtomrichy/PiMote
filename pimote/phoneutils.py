#   PhoneUtils - Author: Tom Richardson, Radu Jipa 2013
#   For use with PiMote and pimoteutils

from pimoteutils import *
import sys


class PhoneServer(PiMoteServer):
	''' 
	This is the main server that runs on the pi. 
	All messages are sorted here and sent to the phone that handles them.
	It also initialises and manages the security. 
	'''

	def addPhone(self, thephone): 
		''' Store the phone object for reference '''
		self.phone = thephone

	def messageReceived(self, message, socket):
		'''
		Messages sent from the phone are received here.
		Message contains the id of the component which sent the message, and the message
		Socket is the socket that the message came from. Contains client id.
		'''
		if isinstance(self.phone, Phone):                     		#Regular phone
			(id, sep, msg) = message.strip().partition(",")     	#Strip component ID and message apart
			self.phone.updateButtons(int(id), msg, self)        	#Update buttons if needed
			if int(id) == 8827:
				self.phone.updateSensors(msg, socket.id)
			else:
				try:
					self.phone.buttonPressed(int(id), msg, socket.id) 	#Allow the user to handle the message + client
				except Exception, e:
					print("Problem in buttonPressed() override: " + str(e))
					self.stop()
					print("Server killed, press enter.")
		elif isinstance(self.phone, ControllerPhone):         		#Controller
			self.phone.controlPress(message)                   		#Controller handler

	def clientConnected(self, socket):
		''' A client has connected to the server on this socket '''
		self.phone.setup(socket, self)                        		#Send them setup information
		try:
			self.phone.clientConnected(socket.id)
		except Exception, e:
			print("Problem in clientConnected() override: " + str(e))
			self.stop()
			print("Server killed, press enter.")

	def clientDisconnected(self, socket):
		''' A client has disconnected from the server and socket '''
		try:
			self.phone.clientDisconnected(socket.id)
		except Exception, e:
			print("Problem in clientDisconnected() override: " + str(e))
			self.stop()
			print("Server killed, press enter.")



''' ################------PHONE TYPES--------##################'''

class Phone():
	''' 
	Phone class holds all variables for phone protocols (does not unclude connection setup)
	Also contains an array which contains all components (ordered) to be shown on the connected phones.
	The user treats this as a phone and specifies what they would like displayed on it.
	You can add components directly, or through adding a Layout. Both work in the same way.
	'''
	name = "PiMote"                                         	#Default app name

	components = []                                         	#All components to be displayed on the phone

	controltype = 0                                        		#Type of phone

	orientation = 0
	ORIENTATION_PORTRAIT = 0
	ORIENTATION_LANDSCAPE = 1

	sensorvalue = 0                                         	#Accellerometer. 0 = off, 1 = normal, 2 = game, 3 = slow
	SENSOR_OFF = 0
	SENSOR_NORMAL = 1
	SENSOR_GAME = 2
	SENSOR_SLOW = 3
	sensorX = 0
	sensorY = 0
	sensorZ = 0

	#More protocol variables for component setup
	CLEAR_ALL      = 0
	INPUT_REGULAR  = 1                                       	#Specify regular input (Button)
	INPUT_TEXT     = 2                                          #Specify an InputText (Editable)
	INPUT_TOGGLE   = 3                                        	#Specify a Toggle Button (ToggleButton)
	OUTPUT_TEXT    = 4                                        	#Specify an OutputText (TextView)
	VIDEO_FEED     = 5                                          #Specify a VideoFeed (MjpgView)
	VOICE_INPUT    = 6                                          #Specify a VoiceInput (Google Voice Recognition button)
	RECURRING_INFO = 7                                      	#Specify a recurring poll from phone to pi
	PROGRESS_BAR   = 8                                        	#Specify a ProgressBar (ProgressBar)
	SPACER         = 9                                          #Specify a Spacer (blank View with specified height)
	SCROLLED_OUTPUT_TEXT = 10
	#Setup
	SET_CONTROL_TYPE = 0                                    	#Set the control type
	SETUP = 1                                               	#Setup information
	#Data being sent
	REQUEST_OUTPUT_CHANGE = 2                               	#Request a change to an output component


	def add(self, component):
		''' Add a component to the phone screen '''
		if isinstance(component, Component):
			component.id = self.setId()
			self.components.append(component)
		else:
			print("Not a Component.")
	def setId(self):
		''' Generates a unique component ID '''
		id=0
		x = 0
		while x < len(self.components):
			if self.components[x].id == id:
				id+=1
				x = 0
			else:
				x+=1
		return id
	def setView(self, layout):
		''' The phone will output the components from the passed in Layout '''
		if isinstance(layout, Layout):
			self.components = []
			self.components = layout.getComponents()
			self.updateDisplay()
		else:
			print("Not a valid Layout")

	def buttonPressed(self, id, msg, clientId):
		''' 
		Override this to handle the button presses. 
		ID - ID of the component that sent the message.
		msg - The message that was sent by that component.
		clientId - The ID of the phone which sent the message.
		'''
		pass
		
	def setup(self, socket, server):
		''' Sends all setup information to the phone from each component '''
		self.socket = socket
		self.server = server
		socket.send(str(Phone.SET_CONTROL_TYPE)+","+str(self.controltype)+","+self.name+","+str(socket.id)+","+str(self.sensorvalue)+","+str(self.orientation))
		for c in self.components:
			c.setup(socket, server) #setup each component

	def setSensor(self, value):
		''' Turns the sensor on or off, and sets the speed it sends messages at '''
		if value == 0 or value == 1 or value == 2 or value == 3:
			self.sensorvalue = value
		else:
			print("Sensor value not valid: must be Phone.SENSOR_OFF, Phone.SENSOR_SLOW, Phone.SENSOR_GAME or Phone.SENSOR_NORMAL.\nSetting to default off")

	def getSensorValues(self):
		''' Returns the current values of the accelerometer '''
		return [self.sensorX, self.sensorY]

	def setOrientation(self, value):
		''' Set the orientation of the phone '''
		if value == 0 or value == 1:
			self.orientation = value
		else:
			print("Invalid Orientation value. Must be Phone.ORIENTATION_LANDSCAPE or Phone.ORIENTATION_PORTRAIT\nSetting to default portrait")

	def updateButtons(self, id, message, server):
		''' Updates button state if necessary and sends to all phones '''
		for c in self.components:
			if isinstance(c, ToggleButton) and c.id == id:
				server.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.REQUEST_OUTPUT_CHANGE)+","+str(Phone.INPUT_TOGGLE)+","+str(id)+","+str(message))
				if int(message) == 1:
					c.value = True
				else:
					c.value = False

	def updateSensors(self, message, clientId):
		''' Updates the sensor variables and calls the sensorUpdate() method '''
		(x, sep, yz) = message.strip().partition(",")
		self.sensorX = x
		(y, sep, z) = yz.strip().partition(",")
		self.sensorY = y
		self.sensorZ = z
		try:
			self.sensorUpdate(float(self.sensorX), float(self.sensorY), float(self.sensorZ), clientId)
		except Exception, e:
			print("Problem with SensorUpdate() override: " + str(e))
			self.server.stop()
			print("Server killed, press enter.")

	def sensorUpdate(self, x, y, z, clientId):
		''' Override this to handle changes in accelerometer values '''
		pass

	def clearComponents(self):
		''' Clear all the components from the components array '''
		self.components = []

	def updateDisplay(self):
		''' Clear the display and repopulate with components[] '''
		try:
			self.server.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(Phone.CLEAR_ALL))
			for c in self.server.getClients():
				self.setup(c, self.server)
		except:
			pass

	def getClientName(self, clientId):
		try:
			name = self.server.getClientName(clientId)
			return name
		except Exception, e:
			print("Client name not found: " + str(e))

	def setTitle(self, title):
		''' Set the title of the application to be displayed on the phone '''
		self.name = str(title)

	def clientConnected(self, clientId):
		''' Override to handle when someone connects '''
		pass
	def clientDisconnected(self, clientId):
		''' Override to handle when someone disconnects '''
		pass
	
# BROKEN

class GridPhone():
	''' 
	GridPhone is an example of a custom made phone (this code) and manager (see Android code) 
	Creates a grid with touchable areas.
	Not working yet.
	'''
	controltype = 1

	def setup(self, socket, server):
		''' Used for communication and setup with device '''
		self.socket = socket
		self.server = server
		socket.send(str(Phone.SET_CONTROL_TYPE)+","+str(self.controltype))





''' ####################----COMPONENTS----###################### '''

class Component():
	''' An object of type Component can be added to the phone screen '''
	def setup(self, socket, server):
		''' 
		Send the setup information to the phone. 
		Also used to store the server and socket variables 
		'''
		pass
	def getId(self): 
		''' Returns the components id '''
		return self.id
	def removeIllegalChars(self, string):
		''' Used to remove characters that could mess with the protocol messages '''
		message = str(string).replace(',', '%/')
		message = str(message).replace('\n', '<br>')
		return message



class Button(Component):
	''' Button class: a simple input. Regular button that can be pressed '''
	def __init__(self, name):
		self.name = self.removeIllegalChars(name)
		self.type = Phone.INPUT_REGULAR
	def getName(self):
		''' Return the name of this component '''
		return self.name
	def getType(self):
		''' Return the type of this component '''
		return self.type
	def setup(self, socket, server):
		''' Send setup information for this Button to the phone '''
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type) + "," + str(self.id) + "," + str(self.name))


class InputText(Button):
	''' Allows the user to input some text and send it back to the pi '''
	def __init__(self, name):
		self.name = self.removeIllegalChars(name)
		self.type = Phone.INPUT_TEXT
	def setup(self, socket, server):
		''' Send setup information for this Button to the phone '''
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type) + "," + str(self.id) + "," + str(self.name))


class ToggleButton(Button):
	''' A button that can be toggled to 'On' or 'Off' positions '''
	def __init__(self, name, initialvalue):
		self.name = self.removeIllegalChars(name)
		self.value = initialvalue
		self.type = Phone.INPUT_TOGGLE
	def getValue(self):
		''' Return the value of the toggle button '''
		return self.value
	def setValue(self, value):
		''' Set the value of the toggle button '''
		self.value = value
	def setup(self, socket, server):
		''' Send setup information for this Button to the phone '''
		tf = 0
		if self.value == True:
			tf=1
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type) + "," + str(self.id) + "," + str(self.name) + "," + str(tf))
		del tf


class VoiceInput(Button):
	''' Allows the button to use their voice to send messages to the Pi '''
	def __init__(self):
		self.type = Phone.VOICE_INPUT
	def setup(self, socket, server):
		''' Send setup information for this Button to the phone '''
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id))


class RecurringInfo(Button):
	''' A recurring message is sent to the Pi from the phone. (The phone polls the pi)'''
	def __init__(self, sleepTime):
		self.type = Phone.RECURRING_INFO
		self.sleepTime = int(sleepTime)
	def setup(self, socket, server):
		''' Send setup information for this Button to the phone '''
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id)+","+str(self.sleepTime))



class OutputText(Component):
	''' A simple TextView where text can be output. Accepts HTML markup '''
	message = ""
	textSize = 16
	def __init__(self, initialmessage):
		self.type = Phone.OUTPUT_TEXT
		self.message = self.removeIllegalChars(initialmessage)
	def setText(self, message):
		''' Change the text displayed on the TextView '''
		self.message = self.removeIllegalChars(message)
		try:
			self.server.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.REQUEST_OUTPUT_CHANGE)+","+str(self.type)+","+str(self.id)+","+str(self.message))
		except:
			pass
	def getText(self):
		''' Get the current text being displayed '''
		return self.message
	def append(self, msg):
		''' Append text to the current text '''
		self.setText(self.getText()+msg)
	def setTextSize(self, size):
		self.textSize = int(size)
	def setup(self, socket, server):
		''' Send setup information for this Output to the phone '''
		self.server = server
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id)+","+str(self.message)+","+str(self.textSize))

class ScrolledOutputText(OutputText):
	''' Another type of output text. This one has a max size and scrolls '''
	def __init__(self, initialmessage, maxHeight):
		self.type = Phone.SCROLLED_OUTPUT_TEXT
		self.message = self.removeIllegalChars(initialmessage)
		self.maxLines = maxLines
	def setup(self, socket, server):
		self.server = server
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id)+","+str(self.message)+","+str(self.textSize)+","+str(self.maxLines))

class ProgressBar(Component):
	''' A progress bar from 0 to maxValue which is shaded up the the current level of progress '''
	def __init__(self, maxValue):
		self.maxValue = int(maxValue)
		self.type = Phone.PROGRESS_BAR
	def setup(self, socket, server):
		''' Send setup information for this Output to the phone '''
		self.server = server
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id)+","+str(self.maxValue))
	def setProgress(self, progress):
		''' Change that output information of this component '''
		if int(progress) <= self.maxValue:
			self.server.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.REQUEST_OUTPUT_CHANGE)+","+str(self.type)+","+str(self.id)+","+str(progress))
		else:
			print("Cannot set progress to higher than the max value specified")


class VideoFeed(Component):
	''' A video feed pulled from mjpeg-viewer '''
	outsidefeed = 0;
	ip = "-"
	def __init__(self, width, height):
		self.type = Phone.VIDEO_FEED
		self.width = int(width)
		self.height = int(height)
	def setIp(self, ip):
		''' Set the IP to something different to the pi '''
		self.ip = ip
		self.outsidefeed = 1
	def setup(self, socket, server):
		''' Send the setup information from the pi to the phone '''
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.width)+","+str(self.height)+","+str(self.outsidefeed)+","+self.ip)


class Spacer(Component):
	''' A simple aestetic component. Places a vertical space between two components '''
	def __init__(self, size):
		self.size = int(size)
		self.type = Phone.SPACER
	def setup(self, socket, server):
		''' Send setup information for this component to the phone '''
		socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.size))


class Layout():
	''' This can store multiple components and can then be sent for display on the phone '''
	def __init__(self):
		self.components = []
	def add(self, component):
		''' Add a component to the phone screen '''
		if isinstance(component, Component):
			component.id = self.setId()
			self.components.append(component)
		else:
			print("Not a Component.")
	def setId(self):
		''' Generates a unique client ID '''
		id=0
		x = 0
		while x < len(self.components):
			if self.components[x].id == id:
				id+=1
				x = 0
			else:
				x+=1
		return id
	def removeAllComponents(self):
		''' Empty the Layout '''
		self.components = []
	def removeComponent(self, component):
		''' Remove a single component ''' 
		if isinstance(component, Component):
			for c in self.components:
				if c == component:
					self.components.remove(c)
					return
		elif isinstance(component, int):
			del self.components[component]
		else:
			print("Please specify a Component or an index")
	def getComponents(self):
		''' Returns a list of all components '''
		return self.components
