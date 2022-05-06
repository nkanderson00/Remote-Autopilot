import socket
import packet
import time
import random
import threading


PACKET_SIZE = 32
ADDRESS = "192.168.1.16"
PORT = 42069
send_delay = 0.01

formats = {0: "B", 1: "B", 2: "H", 3: "H", 4: "b", 5: "b"}

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setblocking(0)

class Value: value = None

def listener(client, container):
	
	client.sendto(b"", (ADDRESS, PORT))
	last_handshake = time.time()
	
	while True:
		
		try:
			data = packet.decode(client.recv(PACKET_SIZE), formats)
			last_handshake = time.time()
			print("SERVER RESPONSE:", data)
			container.value = data
		
		except Exception as ex:
			
			if time.time() - last_handshake > 2:
				try:
					client.sendto(b"", (ADDRESS, PORT))
					last_handshake = time.time()
				
				except: time.sleep(0.01)
		
		
def sender(client, container):
	while True:
		if container.value:
			client.sendto(container.value, (ADDRESS, PORT))
			container.value = None
		else: time.sleep(send_delay)
		


print("started")

rx_container, tx_container = Value(), Value()

listener(client, rx_container)
#rx_task = threading.Thread(target=listener, args=(client, rx_container), daemon=True)
#tx_task = threading.Thread(target=sender, args=(client, tx_container), daemon=True)
#rx_task.start()
#tx_task.start()
"""
while True:

	data = {0:(random.randint(0,30),), 1:[random.uniform(-100,100) for i in range(3)], 2:[random.uniform(-100,100) for i in range(2)]}
	data = packet.encode(data)
	tx_container.value = data
		
	
	time.sleep(1)
"""


