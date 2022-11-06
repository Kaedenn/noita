#!/usr/bin/env python3

"""
Simple ACF file parser
"""

import enum
import re

import utility.loghelper
from . import idict

ACF_WS = r"[\s]*"
ACF_VALUE_FORMAT = r'"([^"]+)"'
ACF_BLOCK_OPEN = re.compile(rf"^{ACF_WS}\{{{ACF_WS}$")
ACF_BLOCK_CLOSE = re.compile(rf"^{ACF_WS}\}}{ACF_WS}$")
ACF_KEY = re.compile(rf"{ACF_WS}{ACF_VALUE_FORMAT}{ACF_WS}$")
ACF_KEY_BLOCK = re.compile(rf"{ACF_WS}{ACF_VALUE_FORMAT}[\s]*\{{{ACF_WS}$")
ACF_PAIR = re.compile(rf"{ACF_WS}{ACF_VALUE_FORMAT}[\s]+{ACF_VALUE_FORMAT}{ACF_WS}$")

logger = utility.loghelper.DelayLogger(__name__)

class Token(enum.Enum):
  "Parser tokens"
  BLOCK_OPEN = "open"
  BLOCK_CLOSE = "close"
  VALUE = "value"
  VALUE_BLOCK = "value-block"
  PAIR = "value-pair"
  BAD = "bad"
  NONE = "none"

def line_value(line):
  "Parse the single line"
  ltext = line.lstrip("\t").rstrip("\r\n")
  if not ltext:
    return None, Token.NONE
  if ACF_BLOCK_OPEN.match(ltext):
    return None, Token.BLOCK_OPEN
  if ACF_BLOCK_CLOSE.match(ltext):
    return None, Token.BLOCK_CLOSE
  mat = ACF_KEY_BLOCK.match(ltext)
  if mat is not None:
    return mat.groups(), Token.VALUE_BLOCK
  mat = ACF_KEY.match(ltext)
  if mat is not None:
    return mat.groups(), Token.VALUE
  mat = ACF_PAIR.match(ltext)
  if mat is not None:
    return mat.groups(), Token.PAIR
  return None, Token.BAD

def descend(thedict, thepath):
  "Follow a path through a dict, treating it like a tree"
  if thepath:
    curr, rest = thepath[0], thepath[1:]
    return descend(thedict[curr], rest)
  return thedict

def parse_acf_text(text, filepath=None):
  "Parse the given text using the acf format"
  from_path = filepath if filepath else "<unnamed>"
  blocks = idict.IDict()
  curr_path = []
  lines = text.splitlines()
  lnr = 0
  while lnr < len(lines):
    line = lines[lnr]
    curr_block = descend(blocks, curr_path)
    next_line = lines[lnr+1] if lnr+1 < len(lines) else ""
    tokens, tkind = line_value(line)
    if tkind == Token.NONE:
      pass
    elif tkind == Token.BAD:
      logger.error("%s:%d: invalid line %r", from_path, lnr, line)
    elif tkind == Token.VALUE_BLOCK:
      bname = tokens[0]
      curr_block[bname] = idict.IDict()
    elif tkind == Token.VALUE:
      bname = tokens[0]
      if next_line and ACF_BLOCK_OPEN.match(next_line):
        curr_block[bname] = idict.IDict()
        curr_path.append(bname)
        lnr += 1 # skip the next "{"
      else:
        logger.error("%s:%d: expected { after %r", from_path, lnr, line)
        curr_block[bname] = "" # treat it like a key with value ""
    elif tkind == Token.PAIR:
      curr_block[tokens[0]] = tokens[1]
    elif tkind == Token.BLOCK_CLOSE:
      if curr_path:
        curr_path.pop()
    elif tkind == Token.BLOCK_OPEN:
      logger.error("%s%d: unexpected block open token")
    else:
      # unreachable
      assert False, f"parser failure on {from_path}:{lnr}: {tokens} {tkind}"
    lnr += 1
  return blocks

def parse_acf_file(path, **kwargs):
  "Parse the acf file given by path"
  logger.trace("Parsing acf file %r", path)
  with open(path, "rt") as fobj:
    return parse_acf_text(fobj.read(), filepath=path, **kwargs)

# vim: set ts=2 sts=2 sw=2:
