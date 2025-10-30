"""
GeneWeb Python Proxy Server - Main Flask Application

This is the main entry point for the Python proxy server.
It can toggle between OCaml and Python backends via BACKEND environment variable.

Usage:
    BACKEND=ocaml python -m python_app.app      # Use OCaml backend
    BACKEND=python python -m python_app.app     # Use Python backend (migrated functions)

Issue: MIG-INF-001 (#225)
"""

import sys

from flask import Flask, Response, redirect, request

from python_app.config import Config
from python_app.ocaml_bridge import OCamlBridge
from python_app.routes import family, person, search, stats

# Validate configuration on import
try:
    Config.validate()
except (FileNotFoundError, ValueError) as e:
    print(f"Configuration error: {e}", file=sys.stderr)
    print("Hint: Set GENEWEB_DIR to point to GeneWeb directory", file=sys.stderr)
    sys.exit(1)

# Create Flask app
app = Flask(__name__)


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
    # In bridge mode (BACKEND=ocaml): proxy ALL queries (any mode/params) to gwd
    if Config.is_ocaml_backend():
        bridge = OCamlBridge()
        query = request.query_string.decode("utf-8")
        path = f"/{base_name}"
        if query:
            path += f"?{query}"
        try:
            html = bridge.proxy_request(path)
            return Response(html, mimetype="text/html")
        except Exception as exc:  # pylint: disable=broad-except
            return f"Error: {str(exc)}", 502

    # Python-only backend: handle selected modes locally
    mode = request.args.get("m", "").upper()
    if mode == "F":
        request.view_args = {"base_name": base_name}
        return family.family_page()
    if mode in ["S", "NG"]:
        request.view_args = {"base_name": base_name}
        return search.search_page()
    if mode == "STAT":
        request.view_args = {"base_name": base_name}
        return stats.stats_page()
    if "p" in request.args and "n" in request.args:
        request.view_args = {"base_name": base_name}
        return person.person_page()

    return redirect(f"/{base_name}?m=S")


# ---- Static passthrough to gwd for assets (css/js/images/webfonts) ----
def _proxy_static(path: str) -> Response:
    bridge = OCamlBridge()
    try:
        body, ctype = bridge.proxy_request_raw(path)
        return Response(body, mimetype=ctype)
    except Exception as exc:  # pylint: disable=broad-except
        return Response(str(exc), status=502)


@app.route('/css/<path:subpath>')
def static_css(subpath: str):
    return _proxy_static(f"/css/{subpath}")


@app.route('/js/<path:subpath>')
def static_js(subpath: str):
    return _proxy_static(f"/js/{subpath}")


@app.route('/images/<path:subpath>')
def static_images(subpath: str):
    return _proxy_static(f"/images/{subpath}")


@app.route('/webfonts/<path:subpath>')
def static_webfonts(subpath: str):
    return _proxy_static(f"/webfonts/{subpath}")


# ---- Admin passthrough (gwsetup) for demo ----
@app.route('/admin')
@app.route('/admin/<path:subpath>')
def admin_passthrough(subpath: str = ""):
    bridge = OCamlBridge()
    try:
        path = "/" + subpath if subpath else "/"
        # preserve query string
        qs = request.query_string.decode("utf-8")
        if qs:
            path = f"{path}?{qs}"
        body, ctype = bridge.proxy_admin_raw(path)
        return Response(body, mimetype=ctype)
    except Exception as exc:  # pylint: disable=broad-except
        return Response(str(exc), status=502)


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
    print("Starting GeneWeb Python Proxy Server")
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
