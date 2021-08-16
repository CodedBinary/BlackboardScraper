from blackboard import LinkExtractor
import re
import base

class ItemExtractor(LinkExtractor):
    def __init__(self):
        self.provides = ["Item"]

    def extract(self, session, bbitem, html_bbitem, targeturl):
        bbfiles = html_bbitem.find_all("a", href=re.compile(f"{targeturl}.*bbcswebdav.*"))  # Only download webdav links to internal documents
        for bbfile in bbfiles:
            link = bbfile["href"]
            name = bbfile.text.strip()
            filename = base.get_filename(link, session)
            bbitem.links += [link]
            bbitem.names += [name]
            bbitem.filenames += [filename]
