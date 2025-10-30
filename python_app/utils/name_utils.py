# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
Name processing utilities - Migration from OCaml Name module.
"""

from unidecode import unidecode


def name_lower(name: str) -> str:
    if not name:
        return ""

    result = []
    special = False

    for char in name:
        char_code = ord(char)
        if char_code < 0x80:
            if char.isalnum() or char == '.':
                if special and result:
                    result.append(' ')
                result.append(char.lower())
                special = False
            else:
                if result:
                    special = True
        else:
            if special and result:
                result.append(' ')
            transliterated = unidecode(char).lower()
            for t_char in transliterated:
                if t_char.isalnum() or t_char == '.':
                    result.append(t_char)
            special = False

    output = ''.join(result)
    while '  ' in output:
        output = output.replace('  ', ' ')
    return output.strip()


def name_strip(name: str) -> str:
    return name.replace(' ', '')


def strip_lower(name: str) -> str:
    lowered = name_lower(name)
    return lowered.replace(' ', '')


def contains_only_ascii(name: str) -> bool:
    return all(ord(char) < 128 for char in name)


def is_normalized_name(name: str) -> bool:
    if not name:
        return True
    if name != name.strip():
        return False
    if '  ' in name:
        return False
    for char in name:
        if char == ' ' or char == '.':
            continue
        if not (char.isalnum() and char.islower() and ord(char) < 128):
            return False
    return True


