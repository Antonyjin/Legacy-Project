"""
GeneWeb Python Proxy Server - Main Flask Application

This is the main entry point for the Python proxy server.
It can toggle between OCaml and Python backends via BACKEND environment variable.

Usage:
    BACKEND=ocaml python -m python_app.app      # Use OCaml backend
    BACKEND=python python -m python_app.app     # Use Python backend (migrated functions)

Issue: MIG-INF-001 (#225)
"""

import re
import sys
from urllib.parse import urlparse

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


@app.route("/css/<path:subpath>")
def static_css(subpath: str):
    return _proxy_static(f"/css/{subpath}")


@app.route("/js/<path:subpath>")
def static_js(subpath: str):
    return _proxy_static(f"/js/{subpath}")


@app.route("/images/<path:subpath>")
def static_images(subpath: str):
    return _proxy_static(f"/images/{subpath}")


@app.route("/webfonts/<path:subpath>")
def static_webfonts(subpath: str):
    return _proxy_static(f"/webfonts/{subpath}")


def _rewrite_admin_urls(html: bytes) -> bytes:
    """
    Rewrite URLs in HTML to add /admin prefix for gwsetup.

    Handles:
    - href="..." links
    - action="..." form actions
    - src="..." for some resources
    """
    html_str = html.decode("utf-8", errors="ignore")

    def rewrite_url(match):
        """Rewrite a single URL attribute."""
        quote = match.group(1)  # The quote character (" or ')
        url = match.group(2)  # The URL content

        # Skip absolute URLs, data URIs, mailto, anchors, and already rewritten URLs
        if url.startswith(("http://", "https://", "//", "mailto:", "#", "/admin/", "data:")):
            return match.group(0)  # Return unchanged

        # Rewrite relative URLs to include /admin prefix
        # Remove leading slash if present, then add /admin prefix
        clean_url = url.lstrip("/")
        return f"href={quote}/admin/{clean_url}{quote}"

    def rewrite_action(match):
        """Rewrite a form action URL."""
        quote = match.group(1)
        url = match.group(2)

        if url.startswith(("http://", "https://", "//", "#", "/admin/")):
            return match.group(0)

        clean_url = url.lstrip("/")
        return f"action={quote}/admin/{clean_url}{quote}"

    def rewrite_src(match):
        """Rewrite a src URL."""
        quote = match.group(1)
        url = match.group(2)

        if url.startswith(("http://", "https://", "//", "/admin/", "data:")):
            return match.group(0)

        clean_url = url.lstrip("/")
        return f"src={quote}/admin/{clean_url}{quote}"

    # Rewrite href attributes
    html_str = re.sub(r'href=(["\'])([^"\']*)\1', rewrite_url, html_str)

    # Rewrite form action attributes
    html_str = re.sub(r'action=(["\'])([^"\']*)\1', rewrite_action, html_str)

    # Rewrite src attributes for images/css
    html_str = re.sub(r'src=(["\'])([^"\']*)\1', rewrite_src, html_str)

    return html_str.encode("utf-8")


def _rewrite_redirect_url(location: str) -> str:
    """
    Rewrite redirect URLs to go through the proxy.

    Converts:
    - http://geneweb:2317/test -> /test
    - http://geneweb:2316/gwsetup -> /admin/gwsetup
    - Absolute URLs to the backend -> relative URLs through proxy
    """

    try:
        parsed = urlparse(location)
        backend_host = f"{Config.OCAML_GWD_HOST}:{Config.OCAML_GWD_PORT}"
        admin_host = f"{Config.OCAML_GWD_HOST}:{Config.OCAML_GWSETUP_PORT}"

        # If it's a redirect to the backend gwd
        if parsed.netloc == backend_host or parsed.netloc.endswith(f":{Config.OCAML_GWD_PORT}"):
            # Convert to relative URL (proxied through main routes)
            return parsed.path + ("?" + parsed.query if parsed.query else "")

        # If it's a redirect to gwsetup
        if parsed.netloc == admin_host or parsed.netloc.endswith(f":{Config.OCAML_GWSETUP_PORT}"):
            # Convert to /admin prefix
            path = parsed.path
            if not path.startswith("/admin"):
                path = "/admin" + path
            return path + ("?" + parsed.query if parsed.query else "")

        # If it's already a relative URL or different domain, return as-is
        if not parsed.netloc:
            # Already relative, but might need /admin prefix if it's a gwsetup path
            if parsed.path.startswith("/gwsetup") or parsed.path == "/":
                if not parsed.path.startswith("/admin"):
                    return "/admin" + parsed.path + ("?" + parsed.query if parsed.query else "")
            return location

        return location
    except Exception:
        # If parsing fails, return as-is
        return location


def _rewrite_absolute_urls(html: bytes) -> bytes:
    """
    Rewrite absolute URLs in HTML that point to backend to use proxy instead.

    Converts URLs like:
    - http://geneweb:2317/test?lang=en -> /test?lang=en
    - http://geneweb:2316/gwsetup -> /admin/gwsetup
    """

    html_str = html.decode("utf-8", errors="ignore")
    backend_port = Config.OCAML_GWD_PORT
    admin_port = Config.OCAML_GWSETUP_PORT

    def rewrite_absolute_url(match):
        """Rewrite an absolute URL in href attribute."""
        quote_char = match.group(1)
        host = match.group(2)
        port = match.group(3)
        path_and_query = match.group(4)

        # Reconstruct full URL for parsing
        url = f"http://{host}:{port}{path_and_query}"

        try:
            parsed = urlparse(url)

            # Extract port from netloc (format: host:port)
            netloc = parsed.netloc
            if ":" in netloc:
                _, port_part = netloc.rsplit(":", 1)
                try:
                    port = int(port_part)
                except ValueError:
                    port = None
            else:
                port = None

            # Check if URL points to backend gwd (port 2317)
            if port == backend_port or (netloc.endswith(f":{backend_port}")):
                # Convert to relative URL (goes through main proxy routes)
                path = parsed.path
                query = ("?" + parsed.query) if parsed.query else ""
                return f"href={quote_char}{path}{query}{quote_char}"

            # Check if URL points to gwsetup (port 2316)
            if port == admin_port or (netloc.endswith(f":{admin_port}")):
                # Add /admin prefix
                path = parsed.path
                if not path.startswith("/admin"):
                    path = "/admin" + path
                query = ("?" + parsed.query) if parsed.query else ""
                return f"href={quote_char}{path}{query}{quote_char}"

        except Exception:
            # On parse failure, keep original content (safe fallback)
            return match.group(0)

        return match.group(0)  # Return unchanged if we can't parse it

    # Pattern to match absolute HTTP URLs in href attributes
    # Matches: href="http://host:port/path" where port is 2316 or 2317
    html_str = re.sub(
        r'href=(["\'])http://([^"\']+?):(2316|2317)([^"\']*)\1',
        rewrite_absolute_url,
        html_str,
        flags=re.IGNORECASE,
    )

    return html_str.encode("utf-8")


# ---- Admin passthrough (gwsetup) for demo ----
@app.route("/admin", methods=["GET", "POST"])
@app.route("/admin/<path:subpath>", methods=["GET", "POST"])
def admin_passthrough(subpath: str = ""):  # pylint: disable=too-many-locals
    bridge = OCamlBridge()
    try:
        # Remove /admin prefix from subpath before forwarding to gwsetup
        # If subpath starts with admin, strip it
        if subpath.startswith("admin/"):
            subpath = subpath[6:]  # Remove "admin/" prefix

        path = "/" + subpath if subpath else "/"

        # Preserve original query string (GeneWeb uses semicolons, not &)
        # Use request.query_string directly to maintain semicolon format
        qs = request.query_string.decode("utf-8")
        if qs:
            path = f"{path}?{qs}"

        # Handle POST data
        data = None
        files = None
        if request.method == "POST":
            # Forward form data as data for POST
            # For POST, GeneWeb expects form-encoded data with semicolons
            data = dict(request.form)
            # Also handle files if any
            if request.files:
                files = {}
                for k, f in request.files.items():
                    # Reset file pointer
                    f.seek(0)
                    files[k] = (f.filename, f.read(), f.content_type)
                    f.seek(0)  # Reset for potential reuse

        # Proxy the request with the appropriate method
        # Pass path with query string already included (for GET)
        # Pass data/files separately (for POST)
        body, ctype, status_code, headers = bridge.proxy_admin_raw_full(
            path, method=request.method, params=None, data=data, files=files
        )

        # Rewrite Location headers to use proxy host/port
        rewritten_headers = {}
        for key, value in headers.items():
            if key.lower() == "location":
                # Rewrite redirect URLs to go through proxy
                rewritten_location = _rewrite_redirect_url(value)
                rewritten_headers[key] = rewritten_location
            else:
                rewritten_headers[key] = value

        # Only rewrite URLs if it's HTML content
        # Static assets (images, css, js) should be served as-is
        if ctype.startswith("text/html"):
            body = _rewrite_admin_urls(body)
            # Also rewrite absolute URLs in HTML that point to backend
            body = _rewrite_absolute_urls(body)

        response = Response(body, status=status_code, mimetype=ctype)
        for key, value in rewritten_headers.items():
            response.headers[key] = value

        return response
    except Exception as exc:  # pylint: disable=broad-except
        return Response(str(exc), status=502)


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.route("/health")
def health():
    """Health check endpoint."""
    if Config.OCAML_REMOTE:
        gwd_available = f"remote:{Config.OCAML_GWD_HOST}:{Config.OCAML_GWD_PORT}"
    else:
        gwd_available = str(Config.OCAML_GWD_PATH.exists())
    return {
        "status": "ok",
        "backend": Config.BACKEND.value,
        "base_name": Config.BASE_NAME,
        "ocaml_gwd_available": gwd_available,
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
    if Config.OCAML_REMOTE:
        print(f"OCaml gwd available: remote at {Config.OCAML_GWD_HOST}:{Config.OCAML_GWD_PORT}")
    else:
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
