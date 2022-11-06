#!/usr/bin/env python3

"""
Ancillary functions to assist with dealing with Steam.
"""

import glob
import os
import platform

import utility.loghelper
from . import acf

STEAM_WIN = "C:\\Program Files (x86)\\Steam"
STEAM_MAC = os.path.expanduser("~/Library/Application Support/Steam")
STEAM_LNX = os.path.expanduser("~/.local/share/Steam")

logger = utility.loghelper.DelayLogger(__name__)

def read_appid(fpath):
  """
  Read the content of a steam_appid.txt file

  Sometimes these files have garbage after the number, such as TF2 having
  "440\\n\\x00" and GarrysMod having "4000\\n\\x00". So, just return the first
  line.
  """
  with open(fpath, "rt") as fobj:
    text = fobj.read()
  return text.splitlines()[0]

def get_steam_path():
  "Get the absolute path to the Steam root directory"
  ostype = platform.system()
  steam = None
  if ostype == "Windows":
    steam = STEAM_WIN
  elif ostype == "Linux":
    steam = STEAM_LNX
  else:
    for spath in (STEAM_MAC, STEAM_WIN, STEAM_LNX):
      if os.path.isdir(spath):
        steam = spath
        break
  if not steam:
    raise OSError("Failed to find Steam installation path")
  return steam

def get_steamapps_path(steam_path):
  "Get the absolute path to the steamapps directory"
  # The steamapps directory used to be "SteamApps", so support that
  sapps = None
  for dname in os.listdir(steam_path):
    if dname.lower() == "steamapps":
      sapps = os.path.join(steam_path, dname)
      break
  return sapps

def get_game_by_id(appid, steam_path=get_steam_path(), by_manifest=True):
  "Get (appid, game_path) for the given game appid"
  sapps = get_steamapps_path(steam_path)
  sgames = os.path.join(sapps, "common")
  if by_manifest:
    mfile = os.path.join(sapps, f"appmanifest_{appid}.txt")
    if os.path.isfile(mfile):
      gameinfo = acf.parse_acf_file(mfile)
      appstate = gameinfo.get("AppState")
      if appstate.get("appid") == appid:
        return appid, os.path.join(sgames, appstate["installdir"])
  for appid_path in glob.glob(os.path.join(sgames, "*", "steam_appid.txt")):
    if read_appid(appid_path) == appid:
      return appid, os.path.dirname(appid_path)
  return None, None

def get_game_by_dir(dirname, steam_path=get_steam_path()):
  "Get (appid, game_path) for the given game directory name"
  sapps = get_steamapps_path(steam_path)
  sgames = os.path.join(sapps, "common")
  game_path = os.path.join(sgames, dirname)
  appid_file = os.path.join(game_path, "steam_appid.txt")
  if os.path.isfile(appid_file):
    return read_appid(appid_file), game_path
  return None, None

def get_game(game_or_appid, steam_path=get_steam_path(), by_manifest=True):
  "Get the appid and game path for the given game name or appid"
  appid, gamepath = None, None
  if game_or_appid.isdigit():
    appid, gamepath = get_game_by_id(
        game_or_appid, steam_path=steam_path, by_manifest=by_manifest)
  if appid is None or gamepath is None:
    appid, gamepath = get_game_by_dir(
        game_or_appid, steam_path=steam_path)
  if appid is None or gamepath is None:
    logger.error("Failed to find game %s in %s",
        game_or_appid, steam_path)
  return appid, gamepath

def get_steam_games(steam_path=get_steam_path(), by_manifest=True):
  """
  Get the games installed within the Steam directory

  by_manifest:
    If True, parse steamapps/appmanifest_*.acf files.
    If False, match game directory names and their steam_appid.txt content.
  """
  sapps = get_steamapps_path(steam_path)
  if by_manifest:
    for mfile in glob.glob(os.path.join(sapps, "appmanifest_*.acf")):
      ginfo = acf.parse_acf_file(mfile)
      try:
        appid = ginfo["AppState"]["appid"]
        gdir = ginfo["AppState"]["installdir"]
        yield appid, gdir
      except KeyError as err:
        logger.error("Error parsing %s", mfile)
        logger.error(err)
  else:
    sgames = os.path.join(sapps, "common")
    for idpath in glob.glob(os.path.join(sgames, "*", "steam_appid.txt")):
      appid = read_appid(idpath)
      gdir = os.path.split(os.path.dirname(idpath))[1]
      yield appid, gdir

def get_appdata_for(game_or_appid=None,
    session="LocalLow",
    steam_path=get_steam_path(),
    by_manifest=True):
  """
  Get the AppData directory

  If game_or_appid is None, then return the global AppData directory.
  Otherwise, return the one that the given game would prefer to use. Note that
  on systems other than Windows, Steam games under Proton all have their own
  unique AppData directories and therefore this argument is required to get the
  correct path.

  "session" is used to select between Roaming, Local, or LocalLow.

  """
  appdir = os.path.join("AppData", session)
  if platform.system() == "Windows":
    # For now, assume all Windows games use %USERPROFILE%\AppData and that
    # there are no per-game appdata directories.
    return os.path.join(os.path.expandvars("$USERPROFILE"), appdir)

  # Everything below is for non-Windows

  if game_or_appid is None:
    return os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))

  sapps = get_steamapps_path(steam_path)
  appid, _ = get_game(
      game_or_appid, steam_path=steam_path, by_manifest=by_manifest)
  game_root = os.path.join(sapps, "compatdata", appid, "pfx", "drive_c")
  game_home = os.path.join(game_root, "users", "steamuser")
  return os.path.join(game_home, appdir)

# vim: set ts=2 sts=2 sw=2:
