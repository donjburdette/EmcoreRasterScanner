import sys
sys.path.append('/Users/donjburdette/TraycerCode/RasterScanner/Motion_control/Zaber_motion/Don_zaber/')
sys.path.append('/Users/donjburdette/TraycerCode/RasterScanner/EmcoreAPI/')
import numpy as np
import socket
import matplotlib.pyplot as plt
import matplotlib
import math

from Zaber_Motion_Library import *
#from EmcoreAnalysis2 import *
import EmcoreAnalysis as analysis

# set scanning parameters (Note: Something is wronge the values supplied to convert distance to turns - fix)

xMin = 50 # mm
xMax = 70 # mm
xStep = 0.5  # mm
yMin = 155 # mm
yMax = 185 # mm
yStep = 0.5 # mm
step_delay_x = 2.0  # seconds
step_delay_y = 0.1 # seconds

# write the data out to a file
fileSaveName = 'data_out_test.txt'

# set-up Emcore connection ---------------
#TCP_IP = '192.168.1.109'  # old Traycer router
#TCP_IP = '192.168.1.108'  # old Traycer lab routher
TCP_IP = '192.168.1.8'

TCP_PORT = 5000   #5555
BUFFER_SIZE = 100
MESSAGE1 = "SetFreq 204.00"   
MESSAGE2 = "GetData       "

sleepTime = 0.05 # seconds  

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# set frequency
print "Setting frequency"
s.send(MESSAGE1)
data = s.recv(BUFFER_SIZE)  # confirm data was received
print "received data:", data

# let lasers settle
settleTime = 2  # seconds
print "Laser settling for: ", settleTime, "seconds."
time.sleep(settleTime)

# ----------------------------------------

# open serial connection ---------------------------
io = serial_connection('/dev/tty.usbserial', '<2Bi')
# define the device
deviceX = linear_slide(io, 1, id = 'x_axis', verbose = True, run_mode = STEP)
deviceY = linear_slide(io, 2, id = 'y_axis', verbose = True, run_mode = STEP)
# --------------------------------------------------

set_max_position(deviceX,200000,0.1)
set_max_position(deviceY,550000,0.1)

# send the stages home
go_home(deviceX)
go_home(deviceY)

# go to start position
print 'xStart (mm): ', xMin, 
print 'yStart (mm): ', yMin, 
go_to_abs_pos(deviceX,xMin,2)
go_to_abs_pos(deviceY,yMin,2)

# collect 2D raster scan data ------------
#calculate the number of steps in x and y
numStepsX = calc_number_steps(xMin,xMax,xStep)
numStepsY = calc_number_steps(yMin,yMax,yStep)

print 'Steps in X: ', numStepsX
print 'Steps in Y: ', numStepsY

# initilize the image matrix
image = np.zeros((numStepsX,numStepsY))

scan_direction = 1
sleepTime = 0.05 # seconds 

for i in range(0, numStepsX):
	#move_relative(deviceX,xStep,step_delay_x)
	if(scan_direction == 1):
		move_relative(deviceX,xStep,step_delay_x)
		for j in range(0,numStepsY):
			move_relative(deviceY,yStep,step_delay_y)
			# get data
			s.send(MESSAGE2)
			time.sleep(sleepTime)
			dataString = s.recv(BUFFER_SIZE) 
			data, timeStamp, LaserTemp1, LaserTemp2 = analysis.dataParse2(dataString)
			data = math.sqrt(data)
			image[i][j] = data
			print i, j, data
		scan_direction = 0
	elif(scan_direction == 0):
		move_relative(deviceX,xStep,step_delay_x)
		for j in range(0,numStepsY):
			move_relative(deviceY,-yStep,step_delay_y)
			print i, j, data
			# get data (clean-up into a nice function when not rushed)
			s.send(MESSAGE2)
			time.sleep(sleepTime)
			dataString = s.recv(BUFFER_SIZE) 
			data, timeStamp, LaserTemp1, LaserTemp2 = analysis.dataParse2(dataString)
			data = math.sqrt(data)
			image[i][numStepsY - j - 1] = data  # this needs to be fixed to take into account the direction change
			# it can be fixed in image processing
		scan_direction = 1

# ----------------------------------------

# save the image to file -----------------
analysis.save_image(fileSaveName,image)
# ----------------------------------------

# close the serial connection
io.close()

# make a plot of the image
figureCount = 0
plt.figure(figureCount)
figureCount = figureCount + 1
plt.imshow(image, aspect = 'auto')
#plt.ylabel("y (mm)")
#plt.xlabel("x (mm)")
plt.title("Sample Image")
plt.colorbar()
#plt.clim(0,1)

matplotlib.rcParams.update({'font.size':18})
plt.show()




