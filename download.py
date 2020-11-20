import yfinance as yf

data=[]

stock="MSFT"

msft = yf.Ticker(str(stock))

hist = msft.history(period="max")



for i in range(len(hist)):
      data.append(hist["High"][i])

print(data)
