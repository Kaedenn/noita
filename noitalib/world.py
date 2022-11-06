#!/usr/bin/env python3

"""
Functions for deciphering the world_state.xml file
"""

import os

from . import xmltools
from .xmltools import parse_entries_node, parse_strings_node
from .logger import logger

# TODO: i18n support

class WorldState:
  "The world state"
  def __init__(self, file_path):
    "See help(type(self))"
    self._path = file_path
    self._root = parse_world(file_path)
    self._interpret()

  def _state_node(self, child=None):
    "Get the WorldStateComponent node, or one of its children"
    state = xmltools.xml_get_child(self._root, "WorldStateComponent")
    if child is not None:
      return xmltools.xml_get_child(state, child)
    return state

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

  def perks(self):
    "Attempt to get the perks obtained this run"
    perks = []
    for vkey, vval in self._globals.items():
      if vkey.startswith("PERK_PICKED_") and vkey.endswith("_PICKUP_COUNT"):
        perk_id = "_".join(vkey.split("_")[2:-2])
        perks.append((perk_id.lower(), int(vval)))
    return perks

def get_world_file(save_path):
  "Return the path to the world file"
  return os.path.join(save_path, "world_state.xml")

def parse_world(world_path):
  "Parse the world.xml file"
  logger.trace("Parsing world file %r", world_path)
  return xmltools.parse_xml(world_path, get_root=True)

# vim: set ts=2 sts=2 sw=2:
