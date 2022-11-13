#!/bin/bash

# Common functions between the two copy scripts

# Constants because `return true` doesn't work and `return 0` on success looks
# weird to a Python programmer
true; export T=$?
false; export F=$?

# Evaluates to true if we should copy this mod, false otherwise
should_copy() { # <mod-name>
  case "$1" in
    shift_query) true;;
    kae_*) true;;
    *) false;;
  esac
}

# Print an error message to the terminal
error() { # <message...>
  echo -e "\033[1;31mERROR\033[0m: $@" >&2
}

# Echo a message if debugging is enabled
log() { # <message...>
  if [[ -n "$NOITA_DEBUG" ]]; then
    echo -e "\033[3mDEBUG\033[0m: $@" >&2
  fi
}

# Echo a message
info() { # <message...>
  echo -e "\033[1mINFO\033[0m: $@" >&2
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

# Echos the path to the Steam base directory. Exits on error
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

# Compare two directories to determine if replication should occur
should_replicate() { # <remote-dir> <local-dir>
  if [[ -d "$2" ]]; then
    if diff -q -r -x '.*' "$1" "$2"; then
      false
    else
      true
    fi
  else
    true
  fi
}

# Copy one directory to another
copy_tree() { # <source> <destination>
  cp -r "$1" "$2" || exit $?
}

# True if a path is indeed a mod
is_mod() { # <path>
  if [[ -d "$1" ]]; then
    if [[ -f "$1/mod.xml" ]]; then
      if [[ -f "$1/init.lua" ]]; then
        true; return $?
      fi
    fi
  fi
  false; return $?
}

# Enumerate mods in a given directory
list_mods() { # <path>
  for modpath in "$1"/*/; do
    if is_mod "$modpath"; then
      echo "$modpath"
    fi
  done
}

