import gdal
import numpy as np
import os
tileFolder = "g2tTiles"
tilePath = os.getcwd() + "\\OpenlayerGeotiff\\"

#Function for getting values out of the first band of a tiff file
def openTIFFasNParray(file):
    src = gdal.Open(file, gdal.GA_Update)
    band = src.GetRasterBand(1)
    a = np.array(band.ReadAsArray())
    # replace nan cells with 0 - fine for the purpose of this script
    notanumber = -2147483648
    a[a==notanumber]=0
    return a



#This function creates a 

maxValue = "{"
zoomlevel = [ f.name for f in os.scandir(tilePath + tileFolder) if f.is_dir() ]
for z in zoomlevel:
    TileCol = [ f.name for f in os.scandir(tilePath + tileFolder + "\\"+z) if f.is_dir() ]
    for c in TileCol:
        TileRow = [ f.name for f in os.scandir(tilePath + tileFolder + "\\"+z+ "\\" +c) if ".tiff" in f.name]
        for r in TileRow:
            TileName = tileFolder  + "\\" + z + "\\" + c + "\\" + r
                        # print(tilePath + TileName)
            pop = openTIFFasNParray(tilePath + TileName)
            maxPop = 0
            if(np.max(pop) > maxPop):
                maxPop = np.max(pop)
            
            NameWithDoubleEscape = tileFolder  + "/" + z + "/" + c + "/" + r #Double \\ are needed for the final result, since a spare backslash is needed for escaping the backslash in js
            maxValue = maxValue + "\"" + NameWithDoubleEscape + "\":" + str(maxPop) + ","

maxValue = maxValue[:-1]#Removed the trailing ,            
maxValue = maxValue + "}"           
            
            
        
print(maxValue)
file = open(tilePath + "maxValues.json", "w+")        
file.write(maxValue)
file.close()  

print("Writting done")


    
# 
# for year in range(2010,2101,10):
# 
#     pop = openTIFFasNParray(datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '-clipped.tiff')
# 
#     if(np.max(pop) > maxPop):
#         maxPop = np.max(pop)
