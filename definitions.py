from datetime import datetime
import ee

# User defined settings
start_string = '2022-10-01';
#end_string = '2022-10-21';
end_string = datetime.today().strftime('%Y-%m-%d')
run = '_01'
#run = ''
program = "WB4B22"
thresh_val = 0.25
cloud_free_thresh = 0.5

field_bid_names = {"W21":['Bid_ID','Field_ID', None], 
                   "F21": ['Bid_ID', 'Field_ID', None],
                   "WDW21": ['wn21_ID', 'Field_Name', ['enrolled']],
                   "WDF21": ['wn21_ID', 'Field_Name', ['enrolled']], 
                   "WB4B22": ['BidID', 'FieldID', ['Bid', 'Enrolled']],
                   "WDDR22": ['BidID', 'FieldID', ['Bid', 'Enrolled']],
                   "WCWR22": ['Contract_I', 'Field_Name', ['App', 'A[pp', 'Bid']],
                   'WSOD22': ['BidID', 'FieldID', ['Enrolled']]
                  }

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
