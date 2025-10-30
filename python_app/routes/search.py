"""
Search page routes.

Handles search functionality: ?m=S or ?m=NG (name search)
"""

from flask import Blueprint, request, Response
from ..config import Config
from ..ocaml_bridge import OCamlBridge
from ..migrated import (
    name_lower,
    escape_html,
)

bp = Blueprint("search", __name__)


def search_page():
    """
    Search page handler.

    Query parameters:
    - m: Mode ("S" for general search, "NG" for surname search)
    - v: Search query (optional)
    - lang: Language (optional)
    """
    base_name = getattr(request, "view_args", {}).get("base_name", Config.BASE_NAME)
    if not base_name:
        base_name = Config.BASE_NAME
    mode = request.args.get("m", "S").upper()
    query = request.args.get("v", "")
    lang = request.args.get("lang", Config.DEFAULT_LANG)

    if Config.is_python_backend() and query:
        # Normalize query (for future Python search implementation)
        _query_normalized = name_lower(query)

    # Proxy to OCaml (search requires database access)
    bridge = OCamlBridge()
    path = f"/{base_name}?m={mode}"
    if query:
        path += f"&v={escape_html(query)}"
    if lang:
        path += f"&lang={lang}"

    try:
        html = bridge.proxy_request(path)
        return Response(html, mimetype="text/html")
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error: {str(exc)}", 500

