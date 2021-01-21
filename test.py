import application as A
import numpy 

#predictionDataSRC = '/var/www/html/StockPredictor/Test Data/Valid (90 Lines).csv'
predictionDataSRC = '/var/www/html/StockPredictor/Test Data/Borderline (60 Lines).csv'
predictionData=A.loadCSV(predictionDataSRC, 0) #load prediction data

xNew = numpy.array(predictionData[-60:]) #get 60 recent days



print(xNew)
print("\n", len(xNew))