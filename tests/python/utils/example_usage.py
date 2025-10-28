#!/usr/bin/env python3
"""
Example usage of number_formatter utility

Demonstrates how to use the number formatting functionality
that replicates GeneWeb's OCaml behavior.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.number_formatter import format_number_with_separator, get_locale_separator


def demo_basic_formatting():
    """Demonstrate basic number formatting"""
    print("=" * 60)
    print("BASIC NUMBER FORMATTING")
    print("=" * 60)
    
    numbers = [0, 100, 999, 1000, 10000, 100000, 1000000, -5000]
    locales = ['en', 'fr', 'de']
    
    for num in numbers:
        print(f"\nNumber: {num}")
        for locale in locales:
            formatted = format_number_with_separator(num, locale)
            sep = get_locale_separator(locale)
            print(f"  {locale} (sep='{sep}'): {formatted}")


def demo_genealogy_statistics():
    """Demonstrate formatting genealogy statistics"""
    print("\n" + "=" * 60)
    print("GENEALOGY DATABASE STATISTICS")
    print("=" * 60)
    
    # Simulated database statistics
    stats = {
        'total_persons': 15234,
        'total_families': 4567,
        'total_surnames': 1234,
        'total_events': 45678,
    }
    
    for locale in ['en', 'fr', 'de']:
        print(f"\n{locale.upper()} Interface:")
        for key, value in stats.items():
            formatted = format_number_with_separator(value, locale)
            label = key.replace('_', ' ').title()
            print(f"  {label:20s}: {formatted:>15s}")


def demo_multilingual_interface():
    """Demonstrate multilingual interface with same numbers"""
    print("\n" + "=" * 60)
    print("MULTILINGUAL INTERFACE - SAME NUMBER, DIFFERENT FORMATS")
    print("=" * 60)
    
    num = 1234567
    
    languages = {
        'en': 'English',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
        'ru': 'Russian',
        'he': 'Hebrew',
        'zh': 'Chinese',
    }
    
    print(f"\nFormatting {num:,} in different locales:")
    for locale, lang_name in languages.items():
        formatted = format_number_with_separator(num, locale)
        sep = get_locale_separator(locale)
        print(f"  {lang_name:12s} ({locale}): {formatted:>15s} [separator: '{sep}']")


def demo_locale_aliases():
    """Demonstrate locale aliases"""
    print("\n" + "=" * 60)
    print("LOCALE ALIASES")
    print("=" * 60)
    
    num = 50000
    
    aliases = [
        ('en_US', 'en'),
        ('en_GB', 'en'),
        ('fr_FR', 'fr'),
        ('de_DE', 'de'),
        ('es_ES', 'es'),
    ]
    
    print(f"\nFormatting {num} with locale aliases:")
    for alias, base in aliases:
        formatted_alias = format_number_with_separator(num, alias)
        formatted_base = format_number_with_separator(num, base)
        match = "✓" if formatted_alias == formatted_base else "✗"
        print(f"  {alias:6s} → {base:2s}: {formatted_alias:>10s} {match}")


def demo_real_world_geneweb():
    """Demonstrate real-world GeneWeb usage scenarios"""
    print("\n" + "=" * 60)
    print("REAL-WORLD GENEWEB SCENARIOS")
    print("=" * 60)
    
    # Test database (from README)
    print("\n1. Test Database (test.gwb):")
    print(f"   Persons: {format_number_with_separator(188, 'en')}")
    
    # Small genealogy database
    print("\n2. Small Genealogy Database:")
    persons = 1500
    print(f"   EN: {format_number_with_separator(persons, 'en')} persons")
    print(f"   FR: {format_number_with_separator(persons, 'fr')} personnes")
    
    # Medium database
    print("\n3. Medium Genealogy Database:")
    persons = 10000
    families = 3500
    print(f"   EN: {format_number_with_separator(persons, 'en')} persons, "
          f"{format_number_with_separator(families, 'en')} families")
    print(f"   FR: {format_number_with_separator(persons, 'fr')} personnes, "
          f"{format_number_with_separator(families, 'fr')} familles")
    
    # Large database
    print("\n4. Large Genealogy Database:")
    persons = 500000
    events = 1250000
    print(f"   EN: {format_number_with_separator(persons, 'en')} persons, "
          f"{format_number_with_separator(events, 'en')} events")
    print(f"   FR: {format_number_with_separator(persons, 'fr')} personnes, "
          f"{format_number_with_separator(events, 'fr')} événements")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 60)
    print("NUMBER FORMATTING UTILITY - DEMONSTRATION")
    print("Issue: MIG-008 - Migrate number formatting")
    print("=" * 60)
    
    demo_basic_formatting()
    demo_genealogy_statistics()
    demo_multilingual_interface()
    demo_locale_aliases()
    demo_real_world_geneweb()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - tests/python/utils/README.md")
    print("  - tests/python/unit/test_number_formatting.py")
    print("  - source_geneweb/lib/util/mutil.ml (OCaml reference)")
    print()


if __name__ == '__main__':
    main()
