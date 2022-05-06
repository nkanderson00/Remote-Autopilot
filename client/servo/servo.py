import configparser
import RPi.GPIO as GPIO

config = configparser.ConfigParser()
config.read("pinout.cfg")
pinout = config["INPUTS"]


#servo rotation values are 0-1
#7.5 is dead center for servos

class PWM:
	
	SERVO_MAX = 11
	SERVO_MIN = 4
	SERVO_MID = (SERVO_MAX+SERVO_MIN)/2
	
	def __init__(self, input_id):
		
		self.reverse = True
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pinout[input_id], GPIO.OUT)
		self.pwm = GPIO.PWM(pinout[input_id], 50)
		
		if input_id != 0:
			self.pwm.start(self.SERVO_MID)
			
		else:
			self.pwm.start(0)
			
			
	def rotate(self, value):
		if self.reverse:
			value = 1-value
		self.pwm.ChangeDutyCycle(value*(self.SERVO_MAX-self.SERVO_MIN)+self.SERVO_MIN)

			

class Servo(PWM):
	
	def __init__(self, input_id):
		super().__init__(input_id)
		self._trim = self.SERVO_MID
		
	@property
	def trim(self):
		return self._trim
		
	@trim.setter
	def trim(self, value):
		self._trim += value/10
		self._trim = max(min(self._trim, self.SERVO_MAX), self.SERVO_MIN)


class Throttle(Servo):

	def __init__(self, input_id):
		super().__init__(input_id)
		self.SERVO_MAX = 10
		self.SERVO_MIN = 5
		
			
