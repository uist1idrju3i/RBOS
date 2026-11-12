#ifndef RBOS_RUNTIME_H
#define RBOS_RUNTIME_H
#include <stdbool.h>
#include "mrubyc.h"
#include "rbos/event_queue.h"
/* Producers must use application IRQ priorities masked by irq_lock (NVIC 2+). */
bool rbos_event_post(const struct rbos_event *event);
/* Foreground consumer; native dispatch is added with each peripheral driver. */
bool rbos_event_take(struct rbos_event *event);
void rbos_stack_paint(void);
void rbos_maintenance(bool service);
void rbos_system_define(void);
void rbos_system_set_task(mrbc_tcb *task);
int rbos_ble_init(void);
void rbos_resources_log(void);
#endif
