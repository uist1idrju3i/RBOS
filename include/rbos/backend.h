#ifndef RBOS_BACKEND_H
#define RBOS_BACKEND_H

#include <stdint.h>

enum rbos_status {
  RBOS_OK,
  RBOS_IO_ERROR,
  RBOS_BUSY,
  RBOS_TIMEOUT,
};

struct rbos_backend {
  void *context;
  /* Borrow the output until return, and write it only on RBOS_OK. */
  enum rbos_status (*temperature_read)(void *context, int32_t *quarter_celsius);
};

#endif
