#!/usr/bin/env python3

"""
Functions for locating Noita-specific directories
"""

import os

import steam.paths
import utility.loghelper

from .constants import NOITA_APPID, NOITA_APPDIR
logger = utility.loghelper.DelayLogger(__name__)

SAVE_DIR_FORMAT = "save{:02d}"
SAVE_MAIN = "save00"
SAVE_SHARED = "save_shared"

def get_saves_path(steam_path, appid=NOITA_APPID):
  "Get the path to the Noita save directories"
  app_root = steam.paths.get_appdata_for(appid, steam_path=steam_path)
  return os.path.join(app_root, NOITA_APPDIR)

def is_save_path(save_path):
  "True if the path resolves to a Noita save"
  if os.path.isdir(save_path):
    save_name = os.path.basename(save_path)
    if save_name == "save_shared":
      return True
    if len(save_name) == len("save00"):
      if save_name.startswith("save") and save_name[-2:].isdigit():
        return True
  return False

def list_saves(saves_root):
  "List all save directories"
  for entry in os.listdir(saves_root):
    save_path = os.path.join(saves_root, entry)
    if is_save_path(save_path):
      yield save_path

def get_save_paths(saves_root, for_saves=None):
  "Get individual save directories. Returns all if for_saves is empty"
  save_paths = list(list_saves(saves_root))
  save_dirs = {os.path.basename(spath): spath for spath in save_paths}
  results = []
  if for_saves:
    for save_name in for_saves:
      if isinstance(save_name, int):
        save_name = SAVE_DIR_FORMAT.format(save_name)
      if save_name in save_dirs:
        results.append(save_dirs[save_name])
  else:
    results.extend(save_dirs.values())
  return results

def path_resolve(path_arg, prefix, raises=False):
  "Resolve prefix/path or prefix/../path"
  if os.path.exists(os.path.join(prefix, path_arg)):
    return os.path.join(prefix, path_arg)
  if os.path.exists(os.path.join(prefix, os.pardir, path_arg)):
    return os.path.realpath(os.path.join(prefix, os.pardir, path_arg))
  if raises:
    raise ValueError("Failed to find {!r} in {!r}".format(path_arg, prefix))
  return path_arg

def resolve_dofile_path(path_arg, mods_path=None, data_path=None, root=None):
  "Resolve a dofile() or dofile_once() argument"
  if path_arg.startswith("mods/") and mods_path is not None:
    result = path_resolve(path_arg, mods_path)
    if os.path.exists(result):
      return result
  if path_arg.startswith("data/") and data_path is not None:
    result = path_resolve(path_arg, data_path)
    if os.path.exists(result):
      return result
  if root is not None:
    if os.path.exists(os.path.join(root, path_arg)):
      return os.path.join(root, path_arg)
  if os.path.exists(path_arg):
    return path_arg
  return None

# vim: set ts=2 sts=2 sw=2:
