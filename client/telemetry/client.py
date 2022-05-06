import socket
import packet
import time
import sys
import threading

#0-5 joystick inputs
#6-11 lat-long, alt, num_sats, gps_qual, true_track, sog_kts
#12-14 heading, pitch, roll
formats = {0: "f", 1: "f", 2: "f", 3: "f", 4: "f", 5: "f",
		   6: "ff", 7: "f", 8: "B", 9: "B", 10: "f", 11: "f",
		   12: "f", 13: "f", 14: "f"}
		
class Radio(threading.Thread):

	def __init__(self, callback):
		super().__init__()
		self.last_ping = 0
		self.ADDRESS = None
		self.daemon = True
		self.active = True
		self.callback = callback

		self.PACKET_SIZE = 18
		self.PORT = 42069

		self.client = None
		self.init_connection()
		

	def init_connection(self):
		print("Setting up socket telemetry")

		if self.client():
			try: self.client.close()
			except: pass

		self.ADDRESS = socket.gethostbyname("affect.red")
		self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.client.setblocking(False)
		self.last_ping = 0
		
		
	def ping(self):
		self.last_ping = time.time()


	#listener
	def run(self):
	   
		while self.active:
			
			try:
				
				data = packet.decode(self.client.recv(self.PACKET_SIZE), formats)
				self.ping()
				self.callback(data)
			
			except:
				
				if time.time() - self.last_ping > 2:
					self.send(b"")
					
			time.sleep(0.005)
			
			
	def send(self, data):
		try:
			self.client.sendto(data, (self.ADDRESS, self.PORT))
			self.ping()
		except:
			self.init_connection()


	def stop(self):
		self.active = False
		self.join()
		
		



