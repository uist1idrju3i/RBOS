#include "rbos/native.h"
#include "backend.h"
#include "rbos/bindings.h"

extern const uint8_t rbos_adc_lifetime_worker[];
static mrbc_tcb *adc_worker;

static void adc_done(mrbc_vm *vm, mrbc_value v[], int argc)
{
  SET_BOOL_RETURN(adc_worker && adc_worker->state == TASKSTATE_DORMANT);
}

static void adc_active(mrbc_vm *vm, mrbc_value v[], int argc)
{
  SET_BOOL_RETURN(rbos_wasm_adc_active());
}

static void adc_time(mrbc_vm *vm, mrbc_value v[], int argc)
{
  const struct rbos_backend *backend = rbos_wasm_backend();
  SET_INT_RETURN(backend->uptime_ms(backend->context));
}

static void adc_spawn(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  if (adc_worker) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "ADC fixture worker still exists");
    return;
  }
  adc_worker = mrbc_create_task(rbos_adc_lifetime_worker, NULL);
  if (!adc_worker) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "ADC fixture worker creation failed");
    return;
  }
  SET_INT_RETURN(adc_worker->vm.vm_id);
}

static void adc_delete(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  if (!adc_worker) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "ADC fixture worker missing");
    return;
  }
  if (adc_worker->state != TASKSTATE_DORMANT) {
    mrbc_terminate_task(adc_worker);
    mrbc_vm_end(&adc_worker->vm);
  }
  mrbc_delete_task(adc_worker);
  mrbc_raw_free(adc_worker);
  adc_worker = NULL;
  SET_NIL_RETURN();
}

static void adc_configure(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_int_t raw, status, delay, stop;
  if (!rbos_require_argc(vm, argc, 4, 4) || !MRBC_KW_END() ||
      !rbos_require_integer(vm, &v[1], INT32_MIN, INT32_MAX, &raw) ||
      !rbos_require_integer(vm, &v[2], RBOS_OK, RBOS_TIMEOUT, &status) ||
      !rbos_require_integer(vm, &v[3], 0, 10000, &delay) ||
      !rbos_require_integer(vm, &v[4], 0, 10000, &stop)) return;
  rbos_wasm_adc_configure(raw, status, delay, stop);
  SET_NIL_RETURN();
}

static void adc_calls(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  SET_INT_RETURN(rbos_wasm_adc_calls());
}

static void adc_input(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  SET_INT_RETURN(rbos_wasm_adc_input());
}

static void adc_service(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  rbos_bindings_service();
  SET_NIL_RETURN();
}

static void temperature_configure(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_int_t value, status;
  if (!rbos_require_argc(vm, argc, 2, 2) ||
      !rbos_require_integer(vm, &v[1], INT32_MIN, INT32_MAX, &value) ||
      !rbos_require_integer(vm, &v[2], RBOS_OK, RBOS_TIMEOUT + 1, &status)) return;
  rbos_wasm_temperature_configure(value, (enum rbos_status)status);
  SET_NIL_RETURN();
}

static void temperature_available(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_int_t available;
  if (!rbos_require_argc(vm, argc, 1, 1) ||
      !rbos_require_integer(vm, &v[1], 0, 1, &available)) return;
  rbos_wasm_temperature_available(available);
  SET_NIL_RETURN();
}

static void temperature_calls(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  SET_INT_RETURN(rbos_wasm_temperature_calls());
}

static void memory_used(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  struct MRBC_ALLOC_STATISTICS stats;
  mrbc_alloc_statistics(&stats);
  SET_INT_RETURN(stats.used);
}

static enum rbos_status status;
static unsigned int calls;

static enum rbos_status fake_read(mrbc_int_t input, mrbc_int_t *output)
{
  ++calls;
  if (status == RBOS_OK) *output = input;
  return status;
}

static void sample(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_int_t input, output;
  if (!rbos_require_argc(vm, argc, 1, 1) ||
      !rbos_require_integer(vm, &v[1], -100, 100, &input)) return;
  if (!rbos_require_status(vm, fake_read(input, &output))) return;
  SET_INT_RETURN(output);
}

static void set_failure(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_int_t input;
  if (!rbos_require_argc(vm, argc, 1, 1) ||
      !rbos_require_integer(vm, &v[1], 0, 4, &input)) return;
  status = (enum rbos_status)input;
  SET_NIL_RETURN();
}

static void call_count(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  SET_INT_RETURN(calls);
}

static void optional(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 1)) return;
  SET_INT_RETURN(argc);
}

static void echo(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 1, 1)) return;
  rbos_return_borrowed(&v[0], &v[1]);
}

static void itself(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  rbos_return_borrowed(&v[0], &v[0]);
}

static void fresh(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  mrbc_value string = mrbc_string_new_cstr(vm, "native");
  if (!string.string) return;
  rbos_return_owned(&v[0], string);
}

static void ownership(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0)) return;
  struct MRBC_ALLOC_STATISTICS before, after;
  mrbc_alloc_statistics(&before);
  for (int i = 0; i < 500; ++i) {
    mrbc_value string = mrbc_string_new_cstr(vm, "native");
    mrbc_value array = mrbc_array_new(vm, 0);
    if (!string.string || !array.array) return;
    mrbc_value slot = mrbc_nil_value();
    rbos_return_owned(&slot, array);
    rbos_return_borrowed(&slot, &string);
    rbos_return_borrowed(&slot, &slot);
    mrbc_decref(&slot);
    mrbc_decref(&string);
  }
  mrbc_alloc_statistics(&after);
  if (before.used != after.used) {
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "Native reference leak");
    return;
  }
  SET_TRUE_RETURN();
}

void rbos_wasm_native_fixture_define(void)
{
  mrbc_class *cls = mrbc_define_class(NULL, "NativeFixture", NULL);
  mrbc_define_method(NULL, cls, "adc_spawn", adc_spawn);
  mrbc_define_method(NULL, cls, "adc_delete", adc_delete);
  mrbc_define_method(NULL, cls, "adc_done", adc_done);
  mrbc_define_method(NULL, cls, "adc_active", adc_active);
  mrbc_define_method(NULL, cls, "adc_time", adc_time);
  mrbc_define_method(NULL, cls, "adc_configure", adc_configure);
  mrbc_define_method(NULL, cls, "adc_calls", adc_calls);
  mrbc_define_method(NULL, cls, "adc_input", adc_input);
  mrbc_define_method(NULL, cls, "adc_service", adc_service);
  mrbc_define_method(NULL, cls, "temperature_configure", temperature_configure);
  mrbc_define_method(NULL, cls, "temperature_available=", temperature_available);
  mrbc_define_method(NULL, cls, "temperature_calls", temperature_calls);
  mrbc_define_method(NULL, cls, "memory_used", memory_used);
  mrbc_define_method(NULL, cls, "sample", sample);
  mrbc_define_method(NULL, cls, "failure=", set_failure);
  mrbc_define_method(NULL, cls, "calls", call_count);
  mrbc_define_method(NULL, cls, "optional", optional);
  mrbc_define_method(NULL, cls, "echo", echo);
  mrbc_define_method(NULL, cls, "itself", itself);
  mrbc_define_method(NULL, cls, "fresh", fresh);
  mrbc_define_method(NULL, cls, "ownership", ownership);
}
