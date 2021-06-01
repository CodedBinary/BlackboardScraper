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


def downloadfolder(folder, driver, lectures=False):
    '''
    Downloads the content in a BlackboardItem folder.
    '''
    session = base.cookietransfer(driver)
    session.headers['User-Agent'] = 'Mozilla/5.0'
    for blackboarditem in folder.content:
        if blackboarditem.type in ["File", "Item", "Image"]:
            base.downloadlink(blackboarditem, session)
            if blackboarditem.text is not None:
                try:
                    name = base.uniquename(blackboarditem.name)
                    open(name, 'w').write(blackboarditem.text)
                except:
                    pass

        elif blackboarditem.type in ["Kaltura Media", "Web Link", "Course Link"]:
            name = base.uniquename(blackboarditem.name)
            open(name, 'w').write(blackboarditem.links[0] + "\n" + blackboarditem.text)

        elif blackboarditem.type == "Lecture_Recordings":
            if lectures:
                name = base.uniquename(blackboarditem.name)
                os.mkdir(name)
                os.chdir(name)
                echo.echoscraping(blackboarditem.links[0], driver)
                os.chdir("..")

        elif blackboarditem.type in ["Content Folder"]:
            name = base.uniquename(blackboarditem.name)
            os.mkdir(name)
            os.chdir(name)
            downloadfolder(blackboarditem, driver)
            os.chdir("..")

        else:
            print("Warning: Unknown listitem type detected. Type", blackboarditem.type)
    return 0


def main(argv):
    # Definitely make this argv[1] but i cbf doing it right now bc i dont
    # want to reorder args and screw smth up
    if len(argv) == 3 and argv[2] == "--lectures":
        lectures = True
    else:
        lectures = False

    targeturl = argv[1]
    driver = authenticate(targeturl)

    rootfolder = blackboard.BlackboardItem()
    rootfolder.links = [driver.current_url]
    rootfolder.type = "Content Folder"
    rootfolder.name = "Learning Resources"

    blackboard.copystructure(rootfolder, driver, targeturl)
    currentTime = str(int(time.time()))
    os.mkdir(currentTime)
    os.chdir(currentTime)
    downloadfolder(rootfolder, driver, lectures)
    return rootfolder


if __name__ == "__main__":
    main(sys.argv)
