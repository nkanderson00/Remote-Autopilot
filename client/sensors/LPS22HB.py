import time
import smbus

#i2c address
LPS22HB_I2C_ADDRESS	= 0x5C
#
LPS_ID				= 0xB1
#Register 
LPS_INT_CFG		    = 0x0B		#Interrupt register
LPS_THS_P_L		    = 0x0C		#Pressure threshold registers
LPS_THS_P_H		    = 0x0D
LPS_WHO_AM_I	    = 0x0F		#Who am I
LPS_CTRL_REG1	    = 0x10		#Control registers
LPS_CTRL_REG2	    = 0x11
LPS_CTRL_REG3	    = 0x12
LPS_FIFO_CTRL	    = 0x14		#FIFO configuration register
LPS_REF_P_XL	    = 0x15		#Reference pressure registers
LPS_REF_P_L		    = 0x16
LPS_REF_P_H		    = 0x17
LPS_RPDS_L		    = 0x18		#Pressure offset registers
LPS_RPDS_H			= 0x19
LPS_RES_CONF		= 0x1A		#Resolution register
LPS_INT_SOURCE		= 0x25		#Interrupt register
LPS_FIFO_STATUS	    = 0x26		#FIFO status register
LPS_STATUS			= 0x27		#Status register
LPS_PRESS_OUT_XL	= 0x28		#Pressure output registers
LPS_PRESS_OUT_L	    = 0x29
LPS_PRESS_OUT_H	    = 0x2A
LPS_TEMP_OUT_L		= 0x2B		#Temperature output registers
LPS_TEMP_OUT_H		= 0x2C
LPS_RES			    = 0x33		#Filter reset register

class LPS22HB(object):
	
	def __init__(self, address=LPS22HB_I2C_ADDRESS):
		super(LPS22HB, self).__init__()
		self._address = address
		self._bus = smbus.SMBus(1)
		self.LPS22HB_RESET()						 #Wait for reset to complete
		self._write_byte(LPS_CTRL_REG1 ,0x02)		#Low-pass filter disabled , output registers not updated until MSB and LSB have been read , Enable Block Data Update , Set Output Data Rate to 0 
	
	def LPS22HB_RESET(self):
		buf = self._read_u16(LPS_CTRL_REG2)
		buf |= 0x04
		self._write_byte(LPS_CTRL_REG2,buf)			   #SWRESET Set 1
		
		while buf:
			buf = self._read_u16(LPS_CTRL_REG2)
			buf &= 0x04
	
	def LPS22HB_START_ONESHOT(self):
		buf = self._read_u16(LPS_CTRL_REG2)
		buf |= 0x01										 #ONE_SHOT Set 1
		self._write_byte(LPS_CTRL_REG2,buf)
	
	def _read_byte(self,cmd):
		return self._bus.read_byte_data(self._address,cmd)
	
	def _read_u16(self,cmd):
		lsb = self._bus.read_byte_data(self._address,cmd)
		msb = self._bus.read_byte_data(self._address,cmd+1)
		return (msb	<< 8) + lsb
	
	def _write_byte(self,cmd,val):
		self._bus.write_byte_data(self._address,cmd,val)

	def read_pressure_temperature_data(self):
		
		u8_buf = [0,0,0]
		self.LPS22HB_START_ONESHOT()
		press_data = temp_data = None
		
		if (self._read_byte(LPS_STATUS)&0x01) == 0x01:  # a new pressure data is generated
			u8_buf[0] = self._read_byte(LPS_PRESS_OUT_XL)
			u8_buf[1] = self._read_byte(LPS_PRESS_OUT_L)
			u8_buf[2] = self._read_byte(LPS_PRESS_OUT_H)
			press_data = ((u8_buf[2]<<16)+(u8_buf[1]<<8)+u8_buf[0])/4096.0
		
		if (lps22hb._read_byte(LPS_STATUS)&0x02) == 0x02:   # a new temperature data is generated
			u8_buf[0] = self._read_byte(LPS_TEMP_OUT_L)
			u8_buf[1] = self._read_byte(LPS_TEMP_OUT_H)
			temp_data = ((u8_buf[1]<<8)+u8_buf[0])/100.0
			
		return press_data, temp_data

	def read_pressure_data(self):
		u8_buf = [0,0,0]
		self.LPS22HB_START_ONESHOT()
		press_data = None

		if (self._read_byte(LPS_STATUS)&0x01) == 0x01:  # a new pressure data is generated
			u8_buf[0] = self._read_byte(LPS_PRESS_OUT_XL)
			u8_buf[1] = self._read_byte(LPS_PRESS_OUT_L)
			u8_buf[2] = self._read_byte(LPS_PRESS_OUT_H)
			press_data = ((u8_buf[2]<<16)+(u8_buf[1]<<8)+u8_buf[0])/4096.0

		return press_data

	def read_temperature_data(self):
		u8_buf = [0,0]
		self.LPS22HB_START_ONESHOT()
		temp_data = None

		if (self._read_byte(LPS_STATUS)&0x02) == 0x02:   # a new temperature data is generated
			u8_buf[0] = self._read_byte(LPS_TEMP_OUT_L)
			u8_buf[1] = self._read_byte(LPS_TEMP_OUT_H)
			temp_data = ((u8_buf[1]<<8)+u8_buf[0])/100.0

		return temp_data


if __name__ == '__main__':
	
	lps22hb = LPS22HB()
	
	while True:
		time.sleep(0.1)
		pressure, temperature = lps22hb.read_pressure_temperature_data()
		print("Pressure = %6.2f hPa , Temperature = %6.2f °C"%(pressure,temperature), end="\r")
