# TNC BirdSense Report Automation Workflows
Short description of BirdReturn
For more readings, refer to [BirdReturns: A Habitat Timeshare for Migratory Birds](https://www.nature.org/en-us/about-us/where-we-work/united-states/california/stories-in-california/migration-moneyball/)
The project analyze data from satellite imagery and on-the-ground observations to determine the flooding status of hatbitats of contracted farm lands.
This repository is part of the BirdReturn project to provide.....
## Features:
- Extract Sentinel 2 data from Google Earth Engine API
- Process data to obtain the percent of flooding and cloud-free indicator by fields
- Extract data from Google Drive API
- Generate a dashboard report through DataPane APP (example screenshot)
- Schedule workflow and report sharing by email

## Preparation
### GEE Authentication with Google Service Account
To access data from GEE API, Google Searvice Account is used to authenticate to Earth Engine. To do so, follow the [guide of create service account](https://developers.google.com/earth-engine/guides/service_account) and complete the steps below:
  1. Create a Google Cloud Project
  2. Choose the created project and create a Service Account
  3. Create a private key for the Service Account and download the Json key file
  4. Register your service account for use with the Earth Engine API.
  5. Save the jason key content as a repo secrete with the Name of GEE_AUTH under the repo Settings
### Google Drive API Authentication
To download files stored in Google Drive, Google Drive Python API is used. The [Google Python Quickstart](https://developers.google.com/drive/api/quickstart/python) provides guidelines to enable the enable the API and set up the Authorize credentials. The following steps describe how to set up Google Drive API and access an Excel file in google drive:
  1. Create a Google Service Account and create a Key. Download the Json key file and copy the service account email. 
  2. Enable Google Drive API for the Google Cloud Project set up from the previous step. 
  3. Grant the the Google Drive folder/file access to the Service Account just set up using the Service Account email.
  4. Copy the Google Drive folder/file id from the url. 
  5. Save the jason key content as a repo secrete with the Name of GDRIVE_AUTH under the repo Settings.
  6. Configure authorize credentials in main.py. Instead of the Google Python Quick start, the [Ben James blog](https://blog.benjames.io/2020/09/13/authorise-your-python-google-drive-api-the-easy-way/) provides an instruction to set up Json toke as an environment variable(repo secrete).
### DataPane Authentication
To generate a dashboard report on [DataPane](https://datapane.com/), an API token is required for access. Follow the [instrution](https://docs.datapane.com/tutorials/automation/#introduction) and complete the following steps:
  1. Create a DataPane account and login
  2. Go to the setting page and copy the API Token
  3. Add the API token as a repo secrete with the Name of DATAPANE_TOKEN 
### Gmail Authentication
Yet Another Gmail [yagmail](https://yagmail.readthedocs.io/en/latest/) is applied to send emails automaticlly. It requires sign-in process to authorize. Follow the instruction to obtain the [Gmail App password](https://support.google.com/mail/answer/185833?hl=en). Then, add the password to the repo secrete with the name of GMAIL_PWD.
### GitHub Repository Secret Set Up
GitHub Repository secrets allows to save passwords, API tokens and other sensitive information. The secrets created are available for GitHub Actions workflows. Follow the [instrution to create and use prepository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) and complete the steps below:
  1. Go to repository Settings and create required secrets in the Security section
  2. Using secrets in workflow .yml file

## How to Use
### Set up a schedule to run repo action
GitHub repository can run script on a fixed schecule, such as daily, weekly, or a certain day of week/month. The scheduling is done by POSIX cron syntax. For more information, refer to the [GitHub Workflow Trigger Events - Schedule](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows).
You can use use [crontab guru](https://crontab.guru) to help generate your cron syntax.
### Define fields (Kirk to add)
### Modify user definitions
The following fileds need be defined:
- Date Range (start and end dates for data extraction): start_string and end_string 
- (Optional) Google Drive folder/file id
- cloud free threshold: cloud_free_thresh
- NDWI Threshold (to add binary layer based on threshold): thresh_val
- 
### Formate Dashboard
For this workflow, DataPane is used to generate a report dashboard. DataPane allows to transform Jupyter Notebook or Python script to a interactive web app. It friendly with Pandas DataFrame, Matplotlib/Seaborn, Plotly and Folim for map visulization. 
Refer to the [DataPane documentation](https://docs.datapane.com/) for page, numbers, table, plot and map formating
### Modifile email message, sender and recieptants
Refer to the example of [yagmail](https://pypi.org/project/yagmail/) to format your email contents.

## Acknowledgement:

