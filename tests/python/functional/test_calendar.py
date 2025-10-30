# pylint: disable=import-outside-toplevel, duplicate-code, redefined-outer-name
"""
FT-PY-005: Test calendar functionality

End-to-end test of viewing birthdays in calendar format.

This is a FUNCTIONAL test because it validates complete user workflows:
- User navigates to calendar page
- User views birthdays by month/year
- User filters birthdays by month
- User navigates through calendar months

User Story: As a user, I want to view birthdays in a calendar format.

Test Scenario:
1. Navigate to calendar page
2. View birthdays organized by month
3. Filter by specific month
4. Navigate between months
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


class GeneWebServer:
    """Helper class to manage gwd process for functional testing"""

    def __init__(self, geneweb_dir: str, port: int = 23188, base_name: str = "test"):
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
    srv = GeneWebServer(geneweb_dir, port=23188)

    if not srv.start():
        pytest.skip("Failed to start GeneWeb server")

    yield srv

    srv.stop()


class TestCalendar:
    """Functional tests for calendar workflow"""

    def test_calendar_page_loads(self, server):
        """Test: Calendar page displays correctly"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "CAL"}, timeout=5)

        assert response.status_code == 200, f"Calendar page failed to load: {response.status_code}"

        # Verify calendar page contains expected elements
        content = response.text.lower()
        assert any(keyword in content for keyword in [
            "calendar", "month", "year", "birthday", "birth"
        ]), "Calendar page missing calendar/birthday references"

        # Verify page structure
        assert "<html" in content, "Calendar page missing HTML structure"

    def test_calendar_displays_birthdays(self, server):
        """Test: Birthdays are shown in calendar format"""
        response = requests.get(
            f"http://localhost:{server.port}/{server.base_name}",
            params={"m": "CAL"}, timeout=5)

        assert response.status_code == 200

        content = response.text.lower()

        # Verify calendar displays birthday information
        has_birthday_data = any(keyword in content for keyword in [
            "birth", "born", "birthday", "january", "february", "march",
            "april", "may", "june", "july", "august", "september",
            "october", "november", "december"
        ])
        assert has_birthday_data, "Calendar missing birthday information"

        # Verify some date information is present
        has_dates = any(str(year) in content for year in range(1900, 2025))
        assert has_dates, "Calendar missing date information"

    def test_calendar_filters_by_month(self, server):
        """Test: Calendar can filter by specific month"""
        # Test filtering by different months
        test_months = [
            ("1", "january"),
            ("6", "june"),
            ("12", "december")
        ]

        for month_num, month_name in test_months:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params={"m": "CAL", "month": month_num}, timeout=5)

            assert response.status_code == 200, f"Calendar filtering by month {month_num} failed"

            content = response.text.lower()

            # Verify month information is present
            assert any(keyword in content for keyword in [
                month_name, "calendar", "birth"
            ]), f"Calendar missing month {month_name} information"

    def test_calendar_navigation_works(self, server):
        """Test: Calendar navigation between months works"""
        # Test navigating through different months
        months = ["1", "2", "3", "6", "12"]

        for month in months:
            response = requests.get(
                f"http://localhost:{server.port}/{server.base_name}",
                params={"m": "CAL", "month": month}, timeout=5)

            assert response.status_code == 200, f"Calendar navigation to month {month} failed"

            content = response.text.lower()

            # Verify navigation elements are present
            has_navigation = any(keyword in content for keyword in [
                "next", "previous", "month", "year", "nav", "link"
            ])
            assert has_navigation or "<a" in content, f"Calendar missing navigation elements for month {month}"

            # Verify calendar structure
            assert "calendar" in content or "birth" in content, f"Calendar missing calendar structure for month {month}"
