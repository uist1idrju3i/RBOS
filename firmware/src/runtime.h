#ifndef RBOS_RUNTIME_H
#define RBOS_RUNTIME_H
#include <stdbool.h>
#include "mrubyc.h"
void rbos_stack_paint(void);
void rbos_maintenance(bool service);
void rbos_system_define(void);
void rbos_system_set_task(mrbc_tcb *task);
int rbos_ble_init(void);
#endif
