#!/bin/bash

# Functions used by both of the mod copy scripts

# Environment variables:
#   NOITA_DEBUG     set to a non-empty value to enable debugging
#   DRY_RUN         set to a non-empty value to enter "dry run mode"
#   INCLUDE_NOTDIR  for check_should_compare; always include mods that
#                   exist in the source but not the destination

# TODO:
# When copying mods, always remove files and directories that exist on
# the destination but don't exist on the source. The two scripts
# currently provide -D for this purpose.

# Constants because `return true` doesn't work and `return 0` on
# success looks weird to a Python programmer
true; export T=$?
false; export F=$?

# Print an error message to stderr
error() { # <message...>
  echo -e "\033[1;31mERROR\033[0m: $@" >&2
}

# Print a debugging message to stderr if debugging is enabled
log() { # <message...>
  if [[ -n "${NOITA_DEBUG:-}" ]]; then
    echo -e "\033[3mDEBUG\033[0m: $@" >&2
  fi
}

# Print an informational message to stderr
info() { # <message...>
  echo -e "\033[1mINFO\033[0m: $@" >&2
}

# Execute a command if DRY_RUN is unset, print the command otherwise
dry() { # <command...>
  if [[ -z "${DRY_RUN:-}" ]]; then
    $@
    return $?
  else
    info "DRY: $@"
    return $F
  fi
}

# Invoke a command with logging and checking
checked() { # <command...>
  declare -a cmd_args=()
  for arg in "$@"; do
    local argq="$(printf '%q' "$arg")"
    if [[ "$argq" != "$arg" ]]; then
      cmd_args+=("'$arg'")
    else
      cmd_args+=("$arg")
    fi
  done
  log "checked argv=${#cmd_args[@]} ${cmd_args[@]}"
  $@
  local status=$?
  if [[ $status -ne 0 ]]; then
    error "command ${cmd_args[0]} exited with non-zero $status"
    exit 1
  fi
  return $status
}

# Echo the path to the Steam base directory, or exit on error
find_steam() { # no args
  local steam_root="$HOME/.steam"
  if [[ -d "$steam_root" ]]; then
    if [[ -h "$steam_root/steam" ]]; then
      echo "$(readlink -f "$steam_root/steam")"
    elif [[ -h "~/.steam/root" ]]; then
      echo "$(readlink -f "$steam_root/root")"
    else
      echo "error: failed to locate Steam" >&2
      exit 1
    fi
  else
    echo "error: failed to locate Steam: ~/.steam missing" >&2
    exit 1
  fi
}

# True if a path is indeed a mod by looking for mod.xml and init.lua
is_mod() { # <path>
  if [[ -d "$1" ]]; then
    if [[ -f "$1/mod.xml" ]]; then
      if [[ -f "$1/init.lua" ]]; then
        return $T
      fi
    fi
  fi
  return $F
}

# Enumerate mods in a given directory
list_mods() { # <path>
  for modpath in "$1"/*/; do
    if is_mod "$modpath"; then
      echo "$modpath"
    fi
  done
}

# Evaluates to true if we should examine the mod having the given name
check_mod_name() {
  case "$1" in
    shift_query) return $T;;
    kae_*) return $T;;
    *) return $F;;
  esac
}

# Evaluates to true if we should copy the mod to the given directory
# Set INCLUDE_NOTDIR to a non-empty value to force including mods
# where the destination does not exist (or is not a directory),
# regardless of the mod's actual name.
check_should_compare() { # <src-path> <dest-root>
  local modname="$(basename "$1")"
  local destpath="$2/$modname"
  if check_mod_name "$modname"; then
    return $T
  elif [[ ! -d "$destpath" ]]; then
    if [[ -n "${INCLUDE_NOTDIR:-}" ]]; then
      return $T
    fi
  fi
  return $F
}

# Compare two directories to determine if replication should occur
compare_paths() { # <remote-dir> <local-dir>
  if [[ -d "$2" ]]; then
    if diff -q -r -x '.*' "$1" "$2"; then
      return $F
    fi
    return $T
  fi
  return $T
}

# Copy a directory into another directory
copy_mod() { # <source-path> <dest-root>
  local src_path="$1"
  local dest_root="$2"
  local dest_path="$2/$(basename "$1")"
  if [[ -n "${DELETE_BEFORE:-}" ]]; then
    if [[ -d "$dest_path" ]]; then
      dry checked rm -r "$dest_path"
    fi
  fi
  dry checked cp -r "$src_path" "$dest_root"
}

