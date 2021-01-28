
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

sc = MinMaxScaler(feature_range = (0, 1)) #defines a new scaling function



'''
the code belows loads each lines from the parameters file to a list
it then assigns these lines and parameters to variables
'''

f = open(advancedSRC + "Parameters.txt", 'r+')
parameters = [line for line in f.readlines()]
f.close()


inputSize = int(parameters[1])
activationFunction = str(parameters[2])
outputSize = int(parameters[3])
lossFunction = parameters[4]
epochs = int(parameters[5])
stackedLayers = parameters[6]

'''
the code belows loads the data 
'''

trainingData = loadCSV(advancedSRC+"PredictionData.csv",0)
predictionData = loadCSV(advancedSRC+"TrainingData.csv",0)


'''
the code below creates a graph of past stock data 
it removes all other files starting with "advancedPast" and then creates a new png file
the file has a timestamp at the end
this prevents browsers from caching the images as they are all unique
'''

fig = plt.figure()
plt.plot( trainingData[-inputSize:] , "-x", color='red') #this plots the previous stock values in red      
plt.xlabel("Day") #provides the label for the X axis
plt.ylabel("Value") #provides the label for the Y axis
pastNewName =  "advancedPast" + str(time.time()) + ".png"
for filename in os.listdir(str(staticSRC)):
    if filename.startswith('advancedPast'):  # not to remove other images
        os.remove(str(staticSRC) + filename)


plt.savefig(staticSRC + pastNewName) #this saves the generated graph
plt.close(fig)




scaledArray = numpy.array(trainingData) #creates a numpy array and loads the trainingData intop it
scaledArray = scaledArray .reshape(-1,1) #reshapes 
scaledArray = sc.fit_transform(scaledArray ) #scales data 

newScaled=[]
for x in scaledArray : #sometimes, after scalling data can include 1,0 or nan after scalling. These must be removed 
    if( int(x[0])!=1 or int(x[0])!=0 or str(x[0])!="nan"):
        newScaled.append(float(x[0]))

X, Y = split(newScaled, inputSize , outputSize) #splits the data into batches 
X = X.reshape((X.shape[0], X.shape[1], 1)) #reshapes

model = keras.models.Sequential()
model.add(keras.layers.LSTM(256, activation=activationFunction[0:-1], return_sequences=stackedLayers, input_shape=(inputSize , 1)))
model.add(keras.layers.LSTM(128, activation=activationFunction[0:-1], return_sequences=stackedLayers ))
model.add(keras.layers.LSTM(64, activation=activationFunction[0:-1],))
model.add(keras.layers.Dense(outputSize))
model.summary()
model.compile(optimizer='adam', loss=lossFunction[0:-1])
data = model.fit(X, Y, epochs=epochs, verbose=1)


scaledArray = numpy.array(predictionData) #creates a numpy array
scaledArray = scaledArray .reshape(-1,1) #reshapes 
scaledArray = sc.fit_transform(scaledArray ) #scales data 

newScaled=[]
for x in scaledArray : #sometimes, after scalling data can include 1,0 or nan after scalling. These must be removed 
    if( int(x[0])!=1 or int(x[0])!=0 or str(x[0])!="nan"):
        newScaled.append(float(x[0]))

xNew = numpy.array(newScaled[-inputSize:]) #get 60 recent days


xNew = xNew.reshape((1, inputSize , 1))
yNew = model.predict(xNew, verbose=1)

unscaledY = sc.inverse_transform(yNew) #this unscales the data

yNew = yNew[0] #converts the 2d array back to 1d
unscaledY=unscaledY[0] #converts the 2d array back to 1d



link = trainingData[-1:] #this takes the 4 most recent 
xLink =[3]
for i in range (len(unscaledY)):
    xLink.append(i+4)
    link.append(unscaledY[i]) #adds the first predicted value. This makes the graph connect up






fig = plt.figure()
plt.plot( [0,1,2,3], trainingData[-4:] , "-x", color='red') #this plots the previous stock values in red
plt.plot( xLink, link , "-x", color='blue') # this plots the predicted stock values in blue     
plt.xlabel("Day") #provides the label for the X axis
plt.ylabel("Value") #provides the label for the Y axis


pastNewName =  "advancedPrediction" + str(time.time()) + ".png"
for filename in os.listdir(str(staticSRC)):
    if filename.startswith('advancedPrediction'):  # not to remove other images
        os.remove(str(staticSRC) + filename)


plt.savefig(staticSRC + pastNewName) #this saves the generated graph
plt.close(fig)
     

f = open(advancedSRC + "progress.txt", "w")
f.write("Complete")
f.close()

f = open(str(staticSRC + 'data.csv'), "w")
for row in unscaledY:
    f.writelines(str(row))
    f.writelines("\n")
f.close()