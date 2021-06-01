#!/usr/bin/env python3
import sys
import os
import time
import requests
from selenium import webdriver

import base
import blackboard
import echo


def authenticate(targeturl):
    driver = webdriver.Chrome()
    driver.get(targeturl)
    input("Click enter when on learning resources page")

    return driver


def downloadskeleton(skeleton, driver, lectures=True):
    session = base.cookietransfer(driver)
    session.headers['User-Agent'] = 'Mozilla/5.0'
    for bone in skeleton["content"]:
        if bone["type"] in ["File", "Item", "Image"]:
            base.downloadlink(bone, session)
            if bone["text"] is not None:
                try:
                    name = base.uniquename(bone["name"])
                    open(name, 'w').write(bone["text"])
                except:
                    pass

        elif bone["type"] in ["Kaltura Media", "Web Link", "Course Link"]:
            name = base.uniquename(bone["name"])
            open(name, 'w').write(bone["links"][0] + "\n" + bone["text"])

        elif bone["type"] == "Lecture_Recordings":
            if lectures:
                name = base.uniquename(bone["name"])
                os.mkdir(name)
                os.chdir(name)
                #echo.echoscraping(bone["links"][0], driver)
                os.chdir("..")  # OS COMPAT

        elif bone["type"] in ["Content Folder"]:
            name = base.uniquename(bone["name"])
            os.mkdir(name)
            os.chdir(name)
            downloadskeleton(bone, driver)
            os.chdir("..")  # OS COMPAT

        else:
            print("Warning: Unknown listitem type detected. Type", bone["type"])
    return 0


def main(argv):
    # Definitely make this argv[1] but i cbf doing it right now bc i dont
    # want to reorder args and screw smth up
    if len(argv) == 3 and argv[2] == "--no-lectures":
        lectures = False
    else:
        lectures = True

    targeturl = argv[1]
    driver = authenticate(targeturl)
    rootfolder = {"links": [driver.current_url],
                  "type": "Content Folder",
                  "name": "Learning Resources"}
    data = blackboard.copystructure(rootfolder, driver, targeturl)
    currentTime = str(int(time.time()))
    os.mkdir(currentTime)
    os.chdir(currentTime)
    downloadskeleton(data, driver, lectures)
    return data


if __name__ == "__main__":
    main(sys.argv)
