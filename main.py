#!/usr/bin/env python3
import sys
import os
import time
from selenium import webdriver
import glob
import importlib.util

import blackboard

# Importing link extractors and folder extractors
modules = glob.glob('LinkExtractors/*.py') + glob.glob('FolderExtractors/*.py') + glob.glob('Downloaders/*.py')
for module in modules:
    spec = importlib.util.spec_from_file_location(module.split("/")[-1].split(".")[0], module)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)

def authenticate(targeturl):
    driver = webdriver.Chrome()
    driver.get(targeturl)
    input("Click enter when on learning resources page")

    return driver

def main(argv):
    # Definitely make this argv[1] but i cbf doing it right now bc i dont
    # want to reorder args and screw smth up
    if len(argv) == 3 and argv[2] == "--lectures":
        lectures = True
    else:
        lectures = False

    extractors = {"folder": [extractor() for extractor in blackboard.FolderExtractor.__subclasses__()],
                  "link": [extractor() for extractor in blackboard.LinkExtractor.__subclasses__()]}
    downloaders = [downloader() for downloader in blackboard.Downloader.__subclasses__()]

    targeturl = argv[1]
    driver = authenticate(targeturl)

    rootfolder = blackboard.BlackboardItem()
    rootfolder.links = [driver.current_url]
    rootfolder.type = "Content Folder"
    rootfolder.name = "Learning Resources"

    rootfolder.copystructure(driver, targeturl, extractors)
    currentTime = str(int(time.time()))
    os.mkdir(currentTime)
    os.chdir(currentTime)
    rootfolder.downloadfolder(downloaders, driver)
    return rootfolder


if __name__ == "__main__":
    main(sys.argv)
