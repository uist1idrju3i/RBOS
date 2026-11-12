#include <string.h>
#include <limits.h>
#include "rbos/adc.h"
#include "rbos/bindings.h"
#include "rbos/native.h"
#include "rbos/button.h"

extern const uint8_t rbos_adc_bytecode[];
static struct rbos_adc adc;
static mrbc_class *adc_class;
static mrbc_class *request_class;
static mrbc_sym input_sym;
static mrbc_value lease;
static bool voltage;

void rbos_bindings_service(void)
{
  rbos_button_service();
  rbos_adc_service(&adc);
  if (!adc.active) mrbc_decref_empty(&lease);
}

static bool receiver(mrbc_vm *vm, mrbc_value *value)
{
  if (mrbc_type(*value) == MRBC_TT_OBJECT && value->instance->cls == adc_class)
    return true;
  mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected ADC instance");
  return false;
}

static bool selector(mrbc_vm *vm, const mrbc_value *value, enum rbos_adc_input *input)
{
  if (!rbos_require_type(vm, value, MRBC_TT_SYMBOL)) return false;
  const char *name = mrbc_symid_to_str(value->sym_id);
  if (name && !strcmp(name, "dvdd")) *input = RBOS_ADC_DVDD;
  else if (name && !strcmp(name, "avdd")) *input = RBOS_ADC_AVDD;
  else if (name && !strcmp(name, "vdd")) *input = RBOS_ADC_VDD;
  else {
    mrbc_raise(vm, MRBC_CLASS(ArgumentError), "Unknown internal ADC input");
    return false;
  }
  return true;
}

static void internal(mrbc_vm *vm, mrbc_value v[], int argc)
{
  enum rbos_adc_input input;
  if (!rbos_require_argc(vm, argc, 1, 1) || !MRBC_KW_END() ||
      !rbos_require_type(vm, &v[0], MRBC_TT_CLASS) ||
      !selector(vm, &v[1], &input)) return;
  if (v[0].cls != adc_class) {
    mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected ADC class");
    return;
  }
  mrbc_value object = mrbc_instance_new(vm, adc_class, 0);
  mrbc_instance_setiv(&object, input_sym, &v[1]);
  rbos_return_owned(&v[0], object);
}

static void adc_new(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 1, INT_MAX) || !MRBC_KW_END()) return;
  mrbc_raise(vm, MRBC_CLASS(NotImplementedError), "External ADC pins are not implemented");
}

static void request_new(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_raise(vm, MRBC_CLASS(TypeError), "ADC requests cannot be instantiated");
}

static void start(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 1, 1) || !MRBC_KW_END() || !receiver(vm, &v[0])) return;
  if (mrbc_type(v[1]) != MRBC_TT_TRUE && mrbc_type(v[1]) != MRBC_TT_FALSE) {
    mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected boolean");
    return;
  }
#if !MRBC_USE_FLOAT
  if (mrbc_type(v[1]) == MRBC_TT_TRUE) {
    mrbc_raise(vm, MRBC_CLASS(NotImplementedError), "ADC voltage requires Float");
    return;
  }
#endif
  enum rbos_adc_input input;
  mrbc_value source = mrbc_instance_getiv(&v[0], input_sym);
  bool valid = selector(vm, &source, &input);
  mrbc_decref(&source);
  if (!valid) return;
  rbos_bindings_service();
  if (adc.active) {
    rbos_require_status(vm, RBOS_BUSY);
    return;
  }
  /* VM-independent allocation and a native reference prevent VM-ID/pointer ABA. */
  mrbc_value request = mrbc_instance_new(NULL, request_class, 0);
  if (!rbos_require_status(vm, rbos_adc_start(&adc, input))) {
    mrbc_decref(&request);
    return;
  }
  lease = request;
  mrbc_incref(&lease);
  voltage = mrbc_type(v[1]) == MRBC_TT_TRUE;
  rbos_return_owned(&v[0], request);
}

static bool request_argument(mrbc_vm *vm, const mrbc_value *request)
{
  if (mrbc_type(*request) == MRBC_TT_OBJECT && request->instance->cls == request_class)
    return true;
  mrbc_raise(vm, MRBC_CLASS(TypeError), "Expected ADC request");
  return false;
}

static bool current(const mrbc_value *request)
{
  return adc.active && mrbc_type(lease) == MRBC_TT_OBJECT &&
         request->instance == lease.instance;
}

static void poll(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 1, 1) || !MRBC_KW_END() ||
      !receiver(vm, &v[0]) || !request_argument(vm, &v[1])) return;
  rbos_bindings_service();
  if (!current(&v[1])) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "ADC request expired or timed out");
    return;
  }
  struct rbos_adc_sample sample;
  enum rbos_status status = rbos_adc_take(&adc, adc.token, &sample);
  if (status == RBOS_PENDING) { SET_NIL_RETURN(); return; }
  rbos_bindings_service();
  if (!rbos_require_status(vm, status)) return;
#if MRBC_USE_FLOAT
  if (voltage) {
    SET_FLOAT_RETURN((mrbc_float_t)sample.raw * sample.full_scale_uv /
                     ((mrbc_float_t)(1u << sample.bits) * 1000000));
    return;
  }
#endif
  SET_INT_RETURN(sample.raw);
}

static void finish(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 1, 1) || !MRBC_KW_END() ||
      !receiver(vm, &v[0]) || !request_argument(vm, &v[1])) return;
  if (current(&v[1])) rbos_adc_cancel(&adc, adc.token);
  rbos_bindings_service();
  SET_NIL_RETURN();
}

void rbos_adc_define(const struct rbos_backend *backend)
{
  adc.backend = backend;
  adc_class = mrbc_define_class(NULL, "ADC", NULL);
  request_class = mrbc_define_class(NULL, "RBOSADCRequest", NULL);
  input_sym = mrbc_str_to_symid("@input");
  mrbc_define_method(NULL, adc_class, "internal", internal);
  mrbc_define_method(NULL, adc_class, "new", adc_new);
  mrbc_define_method(NULL, adc_class, "__start", start);
  mrbc_define_method(NULL, adc_class, "__poll", poll);
  mrbc_define_method(NULL, adc_class, "__finish", finish);
  mrbc_define_method(NULL, request_class, "new", request_new);
  if (mrbc_run_mrblib(rbos_adc_bytecode) != 1) hal_abort("ADC library load failed\n");
}
