#!/bin/bash

# Copy mods from this directory to the Noita directory

source "$(dirname "$0")/mod_copy_util.sh"

print_help() {
  cat <<EOF >&2
usage: $0 [-n] [-i DIR] [-D] [-v] [-V] [-h] [MOD...]

options:
  -n      dry run; do not actually copy anything
  -i DIR  copy mods from DIR instead of from CWD
  -p PAT  include mods with names matching PAT
  -D      delete destination mod directory before copying
  -v      enable verbose diagnostics
  -V      enable very verbose diagnostics: show diffs
  -h      this message

Copies all matching mods from DIR to the Noita mods directory. A mod
"matches" if it satisfies any of the following conditions:
  * matches any pattern in MOD_INCL_PATS
  * exists locally but does not exist in the Noita mod directory

Specifying a mod on the command-line will prevent this behavior; only
the mod(s) specified will be processed.
EOF
  declare -p MOD_INCL_PATS >&2
}

export LOCAL_DIR="$(dirname "$0")"
while getopts "nip:DvVh" arg; do
  case "$arg" in
    h) print_help; exit 0;;
    V) export NOITA_TRACE=1;;
    v) export NOITA_DEBUG=1;;
    D) export DELETE_BEFORE=1;;
    i) export LOCAL_DIR="$OPTARG";;
    p) MOD_INCL_PATS+=("$OPTARG");;
    n) export DRY_RUN=1;;
    *) error "execute $0 -h for usage"; exit 1;;
  esac
done
shift $((OPTIND - 1))

declare -a NAMED_MODS=("$@")

log "NOITA_TRACE=${NOITA_TRACE:-}"
log "NOITA_DEBUG=${NOITA_DEBUG:-}"
log "DRY_RUN=${DRY_RUN:-\033[3munset\033[0m}"
log "LOCAL_DIR=${LOCAL_DIR:-\033[3munset\033[0m}"
log "NAMED_MODS[${#NAMED_MODS[@]}]=(${NAMED_MODS[@]})"

_main() {
  if [[ $SHLVL -eq 1 ]]; then
    echo "error: this script may not be sourced" >&2
    return
  fi

  local mod_source="${LOCAL_DIR:-"$(dirname "$0")"}"
  local mod_dest="$(find_steam)/steamapps/common/Noita/mods"

  if [[ ! -d "$mod_source" ]]; then
    error "$mod_source is not a directory"
    exit 1
  fi

  declare -A to_compare=()
  if [[ ${#NAMED_MODS[@]} -eq 0 ]]; then
    readarray -t mods < <(list_mods "$mod_source")
    for modpath in "${mods[@]}"; do
      local modname="$(basename "$modpath")"
      local moddest="$mod_dest/$modname"
      log "scanning $(color 1 3 $modname) ($modpath)"
      if INC_NODEST=1 check_should_compare "$modpath" "$mod_dest"; then
        log "adding $(color 1 3 $modname) to the mods to compare"
        to_compare+=(["$modpath"]="$moddest")
      fi
    done
  else
    log "restricting processing to ${#NAMED_MODS[@]} mod(s)"
    for modname in "${NAMED_MODS[@]}"; do
      log "adding specifically named mod $(color 1 3 $modname)"
      to_compare+=(["$mod_source/$modname"]="$mod_dest/$modname")
    done
  fi

  info "comparing ${#to_compare[@]} mods"

  for modpath in "${!to_compare[@]}"; do
    local moddest="${to_compare["$modpath"]}"
    local modroot="$(dirname "$moddest")"
    local modname="$(basename "$modpath")"
    log "checking $(color 1 3 $modpath) against $(color 1 3 $moddest)..."
    if compare_paths "$modpath" "$moddest"; then
      info "Deploying $(color 1 3 $modname) to $(color 1 3 $moddest)"
      copy_mod "$modpath" "$modroot"
    else
      log "$modname $moddest is up-to-date with $modpath"
    fi
  done
}

_main

# vim: set ts=2 sts=2 sw=2:
