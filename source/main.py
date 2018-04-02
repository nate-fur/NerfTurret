# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 09:50:49 2018

@author: mecha25
"""
import pyb
import micropython
import gc
import time
import ProjectClasses
import cotask
import print_task
import task_share
import mybno055
import ustruct

# Creates a global variable for the angle coords of all board spots
grid = [[[0,0],[0,0],[0,0],[0,0],[0,0]] for i in range(5)]

micropython.alloc_emergency_exception_buf (100)


def heading_motor_fun ():
    """ Function which runs for Task 1, which runs a motor controller loop for
    our pan (heading) motor. Once the control loop sets the pan axis
    to its setpoint, the pan_OK share is set to 1."""
    frq = 100
    heading_setpoint_share.put(90)
    heading_motor = ProjectClasses.MotorDriver(3,pyb.Pin.board.PA10,
                                               pyb.Pin.board.PB4,pyb.Pin.board.PB5)
    heading_controller = ProjectClasses.Controller(8.5, 0.2, 0.5,
                                                   heading_setpoint_share.get(), frq)
    heading_motor.set_duty_cycle(0)

    while True:
        heading_controller.set_setpoint(heading_setpoint_share.get())
        heading = heading_share.get()

        if heading_controller.is_done(heading):
            heading_OK.put(1)

        power_level = heading_controller.control_loop(heading)
        heading_motor.set_duty_cycle(power_level)

        yield (0)

       
def pitch_motor_fun ():
    """ Function which runs for Task 1, which runs a motor controller loop for
    our tilt (pitch) motor. Once the control loop is finished and the tilt axis
    is at its setpoint, the tilt_OK share is set to 1."""
    frq2 = 100
    pitch_setpoint_share.put(0)
    pitch_motor = ProjectClasses.MotorDriver(5, pyb.Pin.board.PC1, 
                                             pyb.Pin.board.PA0, pyb.Pin.board.PA1)
    pitch_controller = ProjectClasses.Controller(5.8, 0.25, .25,
                                                 pitch_setpoint_share.get(), frq2)
    pitch_motor.set_duty_cycle(0)

    while True:
        pitch_controller.set_setpoint(pitch_setpoint_share.get())
        pitch = pitch_share.get()

        if pitch_controller.is_done(pitch):
            pitch_OK.put(1)

        power_level2 = pitch_controller.control_loop(pitch)
        pitch_motor.set_duty_cycle(power_level2)

        yield(0)


def IMU_fun ():
    """ A function to run Task 3, the IMU task, which reads Euler angle data from
    the IMU. The pan angle (IMU's heading angle) will be communicated via a share 
    with the pan motor, and the tilt angle (IMU's pitch angle) will be communicated
    via a share with the tilt motor. """
    i2c = pyb.I2C(1, pyb.I2C.MASTER)
    imu = mybno055.BNO055(i2c)
    
    while True: 
        heading_share.put(imu.get_heading())
        pitch_share.put(imu.get_pitch())
        yield(0)


def servo_fun ():
    """ A function to run task 4 to shoot a nerf dart at the board. This function
    will shoot when both axes have reached their setpoint locations. It causes 
    a servo to rotate which pushes a dart into position to fire."""
    
    servo = ProjectClasses.Servo(2, pyb.Pin.board.PB3, 2)
    forward_position = 1150
    back_position = 1600
    servo.set_pulse_width(back_position)
    done_count = 2  # count to signify when servo is done firing
    go_count = 50
    state = 1
    while True:
        if state == 1:

            if calibrated_share.get() == 1:
                state = 2

        elif state == 2:

            go = heading_OK.get() and pitch_OK.get()
            ready = trigger_ready_share.get()
            if go and ready:
                go_count -= 1

                if go_count == 0:  # need to delay so that the gun doesn't fire too early
                    go_count = 50
                    servo.set_pulse_width(forward_position)
                    done_count -= 1

                    if done_count == 0:  # need to wait until the gun is done shooting until its placed back to start
                        done_count = 2
                        servo.set_pulse_width(back_position)
                        heading_OK.put(0)
                        pitch_OK.put(0)
                        trigger_ready_share.put(0)

        yield(0)


def input_fun():
    """ A function to receive the setpoints from a PC for each motor controller
    based on the turret coordinates and the selected board square """
    global grid
    state = 1
    while True:
        if state == 1:  # Do nothing until we are done calibrating
            if calibrated_share.get() == 1:
                state = 2

        elif state == 2:
            if vcp.any():
                try:
                    row_b = vcp.read(4)
                    if row_b is not None:
                        row = ustruct.unpack("i", row_b)[0]
                        if row == 7:  # Done to handle the bug where sending 0x03 as row/col would cause keyb intr.
                            row = 3
                            
                        col_b = vcp.read(4)
                        if col_b is not None:
                            col = ustruct.unpack("i", col_b)[0]
                            if col == 7:
                                col = 3
                        if (row >= 0 and row < 5) and (col >= 0 and col < 5):
                            heading_setpoint_share.put(grid[row][col][0])
                            pitch_setpoint_share.put(grid[row][col][1])
                            trigger_ready_share.put(1)

                except ValueError:  # Sometimes unpacking data from USB would cause unwanted ValueErrors
                    pass
            
        yield(0)


def calib_fun():
    """ Function to calibrate the nerf gun turret for aiming at specific squares on the board. It
     targets 9 of the 25 squares and sets the coordinates of these square accordingly """
    global grid
    set_coord_share.put(0)
    heading_setpoint_share.put(90)
    pitch_setpoint_share.put(0)
    state = 1
    while True:
        if state == 1:

            for row in range(0, 5, 2):
                for column in range(0, 5, 2):
                    while set_coord_share.get() == 0:
                        yield(0)
   
                    grid[row][column] = [heading_share.get(), pitch_share.get()]
                    set_coord_share.put(0)

            calibrated_share.put(1)
            generate_values()
            state = 2
        
        yield(0)


def generate_values():
    """ Function to fill in the 16 coords of unfilled squares using linear approximations of the coordinates
    found in the calibration function"""
    global grid
    # Generate values for even columns
    for row in range(1,4,2):
        for col in range(0,5,2):
            grid[row][col][0] = (grid[row-1][col][0] + grid[row+1][col][0]) / 2
            grid[row][col][1] = (grid[row-1][col][1] + grid[row+1][col][1]) / 2

    # Generate values for odd columns
    for row in range(5):
        for col in range(1,4,2):
            grid[row][col][0] = (grid[row][col+1][0] + grid[row][col-1][0]) / 2
            grid[row][col][1] = (grid[row][col+1][1] + grid[row][col-1][1]) / 2


def move_motor_fun():
    """ Function to move the motor to each of the 9 squares that we need coordinates for during our calibration run"""
    heading_motor = ProjectClasses.MotorDriver(3,pyb.Pin.board.PA10,
                                               pyb.Pin.board.PB4,pyb.Pin.board.PB5)
    heading_motor.set_duty_cycle(0)                                           
    pitch_motor = ProjectClasses.MotorDriver(5, pyb.Pin.board.PC1,
                                             pyb.Pin.board.PA0, pyb.Pin.board.PA1)
    pitch_motor.set_duty_cycle(0)
    state = 1
    pitch_adj = 2
    heading_adjust = 2
    while True:
        if state == 1:                
            char = vcp.read(1)
            if char is not None:
                if char == b'w':
                    print_task.put('w')
                    pitch_setpoint_share.put(pitch_setpoint_share.get()+pitch_adj)

                elif char == b'a':
                    print_task.put('a')
                    heading_setpoint_share.put(heading_setpoint_share.get()-heading_adjust)

                elif char == b's':
                    print_task.put('s')
                    pitch_setpoint_share.put(pitch_setpoint_share.get()-pitch_adj)

                elif char == b'd':
                    print_task.put('d')
                    heading_setpoint_share.put(heading_setpoint_share.get()+heading_adjust)

                elif char == b' ':
                    set_coord_share.put(1)
                
            if calibrated_share.get() == 1:
                state = 2
                
            yield(0)
            
        elif state == 2:
            yield(0)


if __name__ == "__main__":
    print ('\033[2JTesting scheduler in cotask.py\n')

    i2c = pyb.I2C(1, pyb.I2C.MASTER)
    imu = mybno055.BNO055(i2c)
    imu.calibrate()  # Resets the heading axis of the IMU on startup so that its angle is 0
    heading_motor = ProjectClasses.MotorDriver(3,pyb.Pin.board.PA10,
                                               pyb.Pin.board.PB4,pyb.Pin.board.PB5)
    heading_motor.set_duty_cycle(20)  # Slightly adjust the turret angle to a low positive value
    time.sleep(0.1)
    heading_motor.set_duty_cycle(0)

    # Creating all of the intertask communications variables
    heading_share = task_share.Share ('f', thread_protect = True, name = "heading_share")
    pitch_share = task_share.Share ('f', thread_protect = True, name = "pitch_share")
    heading_setpoint_share = task_share.Share ('f', thread_protect = True, name = "heading_setpoint")
    pitch_setpoint_share = task_share.Share ('f', thread_protect = True, name = "pitch_setpoint")
    heading_OK = task_share.Share ('f', thread_protect = True, name = "heading_OK")
    pitch_OK = task_share.Share ('f', thread_protect = True, name = "pitch_OK")
    trigger_ready_share = task_share.Share ('f', thread_protect = True, name = "trigger_ready_share")
    set_coord_share = task_share.Share ('f', thread_protect = True, name = "set_coord")
    calibrated_share = task_share.Share ('f', thread_protect = True, name = "calibrated")

    # Assigns a each of the above functions to the a task variable
    task1 = cotask.Task (heading_motor_fun, name = 'Heading Motor', priority = 1, period = 10, profile = True, trace = False)
    task2 = cotask.Task (pitch_motor_fun, name = 'Pitch_Motor', priority = 2, period = 10, profile = True, trace = False)
    task3 = cotask.Task (IMU_fun, name = 'IMU', priority = 1, period = 10, profile = True, trace = False)
    task4 = cotask.Task (servo_fun, name = 'Shooting_Servo', priority = 4, period = 25, profile = True, trace = False)
    task5 = cotask.Task (input_fun, name = 'Get_Input', priority = 4, period = 25, profile = True, trace = False)
    task6 = cotask.Task (calib_fun, name = 'Calibrate', priority = 5, period = 25, profile = True, trace = False)
    task7 = cotask.Task (move_motor_fun, name = 'Move_Motor', priority = 5, period = 25, profile = True, trace = False)

    # Append all of the tasks to the task list that will run continuously
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    cotask.task_list.append(task3)
    cotask.task_list.append(task4)
    cotask.task_list.append(task5)
    cotask.task_list.append(task6)
    cotask.task_list.append(task7)
    
    gc.collect ()

    vcp = pyb.USB_VCP ()

    while True:
        cotask.task_list.pri_sched()
    
