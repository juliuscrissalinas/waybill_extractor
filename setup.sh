#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Waybill Extractor...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js and try again.${NC}"
    exit 1
fi

# Setup backend
echo -e "${YELLOW}Setting up backend...${NC}"
cd backend || { echo -e "${RED}Backend directory not found${NC}"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }

# Install dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install django djangorestframework django-cors-headers python-dotenv boto3 openpyxl Pillow python-magic django-storages mistralai requests || { echo -e "${RED}Failed to install backend dependencies${NC}"; exit 1; }

# Check if .env file exists
if [ ! -f ../.env ]; then
    echo "Creating .env file..."
    cat > ../.env << EOL
# For AWS Textract (optional)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# For Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here

# Django settings
DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EOL
    echo -e "${YELLOW}Please update the .env file with your actual API keys${NC}"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate || { echo -e "${RED}Failed to run migrations${NC}"; exit 1; }

# Create superuser if needed
echo -e "${YELLOW}Do you want to create a superuser? (y/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

# Create extraction models
echo "Creating extraction models..."
python - << EOF
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waybill_project.settings')
django.setup()

from waybill.models import ExtractionModel

# Create Mistral extraction model
try:
    mistral_model, created = ExtractionModel.objects.get_or_create(
        name='Mistral',
        defaults={
            'description': 'Mistral AI OCR model for waybill extraction',
            'is_active': True
        }
    )
    if created:
        print(f"Created extraction model: {mistral_model.name}")
    else:
        print(f"Extraction model already exists: {mistral_model.name}")

    # Create AWS Textract extraction model
    textract_model, created = ExtractionModel.objects.get_or_create(
        name='AWS Textract',
        defaults={
            'description': 'AWS Textract OCR model for waybill extraction',
            'is_active': True
        }
    )
    if created:
        print(f"Created extraction model: {textract_model.name}")
    else:
        print(f"Extraction model already exists: {textract_model.name}")
except Exception as e:
    print(f"Error creating extraction models: {e}")
EOF

# Deactivate virtual environment
deactivate

# Setup frontend
echo -e "${YELLOW}Setting up frontend...${NC}"
cd ../frontend || { echo -e "${RED}Frontend directory not found${NC}"; exit 1; }

# Install dependencies
echo "Installing frontend dependencies..."
npm install || { echo -e "${RED}Failed to install frontend dependencies${NC}"; exit 1; }

# Return to root directory
cd ..

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To run the application:${NC}"
echo "1. Update the .env file with your actual API keys"
echo "2. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python manage.py runserver"
echo "3. In a new terminal, start the frontend server:"
echo "   cd frontend"
echo "   npm start"
echo "4. Access the application at http://localhost:3000"

echo -e "${GREEN}Happy extracting!${NC}" 