from datetime import datetime
# import datetime as dt
import ee
import os

try:
    GEE_AUTH = os.environ["GEE_AUTH"]
except KeyError:
    GEE_AUTH = "Token not available!"

# GEE authentication
ee_account = 'gee-auth@tnc-birdreturn-test.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(ee_account, key_data=GEE_AUTH)
ee.Initialize(credentials)

# User defined settings


end_string = datetime.today().strftime('%Y-%m-%d')
run = '_01'

# define programs to run 
programs = ["WB4B22", "WCWR22", "Bid4Birds"]

# define thresholds
thresh_val = 0.25
cloud_free_thresh = 0.5
cloudy = 0.10 # below this cloudy threshold, datapane dashboard won't refelect the corresponding status plot

# define bid and filed id based on program
# program: [BidID, Field_ID, enrolled_status, season, start_date, gdrive_file_id]
field_bid_names = {
                    "W21":['Bid_ID','Field_ID', None, 'Winter 2021-2022', '2021-10-01', None], 
                   "F21": ['Bid_ID', 'Field_ID', None, 'Winter 2021-2022', '2021-10-01', None],
                   "WDW21": ['wn21_ID', 'Field_Name', ['enrolled'], 'Winter 2021-2022', '2021-10-01', None],
                   "WDF21": ['wn21_ID', 'Field_Name', ['enrolled'], 'Winter 2021-2022', '2021-10-01', None], 
                   "WB4B22": ['BidID', 'FieldID', ['Bid', 'Enrolled'], 'Winter 2022-2023', '2022-10-01', '110LWV3EVyZBKYsGOtrSPh-J0i_LaJvN-'],
                   "WDDR22": ['BidID', 'FieldID', ['Bid', 'Enrolled'], 'Winter 2022-2023', '2022-10-01', None],
                   "WCWR22": ['Contract_I', 'Field_Name', ['App', 'A[pp', 'Bid'],  'Winter 2022-2023', '2022-10-01', '1dxz5jL2Pv1Uf7k6wSuqwIsoDpNNZhAAX'],
                   'WSOD22': ['BidID', 'FieldID', ['Enrolled'], 'Winter 2022-2023', '2022-10-01', None],
                   "Bid4Birds": ['BidID', 'FieldID', ['Enrolled'], 'Spring 2023', '2023-02-01', None],
                    "M23": ['BidID', 'FieldID', ['Enrolled'], 'Summer 2023', '2023-04-01', None]
                  }

# User defined fields settings
in_fields_W21 = ee.FeatureCollection("users/kklausmeyer/Bid4Birds_Fields_Winter2021_1206")
in_fields_F21 = ee.FeatureCollection("users/kklausmeyer/B4B_fields_Fall2021");
in_fields_WDW21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDW");
in_fields_WDF21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDF_enrolled");
in_fields_WB4B22 = ee.FeatureCollection("projects/codefornature/assets/B4B_fields_Winter2022_20221214");
in_fields_WCWR22 = ee.FeatureCollection("projects/codefornature/assets/CWRHIP_fields_Winter2022_20221221");
in_fields_WSOD22 = ee.FeatureCollection("projects/codefornature/assets/DSOD_fields_Winter2022");
in_fields_WDDR22 = ee.FeatureCollection("projects/codefornature/assets/DDR_fields_Winter2022");
in_fields_Bid4Birds = ee.FeatureCollection("projects/codefornature/assets/Bid4Birds_SV_Ag_Spring_2023_Fields");
in_fields_M23 = ee.FeatureCollection("projects/codefornature/assets/B4B_ponds_Summer23_20230525");

field_list = {
              "W21": in_fields_W21,
              "F21": in_fields_F21,
              "WDW21": in_fields_WDW21,
              "WDF21": in_fields_WDF21,
              "WB4B22": in_fields_WB4B22,
              "WCWR22": in_fields_WCWR22,
              "WSOD22": in_fields_WSOD22,
              "WDDR22": in_fields_WDDR22,
              "Bid4Birds": in_fields_Bid4Birds,
              "M23": in_fields_M23
              }

#Google Drive authentication and read the Excel file from google drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# folium map related definitions
# s2_vis_params = {
#     'bands': ['B4', 'B3', 'B2'],
#     'max': 3133,
#     'min': 405,
#     'gamma': 1,
#     'opacity':0.7
# }

# thresh_vis_params = {
#     'palette' : ['white', 'blue']
# }



recipients = {
    "W21": [],
    "F21": [],
    "WDW21": [],
    "WDF21": [],
    "WB4B22": ["wangxinyi1986@gmail.com"],
    "WCWR22": ["wangxinyi1986@gmail.com", "cjcarroll@usfca.edu"],
    "WSOD22": [],
    "WDDR22": [],
    "Bid4Birds": ["wangxinyi1986@gmail.com"],
    "M23": ["wangxinyi1986@gmail.com"]
}
  # ,"kklausmeyer@tnc.org", "wangxinyi1986@gmail.com", "wliao14@dons.usfca.edu", "ksesser@calrice.org"
