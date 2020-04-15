  const projection = ol.proj.get('EPSG:4326');
  //This is the 
  var tileMetadata = {};
  //This is the folder, where the tiles are extracted from. Locally it can be "g2tTiles" for India or "newTestTiles" for the States
  tileMetadata.tileFolder = 'g2tTiles'

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
      
      
      
      var minx = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.minx.value);
      var maxx = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.maxx.value);
      var miny = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.miny.value);
      var maxy = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.maxy.value);
      tileMetadata.boundingBox = [minx, miny, maxx, maxy]
      tileMetadata.origin = [minx, maxy]
      tileMetadata.center = [(minx+maxx)/2,(miny+maxy)/2]
      console.log({tileMetadata})    
      
  }
loadDoc();


// // create matrix
//   for (z = 0; z < 18; ++z) {
//     // generate resolutions and matrixIds arrays for this WMTS
//     // eslint-disable-next-line no-restricted-properties
//     // resolutions[z] = size / Math.pow(2, (z + 1));
//     // resolutions[z] = size / Math.pow(2, z);
//     resolutions[z] = size / Math.pow(2, z - 0.17); //A dirty fix to the misalignment 
//     matrixIds[z] = z;
//   }

// define the wms layer


var tileGrid = new ol.tilegrid.WMTS({
  origin: tileMetadata.origin,
  resolutions: tileMetadata.resolutions,
  matrixIds: tileMetadata.matrixIds,
})

var tileSource = new ol.source.WMTS({
  // url: 'http://webportals.ipsl.jussieu.fr/ScientificApps/dev/forge_patrick/eox/tileSet/{TileMatrix}/{TileRow}/{TileCol}.tif',
  // url: 'g2tTiles/{TileMatrix}/{TileCol}/{TileRow}.tiff', //I have a folder with the testRaster choped up in 
  
  url: tileMetadata.tileFolder+'/{TileMatrix}/{TileCol}/{TileRow}.tiff', //I have a folder with the testRaster choped up in 
  projection,
  tileGrid: tileGrid,
  requestEncoding: 'REST',
  transition: 0
})



  var wmslayer = new ol.layer.Tile({
    source: tileSource,
    extent: tileMetadata.boundingBox
  });



// define the base layer
var osmSource = new ol.source.OSM();
 var osm =	new ol.layer.Tile({
      source: osmSource,
      // extent: projectionExtent
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
      zoom: 8,
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
  $(document).ready(function() {
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


map.on("moveend", function() {
        var zoom = map.getView().getZoom(); //originally this was -1??
        var zoomInfo = 'Zoom level = ' + zoom;
        document.getElementById('zoomlevel').innerHTML = zoomInfo;

        mapExtent = map.getView().calculateExtent(map.getSize())
        mapZoom = map.getView().getZoom();
        // var tileUrlFunction = tileSource.getTileUrlFunction()
        // tileGrid.forEachTileCoord(mapExtent, mapZoom, function (tileCoord) {
        // 
        // 
        //   console.log(tileUrlFunction(tileCoord, ol.proj.get('EPSG:4326')));
        // 
        // 
        // })
        
        
    });

  });

