import socket
from . import packet
import time
import threading

class Queue:
	data = []
	prev_data = None

	
class Server:

	def __init__(self, port, protocol, packet_size):
	
		self.port = port
		self.protocol = protocol
		self.packet_size = packet_size
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(("0.0.0.0", self.port))
		self.sock.setblocking(0)
		self.queue = Queue()
		self.client = None
		self.running = True
		
		
	def quit(self):
		self.running = False
		
		
	def run_daemon(self):
	
		while self.running:
			
			try:
			
				data, address = self.sock.recvfrom(self.packet_size)
				print("CLIENT CONNECTED:", address)
				self.client = address
				
			except: pass
			
			if self.client and self.queue.data:# != self.queue.prev_data:
				self.sock.sendto(self.queue.data.pop(0), self.client)
				#self.queue.prev_data = self.queue.data
			
			time.sleep(0.005)
			
			
		print("Server stopped")
		
	
	def run(self):
		
		threading.Thread(target=self.run_daemon, daemon=True).start()
		print(f"Server is running on port: {self.port}")

	

