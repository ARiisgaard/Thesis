  const projection = ol.proj.get('EPSG:4326');
  
  
  //This is the 
  var tileMetadata = {};
  //This is the folder, where the tiles are extracted from. Locally it can be "g2tTiles" for India or "newTestTiles" for the States
  tileMetadata.tileFolder = 'g2tTiles'

//Making a request for the tileData - see function below
  function loadDoc() {
      var xhttp = new XMLHttpRequest();
      xhttp.open("GET", tileMetadata.tileFolder+"/tilemapresource.xml", false);
      xhttp.send();
      getTileMetadata(xhttp);//(this);
  }


  //When gdal2tiles32.py is run it creates a xml file with metadata. This function extracts the relevant data
  function getTileMetadata(xml)
  {
      var xmlDoc = xml.responseXML;
      var parser = new DOMParser();
      var xmlDoc = parser.parseFromString(xml.responseText, "application/xml");
      
      
      //Getting the resolutions for the tiles. 
      var numberOfZoomLevels = xmlDoc.getElementsByTagName("TileSets")[0].childElementCount;//.childNodes[0]
      tileMetadata.resolutions = [];
      tileMetadata.matrixIds = [];
      for (z = 0; z < numberOfZoomLevels; z++) {
        tileMetadata.resolutions[z] = parseFloat(xmlDoc.getElementsByTagName("TileSets")[0].children[z].attributes["units-per-pixel"].value);
        tileMetadata.matrixIds[z] = parseFloat(xmlDoc.getElementsByTagName("TileSets")[0].children[z].attributes["order"].value);

      }
      
      
      //Getting the coordinates for bounding box, origin and center
      var minx = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.minx.value);
      var maxx = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.maxx.value);
      var miny = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.miny.value);
      var maxy = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.maxy.value);
      tileMetadata.boundingBox = [minx, miny, maxx, maxy]
      tileMetadata.origin = [minx, maxy]
      tileMetadata.center = [(minx+maxx)/2,(miny+maxy)/2]
      
  }
loadDoc();

// 
var tileGrid = new ol.tilegrid.WMTS({
  origin: tileMetadata.origin,
  resolutions: tileMetadata.resolutions,
  matrixIds: tileMetadata.matrixIds,
  tileSize: 256,//[256, 256],
})

var tileSource = new ol.source.WMTS({
  // url: 'http://webportals.ipsl.jussieu.fr/ScientificApps/dev/forge_patrick/eox/tileSet/{TileMatrix}/{TileRow}/{TileCol}.tif',
  url: tileMetadata.tileFolder+'/{TileMatrix}/{TileCol}/{TileRow}.tiff', //I have a folder with the testRaster choped up in 
  projection: projection,
  tileGrid: tileGrid,
  requestEncoding: 'REST',
  transition: 0
})

//Opens the file with the max values for each tile
var maxValue = {};
$.getJSON("maxValues.json", function(json) {
    maxValue = json
});



  var wmslayer = new ol.layer.Tile({
    source: tileSource,
    extent: tileMetadata.boundingBox
  });

// define the base layer
var osmSource = new ol.source.OSM();
 var osm =	new ol.layer.Tile({
      source: osmSource,
      extent: tileMetadata.boundingBox
    });

// define the map
  var map = new ol.Map({
    target: 's2map',
    layers: [
osm,
      wmslayer,
    ],
wrapDateLine: true,
    view: new ol.View({
      projection,
      center: tileMetadata.center,
      zoom: 7,
      maxZoom: 11,
      minZoom: 2
    }),
    controls: ol.control.defaults({
      attributionOptions: {
        collapsible: false
      }
    }),
  });

// olGeoTiff setup
  var olgt_map = new olGeoTiff(wmslayer);
  olgt_map.plotOptions.domain = [0, 2000];
  olgt_map.plotOptions.noDataValue = -9999;
  olgt_map.plotOptions.palette = 'rainbow';

// handle user input
$(window).on('load', function() {
    
  
    var $container = $('#s2map').parent();

    // slider1 (domain)
      var slider = $container.find('.domainslider')[0];

      noUiSlider.create(slider, {
        start: olgt_map.plotOptions.domain,
        connect: true,
        range: { 'min': 0, 'max': 15000 }, // TODO: Calculate these based on the current extent 
        tooltips: true,
      });

      slider.noUiSlider.on('change', function(values) {
        olgt_map.plotOptions.domain = [values[0], values[1]];
        olgt_map.redraw();
      });

    // slider2 (opacity)
      var slider2 = $container.find('.opacityslider')[0];

      var opacity = 0.5;
      noUiSlider.create(slider2, {
        start: opacity,
        connect: true,
        range: { 'min': 0, 'max': 1 },
        tooltips: true,
      });
      wmslayer.setOpacity(opacity);

      slider2.noUiSlider.on('slide', function(values) {
        wmslayer.setOpacity(values[0]*1);
      });

    // palette
      $container.find('.palette').on("change", function() {
        var palette = this.options[this.selectedIndex].text;
        olgt_map.plotOptions.palette = palette;
        olgt_map.redraw();
      });

console.log(maxValue)
map.on("moveend", function() {

        var zoom = map.getView().getZoom(); //originally this was -1??
        var zoomInfo = 'Zoom level = ' + zoom;
        document.getElementById('zoomlevel').innerHTML = zoomInfo;

        var mapExtent = map.getView().calculateExtent(map.getSize())
        var mapZoom = map.getView().getZoom();
        var tileUrlFunction = tileSource.getTileUrlFunction()
        var currentMax = 0;
        tileGrid.forEachTileCoord(mapExtent, mapZoom, function (tileCoord) {
        
          tileName = tileUrlFunction(tileCoord, ol.proj.get('EPSG:4326'))
          
          if (maxValue[tileName] !== undefined && maxValue[tileName] > currentMax){
            currentMax = maxValue[tileName]
          }
          
          // console.log(maxValue[tileName])
          console.log({currentMax})
          // console.log(maxValue[tileName])
          
        
        })
        olgt_map.plotOptions.domain = [0, currentMax];
        olgt_map.redraw();
        
    });

  });

