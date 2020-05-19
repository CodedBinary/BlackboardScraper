import base
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains


def selectvideo(srcoptions):
    '''Used to determine which echo videos are selected for download.

    Args:
        srcoptions  (lst)   : A list of dictionaries. Each dictionary corresponds to a single screen/stream you can download. Each dict is formatted as follows:

        name        (str)   : The name of the source. My university uses "video-one", "video-two", and "audio" for two video streams and an audio only one.
        contents    (lst)   : A list of the resolution options in the dropdown. Each option contains a text and value key:
            text    (str)   : Literally just the text in the dropdown box.
            value   (str)   : The url of the download.

    Return:
        links       (dict)  : A dict of the videos to download.
            res     (str)   : The resolution of the video to download
            links   (lst)   : The url of the video to download in a list
            type    (str)   : The type should always be Lecture_Recordings or an equivalent
    '''
    links = [{"res": option["contents"][-1]["text"],
              "links": [option["contents"][-1]["value"]],
              "type": "Lecture_Recordings"} for option in srcoptions]
    return links


def getechovideos(driver, metadata):
    ''' Retrieves the echo audio and video links for a given lecture, merges metadata from parent function, and downloads file. Requires the driver is currently on the download box after clicking the green button.
    '''
    soup = base.loadpage(driver)
    screen = soup.find("div", {"class": "downloadOptions"}).contents
    srcoptions = [{"name": srcoption.find("select")["name"],
                   "contents": [{"value": resoption["value"],
                                 "text": resoption.text} for resoption in srcoption.find_all("option")]}
                  for srcoption in screen if srcoption != "\n"]
    # I don't think theres any hope for this list comprehension maybe u guys can screw around with making the split version work
    downloads = selectvideo(srcoptions)
    session = base.cookietransfer(driver)
    for download in downloads:
        print(download)
        download.update(metadata)
        print(download)
        base.downloadlink(download, session)
    return 0


def echoscraping(link, driver):
    ''' Scrapes the given echo page for links and data.
    '''
    driver.get(link)
    time.sleep(1)
    soup = base.loadpage(driver)
    datelist = soup.find_all("span", {"class": "date"})
    timelist = soup.find_all("span", {"class": "time"})
    namelist = soup.find_all("div", {"class": "class-row"})
    datelist = [recorddate.text for recorddate in datelist]
    timelist = [recordtime.text for recordtime in timelist]
    namelist = [recordname.find("header", {"class": "header"}).contents[0].text for recordname in namelist]
    metadata = [  # I'm pretty sure this isnt the way to format it
                {"name": namelist[i],
                 "time": timelist[i],
                 "date": datelist[i]}
                for i in range(len(datelist))]

    for i in range(len(driver.find_elements_by_class_name("class-row"))):
        row = driver.find_elements_by_class_name("class-row")[i]
        button = row.find_element_by_class_name("menu-opener")  # Some echo pages have multiple green buttons per row. We need each iteration of the for loop to correspond to a row so the metadata matches up. Afaik, there can only be one lecture recording button and it always occurs first, so there isn't a for loop for each button.
        ActionChains(driver).move_to_element_with_offset(button, 0, 0).perform()
        button.click()  # Click the green play button
        time.sleep(1)

        try:
            downloadbutton = driver.find_elements_by_css_selector("a[role='menuitem']")[1]
            ActionChains(driver).move_to_element(downloadbutton).perform()
            downloadbutton.click()
            time.sleep(1)
        except IndexError:
            pass

        getechovideos(driver, metadata[i])  # We pass the metadata down so getechovideos can submit the download itself.
        driver.find_element_by_css_selector("a[class='btn white medium']").click()  # Click the cancel button
    return 0
