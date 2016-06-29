import glob
import os 
import sys
import numpy as np
from numpy import mean, sqrt, square
import matplotlib.pyplot as plt 

#Function to display graphs  
def display(file_array):
	plot_ID = 1 

	for file in file_array : 
		x_axis	= np.arange(0, file[:,0].size, 1)	
		plt.subplot(5, 2, plot_ID)					# change number of subplots for now arbitrary 
		plt.ylim((0, 1023))
		plt.xlim((0, 1000))
		
		for i in range(0,4) : 
			plt.plot(x_axis, file[:, i])	
			
		plot_ID += 1
		
		#print(extract_features(file, 1))
		print("NEW file features: ", extract_features(file, 4))

	plt.show()
	
def extract_features (file, inputs) : # each file has its own feature vector
	feature_vector = []

	for i in range(0, inputs) :

		feature_vector.append(np.mean(file[:,i]))							#0 # Related to firing point & energy information
		feature_vector.append(np.amax(file[:,i]))							#1 # Related to firing point & energy information
		feature_vector.append(np.sqrt(np.mean(np.square(file[:,i]))))		#2 # Relates to constant force and non fatiguing contraction & energy information  
		feature_vector.append(WL(file, i))								    #3 # Relates to the complexity of the signal
		feature_vector.append(np.std(file[:,i]))							#4 # Related to firing point & energy information
		feature_vector.append('SKIP')
		#feature_vector.append(np.var(file[:,i]))	#6
	return feature_vector

def WL(file, i) : # Relates to the complexity of the signal 
	WL_results = []
	
	for j in range(0, len(file) - 1):
		result = file[j+1,i] - file[j,i]
		WL_results.append(result)

	return np.sum(WL_results)
#SD_ZC and SSC 

# could add SSC = > slope sign change _ relates to the frequency, number of times the slope of the EMG signal changes, could be good only if we determin exactly
# at what point word starts 
# note: will have to get rid of other movement such as twitching .. 

def main() :
	global storeDir
	file_array = []

	for file in glob.glob('' + storeDir + '/*') :
		data = np.loadtxt(file)
		file_array.append(data)
		
	display(file_array)
		
if __name__ == '__main__':
	
	storeDir = ' '

	try: 
		storeDir = sys.argv[1]
		if not os.path.exists(storeDir):
			print('Error: Directory does not exist')
			exit()
	except: 
		print('Error: Provide Directory')
		exit()

	main()