#include "rbos/native.h"

bool rbos_require_argc(mrbc_vm *vm, int argc, int minimum, int maximum)
{
  if (argc >= minimum && argc <= maximum) return true;
  mrbc_raise(vm, MRBC_CLASS(ArgumentError),
             maximum == 0 ? "Expected no arguments" : "Wrong number of arguments");
  return false;
}

bool rbos_require_type(mrbc_vm *vm, const mrbc_value *value, mrbc_vtype type)
{
  if (mrbc_type(*value) == type) return true;
  mrbc_raise(vm, MRBC_CLASS(TypeError), "Unexpected argument type");
  return false;
}

bool rbos_require_integer(mrbc_vm *vm, const mrbc_value *value,
                          mrbc_int_t minimum, mrbc_int_t maximum, mrbc_int_t *result)
{
  if (!rbos_require_type(vm, value, MRBC_TT_INTEGER)) return false;
  mrbc_int_t number = mrbc_integer(*value);
  if (number < minimum || number > maximum) {
    mrbc_raise(vm, MRBC_CLASS(RangeError), "Integer out of range");
    return false;
  }
  *result = number;
  return true;
}

bool rbos_require_status(mrbc_vm *vm, enum rbos_status status)
{
  if (status == RBOS_OK) return true;
  const char *message;
  switch (status) {
  case RBOS_BUSY: message = "Device busy"; break;
  case RBOS_TIMEOUT: message = "Device timeout"; break;
  default: message = "Driver failure"; break;
  }
  mrbc_raise(vm, MRBC_CLASS(RuntimeError), message);
  return false;
}

void rbos_return_borrowed(mrbc_value *slot, const mrbc_value *value)
{
  mrbc_value retained = *value;
  mrbc_incref(&retained);
  rbos_return_owned(slot, retained);
}

void rbos_return_owned(mrbc_value *slot, mrbc_value value)
{
  mrbc_decref(slot);
  *slot = value;
}
