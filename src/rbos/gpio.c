#include "rbos/gpio.h"

bool rbos_pin_parse(const char *name, size_t length, uint32_t *pin)
{
  if (!name || !pin || length < 4 || length > 13 || name[0] != 'P') return false;
  uint32_t port = 0, bit = 0;
  size_t i = 1, start = i;
  while (i < length && name[i] >= '0' && name[i] <= '9') {
    uint32_t digit = name[i++] - '0';
    if (port > (UINT32_MAX / 32 - digit) / 10) return false;
    port = port * 10 + digit;
  }
  if (i == start || i == length || name[i++] != '.') return false;
  start = i;
  while (i < length && name[i] >= '0' && name[i] <= '9') {
    bit = bit * 10 + (name[i++] - '0');
    if (bit > 31 || i - start > 2) return false;
  }
  if (i != length || i == start) return false;
  *pin = port * 32 + bit;
  return true;
}

bool rbos_gpio_mode(uint32_t previous, uint32_t requested, uint32_t *mode)
{
  const uint32_t base = RBOS_GPIO_IN | RBOS_GPIO_OUT | RBOS_GPIO_HIGH_Z;
  if (!mode || !requested || (requested & ~63u)) return false;
  uint32_t result = requested;
  if (!(result & base)) {
    if (!(previous & base)) return false;
    result |= previous & (base | RBOS_GPIO_OPEN_DRAIN);
    if (!(requested & (RBOS_GPIO_PULL_UP | RBOS_GPIO_PULL_DOWN)))
      result |= previous & (RBOS_GPIO_PULL_UP | RBOS_GPIO_PULL_DOWN);
  }
  uint32_t direction = result & base;
  if (!direction || (direction & (direction - 1)) ||
      (result & (RBOS_GPIO_PULL_UP | RBOS_GPIO_PULL_DOWN)) ==
        (RBOS_GPIO_PULL_UP | RBOS_GPIO_PULL_DOWN) ||
      ((result & RBOS_GPIO_HIGH_Z) && result != RBOS_GPIO_HIGH_Z) ||
      ((result & RBOS_GPIO_OPEN_DRAIN) && direction != RBOS_GPIO_OUT)) return false;
  *mode = result;
  return true;
}
