import re
from bs4 import BeautifulSoup
import base
import time


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

        elif bbitem.type == "Learning Module":
            href = html_bbitem.find("a", href=re.compile("webapp"))["href"]
            link = targeturl + href

        elif bbitem.type == "Image":
            link = html_bbitem.find("div", class_="vtbegenerated").find("img")["src"]

        elif bbitem.type in ["module_treeNode", "module_html page", "module_downloadable content"]:
            # ONLY FOR DOCUMENTATION
            print("ERROR: This should not occur. Ref 132131")
            print(bbitem.type)

        else:
            print("WARNING: UNKNOWN OBJECT TYPE DETECTED", bbitem.type)
            print("This item will be skipped, and not recorded.")
            fucked = 1

        if fucked != 1:
            bbitem.links += [link]

def deeplinkextractor(bbitem, html_bbitem, targeturl):
    '''
    When scraping Learning Modules, accesses each content item, and extracts the links. Differs from linkextractor because linkextractor does not access the link of the item, whereas this does.

    Args:
    bbitem  (BlackboardItem)  : The object the items are being extracted into
    html_bbitem  (soup)  : The BeautifulSoup object corresponding to the object. Note this is usually a new webpage.
    targeturl   (str)   : The domain of the blackboard site. Used to prepend to hrefs.
    '''

    item = html_bbitem.find("ul", class_="attachments clearfix")
    file = html_bbitem.find("div", class_="item clearfix")

    # If the contents of the module_treeNode look like a "File":
    if file is not None:
        bbitem.type = "File"
        linkextractor(bbitem, file, targeturl)
    elif item is not None:
        bbitem.type = "Item"
        linkextractor(bbitem, item, targeturl)
    else:
        # Potentially a text file, potentially not.
        bbitem.type = "module_html page"
        content = html_bbitem.find("div", {"id": "containerdiv"})
        bbitem.text = content.text + "\n" + str(content)


def determine_folder_html_bbitem(html_bbitem, targeturl):
    '''
    Constructs a BlackboardItem object from the html of an element of a Content Folder

    Args:
        html_bbitem (beautifulsoup): the html of an element of a Content Folder
        targeturl (str): the url, used for prepending hrefs
    Returns:
        bbitem (BlackboardItem): the information pertaining to that without html
    '''
    bbitem = BlackboardItem()
    bbitem.name = html_bbitem.find("h3").find("span", style=re.compile("")).text
    bbitem.type = html_bbitem.img["alt"]
    bbitem.text = str(html_bbitem.find("div", {"class": "vtbegenerated"}))

    linkextractor(bbitem, html_bbitem, targeturl)
    
    return bbitem

def determine_module_html_bbitem(html_bbitem, targeturl):
    '''
    Constructs a BlackboardItem object from the html of an element of a Learning Module

    Args:
        html_bbitem (beautifulsoup): the html of an element of a Content Folder
        targeturl (str): the url, used for prepending hrefs
    Returns:
        bbitem (BlackboardItem): the information pertaining to that without html
    '''
    bbitem = BlackboardItem()
    baseitem = html_bbitem.find("a", class_=re.compile("tocItem"))
    bbitem.name = baseitem.text
    bbitem.type = "module_treeNode"

    urlinfo = baseitem["onclick"]
    url = re.search('\(([^)]+)', urlinfo).group(1).strip()[1:-1]
    url = targeturl + url

    session = base.cookietransfer(driver)
    response = session.get(url, allow_redirects=False)

    if response.status_code == 200:
        driver.get(url)
        subitem_html = base.loadpage(driver)
        deeplinkextractor(bbitem, subitem_html, targeturl)

    elif response.status_code == 302:
        bbitem.type = "module_downloadable content"
        baseurl = url[url.index('execute')+7:]
        courseid = re.search("course_id.*?&", url).group()[10:-1]
        contentid = re.search("content_id.*?&", url).group()[11:-1]
        url = baseurl + "/content/file?cmd=view&content_id=" + contentid + "&course_id=" + courseid
        bbitem.links = [url]
    else:
        print("Error: Unexpected response url.")

    return bbitem

def copystructure(folder, driver, targeturl):
    '''Recursively copies the structure and links of a blackboard folder

    Args:
    folder  (BlackboardItem)  : The root folder to copy. Should be initialised with a type, name, and desired link.
    driver  (????)  : The instance of the selenium driver to be used
    '''

    if folder.type == "Content Folder":
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
            bbitem = determine_folder_html_bbitem(html_bbitem, targeturl)

            contentlist += [bbitem]
        folder.content = [copystructure(x, driver, targeturl) for x in contentlist]     # Stores the contents of the folder under the key contents
        return folder

    elif folder.type == "Learning Module":
        contentlist = []
        driver.get(folder.links[0])
        time.sleep(1)
        soup = base.loadpage(driver)

        try:                # empty folders can fuck shit up
            treecontainer = soup.find("div", {"class": "treeContainer"})
            contents = [x for x in treecontainer.find_all("li", id=re.compile("_"))]
        except AttributeError:  # TOM: This way non intended shit that fucks up can be detected.
            contents = []

        for html_bbitem in contents:
            # html_bbitem corresponds to the html of one item in a blackboard page. For example, the Week 1 folder, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.
            bbitem = determine_module_html_bbitem(html_bbitem, targeturl)
            contentlist += [bbitem]

        folder.content = [copystructure(x, driver, targeturl) for x in contentlist]     # Stores the contents of the folder under the key contents
        return folder
    else:
        # copystructure will be called on regular items and such by recursion. It should simply return the item if it is not a folder
        return folder
