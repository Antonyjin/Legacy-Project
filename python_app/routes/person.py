# pylint: disable=too-many-locals
"""
Person page routes.

Handles person detail pages: ?p=<firstname>&n=<surname>&oc=<occurrence>
"""

from flask import Blueprint, Response, request

from python_app.config import Config
from python_app.migrated import escape_html, extract_param, name_lower, url_decode
from python_app.ocaml_bridge import OCamlBridge

bp = Blueprint("person", __name__)

# Template placeholder (will be replaced with actual GeneWeb templates)
PERSON_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Person: {{ firstname }} {{ surname }}</title></head>
<body>
    <h1>Person Page</h1>
    <p><strong>Backend:</strong> {{ backend }}</p>
    <p><strong>Name:</strong> {{ firstname }} {{ surname }}</p>
    {% if occurrence %}<p><strong>Occurrence:</strong> {{ occurrence }}</p>{% endif %}
    <pre>{{ debug_info }}</pre>
</body>
</html>
"""


def person_page():
    """
    Person detail page handler.

    Query parameters:
    - p: First name
    - n: Surname
    - oc: Occurrence (optional)
    - lang: Language (optional)
    """
    # Get base_name from view_args (set by app.py) or default
    base_name = getattr(request, "view_args", {}).get("base_name", Config.BASE_NAME)
    if not base_name:
        base_name = Config.BASE_NAME

    # Parse query parameters
    params = list(request.args.items())
    p_val, params = extract_param("p", params)
    n_val, params = extract_param("n", params)
    oc_val, params = extract_param("oc", params)
    lang_val, params = extract_param("lang", params)

    # Decode URL-encoded values
    firstname = url_decode(p_val) if p_val else ""
    surname = url_decode(n_val) if n_val else ""
    occurrence = oc_val if oc_val else "0"
    lang = lang_val if lang_val else Config.DEFAULT_LANG

    if Config.is_python_backend():
        # Python backend: Use migrated functions for processing
        # Normalize names for future search usage (not used yet)
        name_lower(firstname) if firstname else ""
        name_lower(surname) if surname else ""

        # Proxy to OCaml for actual data retrieval (database access not migrated)
        bridge = OCamlBridge()
        path = f"/{base_name}?p={escape_html(firstname)}&n={escape_html(surname)}"
        if occurrence and occurrence != "0":
            path += f"&oc={occurrence}"
        if lang:
            path += f"&lang={lang}"

        try:
            html = bridge.proxy_request(path)
            return Response(html, mimetype="text/html")
        except Exception as exc:  # pylint: disable=broad-except
            return f"Error: {str(exc)}", 500

    # OCaml backend: Direct proxy
    bridge = OCamlBridge()
    path = f"/{base_name}?p={firstname}&n={surname}"
    if occurrence and occurrence != "0":
        path += f"&oc={occurrence}"
    if lang:
        path += f"&lang={lang}"

    try:
        html = bridge.proxy_request(path)
        return Response(html, mimetype="text/html")
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error: {str(exc)}", 500
