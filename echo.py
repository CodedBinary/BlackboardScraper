import base
import main
import Settings

import copy
import traceback
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import sys
import getopt


def get_bones_from_video(video):
    """
    Get a bone object from every link associated with a lecture recording,
    and set the appropriate attribute data

    @arg a bone dictionary, with an additional "media" attribute containing
        the media information scraped from the website
    Text fields values depends on the website, but the structure should
    mostly stay the same.

    video (dict):

        media (lst)   : A list of dictionaries. Each dictionary
                        corresponds to a single screen/stream you can download.
            stream-name        (str)   : The name of the source. My university uses
                                  "video-one", "video-two", and "audio" for two
                                  video streams and an audio only one.

            contents    (lst)   : A list of the resolution options in the dropdown.
                                  Each option contains a text and value key:
                text    (str)   : Literally just the text in the dropdown box.
                value   (str)   : The url of the download.

        date (str)   : Contains date information
        time (str)    : The time period as shown in echo
        name (str)    : The name of the lecture


    Example:
    {
        'date': 'July 24, 2018',
        'media': [   {   'contents': [   {   'link': 'https://.....mp4',
                                            'text': 'SD 360p - 37.1 MB'},
                                        {   'link': 'https://.....mp4',
                                            'text': 'HD 720p - 82.7 MB'}
                                    ],
                        'stream-name': 'video-one-files'},
                    {   'contents': [   {   'link': 'https://.....mp4',
                                            'text': 'SD 360p - 37.2 MB'},
                                        {   'link': 'https://.....mp4',
                                            'text': 'HD 720p - 147.7 MB'}
                                    ],
                        'stream-name': 'video-two-files'},
                    {   'contents': [   {   'link': 'https://.....mp4',
                                            'text': 'mp3 17022 - 57.9 MB'}
                                    ],
                        'stream-name': 'audio-files'}
                ],
        'name': 'Multivariate Calculus & ODEs : Lecture 1 (Stream 1)-Introduction',
        'time': '10:00am-10:59am'
    }
    @returns a list of bone dictionaries

    """
    bones = []
    for media in video["media"]:
        if 1 == 1:  # Change this to exclude certain downloads
            bone = copy.deepcopy(video)
            bone["type"] = "Lecture_Recordings"
            del bone["media"]
            if "attributes" not in bone.keys():
                bone["attributes"] = {}

            bone["attributes"]["stream-name"] = media["stream-name"]

            for download in media["contents"]:
                thisbone = copy.deepcopy(bone)
                thisbone["attributes"]["res"] = download["text"]
                thisbone["links"] = [download["link"]]
                thisbone["attributes"]["ext"] = download["link"].split(".")[-1]
                thisbone["attributes"]["dest"] = base.get_destinations(thisbone)
                bones.append(thisbone)

    return bones


def video_matches(bone):
    """
    @arg bone: a single bone dict
    @return : True if the bone should be downloaded, False if otherwise
    """

    if ("audio" in bone["attributes"]["stream-name"]):
        return False
    if ("360p" in bone["attributes"]["res"]):
        return False

    return True


def get_echo_videos(driver, metadata):
    '''
    Args:
    driver (???)    : The selenium webdriver
    metadata (dict) : The metadata for the specific lecture that is being downloaded

    Retrieves the echo audio and video links for a given lecture, merges
    metadata from parent function, and downloads file. Requires the driver is
    currently on the download box after clicking the green button.
    '''
    soup = base.loadpage(driver)
    screen = soup.find("div", {"class": "downloadOptions"}).contents

    srcoptions = [{"stream-name": srcoption.find("select")["name"],
                   "contents": [{"link": resoption["value"],
                                 "text": resoption.text}
                                for resoption in srcoption.find_all("option")]}
                  for srcoption in screen if srcoption != "\n"]

    video = metadata  # seems pretty iffy
    video["media"] = srcoptions
    bones = get_bones_from_video(video)

    session = base.cookietransfer(driver)
    for download in bones:
        if not video_matches(download):
            print("Skipping: ", ":::".join([download["name"],
                                            download["attributes"]["stream-name"],
                                            download["attributes"]["res"]]))
            continue
        elif Settings.settings["dry_run"]:
            continue
        else:
            print("Downloading: ", download["name"])
            base.downloadlink(download, session)

            Settings.Echo.log_download_json(download)


def getmetadata(soup):
    ''' Returns the video metadata for an echo page
    '''
    datelist = soup.find_all("span", {"class": "date"})
    datelist = [recorddate.text for recorddate in datelist]

    timelist = soup.find_all("span", {"class": "time"})
    timelist = [recordtime.text for recordtime in timelist]

    namelist = soup.find_all("div", {"class": "class-row"})
    namelist = [recordname.find("header", {"class": "header"}).contents[0].text
                for recordname in namelist]
    metadata = []

    for i in range(len(datelist)):
        start_time = timelist[i].split("-")[0]
        record = {"name": namelist[i],  # lecture title
                  "time": timelist[i],  # time string
                  "date": datelist[i],
                  "attributes": {}}  # attributes specific to the bone type
        rec_date = datetime.min
        rec_time = datetime.min
        try:
            rec_date = datetime.strptime(datelist[i], Settings.echo["parse_date_format"])
        except ValueError as e:
            print("Error parsing date: ", e)
            print(datelist[i])
        try:
            rec_time = datetime.strptime(start_time, Settings.echo["parse_time_format"])
        except ValueError as e:
            print(start_time)
            print("Error parsing time: ", e)
        record["datetime"] = datetime.combine(rec_date.date(), rec_time.time())

        metadata.append(record)

    return metadata


def echoscraping(link, driver):
    ''' Scrapes the given echo page for links and data.
    '''
    print("Starting Echo Scraper")
    driver.get(link)
    time.sleep(2)
    soup = base.loadpage(driver)
    metadata = getmetadata(soup)

    rows = driver.find_elements_by_class_name("class-row")
    for i in range(len(rows)):
        try:
            row = rows[i]
            # Some echo pages have multiple green buttons per row. We need each
            # iteration of the for loop to correspond to a row so the metadata
            # matches up. Afaik, there can only be one actual lecture recording
            # button and it always occurs first, so there isn't a for loop for
            # each button.
            greenbutton = row.find_element_by_class_name("menu-opener")
            ActionChains(driver).move_to_element(greenbutton).perform()
            greenbutton.click()  # Click the green play button
            time.sleep(0.4)

            downloadbutton = driver.find_elements_by_css_selector("a[role='menuitem']")[1]
            ActionChains(driver).move_to_element(downloadbutton).perform()
            downloadbutton.click()
            time.sleep(0.2)

            # We pass the metadata down so get_echo_videos can submit the
            # download itself.
            get_echo_videos(driver, metadata[i])
            # Click the cancel button
            driver.find_element_by_css_selector("a[class='btn white medium']").click()
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            try:
                driver.find_element_by_css_selector("a[class='btn white medium']").click()  # Click the cancel button
            except:
                pass

    return 0


if __name__ == "__main__":
    Settings.Settings.get_opts()
    Settings.Echo.get_opts()

    driver = main.authenticate(Settings.echo["login_link"])
    echoscraping(Settings.echo["echo_link"], driver)
