import yfinance as yf
import lxml

data=[]

stock="MSFT"

msft = yf.Ticker(str(stock))

hist = msft.history(period="max")

print(msft.info['longName'])

txt = msft.info['longBusinessSummary']



x = txt.split(". ")

print(x[0]) 

data = (hist["High"])

print(data[1])