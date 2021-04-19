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

stocks = [line.rstrip('\n') for line in open("/var/www/html/StockPredictor/basic/Training Algorithm/stockList.txt")]



for i in stocks:
    print(i)
    try:
        data = downloadStockData(i)

        arr = numpy.array(data)

        arr= arr.reshape(-1,1)
        print(arr)


        arr= sc.fit_transform(arr)

        newArr= arr.tolist()
        # print(str(newArr)[1:-1])

        with open("/var/www/html/StockPredictor/basic/Training Algorithm/stockData.csv", "a") as f:
            for x in arr:
                if(str(x[0])!="nan"):
                    print(x)
                    f.write((str(x[0])+"\n"))
    except:
        print("----------fail")


