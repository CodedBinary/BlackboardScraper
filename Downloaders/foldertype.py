import base
from blackboard import Downloader
import os

class foldertype(Downloader):
    def __init__(self):
        self.provides = ["Content Folder", "Learning Module"]

    def download(self, downloaders, blackboarditem, session, driver):
        name = base.uniquename(blackboarditem.name)
        os.mkdir(name)
        os.chdir(name)
        blackboarditem.downloadfolder(downloaders, driver)
        os.chdir("..")
