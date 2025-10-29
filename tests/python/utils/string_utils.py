"""
String utility functions - Migration from OCaml Name module.

This module replicates the OCaml string manipulation functions from GeneWeb,
specifically migrating Name.strip_c, Name.purge, and Name.contains_forbidden_char.

OCaml Reference:
- source_geneweb/lib/util/name.ml: String utility implementations
- source_geneweb/lib/util/name.mli: Function signatures and documentation

Issue: MIG-007 - Migrate string utility functions
"""

# Forbidden characters list (matches OCaml forbidden_char)
FORBIDDEN_CHAR = [':', '@', '#', '=', '$']


def strip_c(s: str, c: str) -> str:
    """
    Remove all occurrences of character c from string s.
    
    Replicates OCaml Name.strip_c behavior which removes all occurrences
    of a given character from a string.
    
    OCaml Reference: source_geneweb/lib/util/name.ml:120-126
    
    Algorithm (from OCaml):
    1. Iterate through each character in the string
    2. Skip characters that match c
    3. Keep all other characters
    4. Build result character by character
    
    Args:
        s: The string to process
        c: The character to remove (must be single character)
    
    Returns:
        String with all occurrences of c removed
    
    Examples:
        >>> strip_c("hello world", "l")
        'heo word'
        >>> strip_c("test@example.com", "@")
        'testexample.com'
        >>> strip_c("a-b-c", "-")
        'abc'
        >>> strip_c("spaces   here", " ")
        'spaceshere'
        >>> strip_c("", "x")
        ''
        >>> strip_c("no matches", "z")
        'no matches'
    
    Raises:
        ValueError: If c is not a single character
    """
    if len(c) != 1:
        raise ValueError(f"strip_c requires a single character, got: {c}")
    
    # Python string replace is efficient for this
    return s.replace(c, '')


def purge(s: str) -> str:
    """
    Remove all forbidden characters from the string.
    
    Removes all characters defined in FORBIDDEN_CHAR list (:, @, #, =, $)
    from the string. This is equivalent to calling strip_c for each
    forbidden character.
    
    OCaml Reference: source_geneweb/lib/util/name.ml:141
    OCaml Implementation: List.fold_left strip_c s forbidden_char
    
    Args:
        s: The string to purge
    
    Returns:
        String with all forbidden characters removed
    
    Examples:
        >>> purge("user@example.com")
        'userexample.com'
        >>> purge("price = $100")
        'price  100'
        >>> purge("file#1: name")
        'file1 name'
        >>> purge("normal text")
        'normal text'
        >>> purge("")
        ''
    
    Notes:
        - Forbidden characters: ':', '@', '#', '=', '$'
        - Multiple forbidden characters are all removed
        - Other characters including spaces are preserved
    """
    result = s
    for forbidden_char in FORBIDDEN_CHAR:
        result = strip_c(result, forbidden_char)
    return result


def contains_forbidden_char(s: str) -> bool:
    """
    Check if string contains any forbidden character.
    
    Returns True if the string contains any character from the
    FORBIDDEN_CHAR list (:, @, #, =, $), False otherwise.
    
    OCaml Reference: source_geneweb/lib/util/name.ml:234
    OCaml Implementation: List.exists (String.contains s) forbidden_char
    
    Args:
        s: The string to check
    
    Returns:
        True if string contains any forbidden character, False otherwise
    
    Examples:
        >>> contains_forbidden_char("user@example.com")
        True
        >>> contains_forbidden_char("price = 100")
        True
        >>> contains_forbidden_char("file#1")
        True
        >>> contains_forbidden_char("normal text")
        False
        >>> contains_forbidden_char("")
        False
    
    Notes:
        - Forbidden characters: ':', '@', '#', '=', '$'
        - Case-sensitive check
    """
    return any(char in s for char in FORBIDDEN_CHAR)

