import re
from bs4 import BeautifulSoup
import base


class BlackboardItem():
    '''
        name (str)      : The name of the object. Eg Week 1, Midsemester Exam
        names (lst)     : The names of the downloadable content in an "Item"
        text (str)      : The text below the title as a string of the html.
        links (lst)     : A list of urls contained in the object.
        type (str)      : The type of object. Eg Course Link, Web Link, Item. These correspond to the pictograms on the left of each object when you visit the blackboard page. To check what each one means, inspect the html of the pictogram and look at the "alt" attribute.
        content (lst)   : A list of objects contained within this object. Only valid for folders.
    '''
    def __init__(self):
        self.name = ""
        self.names = []
        self.text = ""
        self.links = []
        self.type = ""
        self.content = []

def linkextractor(bbitem, html_bbitem, targeturl):
    '''Extracts relevent links from a block of html in blackboard in to a blackboarditem

    Args:
    bbitem  (BlackboardItem)  : The object the items are being extracted into
    html_bbitem  (soup)  : The BeautifulSoup object corresponding to the object
    targeturl   (str)   : The domain of the blackboard site. Used to prepend to hrefs.
    '''

    fucked = 0
    if bbitem.type == "Item":
        bbfiles = html_bbitem.find_all("a", href=re.compile("bbc"))  # Items may not contain a link to download.
        for bbfile in bbfiles:
            link = targeturl + bbfile["href"]
            filename = bbfile.text.strip()
            bbitem.links += [link]
            bbitem.names += [filename]

    else:                               # elif isn't used so that bbitem.links can be assigned [link] uniformly for the rest of the categories
        if bbitem.type == "File":
            href = html_bbitem.find("a", href=re.compile("bbc"))["href"]
            link = targeturl + href

        elif bbitem.type == "Kaltura Media":
            href = html_bbitem.find("div", {"class": "kalturawrapper"}).find("iframe")["src"]
            link = targeturl + href

        elif bbitem.type == "Course Link":
            link = html_bbitem.find("a", href=re.compile("http"))["href"]

        elif bbitem.type == "Web Link":
            link = html_bbitem.find("a", href=re.compile("http"))["href"]

        elif bbitem.type == "Lecture_Recordings":
            href = html_bbitem.find("a", href=re.compile("webapp"))["href"]
            link = targeturl + href

        elif bbitem.type == "Content Folder":
            href = html_bbitem.find("a", href=re.compile("webapp"))["href"]
            link = targeturl + href

        elif bbitem.type == "Image":
            link = html_bbitem.find("div", class_="vtbegenerated").find("img")["src"]

        else:
            print("WARNING: UNKNOWN OBJECT TYPE DETECTED", bbitem.type)
            print("This item will be skipped, and not recorded.")
            fucked = 1

        if fucked != 1:
            bbitem.links += [link]


def copystructure(folder, driver, targeturl):
    '''Recursively copies the structure and links of a blackboard folder

    Args:
    folder  (BlackboardItem)  : The root folder to copy. Should be initialised with a type, name, and desired link.
    driver  (????)  : The instance of the selenium driver to be used
    '''
    # copystructure will be called on regular items and such by recursion. It should simply return the item if it is not a folder
    if folder.type != "Content Folder":
        return folder

    # We are using a list for the directory structure instead of a dict because we can have duplicate names and urls are ugly
    contentlist = []
    driver.get(folder.links[0])
    soup = base.loadpage(driver)

    try:                # empty folders can fuck shit up
        contents = [x for x in soup.find("ul", {"id": "content_listContainer"}).contents if x != "\n"]
    except AttributeError:  # TOM: This way non intended shit that fucks up can be detected.
        contents = []

    for html_bbitem in contents:
        # html_bbitem corresponds to the html of one item in a blackboard page. For example, the Week 1 folder, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.
        # bbitem stores the extracted information of html_bbitem.
        bbitem = BlackboardItem()
        bbitem.name = html_bbitem.find("h3").find("span", style=re.compile("")).text
        bbitem.type = html_bbitem.img["alt"]
        bbitem.text = str(html_bbitem.find("div", {"class": "vtbegenerated"}))
        linkextractor(bbitem, html_bbitem, targeturl)

        contentlist += [bbitem]
    folder.content = [copystructure(x, driver, targeturl) for x in contentlist]     # Stores the contents of the folder under the key contents
    return folder
