from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("cc"), "Host C compiler required")
class ADCTests(unittest.TestCase):
    def test_request_lifecycle_and_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "test"
            result = subprocess.run([
                "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(ROOT / "include"), str(ROOT / "src/rbos/adc.c"),
                str(ROOT / "tools/mrubyc-wasm/test_adc.c"), "-o", str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(output)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wiring(self):
        for path in ("src/rbos/adc.c", "src/rbos/adc_binding.c"):
            text = (ROOT / path).read_text()
            self.assertNotIn("#include <nrf", text)
            self.assertNotIn("#include <zephyr", text)
        script = (ROOT / "tools/mrubyc-wasm/check.sh").read_text()
        for fixture in ("adc", "adc_concurrent", "adc_worker"):
            self.assertIn(f'"$build/{fixture}.mrb"', script)


if __name__ == "__main__":
    unittest.main()
