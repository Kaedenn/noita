#!/usr/bin/env python3

"""
Functions for deciphering the world_state.xml file
"""

import os
import pathlib

import utility.loghelper
from . import sessions
from . import xmltools
from .xmltools import parse_entries_node, parse_strings_node
logger = utility.loghelper.DelayLogger(__name__)

# TODO: i18n support (is this even needed?)

class WorldState:
  "The world state"
  def __init__(self, file_path):
    "See help(type(self))"
    self._path = file_path
    self._root = parse_world(file_path)
    self._globals = {}
    self._orbs = ()
    self._flags = ()
    self._shifts = ()
    self._state = xmltools.xml_get_child(self._root, "WorldStateComponent")
    self._interpret()

  @property
  def path(self):
    "Path to world file"
    return self._path

  def _state_node(self, child=None):
    "Get the WorldStateComponent node, or one of its children"
    if child is not None:
      return xmltools.xml_get_child(self._state, child)
    return self._state

  def _state_attrib(self, attrib, default=None):
    "Get an attribute of the WorldStateComponent node"
    return self._state.attrib.get(attrib, default)

  def _interpret(self):
    "Interpret self._root and (re)set self attributes"
    lua_node = self._state_node("lua_globals")
    self._globals = parse_entries_node(lua_node, as_int=True)
    # TODO: pending_portals
    # TODO: apparitions_per_level
    # TODO: npc_parties
    self._orbs = tuple(int(celem) for celem in \
        parse_strings_node(self._state_node("orbs_found_thisrun")))
    self._flags = parse_strings_node(self._state_node("flags"))
    self._shifts = parse_strings_node(self._state_node("changed_materials"))
    # TODO: cuts_through_world

    self._stat_file = self._state_attrib("session_stat_file")

  def orbs(self):
    "Get the orbs that have been attained this run"
    return tuple(self._orbs)

  def has_orb(self, num):
    "True if the given orb (0-10 inclusive) was collected"
    return num in self._orbs

  def shifts(self):
    "Get all (material, material) shifts"
    return zip(self._shifts[::2], self._shifts[1::2])

  def lua_globals(self):
    "Get the lua globals"
    return dict(self._globals)

  def flags(self):
    "Get the flags"
    return tuple(self._flags)

  def getvar(self, name, astype=None, default=None):
    "Get a variable from lua_globals, optionally as a specific type"
    if name in self._globals:
      value = self._globals[name]
      if astype is not None:
        value = astype(value)
      return value
    return default

  def getvar_int(self, name, default=0):
    "Get a variable from lua_globals as an int"
    return self.getvar(name, astype=int, default=default)

  def perks(self):
    "Attempt to get the perks obtained this run"
    perks = []
    for vkey, vval in self._globals.items():
      if vkey.startswith("PERK_PICKED_") and vkey.endswith("_PICKUP_COUNT"):
        perk_id = "_".join(vkey.split("_")[2:-2])
        perks.append((perk_id.lower(), int(vval)))
    return perks

  def fungal_shifts(self):
    "Get the number of fungal shifts"
    return self.getvar("fungal_shift_iteration", astype=int, default=0)

  def stevari_deaths(self):
    "Get the number of times Stevari has been killed"
    return self.getvar("STEVARI_DEATHS", astype=int, default=0)

  def new_perks(self):
    "Get the new perks found this run"
    for flag in self._flags:
      if flag.startswith("new_perk_"):
        yield flag.split("_", 1)[1]

  def new_spells(self):
    "Get the new spells found this run"
    for flag in self._flags:
      if flag.startswith("new_action_"):
        yield flag.split("_", 1)[1]

  def new_kills(self):
    "Get the new kills found this run"
    for flag in self._flags:
      if flag.startswith("new_kill_"):
        yield flag.split("_", 1)[1]

  def reroll_info(self):
    "Return information about perk reroll status"
    return {
      "perk_index": self.getvar_int("TEMPLE_NEXT_PERK_INDEX"),
      "destroy_chance": self.getvar_int("TEMPLE_PERK_DESTROY_CHANCE"),
      "reroll_count": self.getvar_int("TEMPLE_PERK_REROLL_COUNT"),
      "reroll_index": self.getvar_int("TEMPLE_REROLL_PERK_INDEX")
    }

  def stats_path(self, save_path):
    "Get the path to the stats file"
    parts = list(pathlib.Path(self._stat_file).parts)
    if parts:
      if parts[0] == "??STA":
        parts[0] = os.path.join(save_path, "stats")
      parts[-1] += "_stats.xml"
      return os.path.join(*parts)
    raise ValueError("invalid stats_path {!r}".format(self._stat_file))

  def get_session_stats(self, save_path):
    "Return a parsed session from this world's stats file"
    return sessions.parse_session(self.stats_path(save_path))

def get_world_file(save_path):
  "Return the path to the world file"
  return os.path.join(save_path, "world_state.xml")

def parse_world(world_path):
  "Parse the world.xml file"
  logger.trace("Parsing world file %r", world_path)
  return xmltools.parse_xml(world_path, get_root=True)

# vim: set ts=2 sts=2 sw=2:
