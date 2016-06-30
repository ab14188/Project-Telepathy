from struct import *
import time
import re
import datetime
import sys
from sys import argv
import getopt
import os
import subprocess
import csv
import numpy as np
import itertools

def readFeatures(file):
	features 	= []
	f 			= open(file)
	result 		= f.read()
	for token in result.split():
		try:
			features.append(float(token))
		except ValueError:
			print ("non float value detected")

	return features

def getSumVector(file):
	features =	readBinaryFile(file)
	#features = [abs(x) for x in features]
	featureAbs = []
	for x in features:
		z = [abs(y) for y in x]
		featureAbs.append(z)
	floats = [float(sum(x)) for x in zip(*featureAbs)]
	return floats

def getSumVectorHalf1(file):
	features =	readBinaryFile(file)
	featurehalf = features[:126]
	#features = [abs(x) for x in features]
	floats = [float(sum(x)) for x in zip(*featurehalf)]
	return floats

def getSumVectorHalf2(file):
	features =	readBinaryFile(file)
	featurehalf = features[126:]
	#features = [abs(x) for x in features]
	floats = [float(sum(x)) for x in zip(*featurehalf)]
	return floats

def readBinaryFile(file):
#for line in f
#remember 374 bytes per frame
	features = []
	f = open(file)
	result = f.read()
	#print result
	frameLength = len(result)/249
	bytearray = list(unpack(str(len(result))+'b', result))
	#bytearray = abs(bytearray)

	return [ bytearray[n:n+frameLength] for n,i in enumerate(bytearray) if n%(frameLength)==0 ] 

# Used when external software ..
def extract(file, programPath):
	return subprocess.check_output([programPath, file]) 

# Extracting features from data array: to test try different combinations of different features 
def extract_features(dataFile):
	data = np.loadtxt(dataFile)
	feature_vector = []

	for i in range(0, 4) :  # up to the number of sensors used 
		feature_vector.append(np.mean(data[:,i]))	      					#0  55 # Related to firing point & energy information
		feature_vector.append(np.amax(data[:,i]))							#1  51 # Related to firing point & energy information
		#feature_vector.append(np.amin(data[:,i]))							##  51
		feature_vector.append(np.sqrt(np.mean(np.square(data[:,i]))))		#2 # 56 Relates to constant force and non fatiguing contraction & energy information  
		#feature_vector.append(WL(data, i))								    #3 # 14 Relates to the complexity of the signal
		#feature_vector.append(np.std(data[:,i]))							###4 56 # Related to firing point & energy information
		feature_vector.append(np.sum(data[:,i]))
		#feature_vector.append(np.var(data[:,i]))
	return feature_vector

def WL(file, i) : # Relates to the complexity of the signal 
	WL_results = []
	for j in range(0, len(file) - 1):
		result = file[j+1,i] - file[j,i]
		WL_results.append(result)

	return np.sum(WL_results)


#Function that combines different features
def combine_features(feature_array) :
	combinations 	= []
	featurenumb 	= int(len(feature_array)/4)
	splitEMGS 		= [feature_array[x:x+featurenumb] for x in range(0, len(feature_array), featurenumb)]

	for i in range(0, 4) :
		combinations.append([])
		for j in range(2, featurenumb + 1) :
			for subset in itertools.combinations(splitEMGS[i], j) :
				combinations[i].append(list(subset))		
	return combinations

if __name__ == '__main__':
	#extract(argv[1])
	#r = readBinaryFile(argv[1])
	getSumVector(argv[1])


#connect all the different confusion matrices together + crossvalidate on the full data not person by person 
# keep having some that disconnects .. 	