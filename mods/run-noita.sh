#!/bin/bash

# This script invokes noita.exe with the specified arguments (if any)

# This script is intended for use on Linux with Steam Proton.
# Change any of the following variables if your setup is different.

STEAM="$HOME/.local/share/Steam"
NOITA="$STEAM/steamapps/common/Noita"
WINE="$STEAM/steamapps/common/Proton - Experimental/files/bin/wine"

export WINEPREFIX="$STEAM/steamapps/compatdata/881100/pfx"
cd "$NOITA" && "$WINE" noita.exe "$@"
