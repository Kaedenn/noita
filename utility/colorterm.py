#!/usr/bin/env python

"""
CSI Console Escape Sequences: Console Colors API

This module defines a class for displaying colored text to the console, using
CSI escape sequences. Usage information:

Import either `Formatter` or `ColorFormatter` (they're the same thing):
  from colorterm import Formatter as C
  from colorterm import ColorFormatter as C

Format some text:
  text = C(C.BOLD, "some bold text")
  text = C(C.BOLD, C.RED, "some bold and red text")
  text = C(C.BOLD, C.RED, C.WHT_BG, "bold red on white")
  text = C.format("some bold text", C.BOLD)
  text = C.format("some bold and red text", C.BOLD, C.RED)
  text = C.format("bold red on white", C.BOLD, C.RED, C.WHT_BG)
  text = C.format("bright white", C.WHT_B)
  text = C.format("bright blue on black", C.BLU_B, C.BLK_BG)

Supported attributes:
  C.BOLD
  C.HALF
  C.ITALIC
  C.UNDERLINE
  C.REVERSE

Supported colors:
  BLK   Black
  RED   Red
  GRN   Green
  BRN   Brown (or yellow on some systems)
  BLU   Blue
  MAG   Magenta
  CYN   Cyan
  WHT   White
  DFLT  Default color (reset foreground/background)

Supported prefixes/suffixes:
  B_<color>     Select bright foreground color
  BFG_<color>   Select bright foreground color (equivalent to B_<color>)
  BBG_<color>   Select bright background color (not supported everywhere)
  <color>_FG    Select foreground color
  <color>_BG    Select background color
Note that <color> and <color>_FG are identical.

Attribute and color aliases:
  YEL       Linked to BRN_FG
  YEL_FG    Linked to BRN_FG
  YEL_BG    Linked to BRN_BG
  ITAL      Linked to ITALIC
  UND       Linked to UNDERLINE
  UNDER     Linked to UNDERLINE
  B         Linked to BOLD
  H         Linked to HALF
  I         Linked to ITALIC
  U         Linked to UNDERLINE
  R         Linked to REVERSE

Note that for all colors, <color> and <color>_FG are identical. The "_FG"
attributes are provided to make certain complex code more readable.

Note that the numerical code can be used directly instead of the attribute
name. See the console_codes(4) manpage for a list of all supported attributes
and their effects. For example:
  text = C(7, "reverse video text")

The following code will provide the same API but without formatting, in case
this module is unavailable:

class DefaultColorFormatter(object):
  def __getattr__(self, key):
    return None
  def __call__(self, *args):
    return args[-1]
C = DefaultColorFormatter()
"""

import re
import sys

# Globals
CSI_RE = re.compile("\033\\[[0-9;]*m") # Escape sequence regex
FMT = "\033[{}m"      # Escape sequence format string
END = FMT.format(0)   # Special "reset" sequence
FG, BG = 30, 40       # Starting indexes for foreground/background colors
FGBRIGHT = 90         # Starting index for bright foreground colors
BGBRIGHT = 100        # Starting index for bright background colors

class ColorFormatterClass:
  """
  Color formatter class: format a string with various CSI console escape
  sequences (see console_codes manpage).

  ColorFormatterClass.__call__ is an alias to ColorFormatterClass.format.

  Examples:
    C = ColorFormatterClass()
    C(C.BLU, "blue string")
    C(C.RED, C.BOLD, "bold red")
    C.format("bold red", C.RED, C.BOLD)
    C.format("black on white", C.BLK, C.WHT_BG)
  """
  def __init__(self):
    self._enabled = True
    # Attributes (subset)
    self._attrs = {
      "BOLD": 1,
      "HALF": 2,
      "ITALIC": 3,
      "UNDERLINE": 4,
      "REVERSE": 7
    }
    # Underlying color codes (not public; values are added to FG or BG)
    self._colors = {
      "BLK": 0, "RED": 1, "GRN": 2, "BRN": 3,
      "BLU": 4, "MAG": 5, "CYN": 6, "WHT": 7,
      "DFLT": 9
    }
    # Alternate names for color codes
    self._color_aliases = {
      "YEL": "BRN",
      "BLACK": "BLK",
      "GREEN": "GRN",
      "BROWN": "BRN",
      "YELLOW": "BRN",
      "BLUE": "BLU",
      "MAGENTA": "MAG",
      "CYAN": "CYN",
      "WHITE": "WHT",
      "DEF": "DFLT",
      "DEFAULT": "DFLT",
    }
    # Alternate names for attribute codes
    self._attr_aliases = {
      "ITAL": "ITALIC",
      "UND": "UNDERLINE",
      "UNDER": "UNDERLINE",
      "B": "BOLD",
      "H": "HALF",
      "I": "ITALIC",
      "U": "UNDERLINE",
      "R": "REVERSE",
    }
    self._extras = {}

  def enable(self):
    "Enable (or re-enable) formatting"
    self._enabled = True

  def disable(self):
    "Disable formatting (for supporting --no-color arguments)"
    self._enabled = False

  def add_color_alias(self, name, value):
    "Add a new alias"
    self._color_aliases[name] = value

  def add_attr_alias(self, name, value):
    "Add a new attribute alias"
    self._attr_aliases[name] = value

  def add_attr(self, name, value):
    "Add an attribute"
    self._attrs[name] = value

  def add_extra(self, name, value):
    "Add a new attribute"
    self._extras[name] = value

  def _parse_color_list(self, args): # pylint: disable=no-self-use
    "Parse a tuple of colors into a list of escape code values"
    clist = []
    for arg in args:
      if isinstance(arg, (list, tuple)):
        clist.extend(arg)
      elif isinstance(arg, str):
        clist.extend(arg.split(";"))
      else:
        clist.append(int(arg))
    return clist

  def get_color(self, key):
    "Like get_value(), but limited to colors"
    adjust = FG
    adjusts = {
      "FG": FG,
      "BG": BG,
      "B": FGBRIGHT,
      "BFG": FGBRIGHT,
      "BBG": BGBRIGHT
    }
    cname, cmod = key, None
    if "_" in key:
      cname, cmod = key.rsplit("_", 1)
      adjust = adjusts.get(cmod, FG)

    if cname in self._colors:
      return self._colors[cname] + adjust

    if cname in self._color_aliases:
      cval = self._color_aliases[cname]
      if cmod:
        return self.get_value(cval + "_" + cmod)
      return self.get_value(cval)
    return None

  def get_value(self, key):
    "Obtain the value of a specific string"
    if key == "RESET":
      return 0
    if key in self._extras:
      return self._extras[key]
    if key in self._attrs:
      return self._attrs[key]
    if key in self._attr_aliases:
      return self.get_value(self._attr_aliases[key])
    return self.get_color(key)

  def __getattr__(self, key):
    "Obtain the value of a specific attribute"
    value = self.get_value(key)
    if value is not None:
      return value
    raise AttributeError(key)

  def get_name(self, num):
    "Return the attribute corresponding to the number given"
    def from_value(mapping, value):
      "Look up all keys having a given value"
      return [key for key, val in mapping.items() if val == value]

    cvals = set(self._colors.values())
    if num == 0:
      return "RESET"
    if num in self._attrs.values():
      return from_value(self._attrs, num)[0]
    if num in self._extras:
      return from_value(self._extras, num)[0]
    if num >= BGBRIGHT and num - BGBRIGHT in cvals:
      return from_value(self._colors, num - BGBRIGHT)[0] + "_BBG"
    if num >= FGBRIGHT and num - FGBRIGHT in cvals:
      return from_value(self._colors, num - FGBRIGHT)[0] + "_BFG"
    if num >= FG and num - FG in cvals:
      return from_value(self._colors, num - FG)[0] + "_FG"
    if num >= BG and num - BG in cvals:
      return from_value(self._colors, num - BG)[0] + "_BG"
    return str(num)

  def __call__(self, *args):
    "Format args[-1] with args[:-1] colors and/or attributes"
    return self.format(args[-1], *args[:-1])

  def format(self, string, *args):
    "Format `string` with `args` colors and/or attributes"
    if self._enabled:
      colors = self._parse_color_list(args)
      code = FMT.format(";".join(str(clr) for clr in colors))
      return code + string + END
    return string

# Public API

# pylint: disable=invalid-name
ColorFormatter = Formatter = ColorFormatterClass()
# pylint: enable=invalid-name

def str_length(strval):
  "Return the length of a string, minus the escape sequences"
  pats = re.findall(CSI_RE, strval)
  return len(strval) - sum(len(pat) for pat in pats)

# Private API

def _test():
  "Run numerous self-tests"
  # pylint: disable=protected-access
  print("Running tests")
  state = {"n": 0}
  F = Formatter # pylint: disable=invalid-name
  def assert_eq(val1, val2, message=None):
    "Assert val1 == val2 with an optional message"
    state["n"] += 1
    msg = "{!r} == {!r}".format(val1, val2)
    if message is not None:
      msg += ": " + message
    assert val1 == val2, msg

  def test_format_call(strval, *colors):
    """
    format/__call__ tests: ensure the following hold:
      Formatter.__call__() and Formatter.format() give identical results
      str_length() gives len(strval) for both __call__() and format() strings
    """
    sval1 = F(*(list(colors) + [strval]))
    sval2 = F.format(*([strval] + list(colors)))
    assert_eq(sval1, sval2,
        "call == format '{!r}' with colors {!r}".format(strval, colors))
    assert_eq(str_length(sval1), len(strval),
        "len({!r}) == len({!r}) {}".format(sval1, strval, len(strval)))
    assert_eq(str_length(sval2), len(strval),
        "len({!r}) == len({!r}) {}".format(sval2, strval, len(strval)))
    print("format({!r}, {}) == \"{}\"".format(strval, colors, sval1))

  test_format_call("") # null empty test
  test_format_call("null test") # null non-empty test
  test_format_call("basic test", F.RED)
  test_format_call("fg and bg test", F.RED, F.WHT_BG)
  test_format_call("fg and bg test", F.RED_FG, F.WHT_BG)
  test_format_call("fg and bg test", F.RED_B, F.WHT_BG)
  test_format_call("fg, bg, attr test", F.BOLD, F.RED_FG, F.WHT_BG)

  # name -> number tests
  for color in F._colors:
    test_format_call("color {} FG".format(color), getattr(F, color + "_FG"))
    test_format_call("color {} B".format(color), getattr(F, color + "_B"))
    test_format_call("color {} BFG".format(color), getattr(F, color + "_BFG"))
    test_format_call("color {} BG".format(color), getattr(F, color + "_BG"))
    test_format_call("color {} BBG".format(color), getattr(F, color + "_BBG"))

  # number -> name for attrs
  for aname, anum in F._attrs.items():
    assert_eq(F.get_name(anum), aname)

  # number -> name for colors
  for cname, cnum in F._colors.items():
    assert_eq(F.get_name(cnum + FG), cname + "_FG")
    assert_eq(F.get_name(cnum + BG), cname + "_BG")
    assert_eq(F.get_name(cnum + FGBRIGHT), cname + "_BFG")
    assert_eq(F.get_name(cnum + BGBRIGHT), cname + "_BBG")

  # number -> name for attr aliases
  for aname, avalue in F._attr_aliases.items():
    valnum = getattr(F, aname)
    print("getattr(F, {}) == {}".format(aname, valnum))
    name = F.get_name(valnum)
    assert_eq(name, avalue)

  # number -> name for color aliases
  for aname, avalue in F._color_aliases.items():
    valnum = getattr(F, aname)
    print("getattr(F, {}) == {}".format(aname, valnum))
    name = F.get_name(valnum)
    if name.endswith("_FG"):
      name = name[:-3]
    if name.endswith("_BFG"):
      name = name[:-4] + "_B"
    assert_eq(name, avalue)

  # extra attributes
  F.add_attr("BLINK", 5)
  assert_eq(F.get_name(5), "BLINK")
  print(F(F.BLINK, "this text blinks"))

  F.add_attr("PUR8", "38;5;201")
  assert_eq(F.get_name("38;5;201"), "PUR8")
  print(F(F.PUR8, "should be a nice purple"))

  F.add_attr("RED24", "48;2;255;0;0")
  assert_eq(F.get_name("48;2;255;0;0"), "RED24")
  print(F(F.RED24, "this text is a very bright red"))

  print("{} tests done".format(state["n"]))

if __name__ == "__main__":
  if "--test" in sys.argv:
    _test()

# vim: set ts=2 sts=2 sw=2:
