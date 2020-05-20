from bs4 import BeautifulSoup
import os
import time
import requests


def echodateconv(echodate):
    textdates = echodate.split()
    months = ["Placeholder", "January", "February", "March", "April",
              "May", "June", "July", "August", "September", "October",
              "November", "December"]
    date = {
            "year": str(textdates[2]),
            "montht": textdates[0],
            "monthn": str(months.index(textdates[0])),
            "date": str(textdates[1][:-1])
            }

    if len(date["date"]) < 2:
        date["date"] = 0 + date["date"]

    if len(date["monthn"]) < 2:
        date["monthn"] = 0 + date["monthn"]
    return date


def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def getnames(bone, downloads):
    ''' Generates a name for the downloads in a bone. Names need not be unique.
    Args:
        bone     (dict): Has the same keys as shown in blackboard.py
        downloads (lst): Contains the requests object obtained by downloading
                         the links
    '''
    if bone["type"] == "Lecture_Recordings":
        dates = bone["date"]
        return [dates["year"]+dates["monthn"]+dates["date"]
                +","+bone["time"]+","+bone["name"]+bone["res"]+"."
                +bone["links"][0].split(".")[-1]]
    else:
    #   return [bone["name"] for x in bone["links"]]
        return [x.split("/")[-1] for x in bone["links"]]


def uniquename(originalname):
    ''' Generates a unique name for a file, given a suggested name.
    '''
    name = originalname

    j = 2
    while os.path.exists(name):     # Add options for changing this format?
        name = originalname.rsplit(".", 1)[0] + "(" + str(j) + ")" + originalname.split(".")[-1]
        j += 1
    return name


def downloadok(bone, url):
    return 1


def downloadlink(bone, session):
    ''' Downloads the links in the bone using the current session.

    To see the structure of the bone, check out blackboard.py
    '''
    downloads = [session.get(url) for url in bone["links"] if downloadok(bone, url) == 1]

    nameslist = getnames(bone, downloads)

    for i in range(len(downloads)):
        name = uniquename(nameslist[i])

        open(name, 'wb').write(downloads[i].content)
    time.sleep(1)
    return 0


def cookietransfer(driver):
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
