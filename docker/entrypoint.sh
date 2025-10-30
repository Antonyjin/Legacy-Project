#!/bin/sh
set -eu

# Defaults
GW_DIR=${GW_DIR:-/app/GeneWeb/gw}
BASES_DIR=${BASES_DIR:-/app/GeneWeb/bases}
OCAML_GWD_PORT=${OCAML_GWD_PORT:-2317}
FLASK_PORT=${FLASK_PORT:-23182}
BACKEND=${BACKEND:-ocaml}
BASE_NAME=${BASE_NAME:-test}

mkdir -p "$BASES_DIR/etc" || true

# Start gwd (OCaml)
"$GW_DIR/gwd" -bd "$BASES_DIR" -p "$OCAML_GWD_PORT" -daemon true || true

# Wait briefly for gwd to bind
sleep 2

# Start Python proxy
export BACKEND FLASK_PORT BASE_NAME GW_DIR BASES_DIR OCAML_GWD_PORT
exec python -m python_app.app
