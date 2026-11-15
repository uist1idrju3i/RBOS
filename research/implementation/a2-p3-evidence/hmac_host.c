#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <psa/crypto.h>
#include "hmac-sha256.h"

static void check(int ok, const char *name)
{
  if (!ok) { fprintf(stderr, "FAIL %s\n", name); exit(1); }
}

static void vector(int n, const unsigned char *key, size_t keylen,
                   const unsigned char *data, size_t datalen, const char *hex)
{
  unsigned char mac[32], expected[32];
  size_t size = 0, want = strlen(hex) / 2;
  for (size_t i = 0; i < want; i++) {
    unsigned value;
    sscanf(hex + i * 2, "%2x", &value);
    expected[i] = value;
  }
  psa_key_attributes_t attr = PSA_KEY_ATTRIBUTES_INIT;
  psa_set_key_type(&attr, PSA_KEY_TYPE_HMAC);
  psa_set_key_algorithm(&attr, PSA_ALG_HMAC(PSA_ALG_SHA_256));
  psa_set_key_usage_flags(&attr, PSA_KEY_USAGE_SIGN_MESSAGE | PSA_KEY_USAGE_VERIFY_MESSAGE);
  psa_key_id_t id;
  check(psa_import_key(&attr, key, keylen, &id) == PSA_SUCCESS, "PSA import");
  check(psa_mac_compute(id, PSA_ALG_HMAC(PSA_ALG_SHA_256), data, datalen,
                        mac, sizeof(mac), &size) == PSA_SUCCESS, "PSA compute");
  check(size == 32 && memcmp(mac, expected, want) == 0, "RFC expected MAC");
  check(psa_mac_verify(id, PSA_ALG_HMAC(PSA_ALG_SHA_256), data, datalen,
                       mac, size) == PSA_SUCCESS, "PSA verify");
  psa_destroy_key(id);

  hmac_sha256_key_t refkey = {0};
  refkey.len = keylen;
  memcpy(refkey.value, key, keylen > 32 ? 32 : keylen);
  hmac_sha256_hmac_t refmac = {0};
  fn_t sign = hmac_sha256_sign(&refkey, &refmac, data, datalen);
  int sign_ok = sign == kSuccess && refmac.len >= want && !memcmp(refmac.value, expected, want);
  if (refkey.id) psa_destroy_key(refkey.id);
  refkey.id = 0;
  memcpy(refmac.value, mac, 32);
  refmac.len = want;
  fn_t verify = hmac_sha256_verify(&refkey, &refmac, data, datalen);
  if (refkey.id) psa_destroy_key(refkey.id);
  printf("RFC4231 case %d: PSA=PASS original-sign=%s original-verify=%s key=%zu data=%zu\n",
         n, sign_ok ? "PASS" : "REJECT", verify == kSuccess ? "ACCEPT" : "REJECT", keylen, datalen);
}

int main(void)
{
  check(psa_crypto_init() == PSA_SUCCESS, "init");
  unsigned char key[131], data[50];
  memset(key, 0x0b, 20);
  vector(1, key, 20, (const unsigned char *)"Hi There", 8,
         "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7");
  const char *message = "what do ya want for nothing?";
  vector(2, (const unsigned char *)"Jefe", 4, (const unsigned char *)message, strlen(message),
         "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843");
  memset(key, 0xaa, 20); memset(data, 0xdd, 50);
  vector(3, key, 20, data, 50, "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe");
  for (int i=0; i<25; i++) key[i] = i+1;
  memset(data, 0xcd, 50);
  vector(4, key, 25, data, 50, "82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b");
  memset(key, 0x0c, 20);
  message = "Test With Truncation";
  vector(5, key, 20, (const unsigned char *)message, strlen(message), "a3b6167473100ee06e0c796c2955552b");
  memset(key, 0xaa, 131);
  message = "Test Using Larger Than Block-Size Key - Hash Key First";
  vector(6, key, 131, (const unsigned char *)message, strlen(message),
         "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54");
  message = "This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm.";
  vector(7, key, 131, (const unsigned char *)message, strlen(message),
         "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2");

  hmac_sha256_key_t fixed = { .len = 32 };
  memset(fixed.value, 0x25, 32);
  hmac_sha256_hmac_t mac = {0};
  message = "A valid 32-byte-key message exceeding thirty-two bytes";
  check(hmac_sha256_sign(&fixed, &mac, (const unsigned char *)message, strlen(message)) == kSuccess,
        "original valid32 sign");
  psa_destroy_key(fixed.id); fixed.id = 0;
  mac.len = 0;
  check(hmac_sha256_verify(&fixed, &mac, (const unsigned char *)message, strlen(message)) == kSuccess,
        "original ignores mac.len");
  psa_destroy_key(fixed.id); fixed.id = 0;
  puts("REPRODUCED original verify accepts full MAC buffer with declared MAC len=0");
  mac.value[0] ^= 1;
  check(hmac_sha256_verify(&fixed, &mac, (const unsigned char *)message, strlen(message)) == kFailure,
        "modified MAC rejection");
  if (fixed.id) psa_destroy_key(fixed.id);
  puts("PASS original supported-input roundtrip and changed-MAC rejection");
  return 0;
}
