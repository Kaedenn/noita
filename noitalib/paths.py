#!/usr/bin/env python3

"""
Functions for determining filesystem paths
"""

import os

import steam.paths

from .constants import NOITA_APPID, NOITA_APPDIR
from .logger import logger

def get_save_path(steam_path, appid=NOITA_APPID):
  "Get the path to the Noita save directories"
  app_root = steam.paths.get_appdata_for(appid, steam_path=steam_path)
  return os.path.join(app_root, NOITA_APPDIR)

# vim: set ts=2 sts=2 sw=2:
