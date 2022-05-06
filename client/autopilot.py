class Autopilot:

	def __init__(self, plane):

		self.enabled = False
		self.plane = plane

		self.home = None
		self.set_home()

		self.heading_mode = 0
		self.altitude_lock = False
		self.aileron_angle = 0
		self.elevator_angle = 0
		self.rudder_angle = 0
		self.throttle = 0
		self.heading = 0
		self.altitude = 0
		self.pitch = 0
		self.roll = 0
		self.speed = 0
		self.distance = 0
		self.distance_to_target = 0
		self.distance_to_home = 0

		self.target_lat = 0
		self.target_lon = 0
		self.target_alt = 0
		self.target_heading = 0

		self.home_lat = 0
		self.home_lon = 0
		self.home_alt = 0
		
		
	def fly_to(self, latitude, longitude):
				
		while self.enabled:
			bearing = self.plane.gps.heading_to(latitude, longitude)
			self.turn_to_heading(bearing)
			
			if self.plane.gps.distance_to(latitude, longitude) < 10:
				self.circle()
		
	
	def turn_to_heading(self, bearing):
		#rotate servos until gyro matches 15 degrees
		#rotation amount is proportional to size of angle between heading and bearing up to 15 degrees
		current_angle = self.plane.gyro.orientation[1]		
		current_heading = self.plane.gyro.heading
		
		#will decrease as heading approaches bearing
		target_angle = min(abs((current_heading-bearing + 180) % 360 - 180)/2, 15)


		if abs(current_heading-bearing) < 180:
			target_angle *= -1
		
		
		self.aileron_angle += (current_angle-target_angle)/10
		
		self.plane.ailerons.rotate(self.aileron_angle)
		
	
	def circle(self, radius=0, latitude=None, longitude=None):
		
		while self.enabled:
			break
			#radius = self.plane.gps.distance_to(latitude, longitude)

		

	#land the plane using ultrasonic sensor and gps
	def land(self):
		pass
	
	def return_to_home(self):
		self.fly_to(self.home)
		self.circle()
		
		
	def set_home(self):
		self.home = self.plane.gps.location
