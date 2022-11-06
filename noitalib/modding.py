#!/usr/bin/env python3

"""
Functions for interacting with Noita mods
"""

import glob
import os

import steam.paths
import utility.loghelper

from . import xmltools
from . import constants
logger = utility.loghelper.DelayLogger(__name__)

def mod_get_id(mod_path):
  "Get the mod's ID (usually its name, lowercase)"
  try:
    with open(os.path.join(mod_path, "mod_id.txt"), "rt") as fobj:
      return fobj.read().splitlines()[0]
  except FileNotFoundError:
    logger.debug("Mod %s lacks mod_id.txt", mod_path)
    return os.path.basename(mod_path)

def mod_get_compat(mod_path):
  "Get the mod's compatibility information, if present"
  compat_path = os.path.join(mod_path, "compatibility.xml")
  try:
    return xmltools.parse_xml(compat_path, get_root=True)
  except FileNotFoundError:
    logger.debug("Mod %s lacks compatibility file", mod_path)
    return {}

def get_mod(mod_path):
  """
  Get (mod_id, mod_info, compat_info) from the given mod directory

  Supports both Steam workshop mods and native Noita mods.
  """
  mod_num = os.path.dirname(mod_path)
  mod_id = mod_get_id(mod_path)
  modfile = os.path.join(mod_path, "mod.xml")
  mod_info = xmltools.parse_xml(modfile, get_root=True).attrib
  return {
    "id": mod_id,
    "workshop_id": os.path.basename(mod_path),
    "name": mod_info["name"],
    "description": mod_info["description"],
    "compat": mod_get_compat(mod_path)
  }

def get_workshop_mods(steam_path, appid=constants.NOITA_APPID):
  "Get all of the downloaded Workshop mods"
  sapps = steam.paths.get_steamapps_path(steam_path)
  wspath = os.path.join(sapps, "workshop", "content", appid)
  logger.debug("Looking for workshop mods in %s", wspath)
  for modfile in glob.glob(os.path.join(wspath, "*", "mod.xml")):
    logger.trace("Found mod file %s", modfile)
    yield get_mod(os.path.dirname(modfile))

def get_native_mods(game_path=None):
  "Get all of the available game mods"
  if game_path is None:
    _, game_path = steam.paths.get_game("Noita")
  for modfile in glob.glob(os.path.join(game_path, "mods", "*", "mod.xml")):
    logger.trace("Found mod file %s", modfile)
    yield get_mod(os.path.dirname(modfile))

def save_get_mods(save_path):
  "Get the mods available for the given save and their status"
  def mod_def(enabled,
      name,
      settings_fold_open="0",
      workshop_item_id="0",
      **kwargs):
    "Simple function to extract specific attributes from everything else"
    return {
      "enabled": enabled == "1",
      "name": name,
      "settings_fold_open": settings_fold_open,
      "workshop_item_id": workshop_item_id,
      "extra": kwargs
    }
  conf_path = os.path.join(save_path, "mod_config.xml")
  root = xmltools.parse_xml(conf_path, get_root=True)
  for order, mod_node in enumerate(root.cssselect("Mod")):
    mod = mod_def(**mod_node.attrib)
    mod["order"] = order + 1
    if not mod["extra"]:
      del mod["extra"]
    yield mod

# vim: set ts=2 sts=2 sw=2:
