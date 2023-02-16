# import logging
# import logging.handlers
import os
import io
import json
from step2 import *
from step3 import *
from definitions import *

# packages for google access
from google.oauth2 import service_account
from googleapiclient.discovery import build

# import requests
import yagmail
import ee
import folium
from datetime import datetime
import datapane as dp
import pandas as pd

# extract token from environment
try:
    GMAIL_PWD = os.environ["GMAIL_PWD"]
except KeyError:
    GMAIL_PWD = "Token not available!"

try:
    GEE_AUTH = os.environ["GEE_AUTH"]
except KeyError:
    GEE_AUTH = "Token not available!"

try:
    GDRIVE_AUTH = os.environ["GDRIVE_AUTH"]
except KeyError:
    GDRIVE_AUTH = "Token not available!"

# GEE authentication
ee_account = 'gee-auth@tnc-birdreturn-test.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(ee_account, key_data=GEE_AUTH)
ee.Initialize(credentials)

# Google Drive authentication and read the Excel file from google drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
gdrive_auth = json.loads(GDRIVE_AUTH)
creds = service_account.Credentials.from_service_account_info(
    gdrive_auth, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)
request = service.files().get_media(fileId=file_id)
file = io.BytesIO(request.execute())

# User defined settings
in_fields_W21 = ee.FeatureCollection(
    "users/kklausmeyer/Bid4Birds_Fields_Winter2021_1206")
in_fields_F21 = ee.FeatureCollection("users/kklausmeyer/B4B_fields_Fall2021")
in_fields_WDW21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDW")
in_fields_WDF21 = ee.FeatureCollection("users/kklausmeyer/BR_21_WDF_enrolled")
in_fields_WB4B22 = ee.FeatureCollection(
    "projects/codefornature/assets/B4B_fields_Winter2022")
in_fields_WCWR22 = ee.FeatureCollection(
    "projects/codefornature/assets/CWRHIP_fields_Winter2022")
in_fields_WSOD22 = ee.FeatureCollection(
    "projects/codefornature/assets/DSOD_fields_Winter2022")
in_fields_WDDR22 = ee.FeatureCollection(
    "projects/codefornature/assets/DDR_fields_Winter2022")

bid_name = field_bid_names[program][0]
field_name = field_bid_names[program][1]
stat_list = field_bid_names[program][2]
field_list = {"W21": in_fields_W21,
              "F21": in_fields_F21,
              "WDW21": in_fields_WDW21,
              "WDF21": in_fields_WDF21,
              "WB4B22": in_fields_WB4B22,
              "WCWR22": in_fields_WCWR22}
fields = field_list[program]

columns1 = [bid_name, field_name, 'Status', 'Pct_CloudFree', 'Date']
columns2 = [bid_name, field_name, 'NDWI', 'threshold', 'Date']

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
    # s2 = ee.ImageCollection('COPERNICUS/S2');
    start = ee.Date(start_string)
    end = ee.Date(end_string)
    # Step 1: Extract images from EE and Filter based on time and geography
    s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterDate(start,
                                                                   end).filterBounds(fields)  # update for sentinel changes 1/25/2022
    s2c = ee.ImageCollection(
        'COPERNICUS/S2_CLOUD_PROBABILITY').filterDate(start, end).filterBounds(fields)

    checks_areaAdded = fields.map(addArea)
    # step 2: add cloudProbability to S2
    withCloudProbability = add_cloudProbability(s2, s2c)

    cloud_free_imgColl = withCloudProbability.map(cloud_free_function)

    maskClouds = buildMaskFunction(50)
    s2Masked = ee.ImageCollection(cloud_free_imgColl.map(
        maskClouds)).select(ee.List.sequence(0, 18))

    s2Masked_byday = mosaicByDate(s2Masked)
    # mosaic into one image per day - NO MASK (to count total pixels per check)
    s2NoMask_byday = mosaicByDate(
        cloud_free_imgColl).select(ee.List.sequence(17, 18))

    # unique_dates = imlist.map(lambda im: ee.Image(im).date().format("YYYY-MM-dd")).distinct()
    withNDWI = s2Masked_byday.map(addNDWIThresh)
    NDWIThreshonly = withNDWI.select(['NDWI', 'threshold'])

#     bands = NDWIThreshonly.first().bandNames().getInfo()
    rrs = fix(checks_areaAdded)
    reduced_cloudfree = s2NoMask_byday.select(
        ['cloud_free_binary', 'pixel_count']).map(rrs)
    flattened_cloudfree = reduced_cloudfree.flatten()
    with_PctCloudFree = flattened_cloudfree.map(addPctCloudFree)

    rrm = fix2(fields)
    reduced = NDWIThreshonly.map(rrm)
    table = reduced.flatten()

    # convert featurecollections to dataframe, combine and formatted as we need
    df = table_combine(with_PctCloudFree, table, columns1, columns2)
    # calculate the cloud free datepoints
    num, percent, percent2, mask, mask2 = cloud_free_percent(df, start_last)
    # create pivoted table and watch list
    try:
        df_d = pd.read_excel(file)
        col = 5
        df_pivot = add_flood_dates(df_d, pivot_table(df), stat_list)
        # generate the watch list with low percentage flooded rate
        watch = watch_list(df_pivot, start_last)
    except FileNotFoundError:
        df_pivot = no_flood_dates(pivot_table(df))
        col = 3
        watch = pd.DataFrame()

    # add plots
    fig_history = history_plot(df_pivot, start_last)
    fig_status = plot_status(df_pivot, start_last)
    heatmaps, cut_bins = all_heatmaps(df_pivot, col, start_last)

    thresh_mean = NDWIThreshonly.select("threshold").mean()

    # Add EE drawing method to folium.
    folium.Map.add_ee_layer = add_ee_layer
    # Create a folium map object.
    my_map = folium.Map(location=[39.141, -121.63],
                        zoom_start=7, height=500, width=800)

    # Add layers to the map object.
    my_map.add_ee_layer(NDWIThreshonly.select(
        "threshold").mean(), thresh_vis_params, 'average flood frequency')
    # my_map.add_ee_layer(s2NoMask_byday.filterMetadata('system:time_start','equals',1612310400000).select('cloud_free_binary'),{'min':0,'max':1,'palette':['white','green']},'temp')
    my_map.add_ee_layer(NDWIThreshonly.select("threshold").filterDate(
        ee.Date(start_string), ee.Date(end_string)), thresh_vis_params, 'threshold')

    # Display ee.FeatureCollection
    my_map.add_ee_layer(fields, {}, 'fields')

    # Add a layer control panel to the map.
    my_map.add_child(folium.LayerControl())

    # upload to datapane
    start_last_text = datetime.strptime(start_last, '%Y-%m-%d').strftime("%b %d, %Y")
    end_last_text = datetime.strptime(end_last, '%Y-%m-%d').strftime("%b %d, %Y")
    app = dp.App(
        # need to format to the date... and add end date
        dp.Text(f'# Weekly Report - {start_last_text} to {end_last_text} #'),
        dp.Text(f'last update: {end_string}'),
        dp.Group(
            dp.BigNumber(heading='Total Fields', value=num),
            dp.BigNumber(heading='Field with cloud-free data this week',
                         value="{:.2%}".format(percent),
                         change="{:.2%}".format(percent - percent2),
                         is_upward_change=True), columns=2),  # check the upward = false
        dp.Text('## Flooding Status ##'),
        dp.Group(
            dp.Plot(
                # caption="Flooding Status This Week (Cloud-Free Fields Only) ",
                fig_status,
                # Lots of white space here, so we can use a smaller height
                responsive=True
            ),
            dp.Plot(
                fig_history, caption="Flooding Status for Last 8 Weeks (Cloud-Free Fields Only)",
                responsive=True),
            columns=2),
        dp.Text(f'## Watch List for the Week Starting from {start_last_text} ##'),
        dp.Table(watch.style.background_gradient(cmap="autumn")),
        dp.Text('## Flooding Percentage by Fields ##'),
        dp.Select(
            blocks=[
                dp.Plot(heatmaps[i], label=f'Bids {int(cut_bins[i])} ~ {int(cut_bins[i+1])}') for i in range(len(heatmaps))] +
            [dp.DataTable(df_pivot.round(3), label="Data Table")],
            type=dp.SelectType.TABS),
        dp.Text('## Flooding Status on Map ##'),
        dp.Plot(my_map, caption="Flooded Area on Map")
    )
    app.upload(name="BirdSense: Drought Relief WaterBird Program, Winter 2022-2023",
               publicly_visible=True)
    url = app.web_url

   # send email
    msg = f"Please check the latest BirdSense report {url}"
    yag = yagmail.SMTP("wangxinyi1986@gmail.com",
                       GMAIL_PWD)
    # Adding Content and sending it

    yag.send(["wliao14@dons.usfca.edu", "wangxinyi1986@gmail.com","kklausmeyer@tnc.org"],  # ,"kklausmeyer@tnc.org", "wangxinyi1986@gmail.com", "wliao14@dons.usfca.edu"
             "Weekly BirdSense Report - Testing",
             msg)


if __name__ == "__main__":
    main()
