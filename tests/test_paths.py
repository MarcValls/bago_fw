from __future__ import annotations

import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / ".bago" / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import paths


class PathHelpersTest(TestCase):
    def test_source_base_dir_finds_repo_root(self) -> None:
        with patch.object(paths, "__file__", str(CORE / "paths.py")):
            self.assertEqual(paths.source_base_dir(), ROOT)

    def test_app_base_dir_uses_executable_when_frozen(self) -> None:
        with patch.object(paths, "is_frozen_app", return_value=True), patch.object(
            paths.sys, "executable", r"C:\Temp\BAGO\bago.exe"
        ):
            self.assertEqual(paths.app_base_dir(), Path(r"C:\Temp\BAGO"))

    def test_bundle_base_dir_uses_meipass_when_frozen(self) -> None:
        with patch.object(paths, "is_frozen_app", return_value=True), patch.object(
            paths.sys, "_MEIPASS", r"C:\Temp\_MEI123", create=True
        ):
            self.assertEqual(paths.bundle_base_dir(), Path(r"C:\Temp\_MEI123"))

    def test_resource_and_external_paths_follow_mode(self) -> None:
        with patch.object(paths, "__file__", str(CORE / "paths.py")):
            self.assertEqual(paths.resource_path("assets", "logo.png"), ROOT / "assets" / "logo.png")
            self.assertEqual(paths.external_program_path("tool.py", "tool.exe"), ROOT / "tool.py")

