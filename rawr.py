from netgrowl import GrowlRegistrationPacket, GrowlNotificationPacket, GROWL_UDP_PORT
from socket import AF_INET, SOCK_DGRAM, socket

class rawr:
	def __init__(self,app_name,host,password, ntypes = None):
		self.app_name=app_name
		self.host=host
		self.password=password
		self.ntypes = ntypes or ["Normal"]
	
	def regApp(self):
		addr = (self.host,GROWL_UDP_PORT)
		s=socket(AF_INET,SOCK_DGRAM)
		p=GrowlRegistrationPacket(application=self.app_name,password=self.password)
	
		[p.addNotification(n) for n in self.ntypes]
	
		s.sendto(p.payload(),addr)


	def sendnotif(self,ntitle,msg, ntype = None):
		addr=(self.host, GROWL_UDP_PORT)
		s=socket(AF_INET, SOCK_DGRAM)
		p = GrowlNotificationPacket(
			application=self.app_name,
			notification=ntype or self.ntypes[0],
			title=ntitle,
			description=msg,
			priority=0,
			password=self.password
		)	
		s.sendto(p.payload(),addr)

if __name__ == '__main__':
	x=rawr("pyatotest","localhost","yay", ntypes = ["Passed", "Failed"])
	x.regApp()
	for i in range(5):
		x.sendnotif("Test Passed!", "Stuff")