#ifndef RBOS_GPIO_H
#define RBOS_GPIO_H

#include <stddef.h>
#include "rbos/native.h"

enum rbos_gpio_mode {
  RBOS_GPIO_IN = 1, RBOS_GPIO_OUT = 2, RBOS_GPIO_HIGH_Z = 4,
  RBOS_GPIO_PULL_UP = 8, RBOS_GPIO_PULL_DOWN = 16, RBOS_GPIO_OPEN_DRAIN = 32,
};

bool rbos_pin_parse(const char *name, size_t length, uint32_t *pin);
bool rbos_gpio_mode(uint32_t previous, uint32_t requested, uint32_t *mode);
bool rbos_gpio_pin(mrbc_vm *vm, const mrbc_value *value, uint32_t *pin);
bool rbos_gpio_claim(mrbc_vm *vm, uint32_t pin);
void rbos_gpio_unclaim(uint32_t pin);
void rbos_gpio_release(uint32_t pin);
void rbos_gpio_define(const struct rbos_backend *backend);

#endif
