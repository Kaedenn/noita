#!/usr/bin/env python3

"""
Various constants pertaining to Noita and its Steam environment
"""

import os

NOITA_APPID = "881100"
NOITA_APPDIR = "Nolla_Games_Noita"

APP_DATA = os.path.join("AppData", "LocalLow")

SESS_DATE_FORMAT = "%Y%m%d-"
SESS_TIME_FORMAT = "%H%M%S_"
SESS_DATETIME_FORMAT = SESS_DATE_FORMAT + SESS_TIME_FORMAT
STATS_FILE_FORMAT = SESS_DATETIME_FORMAT + "stats.xml"

# vim: set ts=2 sts=2 sw=2:
