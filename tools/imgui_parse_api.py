#!/usr/bin/env python3

"""
Attempt to build reference documentation for Noita Dear-ImGui
"""

import argparse
import csv
import glob
import json
import logging
import os
import re
import sys

class TraceLogger(logging.Logger):
  "Logger subclass defining trace(msg, ...)"
  TRACE = 5
  def trace(self, *args, **kwargs):
    "Log a trace-level message"
    return self.log(TraceLogger.TRACE, *args, **kwargs, stacklevel=2)

logging.TRACE = TraceLogger.TRACE
logging.addLevelName(TraceLogger.TRACE, "TRACE")
logging.setLoggerClass(TraceLogger)

LOG_FORMAT = "%(module)s:%(lineno)s: %(levelname)s: %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

logger = logging.getLogger(__name__)

BRACKETS = (
  ("<", ">"),
  ("{", "}"),
  ("(", ")"),
  ("[", "]")
)
BRACKET_ASSOC = dict(BRACKETS)

# Pattern for matching lambda functions with or without return types
R_LAMBDA = re.compile("".join((
  r"\[\]",                        # `[]` token
  r"\((?P<args>[^)}]*)\)[ ]*",    # lambda argument list
  r"(->[ ]*(?P<return>[^{]+))?",  # lambda return type (optional)
  r"(?P<body>{[^}]*})"            # lambda function body { ... }
)))

# Above, but without the groups (must match exactly!)
P_LAMBDA = "".join((
  r"\[\]",            # `[]` token
  r"\([^)}]*\)[ ]*",  # lambda argument list
  r"(->[ ]*[^{]+)?",  # lambda return type (optional)
  r"{[^}]*}"          # lambda function body { ... }
))

# [auto thing =] imgui.[func]([name], [data...])
R_DECL = re.compile("".join((
  r"^[ ]*",                         # leading whitespace
  r"(?P<prefix>[^=]*=[ ]*)?",       # possible "auto <thing> ="
  r"imgui.(?P<func>[a-z_]+)[^(]*",  # imgui.<function>
  r"\(",                            # begin argument list
  r"\"(?P<name>[^\"]+)\",",         # first argument: name of thing
  r" (?P<value>.*)",                # rest of arguments: value of thing
  r"\);$"                           # end of argument list
)))

P_SYMBOL = r"([A-Z_][A-Za-z0-9_]*::)?[A-Z_][A-Za-z0-9_]*"

VALUE_PATTERNS = {_name: re.compile(_value) for _name, _value in {
  "no-constructor": "sol::no_constructor",
  # unqualified function pointers should be phased out by 16 Mar 2023
  #"func-ptr": "(?P<function>" + P_SYMBOL + ")",
  "property-lambda": r"sol::property\((?P<lambda>" + P_LAMBDA + r")\)",
  "property-function": r"sol::property\((?P<function>" + P_SYMBOL + r")\)",
  "readonly-function": r"sol::readonly\((?P<function>" + P_SYMBOL + r")\)",
  "resolve-function": r"sol::resolve<(?P<type>.*)>\((?P<function>" + P_SYMBOL + r")\)",
  "overload": r"sol::overload\((?P<overloads>.*)\)",
  "lambda": "(?P<lambda>" + P_LAMBDA + ")",
  "enum-value": "(?P<value>[A-Z][A-Za-z0-9_]+)",
}.items()}

def is_bracket(char):
  "True if the character is a bracket, False otherwise"
  for pair in BRACKETS:
    if char in pair:
      return True
  return False

def collapse_whitespace(text):
  "Collapse consecutive whitespace"
  return re.sub("[ ]+", " ", text)

def each_line(file_path, mode="rt", rstrip=True):
  "Iterate over the file, line by line"
  with open(file_path, mode=mode) as fobj:
    for lnum, line in enumerate(fobj):
      if rstrip:
        line = line.rstrip(os.linesep)
      yield lnum, line

def get_lua_decl_files(tree_root):
  "Get the files that define Lua values"
  # Allow parsing single file(s)
  if os.path.isfile(tree_root):
    return [tree_root]
  return glob.glob(os.path.join(tree_root, "src", "lua_features", "*.cpp"))

def line_is_declaration(line):
  "True if the line adds a Lua value"
  if line.lstrip().startswith("//"):
    return False
  if "imgui.set_function" in line:
    return True
  if "imgui.new_enum" in line:
    return True
  if "imgui.new_usertype" in line:
    return True
  return False

def depths_to_string(depths):
  "Build a string representing the depths mapping"
  parts = []
  for lchar, rchar in BRACKETS:
    if depths.get(lchar, 0):
      parts.append(f"{lchar}{rchar}={depths[lchar]}")
  return "; ".join(parts)

def update_depths(depths, line):
  "Update the depths dictionary with the line content"
  total = 0
  depths_start = dict(depths)
  total_start = sum(depths.values())
  for lbracket, rbracket in BRACKETS:
    lcount = line.count(lbracket)
    rcount = line.count(rbracket)
    if rbracket == ">":
      rcount = line.count(">") - line.count("->")
    depths[lbracket] = depths.get(lbracket, 0) + lcount - rcount
    total += depths[lbracket]

  if logger.getEffectiveLevel() <= logging.TRACE:
    d_start = depths_to_string(depths_start) or "<none>"
    d_end = depths_to_string(depths) or "<none>"
    if d_start != d_end:
      logger.trace("%r: %d to %d; \"%s\" to \"%s\"", line, total_start, total,
          d_start, d_end)
    elif total:
      logger.trace("%r: no change; d=%d; \"%s\"", line, total_start, d_start)
    else:
      logger.trace("%r: no change", line)
  return total

def get_declarations(file_path):
  "Extract the C++ source code declarations from the given file"
  file_name = os.path.basename(file_path)
  with open(file_path, "rt") as fobj:
    lines = fobj.read().splitlines()

  decls = []          # list of all parsed decls
  curr_start = None   # current decl start line
  curr_end = None     # current decl end line
  curr = []           # current decl source code lines
  depths = {}         # current decl bracket depth counts

  lnum = 0
  while lnum < len(lines):
    line = lines[lnum].strip()
    lnum += 1
    if not line:
      continue
    logger.trace("%s:%d: %s", file_name, lnum, line)
    if line_is_declaration(line):
      logger.debug("%s:%d defines %r", file_name, lnum, line)
      if curr:
        if curr_end is None:
          curr_end = lnum
        decls.append((file_path, curr_start, curr_end, curr))
      curr_start = lnum
      curr_end = None
      curr = [line]
      depths = {}

      while update_depths(depths, line) > 0:
        if lnum >= len(lines):
          logger.warning("EOF parsing %s:%d %r", file_path, lnum, curr[0])
          logger.debug("\n".join(curr))
          break
        line = lines[lnum].strip()
        curr.append(line)
        lnum = lnum + 1
      curr_end = lnum

  if curr:
    decls.append((file_path, curr_start, curr_end, curr))
  return decls

def match_decl(text):
  "Match the text against the decl pattern"
  match = R_DECL.match(text)
  result = {"func": "", "name": "", "value": ""}
  if match is not None:
    result.update(match.groupdict())
    return result
  return None

def is_string(value):
  "True if the given rvalue looks like a C-string"
  return value and value[0] == value[-1] == '"'

def collate_lines(lines):
  "Combine code into a single line"
  filtered = []
  for line in lines:
    if "//" in line:
      line = line.replace("//", "/*", 1) + "*/"
    filtered.append(line)
  return collapse_whitespace(" ".join(filtered))

def comma_extract_one(code):
  "Extract one value from a comma-separated list of values"
  pos = 0
  depths = {char: 0 for char, _ in BRACKETS}

  in_string = False
  colnum = 0
  char = None
  last_char = None
  while colnum < len(code):
    last_char = char
    char = code[colnum]
    colnum += 1
    if char == '"':
      in_string = not in_string
    elif char == '\\' and in_string:
      colnum += 1
    elif is_bracket(char):
      if (last_char, char) != ("-", ">"):
        # don't count lambda expressions
        update_depths(depths, char)
    elif char == "," and not in_string and sum(depths.values()) == 0:
      logger.debug("Found identifier [:%d]: %r", colnum, code[:colnum])
      return code[:colnum-1], code[colnum:]
  return code, ""

def comma_split(code, trim=False):
  "Split a comma-separated list of values"
  values = []
  remainder = code
  while remainder:
    piece, remainder = comma_extract_one(remainder)
    if trim:
      piece = piece.strip()
      remainder = remainder.strip()
    values.append(piece)
  return values

# TODO: sol::overload<FuncType>(func1, func2, ...)
# TODO: propagate return types across overloads; they all return the same thing
def parse_function(text):
  "Parse a function to extract whatever information we can deduce about it"
  if text.startswith("sol::readonly("):
    logger.debug("Purging readonly from %r", text)
    text = text[text.index("(")+1:text.rindex(")")]

  funcinfo = {}
  for patname, pattern in VALUE_PATTERNS.items():
    match = pattern.match(text)
    if match is None:
      continue
    groups = match.groupdict()
    logger.debug("Matched %s %r", patname, text)
    logger.trace("groups: %r", groups)
    if funcinfo:
      # only one pattern should match the given code; multi-matches are
      # symptoms of bugs in the regexes
      logger.error("multi-match %r after %r", patname, funcinfo["kind"])
      logger.warning("source-text: %r", text)
      logger.warning("groups: %r", groups)
      logger.warning("prior: %r", funcinfo)
    funcinfo["kind"] = patname
    funcinfo.update(**groups)
  if not funcinfo:
    logger.warning("Parsing line %r failed", text)
  return funcinfo

def parse_enum(text):
  "Parse an enum to extract whatever information we can deduce about it"
  if "(" in text and ")" in text and text.index("(") < text.index(")"):
    text = text[text.index("(")+1:text.index(")", text.index("(")+1)]

  if "/*" in text and "*/" in text and text.index("/*") < text.index("*/"):
    startpos = text.index("/*")
    endpos = text.index("*/", startpos+2)+2
    logger.trace("Purging comment %r from %r", text[startpos:endpos], text)
    text = text[:startpos] + text[endpos:]

  rvalues = comma_split(text, trim=True)
  result = {"order": 1, "data": rvalues}
  if all(is_string(value) for value in rvalues[::2]):
    # it's a plain string-literal enumeration with no variable keys
    result["order"] = 2
    result["data"] = tuple((name.strip('"'), parse_function(value))
      for name, value in zip(rvalues[::2], rvalues[1::2]))
  return result

def parse_usertype(text):
  "Parse a usertype to extract whatever information we can deduce about it"
  return {}

def parse_declaration(declobj):
  "Parse a single declaration object"
  lines = declobj["value"]
  kind = None
  data = {}
  try:
    if declobj["func"] == "set_function":
      kind = "function"
      data = parse_function(lines)
    elif declobj["func"] == "new_enum":
      kind = "enum"
      data = parse_enum(lines)
    elif declobj["func"] == "new_usertype":
      kind = "usertype"
      data = parse_usertype(lines)
    else:
      logger.warning("Unknown decl type %s", declobj["func"])
      logger.warning("While parsing %s: %d: %s", declobj["file"],
          declobj["lines"][0], declobj["name"])
  except ValueError as err:
    logger.error("Parse failure parsing %s: %d: %s", declobj["file"],
          declobj["lines"][0], declobj["name"])
    logger.warning(declobj)
    logger.error(err)
  return kind, data

def dump_csv(matches, to_fobj=sys.stdout):
  "Dump the matches to the file object as CSV"
  csvw = csv.writer(to_fobj)
  csvw.writerow(("File", "Start Line", "End Line", "Type", "Name", "Code", "Data"))
  for match in matches:
    logger.trace(match)
    if csvw is not None:
      row = []
      row.append(match["file"])
      row.extend(str(num) for num in match["lines"])
      row.append(match["parse-kind"])
      row.append(match["name"])
      row.append(match["value"])
      row.append(json.dumps(match["data"]))
      csvw.writerow(row)

def dump_json(matches, to_fobj=sys.stdout):
  "Dump the matches to the file object as JSON"
  json.dump(matches, to_fobj, indent=2)
  to_fobj.write(os.linesep)

def dump_plain(matches, to_fobj=sys.stdout):
  "Dump the matches to the file object as normal text"
  for match in matches:
    print("{} imgui.{} = {!r}".format(
      match["func"], match["name"], match["value"]))

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("path", help="path to the Noita-Dear-ImGui repo")
  ag = ap.add_argument_group("output")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-c", "--csv", action="store_true", help="generate CSV")
  mg.add_argument("-j", "--json", action="store_true", help="generate JSON")
  ag = ap.add_argument_group("diagnostics")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-v", "--verbose", action="store_true", help="verbose output")
  mg.add_argument("-t", "--trace", action="store_true", help="trace output")
  args = ap.parse_args()
  if args.verbose:
    logger.setLevel(logging.DEBUG)
  if args.trace:
    logger.setLevel(logging.TRACE)

  decls = []
  for file_path in get_lua_decl_files(args.path):
    logger.debug("Scanning %r", file_path)
    decls.extend(get_declarations(file_path))
  logger.debug("Scanned %d declarations", len(decls))

  matches = []
  # Ensure everything matches and parse out the relevant data
  for path, start, end, lines in decls:
    decl = collate_lines(lines)
    filename = os.path.basename(path)
    logger.debug("%s[%d~%d]: %r", filename, start, end, decl)
    groups = match_decl(decl)
    if groups:
      match = {
        "file": filename,
        "path": path,
        "lines": (start, end),
        "func": groups["func"],
        "name": groups["name"],
        "value": groups["value"],
        "prefix": groups["prefix"],
        "parse-kind": None,
        "data": None,
      }
      declkind, decldata = parse_declaration(match)
      match["parse-kind"] = declkind
      match["data"] = decldata
      matches.append(match)
    else:
      logger.warning("Decl at %s[%d~%d] doesn't match pattern; %r",
          filename, start, end, decl)
      logger.warning("Decl lines: %s", "\n".join(lines))

  if args.csv:
    dump_csv(matches, to_fobj=sys.stdout)
  elif args.json:
    dump_json(matches, to_fobj=sys.stdout)
  else:
    dump_plain(matches, to_fobj=sys.stdout)

if __name__ == "__main__":
  main()

# vim: set ts=2 sts=2 sw=2:
