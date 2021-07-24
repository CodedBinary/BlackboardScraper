from blackboard import LinkExtractor
import re

class FolderTypeExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Lecture_Recordings", "Content Folder", "Learning Module"]

    def extract(self, session, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("a", href=re.compile("webapp"))["href"]
        bbitem.links += [targeturl + href]
