#!/bin/bash

set -e

# variables (+ we need the env credentials for movebank)
SCRIPT_DIR=$(dirname "$0")
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/dataset_downloader.py"

# echo "ROOT DIR SET TO $SCRIPT_DIR"
# echo "Venv dir SET TO $VENV_DIR"
# echo "Python script SET TO $PYTHON_SCRIPT"

# create venv if it doesnt exist
if [ -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."
fi

source "$VENV_DIR/bin/activate"

# install requirements
echo "Installing dependencies from requiremetns.txt..."
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# check arg
if [ -z "$1" ]; then
    echo "Usage: $0 <number_of_rows>"
    deactivate
    exit 1
fi

echo "Running downloader..."
python "$PYTHON_SCRIPT" "$1"

deactivate

echo "Download complete"
