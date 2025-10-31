#!/bin/sh
set -eu

# Defaults for Python-only deployment
FLASK_PORT=${FLASK_PORT:-23182}
BACKEND=${BACKEND:-python}
BASE_NAME=${BASE_NAME:-test}

# Start Python proxy (Flask app)
export BACKEND FLASK_PORT BASE_NAME
exec python -m python_app.app
