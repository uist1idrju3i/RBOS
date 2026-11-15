#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <zephyr/sys/crc.h>
#include "rbos/ble_name.h"

void rbos_ble_device_id_bytes(uint32_t word0, uint32_t word1, uint8_t bytes[8])
{
	for (unsigned int i = 0; i < 4; ++i) {
		bytes[i] = word1 >> (24 - 8 * i);
		bytes[4 + i] = word0 >> (24 - 8 * i);
	}
}

int rbos_ble_name_generate(char *name, size_t capacity, const char *prefix,
                          const uint8_t device_id[8])
{
	if (!name || !prefix || !device_id) return -EINVAL;
	size_t length = strlen(prefix);
	if (!length || length > RBOS_BLE_NAME_MAX_PREFIX) return -EINVAL;
	if (capacity < length + 6) return -ENOSPC;
	uint16_t crc = crc16_reflect(0x9eb2, 0xffff, device_id, 8);
	int result = snprintf(name, capacity, "%s_%04X", prefix, (unsigned int)crc);
	return result < 0 ? -EIO : 0;
}
