import getopt
import time
import json
import sys

global settings
settings = {
    "dry_run": 0,                           # 0 to copy and download; 1 to copy and not download; 2 to not copy or download; 3 to not copy, download, or authenticate
    "item_as_folder": False,                # Determines if Item items will be downloaded into their own folder or not
    "exclude_filetype": [],
    "optstring": "d",
    "longopts": ["lectures", "exclude-filetype="],
    "settings_file": "settings.json",
    "download_lectures": False,
    "parse_date_format": "%B %d, %Y",  # July 24, 2018
    "parse_time_format": "%I:%M%p",  # 10:00am
    "write_date_format": "%Y-%m-%d (%A)",
    "write_time_format": "%X",  # locale-specifc default time format
    "save_file_format": "{format_date} {format_time} {stream-name} {name}.{ext}",
    "help_text": "Usage: echo.py -l <login link> -e <echo link>"
}

opts, args = getopt.getopt(sys.argv[1:], settings["optstring"], longopts=settings["longopts"])

settings["url"] = args[0]

for opt, arg in opts:
    if opt == "-d":
        settings["dry_run"] += 1

    if opt == "--lectures":
        settings["download"] = True

    if opt == "--exclude-filetype":
        settings["exclude_filetype"] += [arg]
