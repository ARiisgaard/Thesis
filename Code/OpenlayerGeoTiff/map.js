const projection = ol.proj.get('EPSG:4326');

////////////
// Getting Metadata
////////////

//Get tile-metadata produced by gdal2tiles32 and store it in the tileMetadata object. Necessary to ensure correct resolutions among other things
var tileMetadata = {};

//The folder, where the tiles are extracted from. Locally it can be "g2tTiles" for India or "newTestTiles" for the States
tileMetadata.tileFolder = 'g2tTiles';
getTileMetadata(tileMetadata);

//Directory with maxvalues for each tile - Used for coloring later
var maxValue = {};
$.getJSON("maxValues.json", function(json) {
  maxValue = json
});
////////////

//Creating the layer with population data. Seperated into three variables, because they are called individually to apply the coloring
var tileGrid = new ol.tilegrid.WMTS({origin: tileMetadata.origin, resolutions: tileMetadata.resolutions, matrixIds: tileMetadata.matrixIds, tileSize: 256})

var tileSource = new ol.source.WMTS({
  // url: 'http://webportals.ipsl.jussieu.fr/ScientificApps/dev/forge_patrick/eox/tileSet/{TileMatrix}/{TileRow}/{TileCol}.tif',
  url: tileMetadata.tileFolder + '/{TileMatrix}/{TileCol}/{TileRow}.tiff',
  projection: projection,
  tileGrid: tileGrid,
  requestEncoding: 'REST',
  transition: 0
})

var wmslayer = new ol.layer.Tile({
  source: tileSource, extent: tileMetadata.boundingBox //The extent has been limited, since there I didn't test with the raster for the entire world
});

// define the base layer
var osmSource = new ol.source.OSM();
var osm = new ol.layer.Tile({source: osmSource, extent: tileMetadata.boundingBox});

// define the map
var map = new ol.Map({
  target: 's2map',
  layers: [
    osm, wmslayer
  ],
  wrapDateLine: true,
  view: new ol.View({projection, center: tileMetadata.center, zoom: 7, maxZoom: 11, minZoom: 2}),
  controls: ol.control.defaults({
    attributionOptions: {
      collapsible: false
    }
  })
});

//Creation of colorscale

var colorScale = {};
colorScale.color_steps = ['#fef0d9','#fdd49e','#fdbb84','#fc8d59','#e34a33','#b30000']
colorScale.percentage_steps = [0, 0.2, 0.4, 0.6, 0.8, 1]
plotty.addColorScale("sequentialMultiHue6Colors", colorScale.color_steps, colorScale.percentage_steps);

// olGeoTiff setup
var olgt_map = new olGeoTiff(wmslayer);
olgt_map.plotOptions.domain = [0, 2000];
olgt_map.plotOptions.noDataValue = -9999;
olgt_map.plotOptions.palette = 'sequentialMultiHue6Colors';



// handle user input
$(window).on('load', function() {


//Add the colors from the color palette to the legend
  for (i = 0; i < colorScale.percentage_steps.length; i++) {
    document.getElementById('d'+String(i)).style.background = colorScale.color_steps[i]
}

  var $container = $('#s2map').parent();

  // slider2 (opacity)
  var slider2 = $container.find('.opacityslider')[0];

  var opacity = 0.7;
  noUiSlider.create(slider2, {
    start: opacity,
    connect: true,
    range: {
      'min': 0,
      'max': 1
    },
    tooltips: true
  });
  wmslayer.setOpacity(opacity);

  slider2.noUiSlider.on('slide', function(values) {
    wmslayer.setOpacity(values[0] * 1);
  });
  var Uppervalue = 0; 

  //Recolor map on movement or zoom
  map.on("moveend", function() {
     recolorMap()
  });
  


});

// Find the highest value currently displayed and recolor based on this
function recolorMap(){

  
  
    var mapExtent = map.getView().calculateExtent(map.getSize())
    var mapZoom = map.getView().getZoom();
  
    //Calculating the max population - Default is set to 0
    var currentMax = 0;
  
    //Function for getting the url/filename for tiles based on their coordinates
    var tileUrlFunction = tileSource.getTileUrlFunction()
  
    //Checks which tiles that currently are being displayed
    tileSource.tileGrid.forEachTileCoord(mapExtent, mapZoom, function(tileCoord) {
  
      //Gets the name of each currently displayed tile
      tileName = tileUrlFunction(tileCoord, ol.proj.get('EPSG:4326'))
  
      //Gets the highest value in each tile by looking in the maxValue-dictionary. If a new highest value is found it is saved in currentMax
      if (maxValue[tileName] !== undefined && maxValue[tileName] > currentMax) {
        currentMax = maxValue[tileName]
      }
  
    })
  
    //Recolors the map based on the highest value found
    olgt_map.plotOptions.domain = [0, currentMax];
    olgt_map.redraw();
    
  
    //Updates the legend
    document.getElementById('MaxValue').innerHTML = currentMax;
    for (i = 0; i < colorScale.percentage_steps.length; i++) {
      document.getElementById('d'+String(i)).title = Math.round(colorScale.percentage_steps[i]*currentMax)
  }

}
