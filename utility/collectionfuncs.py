#!/usr/bin/env python3

"""
Common functions that build or operate upon collections of values
"""

import collections

def mixin_lt_eq_comparable(cls):
  """
  Define the standard suite of functions based on __lt__ and __eq__

  Does not require the right-hand-side operand implement __lt__
  """
  cls.__ne__ = lambda self, other: not self.__eq__(other)
  cls.__le__ = lambda self, other: self.__lt__(other) or self.__eq__(other)
  cls.__gt__ = lambda self, other: not self.__le__(other)
  cls.__ge__ = lambda self, other: not self.__lt__(other)
  return cls

def mixin_lt_comparable(cls):
  """
  Define the standard suite of functions based on __lt__

  Note that __eq__ requires both operands implement __lt__
  """
  cls.__eq__ = lambda self, other: \
      not self.__lt__(other) and not other.__lt__(self)
  cls = mixin_lt_eq_comparable(cls)
  return cls

def aggregate_values_dict(entries):
  "Build a dict associating a value to all entries with that value"
  result = collections.defaultdict(list)
  if isinstance(entries, dict):
    entries = entries.items()
  for key, val in entries:
    result[val].append(key)
  return dict(result)

# vim: set ts=2 sts=2 sw=2:
