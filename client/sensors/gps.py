import serial
import pynmea2
import threading
import time
from ..telemetry import packet, radio
from math import *

talkers = ("GGA", "VTG")


class GPS_Poller(threading.Thread):

    def __init__(self, callback):
        super().__init__()
        self.daemon = True
        self.active = True
        self.callback = callback
        self.ser = serial.Serial("/dev/ttyUSB1", baudrate=115200, timeout=1)

    def run(self):

        while self.active:
            try:

                data = self.ser.readline().decode()
                if not data: continue
                parsed = pynmea2.parse(data)
                sentence_type = type(parsed).__name__

                if sentence_type in talkers:
                    self.callback(sentence_type, parsed)

            except:
                pass

        self.ser.close()


    def stop(self):
        self.active = False
        self.join()


class GPS:

    def __init__(self, plane=None):
        self.plane = plane
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.num_sats = 0
        self.gps_qual = 0
        self.true_track = 0
        self.speed = 0
        self.poller = GPS_Poller(self.nmea_callback)
        self.poller.start()

    def __del__(self):
        self.stop()

    def __repr__(self):
        return f"Position <{self.latitude}, {self.longitude}>, Altitude: {self.altitude}, Speed: {self.speed}"

    def heading_to(self, latitude, longitude, altitude):
        x = cos(latitude) * sin(self.longitude - longitude)
        y = cos(self.latitude) * sin(latitude) - sin(self.latitude) * cos(latitude) * cos(self.longitude - longitude)
        bearing = degrees(atan2(x, y))
        return bearing

    def get_location(self):
        return self.latitude, self.longitude

    def distance_to(self, latitude, longitude):
        #using haversine formula in meters
        R = 6371000
        dlat = radians(latitude - self.latitude)
        dlon = radians(longitude - self.longitude)
        a = sin(dlat / 2) * sin(dlat / 2) + cos(self.latitude) * cos(latitude) * sin(dlon / 2) * sin(dlon / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        d = R * c
        return d

    def nmea_callback(self, sentence_type, nmea):
        print("GPS:", nmea)

        if sentence_type == "GGA":
            self.latitude = nmea.lat
            self.longitude = nmea.lon
            self.altitude = nmea.altitude
            self.num_sats = nmea.num_sats
            self.gps_qual = nmea.gps_qual
            data = {6: (nmea.lat, nmea.lon), 7: (nmea.altitude,),
                            8: (nmea.num_sats,), 9: (nmea.gps_qual,)}

        elif sentence_type == "VTG":
            self.true_track = nmea.true_track
            self.speed = nmea.spd_over_grnd_kts
            data = {10: (nmea.true_track,), 11: (float(nmea.spd_over_grnd_kts),)}

        else:
            return

        self.plane.to_radio(data)

    def stop(self):
        self.poller.stop()


if __name__ == "__main__":

    gps = GPS()
    time.sleep(10)
    gps.stop()
    print(gps)
    print(gps.distance_to(0, 0))
    print(gps.heading_to(0, 0, 0))
    print(gps.get_location())
    print(gps.speed)
    print(gps.true_track)
    print(gps.altitude)
    print(gps.num_sats)
    print(gps.gps_qual)
