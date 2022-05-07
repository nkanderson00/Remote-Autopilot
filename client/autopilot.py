import warnings

class Autopilot:

	WAYPOINT_RADIUS_IGNORE = 50 #feet

	def __init__(self, plane):

		self.enabled = False
		self.plane = plane

		self.home = None
		self.set_home()

		self._heading_lock = False
		self._heading_mode = 0 #0 is MAINTAIN, 1 is WAYPOINT
		self._target_heading = 0
		self._target_lat = 0
		self._target_lon = 0
		self._altitude_lock = False
		self._target_altitude = 400

		self.aileron_angle = 0
		self.elevator_angle = 0
		self.rudder_angle = 0
		self.throttle = 0
		self.heading = 0
		self.altitude = 0
		self.pitch = 0
		self.roll = 0
		self.ground_speed = 0
		self.climb_rate = 0
		self._climb_angles = {}
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

			if self._heading_lock:
				match self._heading_mode:
					case 0:
						self.turn_to_heading(self._target_heading)
					case 1:
						if self.plane.gps.get_distance_to(self._target_lat, self._target_lon) > self.WAYPOINT_RADIUS_IGNORE:
							self.turn_to_heading(self.plane.gps.get_heading_to(self._target_lat, self._target_lon))

			if self._altitude_lock and self._target_altitude:
				self.approach_altitude()
			
			#if self.plane.gps.distance_to(latitude, longitude) < 10:
				#self.circle()

	def lock_heading(self, mode: int = 0):
		if mode not in range(2):
			warnings.warn("Invalid heading mode. Value must be 0 or 1.", RuntimeWarning)
		self._heading_lock = True
		self._heading_mode = mode
		self._target_heading = self.plane.gyro.heading
		self.plane.to_radio({18:(1,)})
		if not self.enabled:
			self.enable()

	def unlock_heading(self):
		self._heading_lock = False
		self._heading_mode = 0
		self.plane.to_radio({18: (0,)})

	def set_heading(self, heading: int):
		if heading < 0 or heading > 360:
			warnings.warn("Invalid heading. Value must be between 0 and 360.", RuntimeWarning)
			heading = min(max(heading, 0), 360)
		self._target_heading = heading

	def set_waypoint(self, latitude, longitude, altitude = None):
		self._target_lat = latitude
		self._target_lon = longitude
		self.altitude = self.plane.gps.altitude
		if altitude is not None:
			self.set_altitude(altitude)

	def lock_altitude(self):
		self._altitude_lock = True
		self._target_altitude = self.plane.gps.altitude
		self.plane.to_radio({19: (1,)})
		if not self.enabled:
			self.enable()

	def unlock_altitude(self):
		self._altitude_lock = False
		self.plane.to_radio({19: (0,)})

	def set_altitude(self, altitude: int):
		if altitude < 0:
			warnings.warn("Invalid altitude. Value must be greater than 0.", RuntimeWarning)
		else:
			self._target_altitude = altitude
	
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

	def approach_altitude(self):
		"""
		need to determine an elevator angle that will not cause a stall if flying up.
		the optimal elevator angle will depend on the maximum climb rate.
		climb rate can be determined by the change in altitude over time.
		air pressure is a good indicator of climb rate.

		Find the elevator angle where the rate of change of pressure is maximum
		"""

		#pressure_altitude = self.plane.meteorology.get_pressure_altitude()
		if abs(self.plane.gps.altitude - self._target_altitude) > 10:
			self.target_elevator_angle += (self._target_altitude-self.plane.gps.altitude)
			self.plane.elevators.rotate(self.target_elevator_angle)

	#land the plane using ultrasonic sensor and gps
	def land(self):
		pass
	
	def return_to_home(self):
		self.lock_heading(mode = 1)
		self.set_heading(self.plane.gps.get_heading_to(*self.home))
		self.mainloop()
		
	def set_home(self):
		self.home = self.plane.gps.location

	def disable(self):
		self.enabled = False
		self.plane.to_radio({17: (0,)})

	def enable(self):
		self.enabled = True
		self.plane.to_radio({17: (1,)})
