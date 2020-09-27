# univariate multi-step vector-output stacked lstm example
import numpy  
import keras

from matplotlib import pyplot as plt
import math 
import csv
import csv
 
def loadCSV(location):
    rawData=[]

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            rawData.append(int(float(row[3].replace(",", ""))))
    return rawData

def split(sequence, inputSize , outputSize):
  iterations= len(sequence) - (inputSize + outputSize) + 1
  X, Y = list(), list()

  for k in range(iterations):
    X.append(sequence[k:k+inputSize])
    Y.append(sequence[k+inputSize:k+inputSize+outputSize])

  return numpy.array(X), numpy.array(Y) 

def setArrays(xSize, ySize):
  xInput = []
  for i in range(xSize):
    xInput.append(i+1)

  xOutput = [] 
  for i in range(ySize):
    xOutput.append(i+1+xSize)

  xLink = [ xInput[-1] , xOutput[0] ]
  return xInput, xOutput, xLink



#rawData = loadCSV("/home/ist/Documents/AI/data3.csv")
#print(rawData)
rawData = [0,1,2,3,4,5,6,7,8,9,10]


inputSize = 4
outputSize = 3

# split into samples
X, Y = split(rawData, inputSize , outputSize)
print(X, Y)
print(X.shape[1])


n = 1
X = X.reshape((X.shape[0], X.shape[1], n))

model = keras.models.Sequential()
model.add(keras.layers.LSTM(101, activation='relu', return_sequences=True, input_shape=(inputSize , n)))
model.add(keras.layers.LSTM(101, activation='relu', return_sequences=True ))
model.add(keras.layers.LSTM(101, activation='relu'))
model.add(keras.layers.Dense(outputSize))
model.summary()
model.compile(optimizer='adam', loss='mae', metrics=['accuracy'])



# fit model
data = model.fit(X, Y, epochs=2000, verbose=0)


#xNew = numpy.array(loadCSV("/home/ist/Documents/AI/data4.csv"))
xNew = numpy.array([4,5,6,7])

xNew = xNew.reshape((1, inputSize , n))
yNew = model.predict(xNew, verbose=1)
yNew = yNew[0]
print(yNew)


#All graph stuff below

#show results graphically
plt.title('Price')
xInput, xOutput, xLink = setArrays(inputSize, outputSize)
yLink = [xNew[0][-1], yNew[0]]

plt.plot(xInput, xNew[0], color='blue', label='Given Data')
plt.plot(xOutput, yNew, color='red', label='Predicted Data')
plt.plot(xLink, yLink, color='red')
plt.legend()
plt.xlabel("Day")
plt.ylabel("Value")
plt.savefig('/var/www/html/FlaskStuff/async_flask/cost.png')

#show data about training
plt.plot(data.history['accuracy'])
plt.title('Model Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.savefig('/var/www/html/FlaskStuff/async_flask/accuracy.png')

plt.plot(data.history['loss'])
plt.title('Model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.savefig('/var/www/html/FlaskStuff/async_flask/loss.png')

f = open("/var/www/html/FlaskStuff/async_flask/progress.txt", "w")
f.write("Complete")
f.close()