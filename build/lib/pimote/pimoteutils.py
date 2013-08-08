"""

ex3.py - Module for ex3 - David Thorne / AIG / 15-01-2009 
Renamed and used as pimoteutils by Tom Richardson - 14/06/2013 


"""

import sys
import threading
import time
import socket as socketlib
import subprocess
import string, random

def generator(size, chars):
  return ''.join(random.choice(chars) for x in range(size))

def createKey():
  size = 16
  chars = string.ascii_letters + string.digits + "                    "
  privateKey = "#"
  for x in range(0,30):
    privateKey += generator(size, chars)
  privateKey += "#"
  file = open('privatekey.data', 'w')
  file.write(privateKey)

class Socket():
  """
  Mutable wrapper class for sockets.
  """

  def __init__(self, socket):
    # Store internal socket pointer
    self._socket = socket
  
  def send(self, msg):
    # Ensure a single new-line after the message
    self._socket.send("%s\n" % msg.strip())
    
  def close(self):
    self._socket.close()
    

class Receiver():
  """
  A class for receiving newline delimited text commands on a socket.
  """

  def __init__(self):
    # Protect access
    self._lock = threading.RLock()
    self._running = True

  def __call__(self, socket):
    """Called for a connection."""
    # Set timeout on socket operations
    socket.settimeout(1)

    # Wrap socket for events
    wrappedSocket = Socket(socket)
    
    # Store the unprocessed data
    stored = ''
    chunk = ''
    
    # On connect!
    self._lock.acquire()
    self.onConnect(wrappedSocket)
    self._lock.release()
    
    # Loop so long as the receiver is still running
    while self.isRunning():
    
      # Take everything up to the first newline of the stored data
      (message, sep, rest) = stored.partition('\n')
      if sep == '': # If no newline is found, store more data...
        while self.isRunning():
          try:
            chunk = ''
            chunk = socket.recv(1024)
            stored += chunk
            break
          except socketlib.timeout:
            pass
          except:
            print('EXCEPTION')
        
        # Empty chunk means disconnect
        if chunk == '':
          break;

        continue
      else: # ...otherwise store the rest
        stored = rest     
        
      # Process the command
      self._lock.acquire()
      success = self.onMessage(wrappedSocket, message)
      self._lock.release()
      
      if not success:
        break;

    # On disconnect!
    self._lock.acquire()
    self.onDisconnect(wrappedSocket)    
    self._lock.release()
    socket.close()
    del socket
    
    # On join!
    self.onJoin()
      
  def stop(self):
    """Stop this receiver."""
    self._lock.acquire()
    self._running = False
    self._lock.release()
    
  def isRunning(self):
    """Is this receiver still running?"""
    self._lock.acquire()
    running = self._running
    self._lock.release()
    return running
    
  def onConnect(self, socket):
    pass

  def onMessage(self, socket, message):
    pass

  def onDisconnect(self, socket):
    pass

  def onJoin(self):
    pass

    
    
class Server(Receiver):

  def start(self, ip, port):
    # Set up server socket
    serversocket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)
    serversocket.setsockopt(socketlib.SOL_SOCKET, socketlib.SO_REUSEADDR, 1)
    serversocket.bind((ip, int(port)))
    serversocket.listen(10)
    serversocket.settimeout(1)
    
    # On start!
    self.onStart()

    # Main connection loop
    threads = []
    while self.isRunning():
      try:
        (socket, address) = serversocket.accept()
        thread = threading.Thread(target = self, args = (socket,))
        threads.append(thread)
        thread.start()
      except socketlib.timeout:
        pass
      except:
        self.stop()

    # Wait for all threads
    while len(threads):
      threads.pop().join()

    # On stop!        
    self.onStop()

  def onStart(self):
    pass

  def onStop(self):
    pass

class Client(Receiver):
  
  def start(self, ip, port):
    # Set up server socket
    self._socket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)
    self._socket.settimeout(1)
    self._socket.connect((ip, int(port)))

    # On start!
    self.onStart()

    # Start listening for incoming messages
    self._thread = threading.Thread(target = self, args = (self._socket,))
    self._thread.start()
    
  def send(self, message):
    # Send message to server
    self._lock.acquire()
    self._socket.send("%s\n" % message.strip())
    self._lock.release()
    time.sleep(0.5)

  def stop(self):
    # Stop event loop
    Receiver.stop(self)
    print("Stopping")
    # Join thread
    if self._thread != threading.currentThread():
      self._thread.join()
    
    # On stop!
    self.onStop()   

  def onStart(self):
    pass

  def onStop(self):
    pass
    
  def onJoin(self):
    self.stop()


# Added by Tom Richardson - 02/07/2013

class PiMoteServer(Server):
  SENT_PASSWORD = 0
  SENT_DATA = 1
  PASSWORD_FAIL = 2314
  REQUEST_PASSWORD = 9855
  STORE_KEY = 5649
  DISCONNECT_USER = 6234
  MESSAGE_FOR_MANAGER = 7335

  isPassword = False
  clientMax = False
  noOfClients = 0
  clients = []

  #Called when the server is started
  def onStart(self):
    print("Server has started")
    if self.isPassword: #If password protected
      read = False
      while not read: #Loop to get the key
        try:
          file = open("privatekey.data", "r")
          self.key = file.read() #Read the key
          file.close()
          read = True
        except: #No such file so generate key and file
          createKey()

  #Called when a message is recieved from the phone
  def onMessage(self, socket, message):
    #First int is a protocol variable
    (sentType, sep, msg) = message.strip().partition(",")
    if int(sentType) == PiMoteServer.SENT_PASSWORD: #Password data
      self.managePassword(msg, socket)
    elif int(sentType) == PiMoteServer.SENT_DATA: #Input data
      self.messageReceived(msg, socket)
    
    # Signify all is well
    return True

  #Called when a phone connects to the server
  def onConnect(self, socket):
    print("Client connected")
    self.noOfClients+=1 #Counting clients
    socket.id = self.setId()
    if self.clientMax:
      if self.noOfClients > self.maxClients:
        socket.send(str(PiMoteServer.DISCONNECT_USER)) #Kick them if full

    if self.isPassword: #if the server has password, request it
      socket.send(str(PiMoteServer.REQUEST_PASSWORD))
    else: #otherwise setup
      self.clients.append(socket)
      self.clientConnected(socket)
    return True

  #Called when a phone disconnects from the server
  def onDisconnect(self, socket):
    print("Client disconnected")
    self.noOfClients-=1 #tracking clients
    self.clientDisconnected(socket)
    for client in self.clients:
      if client.id == socket.id:
        self.clients.remove(client)
    return True

  def setId(self):
    id=0
    x = 0
    while x < len(self.clients):
      if self.clients[x].id == id:
        id+=1
        x = 0
      else:
        x+=1
    return id
  #Used to set a password for the server
  def setPassword(self, pswd):
    self.isPassword = True
    self.password = pswd

  #Handle the password received from the phone
  def managePassword(self, password, socket):
    if password == self.password: #Password was right, tell them to store key
      socket.send(str(PiMoteServer.STORE_KEY)+","+self.key)
      socket.id = self.setId()
      self.clients.append(socket)
      self.clientConnected(socket)
    elif password == self.key:#they had a key
      socket.id = self.setId()
      self.clients.append(socket)
      self.clientConnected(socket)
    else:#wrong password
      socket.send(str(PiMoteServer.PASSWORD_FAIL)) #kick them

  #Used to limit the amount of clients that can connect at one time
  def setMaxClients(self, x):
    self.clientMax = True
    self.maxClients = x

  def getClients(self):
    return self.clients

  def send(self, msg):
    ''' Used to send a message to all connected clients '''
    for client in self.getClients():
      client.send(msg)

  def messageReceived(self, message, socket):
    pass
  def clientConnected(self, socket):
    pass
  def clientDisconnected(self, socket):
    pass


#Unfinished (low priority)
class PiMoteClient(Client):
  SEND_PASSWORD = 0
  SEND_DATA = 1
  def onMessage(self, socket, message):
    (id, sep, msg) = message.split().partition(",")
    if id == PiMoteServer.REQUEST_PASSWORD:
      password = raw_input("Server password: ")
      self.send(int(self.SEND_PASSWORD)+","+password)
    elif id == PiMoteServer.STORE_KEY:
      print("Store key")
    elif id == PiMoteServer.PASSWORD_FAIL:
      print("Wrong password")
      self.stop()
    elif id == PiMoteServer.DISCONNECT_USER:
      print("Disconnected by server")
      self.stop()
    elif id == PiMoteServer.MESSAGE_FOR_MANAGER:
      self.messageReceived(msg)
    else:
      self.messageReceived(message)
    pass
  def onConnect(self, socket):
    pass
  def onDisconnect(self, socket):
    pass


  def run(self):
    pass
  def messageReceived(self, message):
    pass
  def sendMessage(self, message):
    self.send(str(self.SEND_DATA)+","+message)


