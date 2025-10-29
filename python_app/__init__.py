"""
GeneWeb Python Proxy Server

This package provides a Python Flask proxy server that can toggle between
OCaml and Python backend implementations for GeneWeb functionality.

Main modules:
- app: Flask application
- config: Configuration and backend toggle
- migrated: Imported utility functions from tests/python/utils/
- routes: HTTP route handlers
- ocaml_bridge: Subprocess calls to OCaml binaries

Issue: MIG-INF-001 (#225)
"""

__version__ = "0.1.0"

