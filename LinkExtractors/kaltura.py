from blackboard import LinkExtractor
import re

class KalturaExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Kaltura Media"]

    def extract(self, session, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("div", {"class": "kalturawrapper"}).find("iframe")["src"]
        bbitem.links += [targeturl + href]
