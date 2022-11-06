#!/usr/bin/env python3

"""
Add "trace" as a more-verbose-than-verbose logging level.
"""

import logging

TRACE = 5

class TraceLogger(logging.Logger):
  "Logger subclass defining trace(msg, ...)"
  def trace(self, *args, **kwargs):
    "Log a trace-level message"
    return self.log(TRACE, *args, **kwargs, stacklevel=2)

def hotpatch(logging_module):
  "Modify the logging module to use our trace logger"
  logging_module.TRACE = TRACE
  logging_module.addLevelName(TRACE, "TRACE")
  logging_module.setLoggerClass(TraceLogger)

# vim: set ts=2 sts=2 sw=2:
