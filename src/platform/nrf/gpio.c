#include <string.h>
#include <board-config.h>
#include <hal/nrf_gpio.h>
#include <zephyr/devicetree.h>
#include <zephyr/kernel.h>
#include "rbos/gpio.h"
#include "gpio.h"
#include "button.h"

#define PIN(node) DT_PROP(node, pin)
#define ENTRY(name, node) { name, PIN(node) }
#define LABEL_ENTRY(label, node) ENTRY(STRINGIFY(label), node),
#define CHILD(node) DT_FOREACH_NODELABEL_VARGS(node, LABEL_ENTRY, node)
static const struct { const char *name; uint32_t pin; } labels[] = {
  DT_FOREACH_CHILD_STATUS_OKAY(DT_NODELABEL(rbos_gpio_pins), CHILD)
  ENTRY("sw0", DT_ALIAS(sw0)), ENTRY("sw1", DT_ALIAS(sw1)),
  ENTRY("sw2", DT_ALIAS(sw2)), ENTRY("sw3", DT_ALIAS(sw3)),
};

BUILD_ASSERT(!IS_ENABLED(CONFIG_GPIO), "Zephyr GPIO driver must not share native pins/GPIOTE");

enum rbos_status rbos_nrf_pin_lookup(void *context, const char *label, uint32_t *pin)
{
  (void)context;
  if (!label || !pin) return RBOS_IO_ERROR;
  for (unsigned int i = 0; i < sizeof(labels) / sizeof(*labels); ++i) {
    if (!strcmp(label, labels[i].name)) { *pin = labels[i].pin; return RBOS_OK; }
  }
  return RBOS_INVALID_PIN;
}

enum rbos_status rbos_nrf_pin_validate(void *context, uint32_t pin)
{
  (void)context;
  uint32_t port = pin / 32, bit = pin % 32;
  static const uint8_t count[] = DT_PROP(DT_NODELABEL(rbos_gpio_pins), port_pin_counts);
  BUILD_ASSERT(ARRAY_SIZE(count) == 3, "nRF54L15 pin metadata requires three ports");
  if (port >= 3 || bit >= count[port] || !nrf_gpio_pin_present_check(pin)) return RBOS_INVALID_PIN;
  /* Only explicitly reviewed DT pins are released. Other pins need an
     electrical/owner review before use, including clocks, NFC and debug. */
  for (unsigned int i = 0; i < sizeof(labels) / sizeof(*labels); ++i) {
    if (pin != labels[i].pin) continue;
    if (IS_ENABLED(CONFIG_LOG_BACKEND_BM_UARTE) && pin == BOARD_CONSOLE_UARTE_PIN_TX)
      return RBOS_RESERVED_PIN;
    if (IS_ENABLED(CONFIG_LOG_BACKEND_BM_UARTE_USE_HWFC) && pin == BOARD_CONSOLE_UARTE_PIN_CTS)
      return RBOS_RESERVED_PIN;
    return RBOS_OK;
  }
  return RBOS_RESERVED_PIN;
}

enum rbos_status rbos_nrf_gpio_configure(void *context, uint32_t pin, uint32_t mode)
{
  enum rbos_status status = rbos_nrf_pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  if (rbos_nrf_button_owns(pin)) return RBOS_BUSY;
  uint32_t checked;
  if (!rbos_gpio_mode(0, mode, &checked)) return RBOS_IO_ERROR;
  nrf_gpio_pin_pull_t pull = (mode & RBOS_GPIO_PULL_UP) ? NRF_GPIO_PIN_PULLUP :
    (mode & RBOS_GPIO_PULL_DOWN) ? NRF_GPIO_PIN_PULLDOWN : NRF_GPIO_PIN_NOPULL;
  if (mode & RBOS_GPIO_OUT) nrf_gpio_pin_clear(pin);
  nrf_gpio_cfg(pin, mode & RBOS_GPIO_OUT ? NRF_GPIO_PIN_DIR_OUTPUT : NRF_GPIO_PIN_DIR_INPUT,
    mode == RBOS_GPIO_HIGH_Z ? NRF_GPIO_PIN_INPUT_DISCONNECT : NRF_GPIO_PIN_INPUT_CONNECT,
    pull, mode & RBOS_GPIO_OPEN_DRAIN ? NRF_GPIO_PIN_S0D1 : NRF_GPIO_PIN_S0S1,
    NRF_GPIO_PIN_NOSENSE);
  return RBOS_OK;
}

enum rbos_status rbos_nrf_gpio_read(void *context, uint32_t pin, uint32_t *level)
{
  enum rbos_status status = rbos_nrf_pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  if (!level) return RBOS_IO_ERROR;
  *level = nrf_gpio_pin_read(pin);
  return RBOS_OK;
}

enum rbos_status rbos_nrf_gpio_write(void *context, uint32_t pin, uint32_t level)
{
  enum rbos_status status = rbos_nrf_pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  if (level > 1) return RBOS_IO_ERROR;
  if (rbos_nrf_button_owns(pin)) return RBOS_BUSY;
  nrf_gpio_pin_write(pin, level);
  return RBOS_OK;
}
