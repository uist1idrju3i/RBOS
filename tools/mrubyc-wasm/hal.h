#ifndef RBOS_WASM_HAL_H
#define RBOS_WASM_HAL_H

#include_next "hal.h"
#include "rbos/bindings.h"

static inline void rbos_wasm_idle_cpu(void)
{
  rbos_bindings_service();
  mrbc_hal_idle_cpu();
}

#undef mrbc_hal_idle_cpu
#define mrbc_hal_idle_cpu() rbos_wasm_idle_cpu()

#endif
