import application as A

predictionDataSRC = '/var/www/html/StockPredictor/advanced/PredictionData.csv'
predictionData=A.loadCSV(predictionDataSRC, 0) #load prediction data

print(A.validateCSVData(predictionData,True, 10,"advanced")[0])