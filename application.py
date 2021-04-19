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

#Below are the execution commands for the flask application
#export FLASK_APP=/var/www/html/FlaskStuff/async_flask/application.py 
#flask run --host=0.0.0.0

__author__ = 'Barney Morris'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True


    x

#This creates a socket app instance 
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)


if __name__ == 'application': #checks if the program is being run, or imported
    device = cuda.get_current_device() #get the current devices
    gpus = tf.config.experimental.list_physical_devices('GPU') #get the GPU devices connected to the pc
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True) #set memory growth to true
    tf.config.experimental.set_virtual_device_configuration(gpus[0], [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=256)]) #set memory limit to 256mb 

    socketio.run(app)



#This starts the stopwatch thread. This starts a timer so the user knows how long the model has been training for.
thread = Thread()
threadStopEvent = Event()


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



'''
This loads the model in and assigns to a global variable
This is far more efficient than loading in a model each time the basicUploader2 function is called
'''

global model
model = load_model(str(basicSRC + 'tempModel.h5'), compile = False)



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
            print("Error: " + str(i))
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


def getStockInfo(stock):
    '''
    This function gets stock information
    It uses yFinance to get the stock name and the stock summary
    The stock summary is often quite long, so I just take the first sentance
    However, some companies put a "." afer their company name eg "Apple Inc."
    Meaning that the entire summary ends up being "Apple Inc.
    So if the summary is the same length as the name, I take two sentances instead of one
    '''


    msft = yf.Ticker(str(stock))
    print(stock)

    name = (msft.info['longName']) #Get full name 
    print(name)
    summary = msft.info['longBusinessSummary'] #Get the summary about the company
    sentance = summary.split(". ") #Split the summary into sentences 

    if(len(sentance[0]) <= len(name)): #Is the summary too short?
        info = sentance[0] + " " + sentance[1] + "." #If the summary is too short, use 2 sentances instead of 1

    else:
        info = sentance[0] + "."
    
    return name, str(info)


def loadCSV(location, column ): 
    #This functions loads CSV data into array

    rawData=[] #Assign new blank array 

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV: #iterate for every row in CSV

            rawData.append(float(row[column].replace(",", ""))) #often data sets use commas to make the data more presentable. Eg 10000 becomes 10,000. This undoes this
    return rawData

def getStockData(stockTicker):
    '''
    This function takes a stockTicker as a parameter
    It returns the past stock values, for the given  
    '''

    rawData=[]
    stock = yf.Ticker(str(stockTicker)) #creates request

    history = stock.history(period="max") #gets history

    for i in range(len(history)):
        if(str(history["High"][i])!="nan"):
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


    if request.method == 'POST':

        processedData=[] # create blank array to hold the final stock data

        stockData = request.files['stockData'] #saves the uploaded file to PastStockData.csv
        stockData.save(basicSRC + 'PastStockData.csv')
    
        textBoxStock = request.form['textBoxStock'] #saves the stock entered into the textbox into variable
        print("Text box: " + textBoxStock)

        dropDownStock = request.form['dropDownStock']# saves stock picked from dropdownbox into variable
        print("Drop down: " + dropDownStock)

        with open(basicSRC + 'PastStockData.csv') as f:
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
            processedData=loadCSV((basicSRC + 'PastStockData.csv'),0)


        if(location!=0 and location!=3 ): #if the user has only provided a ticker            
            processedData= getStockData(stockTicker) 
            



        valid, error = validateCSVData(processedData, True, 60, "basic")

        if (valid!=0): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            return render_template('error.html', message=[error]) # return an error if there are not ints OR not enough data

        sc = MinMaxScaler(feature_range = (0, 1)) #defines a new scaling function

        scaledArray = numpy.array(processedData) #creates a numpy array
        scaledArray = scaledArray .reshape(-1,1) #reshapes 
        scaledArray = sc.fit_transform(scaledArray ) #scales data 

        newScaled=[]
        for x in scaledArray : #sometimes, after scalling data can include 1,0 or nan after scalling. These must be removed 
            if( int(x[0])!=1 or int(x[0])!=0 or str(x[0])!="nan"):
                newScaled.append(float(x[0]))

        xNew = numpy.array(newScaled[-60:]) #get 60 recent days
        

        xNew = xNew.reshape((1,60,1)) #reshapes the array ready for predictions 
        yNew = model.predict(xNew, verbose=1) #predicts new stock value
        unscaledY = sc.inverse_transform(yNew) #this unscales the data

        yNew = yNew[0] #converts the 2d array back to 1d
        unscaledY=unscaledY[0] #converts the 2d array back to 1d

        link = processedData[-1:] #this takes the 4 most recent 
        for i in range (len(unscaledY)):
            link.append(unscaledY[i]) #adds the first predicted value. This makes the graph connect up

        fig = plt.figure()
        plt.plot( [0,1,2,3], processedData[-4:] , "-x", color='red') #this plots the previous stock values in red
        plt.plot( [3,4,5,6,7], link , "-x", color='blue') # this plots the predicted stock values in blue
        plt.xlabel("Day") #provides the label for the X axis
        plt.ylabel("Value") #provides the label for the Y axis
        
        newName =  "basicPrediction" + str(time.time()) + ".png"
        for filename in os.listdir(str(staticSRC)):
            if filename.startswith('basicPrediction'):  
                os.remove(str(staticSRC) + filename)

        plt.savefig(staticSRC + newName) #Saves the generated graph
        plt.close(fig) #Closes graph (so a new one can be made)



        '''
        if the user has chosen a stock ticker, it will have a corresponding interactable graph on trading view

        If the user has uploaded a file, then there will be no interactable graph widget on trading view
        So I will need to generate a graph of past stock data in place

        the variable pastSRC can then hold the location of past stock data. This can either the trading view widget, OR the location of a locally made graph
        ''' 

        f = open(str(staticSRC + 'data.csv'), "w")
        
        if(stockTicker!=""): #if the user has chosen a stock ticker
            name, summary = getStockInfo(stockTicker)    #gets the stock ticker name and summary
            f.writelines(name + "\n")
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
           
        '''
        the code below writes the data to the data csv
        it will write 6 days worth of past stock values
        and the 4 future predicted stock values
        '''
            
        for row in processedData[-6:]:
            f.writelines(str(row) + "\n")
        f.writelines("\n")    
        for row in unscaledY:
            f.writelines(str(row) + "\n")
        f.close()

        '''
        if the last predicted value is greater than the last past stock value 
        then machine learning algorithm has predicted the stock will be worth more in the future
        as stock value is going up, it would make sense to buy

        the below code sets the variables to tell the user whether to buy or sell - and set the colour
        '''

        if(processedData[-1] > unscaledY[-1]):
            colour = "red"
            change = '  - SELL'
        else:
            colour = "blue"
            change = '  - BUY'

        #render the page, with all the variables
        return render_template('predictions.html', stockName=name, stockTicker=str(stockTicker), link=link, imgSRC=imgSRC, pastSRC=pastSRC, summary=summary, change=change, colour=colour)

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

        #this writes all the machine learning parameters to a text file. The "advanced.py" python file will use them to create a model and prediction 
        with open(advancedSRC + 'Parameters.txt', 'w') as f:
            f.write(str(title)+"\n")
            f.write(str(inputBatches)+"\n")
            f.write(str(activationFunction)+"\n")
            f.write(str(outputBatches)+"\n")
            f.write(str(lossFunction)+"\n")
            f.write(str(epochs)+"\n")
            f.write(str(stackedLayers))

        
        trainingData=loadCSV(trainingDataSRC, 0) #load the training data
        predictionData=loadCSV(predictionDataSRC, 0) #load prediction data

        error=[]# there could be lots or errors. So, every error gets appended to this list. The full list is rendered to the user.


        validatedPrediction = validateCSVData(predictionData,True,inputBatches,"advanced")[0] #this function validates data, and returns values depending on the validity - check the function for more information 

        if( validatedPrediction == 3): #checks if there is enough prediction data OR if the input batches are too large
            error.append("Input Batches too large, or not enough prediction data")
        elif( validatedPrediction == 1): #checks if there are non integers within the csv
            error.append("Prediction data csv contains non integers")


        validatedTraining = validateCSVData(trainingData, True, (inputBatches+outputBatches), "advanced")[0]
    
        if (validatedTraining == 3): #checks if there is enough training data OR if the batches are too large
            error.append("Batches too large, or not enough training data")
        elif(validatedTraining==1): #checks if there are non integers within the csv
            error.append("Training data csv contains non integers")
        
        
        if(len(error)!=0): #if errors have been appended to the error list - render the error page
            return render_template('error.html', message=error)
        else:
            print("Both CSV files are valid")

        warning ="" #creates a empty variable to hold the warning  
        if (validateCSVData(trainingData, True, (inputBatches+outputBatches)*10, "advanced")[0] == 3): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
            warning = "Warning: Little training data " 

        return render_template('progress.html', warning=warning)

@app.route('/advancedProgress', methods = ['GET', 'POST'])
def advancedProgress2():
    '''this page is rendered when the user clicks the GO button'''

    f = open(advancedSRC + "Parameters.txt", "r")
    name = f.readline()
    f.close()
    
    for filename in os.listdir(str(staticSRC)):
        if filename.startswith('advancedPast'):
            pastSRC = "/static/img/" + filename # creates the path for the graph of past stock values
        if filename.startswith("advancedPrediction"):
            imgSRC = "/static/img/" + filename # creates the path for the graph of predicted stock values

    
    return render_template('predictions.html', stockName=name, imgSRC=imgSRC, pastSRC=pastSRC) #renders page



def stopwatch(): #this is the incramental stopwatch that can be seen on the advanced predictor page
    
    f = open(advancedSRC + "progress.txt", "w")
    f.write("Training") #write "training" to the progress file
    f.close()

    os.system("/home/ist/anaconda3/envs/tf_gpu/bin/python /var/www/html/StockPredictor/advanced.py &") #start the "advanced.py" file 

    second, minute, hour = 0,0,0    #set stopwatch to 0

    while not threadStopEvent.isSet(): #while the thread is still going - while there is still a user present
        f = open(advancedSRC + "progress.txt", "r") #the "advanced.py" will write "Complete" when the training is complete
        status = f.read()
        print(status)
        f.close()
        if(status=="Training"): #checks if the model is stil training

            second+=1    # increment the stopwatch by 1 second
            if(second == 60): #if there have been 60 seconds, add another min   
                second = 0    
                minute+=1    

            if(minute == 60): #if ther have been 60 minutes, add another hour    
                minute = 0    
                hour+=1
        else:
            socketio.sleep(1) # wait 1 second
            socketio.emit('newdata', {'minute': minute, 'second': second, 'hour': hour, 'status': status}, namespace='/test') #send the elapsed time and status to socket. This data will get picked up in the JS function 

            return 0 # this makes sure that the stopwatch() function will end when the traininhg has finished

        socketio.sleep(1) # wait 1 second
        socketio.emit('newdata', {'minute': minute, 'second': second, 'hour': hour, 'status': status}, namespace='/test') #send the elapsed time and status to socket. This data will get picked up in the JS function 
        


@app.route('/progress')
def index():
    #only by rendering this page first will the client be connected to the socketio instance
    return render_template('progress.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the timer thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(stopwatch) #start the stopwatch in the background


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected') #prints to terminal if the user quits


