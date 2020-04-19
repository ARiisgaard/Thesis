//Making a request for the tileData - see function getTileMetadata
function getTileMetadata(objectWithMetadata) {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", objectWithMetadata.tileFolder + "/tilemapresource.xml", false);
  xhttp.send();
  processTileMetadata(xhttp, objectWithMetadata);
}

//When gdal2tiles32.py is run it creates a xml file with metadata. This function extracts the relevant data
function processTileMetadata(xml, objectWithMetadata) {
  var xmlDoc = xml.responseXML;
  var parser = new DOMParser();
  var xmlDoc = parser.parseFromString(xml.responseText, "application/xml");

  //Getting the resolutions for the tiles - this is done for each zoom level.
  var numberOfZoomLevels = xmlDoc.getElementsByTagName("TileSets")[0].childElementCount;
  objectWithMetadata.resolutions = [];
  objectWithMetadata.matrixIds = [];
  for (z = 0; z < numberOfZoomLevels; z++) {
    objectWithMetadata.resolutions[z] = parseFloat(xmlDoc.getElementsByTagName("TileSets")[0].children[z].attributes["units-per-pixel"].value);
    objectWithMetadata.matrixIds[z] = parseFloat(xmlDoc.getElementsByTagName("TileSets")[0].children[z].attributes["order"].value);

  }

  //Getting the coordinates for bounding box, origin and center
  var minx = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.minx.value);
  var maxx = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.maxx.value);
  var miny = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.miny.value);
  var maxy = parseFloat(xmlDoc.getElementsByTagName("BoundingBox")[0].attributes.maxy.value);
  objectWithMetadata.boundingBox = [minx, miny, maxx, maxy]
  objectWithMetadata.origin = [minx, maxy]
  objectWithMetadata.center = [
    (minx + maxx) / 2,
    (miny + maxy) / 2
  ]

}