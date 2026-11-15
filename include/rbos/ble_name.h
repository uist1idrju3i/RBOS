#ifndef RBOS_BLE_NAME_H
#define RBOS_BLE_NAME_H

#include <stddef.h>
#include <stdint.h>

#define RBOS_BLE_NAME_MAX_PREFIX 21
#define RBOS_BLE_NAME_CAPACITY 27

void rbos_ble_device_id_bytes(uint32_t word0, uint32_t word1, uint8_t bytes[8]);
int rbos_ble_name_generate(char *name, size_t capacity, const char *prefix,
                          const uint8_t device_id[8]);

#endif
