from bs4 import BeautifulSoup
import time
import requests


def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def downloadlink(bone, session):
    ''' Downloads the links in the bone using the current session.

    To see the structure of the bone, check out blackboard.py
    '''
    myfiles = bone["links"]
    for myfile in myfiles:
        download = session.get(myfile)
        open(bone["name"], 'wb').write(download.content)  # Duplicate names??
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
