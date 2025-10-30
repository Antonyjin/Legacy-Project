# pylint: disable=import-outside-toplevel, consider-using-with, line-too-long, unused-variable, unused-import, trailing-whitespace
"""
OCaml Bridge: Subprocess calls to OCaml binaries

This module handles calling OCaml binaries (gwd, gwb2ged, ged2gwb) via subprocess.
Used when:
- BACKEND=ocaml (proxy mode)
- BACKEND=python but need OCaml-only features (database access, GEDCOM operations)
"""

import subprocess  # nosec B404 - used with fixed args, no shell
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from python_app.config import Config


class OCamlBridge:
    """Bridge to OCaml GeneWeb binaries."""

    def __init__(self):
        self.config = Config
        self.gwd_process: Optional[subprocess.Popen] = None

    def start_gwd(self, port: Optional[int] = None) -> subprocess.Popen:
        """
        Start OCaml gwd daemon via subprocess.

        Args:
            port: Port to run gwd on (default: OCAML_GWD_PORT)

        Returns:
            subprocess.Popen instance

        Note: gwd daemonizes, so the parent process exits immediately.
        Use is_gwd_running() to check if it's actually responding.
        """
        port = port or self.config.OCAML_GWD_PORT

        # Kill any existing gwd on this port
        subprocess.run(  # nosec B603,B607 - fixed command, port is int-derived
            ["pkill", "-f", f"gwd.*-p {port}"],
            check=False,
            capture_output=True
        )
        time.sleep(0.5)

        # Start gwd
        cmd = [
            str(self.config.OCAML_GWD_PATH),
            "-hd", str(self.config.GW_DIR),
            "-bd", str(self.config.BASES_DIR),
            "-p", str(port),
            "-lang", self.config.DEFAULT_LANG,
        ]

        process = subprocess.Popen(  # nosec B603 - fixed arg list
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Wait a bit for daemonization
        time.sleep(1)

        # Check if gwd is responding via HTTP
        if not self.is_gwd_running(port):
            raise RuntimeError("gwd failed to start or respond")

        self.gwd_process = process
        return process

    def stop_gwd(self, port: Optional[int] = None) -> None:
        """
        Stop OCaml gwd daemon.

        Args:
            port: Port to stop gwd on (default: OCAML_GWD_PORT)
        """
        port = port or self.config.OCAML_GWD_PORT

        # Kill all gwd processes on this port
        subprocess.run(  # nosec B603,B607 - fixed command, port is int-derived
            ["pkill", "-f", f"gwd.*-p {port}"],
            check=False,
            capture_output=True
        )

        self.gwd_process = None
        time.sleep(0.3)

    def is_gwd_running(self, port: Optional[int] = None) -> bool:
        """
        Check if gwd is responding via HTTP.

        Args:
            port: Port to check (default: OCAML_GWD_PORT)

        Returns:
            True if gwd is responding, False otherwise
        """
        port = port or self.config.OCAML_GWD_PORT
        url = f"http://localhost:{port}/{self.config.BASE_NAME}"

        try:
            response = requests.get(url, timeout=1.0)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def export_gedcom(self, base_name: str, output_path: Path) -> None:
        """
        Export database to GEDCOM using OCaml gwb2ged.

        Args:
            base_name: Name of the base to export
            output_path: Path to write GEDCOM file

        Raises:
            subprocess.CalledProcessError: If export fails
        """
        cmd = [
            str(self.config.OCAML_GWB2GED_PATH),
            "-o", str(output_path),
            str(self.config.BASES_DIR / f"{base_name}.gwb"),
        ]

        subprocess.run(  # nosec B603 - fixed arg list
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

    def import_gedcom(self, gedcom_path: Path, base_name: str) -> None:
        """
        Import GEDCOM file using OCaml ged2gwb.

        Args:
            gedcom_path: Path to GEDCOM file
            base_name: Name of the base to create

        Raises:
            subprocess.CalledProcessError: If import fails
        """
        cmd = [
            str(self.config.OCAML_GED2GWB_PATH),
            "-o", str(self.config.BASES_DIR / f"{base_name}.gwb"),
            str(gedcom_path),
        ]

        subprocess.run(  # nosec B603 - fixed arg list
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

    def proxy_request(self, path: str, method: str = "GET", params: Optional[Dict[str, Any]] = None) -> str:
        """
        Proxy HTTP request to OCaml gwd.

        Args:
            path: URL path (e.g., "/test?p=Charles&n=Windsor")
            method: HTTP method (default: GET)
            params: Query parameters (optional)

        Returns:
            Response body as string

        Raises:
            requests.RequestException: If request fails
        """
        if not path.startswith("/"):
            path = "/" + path

        # Build URL
        url = f"http://localhost:{self.config.OCAML_GWD_PORT}{path}"

        if params:
            import urllib.parse
            url += "?" + urllib.parse.urlencode(params)

        response = requests.request(method, url, timeout=10.0)
        response.raise_for_status()

        return response.text
