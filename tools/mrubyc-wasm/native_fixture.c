#include "rbos/native.h"

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
  mrbc_define_method(NULL, cls, "sample", sample);
  mrbc_define_method(NULL, cls, "failure=", set_failure);
  mrbc_define_method(NULL, cls, "calls", call_count);
  mrbc_define_method(NULL, cls, "optional", optional);
  mrbc_define_method(NULL, cls, "echo", echo);
  mrbc_define_method(NULL, cls, "itself", itself);
  mrbc_define_method(NULL, cls, "fresh", fresh);
  mrbc_define_method(NULL, cls, "ownership", ownership);
}
