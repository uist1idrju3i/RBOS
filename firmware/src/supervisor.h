#ifndef RBOS_SUPERVISOR_H
#define RBOS_SUPERVISOR_H
#include <stdbool.h>
#include "mrubyc.h"

int rbos_supervisor_start(void);
void rbos_supervisor_poll(bool idle);
int __wrap_mrbc_vm_run(mrbc_vm *vm);
#endif
