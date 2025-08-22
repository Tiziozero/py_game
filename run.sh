#!/bin/sh

VENV="venv"

# Create venv if it doesn't exist
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi

# Activate venv
. "$VENV/bin/activate"

# Run your script
python3 main.py

