# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
HTTP parameter parsing utilities - Migration from OCaml GeneWeb.
"""

from typing import List, Tuple
from urllib.parse import quote_plus, unquote_plus


def url_encode(s: str) -> str:
    if not s:
        return ""
    return quote_plus(s, safe='', encoding='utf-8')


def url_decode(s: str, strip_spaces: bool = True) -> str:
    if not s:
        return ""
    decoded = unquote_plus(s)
    if strip_spaces:
        decoded = decoded.strip()
    return decoded


def extract_param(key: str, params: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
    if not params:
        return ("", [])
    for i, (k, v) in enumerate(params):
        if k == key:
            decoded_value = url_decode(v)
            remaining = params[:i] + params[i+1:]
            return (decoded_value, remaining)
    return ("", params)


def parse_query_string(query: str) -> List[Tuple[str, str]]:
    if not query:
        return []
    params = []
    for param in query.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            params.append((key, value))
        else:
            params.append((param, ''))
    return params


def extract_all_params(params: List[Tuple[str, str]]) -> dict:
    result = {}
    for key, value in params:
        if key not in result:
            result[key] = url_decode(value)
    return result


