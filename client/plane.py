# running on pi
from autopilot import Autopilot
from servo import servo
import sensors
from telemetry import radio


"""
this is the main file for the plane
it beings everything together
"""


class Plane:

    STANDARD_TURN_ANGLE = 15

    def __init__(self):

        self.radio = radio.Radio(self.radio_callback)
        self.radio.start()

        self.gps = sensors.gps.GPS(self)
        self.gyro = sensors.gyro.Gyro(self)
        self.autopilot = Autopilot(self)

        self.throttle = servo.Throttle(0)
        self.rudder = servo.Servo(1)
        self.ailerons = servo.Servo(2)
        self.elevator = servo.Servo(3)

        self.servo_ids = {0: self.throttle, 1: self.rudder, 2: self.ailerons, 3: self.elevator}

    def radio_callback(self, data):
        """receives decoded data from the radio and passes it to the servos."""

        print("SERVER RESPONSE:", data)

        for k, v in data.items():

            if k == 0:
                self.throttle.rotate(v[0])

            elif k <= 3:
                self.autopilot.disable()
                self.servo_ids[k].rotate(v[0])

            elif k == 4:
                self.ailerons.trim(v[0])

            elif k == 5:
                self.elevator.trim(v[0])

    def to_radio(self, data: dict):
        self.radio.send(data)

    def run(self):
        self.gps.run()
        self.gyro.run()
        self.autopilot.run()
        self.radio.start()

    def stop(self):
        self.gps.stop()
        self.gyro.stop()
        self.autopilot.stop()
        self.radio.stop()