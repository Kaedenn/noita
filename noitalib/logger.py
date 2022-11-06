#!/usr/bin/env python3

"""
The logger instance
"""

import utility.loghelper

def create(name):
  "Create a new delayed logger"
  return utility.loghelper.DelayLogger(name)

logger = create("noita")

# vim: set ts=2 sts=2 sw=2:
