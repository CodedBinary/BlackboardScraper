from blackboard import LinkExtractor
import re

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
