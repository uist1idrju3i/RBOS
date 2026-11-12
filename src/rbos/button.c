#include <string.h>
#include <limits.h>
#include "rbos/button.h"
#include "rbos/gpio.h"

extern const uint8_t rbos_button_bytecode[];
static const struct rbos_backend *device;
static mrbc_class *button_class;
static mrbc_class *subscription_class;
static mrbc_sym subscription_sym;
static uint32_t generation, delivery_overflow;
static struct {
  mrbc_value lease;
  uint32_t pin, generation, level, count;
  bool active;
} buttons[4];

static bool stop(unsigned int i)
{
  if (device->button_unwatch(device->context, buttons[i].pin, buttons[i].generation) != RBOS_OK)
    return false;
  rbos_gpio_release(buttons[i].pin);
  mrbc_decref_empty(&buttons[i].lease);
  buttons[i].active = false;
  buttons[i].count = 0;
  return true;
}

void rbos_button_service(void)
{
  if (!device) return;
  for (unsigned int i = 0; i < 4; ++i)
    if (buttons[i].active && buttons[i].lease.instance->ref_count == 1) stop(i);
  if (!device->event_take) return;
  struct rbos_event event;
  for (unsigned int n = 0; n < RBOS_EVENT_QUEUE_CAPACITY; ++n) {
    if (!device->event_take(device->context, &event)) break;
    if (event.type != RBOS_EVENT_BUTTON || event.value > 1 || !event.count) continue;
    for (unsigned int i = 0; i < 4; ++i) {
      if (!buttons[i].active || buttons[i].pin != event.source ||
          buttons[i].generation != event.generation) continue;
      if (event.count > (uint32_t)INT_MAX - buttons[i].count) {
        if (delivery_overflow < UINT32_MAX) ++delivery_overflow;
        continue;
      }
      buttons[i].level = event.value;
      buttons[i].count += event.count;
    }
  }
}

static int receiver(mrbc_vm *vm, mrbc_value *value, bool allow_closed)
{
  if (mrbc_type(*value) != MRBC_TT_OBJECT || value->instance->cls != button_class) {
    mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected Button instance");
    return -1;
  }
  mrbc_value subscription = mrbc_instance_getiv(value, subscription_sym);
  int found = -1;
  if (mrbc_type(subscription) == MRBC_TT_OBJECT && subscription.instance->cls == subscription_class) {
    for (unsigned int i = 0; i < 4; ++i)
      if (buttons[i].active && buttons[i].lease.instance == subscription.instance) found = i;
  }
  mrbc_decref(&subscription);
  if (found >= 0) return found;
  if (!allow_closed) mrbc_raise(vm, MRBC_CLASS(RuntimeError), "Button is closed");
  return -1;
}

static void button_new(mrbc_vm *vm, mrbc_value v[], int argc)
{
  uint32_t pin;
  if (!rbos_require_argc(vm, argc, 1, 1) || !MRBC_KW_END() ||
      !rbos_require_type(vm, &v[0], MRBC_TT_CLASS)) return;
  if (v[0].cls != button_class) { mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected Button class"); return; }
  if (!rbos_gpio_pin(vm, &v[1], &pin)) return;
  if (!device->button_watch || !device->button_unwatch || !device->event_take)
    { rbos_require_status(vm, RBOS_UNSUPPORTED); return; }
  rbos_button_service();
  unsigned int i;
  for (i = 0; i < 4 && buttons[i].active; ++i) {}
  if (i == 4 || generation == UINT32_MAX) { rbos_require_status(vm, RBOS_BUSY); return; }
  /* Native-only objects survive VM-ID reuse; no Proc, VM or task pointer is retained. */
  mrbc_value object = mrbc_instance_new(vm, button_class, 0);
  if (!object.instance) return;
  mrbc_value subscription = mrbc_instance_new(NULL, subscription_class, 0);
  if (!subscription.instance) { mrbc_decref(&object); return; }
  mrbc_instance_setiv(&object, subscription_sym, &subscription);
  if (!rbos_gpio_claim(vm, pin)) { mrbc_decref(&object); mrbc_decref(&subscription); return; }
  uint32_t token = ++generation;
  enum rbos_status status = device->button_watch(device->context, pin, token);
  if (!rbos_require_status(vm, status)) {
    rbos_gpio_unclaim(pin);
    mrbc_decref(&object);
    mrbc_decref(&subscription);
    return;
  }
  buttons[i].lease = subscription;
  buttons[i].pin = pin;
  buttons[i].generation = token;
  buttons[i].count = 0;
  buttons[i].active = true;
  rbos_return_owned(&v[0], object);
}

static void close_button(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0) || !MRBC_KW_END()) return;
  if (mrbc_type(v[0]) != MRBC_TT_OBJECT || v[0].instance->cls != button_class) {
    mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected Button instance"); return;
  }
  int i = receiver(vm, &v[0], true);
  if (i >= 0 && !stop(i)) { rbos_require_status(vm, RBOS_IO_ERROR); return; }
  SET_NIL_RETURN();
}

static void poll(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0) || !MRBC_KW_END()) return;
  int i = receiver(vm, &v[0], false);
  if (i < 0) return;
  rbos_button_service();
  if (!buttons[i].count) { SET_NIL_RETURN(); return; }
  mrbc_value array = mrbc_array_new(vm, 2);
  if (!array.array) return;
  mrbc_value level = mrbc_integer_value(buttons[i].level);
  mrbc_value count = mrbc_integer_value(buttons[i].count);
  mrbc_array_push(&array, &level);
  mrbc_array_push(&array, &count);
  buttons[i].count = 0;
  rbos_return_owned(&v[0], array);
}

static void pressed(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0) || !MRBC_KW_END()) return;
  int i = receiver(vm, &v[0], false);
  if (i < 0) return;
  uint32_t level;
  if (!device->gpio_read) { rbos_require_status(vm, RBOS_UNSUPPORTED); return; }
  if (!rbos_require_status(vm, device->gpio_read(device->context, buttons[i].pin, &level))) return;
  if (level > 1) { rbos_require_status(vm, RBOS_IO_ERROR); return; }
  SET_BOOL_RETURN(level == 0);
}

static void stats(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0) || !MRBC_KW_END() ||
      !rbos_require_type(vm, &v[0], MRBC_TT_CLASS)) return;
  if (v[0].cls != button_class) { mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected Button class"); return; }
  if (!device || !device->event_stats) { rbos_require_status(vm, RBOS_UNSUPPORTED); return; }
  struct rbos_event_stats snapshot;
  device->event_stats(device->context, &snapshot);
  mrbc_value result = mrbc_array_new(vm, 4);
  if (!result.array) return;
  uint32_t values[] = { snapshot.pending, snapshot.overflow, snapshot.coalesced, delivery_overflow };
  for (unsigned int i = 0; i < 4; ++i) {
    mrbc_value value = mrbc_integer_value(values[i] > INT_MAX ? INT_MAX : values[i]);
    mrbc_array_push(&result, &value);
  }
  rbos_return_owned(&v[0], result);
}

static void subscription_new(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_raise(vm, MRBC_CLASS(TypeError), "Button subscriptions cannot be instantiated");
}

void rbos_button_define(const struct rbos_backend *backend)
{
  device = backend;
  memset(buttons, 0, sizeof(buttons));
  generation = delivery_overflow = 0;
  button_class = mrbc_define_class(NULL, "Button", NULL);
  subscription_class = mrbc_define_class(NULL, "RBOSButtonSubscription", NULL);
  subscription_sym = mrbc_str_to_symid("@subscription");
  mrbc_define_method(NULL, subscription_class, "new", subscription_new);
  mrbc_define_method(NULL, button_class, "new", button_new);
  mrbc_define_method(NULL, button_class, "poll", poll);
  mrbc_define_method(NULL, button_class, "close", close_button);
  mrbc_define_method(NULL, button_class, "pressed?", pressed);
  mrbc_define_method(NULL, button_class, "stats", stats);
  if (mrbc_run_mrblib(rbos_button_bytecode) != 1) hal_abort("Button library load failed\n");
}
