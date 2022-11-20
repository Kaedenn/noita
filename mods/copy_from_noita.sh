#!/bin/bash

# Copy mods from the Noita mods folder to this directory

source "$(dirname "$0")/mod_copy_util.sh"

print_help() {
  cat <<EOF >&2
usage: $0 [-n] [-o DIR] [-D] [-v] [-h] [MOD...]

options:
  -n      dry run; do not actually copy anything
  -o DIR  copy mods to DIR instead of to CWD
  -D      delete destination mod directory before copying
  -v      enable verbose diagnostics
  -h      this message

Any mods specified on the command-line will automatically be considered
for replication regardless of name.
EOF
}

export LOCAL_DIR="$(dirname "$0")"
while getopts "no:Dvh" arg; do
  case "$arg" in
    h) print_help; exit 0;;
    v) export NOITA_DEBUG=1;;
    D) export DELETE_BEFORE=1;;
    o) export LOCAL_DIR="$OPTARG";;
    n) export DRY_RUN=1;;
    *) error "execute $0 -h for usage"; exit 1;;
  esac
done
shift $((OPTIND - 1))

declare -a NAMED_MODS=("$@")

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

  readarray -t mods < <(list_mods "$mod_source")
  declare -A to_compare=()
  for modpath in "${mods[@]}"; do
    local modname="$(basename "$modpath")"
    local moddest="$mod_dest/$modname"
    log "scanning $modname ($modpath)"
    if check_should_compare "$modpath" "$mod_dest"; then
      log "adding $modname to the mods to compare"
      to_compare+=(["$modpath"]="$moddest")
    fi
  done

  for modname in "${NAMED_MODS[@]}"; do
    log "adding specifically named mod $modname"
    to_compare+=(["$mod_source/$modname"]="$mod_dest/$modname")
  done

  info "comparing ${#to_compare[@]} mods"

  for modpath in "${!to_compare[@]}"; do
    local moddest="${to_compare["$modpath"]}"
    local modroot="$(dirname "$moddest")"
    local modname="$(basename "$modpath")"
    log "checking $modpath against $moddest..."
    if compare_paths "$modpath" "$moddest"; then
      info "Copying $modname from $modpath"
      copy_mod "$modpath" "$modroot"
    else
      log "$modname $moddest is up-to-date with $modpath"
    fi
  done
}

_main

# vim: set ts=2 sts=2 sw=2:
