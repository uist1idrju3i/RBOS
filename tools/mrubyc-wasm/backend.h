#ifndef RBOS_WASM_BACKEND_H
#define RBOS_WASM_BACKEND_H

#include "rbos/backend.h"

const struct rbos_backend *rbos_wasm_backend(void);
void rbos_wasm_temperature_configure(int32_t quarter_celsius, enum rbos_status status);
void rbos_wasm_temperature_available(int available);
unsigned int rbos_wasm_temperature_calls(void);

#endif
