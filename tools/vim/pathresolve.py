#!/usr/bin/env python3

"""
Resolve paths to files to assist mod development
"""

import argparse
import logging
import os
import sys

from os.path import dirname, basename, abspath, realpath

logging.basicConfig(format="%(module)s:%(lineno)s: %(levelname)s: %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def path_is_root(path):
  "True if path is the root path, False otherwise"
  return abspath(path) == abspath(os.path.join(path, os.pardir))

def is_mod(path):
  "True if the path looks like a Noita mod"
  if os.path.isfile(os.path.join(path, "mod.xml")):
    if os.path.isfile(os.path.join(path, "init.lua")):
      return True
  return False

def get_mod_path(path, quietly=False):
  "Get the path to the mod directory containing the given path"
  cpath = realpath(abspath(path))
  if os.path.isfile(cpath):
    cpath = dirname(cpath)

  while not is_mod(cpath) and not path_is_root(cpath):
    cpath = abspath(os.path.join(cpath, os.pardir))

  if path_is_root(cpath):
    if not quietly:
      logger.warning("failed to find mod path containing %r", path)
    return None

  if not is_mod(cpath):
    if not quietly:
      logger.error("mod path search on %r failed prematurely", path)
    return None

  return cpath

def path_startswith(path, name):
  "True if the path starts with name"
  parts = path.split(os.sep)
  return len(parts) > 1 and parts[0] == name

def resolve_path(path, mods_dir=None, data_dir=None, extra_paths=()):
  "Resolve a dofile() path argument"
  logger.debug("Resolve %s (mods=%r, data=%r, extras=%r)",
      path, mods_dir, data_dir, extra_paths)

  # Handle "mods/<name>/<path>..."
  if path_startswith(path, "mods") and mods_dir is not None:
    module = os.path.join(mods_dir, os.pardir, path)
    if os.path.exists(module):
      return module

  # Handle "data/<path>..."
  if path_startswith(path, "data") and data_dir is not None:
    module = os.path.join(data_dir, os.pardir, path)
    if os.path.exists(module):
      return module

  if extra_paths:
    for base in extra_paths:
      # Handle "<base>/<path>..."
      if os.path.exists(os.path.join(base, path)):
        logger.debug("Direct; %s relative to base %s", path, base)
        return os.path.join(base, path)

  # Handle direct path
  if os.path.exists(path):
    return path

  return None

def main():
  "Entry point"
  ap = argparse.ArgumentParser()
  ap.add_argument("filepath", help="path to resolve")
  ag = ap.add_argument_group("support paths")
  ag.add_argument("-m", "--mod-path", metavar="PATH",
      help="path to Noita mods directory")
  ag.add_argument("-d", "--data-path", metavar="PATH",
      help="path to the extracted data.wak directory")
  ag.add_argument("-p", "--path", action="append",
      help="add additional lookup path")
  ag = ap.add_argument_group("supplemental arguments")
  ag.add_argument("-n", "--no-nl", action="store_true",
      help="do not output a newline")
  ag = ap.add_argument_group("diagnostics")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-v", "--verbose", action="store_true",
      help="enable verbose diagnostics")
  mg.add_argument("-w", "--warnings", action="store_true",
      help="disable diagnostics below warning")
  mg.add_argument("-e", "--errors", action="store_true",
      help="disable diagnostics below error")
  mg.add_argument("-q", "--quiet", action="store_true",
      help="disable all but the most severe diagnostics")
  args = ap.parse_args()
  if args.verbose:
    logger.setLevel(logging.DEBUG)
  elif args.warnings:
    logger.setLevel(logging.WARNING)
  elif args.errors:
    logger.setLevel(logging.ERROR)
  elif args.quiet:
    logger.setLevel(logging.CRITICAL)

  filepath = args.filepath.strip()
  mods_path = args.mod_path
  data_path = args.data_path
  addl_paths = args.path if args.path else [os.curdir]
  result = resolve_path(filepath, mods_dir=mods_path, data_dir=data_path, extra_paths=addl_paths)

  if result:
    sys.stdout.write(result)
    if not args.no_nl:
      sys.stdout.write(os.linesep)
  else:
    logger.error("Failed to find %r", filepath)
    logger.warning("mods_dir=%r", mods_path)
    logger.warning("data_dir=%r", data_path)
    logger.warning("extra_paths=%r", addl_paths)

if __name__ == "__main__":
  main()

# vim: set ts=2 sts=2 sw=2:
