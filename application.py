# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, request, url_for, redirect
from random import random
from time import sleep
from threading import Thread, Event
import os

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


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/basic')
def basic():
   return render_template('basicPredictor.html')

@app.route('/advanced')
def advanced():
   return render_template('advancedPredictor.html')

@app.route('/predictions')
def predictions():
   return render_template('predictions.html')

@app.route('/basicUploader', methods = ['GET', 'POST'])
def basicUploader2():
    
    if request.method == 'POST':
        
        stockData = request.files['stockData']
        stockData.save('/var/www/html/FlaskStuff/data.csv')
      
        textBoxStock = request.form['textBoxStock']
        print("Text box: " + textBoxStock)

        dropDownStock = request.form['dropDownStock']
        print("Drop down: " + dropDownStock)
    

        with open('/var/www/html/FlaskStuff/nopol.txt', 'w') as f:
            f.write(str(textBoxStock))
            
        return render_template('cool_form.html')

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
        trainingData.save('/var/www/html/StockPredictor/trainingData.csv')
      
        outputBatches = request.form['outputBatches']
        print("outputBatches: " + outputBatches) 
        
        lossFunction = request.form['lossFunction']
        print("lossFunction: " + lossFunction)
 

        predictionData = request.files['predictionData']
        predictionData.save('/var/www/html/StockPredictor/predictionData.csv')

        epochs = request.form['epochs']
        print("epochs: " + epochs)

        stackedLayers = request.form['stackedLayers']
        print("stackedLayers: " + stackedLayers)

        
            
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
