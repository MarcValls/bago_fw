#!/usr/bin/env python3
"""Central path helpers for source, frozen app, and bundled resources."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def is_frozen_app() -> bool:
    """Return True when running as a PyInstaller-frozen executable."""
    return bool(getattr(sys, "frozen", False))


def _find_source_root() -> Path:
    """Best-effort root discovery for the source tree."""
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".bago").is_dir():
            return candidate
    try:
        return current.parents[2]
    except IndexError:
        return current.parent


def source_base_dir() -> Path:
    """Return the project root when running from source."""
    return _find_source_root()


def app_base_dir() -> Path:
    """Return the writable application directory."""
    if is_frozen_app():
        return Path(sys.executable).resolve().parent
    return source_base_dir()


def bundle_base_dir() -> Path:
    """Return the directory that contains bundled resources."""
    if is_frozen_app():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(str(meipass)).resolve()
    return source_base_dir()


def resource_path(*parts: Any) -> Path:
    """Build a path to a bundled resource."""
    return bundle_base_dir().joinpath(*(str(part) for part in parts if str(part)))


def external_program_path(source_name: str, frozen_name: str | None = None) -> Path:
    """Return the path to a helper program next to the app."""
    if is_frozen_app():
        return app_base_dir() / str(frozen_name or source_name)
    return app_base_dir() / str(source_name)

