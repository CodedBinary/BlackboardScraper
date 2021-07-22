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

    def copystructure(self, driver, targeturl, extractors):
        '''Recursively copies the structure and links of a blackboard folder. The blackboard folder is specified with self.links[0]

        Args:
        self  (BlackboardItem)  : The root folder to copy. Should be initialised with a type, name, and desired link.
        driver (????)           : The instance of the selenium driver to be used
        targeturl (str)         : The url to prepend to any relevant hrefs
        extractors (dict)       : A dict of extractors, with keys "folder", "content", "link", with values each a list of extractors
        '''
        if self.type not in [y for x in extractors["folder"]+extractors["link"] for y in x.provides]:
            print("ERROR: TYPE NOT RECOGNISED")

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

    def downloadfolder(self, downloaders, driver, lectures=False):
        '''
        Downloads the content in a BlackboardItem's contents. Should be a Content Folder or a Learning Module.
        '''
        session = base.cookietransfer(driver)
        session.headers['User-Agent'] = 'Mozilla/5.0'
        for blackboarditem in self.content:
            downloaded = False
            for downloader in downloaders:
                if blackboarditem.type in downloader.provides and blackboarditem.type != "Lecture_Recordings":
                    downloader.download(downloaders, blackboarditem, session, driver)
                    downloaded = True
                    break
            if not downloaded:
                print("Warning: Unknown listitem type detected. Type", blackboarditem.type)

class LinkExtractor():
    '''
    Takes an html block (of a certain type of object) and returns an appropriate link. There should be a LinkExtractor that can handle any type of html that occurs on the blackboard page.
    '''
    def __init__(self):
        self.provides = []

    def extract(self, bbitem, html_bbitem, targeturl):
        pass

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

class Downloader():
    '''
    Downloads a given BlackboardItem
    '''
    def __init__(self):
        self.provides = []

    def download(self, downloaders, blackboarditem, session, driver):
        pass
