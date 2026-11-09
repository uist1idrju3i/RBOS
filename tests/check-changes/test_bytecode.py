from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/bm-build/check-bytecode.py'


class BytecodeTests(unittest.TestCase):
    def check(self, data, expected_error=None):
        source = '#include <stdint.h>\nconst uint8_t task[] = {\n'
        source += ''.join(f'0x{byte:02x},' for byte in data) + '\n};\n'
        self.check_source(source, expected_error)

    def check_source(self, source, expected_error=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'task.c'
            path.write_text(source)
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 1 if expected_error else 0, result.stderr)
        if expected_error:
            self.assertIn(expected_error, result.stderr)

    def test_valid_bytecode(self):
        self.check(b'RITE0400' + (12).to_bytes(4, 'big'))
        self.check(b'RITE0400' + (256).to_bytes(4, 'big') + bytes(244))

    def test_wrong_version(self):
        self.check(b'RITE0300' + (12).to_bytes(4, 'big'), 'Invalid bytecode version')

    def test_wrong_magic(self):
        self.check(b'NOPE0400' + (12).to_bytes(4, 'big'), 'Invalid bytecode magic')

    def test_wrong_size(self):
        for size in (0, 11, 13, 0x0c000000):
            with self.subTest(size=size):
                self.check(b'RITE0400' + size.to_bytes(4, 'big'), 'Invalid declared bytecode size')

    def test_empty_truncated_and_malformed_arrays(self):
        self.check(b'', 'Truncated bytecode header')
        self.check(b'RITE0400', 'Truncated bytecode header')
        self.check_source('', 'Missing mrbc byte array')
        self.check_source('const uint8_t task[] = {0x52,broken};', 'Invalid mrbc byte array')

    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), str(Path(directory) / 'missing.c')],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Bytecode check failed:', result.stderr)


if __name__ == '__main__':
    unittest.main()
