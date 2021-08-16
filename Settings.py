import getopt
import time
import json
import sys

from enum import IntEnum


usagetext = """BlackboardScraper https://github.com/CodedBinary/BlackboardScraper
Usage: main.py <university login page> [options]

   -d                 : Dry run only, do not download content.
   -v                 : Enable vebose output.
   --lectures         : Allow downloading lectures from echo
   --exclude-filetype : do not download files with this extension (not work)
   """

helptext = """BlackboardScraper https://github.com/CodedBinary/BlackboardScraper

Run main.py with a single argument - your university's login page. After inspecting the source to check it won't send me your password, log in on the instance of chrome that opens. Navigate to the learning resources page of your chosing. Click enter in the terminal. By default, this will download the entire course learning resources, copy all links and text, and DOWNLOAD ALL OF THE LECTURES FROM ECHO. If you don't want to use this feature, read details."""


def exitusage():
    print(usagetext)
    exit(1)


class Download(IntEnum):
    YES = 0
    COPY_ONLY = 1
    AUTH_ONLY = 2
    DO_NOTHING = 3

class Verbosity(IntEnum):
    ERROR = 0
    INFO = 1
    DEBUG = 2


global settings
settings = {
    "dry_run": Download.YES,                # 0 to copy and download; 1 to copy and not download; 2 to not copy or download; 3 to not copy, download, or authenticate
    "item_as_folder": False,                # Determines if Item items will be downloaded into their own folder or not
    "exclude_filetype": [],
    "optstring": "dv",
    "longopts": ["lectures", "exclude-filetype", "cookie-file"],
    "settings_file": "settings.json",
    "download_lectures": False,
    "parse_date_format": "%B %d, %Y",  # July 24, 2018
    "parse_time_format": "%I:%M%p",  # 10:00am
    "write_date_format": "%Y-%m-%d (%A)",
    "write_time_format": "%X",  # locale-specifc default time format
    "save_file_format": "{format_date} {format_time} {stream-name} {name}.{ext}",
    "verbosity": Verbosity.INFO,
    "help_text": "Usage: echo.py -l <login link> -e <echo link>",
    "session_file": "session_cookies"
}

opts, args = getopt.getopt(sys.argv[1:], settings["optstring"], longopts=settings["longopts"])

if not len(args) == 1:
    exitusage()

settings["url"] = args[0]

for opt, arg in opts:

    if opt == "-v":
        settings["verbosity"] = Verbosity.DEBUG

    if opt == "-d":
        settings["dry_run"] = Download.COPY_ONLY

    if opt == "--lectures":
        settings["download"] = True

    if opt == "--exclude-filetype":
        settings["exclude_filetype"] += [arg]

    if opt == "--cookie-file":
        settings["session_file"] = arg
