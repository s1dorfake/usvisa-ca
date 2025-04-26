import re
import traceback
import random
from datetime import datetime
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from legacy_rescheduler import legacy_reschedule
from request_tracker import RequestTracker
from settings import *
from bot import TelegramAlertBot

import tempfile

bot = TelegramAlertBot()

def get_chrome_driver() -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", DETACH)
    options.add_argument("--incognito")
    if not SHOW_GUI:
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")  # Required for Linux compatibility
    options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues on Linux

    driver = webdriver.Chrome(options=options)
    return driver


def login(driver: WebDriver) -> None:
    driver.get(LOGIN_URL)
    timeout = TIMEOUT

    email_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "user_email"))
    )
    email_input.send_keys(USER_EMAIL)

    password_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, "user_password"))
    )
    password_input.send_keys(USER_PASSWORD)

    policy_checkbox = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "icheckbox"))
    )
    policy_checkbox.click()

    login_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.NAME, "commit"))
    )
    login_button.click()


def get_appointment_page(driver: WebDriver) -> None:
    timeout = TIMEOUT
    continue_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Continue"))
    )
    continue_button.click()
    sleep(3)
    current_url = driver.current_url
    url_id = re.search(r"/(\d+)", current_url).group(1)
    appointment_url = APPOINTMENT_PAGE_URL.format(id=url_id)
    driver.get(appointment_url)


def get_available_dates(
    driver: WebDriver, 
    request_tracker: RequestTracker,
    suffix: str = AVAILABLE_DATE_REQUEST_SUFFIX_TORONTO,
) -> list | None:
    request_tracker.log_retry()
    request_tracker.retry()
    current_url = driver.current_url
    request_url = current_url + suffix
    request_header_cookie = "".join(
        [f"{cookie['name']}={cookie['value']};" for cookie in driver.get_cookies()]
    )
    request_headers = REQUEST_HEADERS.copy()
    request_headers["Cookie"] = request_header_cookie
    request_headers["User-Agent"] = driver.execute_script("return navigator.userAgent")
    try:
        response = requests.get(request_url, headers=request_headers)
    except Exception as e:
        print("Get available dates request failed: ", e)
        return None
    if response.status_code != 200:
        print(f"Failed with status code {response.status_code}")
        print(f"Response Text: {response.text}")
        return None
    try:
        dates_json = response.json()
    except:
        print("Failed to decode json")
        print(f"Response Text: {response.text}")
        return None
    dates = [datetime.strptime(item["date"], "%Y-%m-%d").date() for item in dates_json]
    return dates


def reschedule(driver: WebDriver, retryCount: int = 0) -> bool:
    date_request_tracker = RequestTracker(
        retryCount if (retryCount > 0) else DATE_REQUEST_MAX_RETRY,
        30 * retryCount if (retryCount > 0) else DATE_REQUEST_MAX_TIME
    )
    while date_request_tracker.should_retry():
        dates = get_available_dates(driver, date_request_tracker)
        if not dates:
            print("Error occured when requesting available dates")
            sleep(DATE_REQUEST_DELAY)
            continue
        earliest_available_date = dates[0]
        latest_acceptable_date = datetime.strptime(
            LATEST_ACCEPTABLE_DATE, "%Y-%m-%d"
        ).date()
        if earliest_available_date <= latest_acceptable_date:
            print(
                f"{datetime.now().strftime('%H:%M:%S')} FOUND SLOT ON {earliest_available_date}!!!"
            )
            try:
                if legacy_reschedule(driver, earliest_available_date):
                    print("SUCCESSFULLY RESCHEDULED!!!")
                    return True
                return False
            except Exception as e:
                print("Rescheduling failed: ", e)
                traceback.print_exc()
                continue
        else:
            print(
                f"{datetime.now().strftime('%H:%M:%S')} Earliest available date is {earliest_available_date}"
            )
        sleep(DATE_REQUEST_DELAY)
    return False


def reschedule_with_new_session(retryCount: int = DATE_REQUEST_MAX_RETRY) -> bool:
    driver = get_chrome_driver()
    session_failures = 0
    while session_failures < NEW_SESSION_AFTER_FAILURES:
        try:
            login(driver)
            get_appointment_page(driver)
            break
        except Exception as e:
            print("Unable to get appointment page: ", e)
            session_failures += 1
            sleep(FAIL_RETRY_DELAY)
            continue
    rescheduled = reschedule(driver, retryCount)
    driver.quit()
    if rescheduled:
        return True
    else:
        return False
    
def send_notifs(earliest_dates):
    latest_acceptable_date = datetime.strptime(
        LATEST_ACCEPTABLE_DATE, "%Y-%m-%d"
    ).date()

    if earliest_dates[TORONTO] and earliest_dates[TORONTO] <= latest_acceptable_date:
        bot.send_mes(f"{TORONTO} - {earliest_dates[TORONTO]}\nhttps://ais.usvisa-info.com/en-ca/niv/users/sign_in")

    if earliest_dates[VANCOUVER] and earliest_dates[VANCOUVER] <= latest_acceptable_date:
        bot.send_mes(f"{VANCOUVER} - {earliest_dates[VANCOUVER]}\nhttps://ais.usvisa-info.com/en-ca/niv/users/sign_in")
    
def scan_appointments(retryCount: int = DATE_REQUEST_MAX_RETRY, sleepTimeSec = 60):
    driver = get_chrome_driver()
    session_failures = 0
    while session_failures < NEW_SESSION_AFTER_FAILURES:
        try:
            login(driver)
            get_appointment_page(driver)
            break
        except Exception as e:
            print("Unable to get appointment page: ", e)
            session_failures += 1
            sleep(FAIL_RETRY_DELAY)
            continue

    while True:
        earliest_dates = get_available_date(driver, retryCount)
        if not earliest_dates[TORONTO] and not earliest_dates[VANCOUVER]:
            driver.quit()
            print("None earliest dates, logging in again.")
            return
        
        send_notifs(earliest_dates)
        sleep(random.uniform(sleepTimeSec - 5, sleepTimeSec + 5))


def get_available_date(driver, retryCount: int = DATE_REQUEST_MAX_RETRY):
    date_request_tracker = RequestTracker(
        retryCount if (retryCount > 0) else DATE_REQUEST_MAX_RETRY,
        30 * retryCount if (retryCount > 0) else DATE_REQUEST_MAX_TIME
    )

    while date_request_tracker.should_retry():
        dates_toronto = get_available_dates(driver, date_request_tracker, AVAILABLE_DATE_REQUEST_SUFFIX_TORONTO)
        sleep(random.uniform(5, 10))
        dates_vancouver = get_available_dates(driver, date_request_tracker, AVAILABLE_DATE_REQUEST_SUFFIX_VANCOUVER)
        if not dates_toronto and not dates_vancouver:
            print("Error occured when requesting available dates")
            sleep(DATE_REQUEST_DELAY)
            continue
        earliest_available_dates = {
            TORONTO : dates_toronto[0] if dates_toronto else None,
            VANCOUVER : dates_vancouver[0] if dates_vancouver else None,
        }
        print(f"Successfully requested available dates: {earliest_available_dates}")
        return earliest_available_dates


if __name__ == "__main__":
    session_count = 0
    while True:
        session_count += 1
        print(f"Attempting with new session #{session_count}")
        scan_appointments()
        sleep(NEW_SESSION_DELAY)

