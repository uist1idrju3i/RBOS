#include <bm/bm_irq.h>
#include <bm/bm_scheduler.h>
#include <bm/softdevice_handler/nrf_sdh_ble.h>
#include <nrfx.h>
#include CONFIG_NRFX_RESERVED_RESOURCES_HEADER
#include <zephyr/logging/log.h>
#include <zephyr/sys/util.h>
#include "runtime.h"

LOG_MODULE_REGISTER(rbos_resources, CONFIG_RBOS_LOG_LEVEL);

BUILD_ASSERT(IS_ENABLED(CONFIG_SOFTDEVICE_S115), "RBOS requires S115");
BUILD_ASSERT(IS_ENABLED(CONFIG_LOG_BACKEND_BM_UARTE), "P2 console requires BM UARTE");
BUILD_ASSERT(!IS_ENABLED(CONFIG_SHELL) && !IS_ENABLED(CONFIG_NFC_T2T_NRFXLIB) &&
             !IS_ENABLED(CONFIG_NFC_T4T_NRFXLIB), "Shell/NFC require a new resource audit");
BUILD_ASSERT(IS_ENABLED(CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED), "RBOS requires SCHED dispatch");
BUILD_ASSERT(IS_ENABLED(CONFIG_BM_SCHEDULER), "RBOS requires the BM scheduler");
BUILD_ASSERT(CONFIG_BM_SCHEDULER_BUF_SIZE >= 512, "BM scheduler heap below audited baseline");
BUILD_ASSERT(IS_ENABLED(CONFIG_ZERO_LATENCY_IRQS) && CONFIG_ZERO_LATENCY_LEVELS == 1 &&
             __NVIC_PRIO_BITS == 3 && BM_IRQ_OFFSET == 2,
             "Ruby HAL requires BASEPRI to mask NVIC priorities 2 through 7");
BUILD_ASSERT(CONFIG_BM_TIMER_IRQ_PRIO >= 2 && CONFIG_BM_TIMER_IRQ_PRIO <= 7,
             "BM timer must use an application IRQ priority");
BUILD_ASSERT(CONFIG_LOG_BACKEND_BM_UARTE_IRQ_PRIO >= 2 &&
             CONFIG_LOG_BACKEND_BM_UARTE_IRQ_PRIO <= 7,
             "Console must use an application IRQ priority");
BUILD_ASSERT((NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK & SD_GRTC_CC_CHANNELS_USED) == 0,
             "GRTC allocator overlaps SoftDevice channels");
BUILD_ASSERT((NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK & BIT(0)) != 0 &&
             (SD_GRTC_CC_CHANNELS_USED & BIT(0)) == 0 && SD_GRTC_IRQn_USED != GRTC_2_IRQn,
             "BM system timer requires GRTC channel 0 and GRTC_2");

#define CHECK_RESERVED(actual, reserved) \
  BUILD_ASSERT(((actual) & (reserved)) == (reserved), "nrfx allocator misses " #reserved)
CHECK_RESERVED(NRFX_DPPI00_CHANNELS_USED, SD_DPPIC00_CHANNELS_USED);
CHECK_RESERVED(NRFX_DPPI10_CHANNELS_USED, SD_DPPIC10_CHANNELS_USED);
CHECK_RESERVED(NRFX_DPPI20_CHANNELS_USED, SD_DPPIC20_CHANNELS_USED);
CHECK_RESERVED(NRFX_PPIB_INTERCONNECT_00_10_CHANNELS_USED,
               SD_PPIB00_CHANNELS_USED | SD_PPIB10_CHANNELS_USED);
CHECK_RESERVED(NRFX_PPIB_INTERCONNECT_11_21_CHANNELS_USED,
               SD_PPIB11_CHANNELS_USED | SD_PPIB21_CHANNELS_USED);

void rbos_resources_log(void)
{
  LOG_INF("resources sched_bytes=%u sched_header=%u service_ms=%u sd_ram=%u",
          (unsigned int)CONFIG_BM_SCHEDULER_BUF_SIZE,
          (unsigned int)sizeof(struct bm_scheduler_event),
          (unsigned int)CONFIG_RBOS_SERVICE_INTERVAL_MS,
          (unsigned int)nrf_sdh_ble_sd_ram_usage_get());
}
