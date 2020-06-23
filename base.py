from bs4 import BeautifulSoup
import os
import time
import requests
from datetime import datetime
import Settings


def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def get_destinations(bone):
    ''' Generates a name for the downloads in a bone. Names need not be unique.
    Args:
        bone     (dict): Has the same keys as shown in blackboard.py
        downloads (lst): Contains the requests object obtained by downloading
                         the links
    '''

    if bone["type"] == "Lecture_Recordings":
        format_strings = bone
        format_strings.update(bone["attributes"])
        format_strings["format_date"] = datetime.strftime(bone["datetime"], Settings.echo["write_date_format"])
        format_strings["format_time"] = datetime.strftime(bone["datetime"], Settings.echo["write_time_format"])

        # return [dates["year"]+dates["monthn"]+dates["date"]+","+bone["time"]+","+bone["name"]+bone["res"]+"."+bone[
        # "links"][0].split(".")[-1]]
        return [Settings.echo["save_file_format"].format(**format_strings)]
    elif bone["type"] == "Item":
        return bone["names"]
    else:
        #   return [bone["name"] for x in bone["links"]]
        return [x.split("/")[-1] for x in bone["links"]]


def uniquename(originalname):
    ''' Generates a unique name for a file, given a suggested name.
    '''
    similar = []
    name = originalname
    if os.path.exists(name):
        # otherwise replace the name(1).extention
        # requires the file has an extension
        if ("." not in name):
            name = name + "(1)"
        else:
            name = ".".join(name.split(".")[:-1]) + "(1)." + name.split(".")[-1]
        i = 2
        while os.path.exists(name):
            substr = f"({i - 1})"
            ind = name.rfind(substr)
            name = name[0:ind] + f"({i})" + name[ind + 3:]
            i += 1
        return name
    else:
        return name


def downloadok(bone, url):
    return 1


def downloadlink(bone, session):
    ''' Downloads the links in the bone using the current session.

    To see the structure of the bone, check out blackboard.py
    '''
    downloads = [session.get(url, allow_redirects=True) for url in bone["links"] if downloadok(bone, url) == 1]

    nameslist = get_destinations(bone)

    for i in range(len(downloads)):
        name = uniquename(nameslist[i])

        open(name, 'wb').write(downloads[i].content)
    time.sleep(1)
    return 0


def cookietransfer(driver):
    # TODO: Add support for pickling session cookies

    ''' Transfers cookies from the driver into a requests session.

    Args:
    driver  (???) : An instance of a selenium webdriver

    Return:
    session (???) : An instance of a requests session

    Allows requests to authenticate using the browser's cookies.
    '''
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session
