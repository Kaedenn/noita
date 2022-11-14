#!/usr/bin/env python3

"""
Define a class that implements a kind of "level of detail" enumeration.
"""

try:
  from . import collectionfuncs as _cfuncs
except ImportError: # allow execution as a script
  import collectionfuncs as _cfuncs
import enum

# pylint: disable=comparison-with-callable

# Mapping of <enum-name>: <enum-obj> for all Detail enumerations
DETAIL = {}

@_cfuncs.mixin_lt_eq_comparable
class Detail(enum.Enum):
  "'Amount of detail' enumeration constants"
  BRIEF = enum.auto()
  BASIC = enum.auto()
  LESS = enum.auto()
  NORMAL = enum.auto()
  MORE = enum.auto()
  FULL = enum.auto()
  def __lt__(self, other):
    "self < other"
    if isinstance(other, Detail):
      return self.value < other.value
    if isinstance(other, str):
      return self.value < Detail[other].value
    return self.value < other

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

def _main():
  "Test suites"
  # pylint: disable=unneded-not
  assert Detail.BRIEF < Detail.BASIC
  assert Detail.BRIEF <= Detail.BRIEF
  assert Detail.BASIC < Detail.LESS
  assert Detail.BASIC <= Detail.BASIC
  assert not Detail.BRIEF > Detail.BRIEF
  assert not Detail.BRIEF != Detail.BRIEF
  print("Tests passed")

if __name__ == "__main__":
  _main()

# vim: set ts=2 sts=2 sw=2:
