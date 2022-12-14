#!/usr/bin/env python3

"""
Provide methods to calculate a seed's AP and LC recipes.
"""

from noitalib import materials
from utility import prng

def shuffle_sequence(sequence, seed, inplace=False):
  "Shuffle a given sequence the way Noita does it"
  items = sequence
  if not inplace:
    items = list(sequence)

  seed = seed // 2 + 12534
  nrng = prng.NoitaRNG(seed)
  nrng.next()
  index = len(items) - 1
  while index >= 0:
    rand = nrng.next() / prng.RAND_SCALE
    target = int(rand * index)
    items[index], items[target] = items[target], items[index]
    index -= 1
  return items

def aplc_get_set(nrng):
  "Determine the four possible components for the AP/LC recipe"
  liq_set = prng.make_chooser(materials.AP_LC_LIQUIDS)
  org_set = prng.make_chooser(materials.AP_LC_ORGANICS)
  return [
    nrng.choose(liq_set),
    nrng.choose(liq_set),
    nrng.choose(liq_set),
    nrng.choose(org_set)
  ]

def aplc_get_recipe(nrng, aplc_materials):
  "Calculate the final AP/LC recipe"
  rng_scaled = nrng.next() / prng.RAND_SCALE
  probability = 10 + int(rng_scaled * 91)
  nrng.next()

  recipe = shuffle_sequence(aplc_materials, nrng.seed)[:3]
  return recipe, probability

def calculate_ap_lc_recipe(seed):
  "Calculate the recipe triplet for the given seed"
  scaled_seed = seed * prng.SEED_SCALE + prng.SEED_OFFSET
  nrng = prng.NoitaRNG(scaled_seed)
  # Noita skips the first six iterations (or uses them elsewhere)
  for _ in range(6):
    nrng.next()

  lc_mats = aplc_get_set(nrng)
  lc_recipe, lc_prob = aplc_get_recipe(nrng, lc_mats)
  ap_mats = aplc_get_set(nrng)
  ap_recipe, ap_prob = aplc_get_recipe(nrng, ap_mats)

  print(lc_mats)
  print(ap_mats)

  return lc_recipe, lc_prob, ap_recipe, ap_prob

# vim: set ts=2 sts=2 sw=2:
