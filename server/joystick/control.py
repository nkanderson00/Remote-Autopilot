import inputs
from server import server, packet
import threading

port = 42069
packet_size = 18

s = server.Server(port, "UDP", packet_size)
queue = s.queue
s.run()


formats = {0: "f", 1: "f", 2: "f", 3: "f", 4: "f", 5: "f"}
axis_codes = {"ABS_Z": [0,1], "ABS_RZ": [1,1], "ABS_X": [2,1], "ABS_Y": [3,1], "ABS_HAT0X": [4,1], "ABS_HAT0Y": [5,1]}

try:
	gamepad = inputs.devices.gamepads[0]
	
except IndexError:
	raise inputs.UnpluggedError("Joystick not detected")
		
while True:

	events = []
	
	events.extend(gamepad.read())
		
	event_dict = {}
		
	for e in events:
		
		if axis_codes.get(e.code) is not None:
			axis_codes[e.code][1] = max(axis_codes[e.code][1], e.state)
			event_dict[axis_codes[e.code][0]] = (e.state/axis_codes[e.code][1],)
			
			if event_dict:
				print("sending", event_dict)
				queue.data.append(packet.encode(event_dict, formats))
			
