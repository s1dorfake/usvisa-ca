import requests
import time
from bot import TelegramAlertBot

URL = "https://tickets.museivaticani.va/api/search/result?lang=it&visitorNum=4&visitDate=18/08/2025&area=1&who=1&page=0"
bot = TelegramAlertBot()

def check():
    r = requests.get(URL).json()

    print(r)

    for visit in r["visits"]:
        if visit["id"] == 640:
            if visit["availability"] == "SOLD_OUT":
                #bot.send_mes(f"Visit '{visit['name']}' is sold out")
                print(f"Visit '{visit['name']}' is sold out")
            else:
                bot.send_mes(f"Visit '{visit['name']}' is '{visit['availability']}'")
                print(f"Visit '{visit['name']}' is '{visit['availability']}'\nhttps://tickets.museivaticani.va/home/visit/4/1755468000000/1/1")


while True:
    check()
    time.sleep(2)

