#!/usr/bin/env python3
import sys
import os
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def authenticate():
    targeturl = "https://learn.uq.edu.au"

    redirect = requests.get(targeturl)
    driver = webdriver.Chrome()
    driver.get(targeturl)

    input("Click enter when on learning resources page")

    return driver

def getdocuments(folder,driver):
    targeturl = "https://learn.uq.edu.au"
    # getdocuments will be called on regular items and such by recursion
    if folder["type"] != "Content Folder":
        return folder

    # We are using a list for the directory structure instead of a dict because we can have duplicate names and urls are ugly
    returnlist = []
    driver.get(folder["links"][0])
    # ADD WAIT IN HERE
    soup = loadpage(driver)

    try:                # empty folders
        contents = [x for x in soup.find("ul", {"id": "content_listContainer"}).contents if x != "\n"]
    except:
        contents = []

    for bblistitem in contents:
        # bblistitem corresponds to the html of one item in a blackboard page. For example, the Week 1 folder, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.

        bbitemdict = {
                "name": bblistitem.find("h3").find("span", style = re.compile("")).text,
                "links": [],
                "type": bblistitem.img["alt"],
                "text": bblistitem.find("div", {"class": "vtbegenerated"}),
                "content": []
                }
        # bbitemdict stores the extracted information of bblistitem. It isn't stored as a class because its easier to export this and we are only storing data in it.

        if bbitemdict["type"] == "Item":
            bbfiles = bblistitem.find_all("a", href=re.compile("bbc"))
            for bbfile in bbfiles:
                link = targeturl + bbfile["href"]
                bbitemdict["links"] += [link]

        else:                               # elif isn't used so that bbitemdict["links"] can be assigned [link] uniformly for the rest of the categories
            if bbitemdict["type"] == "File":
                href = bblistitem.find("a", href=re.compile("bbc"))["href"]
                link = targeturl + href

            elif bbitemdict["type"] == "Kaltura Media":
                href = bblistitem.find("div", {"class": "kalturawrapper"}).find("iframe")["src"]
                link = targeturl + href

            elif bbitemdict["type"] == "Course Link":
                link = bblistitem.find("a", href=re.compile("http"))["href"]

            elif bbitemdict["type"] == "Web Link":
                link = bblistitem.find("a", href=re.compile("http"))["href"]

            elif bbitemdict["type"] == "Lecture_Recordings":
                link = bblistitem.find("a", href=re.compile("webapp"))["href"]

            elif bbitemdict["type"] == "Content Folder":
                link = targeturl + bblistitem.find("a", href=re.compile("webapp"))["href"]

            else:
                print("WARNING: UNKNOWN OBJECT TYPE DETECTED", bbitemdict["type"])

            bbitemdict["links"] += [link]
        returnlist += [bbitemdict]
    folder["content"] = [getdocuments(x,driver) for x in returnlist]
    return folder

def downloadechovideo(link):

    return 0

def getechovideos():
    ### SELECT RESOLUTION HERE
    buttonlist = driver.find_elements_by_xpath('//a[@class=matches(".*screenOption.*")]')

    for button in buttonlist:
        button.click()
        href = soup.find("div", {"class": "right"}).contents[1]["href"] # Find the href on the right hand button
        link = "https://echo360.org.au" + href
        downloadlink(link)
        # You can't keep the links separately, because echo generates links dynamically; clicking on options doesn't change the download link

def echoscraping(link):
    driver.get(link)
    # ADD WAIT HERE
    soup = loadpage(driver)
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
        getechovideos()
        driver.find_element_by_xpath("//a[@class='btn white medium']").click()  # Click the cancel button
    return 0

def main(argv):
    driver = authenticate()
    data = getdocuments({"links": [driver.current_url], "type": "Content Folder"}, driver)
    return data


if __name__ == "__main__":
    main(sys.argv)


