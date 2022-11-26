#!/usr/bin/env python3

"""
Common functions that build or operate upon collections of values
"""

import collections

def aggregate_values_dict(entries):
  "Build a dict associating a value to all entries with that value"
  result = collections.defaultdict(list)
  if isinstance(entries, dict):
    entries = entries.items()
  for key, val in entries:
    result[val].append(key)
  return dict(result)

# vim: set ts=2 sts=2 sw=2:
