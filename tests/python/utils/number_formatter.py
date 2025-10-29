"""
Number formatting utilities with thousands separator support.

This module replicates the OCaml behavior from Mutil.string_of_int_sep
and the localized thousand separators from GeneWeb's lexicon.txt.

OCaml Reference:
- source_geneweb/lib/util/mutil.ml: string_of_int_sep
- source_geneweb/lib/allnDisplay.ml: format_with_thousand_sep
- GeneWeb/gw/lang/lexicon.txt: (thousand separator) translations
"""

# Thousand separator mappings from GeneWeb's lexicon.txt
# These match the OCaml behavior: transl conf "(thousand separator)"
LOCALE_SEPARATORS = {
    'af': ' ',      # Afrikaans: space
    'ar': '.',      # Arabic: dot
    'bg': ' ',      # Bulgarian: space
    'br': ' ',      # Breton: space
    'ca': '.',      # Catalan: dot
    'co': ' ',      # Corsican: space
    'cs': ' ',      # Czech: space
    'da': '.',      # Danish: dot
    'de': '.',      # German: dot
    'en': ',',      # English: comma
    'eo': '.',      # Esperanto: dot
    'es': '.',      # Spanish: dot
    'et': ' ',      # Estonian: space
    'fi': '.',      # Finnish: dot
    'fr': ' ',      # French: space (narrow no-break space)
    'he': ',',      # Hebrew: comma
    'is': '.',      # Icelandic: dot
    'it': '.',      # Italian: dot
    'lt': '\u00A0', # Lithuanian: non-breaking space
    'lv': "'",      # Latvian: apostrophe
    'nl': '.',      # Dutch: dot
    'no': '.',      # Norwegian: dot
    'oc': ' ',      # Occitan: space
    'pl': '.',      # Polish: dot
    'pt': '.',      # Portuguese: dot
    'ro': '.',      # Romanian: dot
    'ru': "'",      # Russian: apostrophe
    'sk': ' ',      # Slovak: space
    'sl': '.',      # Slovenian: dot
    'sv': '.',      # Swedish: dot
    'tr': ',',      # Turkish: comma
    'zh': '.',      # Chinese: dot
}

# Common locale aliases for convenience
LOCALE_ALIASES = {
    'en_US': 'en',
    'en_GB': 'en',
    'fr_FR': 'fr',
    'de_DE': 'de',
    'es_ES': 'es',
    'it_IT': 'it',
    'pt_BR': 'pt',
    'pt_PT': 'pt',
    'zh_CN': 'zh',
}


def format_number_with_separator(num: int, locale: str = 'en') -> str:
    """
    Format an integer with thousands separator according to locale.
    
    This function replicates the OCaml behavior from:
    - Mutil.string_of_int_sep (source_geneweb/lib/util/mutil.ml)
    - format_with_thousand_sep (source_geneweb/lib/allnDisplay.ml)
    
    Args:
        num: The integer to format
        locale: The locale code (e.g., 'fr', 'en', 'de', 'fr_FR', 'en_US')
                Defaults to 'en' (English with comma separator)
    
    Returns:
        Formatted string with thousands separator
    
    Examples:
        >>> format_number_with_separator(1000, 'en')
        '1,000'
        >>> format_number_with_separator(1000, 'fr')
        '1 000'
        >>> format_number_with_separator(1000, 'de')
        '1.000'
        >>> format_number_with_separator(1000000, 'en')
        '1,000,000'
        >>> format_number_with_separator(0, 'en')
        '0'
        >>> format_number_with_separator(-1000, 'en')
        '-1,000'
    
    Raises:
        ValueError: If locale is not supported
    """
    # Handle locale aliases (e.g., 'en_US' -> 'en')
    if locale in LOCALE_ALIASES:
        locale = LOCALE_ALIASES[locale]
    
    # Validate locale
    if locale not in LOCALE_SEPARATORS:
        raise ValueError(
            f"Unsupported locale: '{locale}'. "
            f"Supported locales: {', '.join(sorted(LOCALE_SEPARATORS.keys()))}"
        )
    
    # Get separator for locale
    separator = LOCALE_SEPARATORS[locale]
    
    # Handle negative numbers
    is_negative = num < 0
    num = abs(num)
    
    # Convert to string
    num_str = str(num)
    
    # If number is less than 1000, no separator needed
    if len(num_str) <= 3:
        return f"-{num_str}" if is_negative else num_str
    
    # Add separators every 3 digits from right to left
    # This replicates the OCaml logic: (len - 1 - i) mod 3 = 0
    result = []
    for i, digit in enumerate(reversed(num_str)):
        if i > 0 and i % 3 == 0:
            result.append(separator)
        result.append(digit)
    
    formatted = ''.join(reversed(result))
    
    return f"-{formatted}" if is_negative else formatted


def get_locale_separator(locale: str = 'en') -> str:
    """
    Get the thousands separator for a given locale.
    
    Args:
        locale: The locale code (e.g., 'fr', 'en', 'de')
    
    Returns:
        The thousands separator character(s) for the locale
    
    Examples:
        >>> get_locale_separator('en')
        ','
        >>> get_locale_separator('fr')
        ' '
        >>> get_locale_separator('de')
        '.'
    
    Raises:
        ValueError: If locale is not supported
    """
    # Handle locale aliases
    if locale in LOCALE_ALIASES:
        locale = LOCALE_ALIASES[locale]
    
    if locale not in LOCALE_SEPARATORS:
        raise ValueError(
            f"Unsupported locale: '{locale}'. "
            f"Supported locales: {', '.join(sorted(LOCALE_SEPARATORS.keys()))}"
        )
    
    return LOCALE_SEPARATORS[locale]
