import getopt
import time
import json
import sys

global settings
settings = {
    "dry_run": False,
    "optstring": "dl:e:",
    "settings_file": "settings.json",
    "download_lectures": False,
    "parse_date_format": "%B %d, %Y",  # July 24, 2018
    "parse_time_format": "%I:%M%p",  # 10:00am
    "write_date_format": "%Y-%m-%d (%A)",
    "write_time_format": "%X",  # locale-specifc default time format
    "save_file_format": "{format_date} {format_time} {stream-name} {name}.{ext}",
    "help_text": "Usage: echo.py -l <login link> -e <echo link>"
}

opts, args = getopt.getopt(sys.argv[1:], settings["optstring"])

for opt, arg in opts:
    if opt == "-d":
        settings["dry_run"] = True

    if opt == "--lectures":
        settings["download"] = True
