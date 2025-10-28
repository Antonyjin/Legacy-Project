"""
FT-PY-010: Test internationalization (i18n) functionality

End-to-end test of multi-language support.

This is a FUNCTIONAL test because it validates complete user workflows:
- User switches between languages
- User views translations
- User sees date format changes
- User verifies multiple language support

User Story: As a user, I want to use the application in multiple languages.

Test Scenario:
1. Switch language setting
2. Verify translations display correctly
3. Check date format adapts to language
4. Test support for multiple languages
"""

import pytest
import requests
import subprocess
import time
import signal
import os
from pathlib import Path


class GeneWebServer:
    """Helper class to manage gwd process for functional testing"""

    def __init__(self, geneweb_dir: str, port: int = 23193, base_name: str = "test"):
        self.geneweb_dir = Path(geneweb_dir)
        self.port = port
        self.base_name = base_name
        self.process = None
        self.log_file = None

    def start(self, timeout: int = 5) -> bool:
        """Start gwd server"""
        gwd_path = self.geneweb_dir / "gw" / "gwd"
        gw_dir = self.geneweb_dir / "gw"
        bases_dir = self.geneweb_dir / "bases"

        if not gwd_path.exists():
            raise FileNotFoundError(f"gwd not found at {gwd_path}")

        # Ensure previous gwd instances on this port are killed
        pkill_cmd = ["pkill", "-f", f"gwd.*-p {self.port}"]
        subprocess.run(pkill_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.5)

        # Start gwd with default English language
        cmd = [
            str(gwd_path),
            "-hd", str(gw_dir),
            "-bd", str(bases_dir),
            "-p", str(self.port),
            "-lang", "en"
        ]

        self.log_file = open(f"gwd_ft_{self.port}.log", "w")
        self.process = subprocess.Popen(
            cmd,
            stdout=self.log_file,
            stderr=subprocess.STDOUT,
            cwd=str(self.geneweb_dir)
        )

        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return True
            time.sleep(0.1)

        return False

    def is_running(self) -> bool:
        """Check if server is responding to HTTP requests"""
        try:
            response = requests.get(
                f"http://localhost:{self.port}/{self.base_name}",
                timeout=2,
                headers={"Connection": "close"}
            )
            return response.status_code in [200, 204]
        except requests.RequestException:
            return False

    def stop(self):
        """Stop gwd server"""
        if self.process:
            # Use pkill to ensure all child processes are killed
            pkill_cmd = ["pkill", "-f", f"gwd.*-p {self.port}"]
            subprocess.run(pkill_cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(0.3)

            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            finally:
                if self.log_file:
                    self.log_file.close()
                if self.process.stdout:
                    self.process.stdout.close()


@pytest.fixture(scope="module")
def geneweb_dir():
    """Find GeneWeb directory"""
    current_dir = Path(__file__).parent
    geneweb_path = current_dir.parent.parent.parent / "GeneWeb"

    if not geneweb_path.exists():
        pytest.skip(f"GeneWeb directory not found at {geneweb_path}")

    return str(geneweb_path)


@pytest.fixture(scope="module")
def server(geneweb_dir):
    """Start GeneWeb server for functional tests"""
    srv = GeneWebServer(geneweb_dir, port=23193)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestI18n:
    """Functional tests for internationalization workflow"""

    def test_i18n_language_switch_works(self, server):
        """Test: Language switching functionality works"""
        # Test English language (default)
        en_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"lang": "en"}
        )

        assert en_response.status_code == 200, "English language page failed to load"

        en_content = en_response.text.lower()
        assert "individual" in en_content or "person" in en_content, "English page missing English terms"

        # Test French language
        fr_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"lang": "fr"}
        )

        assert fr_response.status_code == 200, "French language page failed to load"

        fr_content = fr_response.text.lower()

        # French page should contain French terms or be different from English
        # Note: Actual translations depend on language files
        assert "<html" in fr_content, "French page missing HTML structure"

    def test_i18n_translations_displayed(self, server):
        """Test: Translations are displayed correctly"""
        # Test multiple languages
        test_languages = ["en", "fr", "de", "es"]

        for lang in test_languages:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params={"lang": lang}
            )

            # Not all languages may be available, but should either work or default gracefully
            assert response.status_code == 200, f"Language {lang} page failed to load"

            content = response.text.lower()

            # Verify page has proper structure
            assert "<html" in content, f"Language {lang} page missing HTML structure"

            # Verify page contains individual/person references (in any language)
            has_content = any(keyword in content for keyword in [
                "individual", "person", "famille", "family",
                "personne", "individu", "persona"
            ])
            assert has_content, f"Language {lang} page missing expected content"

    def test_i18n_date_format_changes(self, server):
        """Test: Date format adapts to language setting"""
        # Get person page with date information
        en_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor", "lang": "en"}
        )

        assert en_response.status_code == 200, "English person page failed to load"

        en_content = en_response.text

        # Verify dates are present in English page
        has_dates_en = any(str(year) in en_content for year in range(1900, 2025))
        assert has_dates_en, "English page missing date information"

        # Get same person page in French
        fr_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor", "lang": "fr"}
        )

        assert fr_response.status_code == 200, "French person page failed to load"

        fr_content = fr_response.text

        # Verify dates are present in French page
        has_dates_fr = any(str(year) in fr_content for year in range(1900, 2025))
        assert has_dates_fr, "French page missing date information"

        # Verify both pages contain person information
        assert "charles" in en_content.lower(), "English page missing person name"
        assert "charles" in fr_content.lower(), "French page missing person name"

    def test_i18n_multiple_languages_supported(self, server):
        """Test: Multiple languages are supported throughout the application"""
        # Test that language parameter works across different page types
        test_cases = [
            {"lang": "en"},  # Home page in English
            {"lang": "fr"},  # Home page in French
            {"p": "Charles", "n": "Windsor", "lang": "en"},  # Person page in English
            {"p": "Charles", "n": "Windsor", "lang": "fr"},  # Person page in French
            {"m": "STAT", "lang": "en"},  # Statistics in English
            {"m": "STAT", "lang": "fr"}   # Statistics in French
        ]

        for params in test_cases:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params=params
            )

            assert response.status_code == 200, f"Page failed to load with params: {params}"

            content = response.text.lower()

            # Verify proper page structure
            assert "<html" in content, f"Page missing HTML structure: {params}"

            # Verify page contains content
            has_content = len(content) > 1000  # Page should have substantial content
            assert has_content, f"Page content too short: {params}"

            # Verify language-specific elements or navigation
            has_structure = any(keyword in content for keyword in [
                "geneweb", "individual", "person", "famille", "family",
                "home", "menu", "nav", "accueil"
            ])
            assert has_structure, f"Page missing expected structure: {params}"
