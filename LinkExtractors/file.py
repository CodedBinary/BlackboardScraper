from blackboard import LinkExtractor
import base
import re

class FileExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["File"]

    def extract(self, session, bbitem, html_bbitem, targeturl):
        href = html_bbitem.find("a", href=re.compile("bbc"))["href"]
        link = targeturl + href
        bbitem.links += [link]

        filename = base.get_filename(link, session)
        bbitem.filenames += [filename]
