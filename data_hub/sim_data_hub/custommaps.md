# How to create an offline map from an image?
## You need to have:
 * a scanned map either in JPG, PNG or a TIFF file
 * Quantum GIS (convert the image to a geo-referenced image)
 * GDAL (If your image is not projected in Web Mercator, it will help you getting the right projection before importing it into TileMill)
 * TileMill (convert GeoTiff to .mbtiles)
 * Mbutil (convert .mbtiles to PNG or JPG, since in our projection it is currently not possible to use .mbtiles offline)

## 1. Quantum GIS
You can reference to: https://tilemill-project.github.io/tilemill/docs/guides/georeferencing-satellite-images/
 * Open QGIS and add your image into the Georeferencer plugin,
 * Set the spatial reference in ‘Coordinate Reference System Selector’. The type of Geographic Coordinate System depends on your image.
 * Select georeferencing points (Add points to your image and enter longitude and latitude of that location).
 * Run it when everything is ready.

## 2. GDAL
Simply use the following gdalwarp command and run it (However, you can change it accordingly and you can find the explanation for each piece of the command here: https://tilemill-project.github.io/tilemill/docs/guides/reprojecting-geotiff/ ):

```
gdalwarp -s_srs EPSG:4326 -t_srs EPSG:3857 -r bilinear \
    -te -20037508.34 -20037508.34 20037508.34 20037508.34 \
    NE2_LR_LC_SR_W.tif natural-earth-2-mercator.tif
```

## 3. TileMill

Create a new project and select 900913 as the SRS projection. Load your GeoTill to TileMill. Please follow the steps in here: https://tilemill-project.github.io/tilemill/docs/guides/reprojecting-geotiff/

## 4. Mbutil

The Mbtiles file you have generated has all our imagery packed into it, now we need to convert them into PNG or JPG. To do so, using the following command:

```
mb-util –image_format=png YourMap.mbtiles New_Folder_Name
```

## 5. Move tiles
Move the created tiles to `ice-data-hub/gui/assets/data/tiles/(Planet)`, where `(Planet)` might be Enceladus, Europa, Ganymede or Mars.