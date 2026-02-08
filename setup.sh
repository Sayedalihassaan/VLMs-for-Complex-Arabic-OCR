#!/bin/bash

# Setup script for Document Analyzer
# This script sets up the environment and dependencies

set -e  # Exit on error

echo "========================================="
echo "  Document Analyzer - Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.11+ is required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Check for poppler
echo ""
echo "Checking for poppler-utils..."
if command -v pdfinfo >/dev/null 2>&1; then
    echo "✓ poppler-utils is installed"
else
    echo "⚠ poppler-utils not found"
    echo "  Install it with:"
    echo "    macOS:   brew install poppler"
    echo "    Ubuntu:  sudo apt-get install poppler-utils"
    echo "    Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Virtual environment created"
    fi
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
echo "✓ pip upgraded"

# Install requirements
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠ IMPORTANT: Edit .env and add your OpenRouter API key!"
    echo "  Get your key at: https://openrouter.ai/"
else
    echo ".env file already exists"
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x run_backend.sh run_frontend.sh
echo "✓ Scripts are executable"

# Create directories
echo ""
echo "Creating data directories..."
mkdir -p data/uploads data/processed logs
echo "✓ Directories created"

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OpenRouter API key"
echo "  2. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo "  3. Start the backend:"
echo "     ./run_backend.sh"
echo "  4. In a new terminal, start the frontend:"
echo "     ./run_frontend.sh"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
echo "For more information, see README.md"
echo ""
