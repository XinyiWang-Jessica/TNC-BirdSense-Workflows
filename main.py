# import logging
# import logging.handlers
import os
from step2 import *

# import requests
import yagmail
import ee
from datetime import datetime

try:
    GMAIL_PWD = os.environ["GMAIL_PWD"]
except KeyError:
    GMAIL_PWD = "Token not available!"

try:
    GEE_AUTH = os.environ["GEE_AUTH"]
except KeyError:
    GEE_AUTH = "Token not available!"
    

service_account = 'gee-auth@tnc-birdreturn-test.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'tnc-birdreturn-test-c95e19825893.json')
ee.Initialize(credentials)

# User defined settings
start_string = '2022-10-01';
#end_string = '2022-10-21';
end_string = datetime.today().strftime('%Y-%m-%d')
run = '_01'
#run = ''
program = "WB4B22"
thresh_val = 0.25

in_fields_W21 = ee.FeatureCollection("users/kklausmeyer/Bid4Birds_Fields_Winter2021_1206")
in_fields_F21 = ee.FeatureCollection("users/kklausmeyer/B4B_fields_Fall2021");
in_fields_WDW21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDW");
in_fields_WDF21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDF_enrolled");
in_fields_WB4B22 = ee.FeatureCollection("projects/codefornature/assets/B4B_fields_Winter2022");
in_fields_WCWR22 = ee.FeatureCollection("projects/codefornature/assets/CWRHIP_fields_Winter2022");

if program == "W21":
    fields = in_fields_W21
    bid_name = 'Bid_ID'
    field_name = 'Field_ID'
elif program == "F21":
  fields = in_fields_F21
  bid_name = 'Bid_ID'
  field_name = 'Field_ID'
elif program == "WDW21":
  fields = in_fields_WDW21
  bid_name = 'wn21_ID'
  field_name = 'Field_Name'
elif program == "WDF21":
  fields = in_fields_WDF21
  bid_name = 'wn21_ID'
  field_name = 'Field_Name'
elif program == "WB4B22":
  fields = in_fields_WB4B22
  bid_name = 'BidID'
  field_name = 'FieldID'
elif program == "WCWR22":
  fields = in_fields_WCWR22
  bid_name = 'Contract_I'
  field_name = 'Field_Name'


# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# logger_file_handler = logging.handlers.RotatingFileHandler(
#     "status.log",
#     maxBytes=1024 * 1024,
#     backupCount=1,
#     encoding="utf8",
# )
# formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# logger_file_handler.setFormatter(formatter)
# logger.addHandler(logger_file_handler)

# try:
#     SOME_SECRET = os.environ["SOME_SECRET"]
# except KeyError:
#     SOME_SECRET = "Token not available!"
    

    
def main():
    # s2 = ee.ImageCollection('COPERNICUS/S2');
    s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED'); # update for sentinel changes 1/25/2022 
    s2c = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
    
    checks_areaAdded = fields.map(addArea);

    start = ee.Date(start_string);
    end = ee.Date(end_string);

    # Filter based on time and geography
    s2 = s2.filterDate(start,end).filterBounds(fields);
    s2c = s2c.filterDate(start,end).filterBounds(fields);
   
    # create list of system:index values in s2 and s2c
    s2_sysindex_list = s2.aggregate_array('system:index')
    s2c_sysindex_list = s2c.aggregate_array('system:index')

    # create list of system:index values in s2 that are NOT in s2c
    s2_sysindex_list_noMatch = s2_sysindex_list.removeAll(s2c_sysindex_list)
    #print(s2_sysindex_list_noMatch.getInfo())

    # filter s2 into two imgColls: 
    s2_sys_ind_match = s2.filter(ee.Filter.inList("system:index", s2c_sysindex_list))
    s2_sys_ind_NoMatch = s2.filter(ee.Filter.inList("system:index", s2_sysindex_list_noMatch))
    
    # for s2 images that have matching system:index values in s2c
    # Join the cloud probability collection to the TOA reflectance collection.
    withCloudProbability_yes_s2c = indexJoin(s2_sys_ind_match, s2c, 'cloud_probability')

    # for s2 image that do NOT have matching system:index values in s2c
    # apply constant cloud probability raster = 0
    withCloudProbability_no_s2c  = s2_sys_ind_NoMatch.map(addNoCloudProb).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
    withCloudProbability = withCloudProbability_yes_s2c.merge(withCloudProbability_no_s2c)
    
    cloud_free_imgColl = withCloudProbability.map(cloud_free_function);
    
    maskClouds = buildMaskFunction(50);
    s2Masked = ee.ImageCollection(cloud_free_imgColl.map(maskClouds)).select(ee.List.sequence(0, 18));
    
    s2Masked_byday = mosaicByDate(s2Masked)
    # mosaic into one image per day - NO MASK (to count total pixels per check)
    s2NoMask_byday = mosaicByDate(cloud_free_imgColl).select(ee.List.sequence(17, 18));
    
     # unique_dates = imlist.map(lambda im: ee.Image(im).date().format("YYYY-MM-dd")).distinct()
    withNDWI = s2Masked_byday.map(addNDWIThresh);
    NDWIThreshonly = withNDWI.select(['NDWI', 'threshold'])
    bands = NDWIThreshonly.first().bandNames().getInfo()
    # reduced_cloudfree = s2NoMask_byday.select(['cloud_free_binary', 'pixel_count']).map(reduceRegionsSum)

#     flattened_cloudfree = reduced_cloudfree.flatten()
    
#     with_PctCloudFree = flattened_cloudfree.map(addPctCloudFree);

    msg = f"I got a number from Earth Engine {bands}"  
    yag = yagmail.SMTP("wangxinyi1986@gmail.com",
                   GMAIL_PWD)
    # Adding Content and sending it
    yag.send(["wangxinyi1986@gmail.com"], 
         "Test Github Actions",
         msg)
    

    
    
if __name__ == "__main__":
    main()
 
        
