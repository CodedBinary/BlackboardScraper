import re
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

    def copystructure(self, driver, targeturl, extractors):
        '''Recursively copies the structure and links of a blackboard folder. The blackboard folder is specified with self.links[0]

        Args:
        self  (BlackboardItem)  : The root folder to copy. Should be initialised with a type, name, and desired link.
        driver (????)           : The instance of the selenium driver to be used
        targeturl (str)         : The url to prepend to any relevant hrefs
        extractors (dict)       : A dict of extractors, with keys "folder", "content", "link", with values each a list of extractors
        '''
        for folderextractor in extractors["folder"]:
            if self.type in folderextractor.provides:
                folderextractor.extract(self, driver, targeturl, self.links[0], extractors)
                break

    def linkextractor(self, html_bbitem, targeturl, extractors):
        '''Extracts relevent links from a block of html in blackboard in to a blackboarditem

        Args:
        html_bbitem  (soup)  : The BeautifulSoup object corresponding to the object
        targeturl   (str)   : The domain of the blackboard site. Used to prepend to hrefs.
        '''
        extracted = False
        for extractor in extractors["link"]:
            if self.type in extractor.provides:
                extractor.extract(self, html_bbitem, targeturl)
                extracted = True
                break

        if self.type in ["module_treeNode", "module_html page", "module_downloadable content"]:
            # ONLY FOR DOCUMENTATION
            print("ERROR: This should not occur. Ref 132131")
            print(self.type)

        if not extracted:
            print("WARNING: UNKNOWN OBJECT TYPE DETECTED", self.type)
            print("This item will be skipped, and not recorded.")

class LinkExtractor():
    '''
    Takes an html block (of a certain type of object) and returns an appropriate link. There should be a LinkExtractor that can handle any type of html that occurs on the blackboard page.
    '''
    def __init__(self):
        self.provides = []

    def extract(self, bbitem, html_bbitem, targeturl):
        pass

class ItemExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Item"]

    def extract(self, bbitem, html_bbitem, targeturl):
        bbfiles = html_bbitem.find_all("a", href=re.compile("bbc"))  # Items may not contain a link to download.
        for bbfile in bbfiles:
            link = targeturl + bbfile["href"]
            filename = bbfile.text.strip()
            bbitem.links += [link]
            bbitem.names += [filename]

class FileExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["File"]

    def extract(self, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("a", href=re.compile("bbc"))["href"]
        bbitem.links += [targeturl + href]

class WebLinkExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Course Link", "Web Link"]

    def extract(self, bbitem, html_bbitem, targeturl):
        link = html_bbitem.find("a", href=re.compile("http"))["href"]
        bbitem.links += [link]

class FolderTypeExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Lecture_Recordings", "Content Folder", "Learning Module"]

    def extract(self, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("a", href=re.compile("webapp"))["href"]
        bbitem.links += [targeturl + href]

class KalturaExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Kaltura Media"]

    def extract(self, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("div", {"class": "kalturawrapper"}).find("iframe")["src"]
        bbitem.links += [targeturl + href]

class ImageExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Image"]

    def extract(self, bbitem, html_bbitem, targeturl):
        link = html_bbitem.find("div", class_="vtbegenerated").find("img")["src"]
        bbitem.links += [link]

class FolderExtractor():
    '''
    Extracts the contents of a folder-type object.

    Must have a "provides" attribute that contains a list of the valid folder-type objects it can handle.

    Must have an "extract" method, accepting an item to extract the contents of, the driver, the targeturl, and the link, that will recursively add all of the children of the given item to its content attribute.
    '''

    def __init__(self):
        self.provides = []

    def extract(self, bbitem, driver, targeturl, link):
        '''
        bbitem (BlackboardItem) : The folder to extract the contents in to
        driver                  : The instance of a selenium driver to use
        targeturl               : The url to use for prepending to hrefs
        link                    : The link of the blackboard folder to extract
        '''
        pass

class CFExtractor(FolderExtractor):
    def __init__(self):
        self.provides = ["Content Folder"]

    def convertHtmlToItem(self, html_bbitem, targeturl, extractors):
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

        bbitem.linkextractor(html_bbitem, targeturl, extractors)
        return bbitem

    def extract(self, bbitem, driver, targeturl, link, extractors):
        '''
        bbitem (BlackboardItem) : The folder to extract the contents in to
        driver                  : The instance of a selenium driver to use
        targeturl               : The url to use for prepending to hrefs
        link                    : The link of the blackboard folder to extract
        '''
        # We are using a list for the directory structure instead of a dict because we can have duplicate names and urls are ugly
        print(bbitem.name)
        driver.get(link)
        time.sleep(1)
        soup = base.loadpage(driver)

        try:                # empty selfs can fuck shit up
            contents = [x for x in soup.find("ul", {"id": "content_listContainer"}).contents if x != "\n"]
        except AttributeError:  # TOM: This way non intended shit that fucks up can be detected.
            contents = []

        for html_bbitem in contents:
            # html_bbitem corresponds to the html of one item in a blackboard page. For example, the Week 1 self, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.
            child = self.convertHtmlToItem(html_bbitem, targeturl, extractors)
            bbitem.content += [child]

        for child in bbitem.content:
            child.copystructure(driver, targeturl, extractors)


class LMExtractor(FolderExtractor):
    def __init__(self):
        self.provides = ["Learning Module"]

    def deeplinkextractor(self, bbitem, html_bbitem, targeturl, extractors):
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
            bbitem.linkextractor(file, targeturl, extractors)
        elif item is not None:
            bbitem.type = "Item"
            bbitem.linkextractor(item, targeturl)
        else:
            # Potentially a text file, potentially not.
            bbitem.type = "module_html page"
            content = html_bbitem.find("div", {"id": "containerdiv"})
            bbitem.text = content.text + "\n" + str(content)

    def convertHtmltoItem(self, driver, html_bbitem, targeturl, extractors):
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
            self.deeplinkextractor(bbitem, subitem_html, targeturl, extractors)

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

    def extract(self, bbitem, driver, targeturl, link, extractors):
        driver.get(link)
        time.sleep(1)
        soup = base.loadpage(driver)

        try:                # empty selfs can fuck shit up
            treecontainer = soup.find("div", {"class": "treeContainer"})
            contents = [x for x in treecontainer.find_all("li", id=re.compile("_"))]
        except AttributeError:  # TOM: This way non intended shit that fucks up can be detected.
            contents = []

        for html_bbitem in contents:
            # html_bbitem corresponds to the html of one item in a blackboard page. For example, the Week 1 self, the Workbook item, or the course link that links to edge. It includes the entire box around the link you click.
            child = self.convertHtmlToItem(html_bbitem, targeturl, extractors)
            bbitem.content += [child]

        for child in bbitem.content:
            child.copystructure(driver, targeturl, extractors)
