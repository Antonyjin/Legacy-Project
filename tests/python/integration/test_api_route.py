"""
IT-PY-002: Test API routes via HTTP

Validate the main GeneWeb API routes return expected responses.
This test suite assumes:
- gwd is available in GeneWeb/gw/gwd
- a base exists (default "test"), same as IT-PY-001
"""

import os
import time
import signal
import pytest
import requests
import subprocess
from pathlib import Path


# ---------------------------
# Helpers (kept local so file is standalone)
# ---------------------------

class GeneWebServer:
    """Minimal helper to boot/shutdown gwd for the tests."""

    def __init__(self, geneweb_dir: str, port: int = 23180, base_name: str | None = None):
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

        # Wait until HTTP responds 200 on /<base>
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


# ---------------------------
# Pytest fixtures
# ---------------------------

@pytest.fixture(scope="session")
def geneweb_dir():
    """Locate the GeneWeb directory (same heuristic as IT-PY-001)."""
    candidates = [
        Path.cwd() / "GeneWeb",
        Path.cwd().parent / "GeneWeb",
    ]
    for p in candidates:
        if p.exists() and (p / "gw" / "gwd").exists():
            return str(p)
    pytest.skip("GeneWeb directory not found (expected ./GeneWeb or ../GeneWeb)")

@pytest.fixture(scope="module")
def server(geneweb_dir):
    """Start one gwd for this test module."""
    srv = GeneWebServer(geneweb_dir, port=23180, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


# ---------------------------
# Tests
# ---------------------------

@pytest.mark.integration
@pytest.mark.requires_gwd
class TestApiRoutes:

    def _get(self, url: str, tries: int = 2):
        """GET with small retry to smooth out flaky first-hit latencies."""
        last = None
        for _ in range(tries):
            try:
                r = requests.get(url, timeout=3)
                # Followed redirects already by default; ensure final is OK-ish.
                if r.status_code in (200, 204):
                    return r
                last = r
            except requests.RequestException as e:
                last = e
            time.sleep(0.15)
        if isinstance(last, requests.Response):
            raise AssertionError(f"Unexpected status {last.status_code} for {url}")
        raise last  # type: ignore[misc]

    def test_home_page(self, server: GeneWebServer):
        """Home page (/) should load HTML."""
        r = self._get(server.base_url)
        assert r.status_code == 200
        assert "<html" in r.text.lower()

    def test_person_page(self, server: GeneWebServer):
        """Person page (?p=&n=). Uses known sample person from IT-PY-001."""
        url = f"{server.base_url}?p=Charles&n=Windsor"
        r = self._get(url)
        assert r.status_code == 200
        # Be tolerant to template/locale changes: check either token appears
        assert ("charles" in r.text.lower()) or ("windsor" in r.text.lower())

    def test_family_page(self, server: GeneWebServer):
        """
        Family page (?m=F).
        GeneWeb supports family-oriented views by surname; use Windsor as a stable sample.
        """
        url = f"{server.base_url}?m=F&v=Windsor"
        r = self._get(url)
        assert r.status_code == 200
        assert "<html" in r.text.lower()

    def test_search_page(self, server: GeneWebServer):
        """Search page (?m=S)."""
        # GeneWeb search typically accepts 'v' (value) or 's' (string); keep both for robustness.
        url = f"{server.base_url}?m=S&v=Charles"
        r = self._get(url)
        assert r.status_code == 200
        assert "<html" in r.text.lower()

    def test_calendar_page(self, server: GeneWebServer):
        """Calendar page (?m=CAL)."""
        url = f"{server.base_url}?m=CAL"
        r = self._get(url)
        assert r.status_code == 200
        assert "<html" in r.text.lower()

    def test_statistics_page(self, server: GeneWebServer):
        """Statistics page (?m=STAT)."""
        url = f"{server.base_url}?m=STAT"
        r = self._get(url)
        assert r.status_code == 200
        assert "<html" in r.text.lower()

    @pytest.mark.parametrize(
        "mode,params",
        [
            ("A", "p=Charles&n=Windsor"),   # Ancestors
            ("D", "p=Charles&n=Windsor"),   # Descendants
        ],
    )
    def test_tree_pages(self, server: GeneWebServer, mode: str, params: str):
        """Tree pages (?m=A and ?m=D)."""
        url = f"{server.base_url}?m={mode}&{params}"
        r = self._get(url)
        assert r.status_code == 200
        assert "<html" in r.text.lower()

    def test_unknown_query_is_handled(self, server: GeneWebServer):
        """
        Defensive check: unknown query should not crash gwd.
        Accept 200 with error page or 4xx, but not 5xx.
        """
        url = f"{server.base_url}?m=UNKNOWN_MODE"
        r = requests.get(url, timeout=3)
        assert r.status_code < 500, f"Server error {r.status_code} on unknown mode"
