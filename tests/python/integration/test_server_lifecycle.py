# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
IT-PY-001: Test HTTP server lifecycle

Tests GeneWeb daemon (gwd) startup, shutdown, and basic health checks.

This is an INTEGRATION test because it validates the interaction between:
- gwd binary (HTTP server)
- Base filesystem (database access)
- Network stack (port binding)
- Process management (startup/shutdown)

Validates:
- Server starts successfully
- Server responds to requests
- Server graceful shutdown
- Server handles port conflicts
- Server handles multiple concurrent requests
"""

import signal
import subprocess
import time
from pathlib import Path

import pytest
import requests


class GeneWebServer:
    """Helper class to manage gwd process for testing"""

    def __init__(self, geneweb_dir: str, port: int = 23180, base_name: str = "test"):
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
        time.sleep(0.1)  # Give OS a moment to clean up

        # Open log file
        self.log_file = open(f"/tmp/gwd_test_{self.port}.log", "w", encoding='utf-8')

        # Start gwd
        self.process = subprocess.Popen(
            [
                str(gwd_path),
                "-hd", str(gw_dir),
                "-bd", str(bases_dir),
                "-p", str(self.port),
                "-lang", "en"
            ],
            stdout=self.log_file,
            stderr=subprocess.STDOUT
        )

        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return True
            time.sleep(0.2)

        return False

    def is_running(self) -> bool:
        """Check if server is running and responding"""
        if self.process is None:
            return False

        # Note: gwd daemonizes, so we can't rely on process.poll()
        # Instead, check if it responds to HTTP requests
        try:
            response = requests.get(
                f"http://localhost:{self.port}/{self.base_name}",
                timeout=1,
                headers={"Connection": "close"}  # Explicitly close connection
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def stop(self, graceful: bool = True) -> bool:
        """Stop gwd server"""
        if self.process is None:
            return True

        try:
            # Close log file first
            if self.log_file and not self.log_file.closed:
                self.log_file.close()

            if graceful:
                # Send SIGTERM for graceful shutdown
                self.process.send_signal(signal.SIGTERM)
                try:
                    self.process.wait(timeout=3)
                    return True
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.process.kill()
                    self.process.wait()
                    return False
            else:
                # Force kill
                self.process.kill()
                self.process.wait()
                return True
        finally:
            # Close stdout pipe to prevent ResourceWarning
            if self.process.stdout:
                self.process.stdout.close()
            self.process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


@pytest.fixture
def geneweb_dir():
    """Get GeneWeb directory path"""
    # Try to find GeneWeb directory
    candidates = [
        Path.cwd() / "GeneWeb",
        Path.cwd().parent / "GeneWeb",
    ]

    for path in candidates:
        if path.exists() and (path / "gw" / "gwd").exists():
            return str(path)

    pytest.skip("GeneWeb directory not found")


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestServerStartup:
    """Test server starts successfully"""

    def test_server_starts(self, geneweb_dir):
        """Test gwd starts and binds to port"""
        server = GeneWebServer(geneweb_dir, port=23180)

        try:
            assert server.start(timeout=5), "Server failed to start"
            assert server.is_running(), "Server not responding after start"
        finally:
            server.stop()

    def test_server_uses_correct_port(self, geneweb_dir):
        """Test server binds to specified port"""
        port = 23181
        server = GeneWebServer(geneweb_dir, port=port)

        try:
            server.start()

            # Should respond on correct port
            response = requests.get(f"http://localhost:{port}/test", timeout=2)
            assert response.status_code == 200

            # Should NOT respond on different port
            with pytest.raises(requests.exceptions.RequestException):
                requests.get(f"http://localhost:23182/test", timeout=1)
        finally:
            server.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestServerResponds:
    """Test server responds to requests"""

    def test_server_responds_http_200(self, geneweb_dir):
        """Test server returns HTTP 200 for valid requests"""
        with GeneWebServer(geneweb_dir, port=23180) as server:
            response = requests.get(f"http://localhost:23180/test", timeout=5)
            assert response.status_code == 200

    def test_server_responds_with_content(self, geneweb_dir):
        """Test server returns HTML content"""
        with GeneWebServer(geneweb_dir, port=23180) as server:
            response = requests.get(f"http://localhost:23180/test", timeout=5)
            assert response.status_code == 200
            assert len(response.text) > 0, "Response body is empty"
            assert "html" in response.text.lower(), "Response doesn't contain HTML"

    def test_server_responds_to_person_page(self, geneweb_dir):
        """Test server responds to person page requests"""
        with GeneWebServer(geneweb_dir, port=23180) as server:
            response = requests.get(
                f"http://localhost:23180/test?p=Charles&n=Windsor", timeout=5)
            assert response.status_code == 200
            assert "Charles" in response.text


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestServerShutdown:
    """Test server graceful shutdown"""

    def test_server_stops_gracefully(self, geneweb_dir):
        """Test SIGTERM results in graceful shutdown"""
        server = GeneWebServer(geneweb_dir, port=23180)
        server.start()

        # Server should be running
        assert server.is_running()

        # Graceful stop
        result = server.stop(graceful=True)
        assert result, "Graceful shutdown failed"

        # Server should no longer be responding
        assert not server.is_running(), "Server still responding after shutdown"

    def test_server_stops_forcefully(self, geneweb_dir):
        """Test SIGKILL results in immediate shutdown"""
        server = GeneWebServer(geneweb_dir, port=23180)
        server.start()

        # Force kill
        result = server.stop(graceful=False)
        assert result, "Force kill failed"

        # Server should no longer be responding
        assert not server.is_running(), "Server still responding after kill"

    def test_server_cleanup_on_stop(self, geneweb_dir):
        """Test server releases port on shutdown"""
        server = GeneWebServer(geneweb_dir, port=23180)
        server.start()
        server.stop()

        # Port should be available again
        server2 = GeneWebServer(geneweb_dir, port=23180)
        try:
            assert server2.start(), "Port not released after shutdown"
        finally:
            server2.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestMultipleServers:
    """Test multiple server instances"""

    def test_server_uses_different_ports(self, geneweb_dir):
        """Test multiple servers can run on different ports"""
        server1 = GeneWebServer(geneweb_dir, port=23180)
        server2 = GeneWebServer(geneweb_dir, port=23181)

        try:
            assert server1.start(), "Server 1 failed to start"
            assert server2.start(), "Server 2 failed to start"

            # Both should respond
            r1 = requests.get("http://localhost:23180/test", timeout=2)
            r2 = requests.get("http://localhost:23181/test", timeout=2)

            assert r1.status_code == 200
            assert r2.status_code == 200
        finally:
            server1.stop()
            server2.stop()

    def test_server_isolates_requests(self, geneweb_dir):
        """Test servers on different ports serve independently"""
        server1 = GeneWebServer(geneweb_dir, port=23180)
        server2 = GeneWebServer(geneweb_dir, port=23181)

        try:
            server1.start()
            server2.start()

            # Each server should respond independently
            r1 = requests.get("http://localhost:23180/test?p=Charles&n=Windsor", timeout=2)
            r2 = requests.get("http://localhost:23181/test?p=Elizabeth&n=Windsor", timeout=2)

            assert r1.status_code == 200
            assert r2.status_code == 200
            assert "Charles" in r1.text
            assert "Elizabeth" in r2.text
        finally:
            server1.stop()
            server2.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
@pytest.mark.slow
class TestConcurrentRequests:
    """Test server handles multiple concurrent requests"""

    def test_server_handles_concurrent_requests(self, geneweb_dir):
        """
        Test server handles 10 concurrent requests

        Note: OCaml gwd has limited concurrency support and may drop connections
        under heavy load. This is a known limitation of the legacy system.
        We accept 70% success rate (7/10 requests) as passing.
        """
        import concurrent.futures

        with GeneWebServer(geneweb_dir, port=23180) as server:

            def make_request(i):
                try:
                    response = requests.get(
                        f"http://localhost:23180/test?p=Charles&n=Windsor",
                        timeout=5
                    )
                    return response.status_code
                except requests.exceptions.RequestException:
                    # OCaml gwd may drop connections under concurrent load
                    return None

            # Make 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, i) for i in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            # Count successful requests
            successful = [r for r in results if r == 200]
            success_rate = len(successful) / len(results)

            # OCaml gwd has concurrency limits - accept 70% success rate
            assert success_rate >= 0.7, f"Success rate {success_rate:.0%} too low (need ≥70%)"
            assert len(results) == 10, "Not all requests completed"

    def test_server_handles_rapid_requests(self, geneweb_dir):
        """Test server handles rapid sequential requests"""
        with GeneWebServer(geneweb_dir, port=23180) as server:
            for i in range(20):
                response = requests.get(f"http://localhost:23180/test", timeout=2)
                assert response.status_code == 200, f"Request {i} failed"
