from icm20948 import ICM20948
import time
from math import *
import tilt_compensator
from ..telemetry import packet, client
import threading

class Sensor(ICM20948):

    mag_min = [0, 0, 0]
    mag_max = [0, 0, 0]

    def __init__(self):
        super().__init__()
        print("ICM20948 initiated. Proceed calibration.")

    def read_heading_pitch_roll(self):
        return tilt_compensator.correct(self)

    def read_and_calibrate_magnetometer_data(self):
        mag = self.read_magnetometer_data()
        self.update_mag_limits(mag)
        return mag

    def update_mag_limits(self, mag):
        self.mag_min = [min(self.mag_min[count], i) for count, i in enumerate(mag)]
        self.mag_max = [max(self.mag_max[count], i) for count, i in enumerate(mag)]



class Sensor_Poller(threading.Thread):


    def __init__(self, callback):
        super().__init__()
        self.daemon = True
        self.active = True
        self.callback = callback
        self.imu = Sensor()

    def run(self):

        while self.active:
            try:

                self.callback(*self.imu.read_heading_pitch_roll())
                time.sleep(0.1)

            except:
                pass

    def stop(self):
        self.active = False
        self.join()




class Gyro:

    heading = 0
    pitch = 0
    roll = 0

    def __init__(self, plane=None):
        self.plane = plane
        self.poller = Sensor_Poller(self.callback)
        self.poller.start()

    def __repr__(self):
        return f"Heading: {self.heading}, Pitch: {self.pitch}, Roll: {self.roll}"

    def callback(self, heading, pitch, roll):
        self.heading = heading
        self.pitch = pitch
        self.roll = roll
        print(round(heading), round(pitch), round(roll), "\t", end="\r")
        data_encoded = {12: (heading,), 13: (pitch,), 14: (roll,)}
        data_encoded = packet.encode(data_encoded, client.formats)
        self.plane.to_radio(data_encoded)


if __name__ == "__main__":
    gyr = Gyro()
    time.sleep(10)
    gyr.poller.stop()
    print(gyr)

