from blackboard import FolderExtractor
from blackboard import BlackboardItem
import base
import time
import re

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
