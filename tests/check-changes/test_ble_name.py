import unittest

import test_temperature


def openblink_crc(data):
    table = []
    for byte in range(256):
        value = byte
        for _ in range(8):
            value = (value >> 1) ^ (0x9EB2 if value & 1 else 0)
        table.append(value)
    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ table[(crc ^ byte) & 0xFF]
    return crc


class BleNameTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_zephyr_order_openblink_crc_known_vectors_and_errors(self):
        known = [('0000000000000000', '51F1'), ('0001020304050607', '223F'),
                 ('0123456789abcdef', '3F1B'), ('ffffffffffffffff', 'C404')]
        for data, expected in known:
            self.assertEqual(f'{openblink_crc(bytes.fromhex(data)):04X}', expected)
        vectors = [bytes.fromhex(data) for data, _ in known]
        vectors += [bytes((index * 17 + offset * 29) % 256 for offset in range(8))
                    for index in range(64)]
        cases = '\n'.join('{' + ','.join(str(byte) for byte in data) + '},' for data in vectors)
        names = ','.join(f'"RBOS_{openblink_crc(data):04X}"' for data in vectors)
        header = '''#include <stdint.h>
#include <stddef.h>
uint16_t crc16_reflect(uint16_t, uint16_t, const uint8_t *, size_t);
'''
        program = r'''
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <string.h>
#include "rbos/ble_name.h"
uint16_t crc16_reflect(uint16_t poly,uint16_t seed,const uint8_t *src,size_t len) {
  assert(poly==0x9eb2 && seed==0xffff && len==8);
  uint16_t crc=seed;
  for (size_t i=0;i<len;++i) {
    crc^=src[i];
    for (int j=0;j<8;++j) crc=(crc&1) ? (crc>>1)^poly : crc>>1;
  }
  return crc;
}
static const uint8_t vectors[][8]={CASES};
static const char *names[]={NAMES};
int main(void) {
  uint8_t bytes[8];
  rbos_ble_device_id_bytes(0x89abcdef,0x01234567,bytes);
  assert(!memcmp(bytes,vectors[2],8));
  char name[RBOS_BLE_NAME_CAPACITY];
  for (size_t i=0;i<sizeof(vectors)/sizeof(vectors[0]);++i) {
    assert(rbos_ble_name_generate(name,sizeof(name),"RBOS",vectors[i])==0);
    assert(!strcmp(name,names[i]));
  }
  assert(rbos_ble_name_generate(name,10,"TEST",bytes)==0 && !strcmp(name,"TEST_3F1B"));
  assert(rbos_ble_name_generate(name,sizeof(name),"123456789012345678901",bytes)==0);
  assert(strlen(name)==26);
  strcpy(name,"unchanged");
  assert(rbos_ble_name_generate(name,9,"RBOS",bytes)==-ENOSPC);
  assert(rbos_ble_name_generate(name,0,"RBOS",bytes)==-ENOSPC);
  assert(rbos_ble_name_generate(name,sizeof(name),"",bytes)==-EINVAL);
  assert(rbos_ble_name_generate(name,sizeof(name),"1234567890123456789012",bytes)==-EINVAL);
  assert(rbos_ble_name_generate(name,sizeof(name),NULL,bytes)==-EINVAL);
  assert(rbos_ble_name_generate(name,sizeof(name),"RBOS",NULL)==-EINVAL);
  assert(rbos_ble_name_generate(NULL,sizeof(name),"RBOS",bytes)==-EINVAL);
  assert(!strcmp(name,"unchanged"));
}
'''.replace('CASES', cases).replace('NAMES', names)
        self.compile_and_run({'zephyr/sys/crc.h': header}, program, ['firmware/src/ble_name.c'])
