# -*- coding: utf-8 -*-
"""
Found some code on GitHub from user deshipu. Used as a driver for BNO055 with the
micropython language we have been using.

@author: deshipu
"""
import pyb
import time
import ustruct
from micropython import const
'''from adafruit_register.i2c_struct import Struct, UnaryStruct'''

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BNO055.git"

_CHIP_ID = const(0xa0)

CONFIG_MODE = const(0x00)
ACCONLY_MODE = const(0x01)
MAGONLY_MODE = const(0x02)
GYRONLY_MODE = const(0x03)
ACCMAG_MODE = const(0x04)
ACCGYRO_MODE = const(0x05)
MAGGYRO_MODE = const(0x06)
AMG_MODE = const(0x07)
IMUPLUS_MODE = const(0x08)
COMPASS_MODE = const(0x09)
M4G_MODE = const(0x0a)
NDOF_FMC_OFF_MODE = const(0x0b)
NDOF_MODE = const(0x0c)
_POWER_NORMAL = const(0x00)
_POWER_LOW = const(0x01)
_POWER_SUSPEND = const(0x02)
_MODE_REGISTER = const(0x3d)
_PAGE_REGISTER = const(0x07)
_TRIGGER_REGISTER = const(0x3f)
_POWER_REGISTER = const(0x3e)
_ID_REGISTER = const(0x00)

## Device address needed for I2C to communicate with BNO055
DEVICE_ADDR = const(0x28)

## The system trigger register
SYS_TRIGGER_REG = const(0x3F)

## The calibration status register for the IMU
CALIB_STAT_REG = const (0x35)

## The unit selection register
UNIT_SEL_REG = const (0x3B)

## The register address of the STATUS register in the MMA845x
STATUS_REG = const (0x39)

## The register address of the OUT_X_MSB register in the MMA845x
PITCH_MSB = const (0x1F)

## The register address of the OUT_X_LSB register in the MMA845x
PITCH_LSB = const (0x1E)

## The register address of the OUT_Y_MSB register in the MMA845x
ROLL_MSB= const (0x1D)

## The register address of the OUT_Y_LSB register in the MMA845x
ROLL_LSB = const (0x1C)

## The register address of the OUT_Z_MSB register in the MMA845x
HEADING_MSB = const (0x1B)

## The register address of the OUT_Z_LSB register in the MMA845x
HEADING_LSB = const (0x1A)

## The register address of the DATA_CFG_REG register in the MMA845x which is
#  used to set the measurement range to +/-2g, +/-4g, or +/-8g
XYZ_DATA_CFG = const (0x4F08)


class BNO055:

    def __init__(self, i2c, address=DEVICE_ADDR):
        """
        Creates an object of the BNO055 class that is used to read orientation angles
        :param i2c: an i2c object that is used to communicate between the board and the IMU
        :param address: the address of the IMU device
        """
        self.i2c = i2c
        self.buffer = bytearray(2)
        self._dev_id = ord(i2c.mem_read(1, address, 0x00))
        if self._dev_id == 0xA0:
            self._works = True
        else:
            self._works = False
            raise ValueError ('Unknown accelerometer device ID ' 
                + str(self._dev_id) + ' at I2C address ' + str(address))
        time.sleep(0.01)
        self.mode = NDOF_MODE
        self.i2c.mem_write(self.mode, DEVICE_ADDR, _MODE_REGISTER) 
        time.sleep(0.01)

    def calibrate(self):
        """ Calibrates the IMU by resetting the IMU, setting the heading angle back to 0"""
        self.i2c.mem_write(CONFIG_MODE, DEVICE_ADDR, _MODE_REGISTER)
        self.i2c.mem_write(32, DEVICE_ADDR, SYS_TRIGGER_REG) 
        time.sleep(1)
        self.i2c.mem_write(NDOF_MODE, DEVICE_ADDR, _MODE_REGISTER) 
        print("Done calibrating")
            
    def set_degrees_units (self):
        """ Changes the output units to degrees for reading the IMU. """
        degrees_mode = int('0b11111011', 2)
        self.i2c.mem_write(degrees_mode, DEVICE_ADDR, UNIT_SEL_REG)        
        
    def change_mode (self, MODE):
        """
        Method that changes the mode of the chip
        :param MODE: the mode to set the chip in
        """
        self.i2c.mem_write(MODE, DEVICE_ADDR, _MODE_REGISTER)

    def get_roll (self):
        """ Get the roll angle from the BMO055 in degrees, assuming
        that the accelerometer was correctly calibrated at the factory.
        @return The measured roll angle in degrees """
        data = self.i2c.mem_read(2, DEVICE_ADDR, ROLL_LSB)
        unpacked = ustruct.unpack('<h', data)
        return unpacked[0] / 16

    def get_pitch (self):
        """ Get the pitch angle from the BMO055 in degrees, assuming
        that the accelerometer was correctly calibrated at the factory.
        @return The measured roll angle in pitch """
        data = self.i2c.mem_read(2, DEVICE_ADDR, PITCH_LSB)
        unpacked = ustruct.unpack('<h', data)
        return unpacked[0] / 16

    def get_heading (self):
        """ Get the heading angle from the BMO055 in degrees, assuming
        that the accelerometer was correctly calibrated at the factory.
        @return The measured roll angle in heading """
        data = self.i2c.mem_read(2, DEVICE_ADDR, HEADING_LSB)
        unpacked = ustruct.unpack('<h', data)
        return unpacked[0] / 16
