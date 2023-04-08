#!/usr/bin/python3
# -*- coding:utf-8 -*-
import logging
import os
import telepot
import time
import yaml
from PyP100 import PyP110
from screen import show_plugs, show_random_image

LONG_SLEEP = 300
SHORT_SLEEP = 60

def initialize_plugs(plugs):
    for plug in plugs:
        plug["tapo"] = PyP110.P110(
            plug["ip"], os.environ["TPLINK_LOGIN"], os.environ["TPLINK_PASSWORD"]
        )
        plug["sleep"] = LONG_SLEEP
        plug["is_on"] = False
        plug["below_threshold_count"] = 0
        plug["tapo"].handshake()
        plug["tapo"].login()
        plug["name"] = plug["tapo"].getDeviceName()
        plug["login_needed"] = False

def relogin(plug):
    logging.info(f"{plug['name']}:   Trying to re-login")
    try:
        plug["tapo"].handshake()
        plug["tapo"].login()
    except Exception as e:
        logging.info(f"{plug['name']}:   Connection error during re-login")
        logging.info(e)
        return False
    plug["login_needed"] = False
    plug["sleep"] = LONG_SLEEP
    return True


def test_plug(plug, bot):
    if plug["login_needed"]:
        if not relogin(plug):
            return False
    try:
        usage = plug["tapo"].getEnergyUsage()["result"]
    except Exception:
        plug["login_needed"] = True
        plug["sleep"] = SHORT_SLEEP
        logging.info(f"{plug['name']}:   Connection error")
        return False
    current_w = usage["current_power"] / 1000.0
    logging.info(f"{plug['name']}: {current_w} W")

    if plug["is_on"]:
        plug["sleep"] = SHORT_SLEEP
        if current_w < plug["threshold_down"]:
            if plug["below_threshold_count"] < plug.get(
                "below_threshold_max_count", 2
            ):
                logging.info(
                    f"{plug['name']}: {plug['below_threshold_count']} < {plug.get('below_threshold_max_count', 2)}"
                )
                plug["below_threshold_count"] += 1
            else:
                plug["is_on"] = False
                plug["sleep"] = LONG_SLEEP
                logging.info(
                    f"{plug['name']}: {plug['below_threshold_count']} >= {plug.get('below_threshold_max_count', 2)}"
                )
                logging.info(f"{plug['name']}:" + " " * 40 + "OFF")
                bot.sendMessage(
                    os.environ["TELEGRAM_SEND_TO"], f"{plug['name']}: OFF"
                )
                return True
        else:
            plug["below_threshold_count"] = 0
    else:
        if current_w > plug["threshold_up"]:
            plug["is_on"] = True
            plug["below_threshold_count"] = 0
            plug["sleep"] = SHORT_SLEEP
            logging.info(f"{plug['name']}:" + " " * 40 + "ON")
            bot.sendMessage(os.environ["TELEGRAM_SEND_TO"], f"{plug['name']}: ON")
            return True


def run_it(plugs, bot):
    count = 0
    while True:
        update_needed = False
        for plug in plugs:
            update_needed = True if test_plug(plug, bot) else update_needed
        if update_needed:
            show_plugs([plug["name"], plug["is_on"]] for plug in plugs)
            count = 0
        if not any([plug["is_on"] for plug in plugs]):
            count += 1
        if count > 3:
            count = 0
            show_random_image()
        logging.info(f"Count: {count}")

        sleeptimes = [plug["sleep"] for plug in plugs]
        sleeptime = sorted(sleeptimes)[0]
        logging.info(f"Going to sleep for {sleeptime} seconds")
        time.sleep(sleeptime)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    bot = telepot.Bot(os.environ["TELEGRAM_BOT_ID"])
    bot.sendMessage(os.environ["TELEGRAM_SEND_TO"], "Started")

    f = open("list.yaml", mode="r")
    plugs = yaml.load(f, Loader=yaml.FullLoader)

    initialize_plugs(plugs)

    show_random_image()
    run_it()