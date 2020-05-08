import re
from bs4 import BeautifulSoup
import base


def linkextractor(bbitemdict, bblistitem, targeturl):
    '''Extracts relevent links from a block of html in blackboard corresponding to an item

    Args:
    bbitemdict  (dict)  : The dict the items are being extracted into
    bblistitem  (soup)  : The BeautifulSoup object corresponding to the object
    targeturl   (str)   : The domain of the blackboard site. Used to prepend to hrefs.

    Returns:
    bbitemdict (dict)   : The dict with an updated "links" entry
    '''

    if bbitemdict["type"] == "Item":
        bbfiles = bblistitem.find_all("a", href=re.compile("bbc"))  # Items may not contain a link to download.
        for bbfile in bbfiles:
            link = targeturl + bbfile["href"]
            bbitemdict["links"] += [link]

    else:                               # elif isn't used so that bbitemdict["links"] can be assigned [link] uniformly for the rest of the categories
        if bbitemdict["type"] == "File":
            href = bblistitem.find("a", href=re.compile("bbc"))["href"]
            link = targeturl + href

        elif bbitemdict["type"] == "Kaltura Media":
            href = bblistitem.find("div", {"class": "kalturawrapper"}).find("iframe")["src"]
            link = targeturl + href

        elif bbitemdict["type"] == "Course Link":
            link = bblistitem.find("a", href=re.compile("http"))["href"]

        elif bbitemdict["type"] == "Web Link":
            link = bblistitem.find("a", href=re.compile("http"))["href"]

        elif bbitemdict["type"] == "Lecture_Recordings":
            href = bblistitem.find("a", href=re.compile("webapp"))["href"]
            link = targeturl + href

        elif bbitemdict["type"] == "Content Folder":
            href = bblistitem.find("a", href=re.compile("webapp"))["href"]
            link = targeturl + href

        else:
            print("WARNING: UNKNOWN OBJECT TYPE DETECTED", bbitemdict["type"])

        bbitemdict["links"] += [link]

    return bbitemdict


def copystructure(folder, driver, targeturl):
    '''Recursively copies the structure and links of a blackboard folder

    Args:
    folder  (dict)  : The root folder to copy. Should be initialised with a type, name, and desired link.
    driver  (lmao)  : The instance of the selenium driver to be used

    Return:
    folder  (dict)      : The recursive structure of the folder.

    Object Structure:
        name (str)      : The name of the object. Eg Week 1, Midsemester Exam
        text (str)      : The text below the title as a string of the html.
        links (lst)     : A list of urls contained in the object.
        type (str)      : The type of object. Eg Course Link, Web Link, Item. These correspond to the pictograms on the left of each object when you visit the blackboard page. To check what each one means, inspect the html of the pictogram and look at the "alt" attribute.
        content (lst)   : A list of objects contained within this object. Only valid for folders.

    '''
    # copystructure will be called on regular items and such by recursion. It should simply return the item if it is not a folder
    if folder["type"] != "Content Folder":
        return folder

    # We are using a list for the directory structure instead of a dict because we can have duplicate names and urls are ugly
    contentlist = []
    driver.get(folder["links"][0])
    soup = base.loadpage(driver)

    try:                # empty folders can fuck shit up
        contents = [x for x in soup.find("ul", {"id": "content_listContainer"}).contents if x != "\n"]
    except AttributeError:  # TOM: This way non intended shit that fucks up can be detected.
        contents = []

    for bblistitem in contents:
        # bblistitem corresponds to the html of one item in a blackboard page. For example, the Week 1 folder, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.
        # bbitemdict stores the extracted information of bblistitem. It isn't stored as a class because its easier to export this and we are only storing data in it.
        bbitemdict = {
                "name": bblistitem.find("h3").find("span", style=re.compile("")).text,
                "links": [],
                "type": bblistitem.img["alt"],
                "text": str(bblistitem.find("div", {"class": "vtbegenerated"})),
                "content": []
                }

        bbitemdict = linkextractor(bbitemdict, bblistitem, targeturl)

        contentlist += [bbitemdict]
    folder["content"] = [copystructure(x, driver, targeturl) for x in contentlist]     # Stores the contents of the folder under the key contents
    return folder
