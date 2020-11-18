import csv

with open("/var/www/html/StockPredictor/basic/PastStockData.csv") as csvfile:
    rawData=[]
    readCSV = csv.reader(csvfile, delimiter=',')
    i=0
    for row in readCSV:
        i = i +1
        if i>15:
            rawData.append(float(row[2].replace(",", "")))



        
print(rawData)

#rawData.append(int(float(readCSV[3].replace(",", ""))))