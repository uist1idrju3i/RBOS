#ifndef RBOS_NRF_ADC_H
#define RBOS_NRF_ADC_H
#include "rbos/backend.h"
uint32_t rbos_nrf_uptime_ms(void *context);
enum rbos_status rbos_nrf_adc_start(void *context, enum rbos_adc_input input, uint32_t token);
enum rbos_status rbos_nrf_adc_poll(void *context, uint32_t token, struct rbos_adc_sample *sample);
void rbos_nrf_adc_cancel(void *context, uint32_t token);
#endif
