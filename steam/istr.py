#!/usr/bin/env python3

"""
A string type that ignores case
"""

import collections

UNSET = "!!UNSET"

class IStr(collections.UserString): # pylint: disable=too-many-ancestors
  "A string that ignores case"

  def casefold(self):
    "Return a normalized str that can be used for caseless compares"
    return super().casefold().data

  def __hash__(self):
    return hash(self.casefold())
  def __eq__(self, other):
    return self.casefold() == other.casefold()
  def __ne__(self, other):
    return self.casefold() != other.casefold()
  def __lt__(self, other):
    return self.casefold() < other.casefold()
  def __le__(self, other):
    return self.casefold() <= other.casefold()
  def __gt__(self, other):
    return self.casefold() > other.casefold()
  def __ge__(self, other):
    return self.casefold() >= other.casefold()

  def __contains__(self, other):
    return self.casefold() in other.casefold()

  def __repr__(self):
    return f"IStr({super().__repr__()!r})"

# vim: set ts=2 sts=2 sw=2:
