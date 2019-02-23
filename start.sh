#!/bin/bash
export FLASK_APP=three_oh_one/server.py
export FLASK_ENV=development
python3 -m flask run --host=0.0.0.0
