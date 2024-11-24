#!/bin/bash

WORKSHOP_DIR="${WORKSHOP_DIR:-$HOME/.local/share/Steam/steamapps/workshop/content/881100}"

print_usage() {
  cat <<EOF >&2
usage: $0 [-h] [-v] [-D] [-q] [-x ARG] [-P ARG] PATH

options:
    -P ARG  pass ARG to diff
    -x ARG  exclude ARG in the diff check
    -q      display only filenames
    -D      do not add default excludes
    -v      enable ve-rbose diagnostics
    -h      print this message and exit
EOF
}

DEBUG="${DEBUG:-}"
declare -a DIFFARGS=()
NODEFAULT=
while getopts "hvDqx:P:" opt; do
  case $opt in
    P) DIFFARGS+=("$OPTARG");;
    x) DIFFARGS+=(-x "$OPTARG");;
    q) DIFFARGS+=(-q);;
    D) NODEFAULT=1;;
    v) DEBUG=1;;
    h) print_usage; exit 0;;
  esac
done
shift $((OPTIND-1))

if [[ -z "$NODEFAULT" ]]; then
  DIFFARGS+=(-x "*.tar.gz")
  DIFFARGS+=(-x .git -x .gitignore)
  DIFFARGS+=(-x ref -x build -x workshop)
  DIFFARGS+=(-x workshop_id.txt -x workshop.xml -x workshop_preview_image.png)
  DIFFARGS+=(-x README.md)
  DIFFARGS+=(-x "*.sh" -x "*.swp")
fi

debug() {
  if [[ -n "$DEBUG" ]]; then
    echo "DEBUG: $@" >&2
  fi
}

if [[ $# -eq 0 ]]; then
  print_usage
  exit 0
fi

if [[ ! -d "$1" ]]; then
  echo "ERROR: $1 does not exist or is not a directory" >&2
  exit 1
fi

if [[ ! -f "$1/mod_id.txt" ]]; then
  echo "ERROR: $1/mod_id.txt does not exist or is not a file" >&2
  exit 1
fi

MOD_ID=$(cat "$1/workshop_id.txt")
MOD_PATH=$WORKSHOP_DIR/$MOD_ID
echo "Comparing $1 with $MOD_PATH"

if [[ ! -d "$MOD_PATH" ]]; then
  echo "ERROR: Mod $1 not downloaded" >&2
  exit 1
fi

debug "diff ${DIFFARGS[@]} '$1' '$MOD_PATH'"
diff "${DIFFARGS[@]}" "$1" "$MOD_PATH"

if [[ $? -ne 0 ]]; then
  echo "Differences detected" >&2
fi

# vim: set ts=2 sts=2 sw=2:
