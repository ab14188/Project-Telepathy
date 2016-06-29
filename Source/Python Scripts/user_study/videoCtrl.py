import sys
import glob
import os.path
import serial
import numpy as np
import subprocess
import time
import datetime
import json
from timeit import default_timer

words 		= ['back', 'down', 'faster', 'forwards', 'left', 'no', 'right', 'slower', 'stop', 'turn', 'up', 'yes'] 	# set of words # add yes and no 
conditions 	= ['spoken', 'mouthed'] 																	# set of conditions 
N_ITEMS_PER_LINE = 4 																					# number of EMGs currently set to 6 should be 4 


# Arduino Management class
class ArduinoManagement():
	
# Function that starts the arduino
	def startArduino(self) : 
		# Starting the arduino
		print('Starting the Arduino')

	# Determining operating system
		if sys.platform.startswith('win'):
			ports = ['COM' + str(i + 1) for i in range(256)]
		elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
	        # this is to exclude your current terminal "/dev/tty"
			ports = glob.glob('/dev/ttyACM*')
		elif sys.platform.startswith('darwin'):
			ports = glob.glob('/dev/tty.usb*')
		else:
			raise EnvironmentError('Unsupported platform')

	# Detecting available ports 
		result = []
		for port in ports:
			try:
				s = serial.Serial(port)
				s.close()
				result.append(port)
			except (OSError, serial.SerialException):
				pass

	# Selecting port connected to the Arduino
		if len(result) > 1:
			print ('Too many ports, select one manually')
			currentNumber = 1
			for port in result:
				print (str(currentNumber) + ' ' + str(port))
				currentNumber+=1
			portNumber = int( input('port number?'))
			result = [result[portNumber-1]]
		if len(result) < 1:
			print ('No ports found')
			exit(0)
		if len(result) is 1:
			print ('Found serial port: ', result)

		strPort = result[0]
		print ('Found serial port: ', result)
		print ('Connecting...')

	# Connecting port to Arduino
		try:
			self.ser = serial.Serial(strPort, 19200)
		except:
			print ('Unable to connect to the Arduino via Serial')
			exit(1)

	    # Wait for port to open
		while self.ser.isOpen() == 0:
			print ('...')
			time.sleep(1)
		time.sleep(2)

		# Once port opened pause recording
		self.recordData = False
		self.ser.write(b"b")	# begin
		self.ser.write(b"p")	# pause 
		print ('Connected!')

# Function that saves the data in a certain directory 
	def savedata(self, savingDir, startTime, maxTime) :
		print('Starting data Capture')
		self.ser.write(b"b")
		self.recordData = True

	# Pre_init storage of data
		data = []
		for x in range(0, N_ITEMS_PER_LINE): 
			data.append( [] )
		
		i = 0

		currentTime = default_timer() - startTime
		time.sleep(1)
	
	# Read data from EMGs until the video terminates and store it in a data array 
		while(currentTime <= maxTime - 2.6):
			if (i % 100) == 0:
				print (i)
        
			line = self.ser.readline()
			print (line) 
			splitLine = [int(val) for val in line.split()]
			if(len(splitLine) == N_ITEMS_PER_LINE):
				for x in range(0, N_ITEMS_PER_LINE):
					data[x].append(splitLine[x])
				i += 1
			currentTime = default_timer() - startTime
			print("currentTime: ", currentTime, " max ", maxTime)
		
		#VM.playExampleVideo('./videos/spoken/green2.mp4')
		# Pause the Arduino from sending information 
		self.ser.write(b"p")
		time.sleep(2)
				
	# Save the data in a file 
		ts 			= time.time()
		filename 	= datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d %H_%M_%S')

		# Check the directory 
		if savingDir != '':
			print(savingDir)
			f = open(os.path.join(savingDir, filename), 'w')
		else:
			f = open(filename, 'w')

		# Write data to file
		for i in range(0, len(data[0])): 
			for x in range(0, N_ITEMS_PER_LINE): 
				f.write(str(data[x][i]))
				f.write(' ')
			f.write('\n')
		f.close()

	def exit_study(self) :
		print('Terminating study ')
		self.ser.write(b"s")
		

# Manages videos
class VideoManagement() :
	# Function that plays the video through vlc
	def playvideo(self, videoName) :
		p = subprocess.Popen(["C:\Program Files\VideoLAN\VLC/vlc.exe", videoName])
		return p

	# Get duration of video 
	def duration(self, videoName) : 
		result = subprocess.Popen(['ffprobe', videoName, '-print_format', 'json', '-show_streams', '-loglevel', 'quiet'], stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		return float(json.loads(result.stdout.read().decode('utf-8'))['streams'][0]['duration'])

	# Funcion used when practice round is running 
	def practiceRun():
		print('This function will be used for playing trainng videos')


	def playExampleVideo(self, videoName) :
		if videoName == './videos/spoken/green.mp4' :
			duration 	= self.duration(videoName) - 1
		else :
			duration 	= self.duration(videoName)
		startTime	= default_timer()
		self.playvideo(videoName)
		
		currentTime = default_timer() - startTime
		while (currentTime < duration ) :
			currentTime = default_timer() - startTime

	def exit_study(self, process):
		process.kill()



# Creates data storing directories for each new participant 
def createDirs() : 
	#Creates global directory for a participant
	folder 		= glob.glob("./results/*")
	storeDir 	= './results/test' + str(len(folder))
	os.mkdir(storeDir)
	
	#Create different directories for the different conditions and words
	for j in range (0, len(conditions)) :
		os.mkdir(storeDir + '/'+ conditions[j]) 
		for i in range (0, len(words)) :
			os.mkdir(storeDir + '/'+ conditions[j] + '/' + words[i]) 

	return storeDir



if __name__ == "__main__" :
	# create storing directories:
	storeDir = createDirs()

	# Set up managements and start Arduino
	videosDir 	=	'./videos'
	AM = ArduinoManagement()
	VM = VideoManagement()
	AM.startArduino()

	#exercise function
	#VM.practiceRun()

	# Repeated for all video files 
	for twice in range (0, 2) :
		for j in range(0, 12) :
			print(j)
			videoName1 	= videosDir + '/spoken/' + words[j] + '.mp4'
			videoName2 	= videosDir + '/spoken/' + words[j] + '_v4.mp4'
			savingDir 	= storeDir + '/spoken/'

			if not os.path.exists(videoName1) or not os.path.exists(videoName2)  :
				print("video does not exist")
			else :
				VM.playExampleVideo(videoName1)
				videoTime 	= (VM.duration(videoName2))	
				for i in range (0, 5) :  
					subp 		= VM.playvideo(videoName2) 
					currentTime = default_timer()
					AM.savedata(savingDir + words[j], currentTime, videoTime)

	# Exiting the study 
	AM.exit_study()
	VM.exit_study(subp)
	sys.exit()

# note can't stop the video .. pb var
# be able to run 2 different options : practice and then real study  
# provide indications before the study starts either by videos or providing general information on how the study will go through 