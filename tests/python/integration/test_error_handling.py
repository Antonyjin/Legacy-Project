# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
IT-PY-008: Test error handling via HTTP API

Validate graceful error handling for edge cases.
Tests that invalid requests don't crash the server.

Components tested:
- 404 errors (missing persons)
- Invalid parameters
- Malformed requests
- Error response formats
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

    def __init__(self, geneweb_dir: str, port: int = 23187, base_name: str | None = None):
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
    srv = GeneWebServer(geneweb_dir, port=23187, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestErrorHandling:
    """Test error handling for edge cases"""

    def test_missing_person_handled(self, server: GeneWebServer):
        """Test that missing person doesn't crash server"""
        url = f"{server.base_url}?p=NonexistentPerson&n=NotFound"
        r = requests.get(url, timeout=3)

        # Should not be 5xx (server error)
        assert r.status_code < 500
        # Response should be valid
        assert len(r.text) > 0

    def test_malformed_name_parameter(self, server: GeneWebServer):
        """Test malformed name parameter handling"""
        # Names with special characters
        url = f"{server.base_url}?p=Test<>&n=Bad"
        r = requests.get(url, timeout=3)

        # Should not crash
        assert r.status_code < 500

    def test_empty_parameters(self, server: GeneWebServer):
        """Test empty parameter values"""
        url = f"{server.base_url}?p=&n="
        r = requests.get(url, timeout=3)

        # Should not crash
        assert r.status_code < 500

    def test_invalid_query_parameter(self, server: GeneWebServer):
        """Test invalid query mode parameter"""
        url = f"{server.base_url}?m=INVALID_MODE"
        r = requests.get(url, timeout=3)

        # Should not crash - either error page or fallback
        assert r.status_code < 500

    def test_very_long_parameter(self, server: GeneWebServer):
        """Test very long parameter value"""
        long_name = "A" * 1000
        url = f"{server.base_url}?p={long_name}&n={long_name}"
        r = requests.get(url, timeout=3)

        # Should not crash
        assert r.status_code < 500

    def test_unicode_characters_in_name(self, server: GeneWebServer):
        """Test Unicode characters in name parameter"""
        url = f"{server.base_url}?p=Jöhn&n=Döe"
        r = requests.get(url, timeout=3)

        # Should not crash
        assert r.status_code < 500

    def test_sql_injection_attempt_harmless(self, server: GeneWebServer):
        """Test that SQL injection attempts don't crash server"""
        # GeneWeb uses its own format, but test defensive coding
        url = f"{server.base_url}?p=x'; DROP TABLE--&n=test"
        r = requests.get(url, timeout=3)

        # Should not crash (GeneWeb isn't SQL-based, but test robustness)
        assert r.status_code < 500

    def test_xss_attempt_harmless(self, server: GeneWebServer):
        """Test that XSS attempts don't crash server"""
        url = f"{server.base_url}?p=<script>alert('xss')</script>&n=test"
        r = requests.get(url, timeout=3)

        # Should not crash - ideally with escaped content
        assert r.status_code < 500

    def test_server_still_running_after_errors(self, server: GeneWebServer):
        """Test that server continues running after error requests"""
        # Make invalid request
        r1 = requests.get(f"{server.base_url}?m=INVALID", timeout=3)
        assert r1.status_code < 500

        # Server should still respond to valid request
        r2 = requests.get(f"{server.base_url}", timeout=3)
        assert r2.status_code == 200

    def test_rapid_invalid_requests(self, server: GeneWebServer):
        """Test server handles rapid invalid requests"""
        for i in range(10):
            url = f"{server.base_url}?p=invalid{i}&m=BADMODE"
            r = requests.get(url, timeout=3)
            # Should not crash
            assert r.status_code < 500

    def test_missing_required_base_name(self, server: GeneWebServer):
        """Test request to nonexistent base name"""
        # GeneWeb may serve error or default
        url = f"http://localhost:{server.port}/nonexistent_base"
        r = requests.get(url, timeout=3)

        # Should not crash (might 404 or redirect)
        assert r.status_code < 500

    def test_network_timeout_recovery(self, server: GeneWebServer):
        """Test server recovers after timeout-like conditions"""
        # Make normal request
        r1 = requests.get(f"{server.base_url}", timeout=3)
        assert r1.status_code == 200

        # Wait a bit
        time.sleep(0.5)

        # Make another normal request
        r2 = requests.get(f"{server.base_url}", timeout=3)
        assert r2.status_code == 200

    def test_concurrent_error_requests(self, server: GeneWebServer):
        """Test server handles concurrent error requests"""
        import concurrent.futures

        def make_bad_request(i):
            try:
                url = f"{server.base_url}?p=bad{i}&n=request{i}"
                r = requests.get(url, timeout=5)
                return r.status_code < 500
            except:
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_bad_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should handle gracefully
        assert all(results), "Some error requests crashed server"
