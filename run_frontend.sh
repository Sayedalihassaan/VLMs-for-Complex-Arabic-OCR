#!/bin/bash

# Run Frontend Application
# This script starts the Streamlit frontend

echo "Starting Document Analyzer Frontend..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Warning: Backend is not running!"
    echo "Please start the backend first with: ./run_backend.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the frontend
streamlit run frontend/app.py --server.port=8501
