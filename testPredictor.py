
import csv
import numpy
import keras
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model

def loadCSV(location):
    rawData=[]

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:

            rawData.append(float(row[0]))
    return rawData

data = loadCSV("/home/ist/Documents/stockData.csv")

def split(sequence, inputSize , outputSize):
  iterations= len(sequence) - (inputSize + outputSize) + 1 #works out the number of potential batches
  X, Y = list(), list() #creates some blank lists

  for k in range(iterations): #loops for items in the list 
    X.append(sequence[k:k+inputSize]) #adds the X values to array
    Y.append(sequence[k+inputSize:k+inputSize+outputSize]) #adds the Y values to the array 

  return numpy.array(X), numpy.array(Y) 

inputSize = 60
outputSize = 4
X, Y = split(data, inputSize, outputSize)

n = 1
X = X.reshape((X.shape[0], X.shape[1], n))

model = keras.models.Sequential()
model.add(keras.layers.LSTM(1024, activation='tanh', return_sequences=True, input_shape=(inputSize , n)))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(512, activation='tanh', return_sequences=True ))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(256, activation='tanh', return_sequences=True ))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.LSTM(128, activation='tanh'))
model.add(keras.layers.Dropout(0.2))
model.add(keras.layers.Dense(outputSize))


callbacks = [
    EarlyStopping(patience=10, verbose=1),
    ReduceLROnPlateau(factor=0.1, patience=3, min_lr=0.00001, verbose=1),
    ModelCheckpoint('modelTemp.h5', verbose=1, save_best_only=True, save_weights_only=True)
]

model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

model.summary()

model.fit(X, Y, epochs=2000, verbose=1, callbacks=callbacks)
model.save('model.h5')  