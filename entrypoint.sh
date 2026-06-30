#!/bin/sh
set -e
pip install --quiet -r requirements.txt
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
