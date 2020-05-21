import getopt
import time
import json
import sys

global_defaults = {
    "dry_run": False,
    "optstring": "dl:e:",
    "settings_file": "settings.json"
}

echo_defaults = {
    "parse_date_format": "%B %d, %Y",  # July 24, 2018
    "parse_time_format": "%I:%M%p",  # 10:00am
    "write_date_format": "%Y-%m-%d (%A)",
    "write_time_format": "%X",  # locale-specifc default time format
    "save_file_format": "{format_date} {format_time} {stream-name} {name}.{ext}",
    "help_text": "Usage: echo.py -l <login link> -e <echo link>"
}

settings = global_defaults
echo = echo_defaults

echo_downloads = []

class Echo:
    """
    Settings Specific to the Echo Downloader
    """

    # Format Codes, See: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

    @staticmethod
    def get_opts():
        global echo
        try:
            opts, args = getopt.getopt(sys.argv[1:], settings["optstring"])
        except getopt.GetoptError:
            print(echo["help_text"])
            exit(1)

        loaded = {}
        done = 0
        for opt, arg in opts:
            if opt == '-l':
                loaded["login_link"] = arg
                done += 1
            if opt == "-e":
                loaded["echo_link"] = arg
                done += 1
        if done < 2:
            print(echo["help_text"])
            exit(1)

        echo.update(loaded)

    def __init__(self):
        global echo
        echo["log_file"] = "download_session_" + str(time.time()) + ".json"
        self.downloads = []

    @staticmethod
    def _savedownload(downloads):
        with open(echo["log_file"], "w") as out:
            out.write(json.dumps(downloads, indent=4, sort_keys=True))

    @staticmethod
    def log_download_json(meta):
        global echo_downloads
        echo_downloads.append(meta)
        # self._savedownload(__echo_downloads)


class Settings:
    """
    Global Program Settings
    """

    @staticmethod
    def get_opts():
        global settings
        try:
            opts, args = getopt.getopt(sys.argv[1:], settings["optstring"])
        except getopt.GetoptError:
            print("Invalid Argument")
            exit(1)

        loaded = {}
        for opt, arg in opts:
            if opt == "-d":
                loaded["dry_run"] = True
        settings.update(loaded)

    @staticmethod
    def load_json(self):
        global settings
        with open(settings["settings_file"], "r") as settings_file:
            loaded = json.loads(settings_file.read())
            settings.update(loaded)
