#include <board-config.h>
#include <bm/bm_irq.h>
#include <nrfx_gpiote.h>
#include <zephyr/irq.h>
#include <zephyr/kernel.h>
#include <zephyr/devicetree.h>
#include "runtime.h"
#include "gpio.h"
#include "button.h"

#define PIN(node) DT_PROP(node, pin)
static nrfx_gpiote_t gpiote20 = NRFX_GPIOTE_INSTANCE(NRF_GPIOTE20);
static nrfx_gpiote_t gpiote30 = NRFX_GPIOTE_INSTANCE(NRF_GPIOTE30);
static struct {
  uint32_t pin, generation;
  uint8_t channel;
  bool active;
  bool unconfigured;
  nrfx_gpiote_t *instance;
} watches[] = { { .pin = PIN(DT_ALIAS(sw0)) }, { .pin = PIN(DT_ALIAS(sw1)) },
                { .pin = PIN(DT_ALIAS(sw2)) }, { .pin = PIN(DT_ALIAS(sw3)) } };

BUILD_ASSERT(DT_PROP(DT_ALIAS(sw0), active_low) && DT_PROP(DT_ALIAS(sw1), active_low) &&
             DT_PROP(DT_ALIAS(sw2), active_low) && DT_PROP(DT_ALIAS(sw3), active_low),
             "Button pressed? requires the audited active-low DK buttons");

ISR_DIRECT_DECLARE(button_irq20)
{
  nrfx_gpiote_irq_handler(&gpiote20);
  return 0;
}

ISR_DIRECT_DECLARE(button_irq30)
{
  nrfx_gpiote_irq_handler(&gpiote30);
  return 0;
}

static void changed(nrfx_gpiote_pin_t pin, nrfx_gpiote_trigger_t trigger, void *context)
{
  (void)trigger;
  (void)context;
  for (unsigned int i = 0; i < 4; ++i) {
    if (!watches[i].active || watches[i].pin != pin) continue;
    struct rbos_event event = { .type = RBOS_EVENT_BUTTON, .source = pin,
      .value = nrf_gpio_pin_read(pin), .generation = watches[i].generation };
    rbos_event_post(&event);
    return;
  }
}

bool rbos_nrf_button_owns(uint32_t pin)
{
  for (unsigned int i = 0; i < 4; ++i)
    if (watches[i].active && watches[i].pin == pin) return true;
  return false;
}

enum rbos_status rbos_nrf_button_watch(void *context, uint32_t pin, uint32_t generation)
{
  enum rbos_status status = rbos_nrf_pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  unsigned int i;
  for (i = 0; i < 4 && watches[i].pin != pin; ++i) {}
  if (i == 4 || !generation) return RBOS_UNSUPPORTED;
  unsigned int key = irq_lock();
  if (watches[i].active) { irq_unlock(key); return RBOS_BUSY; }
  nrfx_gpiote_t *instance = pin / 32 == 0 ? &gpiote30 : &gpiote20;
  if (!nrfx_gpiote_init_check(instance)) {
    if (nrfx_gpiote_init(instance, 7)) { irq_unlock(key); return RBOS_IO_ERROR; }
  }
  BM_IRQ_DIRECT_CONNECT(GPIOTE20_0_IRQn, 7, button_irq20, 0);
  BM_IRQ_DIRECT_CONNECT(GPIOTE30_0_IRQn, 7, button_irq30, 0);
  uint8_t channel;
  if (nrfx_gpiote_channel_alloc(instance, &channel)) { irq_unlock(key); return RBOS_BUSY; }
  uint32_t local_pin = pin;
  NRF_GPIO_Type *port = nrf_gpio_pin_port_decode(&local_pin);
  uint32_t previous = port->PIN_CNF[local_pin];
  nrfx_gpiote_trigger_config_t trigger = { .trigger = NRFX_GPIOTE_TRIGGER_TOGGLE,
    .p_in_channel = &channel };
  nrfx_gpiote_handler_config_t handler = { .handler = changed };
  nrfx_gpiote_input_pin_config_t config = { .p_trigger_config = &trigger,
    .p_handler_config = &handler };
  if (nrfx_gpiote_input_configure(instance, pin, &config)) {
    nrfx_gpiote_pin_uninit(instance, pin);
    nrfx_gpiote_channel_free(instance, channel);
    port->PIN_CNF[local_pin] = previous;
    irq_unlock(key);
    return RBOS_IO_ERROR;
  }
  /* Configure electrical input only after all fallible allocation/configuration. */
  nrf_gpio_cfg_input(pin, NRF_GPIO_PIN_PULLUP);
  watches[i].instance = instance;
  watches[i].generation = generation;
  watches[i].channel = channel;
  watches[i].unconfigured = false;
  watches[i].active = true;
  nrfx_gpiote_trigger_enable(instance, pin, true);
  irq_unlock(key);
  return RBOS_OK;
}

enum rbos_status rbos_nrf_button_unwatch(void *context, uint32_t pin, uint32_t generation)
{
  (void)context;
  unsigned int key = irq_lock();
  for (unsigned int i = 0; i < 4; ++i) {
    if (!watches[i].active || watches[i].pin != pin || watches[i].generation != generation) continue;
    if (!watches[i].unconfigured) {
      nrfx_gpiote_trigger_disable(watches[i].instance, pin);
      if (nrfx_gpiote_pin_uninit(watches[i].instance, pin)) { irq_unlock(key); return RBOS_IO_ERROR; }
      watches[i].unconfigured = true;
    }
    if (nrfx_gpiote_channel_free(watches[i].instance, watches[i].channel))
      { irq_unlock(key); return RBOS_IO_ERROR; }
    watches[i].active = false;
    nrf_gpio_cfg_default(pin);
    irq_unlock(key);
    return RBOS_OK;
  }
  irq_unlock(key);
  return RBOS_IO_ERROR;
}

bool rbos_nrf_event_take(void *context, struct rbos_event *event)
{
  (void)context;
  return rbos_event_take(event);
}

void rbos_nrf_event_stats(void *context, struct rbos_event_stats *stats)
{
  (void)context;
  rbos_event_snapshot(stats);
}
