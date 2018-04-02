# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 18:31:22 2018

@authors: Nathaniel Furbeyre, Tyler Noxon, Kair Turbayev
"""

import serial
import struct
import time

#from matplotlib import pyplot as pyp

'''
def split():
    Formats and converts data retrieved from the serial port to be able to plot
    for line in serial_data:
        num_strs = line.split (' ')
        try:
            t = float(num_strs[0])
            p = float(num_strs[1])
        except (ValueError , IndexError):
            pass
        else:
            time.append(t)
            pos.append(p)
'''
def send_values(coords):
    ''' A function to get the setpoint, kp and ki values to sent to the motor
    controller on the microcontroller'''
    if coords[0] == 3:
        coords[0] = 7
    row = struct.pack("i", coords[0])
    ser.write(row)
    
    if coords[1] == 3:
        coords[1] = 7
    col = struct.pack("i", coords[1])
    ser.write(col)

coords = [2, 2]

with serial.Serial('/dev/ttyACM0',115200, 5) as ser:
    ser.write([0x04])
    time.sleep(0.5)
    ser.write([0x04]) 
    
    coord_count = 0
    while coord_count < 9:
        try:        
            value = input("Key: ")
            if value == ' ':
                coord_count += 1
            char = struct.pack("b", ord(value))
            ser.write(char)
        except TypeError:
            pass
    
    print("Done Calibrating... Entering Game Mode")
    
    while True:  
        coords[0] = eval(input("Row: "))
        coords[1] = eval(input("Column: "))        
        send_values(coords)

    print("done sending values")
