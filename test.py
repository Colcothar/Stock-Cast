
import numpy  
import keras
from matplotlib import pyplot as plt
import csv
from sklearn.preprocessing import MinMaxScaler
import os
import time

'''
Below are 3 variables that the file path to important folders

The basicSRC hold the complete file path for the basic folder
The staticSRC holds the complete file path to the images folder
The advancedSRC holds the complete file path for the advanced folder

This makes the rest of the code easier to view and understand withouth having to have long file paths everywhere
'''

global basicSRC, staticSRC
basicSRC = "/var/www/html/StockPredictor/basic/"
advancedSRC = "/var/www/html/StockPredictor/advanced/"
staticSRC = "/var/www/html/StockPredictor/static/img/"

def validateCSVData(processedData,minDataTrue, minData, predictionType=None):
    '''
    This function checks the csv has valid data

    returns 0 for valid data
    returns 1 for not integers
    returns 2 for no data 
    returns 3 for not enough data
   '''

    valid = 0
    error="No error, data is valid"
    
    for i in processedData:
        try: # try converting to int
            int(i)
        except:
            print(i)
            valid = 1
            error= "Data contains non integers"

    if(minDataTrue==True):
        if(len(processedData)==0):
            valid = 2
            if(predictionType=="basic"):
                error = "Stock doesn't exist"
            else:
                error = "No data"
        elif(len(processedData)<int(minData)):
            valid = 3

            error = "Not enough data"
    
    return valid, error 

def split(sequence, inputSize , outputSize):
  iterations= len(sequence) - (inputSize + outputSize) + 1 #this calculates the number of possible samples 
  X, Y = list(), list() #creates 2 blank lists to hold this data 

  for k in range(iterations): #loops for all the batches
    X.append(sequence[k:k+inputSize]) #appends the input batches
    Y.append(sequence[k+inputSize:k+inputSize+outputSize]) #appends the output batches

  return numpy.array(X), numpy.array(Y) 

def loadCSV(location, column ): 
    #This functions loads CSV data into array

    rawData=[] #Assign new blank array 

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: #iterate for every row in CSV
            rawData.append(float(row[column].replace(",", ""))) #often data sets use commas to make the data more presentable. Eg 10000 becomes 10,000. This undoes this
    return rawData


trainingData = loadCSV("/var/www/html/StockPredictor/Test Data/Valid (60 Lines).csv",0)


inputBatches = 60
outputBatches = 0


data = History[1]

error=[]
validatedTraining = validateCSVData(trainingData, True, (inputBatches+outputBatches), "advanced")[0]

if (validatedTraining == 3): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
    error.append("Batches too large, or not enough training data")
elif(validatedTraining==1):
    error.append("Training data csv contains non integers")

if(inputBatches==0):
    error.append("Can't have zero batches")

trainingData[0:-inputBatches]
if( len(error)==0):
    print(trainingData)
else:
    print(error)
