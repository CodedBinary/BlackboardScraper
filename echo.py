import base
import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

JSON_SAVE_FILE = "download_session_" + str(time.time()) + ".json"
download_later = []


def selectvideo(video):
    '''Used to determine which echo videos are selected for download.

    Args:
    video (dict)
        media (lst)   : A list of dictionaries. Each dictionary
        corresponds to a single screen/stream you can download.
            stream-name        (str)   : The name of the source. My university uses
                                  "video-one", "video-two", and "audio" for two
                                  video streams and an audio only one.

            contents    (lst)   : A list of the resolution options in the dropdown.
                                  Each option contains a text and value key:
                text    (str)   : Literally just the text in the dropdown box.
                value   (str)   : The url of the download.

        date (dict)   : Contains date information
            year    (str) : The year, as yyyy
            montht  (str) : The month, as a name
            monthn  (str) : The month, as mm
            date    (str) : The date, as dd
        time (str)    : The time period as shown in echo
        name (str)    : The name of the lecture


    Return:
        links       (dict)  : A dict of the videos to download.
            res     (str)   : The resolution of the video to download
            links   (lst)   : The url of the video to download in a list
            type    (str)   : The type should always be Lecture_Recordings or
                              an equivalent

   {

   Example:
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
    'name': 'Multivariate Calculus & ODEs : Lecture 1 (Stream 1) -Introduction',
    'time': '10:00am-10:59am'
    }

    '''

    # Select on video
    if ("Set This To Exclude Videos" in video["name"]):
        print("Skipped:", video["name"])
        return []

    links = []

    # Select Media
    for media in video["media"]:
        if 1 == 1:  # Change this to exclude certain downloads
            links.append({
                "res": media["contents"][-1]["text"],  # get the higher res
                "links": [media["contents"][-1]["link"]],  # get the higher res
                "type": "Lecture_Recordings",
                "name": video["name"] + " " + media["stream-name"],
                "time": video["time"],
                "date": video["date"]})

            print(video["name"] + media["stream-name"])
    return links


def savedownload(downloads):
    with open(JSON_SAVE_FILE, "w") as out:
        out.write(json.dumps(downloads, indent=4, sort_keys=True))


def load_json(filename):
    with open(filename, "r") as f:
        return json.loads(f.read())


def getechovideos(driver, metadata):
    '''
    Args:
    driver (???)    : The selenium webdriver
    metadata (dict) : The metadata for the lecture that is being downloaded

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

    video = metadata
    video["media"] = srcoptions

    downloads = selectvideo(video)

    session = base.cookietransfer(driver)
    for download in downloads:
        download_later.append(download)
        print("Downloading: ", download["name"])
        base.downloadlink(download, session)
        savedownload(download_later)


def download_existing(save_file, driver):
    session = base.cookietransfer(driver)
    download_all(load_json(save_file), session)


def echoscraping(link, driver):
    ''' Scrapes the given echo page for links and data.
    '''
    print("Starting Echo Scraper")
    print("Download information will be saved to the file:", JSON_SAVE_FILE)
    driver.get(link)
    time.sleep(2)
    soup = base.loadpage(driver)
    datelist = soup.find_all("span", {"class": "date"})
    timelist = soup.find_all("span", {"class": "time"})
    namelist = soup.find_all("div", {"class": "class-row"})
    datelist = [base.echodateconv(recorddate.text) for recorddate in datelist]
    timelist = [recordtime.text for recordtime in timelist]
    namelist = [recordname.find("header", {"class": "header"}).contents[0].text for recordname in namelist]
    metadata = [  # I'm pretty sure this isnt the way to format it
                {"name": namelist[i],  # lecture title
                 "time": timelist[i],  # time string
                 "date": datelist[i]}  # date dict
                for i in range(len(datelist))]

    for i in range(len(driver.find_elements_by_class_name("class-row"))):
        try:
            row = driver.find_elements_by_class_name("class-row")[i]
            # Some echo pages have multiple green buttons per row. We need each
            # iteration of the for loop to correspond to a row so the metadata
            # matches up. Afaik, there can only be one actual lecture recording
            # button and it always occurs first, so there isn't a for loop for
            # each button.
            greenbutton = row.find_element_by_class_name("menu-opener")
            ActionChains(driver).move_to_element_with_offset(greenbutton, 0, 0).perform()

            greenbutton.click()  # Click the green play button
            time.sleep(0.4)

            downloadbutton = driver.find_elements_by_css_selector("a[role='menuitem']")[1]
            ActionChains(driver).move_to_element(downloadbutton).perform()
            downloadbutton.click()
            time.sleep(0.2)
            # We pass the metadata down so getechovideos can submit the
            # download itself.
            getechovideos(driver, metadata[i])
            # Click the cancel button
            driver.find_element_by_css_selector("a[class='btn white medium']").click()
        except Exception as e:
            print("Error: ", e)
            try:
                driver.find_element_by_css_selector("a[class='btn white medium']").click()  # Click the cancel button
            except:
                pass

    return 0
