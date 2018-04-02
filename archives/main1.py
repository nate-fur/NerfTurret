# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 11:24:52 2018

@author: mecha25
"""
import time
import mybno055
import Lab_2_Classes
import pyb
from pyb import I2C

i2c = I2C(1, I2C.MASTER)
imu = mybno055.BNO055(i2c)
#imu.calibrate()

motor1 = Lab_2_Classes.MotorDriver()
controller1.set_setpoint(115)
controller1.set_kp(3.8)
controller1.set_ki(.05)
motor1.set_duty_cycle(0)   

'''
motor2 = Lab_2_Classes.MotorDriver()
controller2 =  Lab_2_Classes.Controller(0.05,0, 0, 200)

controller1.set_setpoint(5)
'''

print("Heading: " + str(imu.get_heading()))
print("Pitch: " + str(imu.get_pitch()))
print("Roll: " + str(imu.get_roll()))

input("Press key")
heading = imu.get_heading()
print(heading)


time.sleep(2)
vcp = pyb.USB_VCP ()

while not vcp.any ():
    if controller1.__flag:
        heading = imu.get_heading()
        power_level = controller1.control_loop(heading)
        print(power_level)
        motor1.set_duty_cycle(power_level)   
        heading = imu.get_heading()
        power_level = controller1.control_loop(heading)
        print(power_level)
        motor1.set_duty_cycle(power_level)
        
        
vcp.read()    
print("Done. heading: " + str(heading))
  
print("Roll: " + str(imu.get_roll()))
motor1.set_duty_cycle(0)   

