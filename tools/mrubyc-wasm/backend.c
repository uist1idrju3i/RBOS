#include <stddef.h>

#include "backend.h"

const struct rbos_backend *rbos_wasm_backend(void)
{
  static const struct rbos_backend backend = { .context = NULL };
  return &backend;
}
