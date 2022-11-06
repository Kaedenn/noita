#!/usr/bin/env python3

"""
Functions for deciphering the player.xml file
"""

import datetime
import os

import utility.loghelper
from . import xmltools
logger = utility.loghelper.DelayLogger(__name__)

class Player:
  "The Noita"
  def __init__(self, file_path):
    "See help(type(self))"
    self._path = file_path
    self._root = parse_player(file_path)
    self._interpret()

  def pos(self):
    "Get the player coordinates"
    return (self._xpos, self._ypos)

  def _interpret(self):
    "Extract information from self._root"
    self._interpret_transform(self._root.find("_Transform"))
    # TODO: Audio
    self._interpret_char_data(self._root.find("CharacterDataComponent"))
    # TODO: GunComponent
    # TODO: HitboxComponent
    # TODO: IngestionComponent
    # TODO: Inventory2Component, InventoryGuiComponent
    # TODO: ItemPickerUpperComponent
    # TODO: KickComponent
    # TODO: LightComponent
    # TODO: LiquidDisplacerComponent
    # TODO: LuaComponents
    # TODO: MaterialInventoryComponent
    # TODO: MaterialSuckerComponent
    # TODO: ParticleEmitterComponent
    # TODO: PathFindingGridMarkerComponent
    # TODO: PhysicsPickUpComponent
    # TODO: PlatformShooterPlayerComponent
    # TODO: PlayerCollisionComponent
    # TODO: SpriteAnimatorComponent and SpriteComponents
    # TODO: SpriteParticleEmitterComponent
    # TODO: SpriteStainsComponent
    # TODO: StatusEffectDataComponent
    # TODO: StreamingKeepAliveComponent
    # TODO: VariableStorageComponents
    # TODO: VelocityComponent
    # TODO: WalletComponent
    # TODO: Entity nodes: arm_r cape perk_entity fungal_shift_ui_icon
    # TODO: Entity name="inventory_quick"
    # TODO: Entity name="inventory_full"

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
    self._damages = elem.attrib # TODO

  def _interpret_drug_effects(self, elem):
    "Intrepret the <DrugEffectComponent> node"
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
