import copy
import json
from pathlib import Path
import runpy
import struct
import tempfile
import unittest

from bytecode_fixture import ROOT, make_bytecode_bundle, make_layout_fixture

tool = runpy.run_path(str(ROOT / 'tools/bm-build/bytecode-layout.py'))


class BytecodeLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / 'bytecode'
        self.app = self.root / 'zephyr'
        self.app.mkdir()
        (self.app / 'zephyr.map').write_text('fixture')
        make_bytecode_bundle(self.bundle, 'a' * 40)
        self.report = make_layout_fixture(self.bundle, self.app)
        self.mapping = (self.app / 'zephyr.map').read_text()
        self.image = (self.app / 'zephyr.signed.bin').read_bytes()

    def verify(self, report):
        return tool['verify'](report, self.bundle, self.mapping, self.image)

    def test_normal_and_nonstandard_section_name(self):
        self.assertEqual(self.verify(self.report)['status'], 'PASS')
        self.assertEqual(self.report['symbols'][0]['section']['name'], '.frozen_payload')

    def elf32(self):
        (self.app / 'zephyr.map').write_text('fixture')
        report = make_layout_fixture(self.bundle, self.app, elf_class=32)
        self.assertEqual(report, self.report)
        return (self.app / 'zephyr.elf').read_bytes()

    def test_elf32_arm_little_endian(self):
        elf = self.elf32()
        self.assertEqual(elf[:7], b'\x7fELF\x01\x01\x01')
        self.assertEqual(struct.unpack_from('<H', elf, 18)[0], 40)
        report = tool['collect'](elf, self.bundle, self.mapping, self.image)
        self.assertEqual(report, self.report)
        self.assertEqual(self.verify(report)['status'], 'PASS')

    def test_elf32_corrupt_header(self):
        original = self.elf32()
        for mutation, message in [('short', 'invalid ELF'), ('magic', 'invalid ELF'),
                                  ('encoding', 'unsupported ELF encoding'),
                                  ('section-offset', 'truncated ELF metadata'),
                                  ('section-entry-size', 'invalid section entry size'),
                                  ('string-index', 'missing section table')]:
            with self.subTest(mutation=mutation):
                elf = bytearray(original)
                if mutation == 'short': elf = elf[:32]
                if mutation == 'magic': elf[0] = 0
                if mutation == 'encoding': elf[5] = 0
                if mutation == 'section-offset': struct.pack_into('<I', elf, 32, len(elf) - 8)
                if mutation == 'section-entry-size': struct.pack_into('<H', elf, 46, 39)
                if mutation == 'string-index': struct.pack_into('<H', elf, 50, 5)
                with self.assertRaisesRegex(ValueError, message):
                    tool['collect'](bytes(elf), self.bundle, self.mapping, self.image)

    def test_elf32_corrupt_section_table(self):
        original = self.elf32()
        shoff = struct.unpack_from('<I', original, 32)[0]
        for mutation, message in [('payload-offset', 'truncated ELF data'),
                                  ('symbol-string-link', 'invalid symbol string table'),
                                  ('symbol-entry-size', 'invalid symbol entry size')]:
            with self.subTest(mutation=mutation):
                elf = bytearray(original)
                if mutation == 'payload-offset': struct.pack_into('<I', elf, shoff + 40 + 16, len(elf))
                if mutation == 'symbol-string-link': struct.pack_into('<I', elf, shoff + 3 * 40 + 24, 5)
                if mutation == 'symbol-entry-size': struct.pack_into('<I', elf, shoff + 3 * 40 + 36, 24)
                with self.assertRaisesRegex(ValueError, message):
                    tool['collect'](bytes(elf), self.bundle, self.mapping, self.image)

    def test_elf32_corrupt_symbol_table(self):
        original = self.elf32()
        shoff = struct.unpack_from('<I', original, 32)[0]
        symoff = struct.unpack_from('<I', original, shoff + 3 * 40 + 16)[0]
        symsize = struct.unpack_from('<I', original, shoff + 3 * 40 + 20)[0]
        for mutation, message in [('truncated-entry', 'truncated symbol table'),
                                  ('name-offset', 'invalid ELF string'),
                                  ('address', 'object outside section'),
                                  ('section-index', 'missing ELF symbol')]:
            with self.subTest(mutation=mutation):
                elf = bytearray(original)
                if mutation == 'truncated-entry': struct.pack_into('<I', elf, shoff + 3 * 40 + 20, symsize - 1)
                if mutation == 'name-offset': struct.pack_into('<I', elf, symoff + 16, 0xffffffff)
                if mutation == 'address': struct.pack_into('<I', elf, symoff + 16 + 4, 0x20004400)
                if mutation == 'section-index': struct.pack_into('<H', elf, symoff + 16 + 14, 0)
                with self.assertRaisesRegex(ValueError, message):
                    tool['collect'](bytes(elf), self.bundle, self.mapping, self.image)

    def test_report_mutations(self):
        for mutation in ('ram', 'writable', 'byte', 'outside', 'missing', 'empty', 'schema'):
            with self.subTest(mutation=mutation):
                r = copy.deepcopy(self.report)
                s = r['symbols'][0]
                if mutation == 'ram': s['address'] = 0x20004400
                if mutation == 'writable': s['section']['flags'] |= 1
                if mutation == 'byte': s['sha256'] = '0' * 64
                if mutation == 'outside': s['address'] = self.report['flash']['address'] - 1
                if mutation == 'missing': r['symbols'].pop()
                if mutation == 'empty': r['symbols'] = []
                if mutation == 'schema': r.pop('schema')
                with self.assertRaises(ValueError): self.verify(r)

    def test_elf_bytes_and_flags_are_checked(self):
        original = (self.app / 'zephyr.elf').read_bytes()
        for mutation in ('byte', 'writable', 'ram', 'missing', 'truncated'):
            with self.subTest(mutation=mutation):
                elf = bytearray(original)
                shoff = struct.unpack_from('<Q', elf, 40)[0]
                if mutation == 'byte': elf[128] ^= 1
                if mutation == 'writable': struct.pack_into('<Q', elf, shoff + 64 + 8, 3)
                if mutation == 'ram': struct.pack_into('<Q', elf, shoff + 64 + 16, 0x20004400)
                if mutation == 'missing': elf[elf.index(self.report['symbols'][0]['symbol'].encode() + b'\0')] = ord('X')
                if mutation == 'truncated': elf = elf[:32]
                with self.assertRaises(ValueError):
                    tool['collect'](bytes(elf), self.bundle, self.mapping, self.image)

    def test_image_and_map_are_independent_checks(self):
        with self.assertRaisesRegex(ValueError, 'image bytes differ'):
            tool['verify'](self.report, self.bundle, self.mapping, bytes(len(self.image)))
        with self.assertRaisesRegex(ValueError, 'address differs'):
            tool['verify'](self.report, self.bundle, self.mapping.replace('0xae00 ', '0xae01 '), self.image)
