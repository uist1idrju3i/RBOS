#ifndef RBOS_BINDINGS_H
#define RBOS_BINDINGS_H

#include "rbos/backend.h"

void rbos_define_classes(const struct rbos_backend *backend);
void rbos_adc_define(const struct rbos_backend *backend);
/* Foreground only, including when the requesting Ruby task no longer runs. */
void rbos_bindings_service(void);

#endif
