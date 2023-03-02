from datetime import datetime
import datetime as dt
import ee

# User defined settings
start_string = '2022-10-01';
#end_string = '2022-10-21';
end_string = datetime.today().strftime('%Y-%m-%d')
run = '_01'
#run = ''
# define program to run
program = "WB4B22"

# define threshold
thresh_val = 0.25
cloud_free_thresh = 0.5

# define bid and filed id based on program
field_bid_names = {"W21":['Bid_ID','Field_ID', None], 
                   "F21": ['Bid_ID', 'Field_ID', None],
                   "WDW21": ['wn21_ID', 'Field_Name', ['enrolled']],
                   "WDF21": ['wn21_ID', 'Field_Name', ['enrolled']], 
                   "WB4B22": ['BidID', 'FieldID', ['Bid', 'Enrolled'], '1F7lJbzeTH_uNE267xgR_GvsIJ7C72Ppd'],
                   "WDDR22": ['BidID', 'FieldID', ['Bid', 'Enrolled']],
                   "WCWR22": ['Contract_I', 'Field_Name', ['App', 'A[pp', 'Bid'], '1dxz5jL2Pv1Uf7k6wSuqwIsoDpNNZhAAX'],
                   'WSOD22': ['BidID', 'FieldID', ['Enrolled']]
                  }

# google drive document file id
file_id = field_bid_names[program][3]

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



# get the start sunday of the previous week
aday = dt.datetime.now().date() - dt.timedelta(days = 6)
start_last = (aday - dt.timedelta(days=aday.weekday()+1)).strftime('%Y-%m-%d')
end_last = (aday + dt.timedelta(days=5 - aday.weekday())).strftime('%Y-%m-%d')
