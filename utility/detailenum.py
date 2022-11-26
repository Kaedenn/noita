#!/usr/bin/env python3

"""
Define a class that implements a kind of "level of detail" enumeration.
"""

import enum
import functools

# Mapping of <enum-name>: <enum-obj> for all Detail enumerations
DETAIL = {}

def _dec_other_cmp(func):
  "Comparable to facilitate comparing two Detail 'things'"
  @functools.wraps(func)
  def wrapper(self, other):
    "Wrapper function"
    if isinstance(other, int):
      return func(self, Detail(other))
    if isinstance(other, str):
      if other in DETAIL:
        return func(self, DETAIL[other])
    if isinstance(other, Detail):
      return func(self, other)
    raise ValueError("Don't know how to compare {self!r} and {other!r}")
  return wrapper

class Detail(enum.Enum):
  "'Amount of detail' enumeration constants"
  # pylint: disable=comparison-with-callable
  BRIEF = enum.auto()
  BASIC = enum.auto()
  LESS = enum.auto()
  NORMAL = enum.auto()
  MORE = enum.auto()
  FULL = enum.auto()
  @_dec_other_cmp
  def __eq__(self, other):
    "self == other"
    return self.value == other.value
  @_dec_other_cmp
  def __ne__(self, other):
    "self != other"
    return self.value != other.value
  @_dec_other_cmp
  def __lt__(self, other):
    "self < other"
    return self.value < other.value
  @_dec_other_cmp
  def __le__(self, other):
    "self <= other"
    return self.value <= other.value
  @_dec_other_cmp
  def __gt__(self, other):
    "self > other"
    return self.value > other.value
  @_dec_other_cmp
  def __ge__(self, other):
    "self >= other"
    return self.value >= other.value
  def __hash__(self):
    "hash(self)"
    return self.value

DETAIL.update({_value.name: _value for _value in Detail})
DETAIL.update({
  "B": Detail.BASIC,
  "L": Detail.LESS,
  "N": Detail.NORMAL,
  "M": Detail.MORE,
  "F": Detail.FULL
})

def detail_help(level_name_or_enum):
  "Return a help string for the given detail level"
  if isinstance(level_name_or_enum, enum.Enum):
    level = level_name_or_enum
  elif level_name_or_enum in DETAIL:
    level = DETAIL[level_name_or_enum]
  else:
    raise ValueError("Invalid detail {!r}".format(level_name_or_enum))

  return {
    Detail.BRIEF: "include only the highest-level summary necessary",
    Detail.BASIC: "include only what's necessary",
    Detail.LESS: "include basic and less important information",
    Detail.NORMAL: "standard level; includes everything deemed useful",
    Detail.MORE: "include more detailed information",
    Detail.FULL: "include absolutely everything known"
  }[level]

# vim: set ts=2 sts=2 sw=2:
