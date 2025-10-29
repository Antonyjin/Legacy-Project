"""
GeneWeb Python Proxy Server - Main Flask Application

This is the main entry point for the Python proxy server.
It can toggle between OCaml and Python backends via BACKEND environment variable.

Usage:
    BACKEND=ocaml python -m python_app.app      # Use OCaml backend
    BACKEND=python python -m python_app.app     # Use Python backend (migrated functions)

Issue: MIG-INF-001 (#225)
"""

import os
import sys
from pathlib import Path

from flask import Flask, request, Response, redirect, url_for

from .config import Config, Backend
from .ocaml_bridge import OCamlBridge
from .routes import person, family, search, stats

# Validate configuration on import
try:
    Config.validate()
except (FileNotFoundError, ValueError) as e:
    print(f"Configuration error: {e}", file=sys.stderr)
    print("Hint: Set GENEWEB_DIR to point to GeneWeb directory", file=sys.stderr)
    sys.exit(1)

# Create Flask app
app = Flask(__name__)

# Register blueprints with base_name parameter
# Routes will be accessible as /<base_name>/person, /<base_name>/family, etc.
# But we handle person/family/search/stats via query params in home route
# So we don't register these blueprints - they're for future use
# app.register_blueprint(person.bp, url_prefix="/<base_name>")
# app.register_blueprint(family.bp, url_prefix="/<base_name>")
# app.register_blueprint(search.bp, url_prefix="/<base_name>")
# app.register_blueprint(stats.bp, url_prefix="/<base_name>")


@app.route("/")
def index():
    """Redirect to default base."""
    return redirect(f"/{Config.BASE_NAME}")


@app.route("/<base_name>")
def home(base_name: str):
    """
    Home page for a base.
    
    Query parameters:
    - lang: Language (optional)
    - m: Mode (optional, for various pages like CAL, P, N, etc.)
    """
    mode = request.args.get("m", "").upper()
    lang = request.args.get("lang", Config.DEFAULT_LANG)
    
    # Route to specific handlers based on mode and query params
    # Pass base_name directly to handlers (they'll extract from context)
    if mode == "F":
        # Family page
        request.view_args = {"base_name": base_name}
        return family.family_page()
    elif mode in ["S", "NG"]:
        # Search page
        request.view_args = {"base_name": base_name}
        return search.search_page()
    elif mode == "STAT":
        # Statistics page
        request.view_args = {"base_name": base_name}
        return stats.stats_page()
    elif "p" in request.args and "n" in request.args:
        # Person page
        request.view_args = {"base_name": base_name}
        return person.person_page()
    
    # Default: Home page - proxy to OCaml for now
    # TODO: Implement Python home page when templates are migrated
    bridge = OCamlBridge()
    path = f"/{base_name}"
    if lang:
        path += f"?lang={lang}"
    
    try:
        html = bridge.proxy_request(path)
        return Response(html, mimetype="text/html")
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "backend": Config.BACKEND.value,
        "base_name": Config.BASE_NAME,
        "ocaml_gwd_available": Config.OCAML_GWD_PATH.exists(),
    }


@app.route("/debug/config")
def debug_config():
    """Debug endpoint to show configuration (development only)."""
    if not Config.DEBUG:
        return "Debug mode disabled", 403
    
    return {
        "backend": Config.BACKEND.value,
        "is_python_backend": Config.is_python_backend(),
        "is_ocaml_backend": Config.is_ocaml_backend(),
        "flask_host": Config.FLASK_HOST,
        "flask_port": Config.FLASK_PORT,
        "geneweb_dir": str(Config.GENEWEB_DIR),
        "bases_dir": str(Config.BASES_DIR),
        "gw_dir": str(Config.GW_DIR),
        "base_name": Config.BASE_NAME,
        "ocaml_gwd_port": Config.OCAML_GWD_PORT,
        "ocaml_gwd_path": str(Config.OCAML_GWD_PATH),
        "ocaml_gwd_exists": Config.OCAML_GWD_PATH.exists(),
    }


def main():
    """Run the Flask development server."""
    print(f"Starting GeneWeb Python Proxy Server")
    print(f"Backend: {Config.BACKEND.value}")
    print(f"Base: {Config.BASE_NAME}")
    print(f"Listening on: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"OCaml gwd available: {Config.OCAML_GWD_PATH.exists()}")
    
    if Config.is_python_backend():
        print("⚠️  Python backend enabled - using migrated functions")
    else:
        print("📦 OCaml backend enabled - proxying to OCaml gwd")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG,
        use_reloader=False,  # Disable reloader when running in subprocess
        threaded=True,  # Enable threading for better subprocess compatibility
    )


if __name__ == "__main__":
    main()

