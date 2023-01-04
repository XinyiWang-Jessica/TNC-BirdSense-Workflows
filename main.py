# import logging
# import logging.handlers
import os
from step2 import *

# import requests
import yagmail
import ee
from datetime import datetime
import datapane as dp
import pandas as pd


try:
    GMAIL_PWD = os.environ["GMAIL_PWD"]
except KeyError:
    GMAIL_PWD = "Token not available!"

# try:
#     LARGE_SECRET_PASSPHRASE = os.environ["LARGE_SECRET_PASSPHRASE"]
# except KeyError:
#     LARGE_SECRET_PASSPHRASE = "Token not available!"
    

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
    start = ee.Date(start_string);
    end = ee.Date(end_string);
    # Step 1: Extract images from EE and Filter based on time and geography
    s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterDate(start,end).filterBounds(fields); # update for sentinel changes 1/25/2022 
    s2c = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY').filterDate(start,end).filterBounds(fields)
    
    checks_areaAdded = fields.map(addArea);
    # step 2: add cloudProbability to S2
    withCloudProbability = add_cloudProbability(s2, s2c);
   
    cloud_free_imgColl = withCloudProbability.map(cloud_free_function);
    
    maskClouds = buildMaskFunction(50);
    s2Masked = ee.ImageCollection(cloud_free_imgColl.map(maskClouds)).select(ee.List.sequence(0, 18));
    
    s2Masked_byday = mosaicByDate(s2Masked)
    # mosaic into one image per day - NO MASK (to count total pixels per check)
    s2NoMask_byday = mosaicByDate(cloud_free_imgColl).select(ee.List.sequence(17, 18));
    
     # unique_dates = imlist.map(lambda im: ee.Image(im).date().format("YYYY-MM-dd")).distinct()
    withNDWI = s2Masked_byday.map(addNDWIThresh);
    NDWIThreshonly = withNDWI.select(['NDWI', 'threshold'])

#     bands = NDWIThreshonly.first().bandNames().getInfo()
    rrs = fix(checks_areaAdded)
    reduced_cloudfree = s2NoMask_byday.select(['cloud_free_binary', 'pixel_count']).map(rrs)
    flattened_cloudfree = reduced_cloudfree.flatten()
    with_PctCloudFree = flattened_cloudfree.map(addPctCloudFree);
    
    rrm = fix2(fields)
    reduced = NDWIThreshonly.map(rrm)
    table = reduced.flatten();
    
    # convert featurecollection to dataframe
    columns = [bid_name,field_name,'Status', 'NDWI','threshold','Date'] # export only select fields
    nested_list = table.reduceColumns(ee.Reducer.toList(len(columns)), columns).values().get(0)
    data = nested_list.getInfo()
    df = pd.DataFrame(data, columns=columns)
    
    #upload to datapane
    app = dp.App(dp.DataTable(df))
    app.upload(name="BirdReturn Report " + end_string)
    url = 'https://cloud.datapane.com/apps/E7PnZwA/birdreturn-report ' + end_string
    
   # send email 
    msg = f"I got a number from Earth Engine {url}"  
    yag = yagmail.SMTP("wangxinyi1986@gmail.com",
                   GMAIL_PWD)
    # Adding Content and sending it
    yag.send(["wangxinyi1986@gmail.com"], 
         "Test Github Actions",
         msg)
    
    
if __name__ == "__main__":
    main()
 
