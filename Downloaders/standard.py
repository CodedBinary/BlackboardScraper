import os
import base
from blackboard import Downloader
import Settings

class standard(Downloader):
    def __init__(self):
        self.provides = ["File", "Image", "module_treeNode", "module_downloadable content", "module_html page"]

    def extract(self, downloaders, blackboarditem, session, driver):
        base.downloadlink(blackboarditem, session)
        if str(blackboarditem.text) != "None" and Settings.settings["write_text_files"]:
            try:
                name = base.uniquename(blackboarditem.name)
                open(name, 'w').write(blackboarditem.text)
            except:
                pass

class item(standard):
    def __init__(self):
        self.provides = ["Item"]

    def extract(self, downloaders, blackboarditem, session, driver):
        if Settings.settings["item_as_folder"]:
            name = base.uniquename(blackboarditem.name)
            os.mkdir(name)
            os.chdir(name)
            standard.extract(self, downloaders, blackboarditem, session, driver)
            os.chdir("..")
        else:
            standard.extract(self, downloaders, blackboarditem, session, driver)
