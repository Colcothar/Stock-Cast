# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request, url_for, redirect
from random import random
from time import sleep
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
tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=128)])

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
        elif(len(processedData)<minData):
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
            rawData.append(row[column].replace(",", "")) #often data sets use commas to make the data more presentable. Eg 10000 becomes 10,000. This undoes this
    return rawData

def getStockData(stockTicker):
    rawData=[]
    stock = yf.Ticker(str(stockTicker)) #creates request

    history = stock.history(period="max") #gets history

    for i in range(len(history)):
        rawData.append(history["High"][i]) #writes the max stock price of the day to the array
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
    

    if request.method == 'POST':

        processedData=[] # create blank array to hold the final stock data

        stockData = request.files['stockData'] #saves the uploaded file to PastStockData.csv
        stockData.save('/var/www/html/StockPredictor/basic/PastStockData.csv')
      
        textBoxStock = request.form['textBoxStock'] #saves the stock entered into the textbox into variable
        print("Text box: " + textBoxStock)

        dropDownStock = request.form['dropDownStock']# saves stock picked from dropdownbox into variable
        print("Drop down: " + dropDownStock)
 
        with open('/var/www/html/StockPredictor/basic/PastStockData.csv') as f:
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
    

            processedData=loadCSV('/var/www/html/StockPredictor/basic/PastStockData.csv',0)



            
                    


        if(location!=0 and location!=3 ): #if the user has only provided a ticker            
            processedData= getStockData(stockTicker) 
            
        valid, error = validateCSVData(processedData, True, 60, "basic")
        #print(error)
        if (valid!=0): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            return render_template('error.html', message=error) # return an error if there are not ints OR not enough data
            
        '''
        generate predictions
        generate graph
        
        '''
        #print("Printing data")
        #sleep(2)
        #print(processedData)

        sc = MinMaxScaler(feature_range = (0, 1))

        scaledArray = numpy.array(processedData)
        scaledArray = scaledArray .reshape(-1,1)
        scaledArray = sc.fit_transform(scaledArray )

        newScaled=[]
        for x in scaledArray :
            if( int(x[0])!=1 or int(x[0])!=0 or str(x[0])!="nan"):
                newScaled.append(float(x[0]))

        #sleep(4)
        #print("\n\nPrinting 60 recent values")
        #sleep(2)
        #print(processedData[-60:])
        #sleep(4)
        #print("\n\nPrinting scaled data")
        #sleep(2)
        #print(newScaled[-60:])

        xNew = numpy.array(newScaled[-60:])
        
        #print(xNew)
        #print("here")
        model = load_model('/var/www/html/StockPredictor/basic/tempModel.h5', compile = False)
        #print("here2")
        xNew = xNew.reshape((1,60,1))
        yNew = model.predict(xNew, verbose=1)
        unscaledY = sc.inverse_transform(yNew)

        yNew = yNew[0]
        unscaledY=unscaledY[0]

        #print(yNew)

        #print(unscaledY, unscaledY[0])
        #print(processedData[-4:])

        link = processedData[-4:]
        link.append(unscaledY[0] )

        plt.plot( [0,1,2,3,4], link , "-x", color='red')
        plt.plot( [4,5,6,7], unscaledY , "-x", color='blue')
        
        plt.xlabel("Day")
        plt.ylabel("Value")
        
        plt.savefig('/var/www/html/StockPredictor/static/img/basicPrediction.png')

        if(stockTicker!=""):
            
            name, summary = getStockInfo(stockTicker)   
          
        del model  
        #tensorflow.keras.clear_session()
        
        

        
        return render_template('predictions.html', stockName=name, stockTicker=str(stockTicker), link=link, summary=summary)

@app.route('/advancedUploader', methods = ['GET', 'POST'])
def advancedUploader2():
    
    if request.method == 'POST':
        predictionDataSRC = '/var/www/html/StockPredictor/advanced/PredictionData.csv'
        trainingDataSRC = '/var/www/html/StockPredictor/advanced/TrainingData.csv'

        title = request.form['title']
        print("Title: " + title)

        inputBatches = request.form['inputBatches']
        print("inputBatches: " + inputBatches)


        activationFunction = request.form['activationFunction']
        print("activationFunction: " + activationFunction)


        trainingData = request.files['trainingData']
        trainingData.save(trainingDataSRC)
      
        outputBatches = request.form['outputBatches']
        print("outputBatches: " + outputBatches) 
        
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


        #predictionDataLength = len(predictionData) #number of elements in predictiond data

        if(validateCSVData(predictionData,True,inputBatches,"advanced")[0] == 3):
            error = "Input Batches too large, or not enough prediction data"


        if (validateCSVData(trainingData, True, (inputBatches+outputBatches), "advanced")[0] == 3): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            error = "Batches too large, or not enough training data"

        if(error!=""):
            return render_template('cool_form.html', message=error)

        if (validateCSVData(trainingData, True, (inputBatches+outputBatches)*10, "advanced")[0] == 3): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            warning = "Warning: Little training data "



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
    socketio.run(app)
