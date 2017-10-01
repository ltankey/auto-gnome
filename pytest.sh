#!/bin/bash
export PYTHONDONTWRITEBYTECODE='1'

# the .venv is in src/ because docs/ has additional requirements
cd src
source .venv/bin/activate
py.test $@
deactivate
cd ..
