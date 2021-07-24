from blackboard import LinkExtractor
import re
import base

class ItemExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Item"]

    def extract(self, session, bbitem, html_bbitem, targeturl):
        bbfiles = html_bbitem.find_all("a", href=re.compile("bbc"))  # Items may not contain a link to download.
        for bbfile in bbfiles:
            link = targeturl + bbfile["href"]
            name = bbfile.text.strip()
            filename = base.get_filename(link, session)
            bbitem.links += [link]
            bbitem.names += [name]
            bbitem.filenames += [filename]
