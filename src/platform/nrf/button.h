#ifndef RBOS_NRF_BUTTON_H
#define RBOS_NRF_BUTTON_H
#include "rbos/backend.h"
enum rbos_status rbos_nrf_button_watch(void *, uint32_t, uint32_t);
enum rbos_status rbos_nrf_button_unwatch(void *, uint32_t, uint32_t);
bool rbos_nrf_button_owns(uint32_t pin);
bool rbos_nrf_event_take(void *, struct rbos_event *);
void rbos_nrf_event_stats(void *, struct rbos_event_stats *);
#endif
