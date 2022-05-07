import warnings

class Autopilot:

	def __init__(self, plane):

		self.enabled = False
		self.plane = plane

		self.home = None
		self.set_home()

		self.heading_lock = False
		self.heading_mode = 0 #0 is MAINTAIN, 1 is WAYPOINT
		self.target_heading = 0
		self.target_lat = 0
		self.target_lon = 0
		self.altitude_lock = False
		self.target_altitude = 400

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

		self.target_aileron_angle = 0
		self.target_elevator_angle = 0

		self.home_lat = 0
		self.home_lon = 0
		self.home_alt = 0
		

	def mainloop(self):
		"""theoretically, once the plane reaches the target location it will float around it weirdly"""
				
		while self.enabled:

			if self.heading_lock:
				match self.heading_mode:
					case 0:
						self.turn_to_heading(self.target_heading)
					case 1:
						self.turn_to_heading(self.plane.gps.get_heading_to(self.target_lat, self.target_lon))

			if self.altitude_lock:
				self.approach_altitude(self.target_altitude)
			
			#if self.plane.gps.distance_to(latitude, longitude) < 10:
				#self.circle()

	def lock_heading(self, mode: int = 0):
		if mode not in range(2):
			warnings.warn("Invalid heading mode. Value must be 0 or 1.", RuntimeWarning)
		self.heading_lock = True
		self.heading_mode = mode
		self.target_heading = self.plane.gyro.heading

	def unlock_heading(self):
		self.heading_lock = False
		self.heading_mode = 0

	def set_heading(self, heading: int):
		if heading < 0 or heading > 360:
			warnings.warn("Invalid heading. Value must be between 0 and 360.", RuntimeWarning)
			heading = min(max(heading, 0), 360)
		self.target_heading = heading

	def set_waypoint(self, latitude, longitude, altitude = None):
		self.target_lat = latitude
		self.target_lon = longitude
		self.altitude = self.plane.gps.altitude
		if altitude is not None:
			self.set_altitude(altitude)

	def lock_altitude(self):
		self.altitude_lock = True
		self.target_altitude = self.plane.gps.altitude

	def unlock_altitude(self):
		self.altitude_lock = False

	def set_altitude(self, altitude: int):
		if altitude < 0:
			warnings.warn("Invalid altitude. Value must be greater than 0.", RuntimeWarning)
		else:
			self.target_altitude = altitude
	
	def turn_to_heading(self, bearing):
		target_roll_angle = self.plane.STANDARD_TURN_ANGLE
		current_heading = self.plane.gyro.heading
		
		#will decrease as heading approaches bearing
		target_angle = min(abs((current_heading-bearing + 180) % 360 - 180)/2, 15)

		if abs(current_heading-bearing) < 180:
			target_angle *= -1
			target_roll_angle *= -1

		#need to determine an aileron angle that will be sufficient to turn the plane to the target heading without going crazy
		#the angle has to be proportional to the difference between the current heading and the target heading
		self.target_aileron_angle += (target_roll_angle-self.plane.gyro.roll)/10 #10 is the smoothness. arbitrary.
		self.plane.ailerons.rotate(self.target_aileron_angle)

	def approach_altitude(self, altitude):
		"""
		need to determine an elevator angle that will not cause a stall if flying up.
		the optimal elevator angle will depend on the maximum climb rate.
		climb rate can be determined by the change in altitude over time.
		air pressure is a good indicator of climb rate.

		Find the
		"""
		
	
	def circle(self, radius, latitude, longitude):
		"""Fly in a circle around the latitude and longitude with a radius of radius"""

		#not really a circle but it should stay in the general area of the circle
		while self.enabled:
			bearing = self.plane.gps.get_heading_to(latitude, longitude)
			self.turn_to_heading(bearing)


		

	#land the plane using ultrasonic sensor and gps
	def land(self):
		pass
	
	def return_to_home(self):
		self.set_heading(self.plane.gps.get_heading_to(*self.home))
		self.mainloop(*self.home)
		#self.circle()
		
		
	def set_home(self):
		self.home = self.plane.gps.location

	def disable(self):
		self.enabled = False
		self.plane.to_radio({17: 0})

	def enable(self):
		self.enabled = True
		self.plane.to_radio({17: 1})
