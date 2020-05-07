#!/usr/bin/env python3
import sys
from selenium import webdriver

import blackboard
import echo


def authenticate(targeturl):
    driver = webdriver.Chrome()
    driver.get(targeturl)

    input("Click enter when on learning resources page")

    return driver


def main(argv):
    targeturl = "https://learn.uq.edu.au"
    driver = authenticate(targeturl)
    rootfolder = {"links": [driver.current_url], "type": "Content Folder", "name": "Learning Resources"}
    data = blackboard.copystructure(rootfolder, driver, targeturl)
    return data


if __name__ == "__main__":
    main(sys.argv)
