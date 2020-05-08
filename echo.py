import base
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains


def selectvideo(srcoptions):
    links = [option["contents"][-1]["value"] for option in srcoptions]
    return links


def getechovideos(driver):
    buttonlist = driver.find_elements_by_css_selector('a[class*="screenOption"]')

    for button in buttonlist:
        button.click()

        soup = base.loadpage(driver)
        dropdown = soup.find("div", {"class": "downloadOptions"}).contents
        srcoptions = [{"name": srcoption.find("select")["name"], "contents": [{"value": resoption["value"], "text": resoption.text} for resoption in srcoption.find_all("option")]} for srcoption in dropdown if srcoption != "\n"]

        links = selectvideo(srcoptions)
        session = base.cookietransfer(driver)
        base.downloadlink(links, session)
        return 0


def echoscraping(link, driver):
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
