#!/usr/bin/python

import sys, serial, argparse
import numpy as np
import glob
from collections import deque
from time import sleep

import matplotlib.animation as animation
import matplotlib.pyplot as plt 

N_ELECTRODES = 4
class AnalogPlot:
	def __init__(self, strPort, maxLen):
		self.ser = serial.Serial(strPort, 19200)
		self.s0 = deque([0.0]*maxLen)
		self.s1 = deque([0.0]*maxLen)
		self.s2 = deque([0.0]*maxLen)
		self.s3 = deque([0.0]*maxLen)
		self.maxLen = maxLen

	# add to buffer
	def addToBuf(self, buf, val):
		if len(buf) < self.maxLen:
			buf.append(val)
		else:
			buf.pop()
			buf.appendleft(val)

	# add data
	def add(self, data):
		assert(len(data) == N_ELECTRODES) 
		self.addToBuf(self.s0, data[0])
		self.addToBuf(self.s1, data[1])
		self.addToBuf(self.s2, data[2])
		self.addToBuf(self.s3, data[3])

	# update plot
	def update(self, frameNum, a0, a1, a2, a3):

		while self.ser.inWaiting() > 10:
			try:
				line = self.ser.readline()
				data = [float(val) for val in line.split()]
				# print data
				if(len(data) == N_ELECTRODES): 
					self.add(data)
					a0.set_data(range(self.maxLen), self.s0)
					a1.set_data(range(self.maxLen), self.s1)
					a2.set_data(range(self.maxLen), self.s2)
					a3.set_data(range(self.maxLen), self.s3)
			except KeyboardInterrupt:
				print('exiting')
		
		#return a0, 

	def close(self):
		self.ser.write(b"s")  
		self.ser.flush()
		self.ser.close()		

def press(event, a0, a1, a2, a3):
    sys.stdout.flush()

    if event.key == '1':
        if a0.get_linestyle() == 'None':
            a0.set_linestyle('-')
            print ('sensor', event.key, 'on')
        else:
            a0.set_linestyle('None')
            print ('sensor', event.key, 'off')
    if event.key == '2':
        if a1.get_linestyle() == 'None':
            a1.set_linestyle('-')
            print ('sensor', event.key, 'on')
        else:
            a1.set_linestyle('None')
            print ('sensor', event.key, 'off')
    if event.key == '3':
        if a2.get_linestyle() == 'None':
            a2.set_linestyle('-')
            print ('sensor', event.key, 'on')
        else:
            a2.set_linestyle('None')
            print ('sensor', event.key, 'off')
    if event.key == '4':
        if a3.get_linestyle() == 'None':
            a3.set_linestyle('-')
            print ('sensor', event.key, 'on')
        else:
            a3.set_linestyle('None')
            print ('sensor', event.key, 'off')

def main():

	if sys.platform.startswith('win'):
		ports = ['COM' + str(i + 1) for i in range(256)]

	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this is to exclude your current terminal "/dev/tty"
		ports = glob.glob('/dev/ttyACM*')

	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.usb*')

	else:
		raise EnvironmentError('Unsupported platform')
	
	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			print("Serial port: ", s)
			s.close()
			result.append(port)
		except (OSError, serial.SerialException):
			pass
	
	if len(result) > 1:
		print ('Too many ports to choose from')
		exit(0)
	if len(result) < 1:
		print ('No ports found')
		exit(0)
	if len(result) is 1:
		print ('Found serial port: ', result)

	strPort = result[0]

	print ('Connecting...')
	analogPlot = AnalogPlot(strPort, 500)

	# wait for port to open
	while analogPlot.ser.isOpen() == 0:
		print ('...')
		sleep(1)
	sleep(2)

	print ('Connected!')

	analogPlot.ser.write(b"b") # b => transform to byte   

	fig = plt.figure()
	ax 	= plt.axes(xlim=(0, 500), ylim=(0, 1023))
	a0, = ax.plot([], [])
	a1, = ax.plot([], [])
	a2, = ax.plot([], [])
	a3, = ax.plot([], [])

	fig.canvas.mpl_connect('key_press_event', lambda event: press(event, a0, a1, a2, a3))

	anim = animation.FuncAnimation(fig, analogPlot.update, 
								 fargs=(a0,a1,a2,a3,), 
								 interval=1)
	
	plt.show()
	analogPlot.close()

	print('exiting.')

if __name__ == '__main__':
	main()

# serial monitor open = port then becomes occupied