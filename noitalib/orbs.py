#!/usr/bin/env python3

"""
Constants and functions pertaining to the Orbs of True Knowledge

Orb constants behave as follows:
  0-127   main world
  128-255 west parallel world
  255-383 east parallel world
However, world constants are centered at zero:
  <0      west parallel worlds
  0       main world
  >0      east parallel worlds
"""

import utility.loghelper
logger = utility.loghelper.DelayLogger(__name__)

ORB_MAX = 128
WORLD_MAIN = "main"
WORLD_WEST = "west"
WORLD_EAST = "east"
ORB_11 = 11

def orb_extract(orb_id):
  "Extract orb and world IDs from a combined orb ID"
  orb_number = orb_id % ORB_MAX
  world_index = orb_id // ORB_MAX
  world_number = world_index
  if world_index != 0:
    if world_index % 2 == 1:
      world_number = (world_index + 1)/2
    else:
      world_number = -world_index/2
  return orb_number, world_number

def get_orb(orb_id):
  "Map a numeric orb ID to an Orb instance"
  if orb_id not in ORBS:
    raise ValueError("Invalid orb {}".format(orb_id))
  return ORBS[orb_id]

def get_orb_world(orb_id):
  "Get the world direction and number for the orb"
  _, world = orb_extract(orb_id)
  if world < 0:
    return WORLD_EAST, abs(world)
  if world > 0:
    return WORLD_WEST, world
  return WORLD_MAIN, 0

class Orb:
  "An Orb of True Knowledge"
  def __init__(self, orbid, spell, place):
    "See help(type(self))"
    self.orbid = orbid
    self.num = orbid % ORB_MAX
    self.world, self.woffset = get_orb_world(orbid)
    self.spell = spell
    self.place = place

  def __cmp__(self, other):
    "cmp(self, other)"
    if isinstance(other, Orb):
      if self.num < other.num:
        return -1
      if self.num > other.num:
        return 1
      return 0
    raise ValueError(f"Can't compare Orb with {type(other)}")

  def __lt__(self, other):
    return self.__cmp__(other) < 0

  def __le__(self, other):
    return self.__cmp__(other) <= 0

  def __eq__(self, other):
    return self.__cmp__(other) == 0

  def __ge__(self, other):
    return self.__cmp__(other) >= 0

  def __gt__(self, other):
    return self.__cmp__(other) > 0

  def __ne__(self, other):
    return self.__cmp__(other) != 0

  def localize(self, langmap):
    "Create a string representing this orb"
    place = langmap(self.place, title=True)
    if self.world != WORLD_MAIN:
      wprefix = "$biome_" + self.world
      if self.woffset != 1:
        wprefix += f" x{self.woffset}"
      place = langmap(wprefix, place, title=True)
      return f"Orb {self.orbid} from {place}"
    spell = langmap(self.spell, title=True)
    desc = f"{spell} from {place}".lstrip()
    return f"Orb {self.num} {desc}"

  def __repr__(self):
    "repr(self)"
    return f"Orb({self.orbid}, {self.spell!r}, {self.place!r})"

BASE_ORBS = {
  0: Orb(0, "$action_sea_lava", "Floating Island"),
  1: Orb(1, "$action_crumbling_earth", "$biome_pyramid"),
  2: Orb(2, "$action_tentacle", "$biome_vault_frozen"),
  3: Orb(3, "$action_nuke", "$biome_lavacave"), # TODO: verify
  4: Orb(4, "$action_necromancy", "$biome_sandcave"),
  5: Orb(5, "$action_bomb_holy", "$biome_wandcave"),
  6: Orb(6, "$action_spiral_shot", "$biome_rainforest_dark"),
  7: Orb(7, "$action_cloud_thunder", "Bridge Chasm"),
  8: Orb(8, "$action_firework", "$biome_boss_victoryroom (Hell)"),
  9: Orb(9, "$action_exploding_deer", "$biome_winter_caves"),
  10: Orb(10, "$action_material_cement", "$biome_wizardcave"),
  11: Orb(11, "", "$item_chest_treasure_super")
}

ORBS = {}
def _init(): # TODO: FIXME: Verify the following logic
  "Initialize the ORBS global"
  for oid, orb in BASE_ORBS.items():
    if oid != ORB_11:
      for wid in (0, 1, 2):
        new_oid = oid + ORB_MAX * wid
        ORBS[new_oid] = Orb(new_oid, orb.spell, orb.place)
    else:
      ORBS[oid] = orb
_init()

# vim: set ts=2 sts=2 sw=2:
