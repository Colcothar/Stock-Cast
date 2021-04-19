import yfinance as yf

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

for i in range(100):
    print(getStockData("AAPL"))

print("FINISHED")