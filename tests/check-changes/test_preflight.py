import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/bm-build/preflight.sh"


class PreflightTests(unittest.TestCase):
    def test_missing_workspace_and_tools_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(["bash", str(SCRIPT), str(root / "missing"), str(root / "build")],
                                    text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("No such file", result.stderr)
            binaries = root / "bin"
            binaries.mkdir()
            for name in ("git", "realpath", "dirname"):
                (binaries / name).symlink_to("/usr/bin/" + name)
            result = subprocess.run(["/usr/bin/bash", str(SCRIPT), str(root), str(root / "build")],
                                    env={"PATH": str(binaries)}, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("Preflight missing tool: west", result.stderr)

    def test_preflight_never_removes_existing_output_or_builds_in_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binaries, workspace, build = (root / name for name in ("bin", "workspace", "build"))
            for path in (binaries, workspace, build):
                path.mkdir()
            (build / "keep").write_text("existing work")
            for name in ("west", "arm-zephyr-eabi-gcc", "cmake", "ninja", "python3"):
                path = binaries / name
                path.write_text("#!/bin/sh\nexit 99\n")
                path.chmod(0o755)
            env = os.environ | {"PATH": str(binaries) + os.pathsep + os.environ["PATH"]}
            for destination, message in ((build, "requires a new"), (workspace / "build", "outside repo/workspace")):
                result = subprocess.run(["bash", str(SCRIPT), str(workspace), str(destination)],
                                        env=env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(message, result.stderr)
            self.assertEqual((build / "keep").read_text(), "existing work")
