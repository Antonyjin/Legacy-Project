#!/bin/bash
# Setup script for Python proxy server virtual environment

set -e  # Exit on error

echo "Setting up Python virtual environment for GeneWeb Proxy Server..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

# Verify installation
echo ""
echo "Verifying installation..."
python -c "import flask; print(f'✅ Flask {flask.__version__} installed')" || { echo "❌ Flask installation failed"; exit 1; }
python -c "import pytest; print(f'✅ pytest installed')" || { echo "❌ pytest installation failed"; exit 1; }
python -c "import requests; print(f'✅ requests installed')" || { echo "❌ requests installation failed"; exit 1; }

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the server:"
echo "  BACKEND=ocaml python -m python_app.app"
echo "  # or"
echo "  BACKEND=python python -m python_app.app"
echo ""
echo "To deactivate when done:"
echo "  deactivate"

