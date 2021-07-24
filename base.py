from bs4 import BeautifulSoup
import os
import time
import requests
from urllib.parse import unquote


def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def get_filename(link, session):
    '''
    Determines the name of a file that is specified by a blackboard cdn link
    '''
    response = session.head(link, allow_redirects=False)
    if "Location" in response.headers:
        href = response.headers["Location"]
        filename = unquote(href.split("/")[-1])
        return filename
    else:
        return ""

def get_destinations(blackboarditem, session=None):
    ''' Generates a name for the files in a blackboarditem that could be downloaded. Names need not be unique.
    Args:
        blackboarditem     (BlackboardItem):
        downloads (lst): Contains the requests object obtained by downloading the links
        session         : Optional requests session, which can be used to observe the true filename (without downloading the file)
    '''

    if blackboarditem.filenames != []:
        return blackboarditem.filenames

    if session is not None and blackboarditem.filenames == []:
        names = []
        for link in blackboarditem.links:
            names += [get_filename(link, session)]
        return names

    if blackboarditem.type == "Lecture_Recordings":
        return [blackboarditem.name + str(blackboarditem.date)]
    elif blackboarditem.type == "Item":
        return blackboarditem.names
    elif blackboarditem.type in ["File", "module_downloadable content"]:
        return [blackboarditem.name]
    else:
        return [x.split("/")[-1] for x in blackboarditem.links]


def uniquename(originalname):
    ''' Generates a name for a file that isn't taken already, given a suggested name.
    '''
    name = originalname
    if os.path.exists(name):
        # otherwise replace the name(1).extention
        # requires the file has an extension
        if ("." not in name):
            name = name + "(1)"  # Unary counting lets go
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


def downloadok(blackboarditem, url):
    return 1


def downloadlink(blackboarditem, session):
    ''' Downloads the links in the blackboarditem using the current session.

    To see the structure of the blackboarditem, check out blackboard.py
    '''
    downloads = [session.get(url, allow_redirects=True) for url in blackboarditem.links if downloadok(blackboarditem, url) == 1]

    nameslist = get_destinations(blackboarditem, session=session)

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
