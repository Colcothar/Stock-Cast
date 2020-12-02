import yfinance as yf
import lxml

import pandas
import numpy
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))

def downloadStockData(stockTicker):
    rawData=[]
    stock = yf.Ticker(str(stockTicker)) #creates request

    history = stock.history(period="max") #gets history

    for i in range(len(history)):
        rawData.append(history["High"][i]) #writes the max stock price of the day to the array
    return(rawData) #return array


data = [1,2,3,4,54,6,90]

arr = numpy.array(data)

arr= arr.reshape(-1,1)

print(arr)

arr= sc.fit_transform(arr)

newArr= arr.tolist()
        

