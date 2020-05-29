const projection = new ol.proj.get('EPSG:4326');

////////////
// Getting Metadata
////////////

//Get tile-metadata produced by gdal2tiles32 and store it in the tileMetadata object. Necessary to ensure correct resolutions among other things
var tileMetadata = {};

//The folder, where the tiles are extracted from. Locally it can be "g2tTiles" for India or "newTestTiles" for the States
var tileFolders = ['g2tTiles', 'g2tSecondMap']
getTileMetadata(tileMetadata, tileFolders);

//Resolutions from the metadata xmlfile creates issues with loading the correct file if any zoomlayers are excluded
//Therefore resolutions tables are created manually.
var resolutions = new Array(14);
var matrixIds = new Array(14);
for (var z = 0; z < 14; ++z) {
  // generate resolutions and matrixIds arrays for this WMTS
  //The number in the resolution calculation is the units-per-pixel value at zoomlayer 0 in the xml file generated by gdal2tiles
  resolutions[z] = 0.03333333333514 / Math.pow(2, z);
  matrixIds[z] = z;
}

var wmslayerMap1 = new ol.layer.Tile({
  source: new ol.source.WMTS({
    url: tileFolders[0] + '/{TileMatrix}/{TileCol}/{TileRow}.tiff',
    projection: projection,
    tileGrid: new ol.tilegrid.WMTS({
      origin: tileMetadata[tileFolders[0] + "origin"],
      resolutions: resolutions,
      matrixIds: matrixIds,
      tileSize: 256
    }),
    requestEncoding: 'REST',
    transition: 0
  }),
  extent: tileMetadata[tileFolders[0] + "boundingBox"],
  opacity: 0.65 //The extent has been limited, since there I didn't test with the raster for the entire world
});

var wmslayerMap2 = new ol.layer.Tile({
  source: new ol.source.WMTS({
    url: tileFolders[1] + '/{TileMatrix}/{TileCol}/{TileRow}.tiff',
    projection: projection,
    tileGrid: new ol.tilegrid.WMTS({
      origin: tileMetadata[tileFolders[1] + "origin"],
      resolutions: resolutions,
      matrixIds: matrixIds,
      tileSize: 256
    }),
    requestEncoding: 'REST',
    transition: 0
  }),
  extent: tileMetadata[tileFolders[1] + "boundingBox"],
  opacity: 0.65 //The extent has been limited, since there I didn't test with the raster for the entire world
});

// define the base layer
var osmSource = new ol.source.OSM();
var osm = new ol.layer.Tile({
  source: osmSource
  // , extent: tileMetadata.boundingBox
});

var sharedView = new ol.View({
  projection,
  center: tileMetadata[tileFolders[0] + "center"],
  zoom: 7,
  maxZoom: 11,
  minZoom: 2
})

// define the map
var map = new ol.Map({
  target: 's2map',
  layers: [
    osm, wmslayerMap1
  ],
  wrapDateLine: true,
  view: sharedView
});

var map2 = new ol.Map({
  target: 'secondMap',
  layers: [
    osm, wmslayerMap2
  ],
  wrapDateLine: true,
  view: sharedView
});

//Creation of colorscale

var colorScale = {};
colorScale.color_steps = [
  '#fef0d9',
  '#fdd49e',
  '#fdbb84',
  '#fc8d59',
  '#e34a33',
  '#b30000'
]
colorScale.percentage_steps = [
  0,
  0.2,
  0.4,
  0.6,
  0.8,
  1
]
plotty.addColorScale("sequentialMultiHue6Colors", colorScale.color_steps, colorScale.percentage_steps);

// olGeoTiff setup
var olgt_map1 = new olGeoTiff(wmslayerMap1);
var olgt_map2 = new olGeoTiff(wmslayerMap2);
olgt_map1.plotOptions.palette = 'sequentialMultiHue6Colors';
olgt_map2.plotOptions.palette = 'sequentialMultiHue6Colors';

recolorMap()
// handle user input
$(window).on('load', function() {

  //Add the colors from the color palette to the legend
  for (i = 0; i < colorScale.percentage_steps.length; i++) {
    document.getElementById('d' + String(i)).style.background = colorScale.color_steps[i]
  }

  //Recolor map on movement or zoom
  // map.on("rendercomplete", function() {
  map.on("moveend", function() {
    recolorMap()
  });

});

// Find the highest value currently displayed and recolor based on this
var currentMax = 0;
var oldMax = currentMax;
function recolorMap() {

  var maxValues = [];

  //Getting map extent and zoom
  var mapExtent = map.getView().calculateExtent(map.getSize())
  var mapZoom = map.getView().getZoom();

  var zoomlevelAdjustment = 3
  //This variable should potentially be deleted later, if the extent get limited to the boundingBox of the layer
  //The loadExtent is the same as the mapextent, unless the mapextent shows an area outside the data area
  //- In this case the loadExtent gets reduced to the bounding box - this is to avoid attempt at loading data, which doesn't exist
  var loadExtent = new Array(4);
  loadExtent[0] = Math.max(mapExtent[0], tileMetadata[tileFolders[0] + "boundingBox"][0]);
  loadExtent[1] = Math.max(mapExtent[1], tileMetadata[tileFolders[0] + "boundingBox"][1])
  loadExtent[2] = Math.min(mapExtent[2], tileMetadata[tileFolders[0] + "boundingBox"][2])
  loadExtent[3] = Math.min(mapExtent[3], tileMetadata[tileFolders[0] + "boundingBox"][3])

  //Function for getting the url/filename for tiles based on their coordinates
  // var maxValues = [];

  //Get the number of tiles - same number of tiles, so no need to run this twice
  var tileNumber = 0;
  wmslayerMap1.getSource().getTileGrid().forEachTileCoord(loadExtent, mapZoom - zoomlevelAdjustment, function(tileCoord) {
    tileNumber++;
  })

  var currentTile = {};
  currentTile[tileFolders[0]] = 0;
  currentTile[tileFolders[1]] = 0;

  //Checks which tiles that currently are being displayed
  //This is done at a lower resolution than the current zoomlevel, since loading otherwise would be too slow
  findHighestValue(wmslayerMap2, tileFolders[1], tileFolders[0])
  findHighestValue(wmslayerMap1, tileFolders[0], tileFolders[1])

  // findHighestValue(wmslayerMap2)

  function findHighestValue(wmslayer, selfCounter, otherCounter) {

    var tileUrlFunction = wmslayer.getSource().getTileUrlFunction()

    wmslayer.getSource().getTileGrid().forEachTileCoord(loadExtent, mapZoom - zoomlevelAdjustment, function(tileCoord) {

      //Gets the name of each currently displayed tile
      tileName = tileUrlFunction(tileCoord, ol.proj.get('EPSG:4326'))
      asyncCall()
      async function asyncCall() {

        tileMaxValue = await calculateMaxValue(tileName);
        maxValues.push(tileMaxValue)
        currentTile[selfCounter]++;
        // console.log(currentTile[selfCounter])
        if (currentTile[selfCounter] == tileNumber && currentTile[otherCounter] == tileNumber && tileNumber != 0) {
          // console.log(maxValues.length)
          // console.log(maxValues.length)
          // console.log(currentTile[selfCounter])
          currentTile[selfCounter] = 0;
          currentTile[otherCounter] = 0;
          tileNumber = 0;
          currentMax = Math.max(...maxValues)
          if (Number.isInteger(currentMax) && currentMax != oldMax) {
            oldMax = currentMax
            olgt_map1.redraw(olgt_map1, currentMax, colorScale);
            olgt_map2.redraw(olgt_map2, currentMax, colorScale);
          }
        }

      }
    })

  }

}

function SearchCity() {
  var cityName = document.getElementById("requestedCity").value;
  var request = "https://nominatim.openstreetmap.org/search?q=" + cityName + "&format=geojson"
  var mapZoom = map.getView().getZoom();

  var xhttp = new XMLHttpRequest();

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var cityData = JSON.parse(this.responseText)
      var cityCoordinates = cityData.features[0].geometry.coordinates

      map.getView().setCenter(cityCoordinates)
      map.getView().setZoom(9)

    }
  }
  xhttp.open("GET", request, true);
  xhttp.send();

}
