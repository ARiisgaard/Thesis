
// set variables
  const projection = ol.proj.get('EPSG:4326');
  const projectionExtent = [73, 19, 81, 25]; //This is the edges of the testRaster.tiff file - to be replaced with calculating the extent
  const size = ol.extent.getWidth(projectionExtent) / 256;  
  const resolutions = new Array(18);
  const matrixIds = new Array(18);

// create matrix
  for (z = 0; z < 18; ++z) {
    // generate resolutions and matrixIds arrays for this WMTS
    // eslint-disable-next-line no-restricted-properties
    // resolutions[z] = size / Math.pow(2, z);
    resolutions[z] = size / Math.pow(2, z - 0.095); //A dirty fix to the misalignment 
    matrixIds[z] = z;
  }

// define the wms layer
  var wmslayer = new ol.layer.Tile({
    source: new ol.source.WMTS({
      // url: 'http://webportals.ipsl.jussieu.fr/ScientificApps/dev/forge_patrick/eox/tileSet/{TileMatrix}/{TileRow}/{TileCol}.tif',
      url: 'g2tTiles/{TileMatrix}/{TileCol}/{TileRow}.tiff', //I have a folder with the testRaster choped up in 
      projection,
      tileGrid: new ol.tilegrid.WMTS({
        origin: ol.extent.getTopLeft(projectionExtent),
        resolutions,
        matrixIds,
      }),
      requestEncoding: 'REST',
      transition: 0
    }),
    extent: projectionExtent
  });

// define the base layer
 var osm =	new ol.layer.Tile({
      source: new ol.source.OSM(),
      extent: projectionExtent
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
      center: [77.0000000,  22.0000000],
      zoom: 8,
      maxZoom: 10,
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
    });

  });

