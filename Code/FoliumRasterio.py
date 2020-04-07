# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 15:00:02 2020

@author: A-G-R
"""


import os 
import folium
from folium import plugins
import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import earthpy as et

########################################################
#Importing test data
########################################################
# # Import data from EarthPy
#TO:DO:
    # Update, so placement is correct
    # Get colors to work 
    # Is it possible to get data in the reverse direction?
    
    



# data = et.data.get_data('colorado-flood')

# # # Set working directory to earth-analytics
# os.chdir(os.path.join(et.io.HOME, 'earth-analytics'))


# ########################################################
# #Creating Raster layer
# ########################################################

# Create variables for destination coordinate system and the name of the projected raster
dst_crs = 'EPSG:4326' 

# in_path = os.path.join("data", "colorado-flood", "spatial", 
#                         "boulder-leehill-rd", "post-flood", 
#                         "lidar", "post_DTM.tif")


# out_path = os.path.join("data", "colorado-flood", "spatial", 
#                         "boulder-leehill-rd", "outputs", 
#                         "reproj_post_DTM.tif")


in_path = 'testRaster.tiff'
out_path = os.path.join("FRtest", "NewRaster.tif")


# Use rasterio package as rio to open and project the raster
# with rio.open(in_path) as src:
#     transform, width, height = calculate_default_transform(
#         src.crs, dst_crs, src.width, src.height, *src.bounds)
#     kwargs = src.meta.copy()
#     kwargs.update({
#         'crs': dst_crs,
#         'transform': transform,
#         'width': width,
#         'height': height
#     })
 

    # Use rasterio package as rio to write out the new projected raster
    # Code uses loop to account for multi-band rasters
    # with rio.open(out_path, 'w', **kwargs) as dst:
    #     for i in range(1, src.count + 1):
    #         reproject(
    #         source=rio.band(src, i),
    #         destination=rio.band(dst, i),
    #         src_transform=src.transform,
    #         src_crs=src.crs,
    #         dst_transform=transform,
    #         dst_crs=dst_crs,
    #         resampling=Resampling.nearest)    
# Use rasterio to import the reprojected data as img
with rio.open(in_path) as src:
    boundary = src.bounds
    img = src.read()
    nodata = src.nodata
    
####################################################################
#Create Folium map
####################################################################

m = folium.Map(location=[40.06, -105.30],
                    tiles='Stamen Terrain', zoom_start = 13)

# Overlay raster called img using add_child() function (opacity and bounding box set)
m.add_child(folium.raster_layers.ImageOverlay(img[0], opacity=1, 
                                   bounds =[[40.04577828237005, -105.32837712340124], [40.093923431943214, -105.28139535136515]]))

    


m.save('FoliumR.html')





################################################################
#New test with Numpy
# ################################################################
# import numpy as np
# import gdal
# image = np.zeros((61, 1))

# image[45, :] = 1.0


# m = folium.Map([37, 0], zoom_start=3)


# folium.raster_layers.ImageOverlay(
#     image=image,
#     bounds=[[0, -60], [60, 60]],
#     origin='lower',
#     colormap=lambda x: (1, 0, 0, x),
#     mercator_project=True,
# ).add_to(m)

# m.save('FoliumR.html')