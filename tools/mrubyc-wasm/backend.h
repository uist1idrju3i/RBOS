#ifndef RBOS_WASM_BACKEND_H
#define RBOS_WASM_BACKEND_H

#include "rbos/backend.h"

const struct rbos_backend *rbos_wasm_backend(void);
void rbos_wasm_temperature_configure(int32_t quarter_celsius, enum rbos_status status);
void rbos_wasm_temperature_available(int available);
unsigned int rbos_wasm_temperature_calls(void);
void rbos_wasm_adc_configure(int32_t raw, enum rbos_status status, uint32_t delay_ms,
                              uint32_t stop_ms);
unsigned int rbos_wasm_adc_calls(void);
int rbos_wasm_adc_input(void);
int rbos_wasm_adc_active(void);

#endif
