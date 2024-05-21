#!/bin/bash

# Common functions used by both of the mod copy scripts

# Environment variables:
#   DRY_RUN         if non-empty, enter "dry run mode"
#   NOCOLOR         if non-empty, disable colors
#   NOITA_TRACE     if non-empty, print diffs
#   NOITA_DEBUG     if non-empty, enable debugging
#   STEAM           alternate path to the Steam root directory
#   DELETE_BEFORE   if non-empty, rm -r $mod_dest prior to copying
#   MOD_INCL_PATS   array; can be modified to force include named mods
#   MOD_EXCL_PATS   array; can be modified to force exclude named mods
#   INC_NODEST      for check_should_compare; always include mods that
#                   exist in the source but not the destination

# Note on diffs: files and directories starting with a period are
# skipped on compare. This behavior cannot be altered.

# TODO:
# When copying mods, always remove files and directories that exist on
# the destination but don't exist on the source. The two scripts
# currently provide -D for this purpose.

# Constants because `return true` doesn't work and `return 0` on
# success looks weird to a Python programmer
true; export T=$?
false; export F=$?

# Always process these mods
declare -a MOD_INCL_PATS=(
  'shift_query'   # custom mod that lists fungal shifts
  '^kae[_-]'      # all mods starting with 'kae_'
  '^k[_-]'        # all mods starting with 'k_' or 'k-'
  '[_-]k$'        # all mods ending with '_k' or '-k'
)

# Omit these specific mods
declare -a MOD_EXCL_PATS=(
  "cheatgui-k"
)

# Format a string with a CSI escape sequence
color() { # <code> <message...>
  let ncodes=$#-1
  local IFS=';'
  local code=${*:1:$ncodes}
  local msg="${@:$#}"
  if [[ -z "${NOCOLOR:-}" ]]; then
    echo -e "\033[${code}m${msg}\033[0m"
  else
    echo "${msg}"
  fi
}

# Print a diagnostic message of some kind to stderr
diag() { # <prefix> <message...>
  echo -e "$1: ${@:2}" >&2
}

# Print an error message to stderr
error() { # <message...>
  diag "$(color 1 31 ERROR)" "$@"
}

# Print a warning message to stderr
warn() { # <message...>
  diag "$(color 1 93 WARNING)" "$@"
}

# Print a debugging message to stderr if debugging is enabled
log() { # <message...>
  if [[ -n "${NOITA_DEBUG:-}" ]]; then
    diag "$(color 94 DEBUG)" "$@"
  fi
}

# Print an informational message to stderr
info() { # <message...>
  diag "$(color 96 INFO)" "$@"
}

# Print a variable's value for debugging
repr() { # <varname> [default]
  if declare -p "$1" >/dev/null 2>&1; then
    echo "$1=$(declare -p "$1" 2>&1 | sed -e 's/^[^=]*=//')"
  else
    echo "$1=${2:-unset}"
  fi
}

# Print an array's contents, like repr does, but less noisy
repr_array() { # <varname> [default]
  if declare -p "$1" >/dev/null 2>&1; then
    local -n ref="$1"
    printf "%s[%d]=(" "$1" ${#ref[@]}
    for ((i=0; i<${#ref[@]}; i+=1)); do
      if [[ $i -ne 0 ]]; then printf " "; fi
      printf '"%s"' "${ref[$i]}"
    done
    printf ")"
  else
    printf "%s[] unset" "$1"
  fi
  printf "\n"
}

# Execute a command if DRY_RUN is unset, print the command otherwise
dry() { # <command...>
  if [[ -z "${DRY_RUN:-}" ]]; then
    $@
    return $?
  else
    info "$(color 93 DRY): $@"
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

# Locate the Steam base directory or exit with an error if not found
find_steam() { # no args
  declare -a steam_paths=("$HOME/.steam")
  declare -a steam_links=("steam" "root")
  if [[ -n "${STEAM:-}" ]]; then
    steam_paths+=("$STEAM")
  fi
  for sroot in "${steam_paths[@]}"; do
    for slink in "${steam_links[@]}"; do
      if [[ -h "$sroot/$slink" ]] && [[ -d "$sroot/$slink" ]]; then
        echo "$(readlink -f "$sroot/$slink")"
        return $T
      fi
    done
  done
  error "failed to locate Steam; please set STEAM=<steam-root>"
  exit 1
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
      echo "$modpath" | sed -e 's/^\.\///' -e 's/\/$//'
    fi
  done
}

# Evaluates to true if we should examine the mod having the given name
check_include_byname() {
  for pat in "${MOD_INCL_PATS[@]}"; do
    if [[ $1 =~ $pat ]]; then
      return $T
    fi
  done
  return $F
}

# Evaluates to true if we should omit the mod having the given name
check_exclude_byname() {
  for pat in "${MOD_EXCL_PATS[@]}"; do
    if [[ $1 =~ $pat ]]; then
      return $T
    fi
  done
  return $F
}

# Evaluates to true if we should copy the mod to the given directory.
# Set INC_NODEST to a non-empty value to force including mods where
# the destination does not exist (or is not a directory), regardless
# of the mod's actual name.
check_should_compare() { # <src-path> <dest-root>
  local modname="$(basename "$1")"
  local destpath="$2/$modname"
  if check_exclude_byname "$modname"; then
    log "excluding $modname (as $destpath) by name pattern"
    return $F
  elif check_include_byname "$modname"; then
    log "including $modname (as $destpath) by name pattern"
    return $T
  elif [[ ! -d "$destpath" ]]; then
    if [[ -n "${INC_NODEST:-}" ]]; then
      log "including $modname (as $destpath) as destination does not exist"
      return $T
    fi
  fi
  return $F
}

# Compare two directories to determine if replication should occur
compare_paths() { # <remote-dir> <local-dir>
  local -a diff_args=()
  if [[ -z "${NOITA_TRACE:-}" ]]; then
    diff_args+=(-q)
  fi
  if [[ -d "$2" ]]; then
    if diff ${diff_args[@]} -r -x '.*' -x '*.zip' "$1" "$2"; then
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
  if [[ ! -d "$dest_path" ]]; then
    dry checked mkdir "$dest_path"
  fi
  dry checked cp -r "$src_path/*" "$dest_path"
}

