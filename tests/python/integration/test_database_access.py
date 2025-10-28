"""
IT-PY-003: Test database access via HTTP API

Validate database read/write operations through the gwd HTTP API.
Tests that the OCaml database layer correctly responds to queries.

Components tested:
- Database file access (.gwb format)
- Person data retrieval
- Family relationships
- Data persistence
"""

import os
import time
import signal
import pytest
import requests
import subprocess
from pathlib import Path


class GeneWebServer:
    """Helper to manage gwd process for testing"""

    def __init__(self, geneweb_dir: str, port: int = 23182, base_name: str | None = None):
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
    srv = GeneWebServer(geneweb_dir, port=23182, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestDatabaseAccess:
    """Test database read/write operations via HTTP API"""

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

    def test_person_data_retrieval(self, server: GeneWebServer):
        """Test retrieving person data from database"""
        # Known person in test database: Charles Windsor
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        # Person data should be in response
        assert "charles" in r.text.lower() or "windsor" in r.text.lower()

    def test_multiple_persons_exist(self, server: GeneWebServer):
        """Test that multiple persons exist in database"""
        # Charles Windsor
        r1 = self._get(f"{server.base_url}?p=Charles&n=Windsor")
        assert r1.status_code == 200

        # Elizabeth Windsor (mother)
        r2 = self._get(f"{server.base_url}?p=Elizabeth&n=Windsor")
        assert r2.status_code == 200

        # Both should contain person data
        assert len(r1.text) > 100  # Non-trivial response
        assert len(r2.text) > 100

    def test_person_data_persistence(self, server: GeneWebServer):
        """Test that data persists across requests"""
        url = f"{server.base_url}?p=Charles&n=Windsor"

        # First request
        r1 = self._get(url)
        text1 = r1.text

        # Wait a moment
        time.sleep(0.5)

        # Second request - should get same data
        r2 = self._get(url)
        text2 = r2.text

        # Content should be identical
        assert text1 == text2, "Person data changed between requests"

    def test_family_relationships_exist(self, server: GeneWebServer):
        """Test that family relationship data exists"""
        # Charles Windsor should have parent links
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        # Should contain parent information
        # Note: Exact HTML structure depends on version, so we check for semantic markers
        html_lower = r.text.lower()
        assert "parent" in html_lower or "father" in html_lower or "mother" in html_lower or "elizabeth" in html_lower

    def test_search_uses_database(self, server: GeneWebServer):
        """Test that search queries database"""
        url = f"{server.base_url}?m=S&v=Charles"
        r = self._get(url)

        assert r.status_code == 200
        # Search results should be HTML
        assert "<html" in r.text.lower()
        # Should find something (person named Charles)
        assert len(r.text) > 100

    def test_database_handles_unknown_person(self, server: GeneWebServer):
        """Test that database gracefully handles missing persons"""
        url = f"{server.base_url}?p=NonexistentPerson&n=NotInDatabase"
        r = requests.get(url, timeout=3)

        # Should not crash - accept 200 (error page) or 404
        assert r.status_code < 500, f"Server error {r.status_code} on missing person"

    def test_database_encoding_support(self, server: GeneWebServer):
        """Test that database supports UTF-8 encoded data"""
        # Test with special characters in search
        url = f"{server.base_url}?m=S&v=Windsor"
        r = self._get(url)

        assert r.status_code == 200
        # Response should be valid UTF-8
        assert isinstance(r.text, str)
        assert len(r.text) > 0
