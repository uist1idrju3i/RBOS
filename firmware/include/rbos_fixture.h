#ifndef RBOS_FIXTURE_H
#define RBOS_FIXTURE_H

#include <stdbool.h>
#include <stdint.h>

#if defined(CONFIG_RBOS_SATURATION_FIXTURE)
#include <zephyr/devicetree.h>
#define RBOS_FIXTURE_PIN DT_PROP(DT_ALIAS(sw0), pin)
int rbos_fixture_connect(uint32_t task_address);
void rbos_fixture_disconnect(void);
void rbos_fixture_begin(uint32_t pin, uint32_t generation);
void rbos_fixture_irq(void);
void rbos_fixture_edge(uint32_t pin, uint32_t level, bool accepted);
void rbos_fixture_delivery(uint32_t pin, uint32_t level, uint32_t count);
bool rbos_fixture_holds_events(void);
void rbos_fixture_poll(void);
#endif

#if defined(CONFIG_RBOS_RETENTION_FIXTURE)
void rbos_retention_start(void);
void rbos_retention_poll(void);
#endif

#endif
