#!/usr/bin/env python3

"""
Functions for deciphering inventory items
"""

import datetime
import enum
import os

import utility.loghelper
from .xmltools import parse_strings_node as xml_parse_strings
from . import xmltools

logger = utility.loghelper.DelayLogger(__name__)

CONTAINER_SIZE = 1000

class Kind(enum.Enum):
  CARD = enum.auto()    # spells (full menu)
  WAND = enum.auto()    # wands (quick menu)
  POTION = enum.auto()  # potions (quick menu)
  SACK = enum.auto()    # satchels (quick menu)
  EGG = enum.auto()     # eggs (quick menu)
  PICKUP = enum.auto()  # items (Kuu, etc) (quick menu)
  OTHER = enum.auto()   # something else
  @classmethod
  def get(cls, kind):
    "Convert a lower-case kind to an enum"
    return cls[kind.upper()]
  def __eq__(self, other):
    "self == other"
    if isinstance(other, str):
      return self == Kind.get(other)
    return self.value == other.value
  def __hash__(self):
    "hash(self)"
    return self.value

def classify_item(entity):
  "Determine which Kind best describes this item"
  tags = entity.attrib["tags"].split(",")
  if "card_action" in tags:
    return Kind.CARD
  if "wand" in tags:
    return Kind.WAND
  if "item_pickup" in tags:
    if "potion" in tags:
      return Kind.POTION
    # TODO: sacks
    if "egg_item" in tags:
      return Kind.EGG
    return Kind.PICKUP
  return Kind.OTHER

