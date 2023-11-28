# import logging
# import logging.handlers
import os
import ee
# import folium
import datapane as dp

# import supporting functions from step2 and step 3
from scripts.step2 import *
from scripts.step3 import *
from scripts.definitions import *

# Obtain GEE token from environment
try:
    GEE_AUTH = os.environ["GEE_AUTH"]
except KeyError:
    GEE_AUTH = "Token not available!"

# GEE authentication
ee_account = 'gee-auth@tnc-birdreturn-test.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(ee_account, key_data=GEE_AUTH)
ee.Initialize(credentials)  

# uncomment the following section to start logging every run
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

def main():
    '''
    For each selected program, 
        - estimate daily flood coverage
        - converted the daily flood coverage to weekly 
        - plot flooding status and create a report for each program
        - combine all the reports
    '''
    
    pages = []
    for program in programs:
        print('run for program: ', program)
        # record the running program (optional)
        # logger.info(f'Run for program: {program}')
    
        # Step 1: Obtain program specific information from definitions
        start_string = field_bid_names[program][4]
        stat_list = field_bid_names[program][2]
        fields_url = field_bid_names[program][6]
        fields = ee.FeatureCollection(fields_url)
        # aday = dt.datetime.now().date() - dt.timedelta(days = 6)
        # start_last_week = (aday - dt.timedelta(days=aday.weekday()+1)).strftime('%Y-%m-%d')
        # end_last = (aday + dt.timedelta(days=5 - aday.weekday())).strftime('%Y-%m-%d')
        
        # Step 2: Generate daily and weekly flooding percentage estimate
        df_daily = daily_percentage_table(program, fields, start_string, end_string, stat_list)
        df_pivot_weekly, watch_list, col = weekly_percentage_table(df_daily, program, fields, stat_list)

        # save the weekly percentage estimate as csv file
        df_pivot_weekly.to_csv('weekly_data/' +program+'_weekly_flood_status.csv')

        # Step 3: Converted to weekly pivoted table
        page = create_report(df_daily, df_pivot_weekly, watch_list, program, fields, start_string, col)
        pages.append(page)

    # Step 4: combine the pages for all the programs and generate one HTML report    
    report = dp.Blocks(
        blocks = [
            pages[i] for i in range(len(pages))
            ]
                      )
    dp.save_report(report, 'index.html')

if __name__ == "__main__":
    main()
