#!/usr/bin/env python3

"""
Functions and constants for encrypting and decrypting Noita data

All salakieli files are encrypted with AES-128-CTR using particular key
and IV (initialization vector) pairs defined below. This module wraps
the encryption and decryption details into convenient functions.
"""

# TODO: encryption

import binascii
import os
import pathlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import utility.loghelper
from . import sessions
from . import xmltools
logger = utility.loghelper.DelayLogger(__name__)

KEY_LEN = 16 # Only the first 16 bytes matter

EXT = "salakieli"

KIV_PLAYER = "player"
KIV_WORLD = "world_state"
KIV_SESSION = "session_numbers"
KIV_STATS = "_stats"
KIV_STREAKS = "_streaks"

KEY_IV_MAP = {
  KIV_PLAYER: (
    "WeSeeATrueSeekerOfKnowledge",
    "YouAreSoCloseToBeingEnlightened"),
  KIV_WORLD: (
    "TheTruthIsThatThereIsNothing",
    "MoreValuableThanKnowledge"),
  KIV_SESSION: (
    "KnowledgeIsTheHighestOfTheHighest",
    "WhoWouldntGiveEverythingForTrueKnowledge"),
  KIV_STATS: (
    "SecretsOfTheAllSeeing",
    "ThreeEyesAreWatchingYou"),
  KIV_STREAKS: (
    "SecretsOfTheAllSeeing",
    "ThreeEyesAreWatchingYou"),
}

def guess_kiv_pair(fname):
  """
  Guess which key and IV pair to use for the given filename.
  """
  fbase, fext = os.path.splitext(fname)
  if fext.lstrip(os.extsep) == EXT:
    if fbase in KEY_IV_MAP:
      return KEY_IV_MAP[fbase]
  logger.warning("Unable to determine key/IV pair for %r", fname)
  return ("", "")

def kiv_to_bin(file_key, file_iv):
  """
  Ensure the key and IV are of the desired format.
  """
  if isinstance(file_key, str):
    file_key = file_key.encode("ascii")
  if isinstance(file_iv, str):
    file_iv = file_iv.encode("ascii")
  return file_key[:KEY_LEN], file_iv[:KEY_LEN]

def decrypt_file(fpath, kiv_name=None):
  """
  Open and decrypt the given file.

  The caller can pass one of the KIV_* constants if known beforehand.
  Otherwise, this function will determine the constants using the
  filename.
  """
  fname = os.path.basename(fpath)
  if kiv_name is None:
    file_key, file_iv = guess_kiv_pair(fname)
  else:
    file_key, file_iv = KEY_IV_MAP[kiv_name]
  hex_key, hex_iv = kiv_to_bin(file_key, file_iv)
  with open(fpath, "rb") as fobj:
    fdata = fobj.read()
  return decrypt_data(fdata, (hex_key, hex_iv))

def decrypt_data(fdata, kiv_pair):
  """
  Decrypt the given binary string.

  The key and IV can be specified via either a KIV_* constant or a pair
  of binary strings.
  """
  if kiv_pair in KEY_IV_MAP:
    data_key, data_iv = kiv_to_bin(*KEY_IV_MAP[kiv_pair])
  else:
    data_key, data_iv = kiv_to_bin(*kiv_pair)

  if not data_key or not data_iv:
    raise ValueError(f"Failed to determine key and/or IV for {fpath!r}")

  cipher = Cipher(algorithms.AES(data_key), modes.CTR(data_iv),
      backend=default_backend())
  decryptor = cipher.decryptor()
  decrypted = decryptor.update(fdata) + decryptor.finalize()
  return decrypted.decode()

# vim: set ts=2 sts=2 sw=2:
