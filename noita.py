#!/usr/bin/env python3

"""
Noita Inquiry Tool

This script aims to distill information about your Noita installation
and your sessions played.
"""

import argparse
import datetime
import glob
import itertools
import logging
import os

import utility.loghelper
from utility.loghelper import LEVEL_CODES
utility.loghelper.tracelog.hotpatch(logging)

# pylint: disable=wrong-import-position
import noitalib
import steam.paths

logging.basicConfig(
    format="%(module)s:%(lineno)s: %(levelname)s: %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__name__)

UNSET = "" # Used to differentiate "unset" and "set but with no value"

def get_saves(saves_path, for_save=None):
  """
  Get a specific save directory if for_save is not None, or a list of
  all save directories otherwise
  """
  if for_save is not None:
    save_dir = os.path.join(saves_path, for_save)
    if os.path.isdir(save_dir):
      return save_dir
    logger.error("No such save %r in %s", for_save, saves_path)
    return None

  save_dirs = []
  for save_dir in os.listdir(saves_path):
    if len(save_dir) == len("save00"):
      if save_dir[:4] == "save" and save_dir[5:].isdigit():
        save_dirs.append(os.path.join(saves_path, save_dir))
  save_dirs.sort(key=os.path.basename)
  return save_dirs

def get_sessions(save_path):
  "Get all of the play sessions within a given save directory"
  stats_path = os.path.join(save_path, "stats", "sessions")
  for stats_file in glob.glob(os.path.join(stats_path, "*_stats.xml")):
    kills_file = stats_file.replace("stats.xml", "kills.xml")
    logger.trace("Found session %r", stats_file)
    yield noitalib.parse_session(stats_file, kills_file)

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

def print_session(save_dir,
    session,
    l10n,
    show_stats=False,
    show_items=False,
    show_biomes=False,
    show_kills=False):
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
  if show_items:
    pass
  if show_biomes:
    for bcode in session["visits"]:
      bname = l10n(bcode) if l10n else bcode
      print(f"\tVisited {bname}")
  if show_kills:
    pass

def dump_language_map(langmap, mode, lang_override):
  "Dump the language map"
  if mode is None:
    if lang_override is None:
      mode = "brief"
    else:
      mode = "value"
  for token in sorted(langmap):
    if mode == "brief":
      print(token)
    elif mode == "value":
      value = langmap.get(token, language=lang_override)
      print(f"{token} {value!r}")
    elif mode == "values":
      values = langmap.get_token(token).translations
      print(f"{token} {values!r}")
    elif mode == "full":
      ttoken = langmap.get_token(token)
      values = ttoken.translations
      notes = ttoken.notes
      print(f"{token} values={values!r} notes={notes!r}")

def orb_to_string(orb_id, orb, langmap):
  "Build a printable string for the given orb"
  return orb.localize(langmap)
  orb_pwdir, orb_pwnum = noitalib.orbs.get_orb_world(orb_id)
  place = langmap(orb.place).title()
  if orb_pwdir != noitalib.orbs.WORLD_MAIN:
    if orb_pwdir == noitalib.orbs.WORLD_WEST:
      pwtok = "$biome_west"
    else:
      pwtok = "$biome_east"
    if orb_pwnum > 1:
      place = langmap(pwtok, f"x{orb_pwnum} {place}")
    else:
      place = langmap(pwtok, place)
    return place
  return f"{langmap(orb.spell)} from {place}"

def print_world(save_dir, wstate, langmap):
  "Print a WorldState"
  save_name = os.path.basename(save_dir)
  print(f"{save_name} - {len(wstate.orbs())} orbs")
  # Orbs
  orbs_have = {oid: noitalib.orbs.get_orb(oid) for oid in wstate.orbs()}
  for orb_id, orb in sorted(orbs_have.items()):
    label = orb.localize(langmap)
    print(f"\tCollected orb {orb_id}: {label}")
  orbs_need = [oid for oid in noitalib.orbs.ORBS if oid not in orbs_have]
  for oid in sorted(orbs_need):
    label = orb_to_string(oid, noitalib.orbs.ORBS[oid], langmap)
    print(f"\tNeed orb {oid}: {label}")
  # Fungal shifts
  print(f"Fungal shifts: {len(list(wstate.shifts()))}")
  for mat1, mat2 in wstate.shifts():
    mat1str = langmap("$mat_" + mat1)
    mat2str = langmap("$mat_" + mat2)
    if mat1 != mat1str:
      mat1str += f" (as {mat1})"
    if mat2 != mat2str:
      mat2str += f" (as {mat2})"
    print(f"\t{mat1str} to {mat2str}")
  logger.debug("Lua global variables:")
  for vkey, vval in wstate.lua_globals().items():
    logger.debug("\t%s = %r", vkey, vval)
  logger.debug("Flags:\n%s", "\n".join(wstate.flags()))
  perks = wstate.perks()
  print(f"Perks: {len(perks)}")
  for perk_id, count in perks:
    perk_name = langmap("$perk_" + perk_id)
    if count > 1:
      print(f"\t{perk_name} x{count}")
    else:
      print(f"\t{perk_name}")

def get_loggers():
  "Get all of the loggers we care about"
  yield logger
  yield noitalib.logger
  yield steam.paths.logger
  yield steam.paths.acf.logger

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
  ag = ap.add_argument_group("game path specification")
  ag.add_argument("--steam", metavar="PATH",
      default=steam.paths.get_steam_path(),
      help="path to Steam root (default: %(default)s)")
  ag.add_argument("--steam-game", metavar="NAME", default="Noita",
      help="determine path to a named Steam game (default: %(default)s)")
  ag.add_argument("--steam-appid", metavar="NUM",
      help="determine path via a specific App ID")
  ag = ap.add_argument_group("save selection")
  ag.add_argument("--save", help="limit output to a specific save directory")
  ag = ap.add_argument_group("output behavior")
  ag.add_argument("--list-saves", action="store_true",
      help="display available save directories")
  ag.add_argument("--list-mods", action="store_true",
      help="list both workshop and native mods")
  ag.add_argument("-L", "--list-sessions", action="store_true",
      help="display the sessions that have been played")
  ag = ap.add_argument_group("session selection and configuration")
  ag.add_argument("-s", "--session", metavar="TERM",
      help="display session(s) matching the given term (see below)")
  ag.add_argument("--show-stats", action="store_true",
      help="include session stats")
  ag.add_argument("--show-items", action="store_true",
      help="include item listing")
  ag.add_argument("--show-biomes", action="store_true",
      help="include session biomes visited")
  ag.add_argument("--show-kills", action="store_true",
      help="include session kills")
  ag = ap.add_argument_group("game data")
  ag.add_argument("-W", "--show-world", action="store_true",
      help="display information about the game world itself")
  ag.add_argument("-P", "--show-player", action="store_true",
      help="display information about the player")
  ag = ap.add_argument_group("internationalization")
  ag.add_argument("--dump-i18n", nargs="?", default=UNSET,
      choices=("brief", "value", "values", "full"),
      help="output the i18n mapping")
  ag.add_argument("--language", metavar="CODE", help="language code override")
  ag.add_argument("--localize", metavar="STR", action="append",
      help="localize the given string")
  ag.add_argument("--no-i18n", action="store_true",
      help="disable internationalization support")
  ag = ap.add_argument_group("diagnostics")
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
  args = ap.parse_args()

  # Check some mutually-exclusive arguments
  if args.no_i18n:
    if args.localize:
      ap.error("--localize cannot be used with --no-i18n")
    if args.dump_i18n != UNSET:
      ap.error("--dump-i18n cannot be used with --no-i18n")

  # Configure all of the loggers to have the desired level, if given
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
      logger_name, level_code = level_pair.rsplit(":", 1)
      if level_code not in LEVEL_CODES:
        ap.error(f"invalid level {level_code}; choices are {LEVEL_CODES}")
      utility.loghelper.apply_level(logger_name, level_code)

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
  save_root = noitalib.paths.get_save_path(steam_path, appid)
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
    dump_language_map(langmap, args.dump_i18n, args.language)

  # Enumerate the specific save directories
  save_shared = get_saves(save_root, "save_shared")
  save_main = None
  if args.save is None:
    save_dirs = get_saves(save_root)
  else:
    save_main = get_saves(save_root, args.save)
    if save_main is None:
      ap.error("Failed to get requested save directory")
    save_dirs = [save_main]

  # Primary behavior follows

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
            show_kills=args.show_kills)

  if args.show_world:
    for save_dir in save_dirs:
      wfile = noitalib.world.get_world_file(save_dir)
      if os.path.exists(wfile):
        wstate = noitalib.world.WorldState(wfile)
        print_world(save_dir, wstate, langmap)

  if args.show_player:
    for save_dir in save_dirs:
      # TODO
      pass

if __name__ == "__main__":
  main()

# vim: set ts=2 sts=2 sw=2:
