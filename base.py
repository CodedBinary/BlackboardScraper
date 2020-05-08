from bs4 import BeautifulSoup
import requests


def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def downloadlink(bone, session):
    myfiles = bone["links"]
    for myfile in myfiles:
        download = session.get(myfile)
        open(bone["name"], 'wb').write(download.content)  # Duplicate names??
    return 0


def cookietransfer(driver):
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return session
