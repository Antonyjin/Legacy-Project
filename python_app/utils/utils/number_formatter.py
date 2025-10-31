# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Number formatting utilities with thousands separator support.
"""

LOCALE_SEPARATORS = {
    'af': ' ',
    'ar': '.',
    'bg': ' ',
    'br': ' ',
    'ca': '.',
    'co': ' ',
    'cs': ' ',
    'da': '.',
    'de': '.',
    'en': ',',
    'eo': '.',
    'es': '.',
    'et': ' ',
    'fi': '.',
    'fr': ' ',
    'he': ',',
    'is': '.',
    'it': '.',
    'lt': '\u00A0',
    'lv': "'",
    'nl': '.',
    'no': '.',
    'oc': ' ',
    'pl': '.',
    'pt': '.',
    'ro': '.',
    'ru': "'",
    'sk': ' ',
    'sl': '.',
    'sv': '.',
    'tr': ',',
    'zh': '.',
}

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
    if locale in LOCALE_ALIASES:
        locale = LOCALE_ALIASES[locale]
    if locale not in LOCALE_SEPARATORS:
        raise ValueError(
            f"Unsupported locale: '{locale}'. "
            f"Supported locales: {', '.join(sorted(LOCALE_SEPARATORS.keys()))}"
        )
    separator = LOCALE_SEPARATORS[locale]
    is_negative = num < 0
    num = abs(num)
    num_str = str(num)
    if len(num_str) <= 3:
        return f"-{num_str}" if is_negative else num_str
    result = []
    for i, digit in enumerate(reversed(num_str)):
        if i > 0 and i % 3 == 0:
            result.append(separator)
        result.append(digit)
    formatted = ''.join(reversed(result))
    return f"-{formatted}" if is_negative else formatted


def get_locale_separator(locale: str = 'en') -> str:
    if locale in LOCALE_ALIASES:
        locale = LOCALE_ALIASES[locale]
    if locale not in LOCALE_SEPARATORS:
        raise ValueError(
            f"Unsupported locale: '{locale}'. "
            f"Supported locales: {', '.join(sorted(LOCALE_SEPARATORS.keys()))}"
        )
    return LOCALE_SEPARATORS[locale]


