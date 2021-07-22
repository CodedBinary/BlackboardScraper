import base
from blackboard import Downloader

class misc(Downloader):
    def __init__(self):
        self.provides = ["Kaltura Media", "Web Link", "Course Link"]

    def download(self, downloaders, blackboarditem, session, driver):
        name = base.uniquename(blackboarditem.name)
        open(name, 'w').write(blackboarditem.links[0] + "\n" + blackboarditem.text)
