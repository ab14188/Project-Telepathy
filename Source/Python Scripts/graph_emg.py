#!/usr/bin/python

import pylab
import serial
import time
import datetime
import sys
import getopt
import os
import subprocess
from time import sleep


numDataVals = 120 # 10 * 12 words 

trainingDir = 'user_study/results/test4/mouthed/'

parentPath = os.getcwd()

graphDir = parentPath + '/user_study/results/test4/Graphs_mouthed' 
print ('printing')
print (parentPath)
print (graphDir)

if not os.path.exists(graphDir):
	os.makedirs(graphDir)

wordNum = 0

# Loop through each words
os.chdir(trainingDir)
for i in os.listdir(os.getcwd()):
	print ('Gesture: ' + i)
	# Loop through each raw data file in the word set
	os.chdir(parentPath + "/" + trainingDir + "/" + i)
	# Create a new subdirectory in the graph directory
	subGraphDir = graphDir  + '/' + i
	if not os.path.exists(subGraphDir):
		os.makedirs(subGraphDir)
	
	for dataFile in os.listdir(os.getcwd()):
		print (dataFile)
		data = pylab.loadtxt(dataFile)
		pylab.plot( data[:,0], label='')
		pylab.plot( data[:,1], label='')
		pylab.plot( data[:,2], label='')
		pylab.plot( data[:,3], label='')
		pylab.ylim([0,1000])
		pylab.legend()
		pylab.title("Word: " + i + "    |    Timestamp: " + dataFile)
		pylab.xlabel("Timestep")
		pylab.ylabel("Amplitude")
		#pylab.show()
		pylab.savefig(subGraphDir + '/' + dataFile)
		pylab.clf()
	wordNum += 1

exit(0)
