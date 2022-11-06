#!/usr/bin/env python3

"""
Get human-readable values for i18n tokens

This module relies heavily on the data/translations/common.csv layout and will
likely break if that file is changed too much. For reference, the code below
makes the following assumptions:
  rows[0] is the header
  rows[0] has the structure:
    [<empty>, ...languages..., <empty>, ...notes...]
  If a token lacks a translation for the selected language, use the "en" one.
"""

import csv
import locale
import os

import utility.loghelper
logger = utility.loghelper.DelayLogger(__name__)

TRANSLATIONS = "data/translations/common.csv"
LANG_FALLBACK = "en"

def plural(num, word):
  "Return '<num> <word>' with <word> plural, if needed"
  if word:
    if num != 1:
      if word[-1] == "y":
        word = word + "ies"
      elif word[-1] in "aiou":
        word = word + "es"
      elif word[-1] == "e":
        word = word + "s"
      else:
        word = word + "s"
    return f"{num} {word}"
  return f"{num}"

def get_preferred_language():
  "Return the preferred two-letter language code"
  lang, _ = locale.getlocale()
  if not lang:
    logger.warning("No locale defined! Defaulting to English")
    return LANG_FALLBACK
  return lang.split("_")[0]

def load_translations_csv(fpath):
  """
  Load the common.csv translations file

  See the module docstring for the assumptions this function makes.
  """
  with open(fpath, "rt") as fobj:
    rows = list(csv.reader(fobj))
  headers = rows[0]
  notes_col = headers.index("", 1) # see module docstring for explanation
  lang_codes = headers[1:notes_col]
  token_map = {}
  for rownum in range(1, len(rows)):
    row = rows[rownum]
    token = row[0]
    values = row[1:notes_col]
    notes = row[notes_col:]
    langmap = dict(zip(lang_codes, values))
    if not token:
      logger.trace("Skipping row %d %r; no token defined", rownum, row)
    elif token in token_map:
      curr = token_map[token]
      logger.debug("Skipping duplicate token %r", token)
      logger.trace("Have: (%r, %r)", langmap, notes)
      logger.trace("Skip: (%r, %r)", curr.translations, curr.notes)
    else:
      token_map[token] = Token(token, langmap, notes)
  return lang_codes, token_map

class Token:
  "A single localized token"
  def __init__(self, token, langmap, notes=None):
    "See help(type(self))"
    self._token = token
    self._map = langmap
    self._languages = tuple(langmap.keys())
    self._notes = notes

  @property
  def token(self):
    "Get the token this map translates"
    return self._token

  @property
  def translations(self):
    "Get the {lang_code: str} mapping"
    return self._map

  @property
  def notes(self):
    "Get the notes list, or None"
    return self._notes

  def get(self, lang=None, fallback=LANG_FALLBACK):
    "Get the localized value for the specified language"
    if lang is None:
      lang = get_preferred_language()
    return self._map.get(lang, self._map[fallback])

  def __str__(self):
    "str(self)"
    return f"${self._token}"

  def __repr__(self):
    "repr(self)"
    value = plural(len(self._map), "value")
    if self._notes:
      value += ", " + plural(len(self._notes), "note")
    return f"Token({self._token!r}, {value})"

class LanguageMap:
  "Map tokens to their localized values"
  def __init__(self, game_path, language=None):
    "Construct the map; see help(type(self)) for signature"
    self._game_path = game_path
    self._language = language
    if language is None:
      self._language = get_preferred_language()
    self._languages = []
    self._tokens = {}
    self.reload_map()

  @property
  def translations_file(self):
    "Return the path to the translations CSV file"
    return os.path.join(self._game_path, TRANSLATIONS)

  @property
  def languages(self):
    "Return the known languages"
    return self._languages

  def has_token(self, token):
    "True if the token is localized, False otherwise"
    return token in self._tokens

  def get_token(self, token):
    "Get the Token instance for the given string"
    if token in self._tokens:
      return self._tokens[token]
    raise ValueError(f"Token {token!r} not localized")

  def reload_map(self):
    "Load the translations CSV"
    langs, tokens = load_translations_csv(self.translations_file)
    self._languages = langs
    self._tokens = tokens

  def get(self, token, language=None, insertions=()):
    "Localize a single token with optional insertions"
    if token.startswith("$"):
      token = token[1:]
    if token in self._tokens:
      phrase = self._tokens[token].get(lang=language)
      if insertions:
        for inum, ivalue in enumerate(insertions):
          phrase = phrase.replace(f"${inum}", ivalue)
      return phrase
    logger.debug("Unknown token %r", token)
    return token

  def localize(self, phrase, *insertions):
    """
    Localize a word or phrase with optional insertions

    Localization is done word-by-word. Words without a leading "$" are
    skipped.
    """
    result = []
    for word in phrase.split():
      if word.startswith("$"):
        result.append(self.get(word, insertions=insertions))
      else:
        result.append(word)
    return " ".join(result)

  def __iter__(self):
    "Obtain the translation tokens"
    yield from self._tokens.keys()

  def __getitem__(self, token):
    "Get translations for a given token"
    return self._tokens[token].translations

  def __call__(self, phrase, *insertions):
    "Alias for self.localize"
    return self.localize(phrase, *insertions)

  # Noita-specific shorthand functions

  def material(self, matid, with_as=False):
    "Get the localized name of a material"
    matstr = self.localize("$mat_" + matid)
    if with_as and matstr != matid:
      matstr += f" (as {matid})"
    return matstr

  def perk(self, perkid, count=1):
    "Get the localized name of a perk"
    perkstr = self.localize("$perk_" + perkid)
    if count > 0:
      perkstr += f" x{count}"
    return perkstr

# vim: set ts=2 sts=2 sw=2:
