#This script creates a json-file with names and max values for each tiff-tile

import gdal
import numpy as np
import os

#Directory containing the maptiles and the path to it
tilePath = os.getcwd() + "\\OpenlayerGeotiff\\"
tileFolder = "g2tTiles"

#Function for getting values out of the first band of a tiff file
def openTIFFasNParray(file):
    src = gdal.Open(file, gdal.GA_Update)
    band = src.GetRasterBand(1)
    a = np.array(band.ReadAsArray())
    # replace nan cells with 0 - fine for the purpose of this script
    notanumber = -2147483648
    a[a==notanumber]=0
    return a


#maxValue is going to contain the content of the json file before it gets written to the file. 
#It is initially defined as "{", because jsons start with this
maxValue = "{"

#Goes through each tiff and find their highest value. The filename and highest value then gets added to the string
zoomlevel = [ f.name for f in os.scandir(tilePath + tileFolder) if f.is_dir() ]
for z in zoomlevel:
    TileCol = [ f.name for f in os.scandir(tilePath + tileFolder + "\\"+z) if f.is_dir() ]
    for c in TileCol:
        TileRow = [ f.name for f in os.scandir(tilePath + tileFolder + "\\"+z+ "\\" +c) if ".tiff" in f.name]
        for r in TileRow:
            #The name used by python to locate the file
            TileName = tileFolder  + "\\" + z + "\\" + c + "\\" + r

            #Opens the file and finds it highest value
            pop = openTIFFasNParray(tilePath + TileName)
            maxPop = 0
            if(np.max(pop) > maxPop):
                maxPop = np.max(pop)
            
            #Name used by javascript. It is a different format, because it needs to match the formate of the forEachTileCoord-function
            TileNameJS = tileFolder  + "/" + z + "/" + c + "/" + r 
            
            #Appends the filename and max value to the json-string
            maxValue = maxValue + "\"" + TileNameJS + "\":" + str(maxPop) + ","

#To finish the json the trailing comma is remove a "}" is placed in the end  
maxValue = maxValue[:-1]          
maxValue = maxValue + "}"           
            
            
#The json-string gets written to a file        
print(maxValue)
file = open(tilePath + "maxValues.json", "w+")        
file.write(maxValue)
file.close()  

print("Writting done")