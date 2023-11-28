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

    "WB4B22": ['BidID', 'FieldID', ['Bid', 'Enrolled'], 
               'Winter 2022-2023', '2022-10-01', None,
               "projects/codefornature/assets/B4B_fields_Winter2022_20221214"
               '110LWV3EVyZBKYsGOtrSPh-J0i_LaJvN-'],
    "WCWR22": ['Contract_I', 'Field_Name', ['App', 'A[pp', 'Bid'],  
               'Winter 2022-2023', '2022-10-01', None,
               "projects/codefornature/assets/CWRHIP_fields_Winter2022_20221221",
               '1dxz5jL2Pv1Uf7k6wSuqwIsoDpNNZhAAX'],

                  }


# Google Drive authentication and read the Excel file from google drive
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

# define report link and email recipients
url = "https://xinyiwang-jessica.github.io/TNC-BirdSense-Workflows/"
recipients = {

    "WB4B22": ["wangxinyi1986@gmail.com"],
    "WCWR22": ["wangxinyi1986@gmail.com", "cjcarroll@usfca.edu"],

}
email_content = f"""
We've just updated the sample BirdSense dashboard with fresh data on flooded fields. 
Check out the updated dashboard here: {url} \n
What's in the update? \n
\t- Current week's flooded field stats 
\t- Trends over the past month 
\t- A "Watchlist" of the fields that are in the flooding period but have less than 33% flooded 
\t- A flooding time series chart can be filtered by Bid ID
\t- An interactive map of the fields enrolled in the program 
\n
Data Table Included: For those who love the nitty-gritty, we've also attached a data table for the sample program with all the raw data behind the dashboard.
As always, we're all ears for feedback. Hit us up if you've got questions or ideas to make BirdSense even better.\n
\n
"""
  # ,"kklausmeyer@tnc.org", "wangxinyi1986@gmail.com", "wliao14@dons.usfca.edu", "ksesser@calrice.org"
