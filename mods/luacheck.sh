#!/bin/bash

CONF="$HOME/.local/share/Steam/steamapps/common/Noita/tools_modding/luacheck_config.lua"
BASE="$(dirname "$0")"

if [[ -e "$BASE/../utility/lua/luacheck_config.lua" ]]; then
  CONF="$BASE/../utility/lua/luacheck_config.lua"
fi

declare -a IGNORE=(131 211 212 213 311 542 611 612 614)
declare -a lua_args=()

while getopts "cIi:a:vh" opt; do
  case "$opt" in
    c) CONF="$OPTARG";;
    I) IGNORE=();;
    i) IGNORE+=("$OPTARG");;
    a) lua_args+=("$OPTARG");;
    v) set -x;;
    h) echo "usage: $0 [-c CONF] [-I] [-i NUM] [-a ARG] [-v] [-h]" >&2; exit 0;;
  esac
done
shift $((OPTIND-1))
echo "$@" >&2

if [[ ${#IGNORE[@]} -gt 0 ]]; then
  lua_args+=(--ignore ${IGNORE[@]})
fi

luacheck $@ --config "$CONF" -quiet --allow-defined --no-max-line-length --globals print_error async wait GameRegisterStatusEffect Reflection_RegisterProjectile RegisterPerk RegisterGun BIOME_NAME ${lua_args[@]}
