# TNC BirdSense Report Automation Workflows
Every year, over 1 billion birds migrate along the Pacific Flyway and travel through California. Many of these birds need wetlands for food and rest to support their journey, but over 95% of the historical wetlands in the Central Valley have been drained and developed. The Nature Conservancy and partners recently launched a program called BirdReturns to pay farmers to flood their fields to support migratory wetland birds.   
For more information, refer to [BirdReturns: A Habitat Timeshare for Migratory Birds](https://www.nature.org/en-us/about-us/where-we-work/united-states/california/stories-in-california/migration-moneyball/).  

As the program scales up with government funds to combat the impacts of the drought, new tools are needed to ensure that farmers flood their fields for the full duration of their contract. The current program has been experimenting with using free images captured by satellites to estimate the extent and duration of flooding on the enrolled fields.   
Based on the promising experiment outcomes, this GitHub Repository is aimed to build a data pipeline to 1) ingest the satellite data, 2) generate flooding extent estimates, and 3) automatically send weekly reports to the field staff who manage the program.  

This repo utilizes the GitHub Action workflow to build a data pipeline and realize the following features.
## Features:
- Extract Sentinel 2 data from Google Earth Engine API
- Process data to obtain the percent of flooding and cloud-free indicator by fields
- Extract data from Google Drive API
- Generate a dashboard report through DataPane APP 
- Schedule workflows for multiple programs
- Share dashboard report by email
- Log workflow actions in status.log

## DataPane Example

![](./img1.png?raw=true )
![](./img2.png?raw=true )
![DataPane Ex](./img3.png?raw=true "Interactive DataPane")

## Preparation
The following authentications need to be set up and added to repository Secrets.
### GEE Authentication with Google Service Account
To access data from GEE API, Google Service Account is used to authenticate to Earth Engine. To do so, follow the [guide to create a service account](https://developers.google.com/earth-engine/guides/service_account) and complete the steps below:
  1. Create a Google Cloud Project
  2. Choose the created project and create a Service Account
  3. Create a private key for the Service Account and download the JSON key file
  4. Register your service account for use with the Earth Engine API.
  5. Save the JSON key content as a repo secret with the Name of GEE_AUTH under the repo Settings
  6. Configure authorizing credentials in definitions.py
  
### Google Drive API Authentication
To download files stored in Google Drive, Google Drive Python API is used. The [Google Python Quickstart](https://developers.google.com/drive/api/quickstart/python) provides guidelines to enable the API and set up the Authorize credentials. The following steps describe how to set up Google Drive API and access an Excel file in google drive:
  1. Create a Google Service Account and create a Key. Download the JSON key file and copy the service account email. 
  2. Enable Google Drive API for the Google Cloud Project set up from the previous step. 
  3. Grant the Google Drive folder/file access to the Service Account just setup using the Service Account email.
  4. Copy the Google Drive folder/file id from the url. 
  5. Save the JSON key content as a repo secret with the Name of GDRIVE_AUTH under the repo Settings.
  6. Configure authorizing credentials in main.py. Instead of the Google Python Quick start, [Ben James' blog](https://blog.benjames.io/2020/09/13/authorise-your-python-google-drive-api-the-easy-way/) provides an instruction to set up JSON token as an environment variable (repo secret).
  
### DataPane Authentication
To generate a dashboard report on [DataPane](https://datapane.com/), an API token is required for access. Follow the [instructions](https://docs.datapane.com/tutorials/automation/#introduction) and complete the following steps:
  1. Create a DataPane account and login
  2. Go to the setting page and copy the API Token
  3. Add the API token as a repo secret with the Name of DATAPANE_TOKEN 
  
### Gmail Authentication
Yet Another Gmail [yagmail](https://yagmail.readthedocs.io/en/latest/) is applied to send emails automatically. It requires sign-in process to authorize. Follow the instruction to obtain the [Gmail App password](https://support.google.com/mail/answer/185833?hl=en). Then, add the password to the repo secret with the name of GMAIL_PWD.

### GitHub Repository Secret Set Up
GitHub Repository secrets allow saving passwords, API tokens, and other sensitive information. The secrets created are available for GitHub Actions workflows. Follow the [instrution to create and use prepository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) and complete the steps below:
  1. Go to repository Settings and create required secrets in the Security section
  2. Using secrets in the workflow .yml file

## How to Use
There is no need for environment setup. GitHub Action will install all the packages as required. Any additional packages and versions need to be added to the requirements.txt.

### Set up a schedule to run repo action
GitHub repository can run the script on a fixed schedule, such as daily, weekly, or a specific day of the week/month. The scheduling is done by POSIX cron syntax. For more information, refer to the [GitHub Workflow Trigger Events - Schedule](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows).
Use [crontab guru](https://crontab.guru) to help generate your cron syntax.

### Define fields (Kirk to add)


### Modify user definitions
The following fileds need be defined:
- Date Range (start and end dates for data extraction from GEE): start_string: string, end_string: string. 
- Reporting period: start_last and end_last. The current repo set the DataPane reporting period of prevouse week. 
- (Optional) Google Drive folder/file id in field_bid_names dictionary
- Cloud free threshold: cloud_free_thresh. The NDWI results are set to NaN for pixels below cloud free threshold.
- NDWI Threshold (to add binary layer based on threshold): thresh_val
- Cloudy threshold: cloudy. If the percentage of cloud-free fields are below this threshold, the status reporting on DataPane for this week will be disabled. 
- Programs to run: programs: list
- Feature names of Field Id, Bid ID, and enrolled status used for the specific program: field_bid_names
- Email recipients can be defined in definitions.py: recipients: list

### Format Dashboard
DataPane is used to generate a reporting dashboard. DataPane allows you to transform Jupyter Notebook or Python script to an interactive web app. It is friendly with Pandas DataFrame, Matplotlib/Seaborn, Plotly, and Folim for map visualization. 
Refer to the [DataPane documentation](https://docs.datapane.com/) for page, numbers, table, plot, and map formatting
### Modifile email message, sender and recieptants
Refer to the example of [yagmail](https://pypi.org/project/yagmail/) to format your email contents.

## License:
his project is licensed under the GNU General Public License v2.0 - see the LICENSE file for details.


## Project Contributors 
Xinyi Wang (USF)
Wan-Chun Liao (USF)
Kirk Klausmeyer (TNC)
Cody Carroll (USF)


## Acknowledgements:
We would also like to thank Robert Clements for his invaluable advice. 
