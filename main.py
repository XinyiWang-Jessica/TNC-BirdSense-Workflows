import logging
import logging.handlers
import os

import requests
import yagmail

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

try:
    SOME_SECRET = os.environ["SOME_SECRET"]
except KeyError:
    SOME_SECRET = "Token not available!"
    
try:
    GMAIL_PWD = os.environ["GMAIL_PWD"]
except KeyError:
    GMAIL_PWD = "Token not available!"


if __name__ == "__main__":
    logger.info(f"Token value: {SOME_SECRET}")
    # extract weather info
    r = requests.get('https://weather.talkpython.fm/api/weather?city=saf&state=CA&country=US')
    if r.status_code == 200:
        data = r.json()
        temperature = data["forecast"]["temp"]
        logger.info(f'Weather in San Francisco: {temperature}')
    msg = f"Hello, today's temperature is {temperature}"  
    yag = yagmail.SMTP("wangxinyi1986@gmail.com",
                   GMAIL_PWD)
    # Adding Content and sending it
    yag.send("wangxinyi1986@gmail.com", 
         "Test yagmail",
         msg)
 
        