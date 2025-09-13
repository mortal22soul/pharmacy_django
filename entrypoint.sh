#!/bin/sh
set -e

echo "Running makemigrations..."
uv run ./manage.py makemigrations

echo "Running migrate..."
uv run ./manage.py migrate

echo "Starting command: $@"
exec "$@"
