from zaber_device import *
from zaber_multidevice import *

import time

# Units are all with respect to 1 mm 
linear_units = {
        'mm':                       1,
        'um':                       1e-3,
        'inches':                   25.4,
        'thou':                     25.4e-3,
        'mil':                      25.4e-3,
        }

class linear_slide(zaber_device):
    ''' linear_slide(connection, 
                 device_number,
                 id, 
                 steps_per_rev = 200, 
                 mm_per_rev = 6.35, 
                 units = 'mm',
                 run_mode = CONTINUOUS,
                 action_handler = None,
                 verbose = False):
    
    Modified zaber_device with support for more meaningful linear units.

    steps_per_rev is the number of steps per revolution of the stepper.
    mm_per_rev is the number of linear mm that corresponds to each revolution of the stepper.


    See the documentation for zaber_device for the full usage.
    '''
    def __init__(self, 
                 connection, 
                 device_number, 
                 id = None,
                 steps_per_rev = 200, 
                 mm_per_rev = 6.35, 
                 units = 'mm',
                 run_mode = CONTINUOUS,
                 action_handler = None,
                 verbose = False):

        mm_per_step = float(mm_per_rev)/float(steps_per_rev)
        self.move_units = units
        
        zaber_device.__init__(self, connection, device_number, id = id,
                units_per_step = mm_per_step*linear_units[self.move_units],
                run_mode = run_mode,
                action_handler = action_handler,
                verbose = verbose)
        

class multiaxis_linear_slides(zaber_multidevice):
    '''multiaxis_linear_slides(connection, 
                               id, 
                               devices, 
                               steps_per_rev = 200, 
                               mm_per_rev = 6.35, 
                               units = 'mm',
                               run_mode = CONTINUOUS,
                               action_handler = None,
                               verbose = False)

    Modified zaber_multidevice with support for more meaningful linear units.
    
    steps_per_rev is the number of steps per revolution of the stepper.
    mm_per_rev is the number of linear mm that corresponds to each revolution of the stepper.

    See the documentation for zaber_multidevice for the full usage.
    '''

    def __init__(self, 
                 connection,  
                 devices, 
                 id = None,
                 steps_per_rev = 200, 
                 mm_per_rev = 6.35, 
                 units = 'mm',
                 run_mode = CONTINUOUS,
                 action_handler = None,
                 verbose = False):

        mm_per_step = float(mm_per_rev)/float(steps_per_rev)
        
        zaber_multidevice.__init__(self,
                                   connection, 
                                   devices,
                                   id = id,
                                   units_per_step = mm_per_step,
                                   move_units = units,
                                   run_mode = run_mode,
                                   action_handler = action_handler, 
                                   verbose=verbose)        
        

def linear_slide_example(io):
    
    x_axis = linear_slide(io, 1, id = 'x_axis', verbose = True)
    # y_axis = linear_slide(io, 2, id = 'y_axis')
    # z_axis = linear_slide(io, 3, id = 'z_axis', verbose = True)
    
    x_axis.home()
    # y_axis.home()
    # z_axis.home()
    
    x_axis.move_relative(100)

    # y_axis.move_absolute(100)
    # y_axis.home()
    # y_axis.move_absolute(0)
    x_axis.move_absolute(20)
    # z_axis.move_relative(10)
    # z_axis.move_absolute(50)
    # z_axis.move_relative(-10)

    x_axis.move_relative(100)    
    
    # Will block
    io.open()

def multiaxis_example(io):
    
    axes = {'x':1, 'y':2, 'z':3}
    
    gantry_system = multiaxis_linear_slides(io, axes, 'gantry', verbose = True)
    gantry_system.home()
    gantry_system.move_relative({'x':100, 'y':200, 'z':0})
    gantry_system.move_absolute({'x':50, 'y':150, 'z':0})
    
    gantry_system.new_meta_command('zigzag', (('move_relative',{'x':10, 'y':10}),\
                                              ('move_relative',{'x':20, 'y':-20}),\
                                              ('move_relative',{'x':10, 'y':10})))

    gantry_system.new_meta_command('two_zigzags', (('zigzag',),('repeat',2)))
    
    gantry_system.two_zigzags()

    gantry_system.home()

    # The alternative, thread safe way of calling the move commands
    io.packet_q.put((('','gantry'),('move_relative',{'x':75, 'z':20})))
    io.packet_q.put((('','gantry'),('move_relative',{'x':75, 'y':200, 'z':20})))
    
    try:
        io.open()
    except:
        io.close()

def step_example(io):

    '''A short example that should move stuff around, that is thread safe, and also does not block.
         This is preliminary, and may not function properly.
    '''
    x_axis = linear_slide(io, 1, id = 'x_axis', verbose = True, run_mode = CONTINUOUS)
    # x_axis = linear_slide(io, 1, id = 'x_axis', verbose = True, run_mode = STEP)
    #x_axis = linear_slide(io, 1, id = 'x_axis', verbose = True)
    # x_axis.home()
    print '100'
    x_axis.move_absolute(100) 
    print '50'
    x_axis.move_absolute(50) 
    try:
        raw_input('yo!')
    except KeyboardInterrupt:
        pass

    io.close()


def examples(argv):
    '''A short example program that moves stuff around
    '''
    io = serial_connection('/dev/tty.usbserial', '<2Bi')
    # linear_slide_example(io)
    # multiaxis_example(io)
    step_example(io)

# Don code additions --------------------------------------
# -----------------------------
def go_home(linear_slide): 
# this function sends the linesar saber device to the home position
    linear_slide.do_now(1,blocking=True)
# ---------------------------

# ---------------------------
def go_to_abs_pos(linear_slide,absolute_position,delay): 
# this function sends the saber linear slider to an absolute position
    numTurns = convert_mm_to_turns(absolute_position)
    linear_slide.do_now(20 , numTurns, blocking=True)
    time.sleep(delay)     # ideally I'd read back from the serial port that 
                            # I reached the position, this is quick and dirty
                            # to meet Brad's deadline
# ---------------------------
def move_relative(linear_slide,distance,delay): 
# this function sends the saber linear slider to an absolute position
    numTurns = convert_mm_to_turns(distance)
    linear_slide.do_now(21 , numTurns, blocking=True)
    time.sleep(delay)     # ideally I'd read back from the serial port that 
                            # I reached the position, this is quick and dirty
                            # to meet Brad's deadline
# ---------------------------

def set_max_position(linear_slide,maxPosition,delay):
    # this function sets the maximum position that the stage can scan to
    #numTurns = convert_mm_to_turns(maxPosition)
    linear_slide.do_now(44,maxPosition)
    time.sleep(delay)

# ---------------------------
def get_position(linear_slide): 
# this function returns the stage's current position
    linear_slide.do_now(60)
# ---------------------------

# ---------------------------------
def linear_scan(linear_slide,min,max,stepSize):
    # example code illustrating linear step motion
    steps = calc_number_steps(min,max,stepSize)
    for i in range(0,steps):
        move_relative(linear_slide,stepSize,1)
        print i
        
# ---------------------------------------------

# ---------------------------------------------
def TwoD_scan(linear_slide1,linear_slide2,minX,maxX,xStep,minY,maxY,yStep):
    # example code illustrating 2D step motion
    numStepsX = calc_number_steps(minX,maxX,xStep)
    numStepsY = calc_number_steps(minY,maxY,yStep)
    delay = 1
    direction_flag = 1
    for i in range(0,numStepsX):
        move_relative(linear_slide1,xStep,delay)
        if(direction_flag == 1):
            for j in range(0,numStepsY):
                move_relative(linear_slide2,yStep,delay)
                print i, j
            direction_flag = 0
        if(direction_flag == 0):
            for j in range(0,numStepsY):
                move_relative(linear_slide2,-yStep,delay)
                print i, j
            direction_flag = 1



# ---------------------------------------------

def calc_number_steps(min,max,step_size):
    return int(1.0*(max-min)/(1.0*step_size))

def convert_mm_to_turns(distance):
    # there is something wrong with the conversion, fix later,
    # I may have to do my own calibration

    #mm_per_rev = 6.35 # mm per turn - when I have time, learn how to read rev_per_turn from the device instance
    #steps_per_rev = 1000.0
    # something wasn't right in those values

    # from measurements
    #300,000 steps = 150 mm
    # So 1 mm = 192 steps
    steps_per_mm = 2000.0  #  1923.0
    numTurns = steps_per_mm*float(distance)
    return numTurns
# ---------------------------------------------------------
if __name__ == "__main__":
    import sys
    examples(sys.argv)
    














