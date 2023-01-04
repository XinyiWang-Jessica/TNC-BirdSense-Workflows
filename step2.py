import ee
import folium

# Import datetime
from datetime import datetime

thresh_val = 0.25

# add area field to fields
def addArea(feature):
    return feature.set({'area_sqm': feature.geometry().area()})

def add_cloudProbability(s2, s2c):
    s2_sysindex_list = s2.aggregate_array('system:index')
    s2c_sysindex_list = s2c.aggregate_array('system:index')
    # create list of system:index values in s2 that are NOT in s2c
    s2_sysindex_list_noMatch = s2_sysindex_list.removeAll(s2c_sysindex_list)
    # filter s2 into two imgColls: 
    s2_sys_ind_match = s2.filter(ee.Filter.inList("system:index", s2c_sysindex_list))
    s2_sys_ind_NoMatch = s2.filter(ee.Filter.inList("system:index", s2_sysindex_list_noMatch))
    # Join the cloud probability collection to the TOA reflectance collection.
    withCloudProbability_yes_s2c = indexJoin(s2_sys_ind_match, s2c, 'cloud_probability')
    # apply constant cloud probability raster = 0
    withCloudProbability_no_s2c = s2_sys_ind_NoMatch.map(addNoCloudProb).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
    # merge two imgColls
    withCloudProbability = withCloudProbability_yes_s2c.merge(withCloudProbability_no_s2c)
    return withCloudProbability
 
    
# ** Cloud masking
# Define a function to join the two collections on their 'system:index'
# property. The 'propName' parameter is the name of the property that
# references the joined image.
def indexJoin(colA, colB, propName):
    primary = colA
    secondary = colB
    condition = ee.Filter.equals(leftField = 'system:index', rightField = 'system:index')
    joined = ee.ImageCollection(ee.Join.saveFirst(propName).apply(primary,secondary,condition))

  # Merge the bands of the joined image.
    return joined.map(lambda image: image.addBands(ee.Image(image.get(propName))))


def buildMaskFunction(cloudProb):
    def applyCloudMask(img):
        # Define clouds as pixels having greater than the given cloud probability.
        cloud = img.select('probability').gt(ee.Image(cloudProb));
        # Apply the cloud mask to the image and return it.
        return img.updateMask(cloud.Not())
    return applyCloudMask

# Define a function to add a cloud probability band with constant raster = 0
# use for sentinel-2 images with no corresponding cloud-probability (s2c) image
def addNoCloudProb (image):
    image = image.addBands(ee.Image(0).rename('probability'))
    return image 

def cloud_free_function(image):
    pixels_cloudFree = image.select('probability').lte(50).rename('cloud_free_binary'); 
    pixels_all = image.select('probability').lte(100).rename('pixel_count'); 
    return image.addBands(pixels_cloudFree).addBands(pixels_all)

def mosaicByDate(imcol):
  # imcol: An image collection
  # returns: An image collection
    imlist = imcol.toList(imcol.size())
    unique_dates = imlist.map(lambda im: ee.Image(im).date().format("YYYY-MM-dd")).distinct()

    def inner_function(d):
        d = ee.Date(d)
        im = imcol.filterDate(d, d.advance(1, "day")).mosaic()
        return im.set(
            "system:time_start", d.millis(), 
            "system:id", d.format("YYYY-MM-dd"))
    mosaic_imlist = unique_dates.map(inner_function)
    
    return ee.ImageCollection(mosaic_imlist)

def addNDWIThresh(image):
    ndwi = image.normalizedDifference(['B8', 'B11']).rename('NDWI')
    thresh = ndwi.gt(thresh_val).rename('threshold')
    return image.addBands([ndwi,thresh])

def fix(area):
    def reduceRegionsSum(image):
        collection=area
        reducer=ee.Reducer.sum()
        scale=10
        sum_cloudfree = image.reduceRegions(collection, reducer, scale)
  # add date field to each feature with image date
        return sum_cloudfree.map(lambda feature: feature.set('Date', image.date().format('YYYY-MM-dd')))
    return reduceRegionsSum

def addPctCloudFree(feature):
    return feature.set({'Pct_CloudFree': ee.Number(feature.get('cloud_free_binary')).divide(ee.Number(feature.get('pixel_count')))})

# Sumarize the mean value of the NDWI value, the threshold layer (i.e. the % of the polygon that is above the threshold )
# reduce regions MEAN
def fix2(fields):
    def reduceRegionsMean(image):
        collection=fields
        reducer=ee.Reducer.mean()
        scale=30
        mean_NDWI_threshold = image.reduceRegions(collection, reducer, scale)
  # add date field to each feature with image date # set geometry to null
        return mean_NDWI_threshold.map(lambda feature: feature.set('Date', image.date().format('YYYY-MM-dd')).setGeometry(None))
    return reduceRegionsMean


# Define a method for displaying Earth Engine image tiles on a folium map.
def add_ee_layer(self, ee_object, vis_params, name):
    
    try:    
        # display ee.Image()
        if isinstance(ee_object, ee.image.Image):    
            map_id_dict = ee.Image(ee_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = name,
            overlay = True,
            control = True
            ).add_to(self)
        # display ee.ImageCollection()
        elif isinstance(ee_object, ee.imagecollection.ImageCollection):    
            ee_object_new = ee_object.mosaic()
            map_id_dict = ee.Image(ee_object_new).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = name,
            overlay = True,
            control = True
            ).add_to(self)
        # display ee.Geometry()
        elif isinstance(ee_object, ee.geometry.Geometry):    
            folium.GeoJson(
            data = ee_object.getInfo(),
            name = name,
            overlay = True,
            control = True
        ).add_to(self)
        # display ee.FeatureCollection()
        elif isinstance(ee_object, ee.featurecollection.FeatureCollection):  
            ee_object_new = ee.Image().paint(ee_object, 0, 2)
            map_id_dict = ee.Image(ee_object_new).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = name,
            overlay = True,
            control = True
        ).add_to(self)
    
    except:
        print("Could not display {}".format(name))

