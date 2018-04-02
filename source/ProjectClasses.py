import pyb


class MotorDriver:
    """ Creates a motor driver for use with the ME405 nucleo board. """

    def __init__ (self, timer, pinENA, pinINP, pinINN, frequ=20000):
        """
        Initializes a motor driver object with the specified pins and channels.
        :param timer:
        :param pinENA:
        :param pinINP:
        :param pinINN:
        :param frequ:
        """
        ENA = pyb.Pin(pinENA, pyb.Pin.OUT_PP)
        IN1A = pyb.Pin(pinINP, pyb.Pin.OUT_PP)
        IN2A = pyb.Pin(pinINN, pyb.Pin.OUT_PP)
        tim = pyb.Timer (timer, freq=frequ)
        self.ch1 = tim.channel (1, pyb.Timer.PWM, pin=IN1A)
        self.ch2 = tim.channel (2, pyb.Timer.PWM, pin=IN2A)       
        ENA.high ()
    def set_duty_cycle (self, level):
        """
        A method to set the speed for the motor using different pulse width percents on the motor timer channels
        :param level: the speed to set the motor to run at (comes as an output of a control loop
        """
        if level == 0:
            self.ch1.pulse_width_percent (0)
            self.ch2.pulse_width_percent (0)

        elif level > 0:
            if level > 100:
                level = 100
            self.ch1.pulse_width_percent (level)
            self.ch2.pulse_width_percent (0)

        elif level < 0:
            if level < -100:
                level = -100
            level = level*(-1)
            self.ch2.pulse_width_percent (level)
            self.ch1.pulse_width_percent (0)
            level = level*(-1)


class Controller:
    """This class creates a PI Controller for general purposes."""

    def __init__ (self, kp, ki, kd, setpoint, frq):
        """ This constructor creates the neccesary variables for the controller to function.
        @param kp the proportional gain given to the controller
        @param ki the integral gain given to the controller
        @param setpoint the setpoint that the controller is trying to reach
        @param frq the frequency that the control loop runs at"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.__flag = False
        self.__delta_t = 1/frq
        self.__esum = 0
        self.__lastErr = 0
        time = 700
        self.__time_list = [0.0] * int(time)
        self.__data_list = [0.0] * int(time)
        self.__tsum = 0.0
        self.__itr_cnt = 0
       

    def set_setpoint (self, setpoint):
        '''This method allows a user to put a new setpoint.
        @param setpoint the new setpoint to give the controller'''
        self.setpoint = setpoint
  
    def set_kp (self, kp):
        '''This method allows a user to put a new proportional gain.
        @param kp the proportional gain given to the controller'''
        self.kp = kp

    def set_ki (self, ki):
        '''This method allows a user to put a new integral gain.
        @param ki the integral gain given to the controller'''
        self.ki = ki
       
    def set_kd (self, kd):
        '''This method allows a user to put a new integral gain.
        @param ki the integral gain given to the controller'''
        self.kd = kd

    def set_flag(self, timer):
        '''This method is not used when running through the task lists,
        but it sets a flag telling the control loop to execute if ran as a
        call back.
        @param timer is the timer channel needed to run callbacks'''
        self.__flag = True

    def control_loop (self, data):
        '''This method computes closed loop controller output, using proportional and integral gain
        @param data the incoming data needed to compare with the setpoint
        @return the output coming from the control loop'''
        error = self.setpoint - data
        if self.__esum < 150:
           self.__esum += error * self.__delta_t
        dErr = (error-self.__lastErr)/self.__delta_t
        output = self.kp * error + self.ki * self.__esum +self.kd*dErr
        self.__tsum += self.__delta_t
        self.__itr_cnt += 1
        self.__lastErr = error
        self.__flag = False
        return output
       
    def is_done(self, data):
        ''' A method to return if the incoming data is close enough to the setpoint
        for the controller to be consided done.
        @return a boolean value signifying if control loop is done '''
        if abs(self.setpoint - data) < 2.5:
            return True
        return False


class Servo:
    """ This class implements the control of a servo used for actuating the nerf
    dart into a motor for firing. """
    
    def __init__(self, timer, pin, chan):
        """This method initializes a servo object with the specified pins and channels"""
        servo_pin = pyb.Pin(pin, pyb.Pin.OUT_PP)
        tim = pyb.Timer(timer, prescaler=79, period=19999)
        self.ch = tim.channel (chan, pyb.Timer.PWM, pin=servo_pin)
         
    def set_pulse_width (self, level):
        """This method allows the user to control the position of the servo"""
        self.ch.pulse_width(level)
