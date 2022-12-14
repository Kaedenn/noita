#!/usr/bin/env python3

"""
Functions for deciphering the player.xml file
"""

# TODO: Separate quick inventory and full inventory
# TODO: Interpret egg contents
# TODO: Handle powder sacks

import datetime
import os

import utility.loghelper
from .xmltools import parse_strings_node as xml_parse_strings
from . import xmltools
from . import items

logger = utility.loghelper.DelayLogger(__name__)

AIR_INITIAL = 7
AIR_DAMAGE_INITIAL = 0.6
HEART_SIZE = 25

def make_attr_getter(attr):
  "Build a simple wrapper function"
  def wrapper(self):
    "Simple wrapper function"
    return getattr(self, "_" + attr)
  wrapper.__name__ = attr
  return wrapper

class Player:
  "The Noita"
  def __init__(self, file_path):
    "See help(type(self))"
    self._path = file_path
    self._root = parse_player(file_path)
    self._xpos = None
    self._ypos = None
    self._rot = None
    self._xscale = None
    self._yscale = None
    self._money = 0
    self._money_spent = 0
    self._money_inf = False

    self._health = 0
    self._max_health = 0
    self._blood_material = "blood_fading"
    self._blood_spray_material = "blood"
    self._blood_multiplier = 1
    self._air = AIR_INITIAL
    self._air_max = AIR_INITIAL
    self._drowning_damage = AIR_DAMAGE_INITIAL
    self._material_damages = {}
    self._damage_multipliers = {}
    self._ingestions = {}
    self._status_effects = {}

    self._wands = []
    self._items = []
    self._spells = []

    # TODO: inventory

    # Raw data
    self._char_data = None
    self._physics = None
    self._damages = None
    self._drug_effects = None
    self._logging = None
    self._stats = None
    self._genome_info = None
    self._interpret()

  def pos(self):
    "Get the player coordinates"
    return (self._xpos, self._ypos)

  health = property(make_attr_getter("health"))
  max_health = property(make_attr_getter("max_health"))
  blood_material = property(make_attr_getter("blood_material"))
  blood_spray_material = property(make_attr_getter("blood_spray_material"))
  blood_multiplier = property(make_attr_getter("blood_multiplier"))
  air = property(make_attr_getter("air"))
  air_max = property(make_attr_getter("air_max"))
  drowning_damage = property(make_attr_getter("drowning_damage"))
  material_damages = property(make_attr_getter("material_damages"))
  damage_multipliers = property(make_attr_getter("damage_multipliers"))
  status_effects = make_attr_getter("status_effects")
  ingestions = make_attr_getter("ingestions")
  wands = property(make_attr_getter("wands"))
  items = property(make_attr_getter("items"))
  spells = property(make_attr_getter("spells"))

  damages = property(make_attr_getter("damages"))
  drug_effects = property(make_attr_getter("drug_effects"))

  def _interpret(self):
    "Extract information from self._root"
    self._interpret_transform(self._root.find("_Transform"))
    # TODO: Audio
    self._interpret_char_data(self._root.find("CharacterDataComponent"))
    # TODO: CharacterPlatformingComponent
    self._interpret_damages(self._root.find("DamageModelComponent"))
    self._interpret_drug_effects(self._root.find("DrugEffectComponent"))
    # TODO: GameLogComponent and GameStatesComponent
    # TODO: GunComponent
    # TODO: HitboxComponent
    # TODO: IngestionComponent
    # TODO: Inventory2Component, InventoryGuiComponent
    # TODO: ItemPickerUpperComponent
    # TODO: KickComponent
    # TODO: LightComponent
    # TODO: LiquidDisplacerComponent
    # TODO: LuaComponents
    for elem in self._root.findall("MaterialInventoryComponent"):
      tags = elem.attrib.get("_tags", "").split(",")
      if "ingestion" in tags:
        self._interpret_ingestions(elem, override=False)
    # TODO: MaterialSuckerComponent
    # TODO: ParticleEmitterComponent
    # TODO: PathFindingGridMarkerComponent
    # TODO: PhysicsPickUpComponent
    # TODO: PlatformShooterPlayerComponent
    # TODO: PlayerCollisionComponent
    # TODO: SpriteAnimatorComponent and SpriteComponents
    # TODO: SpriteParticleEmitterComponent
    # TODO: SpriteStainsComponent
    self._interpret_status_effects(self._root.find("StatusEffectDataComponent"))
    # TODO: StreamingKeepAliveComponent
    # TODO: VariableStorageComponents
    # TODO: VelocityComponent
    self._interpret_wallet(self._root.find("WalletComponent"))
    for elem in self._root.findall("Entity"):
      name = elem.attrib.get("name")
      tags = elem.attrib.get("tags")
      if name == "arm_r":
        logger.debug("Parsing arm_r %r", elem)
      elif name == "cape":
        logger.debug("Parsing cape %r", elem)
        # TODO: cape stains
      elif name == "perk_entity" or "perk_entity" in tags:
        logger.debug("Parsing perk entity %r", elem)
        # TODO
      elif name == "fungal_shift_ui_icon":
        logger.debug("Parsing fungal shift icon %r", elem)
        # TODO
      elif name == "inventory_quick":
        logger.debug("Parsing quick inventory %r", elem)
        self._interpret_inventory(elem, quick=True)
      elif name == "inventory_full":
        logger.debug("Parsing full inventory %r", elem)
        self._interpret_inventory(elem, quick=False)
      else:
        if name is None or name == "":
          name = "<unnamed>"
        # TODO: try to parse the unnamed entity anyway
        logger.trace("Skipping %s entity %r %r", name, elem, elem.attrib)
        logger.trace("Value: %s", xmltools.tostring(elem))
    # TODO: Entity name="inventory_quick" for wands/flasks
    # TODO: Entity name="inventory_full" for spells

  def _interpret_transform(self, elem):
    "Interpret the <_Transform> node"
    self._xpos = elem.attrib["position.x"]
    self._ypos = elem.attrib["position.y"]
    self._rot = elem.attrib["rotation"]
    self._xscale = elem.attrib["scale.x"]
    self._yscale = elem.attrib["scale.y"]

  def _interpret_char_data(self, elem):
    "Interpret the <CharacterDataComponent> node"
    self._char_data = elem.attrib # TODO

  def _interpret_platforming(self, elem):
    "Interpret the <CharacterPlatformingComponent> node"
    self._physics = elem.attrib # TODO

  def _interpret_damages(self, elem):
    "Interpret the <DamageModelComponent> node"
    hearts = float(elem.attrib["hp"])
    max_hearts = float(elem.attrib["max_hp"])
    self._health = round(hearts * HEART_SIZE, 2)
    self._max_health = round(max_hearts * HEART_SIZE, 2)
    if self._health == int(self._health):
      self._health = int(self._health)
    if self._max_health == int(self._max_health):
      self._max_health = int(self._max_health)
    self._blood_material = elem.attrib["blood_material"]
    self._blood_spray_material = elem.attrib["blood_spray_material"]
    self._blood_multiplier = elem.attrib["blood_multiplier"]
    self._air = float(elem.attrib["air_in_lungs"])
    self._air_max = float(elem.attrib["air_in_lungs_max"])
    self._drowning_damage = float(elem.attrib["air_lack_of_damage"])
    mat_mults = elem.attrib["materials_how_much_damage"].split(",")
    mat_names = elem.attrib["materials_that_damage"].split(",")
    for mult, mat in zip(mat_mults, mat_names):
      self._material_damages[mat] = float(mult)
    mult_elem = elem.find("damage_multipliers")
    for dmg_kind, dmg_mult in mult_elem.attrib.items():
      self._damage_multipliers[dmg_kind] = float(dmg_mult)
    self._damages = elem.attrib

  def _interpret_ingestions(self, elem, override=True):
    "Interpret the <MaterialInventoryComponent _tags='ingestion'> node"
    entries = elem.find("count_per_material_type")
    materials = []
    if entries is not None:
      materials = [node.attrib for node in entries.findall("Material")]
    if override:
      self._ingestions = {}
    for material in materials:
      mcount = material["count"]
      mkind = material["material"]
      self._ingestions[mkind] = mcount

  def _interpret_status_effects(self, elem):
    "Interpret the <StatusEffectDataComponent> node"
    labels = ("stain", "previous", "ingestion", "causes_many")
    causes = elem.attrib["ingestion_effect_causes"].split(",")
    stains = xml_parse_strings(elem.find("stain_effects"))
    effects_prev = xml_parse_strings(elem.find("effects_previous"))
    ingestion = xml_parse_strings(elem.find("ingestion_effects"))
    causes_many = xml_parse_strings(elem.find("ingestion_effect_causes_many"))
    status_values = zip(stains, effects_prev, ingestion, causes_many)
    for cause, values in zip(causes, status_values):
      if cause != "air" or any(val != "0" for val in values):
        self._status_effects[cause] = zip(labels, values)

  def _interpret_inventory(self, elem, quick):
    "Interpret an inventory node"
    entries = []
    for celem in elem.findall("Entity"):
      kind = items.classify_item(celem)
      entries.append((kind, celem))
    logger.debug("Inventory contents: %d entries", len(entries))
    for kind, celem in entries:
      icomp = celem.find("ItemComponent")
      iattrs = {}
      if icomp is not None:
        iattrs = icomp.attrib
      iname = iattrs.get("item_name")
      idesc = iattrs.get("ui_description")
      if kind == items.Kind.CARD: # TODO: interpret
        self._items.append((items.Kind.CARD, iname, idesc))
      elif kind == items.Kind.WAND: # TODO: interpret
        self._items.append((items.Kind.WAND, iname, idesc))
      elif kind == items.Kind.POTION or kind == items.Kind.SACK:
        melem = celem.find("MaterialInventoryComponent")
        contents = {}
        for mat in melem.find("count_per_material_type").findall("Material"):
          contents[mat.attrib["material"]] = int(mat.attrib["count"])
        self._items.append((kind, iname, idesc, contents))
      elif kind == items.Kind.EGG: # TODO: interpret
        self._items.append((items.Kind.EGG, iname, idesc))
      elif kind == items.Kind.PICKUP: # TODO: elaborate?
        self._items.append((items.Kind.PICKUP, iname, idesc))
      else:
        logger.warning("Unknown item type %s for %s: %s", kind, iname, idesc)

  def _interpret_drug_effects(self, elem):
    "Intrepret the <DrugEffectComponent> node"
    logger.trace("Parsing drug effects %r: %r", elem, elem.attrib)
    self._drug_effects = elem.attrib # TODO

  def _interpret_game_log(self, elem):
    "Interpret the <GameLogComponent> node"
    self._logging = elem.attrib # TODO

  def _interpret_stats(self, elem):
    "Interpret the <GameStatsComponent> node"
    self._stats = elem.attrib # TODO

  def _interpret_genome(self, elem):
    "Interpret the <GenomeDataComponent> node"
    self._genome_info = elem.attrib # TODO

  def _interpret_wallet(self, elem):
    "Interpret the <WalletComponent> node"
    self._money = int(elem.attrib["money"])
    self._money_spent = int(elem.attrib["money_spent"])
    self._money_inf = elem.attrib["mHasReachedInf"] == "1"

def get_player_file(save_path):
  "Return the path to the player file"
  return os.path.join(save_path, "player.xml")

def has_player_file(save_path):
  "True if the save contains a player file"
  return os.path.isfile(get_player_file(save_path))

def parse_player(player_path):
  "Parse the player.xml file"
  logger.trace("Parsing player file %r", player_path)
  return xmltools.parse_xml(player_path, get_root=True)

# vim: set ts=2 sts=2 sw=2:
