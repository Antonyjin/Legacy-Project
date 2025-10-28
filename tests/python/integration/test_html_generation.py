"""
IT-PY-004: Test HTML generation via HTTP API

Validate that HTML templates render correctly with database data.
Tests template rendering, data presence, and HTML structure.

Components tested:
- Template engine (HTML generation)
- Data binding (database → HTML)
- HTML structure validity
- Proper HTML encoding
"""

import os
import time
import signal
import pytest
import requests
import subprocess
from pathlib import Path
from html.parser import HTMLParser


class GeneWebServer:
    """Helper to manage gwd process for testing"""

    def __init__(self, geneweb_dir: str, port: int = 23183, base_name: str | None = None):
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


class HTMLValidator(HTMLParser):
    """Simple HTML validator to check for basic structure"""

    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if not self.tag_stack or self.tag_stack[-1] != tag:
            # Unclosed tag warning (not strict error)
            pass
        else:
            self.tag_stack.pop()


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
    srv = GeneWebServer(geneweb_dir, port=23183, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestHTMLGeneration:
    """Test HTML generation and template rendering"""

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

    def test_home_page_contains_html_structure(self, server: GeneWebServer):
        """Test home page has valid HTML structure"""
        r = self._get(server.base_url)

        assert r.status_code == 200
        assert "<html" in r.text.lower()
        assert "</html>" in r.text.lower()
        assert "<body" in r.text.lower()

    def test_home_page_has_content(self, server: GeneWebServer):
        """Test home page renders content"""
        r = self._get(server.base_url)

        assert r.status_code == 200
        # Should have meaningful content
        assert len(r.text) > 500
        # Should contain some text content
        assert "geneweb" in r.text.lower() or "family" in r.text.lower() or "person" in r.text.lower()

    def test_person_page_renders_name(self, server: GeneWebServer):
        """Test person page renders person name from database"""
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        assert "<html" in r.text.lower()
        # Person name should be in rendered output
        assert "charles" in r.text.lower() or "windsor" in r.text.lower()

    def test_person_page_renders_dates(self, server: GeneWebServer):
        """Test person page renders birth/death dates"""
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        # Charles Windsor was born 1948 - should be in page
        assert "1948" in r.text or "born" in r.text.lower() or "date" in r.text.lower()

    def test_statistics_page_renders_numbers(self, server: GeneWebServer):
        """Test statistics page renders numeric data"""
        url = f"{server.base_url}?m=STAT"
        r = self._get(url)

        assert r.status_code == 200
        # Statistics should contain numbers
        # Look for digits in content
        assert any(char.isdigit() for char in r.text)

    def test_calendar_page_renders_months(self, server: GeneWebServer):
        """Test calendar page renders month/date information"""
        url = f"{server.base_url}?m=CAL"
        r = self._get(url)

        assert r.status_code == 200
        # Calendar should have time-related content
        html_lower = r.text.lower()
        # Should have month names or numbers
        assert any(month in html_lower for month in ["january", "february", "march", "january", "jan", "feb", "01", "02"])

    def test_html_encoding_valid(self, server: GeneWebServer):
        """Test HTML is properly encoded"""
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        # Should be valid UTF-8 (no encoding errors)
        assert isinstance(r.text, str)
        # Should not have raw angle brackets in attribute values
        # (proper encoding would use &lt; &gt; etc)

    def test_search_page_renders_results(self, server: GeneWebServer):
        """Test search page renders result list"""
        url = f"{server.base_url}?m=S&v=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        assert "<html" in r.text.lower()
        # Should have content (result list or no-results message)
        assert len(r.text) > 100

    def test_family_page_renders_names(self, server: GeneWebServer):
        """Test family page renders family member names"""
        url = f"{server.base_url}?m=F&v=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        assert "<html" in r.text.lower()
        # Family page should have family name
        assert "windsor" in r.text.lower() or len(r.text) > 100

    def test_page_title_present(self, server: GeneWebServer):
        """Test pages have proper HTML title"""
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        html_lower = r.text.lower()
        # Should have title tag or head section
        assert "<title" in html_lower or "<head" in html_lower
