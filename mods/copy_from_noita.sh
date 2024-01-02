#!/bin/bash

# Copy mods from the Noita mods folder to this directory

source "$(dirname "$0")/mod_copy_util.sh"

print_help() {
  cat <<EOF >&2
usage: $0 [-n] [-o DIR] [-p PAT] [-D] [-C] [-v|-V] [-h] [MOD...]

options:
  -n      dry run; do not actually copy anything
  -o DIR  copy mods to DIR instead of to CWD
  -p PAT  include mods with names matching PAT
  -D      delete destination mod directory before copying
  -C      disable color formatting
  -v      enable verbose diagnostics
  -V      enable very verbose diagnostics and show diffs
  -h      this message

Copies all matching mods from the Noita mods directory to DIR. A mod
"matches" if it matches any pattern in MOD_INCL_PATS.

Specifying a mod on the command-line will prevent this behavior; only
the mod(s) specified will be processed.

MOD_INCL_PATS = (${MOD_INCL_PATS[@]})
EOF
}

export LOCAL_DIR="$(dirname "$0")"
while getopts "no:p:DCvVh" arg; do
  case "$arg" in
    h) print_help; exit 0;;
    V) export NOITA_TRACE=1;;
    v) export NOITA_DEBUG=1;;
    C) export NOCOLOR=1;;
    D) export DELETE_BEFORE=1;;
    o) export LOCAL_DIR="$OPTARG";;
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

  local mod_source="$(find_steam)/steamapps/common/Noita/mods"
  local mod_dest="${LOCAL_DIR:-"$(dirname "$0")"}"

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
      if check_should_compare "$modpath" "$mod_dest"; then
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
      info "Copying $(color 1 3 $modname) from $(color 1 3 $modpath)"
      copy_mod "$modpath" "$modroot"
    else
      log "$modname $moddest is up-to-date with $modpath"
    fi
  done
}

_main

# vim: set ts=2 sts=2 sw=2:
