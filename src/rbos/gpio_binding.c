#include <string.h>
#include <limits.h>
#include "rbos/gpio.h"

static const struct rbos_backend *device;
static mrbc_class *gpio_class;
static mrbc_sym pin_sym;
static struct {
  uint32_t pin, mode;
  bool claimed;
} pins[64];

static int state(uint32_t pin)
{
  for (unsigned int i = 0; i < 64; ++i)
    if ((pins[i].mode || pins[i].claimed) && pins[i].pin == pin) return i;
  return -1;
}

bool rbos_gpio_pin(mrbc_vm *vm, const mrbc_value *value, uint32_t *pin)
{
  bool label = false;
  switch (mrbc_type(*value)) {
  case MRBC_TT_INTEGER:
    if (mrbc_integer(*value) < 0) return rbos_require_status(vm, RBOS_INVALID_PIN);
    if ((uint64_t)mrbc_integer(*value) > UINT32_MAX) return rbos_require_status(vm, RBOS_INVALID_PIN);
    *pin = (uint32_t)mrbc_integer(*value);
    break;
  case MRBC_TT_STRING:
    if (!rbos_pin_parse((const char *)value->string->data, value->string->size, pin)) {
      mrbc_raise(vm, MRBC_CLASS(ArgumentError), "Expected P<port>.<pin>");
      return false;
    }
    break;
  case MRBC_TT_SYMBOL: label = true; break;
  default:
    mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected Integer, String or Symbol pin");
    return false;
  }
  if (!device || !device->pin_validate || (label && !device->pin_lookup))
    return rbos_require_status(vm, RBOS_UNSUPPORTED);
  if (label) {
    const char *name = mrbc_symid_to_str(value->sym_id);
    enum rbos_status status = name ? device->pin_lookup(device->context, name, pin) : RBOS_INVALID_PIN;
    if (status == RBOS_INVALID_PIN) {
      mrbc_raise(vm, MRBC_CLASS(ArgumentError), "Unknown board pin");
      return false;
    }
    if (!rbos_require_status(vm, status)) return false;
  }
  return rbos_require_status(vm, device->pin_validate(device->context, *pin));
}

static int slot(mrbc_vm *vm, uint32_t pin)
{
  int index = state(pin);
  if (index >= 0) return index;
  for (unsigned int i = 0; i < 64; ++i)
    if (!pins[i].mode && !pins[i].claimed) return i;
  rbos_require_status(vm, RBOS_BUSY);
  return -1;
}

bool rbos_gpio_claim(mrbc_vm *vm, uint32_t pin)
{
  int index = slot(vm, pin);
  if (index < 0) return false;
  if (pins[index].claimed) return rbos_require_status(vm, RBOS_BUSY);
  pins[index].pin = pin;
  pins[index].claimed = true;
  return true;
}

void rbos_gpio_release(uint32_t pin)
{
  int index = state(pin);
  if (index >= 0) memset(&pins[index], 0, sizeof(pins[index]));
}

void rbos_gpio_unclaim(uint32_t pin)
{
  int index = state(pin);
  if (index >= 0) pins[index].claimed = false;
}

static bool configure(mrbc_vm *vm, uint32_t pin, uint32_t requested, bool constructor)
{
  int index = slot(vm, pin);
  if (index < 0) return false;
  uint32_t mode;
  if (!rbos_gpio_mode(constructor ? 0 : pins[index].mode, requested, &mode)) {
    mrbc_raise(vm, MRBC_CLASS(ArgumentError), "Invalid GPIO mode");
    return false;
  }
  if (pins[index].claimed) return rbos_require_status(vm, RBOS_BUSY);
  if (!device->gpio_configure) return rbos_require_status(vm, RBOS_UNSUPPORTED);
  if (!rbos_require_status(vm, device->gpio_configure(device->context, pin, mode))) return false;
  pins[index].pin = pin;
  pins[index].mode = mode;
  return true;
}

static bool number(mrbc_vm *vm, const mrbc_value *value, uint32_t *mode)
{
  mrbc_int_t integer;
  if (!rbos_require_integer(vm, value, 0, INT_MAX, &integer)) return false;
  *mode = integer;
  return true;
}

static bool receiver(mrbc_vm *vm, mrbc_value *value, uint32_t *pin)
{
  if (mrbc_type(*value) != MRBC_TT_OBJECT || value->instance->cls != gpio_class) {
    mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected GPIO instance");
    return false;
  }
  mrbc_value stored = mrbc_instance_getiv(value, pin_sym);
  bool valid = rbos_gpio_pin(vm, &stored, pin);
  mrbc_decref(&stored);
  return valid;
}

static bool class_receiver(mrbc_vm *vm, const mrbc_value *value)
{
  if (mrbc_type(*value) == MRBC_TT_CLASS && value->cls == gpio_class) return true;
  mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected GPIO class");
  return false;
}

static void gpio_new(mrbc_vm *vm, mrbc_value v[], int argc)
{
  uint32_t pin, mode, checked;
  if (!rbos_require_argc(vm, argc, 2, 2) || !MRBC_KW_END() ||
      !class_receiver(vm, &v[0]) || !number(vm, &v[2], &mode)) return;
  if (!rbos_gpio_mode(0, mode, &checked)) {
    mrbc_raise(vm, MRBC_CLASS(ArgumentError), "GPIO direction is required");
    return;
  }
  if (!rbos_gpio_pin(vm, &v[1], &pin)) return;
  mrbc_value object = mrbc_instance_new(vm, gpio_class, 0);
  if (!object.instance) return;
  mrbc_value stored = mrbc_integer_value(pin);
  mrbc_instance_setiv(&object, pin_sym, &stored);
  if (!configure(vm, pin, mode, true)) { mrbc_decref(&object); return; }
  rbos_return_owned(&v[0], object);
}

static void setmode(mrbc_vm *vm, mrbc_value v[], int argc)
{
  bool at = mrbc_type(v[0]) == MRBC_TT_CLASS;
  uint32_t pin, mode;
  if (!rbos_require_argc(vm, argc, at ? 2 : 1, at ? 2 : 1) || !MRBC_KW_END() ||
      !number(vm, &v[at ? 2 : 1], &mode)) return;
  if (at ? (!class_receiver(vm, &v[0]) || !rbos_gpio_pin(vm, &v[1], &pin)) :
           !receiver(vm, &v[0], &pin)) return;
  if (configure(vm, pin, mode, false)) SET_NIL_RETURN();
}

static void read_pin(mrbc_vm *vm, mrbc_value v[], int argc, int predicate, bool at)
{
  uint32_t pin, level;
  if (!rbos_require_argc(vm, argc, at ? 1 : 0, at ? 1 : 0) || !MRBC_KW_END()) return;
  if (at ? (!class_receiver(vm, &v[0]) || !rbos_gpio_pin(vm, &v[1], &pin)) :
           !receiver(vm, &v[0], &pin)) return;
  int index = state(pin);
  if (index < 0 || (!pins[index].claimed && (pins[index].mode == RBOS_GPIO_HIGH_Z))) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "GPIO input is not configured");
    return;
  }
  if (!device->gpio_read) { rbos_require_status(vm, RBOS_UNSUPPORTED); return; }
  if (!rbos_require_status(vm, device->gpio_read(device->context, pin, &level))) return;
  if (level > 1) { rbos_require_status(vm, RBOS_IO_ERROR); return; }
  if (predicate >= 0) { SET_BOOL_RETURN(level == (uint32_t)predicate); }
  else { SET_INT_RETURN(level); }
}

#define READ_METHOD(name, predicate, at) \
  static void name(mrbc_vm *vm, mrbc_value v[], int argc) { read_pin(vm, v, argc, predicate, at); }
READ_METHOD(read, -1, false)
READ_METHOD(high, 1, false)
READ_METHOD(low, 0, false)
READ_METHOD(read_at, -1, true)
READ_METHOD(high_at, 1, true)
READ_METHOD(low_at, 0, true)

static void write_pin(mrbc_vm *vm, mrbc_value v[], int argc, bool at)
{
  uint32_t pin;
  mrbc_int_t level;
  if (!rbos_require_argc(vm, argc, at ? 2 : 1, at ? 2 : 1) || !MRBC_KW_END() ||
      !rbos_require_integer(vm, &v[at ? 2 : 1], 0, 1, &level)) return;
  if (at ? (!class_receiver(vm, &v[0]) || !rbos_gpio_pin(vm, &v[1], &pin)) :
           !receiver(vm, &v[0], &pin)) return;
  int index = state(pin);
  if (index >= 0 && pins[index].claimed) { rbos_require_status(vm, RBOS_BUSY); return; }
  if (index < 0 || !(pins[index].mode & RBOS_GPIO_OUT)) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "GPIO is not an output");
    return;
  }
  if (!device->gpio_write) { rbos_require_status(vm, RBOS_UNSUPPORTED); return; }
  if (rbos_require_status(vm, device->gpio_write(device->context, pin, level))) SET_NIL_RETURN();
}

static void write(mrbc_vm *vm, mrbc_value v[], int argc) { write_pin(vm, v, argc, false); }
static void write_at(mrbc_vm *vm, mrbc_value v[], int argc) { write_pin(vm, v, argc, true); }

void rbos_gpio_define(const struct rbos_backend *backend)
{
  device = backend;
  memset(pins, 0, sizeof(pins));
  pin_sym = mrbc_str_to_symid("@pin");
  gpio_class = mrbc_define_class(NULL, "GPIO", NULL);
  const char *names[] = { "IN", "OUT", "HIGH_Z", "PULL_UP", "PULL_DOWN", "OPEN_DRAIN" };
  for (unsigned int i = 0; i < 6; ++i) {
    mrbc_value value = mrbc_integer_value(1u << i);
    mrbc_set_class_const(gpio_class, mrbc_str_to_symid(names[i]), &value);
  }
  mrbc_define_method(NULL, gpio_class, "new", gpio_new);
  mrbc_define_method(NULL, gpio_class, "setmode", setmode);
  mrbc_define_method(NULL, gpio_class, "read", read);
  mrbc_define_method(NULL, gpio_class, "high?", high);
  mrbc_define_method(NULL, gpio_class, "low?", low);
  mrbc_define_method(NULL, gpio_class, "write", write);
  mrbc_define_method(NULL, gpio_class, "read_at", read_at);
  mrbc_define_method(NULL, gpio_class, "high_at?", high_at);
  mrbc_define_method(NULL, gpio_class, "low_at?", low_at);
  mrbc_define_method(NULL, gpio_class, "write_at", write_at);
}
