#!/usr/bin/env python3

"""
Common XML-related functions to support Noita
"""

import lxml.etree as et

import utility.loghelper
logger = utility.loghelper.DelayLogger(__name__)

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

def remove_space_tails(node, replace_with=""):
  "Remove all node tails that consist of only whitespace"
  for cnode in node.getchildren():
    if cnode.tail and cnode.tail.isspace():
      cnode.tail = replace_with
    remove_space_tails(cnode, replace_with)

def tostring(elem):
  "Convert an element to a string"
  return et.tostring(elem).decode()

# vim: set ts=2 sts=2 sw=2:
