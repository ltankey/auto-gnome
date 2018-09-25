#!/bin/bash
export PYTHONDONTWRITEBYTECODE='1'

# the .venv is in gnome/ because docs/ has additional requirements
cd gnome
source .venv/bin/activate
py.test $@
deactivate
cd ..
