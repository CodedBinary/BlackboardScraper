#!/usr/bin/env python3
import sys
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def loadpage():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def authenticate():
    targeturl = "https://learn.uq.edu.au"

    redirect = requests.get(targeturl)
    driver = webdriver.Chrome()
    driver.get(targeturl)

    input("Click enter when on learning resources page")

    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

def getdocuments(targeturl):
    driver.get(targeturl)
    # May need an appropriate wait in here
    soup = loadpage()

    title = soup.find("span", {"id": "pageTitleText"}).contents[1].contents[0]
    os.mkdir(title)

    for bbobject in soup.find("ul", {"id": "content_listContainer"}).contents:
        objecttype = bboject.img["alt"]
        linklist = []

        if objecttype == "Item":
            bbfiles = bbobject.find_all("a", href=re.compile("bbc")
            for bbfile in bbfiles:
                link = targeturl + bbfile["href"]

        elif objecttype == "File":
            bbfile = bbobject.find("a", href=re.compile("bbc")
            link = targeturl + bbfile["href"]

        elif objecttype == "Course Link":
            link = bbobject.find("a", href=re.compile("http"))["href"]

        elif objecttype == "Web Link":
            link = bbobject.find("a", href=re.compile("http"))["href"]

        elif objecttype == "Lecture_Recordings":
            link = bbobject.find("a", href=re.compile("webapp"))["href"]

        elif objecttype == "Content Folder":
            link = targeturl + bbobject.find("a", href=re.compile("webapp"))["href"]
            linklist += [link]

        else:
            print("WARNING: UNKNOWN OBJECT TYPE DETECTED", objecttype)

        text = bbobject.find("div", {"class": "vtbegenerated"})

        # At the moment we have the text and link variables. Note that link gets overwritten, so saving operations need to go in the for loop. We need to find out a nice way to save the text and links in the file structure and then actually download them. 

    for link in linklist:
        getdocuments(link)

def echoscraping(link):
    return 0

def main(argv):
    authenticate()
    getdocuments(driver.current_url)
    pass


if __name__ == "__main__":
    main(sys.argv)


