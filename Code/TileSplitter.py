import os
import gdal

in_path = os.path.expanduser('~') + '\\Desktop\\Data\\Raster\\GRUMP\\SSP5\\'
input_filename = 'popmean-2010-clipped.tiff'

# As a test tiles are only generate for the 10th zoom level
out_path = os.path.expanduser('~') + '\\Desktop\\Data\\10\\'
# output_filename = 'tile_'

tile_size_x = 200#50
tile_size_y = 300#70

ds = gdal.Open(in_path + input_filename)
band = ds.GetRasterBand(1)
xsize = band.XSize
ysize = band.YSize

for i in range(0, xsize, tile_size_x):
    os.system('cd '+out_path+' & mkdir ' + str(i))
    for j in range(0, ysize, tile_size_y):
        com_string = "gdal_translate -of GTIFF -srcwin " + str(i) + ", " + str(j) + ", " + str(tile_size_x) + ", " + str(
            tile_size_y) + " " + str(in_path) + str(input_filename) + " " + str(out_path) + str(i) + "\\" + str(j) + ".tiff"
        os.system(com_string)
