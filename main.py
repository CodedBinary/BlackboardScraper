#!/usr/bin/env python3
import sys
import os
import time
from selenium import webdriver
import glob
import importlib.util
import Settings

import base
import blackboard

# Importing link extractors and folder extractors
# Note this seems to break for...some fucking reason???
#modules = glob.glob('LinkExtractors/*.py') + glob.glob('FolderExtractors/*.py') + glob.glob('Downloaders/*.py')
#for module in modules:
#    spec = importlib.util.spec_from_file_location(module.split("/")[-1].split(".")[0], module)
#    foo = importlib.util.module_from_spec(spec)
#    spec.loader.exec_module(foo)
#    print("\n", foo)
#    print("prepre folderextractor subclasses", blackboard.FolderExtractor.__subclasses__())
#    print("prepre linkextractor subclasses", blackboard.LinkExtractor.__subclasses__())
#    print("prepre Downloader subclasses", blackboard.Downloader.__subclasses__())
#def all_subclasses(cls):
#    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])
#

import Downloaders.dfoldertype
import Downloaders.echo
import Downloaders.misc
import Downloaders.standard
import FolderExtractors.cf
import FolderExtractors.lm
import LinkExtractors.file
import LinkExtractors.image
import LinkExtractors.item
import LinkExtractors.kaltura
import LinkExtractors.foldertype
import LinkExtractors.weblink

def authenticate(targeturl):
    driver = webdriver.Chrome()
    driver.get(targeturl)
    input("Click enter when on learning resources page")

    return driver

def main(argv):
    # Definitely make this argv[1] but i cbf doing it right now bc i dont
    # want to reorder args and screw smth up
    extractors = {}
    extractors = {"link": [extractor for extractor in blackboard.LinkExtractor.__subclasses__()]}
    extractors["folder"] = [extractor for extractor in blackboard.FolderExtractor.__subclasses__()]
    downloaders = [downloader for downloader in blackboard.Downloader.__subclasses__()]

    if Settings.settings["verbosity"] >= 2:
        print("Extractors: ", extractors)
        print(blackboard.Downloader.__subclasses__())
        print("Downloaders: ", downloaders)

    if Settings.settings["verbosity"] >= 3:
        print("Settings: ", Settings.settings)

    rootfolder = blackboard.BlackboardItem()
    rootfolder.type = "Content Folder"
    rootfolder.name = "Learning Resources"
    targeturl = Settings.settings["url"]

    if Settings.settings["dry_run"] <= 2:
        driver = authenticate(targeturl)
        session = base.cookietransfer(driver)
        session.headers['User-Agent'] = 'Mozilla/5.0'
        rootfolder.links = [driver.current_url]

    if Settings.settings["dry_run"] <= 1:
        rootfolder.copystructure(driver, session, targeturl, extractors)

    if Settings.settings["dry_run"] == 0:
        currentTime = str(int(time.time()))
        os.mkdir(currentTime)
        os.chdir(currentTime)
        rootfolder.downloadfolder(session, downloaders, driver)
    return rootfolder


if __name__ == "__main__":
    main(sys.argv)
