#!/usr/bin/env python3

"""
Noita random number generation utility

Noita uses a modified linear congruential generator (LCG), specifically
the Lehmer/Park-Miller RNG with the following standard values:
  a = 16807         primitive root modulo M_31 = 7^5
  m = 2147483647    prime M_31 = 2^31 - 1
so that
  q = 127773        m div a = 2147483647 div 16807
  r = 2836          m mod a = 2147483647 mod 16807

Thus the next value is calculated via
  rDiv = value / q
  rMod = value % q
  v = a * rMod - r * rDiv
  if v < 0: v += m
  return v

https://craftofcoding.wordpress.com/2021/07/05/demystifying-random-numbers-schrages-method/
"""

import argparse
import decimal
import logging
import os
import sys

logging.basicConfig(format="%(module)s:%(lineno)s: %(levelname)s: %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

RAND_SCALE = 2**31
# v = a * (v mod q) - r * (v div q)
RAND_COEFF = 16807                  # a = 7^5
RAND_MAX = RAND_SCALE - 1           # m = 2**31-1
RAND_DIV = RAND_MAX // RAND_COEFF   # q = 127773
RAND_MOD = RAND_MAX % RAND_COEFF    # r = 2836

# Extracted from cheatgui alchemy.lua
SEED_SCALE  = decimal.Decimal("0.17127000")
SEED_OFFSET = decimal.Decimal("1323.59030000")

class NoitaRNG:
  "Implement Noita's RNG"
  def __init__(self, seed):
    self._seed = seed
    self._value = seed

  @property
  def seed(self):
    "Obtain the initial seed"
    return self._seed

  @property
  def value(self):
    "Obtain the current value"
    return self._value

  def next(self):
    "Advance the value by one iteration and return the new value"
    x_div = self._value // RAND_DIV
    x_mod = self._value % RAND_DIV
    next_value = x_div * RAND_MOD + x_mod * RAND_COEFF
    if next_value <= 0:
      next_value += RAND_MAX
    logger.debug("Advance %d -> %d (%f)",
        self._value, next_value, next_value / RAND_SCALE)
    self._value = next_value
    return self._value

  def select(self, num_items):
    "Choose a random number between 0 and num_items-1 inclusive"
    value = self.next() / RAND_SCALE
    index = int(num_items * value)
    logger.debug("Chose index %d of %d", index, num_items)
    return index

  def choose(self, chooser, unique=False, iter_limit=1000):
    "Choose a random entry from the chooser mapping"
    curr = 0
    while curr < iter_limit: # this is how Noita does it
      curr += 1
      index = self.select(len(chooser))
      choice, seen = chooser[index]
      if not unique or not seen:
        chooser[index][1] = True
        return choice
    return None

def make_chooser(sequence):
  "Create a mapping sufficient for choose()"
  return {idx: [key, False] for idx, key in enumerate(sequence)}

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("seed", type=int, help="world seed")
  ag = ap.add_argument_group("iteration control")
  ag.add_argument("-S", "--skip", type=int, metavar="NUM", default=0,
      help="advance %(metavar)s iterations prior to generation")
  ag.add_argument("-N", "--num", type=int, metavar="NUM", default=20,
      help="display %(metavar)s iterations (default: %(default)s)")
  ag = ap.add_argument_group("random functions")
  ag.add_argument("--choose", metavar="PATH", type=argparse.FileType("rt"),
      help="pick random thing(s) from %(metavar)s")
  ag.add_argument("-u", "--unique", action="store_true",
      help="disallow duplicate choices")
  ap.add_argument("-v", "--verbose", action="store_true", help="verbose output")
  args = ap.parse_args()
  if args.verbose:
    logger.setLevel(logging.DEBUG)

  # Rescale the seed the way Noita does it
  seed = int(args.seed * SEED_SCALE + SEED_OFFSET)
  rng = NoitaRNG(seed)

  for _ in range(args.skip):
    rng.next()

  if args.choose is not None:
    entries = [line for line in args.choose.read().splitlines() if line]
    logger.debug("Picking from %d items", len(entries))
    chooser = make_chooser(entries)
    for idx in range(args.num):
      value = rng.choose(chooser, unique=args.unique)
      print(f"{idx} {value}")
  else:
    for idx in range(args.num):
      value = rng.next()
      print(f"{idx} {value}")

if __name__ == "__main__":
  main()

# vim: set ts=2 sts=2 sw=2:
