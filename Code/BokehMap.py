from bokeh.plotting import figure, save, output_file, show
from bokeh.tile_providers import get_provider, Vendors
from PIL import Image
import gdal
import numpy as np
import subprocess
import geopandas as gpd
import rasterio
from rasterio.plot import show as Rshow

# subprocess.run('gdaldem color-relief '+'testRaster.tiff'+' popcolor.txt ' + 'coloredfile.tiff'+' >> log.txt', shell=True, check=True)

def BokehFromTiff():
    src = gdal.Open('testRaster.tiff', gdal.GA_Update)
    band = src.GetRasterBand(1)
    imarray = np.array(band.ReadAsArray())
    output_file(r"testRaster.html")
    imarray = imarray[::-1]
    p = figure(x_range=(-180,180), y_range=(-60,85))
    p.image_rgba(image=[imarray], x=[-180], y=[-60], dw=[360], dh=[145],
    dilate=False)
    save(p)
    show(p)
    
def BokehWithoutGdal():
    im = Image.open('coloredfile.tiff')
    im = im.convert("RGBA")
    imarray = np.array(im)
    imarray = imarray[::-1]   
    p = figure(x_range=(-180,180), y_range=(-60,85), width=1000, height=1000)
    
    p.image_rgba(image=[imarray], x=[-180], y=[-60], dw=[360], dh=[145],
    dilate=False)
    
    show(p)


def loadAsGrid():
    grid = gpd.read_file('testRaster.tiff')
    CRS = grid.crs
    print(CRS)

def rasterioTest():
    fp = r'testRaster.tiff'
    raster = rasterio.open(fp)
    Rshow(raster)
    

# rasterioTest()
BokehFromTiff()
# BokehWithoutGdal()

# colorPlease()