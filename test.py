import csv
with open('/var/www/html/StockPredictor/TestData/Valid.csv' , newline='') as f:
    readData = list(csv.reader(f))

print(readData)
print(readData)

def loadCSV(location, column ):
    rawData=[]

    with open(location) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            rawData.append(int(row[column].replace(",", "")))
    return rawData


print(loadCSV('/var/www/html/StockPredictor/TestData/Valid.csv'))

