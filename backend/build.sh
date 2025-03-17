#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create static directories if they don't exist
mkdir -p static
mkdir -p staticfiles

# Apply migrations first
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input 