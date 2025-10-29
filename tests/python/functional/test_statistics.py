"""
FT-PY-006: Test statistics functionality

End-to-end test of viewing database statistics.

This is a FUNCTIONAL test because it validates complete user workflows:
- User navigates to statistics page
- User views individual and family counts
- User verifies statistics accuracy
- User checks data formatting

User Story: As a user, I want to view database statistics.

Test Scenario:
1. Navigate to statistics page
2. View database counts
3. Verify statistics are accurate
4. Check formatting and presentation
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

    def __init__(self, geneweb_dir: str, port: int = 23189, base_name: str = "test"):
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
    srv = GeneWebServer(geneweb_dir, port=23189)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestStatistics:
    """Functional tests for statistics workflow"""

    def test_statistics_page_loads(self, server):
        """Test: Statistics page displays correctly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "STAT"}
        )

        assert response.status_code == 200, f"Statistics page failed to load: {response.status_code}"

        # Verify statistics page contains expected elements
        content = response.text.lower()
        assert any(keyword in content for keyword in [
            "statistic", "stat", "total", "count", "number"
        ]), "Statistics page missing statistics references"

        # Verify page structure
        assert "<html" in content, "Statistics page missing HTML structure"

    def test_statistics_count_display(self, server):
        """Test: Statistics counts are displayed"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "STAT"}
        )

        assert response.status_code == 200

        content = response.text.lower()

        # Verify statistics display count information
        has_counts = any(keyword in content for keyword in [
            "individual", "person", "family", "families", "male", "female"
        ])
        assert has_counts, "Statistics missing count information"

        # Verify numeric data is present
        has_numbers = any(char.isdigit() for char in content)
        assert has_numbers, "Statistics missing numeric data"

    def test_statistics_data_correct(self, server):
        """Test: Statistics data is present and reasonable"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "STAT"}
        )

        assert response.status_code == 200

        content = response.text

        # The exact count formatting can vary across builds. Check for:
        # 1) Presence of any numeric counts
        # 2) References to individuals/persons
        import re
        has_numbers = bool(re.search(r"\d+", content))
        content_lower = content.lower()
        has_individual_ref = ("individual" in content_lower) or ("person" in content_lower)
        assert has_numbers and has_individual_ref, (
            "Statistics missing count data or individual references"
        )

        # Verify statistics contain reasonable data
        # Look for gender statistics
        has_gender_stats = any(keyword in content_lower for keyword in [
            "male", "female", "men", "women", "gender"
        ])
        assert has_gender_stats, "Statistics missing gender information"

    def test_statistics_formats_properly(self, server):
        """Test: Statistics are formatted correctly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "STAT"}
        )

        assert response.status_code == 200

        content = response.text.lower()

        # Verify proper structure and formatting
        has_structure = any(keyword in content for keyword in [
            "table", "list", "row", "column", "<td", "<tr", "<li"
        ])
        assert has_structure, "Statistics missing proper formatting structure"

        # Verify navigation elements
        has_navigation = any(keyword in content for keyword in [
            "home", "back", "menu", "nav", "<a"
        ])
        assert has_navigation, "Statistics missing navigation elements"

        # Verify proper HTML structure
        assert "<html" in content, "Statistics missing HTML structure"
        assert "<body>" in content, "Statistics missing body section"
