from blackboard import LinkExtractor
import re

class FileExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["File"]

    def extract(self, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("a", href=re.compile("bbc"))["href"]
        bbitem.links += [targeturl + href]

