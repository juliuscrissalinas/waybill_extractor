#!/bin/bash

# Load environment variables from .env file
set -a
source .env
set +a

# Print the loaded variables (hiding sensitive information)
echo "Environment variables loaded:"
echo "AWS Region: $AWS_REGION"
echo "AWS Access Key ID: ${AWS_ACCESS_KEY_ID:0:5}..."
echo "AWS Secret Key: ${AWS_SECRET_ACCESS_KEY:0:5}..."
echo "Mistral API Key: ${MISTRAL_API_KEY:0:5}..." 