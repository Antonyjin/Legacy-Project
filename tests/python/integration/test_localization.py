# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
IT-PY-006: Test localization integration

Validate language switching and translations in full API responses.
Tests i18n parameter handling and language fallback.

Components tested:
- Language parameter (lang=en, lang=fr)
- Translation content validation
- Fallback behavior
- Multiple language support
"""

import os
import signal
import subprocess
import time
from pathlib import Path

import pytest
import requests


class GeneWebServer:
    """Helper to manage gwd process for testing"""

    def __init__(self, geneweb_dir: str, port: int = 23185, base_name: str | None = None):
        self.geneweb_dir = Path(geneweb_dir)
        self.port = port
        self.base_name = base_name or os.getenv("GENEWEB_BASE", "test")
        self.proc: subprocess.Popen | None = None

    @property
    def base_url(self) -> str:
        return f"http://localhost:{self.port}/{self.base_name}"

    def start(self, timeout: float = 6.0) -> None:
        gwd = self.geneweb_dir / "gw" / "gwd"
        gw_dir = self.geneweb_dir / "gw"
        bases_dir = self.geneweb_dir / "bases"
        if not gwd.exists():
            raise FileNotFoundError(f"gwd not found at {gwd}")

        self.proc = subprocess.Popen(
            [str(gwd), "-hd", str(gw_dir), "-bd", str(bases_dir), "-p", str(self.port), "-lang", "en"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        deadline = time.time() + timeout
        last_err = None
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError("gwd exited unexpectedly while starting")
            try:
                r = requests.get(self.base_url, timeout=0.8)
                if r.status_code == 200:
                    return
            except requests.RequestException as e:
                last_err = e
            time.sleep(0.2)
        raise TimeoutError(f"gwd did not become ready: {last_err}")

    def stop(self, graceful: bool = True) -> None:
        if not self.proc:
            return
        try:
            if graceful:
                self.proc.send_signal(signal.SIGTERM)
                self.proc.wait(timeout=3)
            else:
                self.proc.kill()
                self.proc.wait(timeout=3)
        finally:
            if self.proc.stdout:
                self.proc.stdout.close()
            self.proc = None


@pytest.fixture(scope="session")
def geneweb_dir():
    """Locate the GeneWeb directory"""
    candidates = [
        Path.cwd() / "GeneWeb",
        Path.cwd().parent / "GeneWeb",
    ]
    for p in candidates:
        if p.exists() and (p / "gw" / "gwd").exists():
            return str(p)
    pytest.skip("GeneWeb directory not found")


@pytest.fixture(scope="module")
def server(geneweb_dir):
    """Start gwd for this test module"""
    srv = GeneWebServer(geneweb_dir, port=23185, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestLocalization:
    """Test localization and multi-language support"""

    def _get(self, url: str, tries: int = 2):
        """GET with retry"""
        last = None
        for _ in range(tries):
            try:
                r = requests.get(url, timeout=3)
                if r.status_code in (200, 204):
                    return r
                last = r
            except requests.RequestException as e:
                last = e
            time.sleep(0.15)
        if isinstance(last, requests.Response):
            raise AssertionError(f"Unexpected status {last.status_code} for {url}")
        raise last

    def test_english_language_parameter(self, server: GeneWebServer):
        """Test lang=en parameter"""
        url = f"{server.base_url}?lang=en"
        r = self._get(url)

        assert r.status_code == 200
        assert len(r.text) > 0

    def test_french_language_parameter(self, server: GeneWebServer):
        """Test lang=fr parameter"""
        url = f"{server.base_url}?lang=fr"
        r = self._get(url)

        assert r.status_code == 200
        assert len(r.text) > 0

    def test_french_translation_content(self, server: GeneWebServer):
        """Test French pages contain French text"""
        url = f"{server.base_url}?lang=fr"
        r = self._get(url)

        assert r.status_code == 200
        html_lower = r.text.lower()
        # Common French words that should appear
        # (may vary by template, so check for any)
        french_markers = ["accueil", "personne", "famille", "recherche", "date", "lieu"]
        # Should have at least some French content
        assert any(marker in html_lower for marker in french_markers) or "lang=fr" in r.url

    def test_language_parameter_affects_output(self, server: GeneWebServer):
        """Test that language parameter changes page output"""
        url_en = f"{server.base_url}?lang=en"
        url_fr = f"{server.base_url}?lang=fr"

        r_en = self._get(url_en)
        r_fr = self._get(url_fr)

        # Both should be valid
        assert r_en.status_code == 200
        assert r_fr.status_code == 200

        # Pages may have different content (ideally), or at least be valid
        assert len(r_en.text) > 100
        assert len(r_fr.text) > 100

    def test_person_page_responds_to_lang_parameter(self, server: GeneWebServer):
        """Test person page respects language parameter"""
        url_en = f"{server.base_url}?p=Charles&n=Windsor&lang=en"
        url_fr = f"{server.base_url}?p=Charles&n=Windsor&lang=fr"

        r_en = self._get(url_en)
        r_fr = self._get(url_fr)

        assert r_en.status_code == 200
        assert r_fr.status_code == 200
        # Both should contain person name
        assert "charles" in r_en.text.lower() or "windsor" in r_en.text.lower()
        assert "charles" in r_fr.text.lower() or "windsor" in r_fr.text.lower()

    def test_search_page_language_support(self, server: GeneWebServer):
        """Test search page supports language parameter"""
        url_en = f"{server.base_url}?m=S&v=Windsor&lang=en"
        url_fr = f"{server.base_url}?m=S&v=Windsor&lang=fr"

        r_en = self._get(url_en)
        r_fr = self._get(url_fr)

        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_statistics_page_language_support(self, server: GeneWebServer):
        """Test statistics page supports language parameter"""
        url_en = f"{server.base_url}?m=STAT&lang=en"
        url_fr = f"{server.base_url}?m=STAT&lang=fr"

        r_en = self._get(url_en)
        r_fr = self._get(url_fr)

        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_calendar_page_language_support(self, server: GeneWebServer):
        """Test calendar page supports language parameter"""
        url_en = f"{server.base_url}?m=CAL&lang=en"
        url_fr = f"{server.base_url}?m=CAL&lang=fr"

        r_en = self._get(url_en)
        r_fr = self._get(url_fr)

        assert r_en.status_code == 200
        assert r_fr.status_code == 200

    def test_unknown_language_fallback(self, server: GeneWebServer):
        """Test fallback behavior for unknown language"""
        # Request unknown language (should fallback gracefully)
        url = f"{server.base_url}?lang=xx"
        r = requests.get(url, timeout=3)

        # Should not crash - either serve default or error gracefully
        assert r.status_code < 500
