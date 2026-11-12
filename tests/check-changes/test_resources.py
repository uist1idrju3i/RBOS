from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONFIG = {
    "CONFIG_SOFTDEVICE_S115": 1,
    "CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED": 1,
    "CONFIG_BM_SCHEDULER": 1,
    "CONFIG_BM_SCHEDULER_BUF_SIZE": 512,
    "CONFIG_ZERO_LATENCY_IRQS": 1,
    "CONFIG_ZERO_LATENCY_LEVELS": 1,
    "__NVIC_PRIO_BITS": 3,
    "BM_IRQ_OFFSET": 2,
    "CONFIG_BM_TIMER_IRQ_PRIO": 5,
    "CONFIG_LOG_BACKEND_BM_UARTE_IRQ_PRIO": 5,
    "CONFIG_RBOS_LOG_LEVEL": 3,
    "CONFIG_RBOS_SERVICE_INTERVAL_MS": 10,
    "CONFIG_NRFX_RESERVED_RESOURCES_HEADER": '"rbos_reserved_resources.h"',
    "NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK": 1,
    "GRTC_2_IRQn": 228,
    "GRTC_3_IRQn": 229,
}
SOFTDEVICE = {
    "SD_DPPIC00_CHANNELS_USED": "0xA",
    "SD_DPPIC10_CHANNELS_USED": "0xFFF",
    "SD_DPPIC20_CHANNELS_USED": "1",
    "SD_PPIB00_CHANNELS_USED": "0xF",
    "SD_PPIB10_CHANNELS_USED": "0xF",
    "SD_PPIB11_CHANNELS_USED": "1",
    "SD_PPIB21_CHANNELS_USED": "1",
    "SD_GRTC_CC_CHANNELS_USED": "0xF80",
    "SD_GRTC_IRQn_USED": "GRTC_3_IRQn",
}
ALLOCATORS = {
    "NRFX_DPPI00_CHANNELS_USED": "NRFX_DPPI00_CHANNELS_USED_BY_BT_CTLR",
    "NRFX_DPPI10_CHANNELS_USED": "NRFX_DPPI10_CHANNELS_USED_BY_BT_CTLR",
    "NRFX_DPPI20_CHANNELS_USED": "NRFX_DPPI20_CHANNELS_USED_BY_BT_CTLR",
    "NRFX_PPIB_INTERCONNECT_00_10_CHANNELS_USED": "NRFX_PPIB_00_10_CHANNELS_USED_BY_BT_CTLR",
    "NRFX_PPIB_INTERCONNECT_11_21_CHANNELS_USED": "NRFX_PPIB_11_21_CHANNELS_USED_BY_BT_CTLR",
}


@unittest.skipUnless(shutil.which("cc"), "Host C compiler required")
class ResourceTests(unittest.TestCase):
    def compile(self, config=None, softdevice=None, allocators=None):
        values = CONFIG | (config or {})
        sd = SOFTDEVICE | (softdevice or {})
        nrfx = ALLOCATORS | (allocators or {})
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            headers = {
                "bm/bm_irq.h": "\n".join(f"#define {k} {v}" for k, v in values.items()) + "\n",
                "bm/bm_scheduler.h": "struct bm_scheduler_event { void *node, *fn; unsigned len; };\n",
                "bm/softdevice_handler/nrf_sdh_ble.h": "unsigned nrf_sdh_ble_sd_ram_usage_get(void);\n",
                "nrfx.h": "",
                "nrf_sd_def.h": "\n".join(f"#define {k} {v}" for k, v in sd.items()) + "\n",
                "nrfx_reserved_resources_ncs.h": "\n".join(f"#define {k} {v}" for k, v in nrfx.items()) + "\n",
                "zephyr/logging/log.h": "#define LOG_MODULE_REGISTER(...)\n#define LOG_INF(...) ((void)0)\n",
                "zephyr/sys/util.h": "#define BUILD_ASSERT(c, m) _Static_assert(c, m)\n"
                                     "#define IS_ENABLED(x) (x)\n#define BIT(x) (1UL << (x))\n",
                "mrubyc.h": "typedef struct mrbc_tcb mrbc_tcb;\n",
            }
            for name, content in headers.items():
                path = base / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            return subprocess.run([
                "cc", "-std=c11", "-Werror", "-fsyntax-only", "-I" + str(base),
                "-I" + str(ROOT / "firmware/include"), "-I" + str(ROOT / "include"),
                str(ROOT / "firmware/src/resources.c"),
            ], text=True, capture_output=True)

    def test_valid_contract(self):
        result = self.compile()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_each_allocator_must_protect_softdevice(self):
        for allocator in ALLOCATORS:
            with self.subTest(allocator=allocator):
                result = self.compile(allocators={allocator: "0"})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("nrfx allocator misses", result.stderr)

    def test_reservations_follow_sdk_masks(self):
        result = self.compile(softdevice={"SD_DPPIC00_CHANNELS_USED": "0xF"})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dispatch_heap_priority_and_hal_contracts(self):
        mutations = {
            "CONFIG_SOFTDEVICE_S115": 0,
            "CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED": 0,
            "CONFIG_BM_SCHEDULER": 0,
            "CONFIG_BM_SCHEDULER_BUF_SIZE": 511,
            "CONFIG_ZERO_LATENCY_IRQS": 0,
            "CONFIG_ZERO_LATENCY_LEVELS": 2,
            "__NVIC_PRIO_BITS": 4,
            "BM_IRQ_OFFSET": 1,
            "CONFIG_BM_TIMER_IRQ_PRIO": 1,
            "CONFIG_LOG_BACKEND_BM_UARTE_IRQ_PRIO": 8,
            "CONFIG_MPSL": 1,
            "CONFIG_BT_LL_SOFTDEVICE": 1,
            "CONFIG_NRFX_RESERVED_RESOURCES_HEADER": '"nrfx_reserved_resources_ncs.h"',
        }
        for key, value in mutations.items():
            with self.subTest(config=key):
                result = self.compile(config={key: value})
                self.assertNotEqual(result.returncode, 0)

    def test_larger_heap_is_allowed(self):
        result = self.compile(config={"CONFIG_BM_SCHEDULER_BUF_SIZE": 1024})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_grtc_conflicts(self):
        cases = [
            ({"NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK": 0}, {}),
            ({"NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK": "0x81"}, {}),
            ({}, {"SD_GRTC_CC_CHANNELS_USED": "0xF81"}),
            ({}, {"SD_GRTC_IRQn_USED": "GRTC_2_IRQn"}),
        ]
        for config, softdevice in cases:
            with self.subTest(config=config, softdevice=softdevice):
                result = self.compile(config=config, softdevice=softdevice)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("GRTC", result.stderr)

    def test_firmware_wires_guards_and_diagnostics(self):
        cmake = (ROOT / "firmware/CMakeLists.txt").read_text()
        config = (ROOT / "firmware/common.conf").read_text()
        main = (ROOT / "firmware/src/main.c").read_text()
        kconfig = (ROOT / "firmware/Kconfig").read_text()
        self.assertIn("zephyr_include_directories(include)", cmake)
        self.assertIn("src/resources.c", cmake)
        self.assertIn('config NRFX_RESERVED_RESOURCES_HEADER\n\tdefault "rbos_reserved_resources.h"', kconfig)
        self.assertIn("CONFIG_NRF_SDH_BLE_LOG_SD_RAM_USAGE=y", config)
        self.assertLess(main.index("if (rbos_ble_init())"), main.index("rbos_resources_log();"))
