import requests
import time
from bot import TelegramAlertBot

URL = "https://tickets.museivaticani.va/api/search/result?lang=it&visitorNum=4&visitDate=18/08/2025&area=1&who=1&page=0"
TIMES_URL = "https://tickets.museivaticani.va/api/visit/timeavail?lang=it&visitLang=&visitTypeId=640&visitorNum=4&visitDate=18/08/2025"

bot = TelegramAlertBot()

LAST_TIMES = []

def check():
    r = requests.get(URL).json()

    print(r)

    for visit in r["visits"]:
        if visit["id"] == 640:
            if visit["availability"] == "SOLD_OUT":
                #bot.send_mes(f"Visit '{visit['name']}' is sold out")
                print(f"Visit '{visit['name']}' is sold out")
            else:
                #bot.send_mes(f"Visit '{visit['name']}' is '{visit['availability']}'")
                print(f"Visit '{visit['name']}' is '{visit['availability']}'\nhttps://tickets.museivaticani.va/home/visit/4/1755468000000/1/1")

def get_times():
    r = requests.get(TIMES_URL).json()

    available_times = []

    for time in r["timetable"]:
        if time['availability'] != "SOLD_OUT":
            available_times.append(time['time'])

    return sorted(available_times)

while True:
    #check()
    new_times = get_times()
    print("new_times", new_times)
    print("LAST_TIMES", LAST_TIMES)
    if new_times != LAST_TIMES:
        LAST_TIMES = new_times
        if len(new_times) > 0:
            print(f"New times available: {', '.join(new_times)}")
            bot.send_mes(f"New times available: {', '.join(new_times)}")
        else:
            print("All times sold out")
    time.sleep(2)

