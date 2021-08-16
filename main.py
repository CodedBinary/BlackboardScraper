#!/usr/bin/env python3
import sys
import os
import time
from selenium import webdriver
import glob
import importlib.util
import Settings
from Settings import Download, settings
import pickle
import base
import blackboard

# Importing link extractors and folder extractors
modules = glob.glob('LinkExtractors/*.py') + glob.glob('FolderExtractors/*.py') + glob.glob('Downloaders/*.py')
for module in modules:
    spec = importlib.util.spec_from_file_location(module.split("/")[-1].split(".")[0], module)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)

def all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])

def authenticate(targeturl):
    driver = webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    loaded = False

    if settings["session_file"] is not None:
        driver.get(targeturl + "/webapps/login/?action=default_login")
        with open(settings["session_file"], "rb") as cf:
            cookies = pickle.load(cf)
            print(cookies)
        for cookie in cookies:
            print(cookie)
            driver.add_cookie(cookie)
        loaded = True

    driver.get(targeturl)

    input("Click enter when on learning resources page")

    if (settings["session_file"] is not None) and (not loaded):
        with open("session_cookies", "wb") as cf:
            pickle.dump(cookies, cf)

    return driver

def main(argv):
    # Definitely make this argv[1] but i cbf doing it right now bc i dont
    # want to reorder args and screw smth up
    extractors = {"folder": [extractor() for extractor in all_subclasses(blackboard.FolderExtractor)],
                  "link": [extractor() for extractor in all_subclasses(blackboard.LinkExtractor)]}
    downloaders = [downloader() for downloader in all_subclasses(blackboard.Downloader)]

    rootfolder = blackboard.BlackboardItem()
    rootfolder.type = "Content Folder"
    rootfolder.name = "Learning Resources"
    targeturl = Settings.settings["url"]

    if Settings.settings["dry_run"] <= Download.AUTH_ONLY:
        driver = authenticate(targeturl)
        session = base.cookietransfer(driver)
        session.headers['User-Agent'] = 'Mozilla/5.0'
        rootfolder.links = [driver.current_url]

    if Settings.settings["dry_run"] <= Download.COPY_ONLY:
        rootfolder.copystructure(driver, session, targeturl, extractors)

    if Settings.settings["dry_run"] == Download.YES:
        currentTime = str(int(time.time()))
        os.mkdir(currentTime)
        os.chdir(currentTime)
        rootfolder.downloadfolder(session, downloaders, driver)

    return rootfolder


if __name__ == "__main__":
    main(sys.argv)
    print("Success.")
