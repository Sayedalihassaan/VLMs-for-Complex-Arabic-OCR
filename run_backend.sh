#!/bin/bash

# Run Backend Server
# This script starts the FastAPI backend server

echo "Starting Document Analyzer Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API key"
    exit 1
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the backend
python backend/main.py
