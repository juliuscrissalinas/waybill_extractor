#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p staticfiles/rest_framework
mkdir -p media

# Collect static files
python manage.py collectstatic --noinput --clear

# Ensure proper permissions
chmod -R 755 staticfiles/
chmod -R 755 media/

# Apply database migrations
python manage.py migrate

# Create initial extraction models
echo "Creating initial extraction models..."
python create_extraction_models.py

# Explicitly install DRF CSS and JS into our static directory
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
echo "Using site-packages: $SITE_PACKAGES"
DRF_PATH="$SITE_PACKAGES/rest_framework/static/rest_framework"
echo "DRF static path: $DRF_PATH"

# Make sure static/rest_framework directory exists
mkdir -p staticfiles/rest_framework/css
mkdir -p staticfiles/rest_framework/js
mkdir -p staticfiles/rest_framework/img

# Copy CSS, JS, and image files
cp -r $DRF_PATH/css/* staticfiles/rest_framework/css/
cp -r $DRF_PATH/js/* staticfiles/rest_framework/js/
cp -r $DRF_PATH/img/* staticfiles/rest_framework/img/ 2>/dev/null || true

# Set proper permissions for collected files
echo "Setting permissions on staticfiles directory..."
chmod -R 755 staticfiles 