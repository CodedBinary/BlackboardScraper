#!/usr/bin/env python3
import sys
import os
import time
import requests
from selenium import webdriver

import blackboard
import echo


def authenticate(targeturl):
    driver = webdriver.Chrome()
    driver.get(targeturl)
    input("Click enter when on learning resources page")

    return driver


def cookietransfer(driver):
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session


def downloadlink(bone, session):
    myfiles = bone["links"]
    for myfile in myfiles:
        download = session.get(myfile)
        open(bone["name"], 'wb').write(download.content)  # Duplicate names??
    return 0


def downloadskeleton(skeleton, driver):
    session = cookietransfer(driver)
    for bone in skeleton["content"]:
        if bone["type"] in ["File", "Item"]:
            for url in bone["links"]:
                downloadlink(bone, session)

        elif bone["type"] in ["Kaltura Media", "Web Link", "Course Link"]:
            open(bone["name"], 'w').write(bone["links"][0] + "\n" + bone["text"])

        elif bone["type"] == "Lecture_Recordings":
            echo.echoscraping(bone["links"][0], driver)

        elif bone["type"] in ["Content Folder"]:
            os.mkdir(bone["name"])  # Duplicate names???
            os.chdir(bone["name"])
            downloadskeleton(bone, driver)
            os.chdir("..")
        else:
            print("Warning: Unknown listitem type detected. Type", bone["type"])
    return 0


def main(argv):
    targeturl = "https://learn.uq.edu.au"
    driver = authenticate(targeturl)
    rootfolder = {"links": [driver.current_url], "type": "Content Folder", "name": "Learning Resources"}
    data = blackboard.copystructure(rootfolder, driver, targeturl)
    currentTime = str(int(time.time()))
    os.mkdir(currentTime)
    os.chdir(currentTime)
    downloadskeleton(data, driver)
    return data


if __name__ == "__main__":
    main(sys.argv)
