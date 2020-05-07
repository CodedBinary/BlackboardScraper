from bs4 import BeautifulSoup


def loadpage(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup
