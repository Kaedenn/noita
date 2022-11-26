#!/usr/bin/env python3

"""
Noita Inquiry Tool

This script aims to distill information about your Noita installation
and your sessions played.
"""

# FIXME:
# noitalib.world may say I have Pyramid orb when I have platform orb

import argparse
import datetime
import glob
import itertools
import logging
import os

import utility.collectionfuncs as cfuncs
import utility.detailenum
from utility.detailenum import Detail, DETAIL
import utility.loghelper
from utility.loghelper import LEVEL_CODES
utility.loghelper.tracelog.hotpatch(logging)

# pylint: disable=wrong-import-position
import noitalib
import steam.paths
from noitalib.translations import plural as Pl

logging.basicConfig(
    format="%(name)s:%(lineno)s: %(levelname)s: %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)

# Permitted values for --dump-i18n
LM_DUMP_BRIEF = "brief"
LM_DUMP_VALUE = "value"
LM_DUMP_VALUES = "values"
LM_DUMP_FULL = "full"
LM_DUMPS = (LM_DUMP_BRIEF, LM_DUMP_VALUE, LM_DUMP_VALUES, LM_DUMP_FULL)

UNSET = "" # Used to differentiate "unset" and "set but with no value"

def localize_material(material, langmap, with_orig=False):
  "Helper function to localize a material"
  if not langmap.is_material(material): # failed to localize
    return material
  mat_str = langmap.material(material)
  if not with_orig or mat_str == material:
    return mat_str.title()
  return "{} ({})".format(mat_str.title(), material)

def get_saves(saves_path, for_save=None):
  "Get a list of all saves if for_save is None, and a single save otherwise"
  for_saves = [for_save] if for_save is not None else None
  save_dirs = noitalib.paths.get_save_paths(saves_path, for_saves)
  if for_save is not None:
    if not save_dirs:
      logger.error("No such save %r in %s", for_save, saves_path)
      return None
    return save_dirs[0]
  save_dirs.sort(key=os.path.basename)
  return save_dirs

def get_sessions(save_path):
  "Get all of the play sessions within a given save directory"
  stats_path = os.path.join(save_path, "stats", "sessions")
  for stats_file in glob.glob(os.path.join(stats_path, "*_stats.xml")):
    logger.trace("Found session %r", stats_file)
    yield noitalib.parse_session(stats_file)

def get_kills_file(stats_file):
  "Get the kills.xml file from the given stats.xml file"
  return stats_file.replace("stats.xml", "kills.xml")

def filter_sessions(sessions, filter_term):
  "Return a list of sessions matching the filter term"
  sessions = sorted(sessions, key=lambda sess: sess["date"])
  if sessions:
    if filter_term == "last":
      yield sessions[-1]
    elif filter_term == "today":
      filter_term = datetime.date.today().strftime(noitalib.SESS_DATE_FORMAT)
      yield from filter_sessions(sessions, filter_term)
    else:
      for session in sessions:
        sfile = session["_files"]["stats_file"]
        if not filter_term:
          yield session
        elif os.path.basename(sfile).startswith(filter_term):
          yield session
        elif session["seed"] == filter_term:
          yield session

def world_get_orbs(save_dir, wstate, langmap):
  "Aggregate everything relating to orbs"
  orbs_have = {oid: noitalib.orbs.get_orb(oid) for oid in wstate.orbs()}
  orbs_need = [oid for oid in noitalib.orbs.ORBS if oid not in orbs_have]
  orb_map_str = wstate.lua_globals().get("ORB_MAP_STRING")
  orb_map = []
  if orb_map_str:
    for orbxy in orb_map_str.split():
      xstr, ystr = orbxy.split(",")
      orb_map.append((int(xstr), int(ystr)))
  else:
    logger.warning("World %s lacks orb map", wstate.path)

  return {
    "orbs_have": orbs_have,
    "orbs_need": orbs_need,
    "orb_map": orb_map
  }

# ----------------------------------------------------------------------
# Public print functions

def print_language_map(langmap, mode, lang_override):
  "Dump the language map"
  if mode is None:
    if lang_override is None:
      mode = LM_DUMP_BRIEF
    else:
      mode = LM_DUMP_VALUE
  elif mode not in LM_DUMPS:
    logger.error("Invalid langmap dump mode %r", mode)
    logger.info("Choices are: %s", LM_DUMPS)
  for token in sorted(langmap):
    if mode == LM_DUMP_BRIEF:
      print(token)
    elif mode == LM_DUMP_VALUE:
      value = langmap.get(token, language=lang_override)
      print(f"{token} {value!r}")
    elif mode == LM_DUMP_VALUES:
      values = langmap.get_token(token).translations
      print(f"{token} {values!r}")
    elif mode == LM_DUMP_FULL:
      ttoken = langmap.get_token(token)
      values = ttoken.translations
      notes = ttoken.notes
      print(f"{token} values={values!r} notes={notes!r}")

def print_session(save_dir, # TODO: configure detail level
    session,
    l10n,
    show_stats=False,
    show_items=False,
    show_biomes=False,
    show_kills=False,
    detail=Detail.BASIC):
  "Print a session"
  stime = session["date"].ctime()
  sseed = session["seed"]
  print(f"{os.path.basename(save_dir)} - {stime} - {sseed}")
  logger.trace("Stats: %r", session["stats"])
  logger.trace("Items: %r", session["items"])
  logger.trace("Biomes visited: %r", session["visits"])
  logger.trace("Kills: %r", session["kills"])
  if show_stats:
    for stat_name, stat_value in session["stats"].items():
      print(f"\t{stat_name} = {stat_value!r}")
  if show_items: # TODO
    pass
  if show_biomes:
    for bcode in session["visits"]:
      bname = l10n(bcode) if l10n else bcode
      print(f"\tVisited {bname}")
  if show_kills: # TODO
    pass

def print_player(save, player, langmap, detail): # TODO: detail levels
  "Print information about a single player"
  labels = []
  labels.append("HP: {}/{}".format(player.health, player.max_health))
  print("{}: {}".format(save, "; ".join(labels)))
  # Display blood attributes
  blood = localize_material(player.blood_material, langmap)
  blood_spray = localize_material(player.blood_spray_material, langmap)
  print("\tPlayer bleeds {} (sprays {})".format(blood, blood_spray))
  # Display absolute damage from damaging materials
  print("Material damage values:")
  for mat, amt in player.material_damages.items():
    mat_str = localize_material(mat, langmap)
    print("\tDamage from {}: {}".format(mat_str, amt))
  # Display damage multipliers
  print("Damage type multipliers:")
  for kind, amt in player.damage_multipliers.items():
    print("\tDamage mult from {}: {}".format(kind, amt))
  # Display status effects
  print("Ingested materials:")
  for mat_kind, mat_count in player.ingestions().items():
    mat_str = localize_material(mat_kind, langmap)
    print("\tIngested {} of {}".format(mat_count, mat_str))
  print("Status effects:")
  for status, values in player.status_effects().items():
    if status != "air":
      label = status
      val_str = " ".join("{}={}".format(key, val) for key, val in values)
      if langmap.is_material(status):
        label = "from eating " + localize_material(status, langmap)
      print("\tEffect {}: {}".format(label, val_str))
  for wand in player.wands: # TODO
    pass
  print("Inventory:")
  for item in player.items: # TODO
    iname = langmap(item[1]) + " (" + item[1] + ")"
    idesc = item[2]
    if idesc.startswith("$"):
      idesc = langmap(idesc) + " (" + idesc + ")"
    iinfo = item[3] if len(item) > 3 else {}
    labels = []
    if iinfo:
      labels.append(repr(iinfo))
    label = " ".join(labels)
    print("\t{} {!r} {}".format(iname, idesc, label).rstrip())
    # TODO: format potion/sack contents
  for spell in player.spells: # TODO
    pass

def print_world(save_dir, wstate, langmap, detail=Detail.BASIC):
  "Print a WorldState"
  save_name = os.path.basename(save_dir)
  num_orbs = Pl(len(wstate.orbs()), "orb")
  session = wstate.get_session_stats(save_dir)
  print(f"{save_name} - {num_orbs} - Seed {session['seed']}")

  if detail >= Detail.BASIC:
    orb_info = world_get_orbs(save_dir, wstate, langmap)
    orbs_have = orb_info["orbs_have"]
    orbs_need = orb_info["orbs_need"]
    orb_map = orb_info["orb_map"]     # dict {orb_id: (orb_x, orb_y)}
    logger.debug("orbs_have = %r", orbs_have)
    for orb_id, orb in sorted(orbs_have.items()):
      label = orb.localize(langmap)
      print(f"\tCollected orb {orb_id}: {label}")
    for oid in sorted(orbs_need):
      label = noitalib.orbs.ORBS[oid].localize(langmap)
      if 0 <= oid < len(orb_map):
        label += " at ({}, {})".format(*orb_map[oid])
      print(f"\tNeed {label}")

  if detail >= Detail.NORMAL:
    shifts = list(wstate.shifts())
    print(f"Shifted materials: {len(shifts)}")
    for mat1, mat2 in shifts:
      mat1str = localize_material(mat1, langmap)
      mat2str = localize_material(mat2, langmap)
      print(f"\t{mat1str} to {mat2str}")

  if detail >= Detail.MORE:
    logger.debug("Lua global variables:")
    for vkey, vval in wstate.lua_globals().items():
      logger.debug("\t%s = %r", vkey, vval)

    flags = wstate.flags()
    logger.debug("Flags: %d", len(flags))
    for flag in flags:
      logger.debug("\t%s", flag)

  if detail >= Detail.BASIC:
    perks = wstate.perks()
    print(f"Perks: {len(perks)}")
    for perk_id, count in perks:
      print(f"\t{langmap.perk(perk_id, count)}")

  if detail >= Detail.MORE:
    print("Perk reroll state:")
    reroll_info = wstate.reroll_info()
    for key, val in reroll_info.items():
      print(f"\t{key} = {val}")

# ----------------------------------------------------------------------
# Functions for logging management

def get_loggers():
  "Get all of the loggers we care about"
  yield logger
  for _, wrapper, _ in utility.loghelper.get_loggers():
    yield wrapper
  yield steam.paths.logger
  yield steam.paths.acf.logger

def configure_logging(ap, args):
  "Configure logging based on the parsed command-line arguments"
  log_level = None
  if args.trace:
    log_level = logging.TRACE # pylint: disable=no-member
  elif args.verbose:
    log_level = logging.DEBUG
  elif args.warnings:
    log_level = logging.WARNING
  elif args.errors:
    log_level = logging.ERROR
  elif args.quiet:
    log_level = logging.FATAL
  if log_level is not None:
    for inst in get_loggers():
      inst.setLevel(log_level)

  # Apply one-off logger configuration
  if args.level:
    for level_pair in args.level:
      sep_chr = ":"
      if "=" in level_pair and level_pair.split("=", 1)[1] in LEVEL_CODES:
        sep_chr = "="
      try:
        logger_name, level_code = level_pair.rsplit(sep_chr, 1)
      except ValueError:
        ap.error(f"invalid level pair {level_pair}; " \
            "must be <name>:<level> or <name>=<level>")
      if level_code not in LEVEL_CODES:
        ap.error(f"invalid level {level_code}; choices are {LEVEL_CODES}")
      utility.loghelper.apply_level(logger_name, level_code)

  if args.list_loggers:
    for inst in get_loggers():
      wrapper = None
      if isinstance(inst, utility.loghelper.DelayLogger):
        if inst.initialized:
          print("{}: delay; initialized".format(inst.name))
        else:
          print("{}: delay; not initialized".format(inst.name))
      else:
        level = logging.getLevelName(inst.getEffectiveLevel())
        print("{}: core logger: {}".format(inst.name, level))

# ----------------------------------------------------------------------
# Private functions implementing top-level arguments

def _main_show_world(save_dirs, langmap, detail):
  "Print information about the world"
  for save_dir in save_dirs:
    wfile = noitalib.world.get_world_file(save_dir)
    if os.path.exists(wfile):
      wstate = noitalib.world.WorldState(wfile)
      print_world(save_dir, wstate, langmap, detail)

def _main_show_players(save_dirs, langmap, detail):
  "Print information about the player(s)"
  players = {}
  for save_dir in save_dirs:
    save_name = os.path.basename(save_dir)
    if noitalib.player.has_player_file(save_dir):
      pfile = noitalib.player.get_player_file(save_dir)
      player = noitalib.player.Player(pfile)
      players[save_name] = player
      logger.debug("In %s: %r", save_dir, player)
  logger.debug("Found %s", Pl(len(players), "player file"))
  for save, player in players.items():
    print_player(save, player, langmap, detail)

def main():
  "Entry point"
  ap = argparse.ArgumentParser(epilog=f"""
The Noita directory is found via the following logic:
  If --steam-appid is given, then look for the game with that appid.
  Otherwise, look for the game in the directory given by --steam-game.

Use --steam to specify a different Steam installation directory.

Noita's Steam App ID is {noitalib.NOITA_APPID}.

-s,--session accepts the following:
  A date, YYYYMMDD, to select all sessions played that day
  A date and time, YYYYMMDD-HHMISS, to select a specific session
  A numeric world seed to select the session by seed
  The word "today" to select the sessions played today
  The word "last" to select the most recent session

--dump-i18n is equivalent to --dump-i18n=brief.

For --level, valid log levels are "T", "D", "I", "W", "E", and "F" for TRACE,
DEBUG, INFO, WARNING, ERROR, and FATAL respectively.
""", formatter_class=argparse.RawDescriptionHelpFormatter)
  ag = ap.add_argument_group("Steam path overrides")
  ag.add_argument("--steam", metavar="PATH",
      default=steam.paths.get_steam_path(),
      help="path to Steam root (default: %(default)s)")
  ag.add_argument("--steam-game", metavar="NAME", default="Noita",
      help="determine path via the named Steam game (default: %(default)s)")
  ag.add_argument("--steam-appid", metavar="NUM",
      help="determine path via a specific Steam App ID")
  ag = ap.add_argument_group("save selection")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-S", "--save", default="save00",
      help="change which save to use (default: %(default)s)")
  mg.add_argument("-A", "--all-saves", action="store_true",
      help="process all saves, not just the main one")
  ag.add_argument("--list-saves", action="store_true",
      help="display available save directories")
  ag = ap.add_argument_group("modding")
  ag.add_argument("--list-mods", action="store_true",
      help="list both workshop and native mods")
  ag = ap.add_argument_group("sessions")
  ag.add_argument("-s", "--session", metavar="TERM",
      help="display session(s) matching the given term (see below)")
  ag.add_argument("-L", "--list-sessions", action="store_true",
      help="display the sessions that have been played")
  ag.add_argument("--show-stats", action="store_true",
      help="include session stats")
  ag.add_argument("--show-items", action="store_true",
      help="include item listing")
  ag.add_argument("--show-biomes", action="store_true",
      help="include session biomes visited")
  ag.add_argument("--show-kills", action="store_true",
      help="include session kills")
  ag = ap.add_argument_group("current game information")
  ag.add_argument("-W", "--show-world", action="store_true",
      help="display information about the game world itself")
  ag.add_argument("-P", "--show-player", action="store_true",
      help="display information about the player")
  ag = ap.add_argument_group("detail level")
  ag.add_argument("-d", "--detail", choices=DETAIL, default=Detail.NORMAL.name,
      help="configure detail level for above actions (default: %(default)s)")
  ag = ap.add_argument_group("internationalization")
  ag.add_argument("--dump-i18n", nargs="?", default=UNSET, choices=LM_DUMPS,
      help="output the i18n mapping")
  ag.add_argument("--language", metavar="CODE", help="language code override")
  ag.add_argument("--localize", metavar="STR", action="append",
      help="localize the given string")
  ag.add_argument("--no-i18n", action="store_true",
      help="disable internationalization support")
  ag = ap.add_argument_group("diagnostic and logging configuration")
  ag.add_argument("--list-loggers", action="store_true",
      help="list all of the known loggers (for debugging)")
  ag.add_argument("--level", metavar="LOGGER:LEVEL", action="append",
      help="configure the named logger with the given level code (see below)")
  mg = ag.add_mutually_exclusive_group()
  mg.add_argument("-V", "--trace", action="store_true",
      help="enable trace-level logging")
  mg.add_argument("-v", "--verbose", action="store_true",
      help="enable verbose-level logging")
  mg.add_argument("-w", "--warnings", action="store_true",
      help="disable all diagnostics below warning")
  mg.add_argument("-e", "--errors", action="store_true",
      help="disable all diagnostics below error")
  mg.add_argument("-q", "--quiet", action="store_true",
      help="disable all diagnostics below critical")

  ap.add_argument("--help-detail", action="store_true",
      help="show detailed usage for -d,--detail argument")
  args = ap.parse_args()

  # Process actions that lead to an early exit
  if args.help_detail:
    print("The -d,--detail argument accepts the following values:")
    value_map = cfuncs.aggregate_values_dict({
      det: val.value for det, val in DETAIL.items()})
    for dvalue, dnames in value_map.items():
      dnames_str = ", ".join(dnames).ljust(len("NORMAL, N"))
      dhelp = utility.detailenum.detail_help(dnames[0])
      print(f"\t{dnames_str} = {dvalue}: {dhelp}")
    ap.exit()

  detail = DETAIL[args.detail]

  # Check some more-complex mutually-exclusive rules
  if args.no_i18n:
    if args.localize:
      ap.error("--localize cannot be used with --no-i18n")
    if args.dump_i18n != UNSET:
      ap.error("--dump-i18n cannot be used with --no-i18n")

  # Configure all of the loggers to have the desired level, if given
  configure_logging(ap, args)

  # Determine where Noita is installed
  steam_appid = args.steam_appid
  steam_game = args.steam_game
  steam_path = args.steam
  if args.steam_appid:
    appid, game_path = steam.paths.get_game_by_id(steam_appid, steam_path)
  else:
    appid, game_path = steam.paths.get_game_by_dir(steam_game, steam_path)
  if not appid or not game_path:
    ap.error("Failed to locate Noita")
  logger.debug("Noita is installed at %s", game_path)

  # Determine where Notia stores save data
  save_root = noitalib.paths.get_saves_path(steam_path, appid)
  if not os.path.isdir(save_root):
    ap.error(f"Failed to locate Noita saves; {save_root} not a directory")
  logger.debug("Noita saves to %s", save_root)

  # Initialize the internationalization system
  langmap = None
  if not args.no_i18n:
    langmap = noitalib.translations.LanguageMap(game_path, args.language)

  # Handle internationalization arguments
  if args.localize:
    for token in args.localize:
      print(langmap(token))

  if args.dump_i18n != UNSET:
    print_language_map(langmap, args.dump_i18n, args.language)

  # Enumerate the specific save directories
  save_shared = get_saves(save_root, "save_shared")
  save_main = get_saves(save_root, args.save)
  save_dirs = [save_main]
  if args.all_saves:
    save_dirs = get_saves(save_root)

  # Primary behaviors follow

  if args.list_saves:
    for save_dir in save_dirs:
      save_name = os.path.basename(save_dir)
      print(f"{save_name} {save_dir}")

  if args.list_mods:
    mods = itertools.chain(
        noitalib.get_workshop_mods(steam_path, appid),
        noitalib.get_native_mods(game_path))
    for mod_def in mods:
      mod_id = mod_def["id"]
      mod_num = mod_def["workshop_id"]
      mod_name = mod_def["name"]
      mod_desc = mod_def["description"]
      print(f"{mod_num}: {mod_id}: {mod_name} - {mod_desc}")

  if args.list_sessions:
    session_sort_key = lambda sess: sess["date"]
    for save_dir in save_dirs:
      sessions = filter_sessions(get_sessions(save_dir), args.session)
      for session in sorted(sessions, key=session_sort_key):
        print_session(save_dir, session, langmap,
            show_stats=args.show_stats,
            show_items=args.show_items,
            show_biomes=args.show_biomes,
            show_kills=args.show_kills,
            detail=detail)

  if args.show_world:
    _main_show_world(save_dirs, langmap, detail=detail)

  if args.show_player:
    _main_show_players(save_dirs, langmap, detail=detail)

if __name__ == "__main__":
  main()

# vim: set ts=2 sts=2 sw=2:
