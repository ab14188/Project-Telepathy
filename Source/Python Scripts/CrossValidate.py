import serial
import math
import time
import datetime
import sys
import getopt
import os
import subprocess
import extract
import numpy as np
import itertools
import matplotlib 
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.metrics import confusion_matrix
from sklearn.lda import LDA
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV
from sklearn.preprocessing import StandardScaler
from svmutil import * 
from time import sleep
import sklearn

# Different gesture types // note should be in alphabetised order
gestureWords    = ['back', 'down', 'faster', 'forwards', 'left', 'no', 'right', 'slower', 'stop', 'turn', 'up', 'yes'] # when i do not have all the classes in tthe measured data it gives me a bad rate -- this is normal  
words           = gestureWords


# Different training directories __represent of different conditions 
trainingDirAll = 'spoken' 
trainingDirs = [trainingDirAll]

# Load data from files and extract features
def load_features(words, trainingDir) : 
    parentPath  = os.getcwd()
    features    = []
    features2   = []
    gestureArray = []
    os.chdir(trainingDir)                                                           # this changes the directory to the given path 

    # loop through the csv files, and store into 2D array
    for i in os.listdir(os.getcwd()):                                           
        if i in words:
            #print("Gesture i: ", i )
            os.chdir(parentPath + "/" + trainingDir + "/" + i)
            for dataFile in os.listdir(os.getcwd()):
                result          = extract.extract_features(dataFile)                # Extract features from the file _ note removed the time features 
                features.append(result)
                #feature_combinations = extract.combine_features(result)
                #features2.append(feature_combinations)
                gestureArray.append(i)                                              # Keep track of the gesture labels

    #x, y = np.shape(feature_combinations)

    #for i in range(0, x+1) :  

    # Scaling the features 
    scaler          = StandardScaler().fit(features)
    features_scaled = scaler.transform(features) 

    os.chdir(parentPath)
    return features_scaled, features, gestureArray                                                             

# Choose training and Test data
def separate_training_test(features_scaled, gestureArray, i) :
    # select subset of features for the fold
    count = 0
    trainingSet     = []
    testingSet      = []
    trainingLabels  = []
    testingLabels   = []
    #currentGesture  = -1                       # to be used later on for label arrays

    for feature_vector in features_scaled:
        #if count%10 == 0 :
            #currentGesture += 1
        #if count%4 == i or count%3 == i: 
        if count%10 == i : 
            testingSet.append(feature_vector)
            testingLabels.append(words.index(gestureArray[count])) 
        else:
            trainingSet.append(feature_vector)  
            trainingLabels.append(words.index(gestureArray[count]))
        count += 1
    return testingSet, testingLabels, trainingSet, trainingLabels

def SVM_classifier(best_C, best_G, trainingSet, trainingLabels, testingSet) :
    clf         = svm.SVC(C=best_C,gamma=best_G)
    clfoutput   = clf.fit(trainingSet, trainingLabels)
    result      = clf.predict(testingSet)
    return result , "SVM"

def LDA_classifier(trainingSet, trainingLabels, testingSet) :
    clf         = LDA()
    clfoutput   = clf.fit(trainingSet, trainingLabels)
    result      = clf.predict(testingSet)      
    return result, "LDA"

def gaussian_classifier(trainingSet, trainingLabels, testingSet) :
    clf         = GaussianNB()
    clfoutput   = clf.fit(trainingSet, trainingLabels)
    result      = clf.predict(testingSet)      
    return result

def cross_validate(words, trainingDir):
    features_scaled, features, gestureArray = load_features(words, trainingDir)
    predictions = []
    cum_rate = 0.0

# loop through 10 times
    for i in range(10): 
        # Choose training and test data
        testingSet, testingLabels, trainingSet, trainingLabels = separate_training_test(features_scaled, gestureArray, i)
        
    # train the data on the new subset
        best_C = 0
        best_G = 0
        best_percentage = 0

        C_range     = np.logspace(-2, 10, num=13, base=2)
        gamma_range = np.logspace(-5, 1, num=7, base=10)
        param_grid  = dict(gamma=gamma_range, C=C_range)
        cv          = StratifiedShuffleSplit(trainingLabels, n_iter=3, test_size=0.11, random_state=42)
        grid        = GridSearchCV(svm.SVC(), param_grid=param_grid, cv=cv)

        grid.fit(trainingSet, trainingLabels) 

        best_C = grid.best_params_['C']
        best_G = grid.best_params_['gamma']

        # Different classifiers 
        result, classifier = SVM_classifier(best_C, best_G, trainingSet, trainingLabels, testingSet)
        #result, classifier = LDA_classifier(trainingSet, trainingLabels, testingSet)
        #result, classifier  = gaussian_classifier(trainingSet, trainingLabels, testingSet)

        predictions.append(result.tolist())
        
        #print("zip + labels : ", result, testingLabels)
        num_correct = 0
        for j,k in zip(result,testingLabels):
            if j == k:
                num_correct += 1

        percentage = (float(num_correct) * 100.0) / float(len(words))
        best_percentage = percentage

        cum_rate += best_percentage
        #print (np.round(percentage,2), '%')
    
    #print predictions
    rate = cum_rate / 10.0

    #print(np.round(rate,2), '%')
    linear_pred = []
    linear_true = []
    for i in predictions:
        count = 0 
        for j in i:
            linear_pred.append(j)
            linear_true.append(count)
            count += 1
    
    #print (linear_pred)
    #print ("linear true: ", linear_true)
    c_matrix = confusion_matrix(linear_true, linear_pred) 

    plot_confusion_matrix(c_matrix, classifier)
    return rate, c_matrix

def validate_participant(directory):
    cv_rates = []
    c_matrices = []

    originalWorkingPath = os.getcwd()
    os.chdir(directory)
    #print("Directory: ", dir, 'validating')
    #for r in itertools.product(words, trainingDirs):
    cv_rate, c_matrix = cross_validate(words, trainingDirs[0]) # this used to be r[0] r[1] 
    cv_rates.append(cv_rate)
    c_matrices.append(c_matrix)
    print("Rate ", np.round(cv_rate,2), " %")
    os.chdir(originalWorkingPath)

    return cv_rates, c_matrices

def plot_confusion_matrix(cm, classifier) :
    gesture_nums = ('back', 'down', 'faster', 'forwards', 'left', 'no', 'right', 'stop', 'turn', 'up', 'yes')

    if not os.path.exists("./CM2") :
        os.mkdir("CM2")
    
    if classifier == "SVM" : 
        file = 'confusion_matrixSVM'
    else: 
        file = 'confusion_matrix' 
    fig = plt.figure()
    plt.clf()
    ax  = fig.add_subplot(111)
    ax.set_aspect(1)

    res = ax.imshow(np.array(cm), cmap=plt.cm.Blues, 
                    interpolation='nearest')

    width   = len(cm)
    height  = len(cm[0])

    for x in range(width):
        for y in range(height):
            if cm[x][y] > 0:
                if cm[x][y] > 4:
                    ax.annotate(str(cm[x][y]), xy=(y, x), 
                        horizontalalignment='center',
                        verticalalignment='center', color = 'white',
                        fontsize = 11)
                elif cm[x][y] < 2:
                    ax.annotate(str(cm[x][y]), xy=(y, x), 
                        horizontalalignment='center',
                        verticalalignment='center', color = 'black',
                        fontsize = 11)
                else:
                    ax.annotate(str(cm[x][y]), xy=(y, x), 
                        horizontalalignment='center',
                        verticalalignment='center', color = 'gray',
                        fontsize = 11)
                        
    res.set_clim(vmin=0, vmax=5)

    cb = fig.colorbar(res)

    plt.xlabel('True')
    plt.ylabel('Predicted')
    
    plt.xticks(range(width), gesture_nums, rotation=45)
    plt.yticks(range(height), gesture_nums)
    ax.grid(True, alpha=0.2)
    #plt.show()
    parentDir = os.getcwd()
    os.chdir("./CM2")
    plt.savefig(file + '.pdf', format='pdf', bbox_inches='tight')
    os.chdir(parentDir)


if __name__ == '__main__':
    print('The scikit-learn version is {}.'.format(sklearn.__version__))
    all_c_matrices = []             
    sum_c_matrices = []

    for i in range (0,5):
        #dir = 'Test0_' + str(i)
        #dir = './try data/neck'
        dir = './user_study/results/test' + str(i)
        cv_rates, c_matrices = validate_participant(dir)
        print('C matrices result: \n', c_matrices)
        all_c_matrices.append(c_matrices)

    first = True
    for idx, n in enumerate(all_c_matrices):
        if first: 
            sum_c_matrices = n
            first = False
        else:
            for idy, j in enumerate(sum_c_matrices):
                sum_c_matrices[idy] = sum_c_matrices[idy] + all_c_matrices[idx][idy]


    #print("SUM_c matrices: ", sum_c_matrices)

    # sum_c_matrices[:] = [((x * 100.0) / 120.0) for x in sum_c_matrices]
    # for x in sum_c_matrices:
    #     for y in x:
    #         for idx, z in enumerate(y):
    #             if idx != len(y) - 1:
    #                 print('%d,' % z), 
    #             else:
    #                 print ('%d' % z)
    # #print all_c_matrices
    # print (sum_c_matrices)

# run tests to determine which features work best 