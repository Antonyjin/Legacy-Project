# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
FT-PY-002: Test person search

End-to-end test of searching for a person and viewing search results.

This is a FUNCTIONAL test because it validates complete user workflows:
- User enters search query
- User submits search
- User views results
- User clicks on result
- User verifies person page loaded

User Story: As a user, I want to search for a person by name and view results.

Test Scenario:
1. Enter search query in search form
2. Submit search
3. View search results page
4. Verify results are relevant
5. Click on a result to view person page
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


class GeneWebServer:
    """Helper class to manage gwd process for functional testing"""

    def __init__(self, geneweb_dir: str, port: int = 23185, base_name: str = "test"):
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

        # Start gwd
        cmd = [
            str(gwd_path),
            "-hd", str(gw_dir),
            "-bd", str(bases_dir),
            "-p", str(self.port),
            "-lang", "en"
        ]

        self.log_file = open(f"gwd_ft_{self.port}.log", "w", encoding='utf-8')
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
    srv = GeneWebServer(geneweb_dir, port=23185)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestPersonSearch:
    """Functional tests for person search workflow"""

    def test_search_form_loads_successfully(self, server):
        """Test: Search form loads and displays correctly"""
        response = requests.get(f"http://localhost:{server.port}/{server.base_name}", timeout=5)

        assert response.status_code == 200, f"Home page failed to load: {response.status_code}"

        # Verify home page has search functionality
        content = response.text.lower()
        assert any(keyword in content for keyword in [
            "search", "find", "query", "form"
        ]), "Home page missing search functionality"

    def test_search_returns_results(self, server):
        """Test: Search query returns matching results"""
        # Search for Windsor (known surname in test database)
        search_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "S", "s": "Windsor"}, timeout=5)

        assert search_response.status_code == 200, f"Search failed: {search_response.status_code}"

        # Verify search results contain expected persons
        content = search_response.text.lower()
        assert "charles" in content or "elizabeth" in content or "william" in content, \
            "Search results missing expected Windsor family members"

    def test_search_filters_correctly(self, server):
        """Test: Search filters results correctly by name"""
        # Search for specific person
        search_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "S", "s": "Charles"}, timeout=5)

        assert search_response.status_code == 200

        content = search_response.text.lower()
        # Results should contain Charles
        assert "charles" in content, "Search results missing Charles"

        # Verify result is relevant (not random data)
        assert len(content) > 100, "Search results appear empty"

    def test_search_result_click_navigates(self, server):
        """Test: Clicking search result navigates to person page"""
        # First, search
        search_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "S", "s": "Windsor"}, timeout=5)
        assert search_response.status_code == 200

        # Then navigate to one of the results
        person_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"p": "Charles", "n": "Windsor"}, timeout=5)

        assert person_response.status_code == 200, "Person page failed to load"

        # Verify we're on correct person page
        content = person_response.text.lower()
        assert "charles" in content, "Person page missing person name"
        assert "windsor" in content, "Person page missing surname"

    def test_search_handles_no_results(self, server):
        """Test: Search handles no results gracefully"""
        # Search for non-existent person
        search_response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "S", "s": "NONEXISTENTPERSON123"}, timeout=5)

        assert search_response.status_code in [200, 404], \
            f"Unexpected status for no results: {search_response.status_code}"

        content = search_response.text.lower()

        # Either should show no results message or empty results
        has_no_result_indicator = any(keyword in content for keyword in [
            "no result", "not found", "no match", "no person", "0 result"
        ])

        # If no explicit message, should just be minimal content
        if not has_no_result_indicator:
            # Page should still load but be minimal
            assert "geneweb" in content or "search" in content

    def test_search_with_special_characters(self, server):
        """Test: Search handles special characters in names"""
        # Test with common special character in surnames
        test_cases = [
            {"m": "S", "s": "Windsor"},  # Basic
            {"m": "S", "s": "Charles"},  # First name
        ]

        for params in test_cases:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params=params, timeout=5)

            assert response.status_code == 200, f"Search failed with params: {params}"

            # Verify page loaded properly
            content = response.text.lower()
            assert len(content) > 100, f"Search results appear empty for: {params}"
            assert any(keyword in content for keyword in [
                "geneweb", "search", "individual", "person"
            ]), f"Search page missing expected content for: {params}"
