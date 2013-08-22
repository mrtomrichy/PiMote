from pimote import *

class myPhone(Phone):
	global nxt
	def buttonPressed(self, id, msg, clientId):
		print(msg)
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
			print("Battery")
			battery.setText(str(nxt.getBatteryPercentage)+"%")
			ultra.setText(str(nxt.getUltrasonicReading()))

	def setup(self, phone, server):
		self.server = server
		phone.setControl("1")
		self.setupComponents(phone, server)

import NXTinterface as r
nxt = r.NXTrobot()

rb = RecurringInfo(2000)
battery = OutputText("Battery")
ultra = OutputText("Ultra")
phone = myPhone()
phone.add(battery)
phone.add(ultra)
phone.add(rb)

server = PhoneServer()
server.addPhone(phone)
server.setMaxClients(1)
server.startServer("0.0.0.0", 8090)
