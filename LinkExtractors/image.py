from blackboard import LinkExtractor
import re

class ImageExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Image"]

    def extract(self, bbitem, html_bbitem, targeturl):
        link = html_bbitem.find("div", class_="vtbegenerated").find("img")["src"]
        bbitem.links += [link]
