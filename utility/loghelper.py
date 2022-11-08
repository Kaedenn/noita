#!/usr/bin/env python3

"""
Define a "delay logger" that is constructed only once needed

This allows for creating global loggers while still permitting
logging.basicConfig usage without needing to take special care with
with import order.
"""

import logging
import os
import sys

from . import tracelog
tracelog.hotpatch(logging)

LEVEL_CODES = {
  "T": logging.TRACE, # pylint: disable=no-member
  "D": logging.DEBUG,
  "I": logging.INFO,
  "W": logging.WARNING,
  "E": logging.ERROR,
  "F": logging.FATAL
}

_LOGGERS = {}

def get_loggers():
  """
  Obtain all (name, DelayLogger, logging.Logger) triples

  If the third element is None, then the specific logger hasn't been
  initialized yet.
  """
  for log_name, log_data in _LOGGERS.items():
    wrapper = log_data["wrapper"]
    logger = log_data["logger"]
    yield log_name, wrapper, logger

def apply_level(logger_name, level_code):
  """
  Configure the named logger to have the given level

  The following special logger names are understood:
    __root__    get the root logger (name = None)
    __name__    get the main logger
    __main__    get the main logger
  """
  if level_code not in LEVEL_CODES:
    raise ValueError(f"Invalid level code {level_code!r}")
  level = LEVEL_CODES[level_code]
  if logger_name == "__root__":
    logger = logging.root
  elif logger_name in ("__name__", "__main__"):
    logger_name = "__main__"
    logger = logging.getLogger(logger_name)
  elif logger_name in _LOGGERS:
    if _LOGGERS[logger_name]["logger"] is not None:
      logger = _LOGGERS[logger_name]["logger"]
    else:
      logger = logging.getLogger(logger_name)
      _LOGGERS[logger_name]["wrapper"].apply(logger)
  else:
    logger = logging.getLogger(logger_name)
  logger.setLevel(level)

BASE_FACTORY = logging.getLogRecordFactory()
def _create_log_record(*args, **kwargs):
  "Custom LogRecord factory"
  record = BASE_FACTORY(*args, **kwargs)
  if record.name == "__main__":
    record.name = record.module
  return record

def _register_logger(name, delay_inst, logger_inst):
  "Register (or re-register) a delay logger"
  _LOGGERS[name] = {"wrapper": delay_inst, "logger": logger_inst}

class DelayLogger:
  "Simple logger wrapper that constructs the logger only when needed"
  def __init__(self, name):
    "See help(type(self)) for signature"
    _register_logger(name, self, None)
    self._name = name
    self._logger = None

  @property
  def name(self):
    "Get self._name"
    return self._name

  @property
  def initialized(self):
    "True if self._logger is not None, False otherwise"
    return self._logger is not None

  def unwrap(self):
    "Get the wrapped logger, or None if it doesn't exist"
    return self._logger

  def apply(self, logger, reregister=True):
    "Use the given logger"
    self._logger = logger
    if reregister:
      _register_logger(self._name, self, self._logger)

  def __getattr__(self, attr):
    "Construct the logger when needed"
    if self._logger is None:
      self._logger = logging.getLogger(self._name)
      _register_logger(self._name, self, self._logger)
    return getattr(self._logger, attr)

def _init():
  "Initialize the module for import"
  logging.setLogRecordFactory(_create_log_record)

if __name__ != "__main__": # module init code
  _init()

# vim: set ts=2 sts=2 sw=2:
