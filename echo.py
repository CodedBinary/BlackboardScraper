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
            name    (str)   : The name of the video to download
            links   (lst)   : The url of the video to download in a list
    '''
    links = [{"name": option["contents"][-1]["name"], "links": option["contents"][-1]["value"]} for option in srcoptions]
    return links


def getechovideos(driver):
    ''' Retrieves the echo audio and video links for a given lecture, given that the driver is currently on the download box after clicking the green button.
    '''
    buttonlist = driver.find_elements_by_css_selector('a[class*="screenOption"]')

    for button in buttonlist:
        button.click()

        soup = base.loadpage(driver)
        screen = soup.find("div", {"class": "downloadOptions"}).contents
        srcoptions = [{"name": srcoption.find("select")["name"], "contents": [{"value": resoption["value"], "text": resoption.text} for resoption in srcoption.find_all("option")]} for srcoption in screen if srcoption != "\n"]

        links = selectvideo(srcoptions)
        session = base.cookietransfer(driver)
        for item in links:
            base.downloadlink({"name": item["name"], "links": item["links"]}, session)
        return 0


def echoscraping(link, driver):
    ''' Scrapes the given echo page for links.
    '''
    driver.get(link)
    time.sleep(1)
    soup = base.loadpage(driver)
    datelist = soup.find_all("span", {"class": "date"})
    timelist = soup.find_all("span", {"class": "time"})
    datelist = [recorddate.text for recorddate in datelist]
    timelist = [recordtime.text for recordtime in timelist]

    for button in driver.find_elements_by_class_name("menu-opener"):
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

        getechovideos(driver)
        driver.find_element_by_css_selector("a[class='btn white medium']").click()  # Click the cancel button
    return 0
