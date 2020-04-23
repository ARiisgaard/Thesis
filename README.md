# Thesis


---
## Using gdal2tiles

python C:\Users\Public\Python\Thesis\Code/gdal2tiles32.py --leaflet --zoom=2-4 --profile=raster --no-kml --webviewer=none testRaster.tiff g2tTiles

 - C:\Users\Public\Python\Thesis\Code/gdal2tiles32.py - path to the modified gdaal2tiles files
 - leaflet - this option ensures the xyz format instead of tms
 - zoom=2-4 - zoom levels
 - profile=raster - Input format is raster
 - webviewer=none - prevent the creation of webviewer, which wouldn't work anyways since they cannot handle the tiff-tiles
 - input file
 - output folder
 - no-kml - prevents the generation of Google Earth files
