import json
from pathlib import Path
import tempfile
import unittest

from notice_fixture import bundle, inventory, notices


class NoticeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "evidence"
        self.root.mkdir()
        bundle(self.root)

    def test_images_licenses_and_apache_selection(self):
        result = notices["verify"](self.root)
        self.assertEqual(result, {"components": 12, "audit": "unverified"})
        data = inventory(self.root)
        mrubyc = next(c for c in data["components"] if c["id"] == "mrubyc")
        self.assertEqual(mrubyc["applies_to"], ["app"])
        text = (self.root / "THIRD_PARTY_NOTICES").read_text()
        for expected in ("Apache-2.0 is selected", "COPYING.RUNTIME", "COPYING.picolibc",
                         "NOTICE", "license-agreement.txt", "license-attribution.txt"):
            self.assertIn(expected, text)

    def test_every_required_license_is_checked(self):
        for component in inventory(self.root)["components"]:
            for source in component["sources"]:
                path = self.root / source["copy"]
                data = path.read_bytes()
                with self.subTest(component=component["id"], source=source["path"]):
                    path.unlink()
                    with self.assertRaises(FileNotFoundError):
                        notices["verify"](self.root)
                    path.write_bytes(b"")
                    with self.assertRaisesRegex(ValueError, "Missing/changed license"):
                        notices["verify"](self.root)
                path.write_bytes(data)

    def test_component_and_license_rows_cannot_be_omitted(self):
        original = inventory(self.root)
        path = self.root / "third-party/inventory.json"
        for field in ("components", "sources"):
            data = json.loads(json.dumps(original))
            (data["components"] if field == "components" else data["components"][0]["sources"]).pop()
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "Missing.*(component|license)"):
                notices["verify"](self.root)

    def test_unknown_archive_and_empty_map_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Unclassified"):
            notices["classify"]("modules/new/libnew.a(new.o)", "app", [])
        for text in ("", "Linker script and memory map\n"):
            with self.assertRaises(ValueError):
                notices["linked"](text)

    def test_discarded_zero_and_load_only_inputs_are_excluded(self):
        text = "Discarded input sections\n .text 0x0 0x20 ignored.a(a.o)\n"
        text += "Linker script and memory map\n .text 0x1000 0x10 kept.a(a.o)\n"
        text += " .text 0x1000 0x0 zero.a(a.o)\nLOAD load_only.a\n"
        text += ".debug_info 0x0 0x20\n .debug_info 0x0 0x20 debug_only.a(a.o)\n"
        self.assertEqual(notices["linked"](text), ["kept.a(a.o)"])

    def test_lto_plugin_inputs_are_recorded(self):
        text = "plugin.a(a.o) (symbol from plugin) (function)\nDiscarded input sections\n"
        text += "Linker script and memory map\n .text 0x1000 0x10 /tmp/cc.ltrans0.o\n"
        self.assertEqual(notices["linked"](text), ["plugin.a(a.o)"])

    def test_changed_map_notice_or_s115_is_rejected(self):
        for relative in ("firmware/zephyr/zephyr.map", "THIRD_PARTY_NOTICES", "production.hex"):
            path = self.root / relative
            data = path.read_bytes()
            path.write_bytes(data + b"changed\n")
            with self.subTest(path=relative), self.assertRaises(ValueError):
                notices["verify"](self.root)
            path.write_bytes(data)


if __name__ == "__main__":
    unittest.main()
