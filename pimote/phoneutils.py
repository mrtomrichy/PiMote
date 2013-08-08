#   PhoneUtils - Author: Tom Richardson, Radu Jipa 2013
#   For use with PiMote and pimoteutils


from pimoteutils import *
import sys

''' ########################-------SERVER-------############################
    This is the main server that runs on the pi. All messages are sorted here and sent
    to the phone that handles them.
    It also initialises and manages the security. '''

class PhoneServer(PiMoteServer):

  def addPhone(self, thephone): 
    ''' Store the phone object for reference '''
    self.phone = thephone

  def messageReceived(self, message, socket):
    '''
    This method is called when a message comes from the phone to the Pi.
    Included are the message sent, and the socket which sent it
    '''
    if isinstance(self.phone, Phone):                     #Regular phone
      (id, sep, msg) = message.strip().partition(",")     #Strip component ID and message apart
      self.phone.updateButtons(int(id), msg, self)        #Update buttons if needed
      if int(id) == 8827:
        self.phone.updateSensors(msg, socket.id)
      else:
        self.phone.buttonPressed(int(id), msg, socket.id) #Allow the user to handle the message + client
    elif isinstance(self.phone, ControllerPhone):         #Controller
      self.phone.controlPress(message)                    #Controller handler

  def clientConnected(self, socket):
    ''' A client has connected to the server '''
    self.phone.setup(socket, self)                        #Send them setup information
    self.phone.clientConnected(socket.id)

  def clientDisconnected(self, socket):
    ''' A client has disconnected from the server '''
    try:
      self.phone.clientDisconnected(socket.id)
    except:
      pass



''' ################------PHONE TYPES--------##################'''

class Phone():
  ''' Phone class holds all variables for phone protocols (does not unclude connection setup)
      Also contains an array which contains all components (ordered) to be shown on the phone.
      The user treats this as a phone and specifies what they would like displayed on it.
  '''
  name = "PiMote"                                         #Default app name

  components = []                                         #All components to be displayed on the phone

  controltype = 0                                         #Type of phone

  orientation = 0
  ORIENTATION_PORTRAIT = 0
  ORIENTATION_LANDSCAPE = 1

  sensorvalue = 0                                         #Accellerometer. 0 = off, 1 = normal, 2 = game, 3 = slow
  SENSOR_OFF = 0
  SENSOR_NORMAL = 1
  SENSOR_GAME = 2
  SENSOR_SLOW = 3
  sensorX = 0
  sensorY = 0
  sensorZ = 0

  #More protocol variables for component setup
  CLEAR_ALL = 0
  INPUT_REGULAR = 1                                       #Specify regular input (Button)
  INPUT_TEXT = 2                                          #Specify an InputText (Editable)
  INPUT_TOGGLE = 3                                        #Specify a Toggle Button (ToggleButton)
  OUTPUT_TEXT = 4                                         #Specify an OutputText (TextView)
  VIDEO_FEED = 5                                          #Specify a VideoFeed (MjpgView)
  VOICE_INPUT = 6                                         #Specify a VoiceInput (Google Voice Recognition button)
  RECURRING_INFO = 7                                      #Specify a recurring poll from phone to pi
  PROGRESS_BAR = 8                                        #Specify a ProgressBar (ProgressBar)
  SPACER = 9                                              #Specify a Spacer (blank View with specified height)
  #Setup
  SET_CONTROL_TYPE = 0                                    #Set the control type
  SETUP = 1                                               #Setup information
  #Data being sent
  REQUEST_OUTPUT_CHANGE = 2                               #Request a change to an output component

  def add(self, component):
    ''' Add a component to the phone screen '''
    if isinstance(component, Component):
      component.id = len(self.components)
      self.components.append(component)
    else:
      print("Not a Component.")

  def buttonPressed(self, id, msg, clientId):
    ''' Overridden by user so they can handle messages received from phone '''
    pass
  #Used for setup
  def setup(self, socket, server):
    ''' Sends all setup information to the phone '''
    self.socket = socket
    self.server = server
    socket.send(str(Phone.SET_CONTROL_TYPE)+","+str(self.controltype)+","+self.name+","+str(socket.id)+","+str(self.sensorvalue)+","+str(self.orientation))
    for c in self.components:
      c.setup(socket, server) #setup each component

  def setSensor(self, value):
    if value == 0 or value == 1 or value == 2 or value == 3:
      self.sensorvalue = value
    else:
      print("Sensor value not valid: must be Phone.SENSOR_OFF, Phone.SENSOR_SLOW, Phone.SENSOR_GAME or Phone.SENSOR_NORMAL.\nSetting to default off")

  def getSensorValues(self):
    return [self.sensorX, self.sensorY]

  def setOrientation(self, value):
    if value == 0 or value == 1:
      self.orientation = value
    else:
      print("Invalid Orientation value. Must be Phone.ORIENTATION_LANDSCAPE or Phone.ORIENTATION_PORTRAIT\nSetting to default portrait")

  def updateButtons(self, id, message, server):
    ''' Update button state if necessary '''
    for c in self.components:
      if isinstance(c, ToggleButton) and c.id == id:
        server.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.REQUEST_OUTPUT_CHANGE)+","+str(Phone.INPUT_TOGGLE)+","+str(id)+","+str(message))
        if int(message) == 1:
          c.value = True
        else:
          c.value = False

  def updateSensors(self, message, clientId):
    (x, sep, yz) = message.strip().partition(",")
    self.sensorX = x
    (y, sep, z) = yz.strip().partition(",")
    self.sensorY = y
    self.sensorZ = z
    self.sensorUpdate(float(self.sensorX), float(self.sensorY), float(self.sensorZ))

  def sensorUpdate(self, x, y, z):
    pass

  def clearComponents(self):
    ''' Clear all the components from the components array '''
    self.components = []

  def updateDisplay(self):
    ''' Clear the display and repopulate with the components '''
    self.server.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(Phone.CLEAR_ALL))
    for c in self.server.getClients():
      self.setup(c, self.server)

  def setTitle(self, title):
    ''' Set the title of the application to be displayed on the phone '''
    self.name = str(title)

  def clientConnected(self, socket):
    ''' Can be overridden by the user to handle when someone connects '''
    pass
  def clientDisconnected(self, socket):
    ''' Can be overridden by the user to handle when someone disconnects '''
    pass
  
# BROKEN
''' ControllerPhone is an example of a custom made phone (this code) and manager (see Android code) '''
class ControllerPhone():
  controltype = 1
  video = False
  voice = False
  recurring = False
  sleepTime = 0
  def controlPress(self, type):
    ''' Overridden by the user to handle messages '''
    pass
  def setVideo(self):
    ''' Add video feed '''
    self.video = True
  def setVoice(self):
    ''' Add voice recognition button '''
    self.voice = True
  def setRecurring(self, sleepTime):
    ''' Add a recurring poll from phone to Pi '''
    self.recurring = True
    self.sleepTime = sleepTime
  def sendMessage(self, message):
    ''' Send a message to the phone '''
    self.socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+message)
  def setup(self, socket):
    ''' Used for communication and setup with device '''
    self.socket = socket
    voiceV = videoV = recurringV = 0
    if self.video == True:
      videoV = 1
    if self.voice == True:
      voiceV = 1
    if self.recurring == True:
      recurringV = 1
    socket.send(str(Phone.SET_CONTROL_TYPE)+","+str(self.controltype) + "," + str(videoV) + "," + str(voiceV)+","+str(recurringV)+","+str(self.sleepTime))





''' ####################----COMPONENTS----###################### '''

class Component():
  def setup(self, socket, server):
    pass
  def getId(self): 
    return self.id
  def removeIllegalChars(self, string):
    message = str(string).replace(',', '%/')
    message = str(message).replace('\n', '<br>')
    return message


''' Button class: a simple input. Regular button that can be pressed '''
class Button(Component):
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

''' Allows the user to input some text and send it back to the pi '''
class InputText(Button):
  def __init__(self, name):
    self.name = self.removeIllegalChars(name)
    self.type = Phone.INPUT_TEXT
  def setup(self, socket, server):
    ''' Send setup information for this Button to the phone '''
    socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type) + "," + str(self.id) + "," + str(self.name))

''' A button that can be toggled to 'On' or 'Off' positions '''
class ToggleButton(Button):
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

''' Allows the button to use their voice to send messages to the Pi '''
class VoiceInput(Button):
  def __init__(self):
    self.type = Phone.VOICE_INPUT
  def setup(self, socket, server):
    ''' Send setup information for this Button to the phone '''
    socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id))

''' A recurring message is sent to the Pi from the phone. (The phone polls the pi)'''
class RecurringInfo(Button):
  def __init__(self, sleepTime):
    self.type = Phone.RECURRING_INFO
    self.sleepTime = int(sleepTime)
  def setup(self, socket, server):
    ''' Send setup information for this Button to the phone '''
    socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id)+","+str(self.sleepTime))


''' A simple TextView where text can be output. Accepts HTML markup '''
class OutputText(Component):
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
  def setTextSize(self, size):
    self.textSize = int(size)
  def setup(self, socket, server):
    ''' Send setup information for this Output to the phone '''
    self.server = server
    socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.id)+","+str(self.message)+","+str(self.textSize))

''' A progress bar from 0 to maxValue which is shaded up the the current level of progress '''
class ProgressBar(Component):
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

''' A video feed pulled from mjpeg-viewer '''
class VideoFeed(Component):
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

''' A simple aestetic component. Places a vertical space between two components '''
class Spacer(Component):
  def __init__(self, size):
    self.size = int(size)
    self.type = Phone.SPACER
  def setup(self, socket, server):
    ''' Send setup information for this component to the phone '''
    socket.send(str(PiMoteServer.MESSAGE_FOR_MANAGER)+","+str(Phone.SETUP)+","+str(self.type)+","+str(self.size))
