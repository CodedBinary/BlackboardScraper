from blackboard import LinkExtractor
import re

class WebLinkExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Course Link", "Web Link"]

    def extract(self, session, bbitem, html_bbitem, targeturl):
        link = html_bbitem.find("a", href=re.compile("http"))["href"]
        bbitem.links += [link]
