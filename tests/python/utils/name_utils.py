"""
Name processing utilities - Migration from OCaml Name module.

This module replicates the OCaml name processing functions from GeneWeb,
specifically migrating Name.lower and related functionality.

OCaml Reference:
- source_geneweb/lib/util/name.ml: Name.lower implementation
- source_geneweb/lib/util/name.mli: Function signatures and documentation

Issue: MIG-001 - Migrate name_lower function
"""

from unidecode import unidecode


def name_lower(name: str) -> str:
    """
    Convert name to lowercase with Unicode transliteration.
    
    This function replicates the OCaml Name.lower behavior:
    - Uppercase letters → lowercase
    - No accents (Unicode → ASCII via unidecode)
    - Non-alphanumeric characters (except '.') → spaces (stripped)
    
    OCaml Reference: source_geneweb/lib/util/name.ml:36-51
    
    Algorithm (from OCaml):
    1. Iterate through each character
    2. If ASCII (< 0x80):
       - Letters/digits/dot: keep (lowercase letters)
       - Other: replace with space (if not at start/end)
    3. If UTF-8 (>= 0x80):
       - Apply unidecode transliteration
       - Lowercase the result
    4. Strip consecutive spaces
    
    Args:
        name: The name to process (can contain UTF-8, accents, etc.)
    
    Returns:
        Normalized lowercase name with ASCII characters only
    
    Examples:
        >>> name_lower("MARTIN")
        'martin'
        >>> name_lower("Jean-François")
        'jean francois'
        >>> name_lower("O'Brien")
        'o brien'
        >>> name_lower("René")
        'rene'
        >>> name_lower("Müller")
        'muller'
        >>> name_lower("Château")
        'chateau'
        >>> name_lower("Smith.Jr")
        'smith.jr'
        >>> name_lower("José María")
        'jose maria'
        >>> name_lower("Владимир")
        'vladimir'
    
    Notes:
        - The dot character '.' is preserved (for suffixes like Jr., Sr.)
        - Multiple spaces are collapsed to single space
        - Leading/trailing spaces are stripped
        - Empty input returns empty string
    """
    if not name:
        return ""
    
    result = []
    special = False  # Track if we need to add space before next char
    
    for char in name:
        char_code = ord(char)
        
        # ASCII characters (< 0x80)
        if char_code < 0x80:
            # Letters, digits, and dot are kept
            if char.isalnum() or char == '.':
                # Add space if we had special chars before
                if special and result:
                    result.append(' ')
                result.append(char.lower())
                special = False
            else:
                # Other characters trigger spacing (but don't add space yet)
                if result:  # Only if we have content (avoid leading spaces)
                    special = True
        else:
            # UTF-8 characters (>= 0x80) - use unidecode
            if special and result:
                result.append(' ')
            
            # Transliterate to ASCII and lowercase
            transliterated = unidecode(char).lower()
            
            # Filter out non-alphanumeric except dots
            for t_char in transliterated:
                if t_char.isalnum() or t_char == '.':
                    result.append(t_char)
            
            special = False
    
    # Join and clean up multiple spaces
    output = ''.join(result)
    
    # Collapse multiple spaces to single space
    while '  ' in output:
        output = output.replace('  ', ' ')
    
    # Strip leading/trailing spaces
    return output.strip()


def strip_lower(name: str) -> str:
    """
    Equivalent to strip(lower(name)) - used for first comparison of names.
    
    This is a composition of name_lower and strip (remove all spaces).
    Used in GeneWeb for:
    - First comparison of names
    - Comparison for first names and surnames
    
    OCaml Reference: source_geneweb/lib/util/name.mli
    
    Args:
        name: The name to process
    
    Returns:
        Normalized lowercase name with no spaces
    
    Examples:
        >>> strip_lower("Jean-François")
        'jeanfrancois'
        >>> strip_lower("DE LA CRUZ")
        'delacruz'
        >>> strip_lower("O'Brien")
        'obrien'
    """
    lowered = name_lower(name)
    return lowered.replace(' ', '')


def contains_only_ascii(name: str) -> bool:
    """
    Check if name contains only ASCII characters.
    
    Args:
        name: The name to check
    
    Returns:
        True if all characters are ASCII (code < 128), False otherwise
    
    Examples:
        >>> contains_only_ascii("Smith")
        True
        >>> contains_only_ascii("René")
        False
        >>> contains_only_ascii("O'Brien")
        True
    """
    return all(ord(char) < 128 for char in name)


def is_normalized_name(name: str) -> bool:
    """
    Check if a name is already in normalized form (output of name_lower).
    
    A normalized name:
    - Contains only lowercase ASCII letters, digits, spaces, and dots
    - Has no consecutive spaces
    - Has no leading/trailing spaces
    
    Args:
        name: The name to check
    
    Returns:
        True if name is normalized, False otherwise
    
    Examples:
        >>> is_normalized_name("jean francois")
        True
        >>> is_normalized_name("Jean-François")
        False
        >>> is_normalized_name("rene")
        True
        >>> is_normalized_name("René")
        False
        >>> is_normalized_name("  spaced  ")
        False
    """
    if not name:
        return True
    
    # Check for leading/trailing spaces
    if name != name.strip():
        return False
    
    # Check for consecutive spaces
    if '  ' in name:
        return False
    
    # Check all characters are lowercase ASCII alphanumeric, space, or dot
    for char in name:
        if char == ' ' or char == '.':
            continue
        if not (char.isalnum() and char.islower() and ord(char) < 128):
            return False
    
    return True
