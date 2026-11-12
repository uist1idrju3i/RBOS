#ifndef RBOS_NATIVE_H
#define RBOS_NATIVE_H

#include <stdbool.h>
#include "mrubyc.h"

enum rbos_status {
  RBOS_OK,
  RBOS_IO_ERROR,
  RBOS_BUSY,
  RBOS_TIMEOUT,
};

/* A false result leaves an exception; the callback must return immediately. */
bool rbos_require_argc(mrbc_vm *vm, int argc, int minimum, int maximum);
bool rbos_require_type(mrbc_vm *vm, const mrbc_value *value, mrbc_vtype type);
bool rbos_require_integer(mrbc_vm *vm, const mrbc_value *value,
                          mrbc_int_t minimum, mrbc_int_t maximum, mrbc_int_t *result);
bool rbos_require_status(mrbc_vm *vm, enum rbos_status status);

/* Borrowed values retain their owner's reference, including when slot == value. */
void rbos_return_borrowed(mrbc_value *slot, const mrbc_value *value);
/* Transfer one owned reference; the caller must not decref it afterwards. */
void rbos_return_owned(mrbc_value *slot, mrbc_value value);

#endif
