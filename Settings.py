import getopt
import time
import json

class Settings:
    dry_run = False 
    echo = None

    __instance = None
    _optstring = "dl:e:"

#    _settings = {"dry_run": dry_run}

    @staticmethod
    def get():
        if Settings.__instance == None:
            Settings()
        return Settings.__instance
    
    @classmethod
    def get_opts(self, argv):
        try:
            opts, args = getopt.getopt(argv, self._optstring)
        except getopt.GetoptError:
            print ("Invalid Argument")
            exit(1)

        for opt, arg in opts:
            if opt == "-d":
                self.dry_run = True
        return opts, args
    
    #@classmethod
    #def __getitem__(self, key):
    #    return self.get()._settings[key]
        
    class Echo:
        # Format Codes, See: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        parse_date_format = "%B %d, %Y"             # July 24, 2018
        parse_time_format = "%I:%M%p"               # 10:00am

        write_date_format = "%Y-%m-%d (%A)"         
        write_time_format = "%X"                    # locale-specifc default time format 
        save_file_format = "{format_date} {format_time} {name}.{ext}"

        def __init__(self):
            self.log_file = "download_session_" + str(time.time()) + ".json"
            self.downloads = []

        def _savedownload(self, downloads):
            with open(self.log_file, "w") as out:
                out.write(json.dumps(downloads, indent=4, sort_keys=True))

        def log_download_json(self, meta):
            self.downloads.append(meta)
            #self._savedownload(self.downloads)


    # DO NOT USE
    def __init__ (self):
        if self.__instance != None:
            raise ValueError
        else:
            Settings.__instance = self
            self.echo = self.Echo()