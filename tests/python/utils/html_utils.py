"""
HTML escaping/unescaping utilities - Migration from GeneWeb.

This module provides safe HTML entity escaping/encoding and decoding functions
for use in GeneWeb HTML generation. Essential for preventing XSS attacks and
ensuring proper display of genealogical data with special characters.

Issue: MIG-010 - Migrate HTML escaping functions
OCaml Reference: Used throughout GeneWeb when printing HTML output

Usage in GeneWeb:
- Escaping person names with special characters (e.g., "Smith & Johnson", "O'Brien")
- Escaping place names with quotes (e.g., "New York, "Queens"")
- Escaping dates and events in HTML output
- Preventing XSS attacks from user input
"""

from html import escape as _py_escape, unescape as _py_unescape


def escape_html(text: str, quote: bool = True) -> str:
    """
    Escape special characters into HTML-safe sequences.
    
    This function is used throughout GeneWeb to safely render genealogical data
    in HTML pages. It escapes characters that have special meaning in HTML to
    prevent rendering issues and XSS attacks.
    
    Args:
        text: The string to escape (can be person names, places, dates, notes)
        quote: If True (default), also escape quotes (' and ")
    
    Returns:
        HTML-escaped string safe for rendering
    
    Escaped characters:
        & → &amp;
        < → &lt;
        > → &gt;
        " → &quot; (if quote=True)
        ' → &#x27; (if quote=True)
    
    Examples:
        >>> escape_html("Smith & Johnson")
        'Smith &amp; Johnson'
        >>> escape_html("O'Brien")
        "O&#x27;Brien"
        >>> escape_html('Place: "New York"')
        'Place: &quot;New York&quot;'
        >>> escape_html("Jean-François")
        'Jean-François'  # Unicode preserved
    
    Notes:
        - Unicode characters are preserved (e.g., accents, non-Latin scripts)
        - Used extensively in GeneWeb HTML generation
        - Essential for XSS prevention
    """
    if text is None:
        return ''
    # Python's escape already does the correct transformation
    return _py_escape(text, quote=quote)


def unescape_html(text: str) -> str:
    """
    Decode HTML entities back to original text.
    
    Converts HTML entities (both named and numeric) back to their original
    characters. Used when processing HTML-encoded data.
    
    Args:
        text: HTML-encoded string with entities
    
    Returns:
        Decoded string with entities converted to characters
    
    Examples:
        >>> unescape_html('Smith &amp; Johnson')
        'Smith & Johnson'
        >>> unescape_html('O&#x27;Brien')
        "O'Brien"
        >>> unescape_html('&quot;New York&quot;')
        '"New York"'
        >>> unescape_html('&lt;tag&gt;')
        '<tag>'
    
    Notes:
        - Handles both named entities (&amp;) and numeric (&#x27;)
        - Essential for roundtrip testing (escape → unescape)
        - Used when parsing HTML-encoded data
    """
    if not text:
        return ''
    return _py_unescape(text)
