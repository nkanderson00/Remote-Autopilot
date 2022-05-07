from . import LPS22HB
from . import SHTC3

"""
Only want to poll this sensor every now and then to save power.
GPS is the primary source of altitude so pressure is really only
needed when determining max climb rate
"""

class Meteorology(LPS22HB, SHTC3):

    def __init__(self, plane):
        super(Meteorology, self).__init__()
        self.plane = plane
        self._pressure = 0
        self._temperature = 0
        self._humidity = 0

    @property
    def get_pressure(self):
        if p := self.read_pressure_data():
            self._pressure = p
            self.plane.to_radio()
        return self._pressure

    @property
    def get_temperature(self):
        if t := self.read_temperature_data():
            self._temperature = t
        return self._temperature

    @property
    def get_humidity(self):
        if h := self.read_humidity():
            self._humidity = h
        return self._humidity

    def get_pressure_altitude(self):
        #convert hPa to inHg
        inHg = self.pressure * 0.0295299830714
        #mean seal level pressure is 29.92 inHg
        #altitude in feet
        return (29.92 - inHg) * 1000 + self.plane.gps.initial_altitude


