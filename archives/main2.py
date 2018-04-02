# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 09:50:49 2018

@author: mecha25
"""
import pyb
import micropython
import gc
import Lab_2_Classes
import cotask
import task_share
import print_task

global per

micropython.alloc_emergency_exception_buf (100)

def motor1_fun ():
    ''' Function which runs for Task 1, which runs a motor controller loop for 
    our first motor.'''
    frq = 1000/25 #25 is the period of the task to run
    #used for varying frequency
    #frq = 1000/(per)
    motor1 = Lab_2_Classes.MotorDriver(3,pyb.Pin.board.PA10,pyb.Pin.board.PB4,pyb.Pin.board.PB5)
    encoder1 = Lab_2_Classes.Encoder(8,pyb.Pin.board.PC6,pyb.Pin.board.PC7,6)
    controller1 = Lab_2_Classes.Controller(0.02, 0, 100000, frq)
    encoder1.zero()
    qflag = True
    state = 1
    while True:
       if state == 1:
          enc1_position = encoder1.read()
          time = controller1.tsum
          power_level = controller1.control_loop(enc1_position)
          motor1.set_duty_cycle(power_level)
          if qflag == True:
             qt1.put(time, in_ISR = False)
             qp1.put(enc1_position, in_ISR = False)
          if qt1.full():
              qflag = False
       yield (0)
       
def motor2_fun ():
    ''' Function which runs for Task 1, which runs a motor controller loop for 
    our second motor.'''
    frq2 = 1000/25 #25 is the period of the task to run
    motor2 = Lab_2_Classes.MotorDriver(5,pyb.Pin.board.PC1,pyb.Pin.board.PA0,pyb.Pin.board.PA1)
    encoder2 = Lab_2_Classes.Encoder(4, pyb.Pin.board.PB6, pyb.Pin.board.PB7,7)
    controller2 = Lab_2_Classes.Controller(0.025, 0, 40000, frq2)
    encoder2.zero()
    qflag = True
    state = 1
    while True:
       if state == 1:
          enc2_position = encoder2.read()
          time2 = controller2.tsum
          power_level2 = controller2.control_loop(enc2_position)
          motor2.set_duty_cycle(power_level2)
          
          if qflag == True:
             qt2.put(time2, in_ISR = False)
             qp2.put(enc2_position, in_ISR = False)
          if qt2.full():
              qflag = False
       yield (0)
         
if __name__ == "__main__": 
    print ('\033[2JTesting scheduler in cotask.py\n')

    share0 = task_share.Share ('i', thread_protect = True, name = "Share_0")
    qt1 = task_share.Queue ('f', 500, thread_protect = True, overwrite = False)
    qp1 = task_share.Queue ('f', 500, thread_protect = True, overwrite = False)
    qt2 = task_share.Queue ('f', 500, thread_protect = True, overwrite = False)
    qp2 = task_share.Queue ('f', 500, thread_protect = True, overwrite = False)
    #used to test different periods and plot the results
    #per = eval(input())                     
    task1 = cotask.Task (motor1_fun, name = 'Motor_1', priority = 1, period = 25, profile = True, trace = False)
    task2 = cotask.Task (motor2_fun, name = 'Motor_2', priority = 2, period = 25, profile = True, trace = False)
    cotask.task_list.append (task1)
    cotask.task_list.append (task2)
    
    gc.collect ()
    time = []
    pos = []
    
    vcp = pyb.USB_VCP ()
    while not vcp.any ():
        cotask.task_list.pri_sched ()   
    vcp.read()
    #used for outputting data to plot the results
#    while not qt1.empty():
#       time.append(qt1.get())
#       pos.append(qp1.get())
#
#    for i in range(len(time)):
#       print(time[i],pos[i])
#    print("end")
#    
    print ('\n' + str (cotask.task_list) + '\n')
    print (task_share.show_all ())
    print (task1.get_trace ())
    print ('\r\n')
    
    
                           