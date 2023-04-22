#!/usr/bin/env python3

"""
Attempt to build reference documentation for Noita Dear-ImGui
"""

# TODO: Improve depth scanning logic using a stack; a closing bracket should
# discard any open brackets between the closing bracket and its previous match.
#   { if (x < 1) { return null } }
#              ^ discard open `<` here

import argparse
import csv
import glob
import json
import logging
import os
import re
import sys

# Ensure we can import the utility modules
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utility import log
log.hotpatch(logging)

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
  r"(?P<body>{.*})"               # lambda function body { ... }
)))

# Above, but without the groups (must match exactly!)
P_LAMBDA = "".join((
  r"\[\]",            # `[]` token
  r"\([^)}]*\)[ ]*",  # lambda argument list
  r"(->[ ]*[^{]+)?",  # lambda return type (optional)
  r"{.*}"             # lambda function body { ... }
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

# Function type "rtype(args...)"
R_FUNCTYPE = re.compile("".join((
  r"(?P<return>[^\(]*)\((?P<args>(.*))\)"
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

class BracketParser:
  """
  Class to facilitate parsing nested brackets/parentheses/etc
  """
  def __init__(self, brackets=BRACKETS):
    "See help(type(self))"
    self._brackets = list(brackets)
    self._bracket_assoc = dict(brackets)
    self._bracket_set = set()
    for left, right in self._brackets:
      self._bracket_set.add(left)
      self._bracket_set.add(right)
    self._depths = self.get_empty_depths()
    self._buffer = []
    self._stack = []

  def get_empty_depths(self):
    "Build a dict representing an empty depths association"
    return {char: 0 for char in self._bracket_assoc}

  def is_left(self, bracket):
    "True if the bracket is a left bracket"
    return any(bracket == left for left, _ in self._brackets)

  def is_right(self, bracket):
    "True if the bracket is a right bracket"
    return any(bracket == right for _, right in self._brackets)

  def get_other(self, bracket):
    "Get the other bracket for the given bracket"
    for left, right in self._brackets:
      if bracket == left:
        return right
      if bracket == right:
        return left
    return None

  @property
  def bufsize(self):
    "Get the number of characters in the current buffer"
    return len(self._buffer)

  def buffer(self):
    "Get the current buffer as a string"
    return "".join(self._buffer)

  def depths(self):
    "Get a copy of the current depths assoc"
    return dict(self._depths)

  def stack(self):
    "Get a copy of the current parsing stack"
    return tuple(self._stack)

  def _push_bracket(self, bracket):
    "Add a bracket to the stack, buffer, and depths"
    self._depths[bracket] += 1
    self._stack.append({
      "pos": self.bufsize,
      "char": bracket
    })
    self._buffer.append(bracket)

  def _pop_bracket(self, bracket):
    "Remove a bracket from the stack and extract the balanced token"
    open_bracket = self.get_other(bracket)
    frame = None
    while len(self._stack) > 0:
      frame = self._stack.pop() # failure to find shouldn't clear stack
      if frame["char"] == open_bracket:
        break
      logger.debug("Skipping half-open bracket %r", frame)
    # TODO

  def feed_one(self, char):
    "Feed a single character to the parser"
    if char in self._bracket_set:
      if char in self._bracket_assoc:
        # left bracket
        # TODO
        pass
      else:
        # right bracket
        # TODO
        pass

  def feed(self, line):
    "Feed text to the parser logic"
    depths_start = self.depths()
    for char in line:
      if char not in self._bracket_set:
        self._buffer.append(char)
        continue
      # TODO

  def reset(self):
    "Mark the end of the parsing logic and obtain any unfinished code"
    result = self.buffer()
    self._depths = self.get_empty_depths()
    self._buffer = []
    self._stack = []
    return result

  def __len__(self):
    "Convenience wrapper for self.bufsize"
    return self.bufsize

  def __str__(self):
    "str(self)"
    return "BracketParser(buffer={!r}, depths={}, stack={})".format(
        self._buffer, self._depths, self._stack)

  __repr__ = __str__

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

def remap_type(typename):
  "Map a C or C++ type to something more Lua-friendly"
  # Don't break if we're given None, an empty string, or an empty list/tuple
  if not typename:
    return "<unknown>"

  # We do handle ["typename", "varname"] pairs or ["typename"] singletons
  if isinstance(typename, (list, tuple)):
    typepart = typename[0]
    varpart = "<unnamed>"
    if len(typename) > 1:
      if len(typename) > 2:
        logger.warning("Too many components to type %r", typename)
      varpart = typename[1]
    return " ".join(remap_type(typepart), varpart)

  # Everything else must be strings
  if not isinstance(typename, str):
    logger.warning("Invalid remap_type argument %r", typename)
    return repr(typename)

  # Perform specific remaps for common C or C++ types

  typename = typename.replace("sol::object", "object")
  typename = typename.replace("sol::this_state", "this")
  typename = typename.replace("std::string", "ref string")
  typename = typename.replace("const char*", "string")
  typename = typename.replace("sol::table", "table")

  if typename.startswith("std::optional<"):
    _, targs = template_split(typename, recurse=False)
    if not targs:
      logger.warning("Failed to extract std::optional argument from %r",
          typename)
      return typename

    if len(targs) > 1:
      logger.warning("std::optional only takes one argument; %r has %d",
          typename, len(targs))
    return remap_type(targs[0])

  if typename.startswith("std::tuple<"):
    _, targs = template_split(typename, recurse=False)
    targs = [remap_type(targ) for targ in targs]
    return "[" + ", ".join(targs) + "]"

  #if typename.endswith("*") or "* " in typename:
  #  typename = "ref " + typename.replace("*", "", 1)

  if typename.startswith("std::tuple<"):
    typenames = typename[typename.index("<")+1:typename.rindex(">")]
    subtypes = comma_split(typenames, trim=True)
    return "[" + ", ".join(remap_type(subtype) for subtype in subtypes) + "]"

  return typename

def template_split(value, recurse=True):
  "Extract template class and template arguments"
  if "<" not in value:
    return value, None
  lpos = value.find("<") + 1
  rpos = len(value)

  # Find the matching bracket (when the depth goes from 0 to -1)
  depth = 0
  for pos, char in enumerate(value[lpos:]):
    if char == "<":
      depth += 1
    elif char == ">":
      depth -= 1
    if depth < 0:
      rpos = lpos + pos
      break
  if rpos >= len(value) or value[rpos] != ">":
    logger.warning("Parsing template %r failed [%d, %d]", value, lpos, rpos)

  ttype = value[:lpos-1]
  targs = comma_split(value[lpos:rpos], trim=True)
  logger.debug("Parsed %s %s from %s[%d:%d]", ttype, targs, value, lpos, rpos)
  if recurse:
    targs = [template_split(targ, recurse=True) for targ in targs]
  return ttype, targs

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

def value_strip(thedict):
  "Strip every string value in the given dict"
  for key in thedict:
    if isinstance(thedict[key], str):
      thedict[key] = thedict[key].strip()
  return thedict

def parse_function(text):
  "Parse a function to extract whatever information we can deduce about it"
  funcinfo = {}

  #if text.startswith("sol::readonly("):
  #  logger.debug("Purging readonly from %r", text)
  #  text = text[text.index("(")+1:text.rindex(")")]
  #  funcinfo["readonly"] = True

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

  # Extract return type and parameter list from function type
  if funcinfo.get("type"):
    logger.debug("Parsing type %r for %r", funcinfo["type"], text)
    match = R_FUNCTYPE.match(funcinfo["type"])
    if match is not None:
      groups = value_strip(match.groupdict())
      funcinfo["return"] = groups["return"]
      funcinfo["args"] = comma_split(groups["args"], trim=True)
    else:
      logger.warning("Parsing type %r (of %r) failed", funcinfo["type"], text)

  # Extract the return type, argument list, and body of a lambda
  if funcinfo["kind"] == "lambda":
    match = R_LAMBDA.match(funcinfo["lambda"])
    if match is not None:
      groups = value_strip(match.groupdict())
      if groups.get("args"):
        groups["args"] = comma_split(groups["args"], trim=True)
      funcinfo.update(**groups)
    else:
      logger.warning("Recursive parse of lambda %r failed", funcinfo["lambda"])

  # Extract each overload and parse them separately
  elif funcinfo["kind"] == "overload":
    funcinfo["functions"] = []
    for piece_full in comma_split(funcinfo["overloads"]):
      piece = piece_full.strip()
      pieceinfo = parse_function(piece)
      pieceinfo["text"] = piece
      funcinfo["functions"].append(pieceinfo)

    rtypes = [fun["return"] for fun in funcinfo["functions"] if fun["return"]]
    num_rtypes = len(rtypes)
    num_funcs = len(funcinfo["functions"])
    if not rtypes:
      logger.warning("No return types for functions %s", funcinfo)
    elif num_rtypes != num_funcs:
      if len(set(rtypes)) != 1:
        logger.warning("Inconsistent return types %r (%d of %d, %d unique)",
            rtypes, num_rtypes, num_funcs, len(set(rtypes)))
        logger.warning("While processing funcinfo %r", funcinfo)
      else:
        for func in funcinfo["functions"]:
          if not func["return"]:
            func["return"] = rtypes[0]

  # If we didn't find a name but have a function reference, use that
  if not funcinfo.get("name") and funcinfo.get("function"):
    funcinfo["name"] = funcinfo["function"]
    # Strip any ImGui:: prefix 
    if funcinfo["name"].startswith("ImGui::"):
      funcinfo["name"] = funcinfo["name"][len("ImGui::"):]

  # Apply type transformations to the return type and arguments
  if funcinfo.get("return"):
    funcinfo["return"] = remap_type(funcinfo["return"])
  if funcinfo.get("args"):
    funcinfo["args"] = [remap_type(arg) for arg in funcinfo["args"]]

  return value_strip(funcinfo)

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

def parse_usertype(text): # TODO
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

def dump_function_plain(funcdef, parent=None, to_fobj=sys.stdout):
  "Dump a single function to the file object"
  rtype = funcdef.get("return")
  if not rtype:
    #logger.warning("Untyped function %r", funcdef)
    rtype = "<unknown>"

  args = []
  for arg in funcdef.get("args", ()):
    if isinstance(arg, (list, tuple)):
      if len(arg) == 1:
        args.append(f"<unknown> {arg}")
      else:
        args.append(f"{arg[0]} {arg[1]}")
    else:
      args.append(arg)

  name = funcdef.get("name")
  if not name and parent is not None:
    name = parent.get("name")
  if not name:
    logger.warning("Unnamed function %r", funcdef)
    if parent is not None:
      logger.warning("With unnamed parent %r", parent)
    name = "<unnamed>"

  to_fobj.write(f"{rtype} {name}({', '.join(args)})\n")

def dump_plain(matches, to_fobj=sys.stdout):
  "Dump the matches to the file object as normal text"
  for match in matches:
    if match["parse-kind"] == "function":
      mdata = match["data"]
      if mdata["kind"] == "overload":
        for submatch in mdata["functions"]:
          dump_function_plain(submatch, parent=match, to_fobj=to_fobj)
      else:
        dump_function_plain(mdata, parent=match, to_fobj=to_fobj)

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("path", help="path to the Noita-Dear-ImGui repo")
  ag = ap.add_argument_group("output")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-c", "--csv", action="store_true", help="generate CSV")
  mg.add_argument("-j", "--json", action="store_true", help="generate JSON")
  ag = ap.add_argument_group("diagnostics")
  ag.add_argument("-C", "--no-color", action="store_true",
      help="disable logging colors")
  ag.add_argument("--color-quotes", action="store_true",
      help="apply color to quoted logging messages")
  ag.add_argument("--quote-char", metavar="CHAR", default=log.QUOTE_CHAR,
      help="use this character for quoting color (default: %(default)r)")
  ag.add_argument("--dump-color-table", action="store_true",
      help="dump the logging color setup for debugging")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-e", "--errors", action="store_const", const=logging.ERROR,
      dest="level", help="disable diagnostics below errors")
  mg.add_argument("-w", "--warnings", action="store_const", const=logging.WARNING,
      dest="level", help="disable diagnostics below warnings")
  mg.add_argument("-v", "--verbose", action="store_const", const=logging.DEBUG,
      dest="level", help="enable verbose output")
  mg.add_argument("-t", "--trace", action="store_const", const=logging.TRACE,
      dest="level", help="enable trace output")
  args = ap.parse_args()
  if not args.no_color:
    logger.enableColor(quote_format=args.color_quotes,
        quote_char=args.quote_char)
  if args.level:
    logger.setLevel(args.level)

  if args.dump_color_table:
    logger.getColorFormatter().dumpDebug()

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
