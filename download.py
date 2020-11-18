import requests
stock = input("Enter stock")
    
url = "http://download.macrotrends.net/assets/php/stock_data_export.php?t=" + stock
      
r = requests.get(url)

with open('/var/www/html/StockPredictor/basic/DownloadedPastStockData.csv', 'wb') as f:
      f.write(r.content) 
      print(r.content)


      