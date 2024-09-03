#!/bin/bash

CONF="$HOME/.local/share/Steam/steamapps/common/Noita/tools_modding/luacheck_config.lua"
BASE="$(dirname "$0")"

if [[ -e "$PWD/.luacheckrc" ]]; then
  CONF="$PWD/.luacheckrc"
elif [[ -e "$BASE/../utility/lua/luacheck_config.lua" ]]; then
  CONF="$BASE/../utility/lua/luacheck_config.lua"
fi

declare -a IGNORE=(
  131 # Unused implicitly defined global variable.
  211 # Unused local variable.
  212 # Unused argument.
  213 # Unused loop variable.
  311 # Value assigned to a local variable is unused.
  512 # Loop can be executed at most once.
  542 # An empty if branch.
  611 # A line consists of nothing but whitespace.
  612 # A line contains trailing whitespace.
  614 # Trailing whitespace in a comment.
)

declare -a lua_args=()

while getopts "cIi:vh" opt; do
  case "$opt" in
    c) CONF="$OPTARG";;
    I) IGNORE=();;
    i) IGNORE+=("$OPTARG");;
    v) set -x;;
    h) cat <<EOF >&2
usage: $0 [-c CONF] [-I] [-i NUM] [-v] [-h] files... args...

options:
    -c CONF   path to config file (default $CONFIG)
    -I        clear error ignore list (default ${IGNORE[@]})
    -i NUM    add NUM to the error ignore list
    -v        enable debugging
    -h        print this message and exit

All arguments after the first filename are passed to luacheck.
EOF
       exit 0;;
  esac
done
shift $((OPTIND-1))

if [[ ${#IGNORE[@]} -gt 0 ]]; then
  lua_args+=(--ignore ${IGNORE[@]})
fi

lua_args+=(--allow-defined)
lua_args+=(--no-max-line-length)
lua_args+=(--exclude-files '**/nxml.lua')
lua_args+=(--codes)

declare -a GLOBALS_EXTRA=(
  GameRegisterStatusEffect
  Reflection_RegisterProjectile
  RegisterPerk
  RegisterGun
  BIOME_NAME
)

luacheck $@ --config "$CONF" --quiet --globals ${GLOBALS_EXTRA[@]} ${lua_args[@]}
