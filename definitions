# User defined settings
start_string = '2022-10-01';
#end_string = '2022-10-21';
end_string = datetime.today().strftime('%Y-%m-%d')
run = '_01'
#run = ''
program = "WB4B22"
thresh_val = 0.25
cloud_free_thresh = 0.5


in_fields_W21 = ee.FeatureCollection("users/kklausmeyer/Bid4Birds_Fields_Winter2021_1206")
in_fields_F21 = ee.FeatureCollection("users/kklausmeyer/B4B_fields_Fall2021");
in_fields_WDW21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDW");
in_fields_WDF21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDF_enrolled");
in_fields_WB4B22 = ee.FeatureCollection("projects/codefornature/assets/B4B_fields_Winter2022");
in_fields_WCWR22 = ee.FeatureCollection("projects/codefornature/assets/CWRHIP_fields_Winter2022");
in_fields_WSOD22 = ee.FeatureCollection("projects/codefornature/assets/DSOD_fields_Winter2022");
in_fields_WDDR22 = ee.FeatureCollection("projects/codefornature/assets/DDR_fields_Winter2022");

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
elif program == "WSOD22":
  fields = in_fields_WSOD22
  bid_name = 'BidID'
  field_name = 'FieldID'
elif program == "WDDR22":
  fields = in_fields_WDDR22
  bid_name = 'BidID'
  field_name = 'FieldID'

s2_vis_params = {
    'bands': ['B4', 'B3', 'B2'],
    'max': 3133,
    'min': 405,
    'gamma': 1,
    'opacity':0.7
}

thresh_vis_params = {
    'palette' : ['white', 'blue']
}

columns1 = [bid_name,field_name, 'Status','Pct_CloudFree','Date']
columns2 = [bid_name,field_name, 'NDWI','threshold','Date']
