# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
IT-PY-009: Test performance benchmarks

Validate response times and system performance under load.
Tests page load times, search performance, and complex queries.

Components tested:
- Page load time benchmarks
- Search performance
- Complex queries performance
- Resource usage monitoring
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

    def __init__(self, geneweb_dir: str, port: int = 23188, base_name: str | None = None):
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
    srv = GeneWebServer(geneweb_dir, port=23188, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics"""

    def test_home_page_load_time(self, server: GeneWebServer):
        """Test home page loads within acceptable time"""
        start = time.time()
        r = requests.get(server.base_url, timeout=5)
        elapsed = time.time() - start

        assert r.status_code == 200
        # OCaml gwd is slow - accept 2 second threshold
        # Python version should be much faster
        assert elapsed < 2.0, f"Home page took {elapsed:.2f}s (expected <2s)"

    def test_person_page_load_time(self, server: GeneWebServer):
        """Test person page loads within acceptable time"""
        start = time.time()
        r = requests.get(f"{server.base_url}?p=Charles&n=Windsor", timeout=5)
        elapsed = time.time() - start

        assert r.status_code == 200
        assert elapsed < 2.0, f"Person page took {elapsed:.2f}s (expected <2s)"

    def test_search_page_load_time(self, server: GeneWebServer):
        """Test search page loads within acceptable time"""
        start = time.time()
        r = requests.get(f"{server.base_url}?m=S&v=Windsor", timeout=5)
        elapsed = time.time() - start

        assert r.status_code == 200
        assert elapsed < 3.0, f"Search page took {elapsed:.2f}s (expected <3s)"

    def test_statistics_page_load_time(self, server: GeneWebServer):
        """Test statistics page loads within acceptable time"""
        start = time.time()
        r = requests.get(f"{server.base_url}?m=STAT", timeout=5)
        elapsed = time.time() - start

        assert r.status_code == 200
        # Statistics might take longer to compute
        assert elapsed < 3.0, f"Statistics page took {elapsed:.2f}s (expected <3s)"

    def test_calendar_page_load_time(self, server: GeneWebServer):
        """Test calendar page loads within acceptable time"""
        start = time.time()
        r = requests.get(f"{server.base_url}?m=CAL", timeout=5)
        elapsed = time.time() - start

        assert r.status_code == 200
        assert elapsed < 2.0, f"Calendar page took {elapsed:.2f}s (expected <2s)"

    def test_repeated_requests_consistency(self, server: GeneWebServer):
        """Test repeated requests have consistent performance"""
        times = []

        for i in range(5):
            start = time.time()
            r = requests.get(server.base_url, timeout=5)
            elapsed = time.time() - start
            assert r.status_code == 200
            times.append(elapsed)

        # All requests should be reasonably fast
        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert avg_time < 2.0, f"Average time {avg_time:.2f}s is too high"
        assert max_time < 3.0, f"Max time {max_time:.2f}s is too high"

    def test_rapid_sequential_requests(self, server: GeneWebServer):
        """Test server handles rapid sequential requests efficiently"""
        start = time.time()

        for i in range(20):
            r = requests.get(server.base_url, timeout=5)
            assert r.status_code == 200

        total_time = time.time() - start
        avg_time_per_request = total_time / 20

        # Average should be reasonable
        assert avg_time_per_request < 2.0, f"Average {avg_time_per_request:.2f}s per request is too high"

    def test_concurrent_requests_performance(self, server: GeneWebServer):
        """Test performance under concurrent load"""
        import concurrent.futures

        def timed_request(url):
            start = time.time()
            r = requests.get(url, timeout=5)
            elapsed = time.time() - start
            return (r.status_code == 200, elapsed)

        urls = [
            f"{server.base_url}",
            f"{server.base_url}?p=Charles&n=Windsor",
            f"{server.base_url}?m=S&v=Windsor",
            f"{server.base_url}?m=STAT",
            f"{server.base_url}?m=CAL",
        ]

        # Repeat each URL 4 times
        all_urls = urls * 4

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(timed_request, url) for url in all_urls]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Check all succeeded
        successful = [r for r, _ in results if r]
        assert len(successful) >= len(results) * 0.7, "Less than 70% of concurrent requests succeeded"

        # Check times are reasonable
        times = [t for _, t in results if t is not None]
        if times:
            avg_time = sum(times) / len(times)
            # Concurrent requests might be slower, but not too much
            assert avg_time < 5.0, f"Average concurrent time {avg_time:.2f}s is too high"

    def test_response_size(self, server: GeneWebServer):
        """Test response sizes are reasonable"""
        r = requests.get(server.base_url, timeout=5)

        assert r.status_code == 200
        content_length = len(r.content)

        # HTML pages should be reasonable size
        assert content_length > 100, "Response too small"
        assert content_length < 10 * 1024 * 1024, "Response too large (>10MB)"  # 10MB limit

    def test_large_response_handling(self, server: GeneWebServer):
        """Test handling of larger responses (statistics page)"""
        start = time.time()
        r = requests.get(f"{server.base_url}?m=STAT", timeout=10)
        elapsed = time.time() - start

        assert r.status_code == 200
        content_length = len(r.content)

        # Should handle reasonably large responses
        assert content_length > 1000
        assert elapsed < 5.0

    @pytest.mark.parametrize("iterations", [10, 20])
    def test_sustained_load(self, server: GeneWebServer, iterations: int):
        """Test server handles sustained load"""
        start = time.time()
        failed = 0

        for i in range(iterations):
            try:
                r = requests.get(server.base_url, timeout=3)
                if r.status_code != 200:
                    failed += 1
            except requests.RequestException:
                failed += 1

        total_time = time.time() - start

        # Should complete in reasonable time
        assert total_time < iterations * 2.0, f"Sustained load test too slow"
        # Should not have too many failures
        assert failed < iterations * 0.2, f"Too many failures: {failed}/{iterations}"
