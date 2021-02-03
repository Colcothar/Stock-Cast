import yfinance as yf

def getStockData(stockTicker):
    rawData=[]
    stock = yf.Ticker(str(stockTicker)) #creates request

    history = stock.history(period="max") #gets history

    for i in range(len(history)):
        if(str(history["High"][i])!="nan"):
            rawData.append(float(history["High"][i])) #writes the max stock price of the day to the array
    return(rawData) #return array


userInput = str(input("Enter stock: "))

while userInput!="end":

    f = open(str("/var/www/html/StockPredictor/Test Data/Stocks/" + userInput + ".csv"), "w")
    arr = getStockData(userInput)
    for x in arr:
        f.write((str(x)+"\n"))
    f.close()

    userInput = str(input("Enter stock: "))
