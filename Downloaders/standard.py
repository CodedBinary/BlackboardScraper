import base
from blackboard import Downloader

class standard(Downloader):
    def __init__(self):
        self.provides = ["File", "Item", "Image", "module_treeNode", "module_downloadable content", "module_html page"]

    def extract(self, downloaders, blackboarditem, session, driver):
        base.downloadlink(blackboarditem, session)
        if str(blackboarditem.text) != "None":
            try:
                name = base.uniquename(blackboarditem.name)
                open(name, 'w').write(blackboarditem.text)
            except:
                pass
