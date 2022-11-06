#!/usr/bin/env python3

"""
Functions for interacting with Noita game sessions

A "session" is a stats.xml file with, optionally, a kills.xml file.
    YYYYMMDD-HHMISS_stats.xml
    YYYYMMDD-HHMISS_kills.xml
"""

import datetime
import os

import utility.loghelper
from . import xmltools
logger = utility.loghelper.DelayLogger(__name__)

def session_get_time(stats_file):
  "Get the date and time the given session was played"
  # 20221013-203926_stats.xml
  try:
    date_part = os.path.basename(stats_file).split("_")[0]
    sdate, stime = date_part.split("-")
  except (IndexError, ValueError) as err:
    logger.error("Failed to extract date from %s: %s", stats_file, err)
    return None
  s_year = sdate[:4]
  s_month = sdate[4:6]
  s_day = sdate[6:]
  s_hour = stime[:2]
  s_minute = stime[2:4]
  s_second = stime[4:]
  try:
    return datetime.datetime(
        int(s_year),
        int(s_month),
        int(s_day),
        int(s_hour),
        int(s_minute),
        int(s_second))
  except ValueError as err:
    logger.error("Failed to extract date from %s: %s", stats_file, err)
    return None

def parse_kills(kills_root):
  "Parse a kills listing"
  base = kills_root.attrib
  deaths_node = xmltools.xml_get_child(kills_root, "death_map")
  kills_node = xmltools.xml_get_child(kills_root, "kill_map")
  return {
    "kill_count": int(base["kills"]),
    "death_count": int(base["deaths"]),
    "kills": xmltools.parse_entries_node(kills_node, as_int=True),
    "deaths": xmltools.parse_entries_node(deaths_node, as_int=True)
  }

def parse_session(stats_file, kills_file):
  "Extract information from a given play session"
  date_played = session_get_time(stats_file)
  stats_root = xmltools.parse_xml(stats_file, get_root=True)

  stats_node = xmltools.xml_get_child(stats_root, "stats")
  biomes_node = xmltools.xml_get_child(stats_root, "biome_baseline")
  visits_node = xmltools.xml_get_child(stats_root, "biomes_visited")
  items_node = xmltools.xml_get_child(stats_root, "item_map")

  build = stats_root.attrib["BUILD_NAME"]
  stats = stats_node.attrib
  seed = stats["world_seed"]
  biomes = biomes_node.attrib
  visits = xmltools.parse_entries_node(visits_node)
  items = {} # TODO

  try:
    kills_root = xmltools.parse_xml(kills_file, get_root=True)
    kills = parse_kills(kills_root)
  except FileNotFoundError:
    logger.debug("No kills for session %r", os.path.basename(stats_file))
    kills_root = None
    kills = {}

  return {
    "build": build,
    "date": date_played,
    "seed": seed,
    "timestamp": date_played.timestamp(),
    "stats": stats,
    "biomes": biomes,
    "items": items,
    "visits": visits,
    "kills": kills,
    "_nodes": {
      "stats_file": stats_root,
      "kills_file": kills_root
    },
    "_files": {
      "stats_file": stats_file,
      "kills_file": kills_file
    }
  }

# vim: set ts=2 sts=2 sw=2:
