# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
HTTP parameter parsing utilities - Migration from OCaml GeneWeb.

This module replicates the OCaml HTTP parameter handling functions from GeneWeb,
specifically migrating Mutil.encode, Mutil.decode, and gwd.extract_assoc.

OCaml Reference:
- source_geneweb/lib/util/mutil.ml: encode function (lines 930-979)
- source_geneweb/lib/util/mutil.ml: decode function (lines 982-1039)
- source_geneweb/bin/gwd/gwd.ml: extract_assoc function (lines 174-180)

Issues:
- MIG-004 - Migrate HTTP parameter parsing (decode, extract_param)
- MIG-009 - Migrate URL encoding functions (encode)
"""

from typing import List, Tuple
from urllib.parse import quote_plus, unquote_plus


def url_encode(s: str) -> str:
    """
    Encode string for URL/query string (percent encoding + space to plus).

    This function replicates the OCaml Mutil.encode behavior:
    - Spaces are converted to '+'
    - Special characters are percent-encoded (%XX)
    - Alphanumeric and safe characters remain unchanged

    OCaml Reference: source_geneweb/lib/util/mutil.ml:930-979

    Algorithm (from OCaml):
    1. Check if encoding is needed (contains spaces or special chars)
    2. If not needed, return original string
    3. Otherwise:
       - Space → '+'
       - Special chars → '%XX' (hex encoding)
       - Safe chars → unchanged

    Special characters that get encoded:
        Control chars (0x00-0x1F, 0x7F-0xFF)
        < > " # % { } | \\ ^ ~ [ ] ` ; / ? : @ = & +

    Args:
        s: The string to encode

    Returns:
        URL-encoded string

    Examples:
        >>> url_encode("Hello World")
        'Hello+World'
        >>> url_encode("Jean-François")
        'Jean-Fran%C3%A7ois'
        >>> url_encode("O'Brien")
        "O%27Brien"
        >>> url_encode("price = $100")
        'price+%3D+%24100'
        >>> url_encode("normal")
        'normal'
        >>> url_encode("")
        ''

    Notes:
        - Python's urllib.parse.quote_plus handles both % and + encoding
        - The OCaml version manually processes each character
        - Both produce identical results for most cases
        - Returns original string if no encoding needed

    Usage in GeneWeb:
        - Used to encode parameter values in query strings
        - Used when building URLs with user input
        - Used in form data encoding
    """
    if not s:
        return ""

    # Python's quote_plus does the same as OCaml's encode:
    # - Encodes spaces as '+'
    # - Percent-encodes special characters
    # - Leaves alphanumeric and safe characters unchanged
    return quote_plus(s, safe='', encoding='utf-8')


def url_decode(s: str, strip_spaces: bool = True) -> str:
    """
    Decode URL-encoded string (percent encoding + plus to space).

    This function replicates the OCaml Mutil.decode (gen_decode) behavior:
    - Decodes percent-encoded characters (%XX)
    - Converts '+' to space
    - Optionally strips leading/trailing spaces

    OCaml Reference: source_geneweb/lib/util/mutil.ml:982-1039

    Algorithm (from OCaml):
    1. Check if decoding is needed (contains '%' or '+')
    2. If not needed, return original string
    3. Otherwise:
       - '%XX' → character with hex code XX
       - '+' → space
       - Other characters → unchanged
    4. If strip_spaces=True, remove leading/trailing spaces

    Args:
        s: The URL-encoded string to decode
        strip_spaces: If True, strip leading and trailing spaces (default: True)

    Returns:
        Decoded string

    Examples:
        >>> url_decode("Hello+World")
        'Hello World'
        >>> url_decode("Jean-Fran%C3%A7ois")
        'Jean-François'
        >>> url_decode("O%27Brien")
        "O'Brien"
        >>> url_decode("%20spaces%20")
        'spaces'
        >>> url_decode("%20spaces%20", strip_spaces=False)
        ' spaces '
        >>> url_decode("no+encoding+needed", strip_spaces=False)
        'no encoding needed'

    Notes:
        - Python's urllib.parse.unquote_plus already handles both % and +
        - The OCaml version manually processes each character
        - Both produce identical results
        - Empty string returns empty string

    Usage in GeneWeb:
        - Used in gwd.ml extract_assoc to decode parameter values
        - Used throughout the application for query string parsing
        - Always called with strip_spaces=True in standard usage
    """
    if not s:
        return ""

    # Python's unquote_plus does the same as OCaml's decode:
    # - Decodes %XX sequences
    # - Converts + to space
    decoded = unquote_plus(s)

    if strip_spaces:
        # Strip leading and trailing spaces (OCaml behavior)
        decoded = decoded.strip()

    return decoded


def extract_param(key: str, params: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Extract a parameter from a list of key-value pairs and return its decoded value.

    This function replicates the OCaml gwd.extract_assoc behavior:
    - Searches for the first occurrence of `key` in the param list
    - Returns the decoded value and the remaining list (without that key-value pair)
    - If not found, returns ("", original_list)

    OCaml Reference: source_geneweb/bin/gwd/gwd.ml:174-180

    Algorithm (from OCaml):
    ```ocaml
    let rec extract_assoc key = function
      | [] -> ("", [])
      | ((k, v) as kv) :: kvl ->
          if k = key then (Mutil.decode v, kvl)
          else
            let v, kvl = extract_assoc key kvl in
            (v, kv :: kvl)
    ```

    Args:
        key: The parameter name to search for
        params: List of (key, value) tuples (typically from query string parsing)

    Returns:
        Tuple of (decoded_value, remaining_params)
        - decoded_value: URL-decoded value if found, empty string if not found
        - remaining_params: Original list with the found key-value pair removed

    Examples:
        >>> params = [('name', 'John'), ('age', '30'), ('city', 'Paris')]
        >>> extract_param('name', params)
        ('John', [('age', '30'), ('city', 'Paris')])

        >>> params = [('p', 'jean'), ('n', 'martin'), ('oc', '0')]
        >>> extract_param('p', params)
        ('jean', [('n', 'martin'), ('oc', '0')])

        >>> params = [('name', 'Jean+Fran%C3%A7ois')]
        >>> extract_param('name', params)
        ('Jean François', [])

        >>> params = [('a', '1'), ('b', '2'), ('a', '3')]
        >>> extract_param('a', params)  # Returns first occurrence
        ('1', [('b', '2'), ('a', '3')])

        >>> extract_param('missing', [('a', '1')])
        ('', [('a', '1')])

    Notes:
        - Only the first occurrence is extracted (if duplicates exist)
        - The value is URL-decoded using url_decode()
        - The remaining list preserves the original order
        - Used extensively in GeneWeb for query parameter extraction

    Usage in GeneWeb:
        - Used in gwd.ml to extract parameters like "b", "w", "lang", "opt", etc.
        - Example: `let x, env = extract_assoc "b" env in`
        - Allows sequential extraction of parameters
    """
    if not params:
        return ("", [])

    # Iterate through the list to find the key
    for i, (k, v) in enumerate(params):
        if k == key:
            # Found it! Decode the value and return remaining params
            decoded_value = url_decode(v)
            remaining = params[:i] + params[i+1:]
            return (decoded_value, remaining)

    # Not found, return empty string and original list
    return ("", params)


def parse_query_string(query: str) -> List[Tuple[str, str]]:
    """
    Parse a query string into a list of (key, value) tuples.

    This is a helper function to convert a query string like "p=jean&n=martin&oc=0"
    into a list of tuples that can be used with extract_param.

    Args:
        query: Query string (e.g., "p=jean&n=martin&oc=0")

    Returns:
        List of (key, value) tuples

    Examples:
        >>> parse_query_string("p=jean&n=martin&oc=0")
        [('p', 'jean'), ('n', 'martin'), ('oc', '0')]

        >>> parse_query_string("name=John+Doe&age=30")
        [('name', 'John+Doe'), ('age', '30')]

        >>> parse_query_string("")
        []

        >>> parse_query_string("key_only")
        [('key_only', '')]

        >>> parse_query_string("a=1&b=&c=3")
        [('a', '1'), ('b', ''), ('c', '3')]

    Notes:
        - Values are NOT decoded here (use extract_param or url_decode separately)
        - Empty query string returns empty list
        - Parameters without '=' get empty string value
        - This mimics the structure used in OCaml's environment list
    """
    if not query:
        return []

    params = []
    for param in query.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            params.append((key, value))
        else:
            # Key without value (e.g., "key_only")
            params.append((param, ''))

    return params


def extract_all_params(params: List[Tuple[str, str]]) -> dict:
    """
    Extract all parameters into a dictionary with decoded values.

    This is a convenience function that extracts all parameters and returns
    them as a dictionary. If a key appears multiple times, only the first
    occurrence is kept.

    Args:
        params: List of (key, value) tuples

    Returns:
        Dictionary mapping keys to decoded values

    Examples:
        >>> params = [('p', 'jean'), ('n', 'martin'), ('oc', '0')]
        >>> extract_all_params(params)
        {'p': 'jean', 'n': 'martin', 'oc': '0'}

        >>> params = [('name', 'Jean+Fran%C3%A7ois')]
        >>> extract_all_params(params)
        {'name': 'Jean François'}

        >>> params = [('a', '1'), ('a', '2')]  # Duplicate keys
        >>> extract_all_params(params)
        {'a': '1'}

    Notes:
        - All values are URL-decoded
        - Duplicate keys: first occurrence wins
        - Empty params list returns empty dict
    """
    result = {}
    for key, value in params:
        if key not in result:
            result[key] = url_decode(value)
    return result
