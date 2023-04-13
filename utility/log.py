#!/usr/bin/env python3
# pylint: disable=invalid-name

"""
Trace-level logger, logging colors, and other logging utilities.

This module defines logger.trace, an optional highly-configurable color
formatter, and an optional deferred logging instance.

Moreover, this module provides a convenient decorator to trace function
invocation, arguments, and return values.

Note that this module must be careful when invoking logger.* functions
to prevent infinite loops or invoking an uninitialized logger.

The function get_logger(name) supports more intelligent logger lookup:
1) Passing "main", "__main__", or the name of the main module will all
   obtain the main module's logger instance.
2) Passing "root" or "__root__" will obtain the root logger instance.
3) Passing the name of a lib.* module (without "lib.") will obtain that
   lib module's logger. For instance, get_logger("config") is equivalent
   to logging.getLogger("lib.config")
4) Everything else is passed unchanged to logging.getLogger.
"""

# TODO: Allow fragments to define an end color instead of just \e[0m
# TODO: Allow for non-CSI escape sequences
# FIXME: Move configuration handler logic outside of this module
# FIXME: Allow nested formatting of msg and quotes
# FIXME: Problem parsing msg="''" ?

import functools
import logging
import os
import sys
import traceback

LOG_FORMAT = "%(module)s:%(lineno)s: %(levelname)s: %(message)s"

PREFIX = "-"

QUOTE_CHAR = "'"

# Static trace information about the current stack frame to aid debugging
TRACE_INFO = {"stack": []}

# The special new trace level
TRACE = 5

# The global (default) color table; used if the configuration object
# doesn't include LogColors sections
COLOR_TABLE = {}

# Populate the above default color table with likely-sane default colors
def _add_color_level(level,
    level_color=None,
    name_color=None,
    module_color=None,
    path_color=None,
    file_color=None,
    line_color=None,
    message_color=None,
    quote_color=None):
  "Define (or redefine) a default/global color rule"
  COLOR_TABLE[level] = {
    "name": name_color,
    "module": module_color,
    "pathname": path_color,
    "filename": file_color,
    "lineno": line_color,
    "levelname": level_color,
    "msg": message_color,
    "quote": quote_color
  }

_add_color_level("default",
    name_color="2;3;92",
    module_color="2;3;92",
    line_color="2;96",
    quote_color="3;37")
_add_color_level(TRACE, level_color="1;2;3;96")
_add_color_level(logging.DEBUG, level_color="1;94")
_add_color_level(logging.INFO, level_color="1;32")
_add_color_level(logging.WARN, level_color="1;33")
_add_color_level(logging.ERROR, level_color="1;31")
_add_color_level(logging.CRITICAL, level_color="1;31")
del _add_color_level

def get_logger(name):
  """
  Try (intelligently) to get the desired logger

  root, __root__ => root logger instance
  main, __main__ => __main__ logger instance
  "<main_module_name>" => __main__ logger instance
  "<module>" => lib.<module> logger instance, if lib.<module> exists
  "<anything else>" => that logger
  """
  if name in ("root", "__root__"):
    return logging.root
  if name in ("main", "__main__"):
    return logging.getLogger("__main__")
  main_module = sys.modules.get("__main__")
  if main_module:
    if hasattr(main_module, "__file__"):
      module_name = os.path.basename(main_module.__file__).split(".")[0]
      if name == module_name:
        return logging.getLogger("__main__")
  if name not in sys.modules:
    if "lib." + name in sys.modules:
      return logging.getLogger("lib." + name)
  return logging.getLogger(name)

def level_for(name):
  "Get the numeric level for the given string"
  levelmap = {
    "trace": TRACE,
    "verbose": logging.DEBUG,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
  }
  # Allow for single-character aliases
  for levelname in list(levelmap):
    levelmap[levelname[0]] = levelmap[levelname]
  if name.lower() in levelmap:
    return levelmap[name.lower()]
  raise ValueError("Unknown logging level {!r}".format(name))

def get_remove(thedict, thekey, default=None, raises=False):
  """
  Remove a key from the dict and return its value.
    raises      if True, raise the KeyError if key isn't present
    default     unless raises is True, return this if the key isn't present
  """
  value = default
  if raises or thekey in thedict:
    value = thedict[thekey]   # will raise ValueError if raises=True
    del thedict[thekey]
  return value

class ColorFormatter(logging.Formatter):
  "Logging formatter to print records using console colors"

  def __init__(self, *args, **kwargs):
    """
    Construct the formatter. Arguments:
      quote           quote character; default is QUOTE_CHAR
      quote_format    boolean to enable/disable quote colors; default True
      colors          color table; default is COLOR_TABLE
    """
    self.__quote_char = get_remove(kwargs, "quote", QUOTE_CHAR)
    self.__format_quote = get_remove(kwargs, "quote_format", True)
    self.__colors = get_remove(kwargs, "colors", COLOR_TABLE)
    super(ColorFormatter, self).__init__(*args, **kwargs)

  @property
  def levels(self):
    "Get all of the levels that have colors defined"
    return tuple(self.__colors)

  def _format(self, field, color):
    "Actually format the given field"
    if color:
      return "\033[{}m{}\033[0m".format(color, field)
    return field

  def _format_quote(self, message, color):
    "Format a possible quote message piece"
    separator = self.__quote_char
    pieces = []
    for idx, piece_pair in enumerate(split_quoted(message, separator)):
      piece, inside = piece_pair
      if inside:
        piece = self._format(piece, color)
      pieces.append(piece)
    return "".join(pieces)

  def _alter_record(self, record, colordef):
    "Alter a record to use color; a bare string is assumed to be for levelname"
    if isinstance(colordef, str):
      colordef = {"levelname": colordef}
    for ckey, cvalue in colordef.items():
      if ckey == "quote":
        continue # these are handled after formatting, not during
      if hasattr(record, ckey):
        rvalue = getattr(record, ckey)
        setattr(record, ckey, self._format(rvalue, cvalue))
    return record

  def updateColor(self, forLevel, forPart, color):
    "Update a single color; forPart is ignored if forLevel='default'"
    if forPart not in self.__colors[forLevel]:
      sys.stderr.write("WARNING: Level {} lacks part {} (setting {})\n".format(
        forLevel, forPart, color))
    self.__colors[forLevel][forPart] = color

  def setFormatQuote(self, enable, quote_char=QUOTE_CHAR):
    "Enable or disable quote coloring"
    self.__format_quote = enable
    self.__quote_char = quote_char

  def dumpDebug(self, to=sys.stderr):
    "Dump the current color configuration for debugging"
    to.write(f"Format {self.__quote_char!r}: {self.__format_quote}\n")
    def sort_key(key):
      if isinstance(key, str):
        return -len(key)
      return key
    for section in sorted(self.__colors, key=sort_key):
      display = []
      for key in self.__colors[section]:
        value = self.__colors[section][key]
        if value is not None:
          display.append(f"{key}={value!r}")
      name = logging.getLevelName(section)
      if section == "default":
        name = "Default"
      to.write("{} Color: {}\n".format(name, ", ".join(display)))

  def format(self, record): # pylint: disable=redefined-builtin
    "Format a log record with color"
    colordef = {}
    # First, extract any default rules
    for key, entry in self.__colors.get("default", {}).items():
      if entry is not None:
        colordef[key] = entry
    # Next, merge any level-specific rules
    for key, entry in self.__colors.get(record.levelno, {}).items():
      if entry is not None:
        colordef[key] = entry
    # Apply any record modifications that need to be made
    if record.name == "__main__":
      record.name = record.module
    # Alter the record's fields to colorize its contents
    record = self._alter_record(record, colordef)
    # Invoke the base formatter to obtain the string
    result = super(ColorFormatter, self).format(record)
    # If quote formatting is enabled, apply that to the final string
    if self.__format_quote:
      if colordef.get("quote"):
        return self._format_quote(result, colordef["quote"])
    return result

class ColorTraceLogger(logging.Logger):
  "Logger subclass defining trace(msg, ...)"
  def __init__(self, *args, **kwargs):
    "See help(type(self))"
    self._injected = False
    self._formatter = None
    if "format" in kwargs:
      self._format = kwargs["format"]
      del kwargs["format"]
    else:
      self._format = LOG_FORMAT
    super(ColorTraceLogger, self).__init__(*args, **kwargs)

  def setFormat(self, format_string):
    "Alter the format for this logger; must be called before enableColor"
    self._format = format_string

  def enableColor(self,
      quote_char=QUOTE_CHAR,
      quote_format=True,
      color_table=None):
    """
    Enable color formatting by injecting a ColorFormatter where needed.

    FIXME: Enabling color logging on this single logger affects all loggers, as
    we modify the root logger's formatter. Not modifying the root formatter
    results in duplicated log messages to the terminal. We need a way to
    suppress the root handler after our own handler executes.
    """
    if self._injected:
      return
    if color_table is None:
      color_table = COLOR_TABLE
    self._formatter = ColorFormatter(self._format,
        quote=quote_char,
        quote_format=quote_format,
        colors=color_table)
    for inst in (self, self.root):
      if inst.hasHandlers():
        for handler in inst.handlers:
          if isinstance(handler, logging.StreamHandler):
            if not isinstance(handler.formatter, ColorFormatter):
              handler.setFormatter(self._formatter)
              self._injected = True
              break
    if not self._injected:
      handler = logging.StreamHandler(sys.stderr)
      handler.setFormatter(self._formatter)
      self.addHandler(handler)
      self._injected = True

  def applyConfig(self, conf):
    "Apply a configuration to the ColorFormatter"
    if self._formatter is not None:
      self._formatter.applyConfig(conf)

  def updateColorRule(self, forLevel, forPart, color):
    "Update a color rule"
    if forLevel == "all":
      for level in self._formatter.levels:
        self._formatter.updateColor(level, forPart, color)
    else:
      self._formatter.updateColor(forLevel, forPart, color)

  def getColorFormatter(self):
    "Get the underlying ColorFormatter handler, or None"
    return self._formatter

  def trace(self, *args, **kwargs):
    "Log a trace-level message"
    stacklevel = kwargs.get("stacklevel", 0) + 2
    if "stacklevel" in kwargs:
      del kwargs["stacklevel"]
    return self.log(TRACE, *args, **kwargs, stacklevel=stacklevel)

class DeferredLogger:
  "Logger instance that's only constructed once needed"
  REGISTERED = {}

  def __init__(self, name):
    "See help(type(self))"
    self._inst = None
    self._name = name
    DeferredLogger.REGISTERED[name] = None

  def __getattr__(self, attr):
    "getattr(self, attr)"
    if self._inst is None:
      self._inst = logging.getLogger(self._name)
      DeferredLogger.REGISTERED[self._name] = self._inst
    return getattr(self._inst, attr)

def hotpatch(logging_module):
  "Modify the logging module to use our trace logger"
  logging_module.TRACE = TRACE
  logging_module.addLevelName(TRACE, "TRACE")
  logging_module.setLoggerClass(ColorTraceLogger)

def split_quoted(text, separator, escape="\\"):
  "Split a string with quoted substrings, honoring escape sequences"
  parts = []
  part = ""
  inside = False
  escaped = False
  for char in text:
    if char in separator and not escaped:
      if part:
        parts.append((part, inside))
      parts.append((char, False))
      part = ""
      escaped = False
      inside = not inside
    else:
      part = part + char
      if char == escape:
        escaped = not escaped
      else:
        escaped = False
  if part:
    parts.append((part, False))
  return parts

def format_stack_frame(frame, depth=0):
  "Generate a quaint string describing the given FrameSummary"
  filename = os.path.relpath(frame.filename)
  prefix_str = ""
  if depth > 0:
    prefix_str = ("-" * depth) + ">"
  return "{}:{} {} in {}: {}".format(filename,
      frame.lineno, prefix_str, frame.name, frame.line)

def format_call_stack(frames=None):
  "Format the current call stack for debugging"
  if frames is None:
    frames = traceback.extract_stack()
  frames = [
    (depth,
      os.path.relpath(frame.filename),
      frame.lineno,
      frame.name,
      frame.line)
    for depth, frame in enumerate(frames)
  ]
  if frames and frames[0][3] == "<module>":
    del frames[0]
  filename_length = max(len(filename) for _, filename, _, _, _ in frames)
  lineno_length = max(len(str(lineno)) for _, _, lineno, _, _ in frames)
  for depth, filename, lineno, name, line in frames:
    filename = filename.ljust(filename_length)
    lineno = str(lineno).ljust(lineno_length)
    prefix_value = "in"
    if depth > 0:
      prefix_value = "{}> in".format("-" * depth)
    location = "{}:{}:".format(filename, lineno)
    yield "{}: {} {} {}: {}".format(location, depth, prefix_value, name, line)

def getattr_multi(object_, *attributes):
  "Return the first attribute that resolves, or None if none resolve"
  for attr_name in attributes:
    try:
      return getattr(object_, attr_name)
    except AttributeError:
      pass
  return None

def func_name(func):
  "Try to get the name of a function; returns str(func) on failure"
  fname = getattr_multi(func, "func_name", "__name__")
  if not fname:
    fname = str(func)
  return fname

def prefix(level=None):
  "Get a specific level (or the current level) prefix string"
  if level is None:
    level = len(TRACE_INFO["stack"]) - 1
  if level == 0:
    return "+"
  return "-" * level + ">"

def traced_function(logger, when="before", trace_func="trace", context=False):
  """
  Build a decorator to trace function execution.

  Arguments:
    logger        Logger instance or logger name
    when="before" Log the function call before execution
    when="after"  Log the function call and its return value after execution
    when="both"   Log the function call both before and after execution
    trace_func    Function of the logger instance to call (default trace)
    context       If True, log the calling context

  Usages:
    @traced_function(__name__)
    def my_function(*args, **kwargs): ...

    @traced_function(my_logger, when="both")
    def my_function(*args, **kwargs): ...

    @traced_function(my_logger, trace_func="debug") # calls my_logger.debug
    def my_function(*args, **kwargs): ...
  """
  # Allow for loggers by name
  if isinstance(logger, str):
    logger = logging.getLogger(logger)

  # Helper function that actually logs the function call
  def do_trace(*args, **kwargs):
    "Log a trace message with the proper stack adjustment"
    return getattr(logger, trace_func)(*args, **kwargs, stacklevel=2)

  def decorator(func):
    "Decorator that calls logger.trace on function call"
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      "Function wrapper"
      name = func_name(func)
      # If the user wants a call stack dump, give them a call stack dump
      if context:
        for frame_nr, frame in enumerate(TRACE_INFO["stack"]):
          do_trace("%s %s", prefix(frame_nr), frame)

      # Format and track the frame string for this specific function call
      args_strs = [repr(arg) for arg in args]
      args_strs.extend("{}={!r}".format(k, v) for k, v in kwargs.items())
      call_frame = "{}({})".format(name, ", ".join(args_strs))
      TRACE_INFO["stack"].append(call_frame)

      # Unless explicitly omitted, log the pre-call line
      if when in ("before", "both"):
        do_trace("%s %s", prefix(), call_frame)

      result = func(*args, **kwargs)

      # Unless explicitly omitted, log the post-call line with result value
      if when in ("after", "both"):
        do_trace("%s %s returned %r", prefix(), call_frame, result)

      # Remove the frame from the stack
      del TRACE_INFO["stack"][-1]
      return result
    return wrapper
  return decorator

# vim: set ts=2 sts=2 sw=2:
