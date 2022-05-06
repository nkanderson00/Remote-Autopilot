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
		self.target_aileron_angle = 0

		self.home_lat = 0
		self.home_lon = 0
		self.home_alt = 0
		

	def fly_to(self, latitude, longitude):
		"""theoretically, once the plane reaches the target location it will float around it weirdly"""
				
		while self.enabled:
			self.turn_to_heading(self.plane.gps.heading_to(latitude, longitude))
			
			#if self.plane.gps.distance_to(latitude, longitude) < 10:
				#self.circle()
		
	
	def turn_to_heading(self, bearing):
		#rotate servos until gyro matches 15 degrees
		#rotation amount is proportional to size of angle between heading and bearing up to 15 degrees
		target_roll_angle = self.plane.STANDARD_TURN_ANGLE
		current_heading = self.plane.gyro.heading
		
		#will decrease as heading approaches bearing
		target_angle = min(abs((current_heading-bearing + 180) % 360 - 180)/2, 15)


		if abs(current_heading-bearing) < 180:
			target_angle *= -1
			target_roll_angle *= -1

		#need to determine an aileron angle that will be sufficient to turn the plane to the target heading without going crazy
		#the angle has to be proportional to the difference between the current heading and the target heading

		self.target_aileron_angle += (target_roll_angle-self.plane.gyro.roll)/10
		self.plane.ailerons.rotate(self.target_aileron_angle)
		
	
	def circle(self, radius, latitude, longitude):
		"""Fly in a circle around the latitude and longitude with a radius of radius"""

		#not really a circle but it should stay in the general area of the circle
		while self.enabled:
			bearing = self.plane.gps.heading_to(latitude, longitude)
			self.turn_to_heading(bearing)


		

	#land the plane using ultrasonic sensor and gps
	def land(self):
		pass
	
	def return_to_home(self):
		self.fly_to(*self.home)
		#self.circle()
		
		
	def set_home(self):
		self.home = self.plane.gps.location
