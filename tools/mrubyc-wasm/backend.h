#ifndef RBOS_WASM_BACKEND_H
#define RBOS_WASM_BACKEND_H

#include "rbos/backend.h"

const struct rbos_backend *rbos_wasm_backend(void);
void rbos_wasm_gpio_status(enum rbos_status status);
unsigned int rbos_wasm_gpio_calls(void);
void rbos_wasm_gpio_level(uint32_t pin, uint32_t level);
uint32_t rbos_wasm_gpio_mode(uint32_t pin);
uint32_t rbos_wasm_button_generation(uint32_t pin);
void rbos_wasm_button_edge(uint32_t pin, uint32_t level, uint32_t generation);
void rbos_wasm_event_fill(void);
void rbos_wasm_temperature_configure(int32_t quarter_celsius, enum rbos_status status);
void rbos_wasm_temperature_available(int available);
unsigned int rbos_wasm_temperature_calls(void);
void rbos_wasm_adc_configure(int32_t raw, enum rbos_status status, uint32_t delay_ms,
                              uint32_t stop_ms);
unsigned int rbos_wasm_adc_calls(void);
int rbos_wasm_adc_input(void);
int rbos_wasm_adc_active(void);

#endif
