import os
import subprocess
from geopy.geocoders import Nominatim
import numpy as np
import gdal
import pandas as pd
import time
import platform

# ---------------------------
# CONFIGURATION:
# ---------------------------


SSPs = ['SSP5']  # ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
models = ['GlobCover', 'GRUMP']  # ['GlobCover', 'GRUMP']
outputdir = os.path.expanduser('~') + '\\Desktop\\Data\\Raster\\'
extent = "76.0 29.0 78.0 28.0"  # Later to be replaced with the entirety of India

#Figures out what the operating system is to ensure that future os-commands are written correctly
#These is nessercery since linux and Window have different command words for deleting and writing multiple lines of code
class osCommandDict: #\\ skal også være en del af dette -.-
            def __init__(self, delete, newAction):
                self.delete = delete
                self.newAction = newAction


if platform.system()=="Windows":
    osCommand = osCommandDict("del", "&")
else:
    osCommand = osCommandDict("rm", ";")

# ---------------------------
# Clipping raster to the desired extent:
# ---------------------------

#Disables since it is not nessercery to clip every time - move to another file

start = time.time()

datadir = os.path.expanduser('~') + '\\Desktop\\Thesis\\RasterData\\'



for model in models:
    for ssp in SSPs:
        for year in range(2010, 2101, 10):

                # clip population file
                infile = '"' + datadir + model + '\\' + ssp + \
                    '\\popmean-' + str(year) + '.tiff"'

                clipped = '"' + outputdir + model + '\\' + ssp + \
                    '\\popmean-' + str(year) + '-clipped.tiff"'

                os.system('gdal_translate -projwin ' + extent +
                          ' -of GTiff -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -a_nodata -2147483648 '+infile + ' '+clipped + ' >> log.txt')

                
                
                # gdalwarp -te ' + extent +
                #           ' -wo NUM_THREADS=ALL_CPUS -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -srcnodata -2147483648 '+infile+' '+clipped+' >> log.txt')

                # clip urbanization file
                infile = '"' + datadir + model + '\\' + ssp + \
                    '\\urbanization-' + str(year) + '.tiff"'

                clipped = '"' + outputdir + model + '\\' + ssp + \
                    '\\urbanization-' + str(year) + '-clipped.tiff"'

                os.system('gdal_translate -projwin ' + extent +
                          ' -of GTiff -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -a_nodata -2147483648 '+infile + ' '+clipped + ' >> log.txt')

                # os.system('gdalwarp -te ' + extent +
                #           ' -wo NUM_THREADS=ALL_CPUS -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -srcnodata -2147483648 '+infile+' '+clipped+' >> log.txt')



end = time.time()

print("Raster clipping time: {0}".format(end-start))




