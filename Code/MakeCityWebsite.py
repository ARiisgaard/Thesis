import os
import subprocess
from geopy.geocoders import Nominatim
import numpy as np
import gdal
import pandas as pd
import time


import matplotlib
matplotlib.use('TkAgg')  # fixes weird matplotlib bug on Mac OS


import matplotlib.pyplot as plt


# This script takes our own population projections as well as the output from CompareWithSEDAC.py and turns the generated series of GeoTIFFs into a colorized aninmated GIF using a bivariate color scale (centered around 0) from ColorBrewer: http://colorbrewer2.org/#type=diverging&scheme=PiYG&n=11
# The different steps are explained here: https://github.com/crstn/CISC/wiki/Turning-population-grids-into-colored-animated-figures

# Then it puts all of that stuff on a website for comparison ...


# ---------------------------
# CONFIGURATION:
# ---------------------------
# Put in a city name below, for which we'll look up the location
# using an online geocoder
# Pick the SSP(s) and urbanization model(s) you want the GIF for
# ---------------------------
start = time.time()
places = [u'Bangalore']
size = 0.4 # in degrees; i.e. the GIF will cover an area of
           # 2 x size by  2 x size centered on the place chosen above. In other
           # words, it will expand by size in four directions away from the
           # chosen place's lat/lon position

# don't change these for this script; would screw up the generated website
# if any of them were missing
# ['SSP1', 'SSP2', 'SSP3', 'SSP4', 'SSP5']
SSPs = ['SSP5']
models = ['GlobCover', 'GRUMP']
outputdir = os.path.expanduser('~') + '\\Desktop\\Thesis\\Result\\'


# some functions we'll be using
# creates a directory if it doesn't exist yet
def makeSafe(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# does what it says...
def openTIFFasNParray(file):
    src = gdal.Open(file, gdal.GA_Update)
    band = src.GetRasterBand(1)
    a = np.array(band.ReadAsArray())
    # replace nan cells with 0 - fine for the purpose of this script
    notanumber = -2147483648
    a[a==notanumber]=0
    return a


# Here we go:
for place in places:

    # find the place:
    try:
        geolocator = Nominatim(user_agent="CISC App")
        location = geolocator.geocode(place)
        print(location.address.encode('utf-8'))
    except: # Temp solution: Sometimes I would get the error: Geocoder: Service timed out - this ensures that the process can keep going even if this step fails
        print("geolocator could not connect")
        class locationObject:
                    def __init__(self, longitude, latitude):
                        self.longitude = longitude
                        self.latitude = latitude


        location = locationObject(10.000654, 53.550341) #These are the coordinates of Hamburg
    # extent to clip to
    extent = str(location.longitude-size) + ' ' + str(location.latitude-size) + ' ' + str(location.longitude+size) + ' ' + str(location.latitude+size)

    # get rid of any potential spaces in the place name for nicer file names
    place = place.replace(" ", "_")

    # ----------------------------------------------
    # First: Just our data
    # ----------------------------------------------
    datadir = os.path.expanduser('~') + '\\Desktop\\Thesis\\RasterData\\'
    for model in models:
        for ssp in SSPs:

            for year in range(2010, 2101, 10):

                # clip population file
                infile = '"' + datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '.tiff"'

                clipped = '"' + datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '-clipped.tiff"'

                os.system('gdalwarp -te '+ extent +' -wo NUM_THREADS=ALL_CPUS -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -srcnodata -2147483648 '+infile+' '+clipped+' >> log.txt')

                # clip urbanization file
                infile = '"' + datadir + model + '\\' + ssp + '\\urbanization-' + str(year) + '.tiff"'

                clipped = '"' + datadir + model + '\\' + ssp + '\\urbanization-' + str(year) + '-clipped.tiff"'

                os.system('gdalwarp -te '+ extent +' -wo NUM_THREADS=ALL_CPUS -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -srcnodata -2147483648 '+infile+' '+clipped+' >> log.txt')

    # Now we'll go through again to figure out what the maximum value in any
    # of the rasters is, so that we can apply the the same color scale to all
    maxPop = 0
    minPop = 10000000 # we just pick something super high here...


    # at the same time, we'll pick up the numbers to generate our charts:


    for model in models:
        for ssp in SSPs:

            totalpop = []
            urbanpop = []
            years    = []


            for year in range(2010,2101,10):

                pop = openTIFFasNParray(datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '-clipped.tiff')

                if(np.max(pop) > maxPop):
                    maxPop = np.max(pop)

                if(np.min(pop) < minPop):
                    minPop = np.min(pop)

                # populate the arrays for our charts:
                urb = openTIFFasNParray(datadir + model + '\\' + ssp + '\\urbanization-' + str(year) + '-clipped.tiff')

                # total population in map extent for the current year
                totalpop.append(np.sum(pop))
                # urban population in map extent for the current year
                urbanpop.append(np.sum(pop[urb == 2]))
                # current year
                years.append(year)

#                print(f"Total pop: {totalpop}")
#                print(f"Urban pop: {urbanpop}")


            # Create the output folder:

            makeSafe(outputdir+'figures') # put the figures in a subfolder

            # Make a stacked area chart in seaborn
            plt.stackplot(year , [urbanpop, totalpop],
                          labels = ['Urban population', 'Total population'])
            plt.legend(loc='upper left')
            plt.savefig(outputdir+'figures\\'+model+'-' +
                        ssp+'-'+place+'-chart.png', dpi=300)

    # Now that we know what the min and max population in the area is,
    # we can generate a sequential color scale for the numbers:
    # http://colorbrewer2.org/#type=sequential&scheme=OrRd&n=9

    stops = np.linspace(minPop, maxPop, num=9)
    print(minPop)
    print(maxPop)
    print(stops)
    
#     os.system("""echo "nv 173 240 255
# """+str(stops[0])+""" 255 247 236
# """+str(stops[1])+""" 254 232 200
# """+str(stops[2])+""" 253 212 158
# """+str(stops[3])+""" 253 187 132
# """+str(stops[4])+""" 252 141 89
# """+str(stops[5])+""" 239 101 72
# """+str(stops[6])+""" 215 48 31
# """+str(stops[7])+""" 179 0 0
# """+str(stops[8])+""" 127 0 0
#                     " >> popcolor.txt""")

    color = """nv 173 240 255
"""+str(stops[0])+""" 255 247 236
"""+str(stops[1])+""" 254 232 200
"""+str(stops[2])+""" 253 212 158
"""+str(stops[3])+""" 253 187 132
"""+str(stops[4])+""" 252 141 89
"""+str(stops[5])+""" 239 101 72
"""+str(stops[6])+""" 215 48 31
"""+str(stops[7])+""" 179 0 0
"""+str(stops[8])+""" 127 0 0
                    """

    f = open("popcolor.txt", "w+")
    f.write(color)
    f.close()

    # os.system("start popcolor.txt")

    # Go through again and colorize them using the color scale above
    for model in models:
        for ssp in SSPs:
            for year in range(2010,2101,10):

                infile = '"' + datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '-clipped.tiff"'

                colorfile = '"' + datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '-color.tiff"'

                labelfile =  '"' + datadir + model + '\\' + ssp + '\\popmean-' + str(year) + '-label.tiff"'

                # colorize

                # os.system('gdaldem color-relief '+infile+' popcolor.txt '+colorfile+' >> log.txt')
                subprocess.run('gdaldem color-relief '+infile+' popcolor.txt ' + colorfile+' >> log.txt', shell=True, check=True)


                # resize
                print(colorfile)
                # os.system('magick '+colorfile+' -resize 250x250 ' +
                #           colorfile+' >> log.txt')
                subprocess.run('magick -quiet '+colorfile+' -resize 250x250 ' +
                               colorfile+' >> log.txt', shell=True, check=True)

                # label with year and delete the colorfile
                # os.system('magick '+colorfile+' -font Times-New-Roman -pointsize 15 -fill black -gravity southwest -annotate +20+20 ' +
                #           str(year)+' '+labelfile+' >> log.txt; del '+colorfile)
                subprocess.run('magick -quiet '+colorfile+' -font Times-New-Roman -pointsize 15 -fill black -gravity southwest -annotate +20+20 ' +
                               str(year)+' '+labelfile+' >> log.txt & del '+colorfile, shell=True, check=True)
            print("Done coloring, making a GIF")

            # All files have been colorized and labeled, let's make a GIF:

            folder = '"' + datadir + model + '\\' + ssp +'"'
            subprocess.run('cd '+folder+' & magick -quiet -delay 40 -loop 0 *label.tiff "' +
                           outputdir+'figures\\'+model+'-'+ssp+'-'+place+'-pop.gif" >> log.txt', shell=True, check=True)

            # clean up:
            subprocess.run(
                'cd '+folder+' & del *label.tiff & del *clipped.tiff; ', shell=True, check=True)



    # remove the color scale file again
    subprocess.run("del popcolor.txt", shell=True, check=True)



    # ----------------------------------------------
    # NEXT UP: Difference compared to the SEDAC data
    # ----------------------------------------------
    datadir = os.path.expanduser('~') + '\\Desktop\\Thesis\\Comparison\\'


    # First, we'll clip all years to the extent around our place

    for model in models:
        for ssp in SSPs:
            for year in range(2010,2101,10):

                infile = '"' + datadir + model + '\\' + \
                    ssp + '\\diff-pop-' + str(year) + '.tiff"'

                clipped = '"' + datadir + model + '\\' + ssp + \
                    '\\diff-pop-' + str(year) + '-clipped.tiff"'

                subprocess.run('gdalwarp -te ' + extent + ' -wo NUM_THREADS=ALL_CPUS -co NUM_THREADS=ALL_CPUS -co COMPRESS=LZW -srcnodata -2147483648 ' +
                          infile+' '+clipped+' >> log.txt', shell=True, check=True)
    # Now we'll go through again to figure out what the maximum value in any
    # of the rasters is, so that we can apply the the same color scale to all
    maxDiff = 0

    for model in models:
        for ssp in SSPs:
            # First, we'll clip all years to the extent around our place
            for year in range(2010,2101,10):

                clipped = datadir + model + '\\' + ssp + \
                    '\\diff-pop-' + str(year) + '-clipped.tiff'

                a = openTIFFasNParray(clipped)

                if(np.max(np.absolute(a)) > maxDiff):
                    maxDiff = np.max(np.absolute(a))


    # Now that we know what the maximum difference across all models, SSPs and
    # years is, we can make a divergent color centered around 0
    # os.system("""echo "nv 173 240 255
    # """+str(maxPop)+""" 142 1 82
    # """+str(maxDiff-minPop)+""" 197 27 125
    # """+str(maxDiff-minPop)+""" 222 119 174
    # """+str(maxDiff-minPop)+""" 241 182 218
    # """+str(maxDiff*0.2)+""" 253 224 239
    # 0 247 247 247
    # -"""+str(maxDiff*0.2)+""" 230 245 208
    # -"""+str(maxDiff*0.4)+""" 184 225 134
    # -"""+str(maxDiff*0.6)+""" 127 188 65
    # -"""+str(maxDiff*0.8)+""" 77 146 33
    # -"""+str(minPop)+""" 39 100 25
    #                 " >> color.txt""")

    color = """nv 173 240 255
"""+str(maxPop)+""" 142 1 82
"""+str(maxDiff-minPop)+""" 197 27 125
"""+str(maxDiff-minPop)+""" 222 119 174
"""+str(maxDiff-minPop)+""" 241 182 218
"""+str(maxDiff*0.2)+""" 253 224 239
0 247 247 247
-"""+str(maxDiff*0.2)+""" 230 245 208
-"""+str(maxDiff*0.4)+""" 184 225 134
-"""+str(maxDiff*0.6)+""" 127 188 65
-"""+str(maxDiff*0.8)+""" 77 146 33
-"""+str(minPop)+""" 39 100 25
                    """
    f = open("color.txt", "w+")
    f.write(color)
    f.close()



    # Go through again and colorize them using the color scale above
    for model in models:
        for ssp in SSPs:
            for year in range(2010,2101,10):

                infile = '"' + datadir + model + '\\' + ssp + '\\diff-pop-' + str(year) + '-clipped.tiff"'

                colorfile = '"' + datadir + model + '\\' + ssp + '\\diff-pop-' + str(year) + '-color.tiff"'

                labelfile =  '"' + datadir + model + '\\' + ssp + '\\diff-pop-' + str(year) + '-label.tiff"'

                # colorize
                subprocess.run('gdaldem color-relief '+infile+' color.txt ' +
                          colorfile+' >> log.txt', shell=True, check=True)

                # resize
                subprocess.run('magick -quiet '+colorfile+' -resize 250x250 ' +
                          colorfile+' >> log.txt', shell=True, check=True)

                # label with year
                subprocess.run('magick -quiet '+colorfile+' -font Times-New-Roman -pointsize 15 -fill black -gravity southwest -annotate +20+20 ' +
                          str(year)+' '+labelfile+' >> log.txt', shell=True, check=True)

            print("Done coloring, making a GIF")

            # All files have been colorized and labeled, let's make a GIF:
            makeSafe(outputdir+'figures') # put the figures in a subfolder

            folder = '"' + datadir + model + '\\' + ssp +'"'
            subprocess.run('cd '+folder+' & convert -delay 40 -loop 0 *label.tiff "' +
                           outputdir+'figures\\'+model+'-'+ssp+'-'+place+'-comparison.gif" >> log.txt', shell=True, check=True)

            # clean up:
            subprocess.run(
                'cd '+folder+' & del *label.tiff & del *clipped.tiff', shell=True, check=True)



    # remove the color scale file again
    subprocess.run("del color.txt", shell=True, check=True)

    # make a website that shows them side by side
    # remove it first if we have an old version:
    of = outputdir+place+'.html'
    if os.path.exists(of):
        os.remove(of)

    with open(of, "w+") as text_file:
        print("""<html>
    <head>
      <style>
        body       { font-family: Helvetica, sans-serif }
        p.vertical { writing-mode: vertical-rl }
        td         { border: 0; margin: 0}
        td.l       { color: white; text-align: center;
                     width:30px; height: 30px; padding: 0}
        a:link, a:visited { color: black }
        a:hover    { color: blue; }
        td#c1      { background: #8e0152 }
        td#c2      { background: #c51b7d }
        td#c3      { background: #de77ae }
        td#c4      { background: #f1b6da }
        td#c5      { background: #fde0ef }
        td#c6      { background: #f7f7f7 }
        td#c7      { background: #e6f5d0 }
        td#c8      { background: #b8e186 }
        td#c9      { background: #7fbc41 }
        td#c10     { background: #4d9221 }
        td#c11     { background: #276419 }
        td#d1      { background: #fff7ec }
        td#d2      { background: #fee8c8 }
        td#d3      { background: #fdd49e }
        td#d4      { background: #fdbb84 }
        td#d5      { background: #fc8d59 }
        td#d6      { background: #ef6548 }
        td#d7      { background: #d7301f }
        td#d8      { background: #b30000 }
        td#d9      { background: #7f0000 }
      </style>
    </head>
    <body>
      <table>
      <tr>
        <td></td>
        <td colspan='5'>
          <h2><a href='https://www.openstreetmap.org/#map=11/"""+str(location.latitude)+"""/"""+str(location.longitude)+"""'>"""+place+"""</a>: CISC spatialization</h2>
          </td>
          </tr>
          <tr>
          <td></td>
          <td>SSP1</td>
          <td>SSP2</td>
          <td>SSP3</td>
          <td>SSP4</td>
          <td>SSP5</td>
          </tr>
          <tr>
          <td>
          <p class='vertical'>GlobCover</p>
          </td>
          <td><img src='figures/GlobCover-SSP1-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GlobCover-SSP2-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GlobCover-SSP3-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GlobCover-SSP4-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GlobCover-SSP5-"""+place+"""-pop.gif' /></td>
          </tr>
          <tr>
          <td>
          <p class='vertical'>GRUMP</p>
          </td>
          <td><img src='figures/GRUMP-SSP1-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GRUMP-SSP2-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GRUMP-SSP3-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GRUMP-SSP4-"""+place+"""-pop.gif' /></td>
          <td><img src='figures/GRUMP-SSP5-"""+place+"""-pop.gif' /></td>
          </tr>
          <tr>
          <td></td>
          <td colspan='5'>
          <table>
            <tr>
              <td colspan="9">Population per cell</td>
            </tr>
            <tr>
      <td class='l' id='d1' title='"""+"{:,}".format(int(stops[0]))+"""'></td>
      <td class='l' id='d2' title='"""+"{:,}".format(int(stops[1]))+"""'></td>
      <td class='l' id='d3' title='"""+"{:,}".format(int(stops[2]))+"""'></td>
      <td class='l' id='d4' title='"""+"{:,}".format(int(stops[3]))+"""'></td>
      <td class='l' id='d5' title='"""+"{:,}".format(int(stops[4]))+"""'></td>
      <td class='l' id='d6' title='"""+"{:,}".format(int(stops[5]))+"""'></td>
      <td class='l' id='d7' title='"""+"{:,}".format(int(stops[6]))+"""'></td>
      <td class='l' id='d8' title='"""+"{:,}".format(int(stops[7]))+"""'></td>
      <td class='l' id='d9' title='"""+"{:,}".format(int(stops[8]))+"""'></td>
            </tr>
            <tr>
              <td colspan="4" style='text-align: left'>"""+"{:,}".format(minPop)+"""</td>
              <td></td>
              <td colspan="4" style='text-align: right'>"""+"{:,}".format(maxPop)+"""</td>
            </tr>
          </table>
          </td>
          </tr>
        <tr>
          <td></td>
          <td colspan='5'>
             <h2 style='margin-top: 70px'><a href='https://www.openstreetmap.org/#map=11/"""+str(location.latitude)+"""/"""+str(location.longitude)+"""'>"""+place+"""</a>: comparison with <a href='https://sedac.ciesin.columbia.edu/data/set/popdynamics-pop-projection-ssp-downscaled-1km-2010-2100'>SEDAC data</a></h2>
            </td>
            </tr>
            <tr>
            <td></td>
            <td>SSP1</td>
            <td>SSP2</td>
            <td>SSP3</td>
            <td>SSP4</td>
            <td>SSP5</td>
            </tr>
            <tr>
            <td>
            <p class='vertical'>GlobCover</p>
            </td>
            <td><img src='figures/GlobCover-SSP1-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GlobCover-SSP2-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GlobCover-SSP3-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GlobCover-SSP4-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GlobCover-SSP5-"""+place+"""-comparison.gif' /></td>
            </tr>
            <tr>
            <td>
            <p class='vertical'>GRUMP</p>
            </td>
            <td><img src='figures/GRUMP-SSP1-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GRUMP-SSP2-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GRUMP-SSP3-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GRUMP-SSP4-"""+place+"""-comparison.gif' /></td>
            <td><img src='figures/GRUMP-SSP5-"""+place+"""-comparison.gif' /></td>
            </tr>
            <tr>
            <td></td>
            <td colspan="5">
            <table>
              <tr>
                <td colspan="5" style='text-align: right'>&larr; More in CISC</td>
                <td></td>
                <td colspan="5">
                  <p style='text-align: left'>More in SEDAC &rarr; <p>
                </td>
              </tr>
              <tr>
        <td class='l' id='c1' title='"""+"{:,}".format(maxDiff)+"""'></td>
        <td class='l' id='c2' title='"""+"{:,}".format(int(maxDiff*0.8))+"""'></td>
        <td class='l' id='c3' title='"""+"{:,}".format(int(maxDiff*0.6))+"""'></td>
        <td class='l' id='c4' title='"""+"{:,}".format(int(maxDiff*0.4))+"""'></td>
        <td class='l' id='c5' title='"""+"{:,}".format(int(maxDiff*0.2))+"""'></td>
        <td class='l' id='c6' title='0'></td>
        <td class='l' id='c7' title='"""+"{:,}".format(int(maxDiff*0.2))+"""'></td>
        <td class='l' id='c8' title='"""+"{:,}".format(int(maxDiff*0.4))+"""'></td>
        <td class='l' id='c9' title='"""+"{:,}".format(int(maxDiff*0.6))+"""'></td>
        <td class='l' id='c10' title='"""+"{:,}".format(int(maxDiff*0.8))+"""'></td>
        <td class='l' id='c11' title='"""+"{:,}".format(maxDiff)+"""'></td>
              </tr>
              <tr>
                <td colspan="5" style='text-align: left'>"""+"{:,}".format(maxDiff)+"""</td>
                <td></td>
                <td colspan="5" style='text-align: right'>"""+"{:,}".format(maxDiff)+"""</td>
              </tr>
            </table>
            </td>
            </tr>
            </table>
            </body>
            </html>""", file=text_file)

    os.system(of)


print('Done.')
end = time.time()

print("Time spent:")
print(end - start)
