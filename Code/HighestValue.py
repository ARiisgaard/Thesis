import os
import subprocess
from geopy.geocoders import Nominatim
import numpy as np
import gdal
import pandas as pd
import time

SSPs = ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
models = ['GlobCover', 'GRUMP']
maxPop = 0
datadir = os.path.expanduser('~') + '\\Desktop\\Thesis\\RasterData\\'

def openTIFFasNParray(file):
    src = gdal.Open(file, gdal.GA_Update)
    band = src.GetRasterBand(1)
    a = np.array(band.ReadAsArray())
    # replace nan cells with 0 - fine for the purpose of this script
    notanumber = -2147483648
    a[a==notanumber]=0
    return a
    
    
for model in models:
    for ssp in SSPs:

        for year in range(2010,2101,10):

            pop = openTIFFasNParray(datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '.tiff')

            if(np.max(pop) > maxPop):
                maxPop = np.max(pop)
                print(maxPop)
