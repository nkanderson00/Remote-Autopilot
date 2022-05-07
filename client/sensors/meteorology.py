from . import LPS22HB
from . import SHTC3


class Meteorology(LPS22HB, SHTC3):

    def __init__(self):
        super(Meteorology, self).__init__()
        self.pressure = 0
        self.temperature = 0
        self.humidity = 0

    def get_pressure(self):
        if p := self.read_pressure_data():
            self.pressure = p

    def get_temperature(self):
        if t := self.read_temperature_data():
            self.temperature = t

    def get_humidity(self):
        if h := self.read_humidity_data():
            self.humidity = h

