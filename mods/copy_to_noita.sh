#!/bin/bash

# Copy mods from this directory to the Noita directory

source "$(dirname "$0")/mod_copy_util.sh"

print_help() {
  cat <<EOF >&2
usage: $0 [-n] [-i DIR] [-v] [-h] [MOD...]

options:
  -n      dry run; do not actually copy anything
  -i DIR  copy mods from DIR instead of from CWD
  -v      enable verbose diagnostics
  -h      this message

Any mods specified on the command-line will automatically be considered
for replication regardless of name.
EOF
}

export LOCAL_DIR="$(dirname "$0")"
while getopts "nvi:h" arg; do
  case "$arg" in
    h) print_help; exit 0;;
    v) export NOITA_DEBUG=1;;
    n) export DRY_RUN=1;;
    i) export LOCAL_DIR="$OPTARG";;
  esac
done
shift $((OPTIND - 1))

declare -a NAMED_MODS=("$@")

log "NOITA_DEBUG=${NOITA_DEBUG:-}"
log "DRY_RUN=${DRY_RUN:-\033[3munset\033[0m}"
log "LOCAL_DIR=${LOCAL_DIR:-\033[3munset\033[0m}"
log "NAMED_MODS[${#NAMED_MODS[@]}]=(${NAMED_MODS[@]})"

# True if we should consider this mod for deployment, false otherwise
check_should_copy() { # <local-path> <remote-root>
  local local_path="$1"
  local mod_name="$(basename "$1")"
  local remote_path="$2/$mod_name"
  # Always replicate mods with certain names
  if should_copy "$mod_name"; then return $T; fi
  # Replicate mods that only exist locally
  if [[ ! -d "$remote_path" ]]; then return $T; fi
  return $F
}

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

  readarray -t mods < <(list_mods "$mod_source")
  declare -A to_compare=()
  for modpath in "${mods[@]}"; do
    local modname="$(basename "$modpath")"
    local moddest="$mod_dest/$modname"
    log "scanning $modname ($modpath)"
    if check_should_copy "$modpath" "$moddest"; then
      log "may need to replicate $modname to $moddest"
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
    if should_replicate "$modpath" "$moddest"; then
      info "Deploying $modname to $moddest"
      if [[ -z "${DRY_RUN:-}" ]]; then
        checked copy_tree "$modpath" "$modroot"
      else
        info "DRY: not replicating '$modpath' to '$modroot'"
      fi
    else
      log "$modname $moddest is up-to-date with $modpath"
    fi
  done
}

_main

# vim: set ts=2 sts=2 sw=2:
