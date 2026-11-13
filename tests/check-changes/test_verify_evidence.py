import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("verify_evidence", ROOT / "tools/bm-build/verify-evidence.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
REVISION = "a" * 40
MODULES = {"nrf-bm": ("nrf-bm", "b" * 40)}
MAP = """Memory Configuration
FLASH 0xa000 0x149000 xr
RAM 0x20004400 0x3b400 xw
Linker script and memory map
 0xa240 _irq_vector_table
text 0xa800 0x300
rodata 0xab00 0x100
datas 0x20004400 0x100 load address 0xac00
bss 0x20004500 0x500
noinit 0x20004a00 0x200
 0x1000 _flash_used = expression
 0xad00 saadc_irq
 0xad20 button_irq20
 0xad40 button_irq30
"""
CONFIG = """CONFIG_SOFTDEVICE_S115=y
CONFIG_NRFX_SAADC=y
CONFIG_NRFX_GPIOTE20=y
CONFIG_NRFX_GPIOTE30=y
CONFIG_NRFX_GPIOTE_NUM_OF_EVT_HANDLERS=4
CONFIG_LOG_BACKEND_BM_UARTE=y
# CONFIG_GPIO is not set
# CONFIG_SHELL is not set
# CONFIG_BM_ZMS is not set
CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED=y
CONFIG_NRFX_RESERVED_RESOURCES_HEADER="rbos_reserved_resources.h"
CONFIG_RBOS_PERIPHERAL_EXERCISE=y
CONFIG_DEBUG_OPTIMIZATIONS=y
"""
LOG = """[1/20] Performing build step for 'firmware'
Memory region Used Size Region Size %age Used
FLASH: 4096 B 1316 KB 1%
RAM: 2048 B 237 KB 1%
[2/20] Performing build step for 'installer'
FLASH: 100 B 100 KB 1%
RAM: 200 B 100 KB 1%
"""


def rehash(root):
    rows = [hashlib.sha256(path.read_bytes()).hexdigest() + "  ./" + path.relative_to(root).as_posix()
            for path in sorted(root.rglob("*")) if path.is_file() and path.name != "SHA256SUMS"]
    (root / "SHA256SUMS").write_text("\n".join(rows) + "\n")


def fixture(root, profile="debug"):
    app = root / "firmware/zephyr"
    app.mkdir(parents=True)
    (app / "zephyr.map").write_text(MAP)
    config = CONFIG
    if profile == "release":
        config = config.replace("CONFIG_DEBUG_OPTIMIZATIONS=y", "CONFIG_SIZE_OPTIMIZATIONS=y\nCONFIG_RBOS_VM_NDEBUG=y")
    if profile in ("stress", "oom"):
        config += "CONFIG_RBOS_TEST_PROFILE_" + profile.upper() + "=y\n"
    if profile == "oom":
        config = config.replace("CONFIG_RBOS_PERIPHERAL_EXERCISE=y\n", "")
    (app / ".config").write_text(config)
    image = bytearray(4096)
    struct.pack_into("<IIHHII", image, 0, 0x96F3B83D, 0, 512, 0, 3584, 0)
    struct.pack_into("<BBHI", image, 20, 0, 1, 4, 0)
    for irq, pointer in ((213, 0xad01), (218, 0xad21), (268, 0xad41)):
        struct.pack_into("<I", image, 0x240 + irq * 4, pointer)
    (app / "zephyr.signed.bin").write_bytes(image)
    (root / "rbos-git.txt").write_text(REVISION + "\n")
    (root / "west-list.txt").write_text("manifest nrf-bm N/A\n")
    (root / "manifest-head.txt").write_text("b" * 40 + "\n")
    (root / "build.log").write_text(LOG)
    rehash(root)


class VerifyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "evidence"
        fixture(self.root)

    def verify(self, **options):
        return verifier.verify(self.root, REVISION, (0, 1, 4, 0), "debug", MODULES, **options)

    def test_valid_and_ram_region_is_not_used_memory(self):
        report = self.verify()
        self.assertEqual(report["map"], dict(flash=4096, ram=2048, text=768, rodata=256,
                                            data=256, bss=1280, noinit=512))
        self.assertNotEqual(report["map"]["ram"], 0x3b400)
        self.assertEqual(report["build_log"], dict(flash=4096, ram=2048))

    def test_wrapped_output_section(self):
        sizes = verifier.map_sizes(MAP.replace("noinit 0x20004a00", "noinit\n  0x20004a00"))
        self.assertEqual(sizes["ram"], 2048)

    def test_disabled_booleans_may_be_omitted_but_required_values_may_not(self):
        exercise = "CONFIG_RBOS_PERIPHERAL_EXERCISE"
        base = CONFIG.replace(exercise + "=y\n", "")
        for key in ("CONFIG_GPIO", "CONFIG_SHELL", "CONFIG_BM_ZMS"):
            base = base.replace("# " + key + " is not set\n", "")
        base += "CONFIG_RBOS_TEST_PROFILE_OOM=y\n"
        for disabled in ("", "# " + exercise + " is not set\n", exercise + "=n\n"):
            with self.subTest(disabled=disabled):
                verifier.configuration(base + disabled, "oom")
        for wrong in (base + exercise + "=y\n", base + "CONFIG_GPIO=y\n",
                      base.replace("CONFIG_NRFX_SAADC=y\n", ""),
                      base.replace("CONFIG_NRFX_GPIOTE_NUM_OF_EVT_HANDLERS=4\n", "")):
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, "configuration"):
                verifier.configuration(wrong, "oom")
        with self.assertRaisesRegex(ValueError, "configuration"):
            verifier.configuration(CONFIG.replace(exercise + "=y\n", ""), "debug")

    def test_version_magic_and_lengths(self):
        image = bytearray((self.root / "firmware/zephyr/zephyr.signed.bin").read_bytes())
        self.assertEqual(verifier.image_header(image), (0, 1, 4, 0))
        for offset, data in ((0, b"NOPE"), (8, b"\xff\xff"), (12, b"\xff" * 4)):
            bad = image.copy()
            bad[offset:offset + len(data)] = data
            with self.assertRaises(ValueError):
                verifier.image_header(bad)

    def test_corruption_and_missing_checksum_coverage(self):
        (self.root / "build.log").write_text("corrupted")
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            self.verify()
        rehash(self.root)
        (self.root / "extra").write_text("unhashed")
        with self.assertRaisesRegex(ValueError, "Unchecksummed"):
            self.verify()

    def test_private_keys_symlinks_and_unsafe_paths(self):
        for name, content in (("keyfile.json", "public but excluded"), ("key.pem", "fixture"),
                              ("innocent.txt", "-----BEGIN RSA PRIVATE KEY-----")):
            path = self.root / name
            path.write_text(content)
            with self.assertRaisesRegex(ValueError, "key"):
                self.verify()
            path.unlink()
        (self.root / "link").symlink_to(self.root / "build.log")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.verify()
        (self.root / "link").unlink()
        (self.root / "SHA256SUMS").write_text("0" * 64 + "  ../escape\n")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            self.verify()

    def test_wrong_revision_dirty_tree_modules_version_irq_profile_and_log(self):
        cases = (("rbos-git.txt", "c" * 40 + "\n", "revision"),
                 ("rbos-git.txt", REVISION + "\n M source\n", "dirty"),
                 ("manifest-head.txt", "c" * 40, "module"),
                 ("firmware/zephyr/.config", CONFIG.replace("EXERCISE=y", "EXERCISE=n"), "configuration"),
                 ("firmware/zephyr/zephyr.map", MAP.replace("0xad00 saadc_irq", "0xad80 saadc_irq"), "IRQ"),
                 ("build.log", LOG.replace("2048 B", "3000 B"), "memory"))
        for relative, content, message in cases:
            path = self.root / relative
            original = path.read_bytes()
            path.write_text(content)
            rehash(self.root)
            with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, message):
                self.verify()
            path.write_bytes(original)
        rehash(self.root)
        with self.assertRaisesRegex(ValueError, "version"):
            verifier.verify(self.root, REVISION, (0, 1, 5, 0), "debug", MODULES)

    def test_baseline_delta_and_explicit_expected_sizes(self):
        baseline = Path(self.directory.name) / "baseline"
        fixture(baseline)
        report = self.verify(baseline=baseline, expected_sizes={"flash": 4096, "ram": 2048})
        self.assertEqual(set(report["map_delta"].values()), {0})
        with self.assertRaisesRegex(ValueError, "Expected memory"):
            self.verify(expected_sizes={"ram": 1000})

    def test_all_four_profiles_and_missing_profile_fail_closed(self):
        base = Path(self.directory.name) / "profiles"
        modules = Path(self.directory.name) / "modules.txt"
        modules.write_text("nrf-bm nrf-bm " + "b" * 40 + "\n")
        for profile in verifier.PROFILES:
            fixture(base / ("firmware-evidence-" + profile + "-" + REVISION), profile)
        args = [str(base), "--revision", REVISION, "--version", "0.1.4+0", "--modules", str(modules)]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(verifier.main(args), 0)
        self.assertEqual(json.loads(output.getvalue())["completion"]["real_hardware"], "NOT_RUN")
        (base / ("firmware-evidence-oom-" + REVISION) / "build.log").unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(verifier.main(args), 1)
