import base
from blackboard import Downloader
import os

class dfoldertype(Downloader):
    def __init__(self):
        self.provides = ["Content Folder", "Learning Module"]

    def extract(self, downloaders, blackboarditem, session, driver):
        name = base.uniquename(blackboarditem.name)
        os.makedirs(name, exist_ok=True)
        os.chdir(name)
        blackboarditem.downloadfolder(session, downloaders, driver)
        os.chdir("..")
