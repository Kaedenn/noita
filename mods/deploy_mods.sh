#!/bin/bash

# Copy mods from this directory to the Noita directory

source "$(dirname "$0")/mod_copy_util.sh"

print_help() {
  cat <<EOF >&2
usage: $0 [-n] [-i DIR] [-p PAT] [-D] [-C] [-v|-V] [-h] [MOD...]

options:
  -n      dry run; do not actually copy anything
  -i DIR  copy mods from DIR instead of from CWD
  -p PAT  include mods with names matching PAT
  -D      delete destination mod directory before copying
  -C      disable color formatting
  -v      enable verbose diagnostics
  -V      enable very verbose diagnostics and show diffs
  -h      this message

If no mods are specified on the command-line, then this script
copies all matching mods from DIR to the Noita mods directory.

A mod "matches" if it satisfies any of the following conditions:
  * matches any pattern in MOD_INCL_PATS but does not match any
    pattern in MOD_EXCL_PATS (see below)
  * exists locally but does not exist in the Noita mod directory

Otherwise, only the specified mod(s) are processed, regardless
of name and exclude/include patterns.

environment variables:
  DRY_RUN   if non-empty, equivalent to passing -n
  NOCOLOR   if non-empty, equivalent to passing -C
  STEAM     path to Steam directory; path is deduced otherwise

EOF
  repr_array MOD_INCL_PATS >&2
  repr_array MOD_EXCL_PATS >&2
}

export LOCAL_DIR="$(dirname "$0")"
while getopts "ni:p:DCvVh" arg; do
  case "$arg" in
    h) print_help; exit 0;;
    V) export NOITA_DEBUG=1;
       export NOITA_TRACE=1;;
    v) export NOITA_DEBUG=1;;
    C) export NOCOLOR=1;;
    D) export DELETE_BEFORE=1;;
    i) export LOCAL_DIR="$OPTARG";;
    p) MOD_INCL_PATS+=("$OPTARG");;
    n) export DRY_RUN=1;;
    *) error "execute $0 -h for usage"; exit 1;;
  esac
done
shift $((OPTIND - 1))

declare -a NAMED_MODS=("$@")

log $(repr NOITA_TRACE "$(color 3 unset)")
log $(repr NOITA_DEBUG "$(color 3 unset)")
log $(repr DRY_RUN "$(color 3 unset)")
log $(repr LOCAL_DIR "$(color 3 unset)")
log $(repr NAMED_MODS)
if [[ -n "${TEST_ARGV:-}" ]]; then exit; fi

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
      local c_path="$(color 1 3 94 $modpath)"
      local c_name="$(color 1 3 96 $modname)"
      local c_dest="$(color 1 3 94 $moddest)"

      log "scanning $c_name ($c_path)"
      local action=
      local reason=
      if check_exclude_byname "$modname"; then
        action="excluding"
        reason="explicitly by name"
      elif [[ ! -d "$mod_dest/$modname" ]]; then
        action="including"
        reason="because destination does not exist"
      elif check_include_byname "$modname"; then
        action="including"
        reason="by whitelisted name pattern"
      else
        action="excluding"
        reason="implicitly by name"
      fi
      local c_reason="$(color 3 "$reason")"
      if [[ "$action" == "including" ]]; then
        log "$(color 1 92 $action) $c_name (as $c_path) $c_reason"
        to_compare+=(["$modpath"]="$moddest")
      elif [[ "$action" == "excluding" ]]; then
        log "$(color 1 33 $action) $c_name (as $c_path) $c_reason"
      else
        error "unexpected action $(color 1 93 $action)"
        error "while processing mod $c_name (at $c_path)"
        exit 1
      fi
    done
  else
    log "restricting processing to ${#NAMED_MODS[@]} mod(s)"
    for modname in "${NAMED_MODS[@]}"; do
      if ! is_mod "$mod_source/$modname"; then
        warn "$(color 1 96 "$mod_source/$modname") is not a valid mod!"
      else
        log "adding specifically named mod $(color 1 3 $modname)"
        to_compare+=(["$mod_source/$modname"]="$mod_dest/$modname")
      fi
    done
  fi

  info "comparing ${#to_compare[@]} mods"
  if [[ ${#to_compare[@]} -eq 0 ]]; then
    error "no mods to process"
    exit 1
  fi

  for modpath in "${!to_compare[@]}"; do
    local moddest="${to_compare["$modpath"]}"
    local modroot="$(dirname "$moddest")"
    local modname="$(basename "$modpath")"

    local c_path="$(color 1 3 94 $modpath)"
    local c_name="$(color 1 3 96 $modname)"
    local c_dest="$(color 1 3 94 $moddest)"
    log "comparing $c_path with $c_dest..."
    if compare_paths "$modpath" "$moddest"; then
      # FIXME: only copy mod if destination is a mod or doesn't exist
      # refuse to overwrite something that isn't a mod
      info "deploying $c_name (at $c_path) to $c_dest"
      copy_mod "$modpath" "$modroot"
    else
      log "$modname $moddest is up-to-date with $modpath"
    fi
  done
}

_main

# vim: set ts=2 sts=2 sw=2:
