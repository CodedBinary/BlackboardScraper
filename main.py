#!/usr/bin/env python3
import sys
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def authenticate(targeturl):
    driver = webdriver.Chrome()
    driver.get(targeturl)

    input("Click enter when on learning resources page")

    return driver

def linkextractor(bbitemdict, bblistitem, targeturl):
    '''Extracts relevent links from a block of html in blackboard corresponding to an item
    Args:
    bbitemdict  (dict)  : The dict the items are being extracted into
    bblistitem  (soup)  : The BeautifulSoup object corresponding to the object
    targeturl   (str)   : The domain of the blackboard site. Used to prepend to hrefs.

    Returns:
    bbitemdict (dict)   : The dict with an updated "links" entry
    '''

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

    return bbitemdict

def copystructure(folder,driver,targeturl):
    '''Recursively copies the structure and links of a blackboard folder

    Args:
    folder  (dict)  : The root folder to copy. Should be initialised with a type, name, and desired link.
    driver  (lmao)  : The instance of the selenium driver to be used

    Return:
    folder  (dict)      : The recursive structure of the folder.

    Object Structure:
        name (str)      : The name of the object. Eg Week 1, Midsemester Exam
        text (html)      : The text below the title as html. ### SHOULD BE CHANGED TO THIS, IS CURRENTLY A BS4 OBJECT ###
        links (lst)     : A list of links contained in the object
        type (str)      : The type of object. Eg Course Link, Web Link, Item...
        content (lst)   : A list of objects contained within this object. Only valid for folders.

    '''
    # copystructure will be called on regular items and such by recursion. It should simply return the item if it is not a folder
    if folder["type"] != "Content Folder":
        return folder

    # We are using a list for the directory structure instead of a dict because we can have duplicate names and urls are ugly
    contentlist = []
    driver.get(folder["links"][0])
    soup = loadpage(driver)

    try:                # empty folders can fuck shit up
        contents = [x for x in soup.find("ul", {"id": "content_listContainer"}).contents if x != "\n"]
    except:
        contents = []

    for bblistitem in contents:
        # bblistitem corresponds to the html of one item in a blackboard page. For example, the Week 1 folder, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.
        # bbitemdict stores the extracted information of bblistitem. It isn't stored as a class because its easier to export this and we are only storing data in it.
        bbitemdict = {
                "name": bblistitem.find("h3").find("span", style = re.compile("")).text,
                "links": [],
                "type": bblistitem.img["alt"],
                "text": bblistitem.find("div", {"class": "vtbegenerated"}),
                "content": []
                }

        bbitemdict = linkextractor(bbitemdict, bblistitem, targeturl)

        contentlist += [bbitemdict]                                                  
    folder["content"] = [copystructure(x,driver,targeturl) for x in contentlist]     # Stores the contents of the folder under the key contents
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
    targeturl = "https://learn.uq.edu.au"
    driver = authenticate(targeturl)
    rootfolder = {"links": [driver.current_url], "type": "Content Folder", "name": "Learning Resources"}
    data = copystructure(rootfolder, driver, targeturl)
    return data

if __name__ == "__main__":
    main(sys.argv)


