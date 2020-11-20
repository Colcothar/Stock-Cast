# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request, url_for, redirect
from random import random
from time import sleep
from threading import Thread, Event
import os
import requests
import csv



#export FLASK_APP=/var/www/html/FlaskStuff/async_flask/application.py 
#flask run --host=0.0.0.0

__author__ = 'Barney Morris'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def validateCSVData(processedData):
    valid = True
    for i in processedData:
        if( processedData[i].is_integer() != False):
            valid=False
    return valid
    

@app.route('/') #displays home page
def main():
    return render_template('index.html')

@app.route('/basic') #displays basic page
def basic():
   return render_template('basicPredictor.html')

@app.route('/advanced') #displays advanced page
def advanced():
   return render_template('advancedPredictor.html')

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
                    location=3
                    error= "No data"
                else:
                    location=2
                    stock=textBoxStock
            else:
                location=1
                stock=dropDownStock
        else:
            location=0
            with open('/var/www/html/StockPredictor/basic/PastStockData.csv') as f: # open 
                processedData= f.read()
                if (validateCSVData(processedData)==False): #the user can upload whatever data they want. This function validates that the uploaded data has integers on everyline 
                    return render_template('error.html') # return an error if there are not ints
                    



        if(location==0): #if the user has only uploaded a text file
            url = "http://download.macrotrends.net/assets/php/stock_data_export.php?t=" + stock # generate url of stock data
      
            r = requests.get(url) # generate request

            with open('/var/www/html/StockPredictor/basic/PastStockData.csv', 'wb') as f:
                f.write(r.content) # write content to textfile

            with open("/var/www/html/StockPredictor/basic/PastStockData.csv") as csvfile:
                
                readCSV = csv.reader(csvfile, delimiter=',')
                i=0
                for row in readCSV:
                    i = i +1
                    if i>15: # the first 15 rows are text about macrotrends, not stock data. So I want to ignore the first 15 rows.
                        processedData.append(float(row[2].replace(",", ""))) #adds each row to array removing the commer

            #generate graph
        print(processedData)

        link = str("https://s.tradingview.com/widgetembed/?frameElementId=tradingview_ff017&symbol=" + dropDownStock + "&interval=D&saveimage=0&toolbarbg=f1f3f6&studies=[]&theme=Light&style=1&timezone=Etc%2FUTC&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=en&utm_source")
        link = "https://bbc.co.uk"
        return render_template('cool_form.html', stock=str(dropDownStock), link=link)

@app.route('/advancedUploader', methods = ['GET', 'POST'])
def advancedUploader2():
    
    if request.method == 'POST':
        
        title = request.form['title']
        print("Title: " + title)

        inputBatches = request.form['inputBatches']
        print("inputBatches: " + inputBatches)

        activationFunction = request.form['activationFunction']
        print("activationFunction: " + activationFunction)


        trainingData = request.files['trainingData']
        trainingData.save('/var/www/html/StockPredictor/advanced/TrainingStockData.csv')
      
        outputBatches = request.form['outputBatches']
        print("outputBatches: " + outputBatches) 
        
        lossFunction = request.form['lossFunction']
        print("lossFunction: " + lossFunction)
 

        predictionData = request.files['predictionData']
        predictionData.save('/var/www/html/StockPredictor/advanced/PredictionData.csv')

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
            
        return render_template('cool_form.html')


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
