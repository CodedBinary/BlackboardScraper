from blackboard import BlackboardItem
from blackboard import FolderExtractor
import re
import time
import base

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
