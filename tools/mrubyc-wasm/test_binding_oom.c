#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define mrbc_raw_alloc real_pool_alloc
#include "alloc.c"
#undef mrbc_raw_alloc

static unsigned target, allocations;
static int armed;
static const char *operation;
static void *allocated[8];
static unsigned baseline_used, partial_used;
static void before_fatal(void);

static void exhaust_pool(void)
{
  for (;;) {
    USED_BLOCK *largest = NULL;
    USED_BLOCK *block = (USED_BLOCK *)BPOOL_TOP(memory_pool);
    for (; block < (USED_BLOCK *)BPOOL_END(memory_pool); block = PHYS_NEXT(block))
      if (!IS_USED_BLOCK(block) && (!largest || BLOCK_SIZE(block) > BLOCK_SIZE(largest)))
        largest = block;
    if (!largest) return;
    assert(real_pool_alloc(BLOCK_SIZE(largest) - sizeof(USED_BLOCK)));
  }
}

void *mrbc_raw_alloc(unsigned size)
{
  if (armed && ++allocations == target) {
    struct MRBC_ALLOC_STATISTICS stat;
    mrbc_alloc_statistics(&stat);
    partial_used = stat.used;
    exhaust_pool();
    before_fatal();
    real_pool_alloc(size);
    assert(0);
  }
  void *result = real_pool_alloc(size);
  if (armed) { assert(allocations < 8); allocated[allocations] = result; }
  return result;
}

#include "../../src/rbos/adc_binding.c"
#define receiver button_receiver
#define poll button_poll
#define device button_device
#include "../../src/rbos/button.c"
#undef device
#undef poll
#undef receiver
#define receiver gpio_receiver
#define device gpio_device
#include "../../src/rbos/gpio_binding.c"
#undef device
#undef receiver

static uint8_t heap[1024 * 1024];
static unsigned configured, watches, unwatches, starts, snapshots, takes;
static bool watched, adc_owned, edge;
static mrbc_vm vm;

static enum rbos_status validate(void *c, uint32_t pin) { return pin == 45 ? RBOS_OK : RBOS_INVALID_PIN; }
static enum rbos_status configure_pin(void *c, uint32_t pin, uint32_t mode) { ++configured; return RBOS_OK; }
static enum rbos_status watch(void *c, uint32_t pin, uint32_t gen) { ++watches; watched = true; return RBOS_OK; }
static enum rbos_status unwatch(void *c, uint32_t pin, uint32_t gen) { ++unwatches; watched = false; return RBOS_OK; }
static bool take(void *c, struct rbos_event *e)
{
  ++takes;
  if (!edge) return false;
  *e = (struct rbos_event){ .type = RBOS_EVENT_BUTTON, .source = 45,
    .generation = buttons[0].generation, .count = 1 };
  edge = false;
  return true;
}
static void snapshot(void *c, struct rbos_event_stats *s) { ++snapshots; *s = (struct rbos_event_stats){0}; }
static uint32_t uptime(void *c) { return 0; }
static enum rbos_status begin_adc(void *c, enum rbos_adc_input input, uint32_t token)
{ ++starts; adc_owned = true; return RBOS_OK; }
static enum rbos_status poll_adc(void *c, uint32_t t, struct rbos_adc_sample *s) { return RBOS_PENDING; }
static void cancel_adc(void *c, uint32_t t) { adc_owned = false; }

static mrbc_value invoke(mrbc_value self, const char *name, unsigned argc, mrbc_value a, mrbc_value b)
{
  mrbc_method method;
  mrbc_class *cls = mrbc_type(self) == MRBC_TT_CLASS ? self.cls : self.instance->cls;
  assert(mrbc_find_method(&method, cls, mrbc_str_to_symid(name)) && method.c_func);
  mrbc_value regs[4] = { self, a, b, mrbc_nil_value() };
  if (argc < 2) regs[argc + 1] = mrbc_nil_value();
  method.func(&vm, regs, argc);
  assert(mrbc_type(vm.exception) <= MRBC_TT_NIL);
  return regs[0];
}

void wasm_uncaught_exception(struct VM *v) { assert(0); }
static void before_fatal(void)
{
  assert(armed && target && allocations == target);
  assert(!configured && !unwatches && !starts && !adc_owned && !adc.active);
  assert(mrbc_type(lease) == MRBC_TT_EMPTY);
  bool active = !strcmp(operation, "poll") || !strcmp(operation, "stats");
  assert(watched == active && watches == (unsigned)active);
  assert(buttons[0].active == active);
  assert((state(45) >= 0) == active);
  if (active) {
    assert(pins[state(45)].claimed && buttons[0].lease.instance->ref_count == 2);
    assert(buttons[0].count == (unsigned)!strcmp(operation, "poll"));
  }
  assert(snapshots == (unsigned)!strcmp(operation, "stats"));
  assert(takes == (!strcmp(operation, "poll") ? 3u :
                  (!strcmp(operation, "request") || !strcmp(operation, "button") ||
                   !strcmp(operation, "stats")) ? 1u : 0u));
  struct MRBC_ALLOC_STATISTICS stat;
  mrbc_alloc_statistics(&stat);
  assert(target == 1 ? partial_used == baseline_used : partial_used > baseline_used);
  if (target > 1 && (!strcmp(operation, "internal") || !strcmp(operation, "gpio") ||
                    !strcmp(operation, "button")))
    assert(((mrbc_instance *)allocated[1])->ref_count == 1);
  if (!strcmp(operation, "button") && target == 3)
    assert(((mrbc_instance *)allocated[2])->ref_count == 2);
  printf("PASS: binding OOM %s allocation=%u watches=%u starts=%u used=%u (fatal; no recovery guarantee)\n",
         operation, allocations, watches, starts, stat.used);
}

int main(int argc, char **argv)
{
  assert(argc == 3);
  operation = argv[1]; target = strtoul(argv[2], NULL, 10);
  mrbc_init(heap, sizeof(heap));
  const struct rbos_backend backend = { .pin_validate = validate, .gpio_configure = configure_pin,
    .button_watch = watch, .button_unwatch = unwatch, .event_take = take, .event_stats = snapshot,
    .uptime_ms = uptime, .adc_start = begin_adc, .adc_poll = poll_adc, .adc_cancel = cancel_adc };
  rbos_define_classes(&backend);
  mrbc_value nil = mrbc_nil_value(), pin = mrbc_integer_value(45);
  mrbc_value adc_type = { .tt = MRBC_TT_CLASS, .cls = mrbc_get_class_by_name("ADC") };
  mrbc_value button_type = { .tt = MRBC_TT_CLASS, .cls = mrbc_get_class_by_name("Button") };
  mrbc_value gpio_type = { .tt = MRBC_TT_CLASS, .cls = mrbc_get_class_by_name("GPIO") };
  mrbc_value input = mrbc_symbol_value(mrbc_str_to_symid("vdd"));
  mrbc_value self = nil;
  if (!strcmp(operation, "request")) self = invoke(adc_type, "internal", 1, input, nil);
  if (!strcmp(operation, "poll") || !strcmp(operation, "stats"))
    self = invoke(button_type, "new", 1, pin, nil);
  if (!strcmp(operation, "poll")) edge = true;
  struct MRBC_ALLOC_STATISTICS baseline;
  mrbc_alloc_statistics(&baseline);
  baseline_used = baseline.used;
  armed = 1;
  if (!strcmp(operation, "internal")) invoke(adc_type, "internal", 1, input, nil);
  else if (!strcmp(operation, "request")) invoke(self, "__start", 1, mrbc_false_value(), nil);
  else if (!strcmp(operation, "gpio")) invoke(gpio_type, "new", 2, pin, mrbc_integer_value(RBOS_GPIO_OUT));
  else if (!strcmp(operation, "button")) invoke(button_type, "new", 1, pin, nil);
  else if (!strcmp(operation, "poll")) invoke(self, "poll", 0, nil, nil);
  else { assert(!strcmp(operation, "stats")); invoke(button_type, "stats", 0, nil, nil); }
  assert(target == 0);
  printf("PASS: binding allocation control %s allocations=%u\n", operation, allocations);
  return 0;
}
