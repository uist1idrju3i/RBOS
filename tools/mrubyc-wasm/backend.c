#include <stddef.h>
#include <string.h>
#include <emscripten.h>

#include "backend.h"
#include "rbos/gpio.h"

static const uint32_t board_pins[] = { 73, 42, 71, 46, 45, 41, 40, 4 };
static struct { uint32_t mode, level; } gpio[96];
static enum rbos_status gpio_status;
static unsigned int gpio_calls;
static uint32_t watched[96];
static struct rbos_event_queue events;

static enum rbos_status pin_lookup(void *context, const char *label, uint32_t *pin)
{
  (void)context;
  const char *names[] = { "led0", "led1", "led2", "led3", "sw0", "sw1", "sw2", "sw3" };
  for (unsigned int i = 0; i < 8; ++i)
    if (!strcmp(label, names[i])) { *pin = board_pins[i]; return RBOS_OK; }
  if (!strncmp(label, "button", 6) && strlen(label) == 7 && label[6] >= '0' && label[6] <= '3') {
    *pin = board_pins[4 + label[6] - '0'];
    return RBOS_OK;
  }
  return RBOS_INVALID_PIN;
}

static enum rbos_status pin_validate(void *context, uint32_t pin)
{
  (void)context;
  const uint8_t count[] = { 7, 16, 11 };
  if (pin / 32 >= 3 || pin % 32 >= count[pin / 32]) return RBOS_INVALID_PIN;
  for (unsigned int i = 0; i < 8; ++i) if (pin == board_pins[i]) return RBOS_OK;
  return RBOS_RESERVED_PIN;
}

static enum rbos_status gpio_configure(void *context, uint32_t pin, uint32_t mode)
{
  enum rbos_status status = pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  if (watched[pin]) return RBOS_BUSY;
  ++gpio_calls;
  if (gpio_status != RBOS_OK) return gpio_status;
  gpio[pin].mode = mode;
  if (mode & RBOS_GPIO_OUT) gpio[pin].level = 0;
  else gpio[pin].level = (mode & RBOS_GPIO_PULL_UP) ? 1 : 0;
  return RBOS_OK;
}

static enum rbos_status gpio_read(void *context, uint32_t pin, uint32_t *level)
{
  enum rbos_status status = pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  ++gpio_calls;
  if (gpio_status == RBOS_OK) *level = gpio[pin].level;
  return gpio_status;
}

static enum rbos_status gpio_write(void *context, uint32_t pin, uint32_t level)
{
  enum rbos_status status = pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  if (watched[pin]) return RBOS_BUSY;
  ++gpio_calls;
  if (gpio_status == RBOS_OK) gpio[pin].level = level;
  return gpio_status;
}

void rbos_wasm_gpio_status(enum rbos_status status) { gpio_status = status; }
unsigned int rbos_wasm_gpio_calls(void) { return gpio_calls; }
void rbos_wasm_gpio_level(uint32_t pin, uint32_t level) { if (pin < 96) gpio[pin].level = level; }
uint32_t rbos_wasm_gpio_mode(uint32_t pin) { return pin < 96 ? gpio[pin].mode : 0; }

static enum rbos_status button_watch(void *context, uint32_t pin, uint32_t generation)
{
  enum rbos_status status = pin_validate(context, pin);
  if (status != RBOS_OK) return status;
  bool button = false;
  for (unsigned int i = 4; i < 8; ++i) if (pin == board_pins[i]) button = true;
  if (!button) return RBOS_UNSUPPORTED;
  if (watched[pin]) return RBOS_BUSY;
  if (gpio_status != RBOS_OK) return gpio_status;
  gpio[pin].mode = RBOS_GPIO_IN | RBOS_GPIO_PULL_UP;
  gpio[pin].level = 1;
  watched[pin] = generation;
  return RBOS_OK;
}

static enum rbos_status button_unwatch(void *context, uint32_t pin, uint32_t generation)
{
  (void)context;
  if (pin >= 96 || watched[pin] != generation) return RBOS_IO_ERROR;
  if (gpio_status != RBOS_OK) return gpio_status;
  watched[pin] = 0;
  gpio[pin].mode = RBOS_GPIO_HIGH_Z;
  return RBOS_OK;
}

static bool event_take(void *context, struct rbos_event *event)
{
  (void)context;
  return rbos_event_queue_pop(&events, event);
}

static void event_stats(void *context, struct rbos_event_stats *stats)
{
  (void)context;
  *stats = (struct rbos_event_stats){ events.size, events.overflow, events.coalesced };
}

uint32_t rbos_wasm_button_generation(uint32_t pin) { return pin < 96 ? watched[pin] : 0; }
void rbos_wasm_button_edge(uint32_t pin, uint32_t level, uint32_t generation)
{
  if (pin >= 96) return;
  gpio[pin].level = level;
  struct rbos_event event = { .type = RBOS_EVENT_BUTTON, .source = pin,
    .value = level, .generation = generation ? generation : watched[pin] };
  rbos_event_queue_push(&events, &event);
}

void rbos_wasm_event_fill(void)
{
  for (unsigned int i = 0; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) {
    struct rbos_event event = { .type = RBOS_EVENT_COMPLETION, .source = i };
    rbos_event_queue_push(&events, &event);
  }
}

static struct {
  int32_t quarter_celsius;
  enum rbos_status status;
  unsigned int calls;
} temperature = { .quarter_celsius = 100 };

static enum rbos_status temperature_read(void *context, int32_t *quarter_celsius)
{
  (void)context;
  ++temperature.calls;
  if (temperature.status == RBOS_OK) *quarter_celsius = temperature.quarter_celsius;
  return temperature.status;
}

static struct {
  int32_t raw;
  enum rbos_status status;
  uint32_t delay_ms, stop_ms, started, stopped, token;
  unsigned int calls;
  int input;
  int active, cancelling;
} adc = { .raw = 1024 };

static uint32_t uptime_ms(void *context)
{
  (void)context;
  return (uint32_t)emscripten_get_now();
}

static enum rbos_status adc_start(void *context, enum rbos_adc_input input, uint32_t token)
{
  if (adc.active) return RBOS_BUSY;
  adc.active = 1;
  adc.cancelling = 0;
  adc.started = uptime_ms(context);
  adc.token = token;
  adc.input = input;
  ++adc.calls;
  return RBOS_OK;
}

static enum rbos_status adc_poll(void *context, uint32_t token, struct rbos_adc_sample *sample)
{
  if (!adc.active || adc.token != token) return RBOS_IO_ERROR;
  if (adc.cancelling) {
    if ((uint32_t)(uptime_ms(context) - adc.stopped) < adc.stop_ms) return RBOS_PENDING;
    adc.active = 0;
    return RBOS_TIMEOUT;
  }
  if ((uint32_t)(uptime_ms(context) - adc.started) < adc.delay_ms) return RBOS_PENDING;
  adc.active = 0;
  if (adc.status == RBOS_OK)
    *sample = (struct rbos_adc_sample){ adc.raw, 3600000, 12 };
  return adc.status;
}

static void adc_cancel(void *context, uint32_t token)
{
  if (adc.active && adc.token == token && !adc.cancelling) {
    adc.cancelling = 1;
    adc.stopped = uptime_ms(context);
  }
}

void rbos_wasm_adc_configure(int32_t raw, enum rbos_status status, uint32_t delay_ms, uint32_t stop_ms)
{
  adc.raw = raw;
  adc.status = status;
  adc.delay_ms = delay_ms;
  adc.stop_ms = stop_ms;
}

unsigned int rbos_wasm_adc_calls(void) { return adc.calls; }
int rbos_wasm_adc_input(void) { return adc.input; }
int rbos_wasm_adc_active(void) { return adc.active; }

static struct rbos_backend backend = {
  .pin_lookup = pin_lookup, .pin_validate = pin_validate,
  .gpio_configure = gpio_configure, .gpio_read = gpio_read, .gpio_write = gpio_write,
  .button_watch = button_watch, .button_unwatch = button_unwatch,
  .event_take = event_take, .event_stats = event_stats,
  .temperature_read = temperature_read, .uptime_ms = uptime_ms,
  .adc_start = adc_start, .adc_poll = adc_poll, .adc_cancel = adc_cancel,
};

const struct rbos_backend *rbos_wasm_backend(void)
{
  return &backend;
}

void rbos_wasm_temperature_configure(int32_t quarter_celsius, enum rbos_status status)
{
  temperature.quarter_celsius = quarter_celsius;
  temperature.status = status;
}

void rbos_wasm_temperature_available(int available)
{
  backend.temperature_read = available ? temperature_read : NULL;
}

unsigned int rbos_wasm_temperature_calls(void)
{
  return temperature.calls;
}
