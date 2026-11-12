#include <errno.h>
#include <string.h>
#include <bm/bm_scheduler.h>
#include <zephyr/logging/log.h>
#include "runtime.h"

LOG_MODULE_REGISTER(rbos_probe, CONFIG_RBOS_LOG_LEVEL);
static unsigned int delivered;
static bool corrupt;
static uint8_t payload[64];

static void consume(void *data, size_t length)
{
  ++delivered;
  if (length && memcmp(data, payload, length)) corrupt = true;
}

int rbos_resources_probe(void)
{
  /* Run before SoftDevice enable and VM creation, never against a live SD queue. */
  memset(payload, 0xa5, sizeof(payload));
  const size_t lengths[] = { 0, 16, 64 };
  for (unsigned int i = 0; i < 3; ++i) {
    size_t length = lengths[i];
    unsigned int accepted = 0;
    delivered = 0;
    corrupt = false;
    int result = 0;
    for (; accepted < 64; ++accepted) {
      result = bm_scheduler_defer(consume, length ? payload : NULL, length);
      if (result) break;
    }
    bm_scheduler_process();
    bool valid = (result == -ENOMEM || (result == 0 && accepted == 64)) &&
      accepted > 0 && delivered == accepted && !corrupt;
    if (!bm_scheduler_defer(consume, length ? payload : NULL, length)) {
      bm_scheduler_process();
      valid = valid && delivered == accepted + 1 && !corrupt;
    } else valid = false;
    LOG_INF("scheduler_probe payload=%u accepted=%u delivered=%u exhausted=%u recovered=%u",
      (unsigned int)length, accepted, delivered, result == -ENOMEM, valid);
    if (!valid) return -EIO;
  }
  return 0;
}
