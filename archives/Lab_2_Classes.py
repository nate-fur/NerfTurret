import pyb

class Encoder:
   ''' This class implements an encoder to be read from the ME 405 board '''

   def __init__(self, timer1, pin1, pin2, timer2):
      ''' This method creates a timer object and 2 timer channel objects for the encoder.
          The arguments passed in are a timer channel and 2 pins. 
          @param timer1: gives the constructor a timer channel number to use
          @param pin1: gives the position of the pin for channel 1
          @param pin2: gives the position of the pin for channel 2
          @param timer2 gives the timer channel for the encoder callbacks'''      
      self.position = 0
      self.prev_count = 0
      self.current_count = 0
      self.tim = pyb.Timer(timer1)
      self.tim.init (prescaler=0, period=0xffff)
      self.timer = pyb.Timer(timer2, freq=100)
      pinA = pyb.Pin (pin1, pyb.Pin.OUT_PP)
      self.ch1 = self.tim.channel(1, pyb.Timer.ENC_AB, pin = pinA)
      pinB = pyb.Pin (pin2, pyb.Pin.OUT_PP)
      self.ch2 = self.tim.channel(2, pyb.Timer.ENC_AB, pin = pinB)
      self.timer.callback(self.add_distance)
   
   def read(self):
      ''' Reads and returns the current position 
          @return: returns the current position of the encoder'''
      return self.position

   def zero(self):
      ''' Sets the timer count to zero '''
      self.position = 0

   def add_distance(self, timer):
      ''' Checks for encoder overflow and calculates the total distance traveled
          @param timer: a timer object needed for the callback to function'''
      self.current_count = self.tim.counter()
      delta_count = self.current_count - self.prev_count
      if (delta_count > 32767):
         delta_count -= 65536
      elif (delta_count < -32767):
         delta_count += 65536
      self.prev_count = self.current_count
      self.position += delta_count

class MotorDriver:
    '''This class creates a motor driver for use with the ME405 board.'''
    def __init__ (self, timer, pinENA, pinINP, pinINN, frequ = 20000):
        '''This method initializes a motor driver object with the specified pins and channels'''
        #print ('Creating a motor driver')
        ENA = pyb.Pin(pinENA, pyb.Pin.OUT_PP)
        IN1A = pyb.Pin(pinINP, pyb.Pin.OUT_PP)
        IN2A = pyb.Pin(pinINN, pyb.Pin.OUT_PP)
        tim = pyb.Timer (timer, freq=frequ)
#        ENA = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
#        IN1A = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
#        IN2A = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
#        tim3 = pyb.Timer (3, freq=20000)
        self.ch1 = tim.channel (1, pyb.Timer.PWM, pin=IN1A)
        self.ch2 = tim.channel (2, pyb.Timer.PWM, pin=IN2A)       
        ENA.high ()
    def set_duty_cycle (self, level):
        '''This method allows the user to control the magnitude and direction of the motor'''
        if level == 0:
           self.ch1.pulse_width_percent (0)
           self.ch2.pulse_width_percent (0)           
        if level > 0:
           if level > 100:
               level = 100
           self.ch1.pulse_width_percent (level)
           self.ch2.pulse_width_percent (0)
        if level < 0:
           if level < -100:
               level = -100
           level = level*(-1)
           self.ch2.pulse_width_percent (level)
           self.ch1.pulse_width_percent (0)
           level = level*(-1)
        #print ('Setting duty cycle to ' + str (level))
        return

class Controller:
    '''This class creates a PI Controller for general purposes.'''
    def __init__ (self, kp, ki, setpoint, frq):
       '''This constructor creates the neccesary variables for the controller to function.
          @param kp the proportional gain given to the controller
          @param ki the integral gain given to the controller
          @param setpoint the setpoint that the controller is trying to reach
          @param frq the frequency that the control loop runs at'''
       self.kp = kp
       self.ki = ki
       self.setpoint = setpoint
       self.__flag = False
       #self.timer = pyb.Timer(2, freq=frq)
       #self.timer.callback(self.set_flag)
       self.__delta_t = 1/frq
       self.__esum = 0
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
       error = self.setpoint-data
       self.__esum += error * self.__delta_t
       output = self.kp * error + self.ki * self.__esum
       self.__tsum += self.__delta_t
       self.__itr_cnt += 1
       #used to create data strings with callbacks
#       self.__time_list[self.__itr_cnt] = self.tsum
#       self.__data_list[self.__itr_cnt] = data
       self.__flag = False
       return output      
       
    def print_data(self):
        '''Prints out the data of the controller after the control loop has executed'''
        for i in range(len(self.__time_list)):
            print(self.__time_list[i],self.__data_list[i])
        print('end')         
        


       
