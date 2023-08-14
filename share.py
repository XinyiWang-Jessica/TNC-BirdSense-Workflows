import yagmail
from definitions import *

# extract token from environment
try:
    GMAIL_PWD = os.environ["GMAIL_PWD"]
except KeyError:
    GMAIL_PWD = "Token not available!"


def share_report(program):
    '''
    This function send out the created datapane report for each program
    '''
    msg = f"Please check the latest BirdSense report for program \
        {program} in the attachment"
    yag = yagmail.SMTP("wangxinyi1986@gmail.com",
                       GMAIL_PWD)
    # Adding Content and sending it
    attachment_path = f'latest_report_{program}.html'  # Replace with your file path
    attachments = [attachment_path]
    yag.send(recipients[program], # defined in definitions.py
             f"Weekly BirdSense Report - {program}",
             msg,
             attachments = attachments)
    yag.close()

# Step 5: send email   
for program in programs:
        share_report(program)
    

