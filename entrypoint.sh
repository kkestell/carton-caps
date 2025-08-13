#!/bin/bash
set -e

source .venv/bin/activate

quart init-db
exec quart run --host=0.0.0.0 --port=5000
