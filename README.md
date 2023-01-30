# TNC BirdSense Report Automation Workflows

Short description of Project

## Features:
- Extract Sentinel 2 data from Google Earth Engine API
- Process data to obtain the percent of flooding and cloud-free indicator by fields
- Generate a dashboard report through DataPane APP (example screenshot)
- Schedule report sharing by email

## Preparation
### GEE Authentication with Google Service Account
To access data from GEE API, Google Searvice Account is used to authenticate to Earth Engine. To do so, follow the [guide of create service account](https://developers.google.com/earth-engine/guides/service_account) and complete the steps below:
  1. Create a Google Cloud Project
  2. Choose the created project and create a Service Account
  3. Create a private key for the Service Account and download the jason key file
  4. Register your service account for use with the Earth Engine API.
  5. Save the jason key content as a repo secrete with the Name of GEE_AUTH under the repo Settings
### DataPane Authentication
To generate a dashboard report on [DataPane](https://datapane.com/), an API token is required for access. Follow the [instrution](https://docs.datapane.com/tutorials/automation/#introduction) and complete the following steps:
  1. Create a DataPane account and login
  2. Go to the setting page and copy the API Token
  3. Add the API token as a repo secrete with the Name of DATAPANE_TOKEN 
### Gmail Authentication
Yet Another Gmail [(yagmail)] (https://yagmail.readthedocs.io/en/latest/)is applied to send emails automaticlly. It requires sign-in process to authorize. Follow the instruction to obtain the [Gmail App password] (https://support.google.com/mail/answer/185833?hl=en). Then, add the password to the repo secrete with the name of GMAIL_PWD.
### GitHub Repository Secrete Set Up

## How to Use
### Set up a schedule to run repo action
### Define fields, start and end dates
### Formate Dashboard
### Modifile email message, sender and recieptants

## Acknowledgement:

