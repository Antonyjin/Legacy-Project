"""
Statistics page routes.

Handles statistics pages: ?m=STAT
"""

from flask import Blueprint, request, Response
from ..config import Config
from ..ocaml_bridge import OCamlBridge

bp = Blueprint("stats", __name__)


def stats_page():
    """
    Statistics page handler.

    Query parameters:
    - m: Mode (must be "STAT")
    - lang: Language (optional, affects number formatting)
    """
    base_name = getattr(request, "view_args", {}).get("base_name", Config.BASE_NAME)
    if not base_name:
        base_name = Config.BASE_NAME
    mode = request.args.get("m", "").upper()

    if mode != "STAT":
        return "Invalid mode. Use ?m=STAT", 400

    lang = request.args.get("lang", Config.DEFAULT_LANG)

    # Proxy to OCaml (statistics require database access)
    bridge = OCamlBridge()
    path = f"/{base_name}?m=STAT"
    if lang:
        path += f"&lang={lang}"

    try:
        html = bridge.proxy_request(path)
        return Response(html, mimetype="text/html")
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error: {str(exc)}", 500

