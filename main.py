#!/usr/bin/env python3
import sys
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

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
        folderlist = []
        courselinklist = []
        weblinklist = []
        lecturerecordingslist = []

        if objecttype == "Item":
            bbfiles = bbobject.find_all("a", href=re.compile("bbc"))
            for bbfile in bbfiles:
                link = targeturl + bbfile["href"]

        elif objecttype == "File":
            bbfile = bbobject.find("a", href=re.compile("bbc"))
            link = targeturl + bbfile["href"]

        elif objecttype == "Kaltura Media":
            href = bbobject.find("div", {"class": "kalturawrapper"}).find("iframe")["src"]
            link = targeturl + href

        elif objecttype == "Course Link":
            link = bbobject.find("a", href=re.compile("http"))["href"]
            courselinklist += [link]

        elif objecttype == "Web Link":
            link = bbobject.find("a", href=re.compile("http"))["href"]
            weblinklist += [link]

        elif objecttype == "Lecture_Recordings":
            link = bbobject.find("a", href=re.compile("webapp"))["href"]
            lecturerecordingslist += [link]

        elif objecttype == "Content Folder":
            link = targeturl + bbobject.find("a", href=re.compile("webapp"))["href"]
            folderlist += [link]

        else:
            print("WARNING: UNKNOWN OBJECT TYPE DETECTED", objecttype)

        text = bbobject.find("div", {"class": "vtbegenerated"})

        # At the moment we have the text and link variables, and then a bunch of arrays of external links. Note that link gets overwritten, so saving operations need to go in the for loop. We need to find out a nice way to save the text and links in the file structure and then actually download them. 

    for link in linklist:
        getdocuments(link)

def echoscraping(link):
    driver.get(link)
    # ADD WAIT HERE
    soup = loadpage()
    datelist = soup.find_all("span", {"class":"date"})
    timelist = soup.find_all("span", {"class":"time"})
    datelist = [date.text for date in datelist]
    timelist = [time.text for time in timelist]

    for button in driver.find_elements_by_class_name("menu-opener"):
        ActionChains(driver).move_to_element(button).perform()
        button.click # Click the green play button
        # ADD WAIT HERE
        driver.find_elements_by_xpath("//a[@role='menuitem']")[1].click() # Click the download button
        # ADD WAIT HERE


        ### SELECT YOUR RESOLUTION AND VIDEO


        soup = loadpage()
        href = soup.find("div", {"class": "right"}).contents[1]["href"] # Find the href on the right hand button
        link = "https://echo360.org.au" + href
        driver.find_element_by_xpath("//a[@class='btn white medium']").click()  # Click the cancel button
    return 0

def main(argv):
    authenticate()
    getdocuments(driver.current_url)
    pass


if __name__ == "__main__":
    main(sys.argv)


