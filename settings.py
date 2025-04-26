from dotenv import load_dotenv
import os

load_dotenv()

USER_EMAIL = os.getenv('USER_EMAIL')
USER_PASSWORD = os.getenv('USER_PASSWORD')
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_HASH = os.getenv('API_HASH')
TG_USERS = [int(el) for el in os.getenv('TG_USERS').split(',') if el]

# Account Info
NUM_PARTICIPANTS = 1

# Say you want an appointment no later than Mar 14, 2024
# Please strictly follow the YYYY-MM-DD format
EARLIEST_ACCEPTABLE_DATE = "2024-03-26"
LATEST_ACCEPTABLE_DATE = "2027-01-30" #"2025-12-31"

# Your consulate's city
CONSULATES = {
    "Calgary": 89,
    "Halifax": 90,
    "Montreal": 91,
    "Ottawa": 92,
    "Quebec": 93,
    "Toronto": 94,
    "Vancouver": 95
} # Only Toronto and Vancouver consulates are verified
# Choose a city from the list above
TORONTO = "Toronto"
VANCOUVER = "Vancouver"

# The following is only required for the Gmail notification feature
# Gmail login info
GMAIL_SENDER_NAME = ""
GMAIL_EMAIL = ""
GMAIL_APPLICATION_PWD = ""

# Email notification receiver info
RECEIVER_NAME = ""
RECEIVER_EMAIL = ""

# Override with local, for developers
# from local import *

# See the automation in action
SHOW_GUI = False  # toggle to false if you don't want to see the browser

# If you just want to see the program run WITHOUT clicking the confirm reschedule button
# For testing, also set a date really far away so the app actually tries to reschedule
TEST_MODE = True

# Don't change the following unless you know what you are doing
DETACH = True
NEW_SESSION_AFTER_FAILURES = 5
NEW_SESSION_DELAY = 60
TIMEOUT = 10
FAIL_RETRY_DELAY = 30
DATE_REQUEST_DELAY = 30
DATE_REQUEST_MAX_RETRY = 60
DATE_REQUEST_MAX_TIME = 30 * 60
LOGIN_URL = "https://ais.usvisa-info.com/en-ca/niv/users/sign_in"
AVAILABLE_DATE_REQUEST_SUFFIX_TORONTO = f"/days/{CONSULATES[TORONTO]}.json?appointments[expedite]=false"
AVAILABLE_DATE_REQUEST_SUFFIX_VANCOUVER = f"/days/{CONSULATES[VANCOUVER]}.json?appointments[expedite]=false"
APPOINTMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/appointment"
PAYMENT_PAGE_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/{id}/payment"
REQUEST_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
}
