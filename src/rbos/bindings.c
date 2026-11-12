#include "rbos/bindings.h"
#include "rbos/native.h"

static const struct rbos_backend *device;

static void temperature_read(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!rbos_require_argc(vm, argc, 0, 0) ||
      !MRBC_KW_END() ||
      !rbos_require_type(vm, &v[0], MRBC_TT_CLASS)) return;
#if MRBC_USE_FLOAT
  if (!device || !device->temperature_read) {
    rbos_require_status(vm, RBOS_IO_ERROR);
    return;
  }
  int32_t quarter_celsius;
  if (!rbos_require_status(vm, device->temperature_read(device->context, &quarter_celsius))) return;
  SET_FLOAT_RETURN((mrbc_float_t)quarter_celsius / 4);
#else
  mrbc_raise(vm, MRBC_CLASS(NotImplementedError), "Temperature requires Float");
#endif
}

static void temperature_new(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_raise(vm, MRBC_CLASS(TypeError), "Temperature cannot be instantiated");
}

void rbos_define_classes(const struct rbos_backend *backend)
{
  device = backend;
  mrbc_class *cls = mrbc_define_class(NULL, "Temperature", NULL);
  mrbc_define_method(NULL, cls, "read", temperature_read);
  mrbc_define_method(NULL, cls, "new", temperature_new);
}
