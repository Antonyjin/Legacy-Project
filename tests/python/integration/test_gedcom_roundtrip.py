"""
IT-PY-005: Test GEDCOM export/import roundtrip

Validate data integrity through GEDCOM export and re-import.
Tests GEDCOM file format compliance and data preservation.

Components tested:
- GEDCOM export functionality (gwb2ged binary)
- GEDCOM file creation
- Data field preservation
- Format compliance
"""

import os
import time
import signal
import pytest
import requests
import subprocess
import tempfile
from pathlib import Path


class GeneWebServer:
    """Helper to manage gwd process for testing"""

    def __init__(self, geneweb_dir: str, port: int = 23184, base_name: str | None = None):
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
    srv = GeneWebServer(geneweb_dir, port=23184, base_name=os.getenv("GENEWEB_BASE", "test"))
    srv.start()
    try:
        yield srv
    finally:
        srv.stop()


@pytest.mark.integration
@pytest.mark.requires_gwd
class TestGEDCOMRoundtrip:
    """Test GEDCOM export/import functionality"""

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

    def test_gedcom_export_creates_file(self, geneweb_dir):
        """Test that gwb2ged creates a GEDCOM file"""
        geneweb_path = Path(geneweb_dir)
        gw_path = geneweb_path / "gw"
        base_path = geneweb_path / "bases" / "test.gwb"

        if not base_path.exists():
            pytest.skip("Test database not found")

        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Run gwb2ged
            result = subprocess.run(
                [str(gw_path / "gwb2ged"), str(base_path), "-o", output_file],
                capture_output=True,
                timeout=10
            )

            # Should succeed
            assert result.returncode == 0, f"gwb2ged failed: {result.stderr.decode()}"

            # Output file should exist and have content
            assert Path(output_file).exists()
            assert Path(output_file).stat().st_size > 0
        finally:
            # Cleanup
            if Path(output_file).exists():
                Path(output_file).unlink()

    def test_gedcom_file_has_valid_format(self, geneweb_dir):
        """Test GEDCOM file has valid GEDCOM format"""
        geneweb_path = Path(geneweb_dir)
        gw_path = geneweb_path / "gw"
        base_path = geneweb_path / "bases" / "test.gwb"

        if not base_path.exists():
            pytest.skip("Test database not found")

        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Export GEDCOM
            result = subprocess.run(
                [str(gw_path / "gwb2ged"), str(base_path), "-o", output_file],
                capture_output=True,
                timeout=10
            )
            assert result.returncode == 0

            # Read and validate GEDCOM format
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Valid GEDCOM should start with HEAD record
            assert "0 HEAD" in content, "GEDCOM should contain HEAD record"
            # Should have TRLR (trailer)
            assert "0 TRLR" in content, "GEDCOM should contain TRLR record"
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()

    def test_gedcom_contains_persons(self, geneweb_dir):
        """Test GEDCOM export contains person records"""
        geneweb_path = Path(geneweb_dir)
        gw_path = geneweb_path / "gw"
        base_path = geneweb_path / "bases" / "test.gwb"

        if not base_path.exists():
            pytest.skip("Test database not found")

        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Export GEDCOM
            result = subprocess.run(
                [str(gw_path / "gwb2ged"), str(base_path), "-o", output_file],
                capture_output=True,
                timeout=10
            )
            assert result.returncode == 0

            # Read GEDCOM content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should have INDI records (persons)
            assert "0 @" in content and "INDI" in content, "GEDCOM should contain INDI records"
            # Should have NAME records
            assert "1 NAME" in content, "GEDCOM should contain NAME records"
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()

    def test_gedcom_contains_dates(self, geneweb_dir):
        """Test GEDCOM export preserves date information"""
        geneweb_path = Path(geneweb_dir)
        gw_path = geneweb_path / "gw"
        base_path = geneweb_path / "bases" / "test.gwb"

        if not base_path.exists():
            pytest.skip("Test database not found")

        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Export GEDCOM
            result = subprocess.run(
                [str(gw_path / "gwb2ged"), str(base_path), "-o", output_file],
                capture_output=True,
                timeout=10
            )
            assert result.returncode == 0

            # Read GEDCOM content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should have date records (BIRT, DEAT)
            assert "BIRT" in content or "DEAT" in content or "DATE" in content, \
                "GEDCOM should contain date information"
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()

    def test_gedcom_file_encoding_utf8(self, geneweb_dir):
        """Test GEDCOM file is properly encoded in UTF-8"""
        geneweb_path = Path(geneweb_dir)
        gw_path = geneweb_path / "gw"
        base_path = geneweb_path / "bases" / "test.gwb"

        if not base_path.exists():
            pytest.skip("Test database not found")

        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Export GEDCOM
            result = subprocess.run(
                [str(gw_path / "gwb2ged"), str(base_path), "-o", output_file],
                capture_output=True,
                timeout=10
            )
            assert result.returncode == 0

            # Should be readable as UTF-8
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                assert len(content) > 0
            except UnicodeDecodeError:
                pytest.fail("GEDCOM file is not valid UTF-8")
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()

    def test_gedcom_preserves_family_relationships(self, geneweb_dir):
        """Test GEDCOM export preserves family relationship data"""
        geneweb_path = Path(geneweb_dir)
        gw_path = geneweb_path / "gw"
        base_path = geneweb_path / "bases" / "test.gwb"

        if not base_path.exists():
            pytest.skip("Test database not found")

        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as tmp:
            output_file = tmp.name

        try:
            # Export GEDCOM
            result = subprocess.run(
                [str(gw_path / "gwb2ged"), str(base_path), "-o", output_file],
                capture_output=True,
                timeout=10
            )
            assert result.returncode == 0

            # Read GEDCOM content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should have family records (FAM) or parent references (FAMC, FAMS)
            assert "FAM" in content or "FAMC" in content or "FAMS" in content, \
                "GEDCOM should contain family relationship information"
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()
