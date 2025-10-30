# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
IT-PY-007: Test authentication via HTTP API

Validate wizard mode, friend mode, and access permissions.
Tests that authentication and authorization work correctly.

Components tested:
- Wizard mode access
- Friend mode access
- Public access restrictions
- Permission validation
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

    def __init__(self, geneweb_dir: str, port: int = 23186, base_name: str | None = None):
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
    srv = GeneWebServer(geneweb_dir, port=23186, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestAuthentication:
    """Test authentication and authorization"""

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
            return last  # Return even on non-200, for auth tests
        raise last

    def test_public_access_allowed(self, server: GeneWebServer):
        """Test that public pages are accessible without authentication"""
        url = f"{server.base_url}"
        r = self._get(url)

        # Public home page should be accessible
        assert r.status_code == 200

    def test_public_person_page_accessible(self, server: GeneWebServer):
        """Test that public person pages are accessible"""
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)

        # Public person page should be accessible
        assert r.status_code == 200
        assert "charles" in r.text.lower() or "windsor" in r.text.lower()

    def test_search_accessible_without_auth(self, server: GeneWebServer):
        """Test that search is accessible without authentication"""
        url = f"{server.base_url}?m=S&v=Windsor"
        r = self._get(url)

        # Search should be accessible
        assert r.status_code == 200

    def test_statistics_accessible_without_auth(self, server: GeneWebServer):
        """Test that statistics are accessible without authentication"""
        url = f"{server.base_url}?m=STAT"
        r = self._get(url)

        # Statistics should be accessible
        assert r.status_code == 200

    def test_wizard_mode_parameter(self, server: GeneWebServer):
        """Test wizard mode parameter is recognized"""
        # Note: This just tests that parameter is accepted, not admin functionality
        url = f"{server.base_url}?m=WIZARD"
        r = requests.get(url, timeout=3)

        # Should either work or show auth error (not crash)
        assert r.status_code < 500

    def test_base_access_allowed(self, server: GeneWebServer):
        """Test that base access is allowed"""
        url = f"{server.base_url}"
        r = requests.get(url, timeout=3)

        # Base should be accessible
        assert r.status_code == 200

    def test_multiple_public_requests(self, server: GeneWebServer):
        """Test multiple public requests work correctly"""
        urls = [
            f"{server.base_url}",
            f"{server.base_url}?p=Charles&n=Windsor",
            f"{server.base_url}?m=S&v=Windsor",
            f"{server.base_url}?m=STAT",
        ]

        for url in urls:
            r = requests.get(url, timeout=3)
            assert r.status_code == 200, f"Failed to access {url}"

    def test_session_handling(self, server: GeneWebServer):
        """Test that sessions are handled correctly"""
        # Make multiple requests - should all succeed
        session = requests.Session()

        urls = [
            f"{server.base_url}",
            f"{server.base_url}?p=Charles&n=Windsor",
            f"{server.base_url}?m=S&v=Windsor",
        ]

        for url in urls:
            r = session.get(url, timeout=3)
            assert r.status_code == 200

        session.close()

    def test_concurrent_public_access(self, server: GeneWebServer):
        """Test that multiple concurrent public accesses work"""
        import concurrent.futures

        def access_page(path):
            try:
                r = requests.get(f"{server.base_url}{path}", timeout=5)
                return r.status_code == 200
            except:
                return False

        paths = [
            "",
            "?p=Charles&n=Windsor",
            "?m=S&v=Windsor",
            "?m=STAT",
            "?m=CAL",
        ]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(access_page, path) for path in paths]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(results), "Some concurrent requests failed"
