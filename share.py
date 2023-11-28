import os
import yagmail
from scripts.definitions import *

# extract Gmail token from environment
try:
    GMAIL_PWD = os.environ["GMAIL_PWD"]
except KeyError:
    GMAIL_PWD = "Token not available!"


def share_report():
    '''
    This function send out the created datapane report for each program
    '''

    file_path = ['weekly_data/' + program + '_weekly_flood_status.csv' for program in programs]
    yag = yagmail.SMTP("wangxinyi1986@gmail.com",
                       GMAIL_PWD)
    # Adding Content and sending it
    yag.send(recipients, # defined in definitions.py
             f"Weekly BirdSense Reports",
             contents = email_content,
             attachments = file_path
             )
    yag.close()
    print('email sent')

# Step 5: send email   
share_report()
    

