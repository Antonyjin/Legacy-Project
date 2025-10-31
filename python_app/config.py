"""
Configuration for GeneWeb Python Proxy Server

Handles backend toggle (OCaml vs Python) and server configuration.
"""

import os
from enum import Enum
from pathlib import Path


class Backend(Enum):
    """Backend implementation selection."""
    OCAML = "ocaml"
    PYTHON = "python"


class Config:
    """Application configuration."""

    # Backend toggle: "ocaml" or "python" (default: ocaml)
    BACKEND = Backend(os.getenv("BACKEND", "ocaml").lower())

    # Flask configuration
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "2318"))  # Different from OCaml default 2317

    # GeneWeb configuration
    GENEWEB_DIR = Path(os.getenv("GENEWEB_DIR", "GeneWeb"))
    BASES_DIR = GENEWEB_DIR / "bases"
    GW_DIR = GENEWEB_DIR / "gw"

    # OCaml gwd configuration (when BACKEND=ocaml or for bridge calls)
    OCAML_GWD_HOST = os.getenv("OCAML_GWD_HOST", "127.0.0.1")
    OCAML_GWD_PORT = int(os.getenv("OCAML_GWD_PORT", "2317"))
    OCAML_GWSETUP_PORT = int(os.getenv("OCAML_GWSETUP_PORT", "2316"))
    OCAML_REMOTE = os.getenv("OCAML_REMOTE", "false").lower() == "true"
    OCAML_GWD_PATH = GW_DIR / "gwd"
    OCAML_GWB2GED_PATH = GW_DIR / "gwb2ged"
    OCAML_GED2GWB_PATH = GW_DIR / "ged2gwb"

    # Base name (default database)
    BASE_NAME = os.getenv("GENEWEB_BASE", "test")

    # Language
    DEFAULT_LANG = os.getenv("GENEWEB_LANG", "en")

    # Debug mode
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    @classmethod
    def is_python_backend(cls) -> bool:
        """Check if Python backend is enabled."""
        return cls.BACKEND == Backend.PYTHON

    @classmethod
    def is_ocaml_backend(cls) -> bool:
        """Check if OCaml backend is enabled."""
        return cls.BACKEND == Backend.OCAML

    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if cls.BACKEND not in [Backend.OCAML, Backend.PYTHON]:
            raise ValueError(f"Invalid BACKEND: {cls.BACKEND}. Must be 'ocaml' or 'python'")

        if cls.is_ocaml_backend() and not cls.OCAML_REMOTE:
            if not cls.OCAML_GWD_PATH.exists():
                raise FileNotFoundError(
                    f"OCaml gwd not found at {cls.OCAML_GWD_PATH}. "
                    "Set GENEWEB_DIR to point to GeneWeb directory."
                )
            if not cls.BASES_DIR.exists():
                raise FileNotFoundError(
                    f"Bases directory not found at {cls.BASES_DIR}. "
                    "Set GENEWEB_DIR to point to GeneWeb directory."
                )
