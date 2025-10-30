"""
Family page routes.

Handles family relationship pages: ?m=F&p=<firstname>&n=<surname>
"""

from flask import Blueprint, Response, request

from python_app.config import Config
from python_app.migrated import escape_html, url_decode
from python_app.ocaml_bridge import OCamlBridge

bp = Blueprint("family", __name__)


def family_page():
    """
    Family relationship page handler.

    Query parameters:
    - m: Mode (must be "F" for family)
    - p: First name
    - n: Surname
    - lang: Language (optional)
    """
    base_name = getattr(request, "view_args", {}).get("base_name", Config.BASE_NAME)
    if not base_name:
        base_name = Config.BASE_NAME
    mode = request.args.get("m", "").upper()

    if mode != "F":
        return "Invalid mode. Use ?m=F", 400

    p_val = request.args.get("p", "")
    n_val = request.args.get("n", "")
    lang = request.args.get("lang", Config.DEFAULT_LANG)

    firstname = url_decode(p_val) if p_val else ""
    surname = url_decode(n_val) if n_val else ""

    # Both backends proxy to OCaml for now (family relationships require database)
    bridge = OCamlBridge()
    path = f"/{base_name}?m=F&p={escape_html(firstname)}&n={escape_html(surname)}"
    if lang:
        path += f"&lang={lang}"

    try:
        html = bridge.proxy_request(path)
        return Response(html, mimetype="text/html")
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error: {str(exc)}", 500
