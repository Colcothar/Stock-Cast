# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request, url_for, redirect
from random import random
import time 
from threading import Thread, Event
import os
import requests
import csv
import yfinance as yf
from matplotlib import pyplot as plt
import tensorflow.keras

import numpy
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.models import load_model

import tensorflow as tf
from numba import cuda 
device = cuda.get_current_device()

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=256)])

model = load_model('/var/www/html/StockPredictor/basic/tempModel.h5', compile = False)



#export FLASK_APP=/var/www/html/FlaskStuff/async_flask/application.py 
#flask run --host=0.0.0.0

__author__ = 'Barney Morris'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#this starts the stopwatch thread. This starts a timer so the user knows how long the model has been training for.
thread = Thread()
thread_stop_event = Event()





#fynction that checks the csv has valid data
def validateCSVData(processedData,minDataTrue, minData, predictionType=None):
    '''
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

#function to get information about the stock
def getStockInfo(stock):

    msft = yf.Ticker(str(stock))


    name = (msft.info['longName']) #get full name 

    summary = msft.info['longBusinessSummary'] #get the summary about the company
    sentance = summary.split(". ") #split the summary into sentences 

    if(len(sentance[0]) <= len(name)):
        info = sentance[0] + " " + sentance[1] + "."
        return name, str(info)
    else:
        info = sentance[0] + "."
        return name, str(info)


    #print(x[0]) #get first sentence
    #data = (hist["High"])
    #print(data[1])


def loadCSV(location, column ): #load CSV data into array
    rawData=[]

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            rawData.append(float(row[column].replace(",", ""))) #often data sets use commas to make the data more presentable. Eg 10000 becomes 10,000. This undoes this
    return rawData

def getStockData(stockTicker):
    rawData=[]
    stock = yf.Ticker(str(stockTicker)) #creates request

    history = stock.history(period="max") #gets history

    for i in range(len(history)):
        rawData.append(float(history["High"][i])) #writes the max stock price of the day to the array
    return(rawData) #return array

@app.route('/') #displays home page
def main():
    return render_template('index.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/basic') #displays basic page
def basic():
   return render_template('basicPredictor.html')

@app.route('/advanced') #displays advanced page
def advanced():
   return render_template('advancedPredictor.html')

@app.route('/help') #displays help page
def help():
   return render_template('help.html')



@app.route('/predictions')
def predictions():
   location = "/static/img/cost.png"
   return render_template('predictions.html', address=location)

@app.route('/basicUploader', methods = ['GET', 'POST']) #function to process the entered data to the basic page
def basicUploader2():
    basicSRC = "/var/www/html/StockPredictor/basic/"
    staticSRC = "/var/www/html/StockPredictor/static/img/"
    model = load_model(str(basicSRC + 'tempModel.h5'), compile = False)


    if request.method == 'POST':

        processedData=[] # create blank array to hold the final stock data

        stockData = request.files['stockData'] #saves the uploaded file to PastStockData.csv
        stockData.save(str(basicSRC + 'PastStockData.csv'))
      
        textBoxStock = request.form['textBoxStock'] #saves the stock entered into the textbox into variable
        print("Text box: " + textBoxStock)

        dropDownStock = request.form['dropDownStock']# saves stock picked from dropdownbox into variable
        print("Drop down: " + dropDownStock)
 
        with open(str(basicSRC + 'PastStockData.csv')) as f:
            firstLine = f.readline()

        stock="null"


        if(firstLine==""):
            if(textBoxStock==""):
                if(dropDownStock==""):
                    print("No data")
                    location=3 #no data
                    error= "No data"
                    return render_template("error.html")
                else:
                    location=2
                    stockTicker=dropDownStock #user has selected a stock from the drop down box
            else:
                location=1
                stockTicker=textBoxStock #user has entered a ticker into the text box
        else:
            location=0 #user has uploaded a csv
            stockTicker=""
            processedData=loadCSV(str(basicSRC + 'PastStockData.csv'),0)


        
                    


        if(location!=0 and location!=3 ): #if the user has only provided a ticker            
            processedData= getStockData(stockTicker) 
            



        valid, error = validateCSVData(processedData, True, 60, "basic")

        if (valid!=0): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            return render_template('error.html', message=error) # return an error if there are not ints OR not enough data

        sc = MinMaxScaler(feature_range = (0, 1)) #defines a new scaling function
 
        scaledArray = numpy.array(processedData) #creates a numpy array
        scaledArray = scaledArray .reshape(-1,1) #reshapes 
        scaledArray = sc.fit_transform(scaledArray ) #scales data 

        newScaled=[]
        for x in scaledArray : #sometimes, after scalling data can include 1,0 or nan after scalling. These must be removed 
            if( int(x[0])!=1 or int(x[0])!=0 or str(x[0])!="nan"):
                newScaled.append(float(x[0]))

        xNew = numpy.array(newScaled[-60:]) #get 60 recent days
        
        #print(xNew)
        #print("here")
        
        #print("here2")

        xNew = xNew.reshape((1,60,1)) #reshapes the array ready for predictions 
        yNew = model.predict(xNew, verbose=1) #predicts new stock value
        unscaledY = sc.inverse_transform(yNew) #this unscales the data

        yNew = yNew[0] #converts the 2d array back to 1d
        unscaledY=unscaledY[0] #converts the 2d array back to 1d

        #print(yNew)

        #print(unscaledY, unscaledY[0])
        #print(processedData[-4:])

        link = processedData[-1:] #this takes the 4 most recent 
        for i in range (len(unscaledY)):
            link.append(unscaledY[i]) #adds the first predicted value. This makes the graph connect up

        
        f = open(str(staticSRC + 'data.csv'), "w")
        for row in unscaledY:
            f.writelines(str(row))
            f.writelines("\n")
        f.close()


        fig = plt.figure()
        plt.plot( [0,1,2,3], processedData[-4:] , "-x", color='red') #this plots the previous stock values in red
        plt.plot( [3,4,5,6,7], link , "-x", color='blue') # this plots the predicted stock values in blue
        
        plt.xlabel("Day") #provides the label for the X axis
        plt.ylabel("Value") #providesw the label for the Y axis
        
        

        newName =  "basicPrediction" + str(time.time()) + ".png"

        for filename in os.listdir(str(staticSRC)):
            if filename.startswith('basicPrediction'):  # not to remove other images
                os.remove(str(staticSRC) + filename)


        plt.savefig(staticSRC + newName) #this saves the generated graph
        plt.close(fig)


        if(stockTicker!=""): #if the user has chosen a stock ticker
            name, summary = getStockInfo(stockTicker)    #gets the stock ticker name and summary
            pastSRC = "https://s.tradingview.com/widgetembed/?frameElementId=tradingview_ff017&symbol=" + stockTicker + "&interval=D&saveimage=0&toolbarbg=f1f3f6&studies=[]&theme=Light&style=1&timezone=Etc%2FUTC&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=en&utm_source"
        else:
            name, summary = "", ""
            fig = plt.figure()
            plt.plot( processedData , "-x", color='red') #this plots the previous stock values in red
            plt.xlabel("Day") #provides the label for the X axis
            plt.ylabel("Value") #providesw the label for the Y axis
            pastNewName =  "basicPast" + str(time.time()) + ".png"

            for filename in os.listdir(str(staticSRC)):
                if filename.startswith('basicPast'):  # not to remove other images
                    os.remove(str(staticSRC) + filename)


            plt.savefig(staticSRC + pastNewName) #this saves the generated graph
            plt.close(fig)

            pastSRC = "/static/img/" + pastNewName 
            




        
        imgSRC = "/static/img/" + newName #this variable points to the location of saved image
        
        return render_template('predictions.html', stockName=name, stockTicker=str(stockTicker), link=link, imgSRC=imgSRC, pastSRC=pastSRC, summary=summary)

@app.route('/advancedUploader', methods = ['GET', 'POST'])
def advancedUploader2():
    
    if request.method == 'POST':
        predictionDataSRC = '/var/www/html/StockPredictor/advanced/PredictionData.csv'
        trainingDataSRC = '/var/www/html/StockPredictor/advanced/TrainingData.csv'

        title = request.form['title']
        print("Title: " + title)

        inputBatches = int(request.form['inputBatches'])
        print("inputBatches: " + str(inputBatches))


        activationFunction = request.form['activationFunction']
        print("activationFunction: " + activationFunction)


        trainingData = request.files['trainingData']
        trainingData.save(trainingDataSRC)
      
        outputBatches = int(request.form['outputBatches'])
        print("outputBatches: " + str(outputBatches)) 
        
        lossFunction = request.form['lossFunction']
        print("lossFunction: " + lossFunction)
 

        predictionData = request.files['predictionData']
        predictionData.save(predictionDataSRC)

        epochs = request.form['epochs']
        print("epochs: " + epochs)

        stackedLayers = request.form['stackedLayers']
        print("stackedLayers: " + stackedLayers)

        with open('/var/www/html/StockPredictor/advanced/Parameters.txt', 'w') as f:
            f.write(str(title)+"\n")
            f.write(str(inputBatches)+"\n")
            f.write(str(activationFunction)+"\n")
            f.write(str(outputBatches)+"\n")
            f.write(str(lossFunction)+"\n")
            f.write(str(epochs)+"\n")
            f.write(str(stackedLayers))

        
        trainingData=loadCSV(trainingDataSRC, 0)
        predictionData=loadCSV(predictionDataSRC, 0) #load prediction data

 
        error=[]
        

        #predictionDataLength = len(predictionData) #number of elements in predictiond data
        #print(len(predictionData), inputBatches)

        validatedPrediction = validateCSVData(predictionData,True,inputBatches,"advanced")[0]

        if( validatedPrediction == 3):
            error.append("Input Batches too large, or not enough prediction data")
        elif( validatedPrediction == 1):
            error.append("Prediction data csv contains non integers")


        validatedTraining = validateCSVData(trainingData, True, (inputBatches+outputBatches), "advanced")[0]
    
        if (validatedTraining == 3): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            error.append("Batches too large, or not enough training data")
        elif(validatedTraining==1):
            error.append("Training data csv contains non integers")
        
        
        if(len(error)!=0):
            return render_template('error.html', message=error)
        else:
            print("Both CSV files are valid")

        if (validateCSVData(trainingData, True, (inputBatches+outputBatches)*10, "advanced")[0] == 3): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            warning = "Warning: Little training data "

        return render_template('blank.html')

@app.route('/advancedProgress', methods = ['GET', 'POST'])
def advancedProgress2():
    return render_template("blank.html")

@app.route('/results')
def result():
    return render_template('results.html')


def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers

    #
    f = open("/var/www/html/FlaskStuff/async_flask/progress.txt", "w")
    f.write("Training")
    f.close()

    os.system("/home/ist/anaconda3/envs/tf_gpu/bin/python /var/www/html/FlaskStuff/async_flask/training.py &")

    second = 0    
    minute = 0    
    hour = 0 
    print("Making random numbers")
    while not thread_stop_event.isSet():
        f = open("/var/www/html/FlaskStuff/async_flask/progress.txt", "r")
        status = f.read()
        print(status)
        f.close()
        if(status=="Training"):
            print("-----------------------Here")
            second+=1    
            if(second == 60):    
                second = 0    
                minute+=1    

            if(minute == 60):    
                minute = 0    
                hour+=1
        else:
            socketio.sleep(1)
            socketio.emit('newdata', {'minute': minute, 'second': second, 'hour': hour, 'status': status}, namespace='/test')

            return 0

        socketio.sleep(1)
        socketio.emit('newdata', {'minute': minute, 'second': second, 'hour': hour, 'status': status}, namespace='/test')
        


@app.route('/progress')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('progress.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')





@app.route('/cool_form', methods=['GET', 'POST'])
def cool_form():

    return render_template('cool_form.html')



if __name__ == '__main__':
    initModel()
    socketio.run(app)
