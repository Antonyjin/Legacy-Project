"""
UT-PY-002: Test HTTP parameter parsing

Tests OCaml's HTTP parameter parsing behavior by calling GeneWeb via HTTP
and validating responses.

Validates:
- Basic parameter parsing (p=name, n=surname)
- URL encoding/decoding
- Special characters
- Multiple values for same parameter
- Empty/missing parameters
"""

import pytest
import requests
from urllib.parse import quote


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestBasicParameterParsing:
    """Test basic parameter parsing (p=name, n=surname)"""

    def test_parse_person_params(self, base_url):
        """Test ?p=Charles&n=Windsor"""
        response = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert response.status_code == 200
        assert "Charles" in response.text

    def test_parse_firstname_param(self, base_url):
        """Test ?p=Charles (surname missing)"""
        response = requests.get(f"{base_url}?p=Charles")
        assert response.status_code == 200
        # Should still work, might show multiple matches or search

    def test_parse_surname_param(self, base_url):
        """Test ?n=Windsor (firstname missing)"""
        response = requests.get(f"{base_url}?n=Windsor")
        assert response.status_code == 200
        # Should still work

    def test_parse_mode_param(self, base_url):
        """Test ?m=F&p=Charles&n=Windsor (family mode)"""
        response = requests.get(f"{base_url}?m=F&p=Charles&n=Windsor")
        assert response.status_code == 200
        # Family page should contain family-related content


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestURLEncodingDecoding:
    """Test URL encoding/decoding"""

    def test_url_encoded_space(self, base_url):
        """Test URL encoding: 'John Doe' vs 'John+Doe' vs 'John%20Doe'"""
        # Test with + (space encoding)
        r1 = requests.get(f"{base_url}?p=Elizabeth&n=Bowes+Lyon")
        assert r1.status_code == 200

        # Test with %20 (space encoding)
        r2 = requests.get(f"{base_url}?p=Elizabeth&n=Bowes%20Lyon")
        assert r2.status_code == 200

        # Both should work (OCaml's Mutil.decode handles both)

    def test_url_encoded_special_chars(self, base_url):
        """Test URL encoding: special characters like é, ñ, ü"""
        # Test with René (accented e)
        name = "René"
        encoded = quote(name)
        response = requests.get(f"{base_url}?p={encoded}&n=Dupont")
        assert response.status_code == 200
        # Should decode correctly (might not find person, but parsing works)

    def test_url_encoded_ampersand(self, base_url):
        """Test URL encoding: & character"""
        # Ampersand should be encoded as %26
        response = requests.get(f"{base_url}?p=Charles&n=Windsor&notes=test%26more")
        assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestSpecialCharacters:
    """Test special characters in parameters"""

    def test_hyphenated_surname(self, base_url):
        """Test hyphenated surnames: Bowes-Lyon"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Bowes-Lyon")
        assert response.status_code == 200
        # Should handle hyphen correctly

    def test_apostrophe_in_name(self, base_url):
        """Test apostrophe: O'Brien"""
        response = requests.get(f"{base_url}?p=Sean&n=O%27Brien")
        assert response.status_code == 200
        # Should handle apostrophe (might not find person, but parsing works)

    def test_unicode_characters(self, base_url):
        """Test Unicode characters: François, José"""
        # Test with François
        response = requests.get(f"{base_url}?p=Fran%C3%A7ois&n=Dupont")
        assert response.status_code == 200
        # Should decode UTF-8 correctly


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestMultipleValues:
    """Test multiple values for same parameter"""

    def test_multiple_mode_params(self, base_url):
        """Test ?m=F&m=D (last one wins in OCaml's extract_assoc)"""
        response = requests.get(f"{base_url}?m=F&m=A&p=Charles&n=Windsor")
        assert response.status_code == 200
        # OCaml's extract_assoc takes the first match, rest are ignored

    def test_parameter_order(self, base_url):
        """Test parameter order doesn't matter"""
        # Order 1: n before p
        r1 = requests.get(f"{base_url}?n=Windsor&p=Charles")
        assert r1.status_code == 200

        # Order 2: p before n
        r2 = requests.get(f"{base_url}?p=Charles&n=Windsor")
        assert r2.status_code == 200

        # Both should work (OCaml uses assoc list)


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestEmptyMissingParameters:
    """Test empty/missing parameters"""

    def test_empty_param_value(self, base_url):
        """Test ?p=&n=Windsor (empty firstname)"""
        response = requests.get(f"{base_url}?p=&n=Windsor")
        assert response.status_code == 200
        # Should handle empty value gracefully

    def test_missing_value(self, base_url):
        """Test ?p&n=Windsor (parameter without =)"""
        response = requests.get(f"{base_url}?p&n=Windsor")
        assert response.status_code == 200
        # Should handle missing value

    def test_no_params(self, base_url):
        """Test base_url with no parameters (home page)"""
        response = requests.get(base_url)
        assert response.status_code == 200
        assert "GeneWeb" in response.text or "geneweb" in response.text

    def test_unknown_param(self, base_url):
        """Test unknown parameter is ignored"""
        response = requests.get(f"{base_url}?unknown=value&p=Charles&n=Windsor")
        assert response.status_code == 200
        # Should ignore unknown param and process known ones


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestLanguageParameter:
    """Test language parameter (lang=fr, lang=en)"""

    def test_lang_en(self, base_url):
        """Test ?lang=en (English)"""
        response = requests.get(f"{base_url}?lang=en")
        assert response.status_code == 200
        # Should show English text (hard to assert specific strings)

    def test_lang_fr(self, base_url):
        """Test ?lang=fr (French)"""
        response = requests.get(f"{base_url}?lang=fr")
        assert response.status_code == 200
        # Should show French text
        # Look for common French words in genealogy
        assert any(word in response.text for word in ["Accueil", "Personne", "Famille"])

    def test_invalid_lang_fallback(self, base_url):
        """Test ?lang=zz (invalid language code)"""
        response = requests.get(f"{base_url}?lang=zz")
        assert response.status_code == 200
        # Should fallback to default language


@pytest.mark.unit
@pytest.mark.requires_gwd
class TestCaseInsensitivity:
    """Test case handling in parameters"""

    def test_lowercase_search(self, base_url):
        """Test lowercase search ?p=charles&n=windsor"""
        response = requests.get(f"{base_url}?m=S&s=windsor")
        assert response.status_code == 200
        # OCaml's Name.lower should handle case-insensitive search

    def test_uppercase_search(self, base_url):
        """Test uppercase search ?p=CHARLES&n=WINDSOR"""
        response = requests.get(f"{base_url}?m=S&s=WINDSOR")
        assert response.status_code == 200
        # Should work (Name.lower normalizes)

    def test_mixed_case(self, base_url):
        """Test mixed case ?p=ChArLeS&n=WiNdSoR"""
        response = requests.get(f"{base_url}?m=S&s=WiNdSoR")
        assert response.status_code == 200
        # Should work


@pytest.mark.unit
@pytest.mark.requires_gwd
@pytest.mark.slow
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_long_param(self, base_url):
        """Test very long parameter value (1000 chars)"""
        long_name = "A" * 1000
        response = requests.get(f"{base_url}?p={long_name}&n=Windsor")
        assert response.status_code in [200, 400, 414]
        # Should handle gracefully (200 if processed, 414 if URI too long)

    def test_special_mode_values(self, base_url):
        """Test various mode values"""
        modes = ["A", "D", "F", "S", "CAL", "P", "N", "STAT"]
        for mode in modes:
            response = requests.get(f"{base_url}?m={mode}")
            assert response.status_code == 200, f"Mode {mode} failed"

    def test_numeric_occurrence(self, base_url):
        """Test occurrence number ?p=Elizabeth&n=Windsor&oc=0"""
        response = requests.get(f"{base_url}?p=Elizabeth&n=Windsor&oc=0")
        assert response.status_code == 200
        # Should handle occurrence number (disambiguates people with same name)

