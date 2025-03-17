#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Ensure needed directories exist with proper permissions
mkdir -p static staticfiles media
chmod -R 755 static staticfiles media

# Apply migrations first
python manage.py migrate

# Copy Django REST Framework static files
python manage.py copy_drf_static

# Explicitly install DRF CSS and JS into our static directory
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
echo "Using site-packages: $SITE_PACKAGES"
DRF_PATH="$SITE_PACKAGES/rest_framework/static/rest_framework"
echo "DRF static path: $DRF_PATH"

# Make sure static/rest_framework directory exists
mkdir -p static/rest_framework/css
mkdir -p static/rest_framework/js
mkdir -p static/rest_framework/img

# Copy CSS, JS, and image files
cp -r $DRF_PATH/css/* static/rest_framework/css/
cp -r $DRF_PATH/js/* static/rest_framework/js/
cp -r $DRF_PATH/img/* static/rest_framework/img/ 2>/dev/null || true

# Collect static files
echo "Running collectstatic..."
python manage.py collectstatic --noinput --clear

# Set proper permissions for collected files
echo "Setting permissions on staticfiles directory..."
chmod -R 755 staticfiles 