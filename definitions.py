from datetime import datetime

# User defined settings
end_string = datetime.today().strftime('%Y-%m-%d')
run = '_01'

# define programs to run 
programs = ["BirdReturnsDSODWetlands_Fall2023", "BirdReturnsSVWetlands_Fall2023"]

# define thresholds
thresh_val = 0.20
cloud_free_thresh = 0.5
cloudy = 0.10 # below this cloudy threshold, datapane dashboard won't refelect the corresponding status plot

# define bid and filed id based on program
# program: [BidID, Field_ID, enrolled_status, season, start_date, gdrive_file_id]
# define bid and filed id based on program
"""
The definitions follow the template below:
program: [0.BidID, 1.Field_ID, 2.enrolled_status, 
            3.season, 4.start_date, 5.program_name
            6.field_asset_url, 
            7.gdrive_file_id(optional)]
"""
field_bid_names = {
    "W21":['Bid_ID','Field_ID', None, 
           'Winter 2021-2022', '2021-10-01', None, 
           "users/kklausmeyer/Bid4Birds_Fields_Winter2021_1206", 
           None], 
    "F21": ['Bid_ID', 'Field_ID', None, 
            'Winter 2021-2022', '2021-10-01', None,
            "users/kklausmeyer/B4B_fields_Fall2021", 
            None],
    "WDW21": ['wn21_ID', 'Field_Name', ['enrolled'], 
              'Winter 2021-2022', '2021-10-01', None,
              "users/kklausmeyer/BR_21_WDW", 
              None],
    "WDF21": ['wn21_ID', 'Field_Name', ['enrolled'], 
              'Winter 2021-2022', '2021-10-01', None,
              "users/kklausmeyer/BR_21_WDF_enrolled", 
              None], 
    "WB4B22": ['BidID', 'FieldID', ['Bid', 'Enrolled'], 
               'Winter 2022-2023', '2022-10-01', None,
               "projects/codefornature/assets/B4B_fields_Winter2022_20221214"
               '110LWV3EVyZBKYsGOtrSPh-J0i_LaJvN-'],
    "WDDR22": ['BidID', 'FieldID', ['Bid', 'Enrolled'], 
               'Winter 2022-2023', '2022-10-01', None,
               "projects/codefornature/assets/DDR_fields_Winter2022", 
               None],
    "WCWR22": ['Contract_I', 'Field_Name', ['App', 'A[pp', 'Bid'],  
               'Winter 2022-2023', '2022-10-01', None,
               "projects/codefornature/assets/CWRHIP_fields_Winter2022_20221221",
               '1dxz5jL2Pv1Uf7k6wSuqwIsoDpNNZhAAX'],
    'WSOD22': ['BidID', 'FieldID', ['Enrolled'], 
               'Winter 2022-2023', '2022-10-01', None,
               "projects/codefornature/assets/DSOD_fields_Winter2022",
               None],
    "Bid4Birds": ['BidID', 'FieldID', ['Enrolled'], 
                  'Spring 2023', '2023-02-01', None,
                  "projects/codefornature/assets/Bid4Birds_SV_Ag_Spring_2023_Fields",
                  None],
    "M23": ['BidID', 'FieldID', ['Enrolled'], 
            'Summer 2023', '2023-04-01', "M23",
            "projects/codefornature/assets/B4B_ponds_Summer23_20230525", 
            None],
    "BirdReturnsDSODWetlands_Fall2023": ['BidID', 'FieldID', ['Enrolled'], 
                                         'Fall 2023', '2023-08-10', "BirdReturns DSOD Wetlands (Fall 2023)",
                                         "projects/codefornature/assets/BirdReturnsDSODWetlands_Fall2023Ponds_share",
                                         None],
    "BirdReturnsSVWetlands_Fall2023": ['BidID', 'Pond_Name', ['Enrolled'], 
                                       'Fall 2023', '2023-08-10', "BirdReturns SV Wetlands (Fall 2023)",
                                       "projects/codefornature/assets/BirdReturnsSVWetlands_Fall2023Ponds_share",
                                       None],
                  }


# Google Drive authentication and read the Excel file from google drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

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
