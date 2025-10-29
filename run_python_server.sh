#!/bin/bash
# Quick start script for Python proxy server

set -e  # Exit on error

# Default to OCaml backend
BACKEND=${BACKEND:-ocaml}
FLASK_PORT=${FLASK_PORT:-2318}
GENEWEB_BASE=${GENEWEB_BASE:-test}

echo "Starting GeneWeb Python Proxy Server"
echo "Backend: $BACKEND"
echo "Port: $FLASK_PORT"
echo "Base: $GENEWEB_BASE"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating it..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    echo "✅ Virtual environment created and dependencies installed"
else
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Verify Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install -r requirements.txt --quiet
fi

echo ""
echo "🚀 Starting server..."
echo "   Access: http://localhost:$FLASK_PORT/$GENEWEB_BASE"
echo "   Health: http://localhost:$FLASK_PORT/health"
echo ""

# Run the server
BACKEND=$BACKEND FLASK_PORT=$FLASK_PORT GENEWEB_BASE=$GENEWEB_BASE \
    python -m python_app.app

