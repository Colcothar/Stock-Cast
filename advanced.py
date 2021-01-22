
import numpy  
import keras
from matplotlib import pyplot as plt
import csv



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
  iterations= len(sequence) - (inputSize + outputSize) + 1
  X, Y = list(), list()

  for k in range(iterations):
    X.append(sequence[k:k+inputSize])
    Y.append(sequence[k+inputSize:k+inputSize+outputSize])

  return numpy.array(X), numpy.array(Y) 

def loadCSV(location, column ): 
    #This functions loads CSV data into array

    rawData=[] #Assign new blank array 

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: #iterate for every row in CSV
            rawData.append(float(row[column].replace(",", ""))) #often data sets use commas to make the data more presentable. Eg 10000 becomes 10,000. This undoes this
    return rawData


trainingData = loadCSV(advancedSRC+"PredictionData.csv",0)
predictionData = loadCSV(advancedSRC+"TrainingData.csv",0)

'''
the code belows loads each lines from the parameters file to a list
it then assigns these lines and parameters to variables
'''



f = open(advancedSRC + "Parameters.txt", 'r+')
parameters = [line for line in f.readlines()]
f.close()



title = parameters[0]
inputSize = int(parameters[1])
activationFunction = str(parameters[2])
outputSize = int(parameters[3])
lossFunction = parameters[4]
epochs = int(parameters[5])
stackedLayers = parameters[6]

print(len(activationFunction))

X, Y = split(trainingData, inputSize , outputSize)
X = X.reshape((X.shape[0], X.shape[1], 1))

model = keras.models.Sequential()
model.add(keras.layers.LSTM(256, activation=activationFunction[0:-1], return_sequences=stackedLayers, input_shape=(inputSize , 1)))
model.add(keras.layers.LSTM(128, activation=activationFunction[0:-1], return_sequences=stackedLayers ))
model.add(keras.layers.LSTM(64, activation=activationFunction[0:-1],))
model.add(keras.layers.Dense(outputSize))
model.summary()
model.compile(optimizer='adam', loss=lossFunction[0:-1])
data = model.fit(X, Y, epochs=epochs, verbose=1)

xNew = numpy.array(predictionData[-inputSize:])

xNew = xNew.reshape((1, inputSize , 1))
yNew = model.predict(xNew, verbose=1)
yNew = yNew[0]
print(yNew)

f = open(advancedSRC + "progress.txt", "w")
f.write("Complete")
f.close()