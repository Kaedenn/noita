#!/usr/bin/env python3

"""
Common XML-related functions to support Noita
"""

import lxml.etree as et

from .logger import logger

def parse_xml(file_path, get_root=True):
  "Helper function to read an XML file"
  with open(file_path, "rt") as fobj:
    root = et.parse(fobj)
  if get_root:
    return root.getroot()
  return root

def xml_get_child(node, cname):
  "Return the named child node. Raises an error if the child can't be found"
  cnode = node.find(cname)
  if cnode is None:
    raise ValueError(f"Failed to find {cname!r} in element {node!r}")
  return cnode

def parse_entries_node(node, as_int=False):
  "Parse a node containing <E>...</E> children"
  entries = {}
  for elem in node.getchildren():
    elkey = elem.attrib.get("key")
    elval = elem.attrib.get("value")
    if elkey is not None and elval is not None:
      if as_int and elval.isdigit():
        elval = int(elval)
      entries[elkey] = elval
  return entries

def parse_strings_node(node):
  "Parse a node containing <string>...</string> children"
  entries = []
  for elem in node.getchildren():
    entries.append(elem.text.strip())
  return entries

# vim: set ts=2 sts=2 sw=2:
