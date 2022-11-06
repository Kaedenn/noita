#!/usr/bin/env python3

"""
Provide a dictionary that ignores case
"""

import functools
import warnings

def casefold(value):
  "casefold the value, but only if it's a string"
  if isinstance(value, str):
    return value.casefold()
  return value

def keymapped(func):
  "Ensure the keymap exists by the time func is called"
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    "Ensure the keymap exists"
    self.ensure_keymap()
    return func(self, *args, **kwargs)
  return wrapper

def loggable(func):
  "Allow the function to be examined"
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    "Print function, arguments, and return value, if enabled"
    callstr = f"{self!r}.{func.__name__}(*{args!r}, **{kwargs!r})"
    try:
      value = func(self, *args, **kwargs)
      if self._logging: # pylint: disable=protected-access
        print(f"{callstr} = {value!r}")
      return value
    except (KeyError, ValueError) as err:
      if self._logging: # pylint: disable=protected-access
        print(f"{callstr} raised {err!r}")
      raise
  return wrapper

class IDict(dict):
  """
  A dictionary that ignores case

  This class operates by storing an additional pairing that maps "casefolded"
  strings to their original value. The parent dictionary contains values as
  they were inserted originally.
  """
  def __init__(self, *args, **kwargs):
    self._keymap = None
    self._logging = False
    self._strict = False
    super().__init__(*args, **kwargs)

  def set_logging(self, logging):
    "If True, print out traces of every function call"
    self._logging = logging

  def set_strict(self, strict):
    "If True, throw an error if problems are found. Otherwise, ignore them"
    self._strict = strict

  def as_dict(self):
    "Return the underlying dictionary"
    return dict(self.items())

  def ensure_keymap(self):
    "Ensure self._keymap is populated and accurate"
    # Avoid calling self.* functions that'd invoke ensure_keymap
    if self._keymap is None:
      self._keymap = {casefold(key): key for key in super().keys()}
    kmkeys = set(self._keymap.values())
    dkeys = set(super().keys())
    if kmkeys != dkeys:
      differences = kmkeys.symmetric_difference(dkeys)
      errmsg = "IDict constraint violation: keymap disagreement; " \
          f"differences = {tuple(differences)!r}"
      if self._strict:
        raise ValueError(errmsg)
      warnings.warn(errmsg)

  @keymapped
  def rekey(self, oldkey, newkey):
    "Reassign a key, possibly to fix capitalization issues"
    value = super().__getitem__(oldkey)
    oldikey = casefold(oldkey)
    newikey = casefold(newkey)
    del self._keymap[oldikey]
    super().__delitem__(oldkey)
    self._keymap[newikey] = newkey
    super().__setitem__(newkey, value)

  @keymapped
  def __len__(self):
    "len(self)"
    return super().__len__()

  @keymapped
  def keys(self):
    "self.keys()"
    return super().keys()

  @keymapped
  def values(self):
    "self.values()"
    return super().values()

  @keymapped
  def items(self):
    "self.items()"
    return super().items()

  @loggable
  @keymapped
  def __setitem__(self, key, value):
    "self[key] = value"
    ikey = casefold(key)
    if ikey in self._keymap and self._keymap[ikey] != key:
      # We're updating an existing value
      key = self._keymap[ikey]
    else:
      self._keymap[ikey] = key
    return super().__setitem__(key, value)

  @loggable
  @keymapped
  def __getitem__(self, key):
    "return self[key]"
    rkey = self._keymap[casefold(key)]
    return super().__getitem__(rkey)

  @loggable
  @keymapped
  def __delitem__(self, key):
    "del self[key]"
    ikey = casefold(key)
    rkey = self._keymap[ikey]
    del self._keymap[ikey]
    return super().__delitem__(rkey)

  @loggable
  @keymapped
  def __contains__(self, key):
    "return key in self"
    ikey = casefold(key)
    if ikey in self._keymap:
      rkey = self._keymap[ikey]
      if super().__contains__(rkey):
        return True
    return False

  @loggable
  @keymapped
  def get(self, key, default=None):
    "return self.get(key, default=None)"
    if key in self:
      return self[key]
    return default

def _tests():
  "Test the above"
  base = {"ABC": "abc"}
  idict = IDict(base)
  idict.set_logging(True)
  assert len(idict) == 1
  assert len(tuple(idict.keys())) == 1
  assert len(tuple(idict.values())) == 1
  assert len(tuple(idict.items())) == 1
  assert all(len(i) == 2 for i in idict.items())
  assert "ABC" in idict
  assert "abc" in idict
  assert idict["ABC"] == "abc"
  assert idict["abc"] == "abc"
  assert " " not in idict
  idict["abc"] = "asd"
  assert idict["ABC"] == "asd"
  assert idict["abc"] == "asd"
  del idict["abc"]
  assert len(idict) == 0
  idict["ABC"] = "abc"
  idict["abc"] = "asd" # overwrite above
  assert len(idict) == 1 # assert value was overwritten
  assert "abc" in idict
  assert "ABC" in idict
  assert "aBc" in idict
  assert idict.get("ABC", 1) == "asd"
  assert idict.get("abc", 1) == "asd"
  assert idict.get(" ", 1) == 1
  assert len(idict) == 1
  del idict["Abc"]
  assert len(idict) == 0
  idict = IDict(base)
  idict.set_logging(True)
  assert "ABC" in tuple(idict)
  assert "ABC" in tuple(idict.keys())
  assert "abc" not in tuple(idict)
  assert "abc" not in tuple(idict.keys())
  assert len(idict) == 1
  idict.rekey("ABC", "abc")
  assert "ABC" not in tuple(idict)
  assert "ABC" not in tuple(idict.keys())
  assert "abc" in tuple(idict)
  assert "abc" in tuple(idict.keys())
  assert len(idict) == 1
  assert idict.as_dict() == {"abc": "abc"}

  # adversarial tests
  base = {"ABC": 1, "abc": 2}
  idict = IDict(base)
  idict.set_logging(True)
  idict.set_strict(True)
  try:
    idict.ensure_keymap()
    assert False, f"IDict failed to complain about {idict!r}"
  except ValueError as err:
    pass
  else:
    assert False, f"IDict complained about {idict!r} with {err}, not ValueError"

# vim: set ts=2 sts=2 sw=2:
