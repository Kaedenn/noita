#!/bin/bash

# This script invokes noita_dev.exe with -workshop_upload

STEAM="$HOME/.local/share/Steam"
NOITA="$STEAM/steamapps/common/Noita"
WINE="$STEAM/steamapps/common/Proton - Experimental/files/bin/wine"

export WINEPREFIX="$STEAM/steamapps/compatdata/881100/pfx"
cd "$NOITA" && "$WINE" noita_dev.exe -workshop_upload
