#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mrubyc.h"
#include "rbos/bindings.h"
#include "backend.h"

#ifndef RBOS_WASM_POOL_SIZE
#define RBOS_WASM_POOL_SIZE (1024 * 1024)
#endif
static unsigned char heap[RBOS_WASM_POOL_SIZE];
static int uncaught_exceptions;

void wasm_uncaught_exception(struct VM *vm)
{
  ++uncaught_exceptions;
  mrbc_print_vm_exception(vm);
  mrbc_decref_empty(&vm->exception);
}

int main(int argc, char **argv)
{
  if (argc < 2) {
    fprintf(stderr, "Usage: %s file.mrb [file.mrb ...]\n", argv[0]);
    return 2;
  }
  mrbc_init(heap, sizeof(heap));
  rbos_define_classes(rbos_wasm_backend());

  for (int i = 1; i < argc; ++i) {
    FILE *file = fopen(argv[i], "rb");
    if (!file) {
      fprintf(stderr, "Cannot open bytecode: %s\n", argv[i]);
      return 2;
    }
    if (fseek(file, 0, SEEK_END) != 0) return 2;
    long size = ftell(file);
    if (size < 20 || size > 1024 * 1024 || fseek(file, 0, SEEK_SET) != 0) {
      fprintf(stderr, "Invalid bytecode size: %s\n", argv[i]);
      return 2;
    }
    unsigned char *bytes = malloc((size_t)size);
    if (!bytes || fread(bytes, 1, (size_t)size, file) != (size_t)size) return 2;
    fclose(file);
    if (memcmp(bytes, "RITE", 4) != 0) {
      fprintf(stderr, "Invalid bytecode header: %s\n", argv[i]);
      return 2;
    }
    uint32_t declared_size = ((uint32_t)bytes[8] << 24) |
                             ((uint32_t)bytes[9] << 16) |
                             ((uint32_t)bytes[10] << 8) | bytes[11];
    if (declared_size != (uint32_t)size) {
      fprintf(stderr, "Invalid declared bytecode size: %s\n", argv[i]);
      return 2;
    }
    if (!mrbc_create_task(bytes, NULL)) {
      fprintf(stderr, "Failed to load bytecode: %s\n", argv[i]);
      return 2;
    }
    // The loader keeps pointers into bytes for the lifetime of the VM.
  }

  int status = mrbc_run();
  int failed = status != 0 || uncaught_exceptions != 0;
  if (failed) fprintf(stderr, "Uncaught task exception (scheduler status %d)\n", status);
  mrbc_hal_flush(1);
  mrbc_hal_flush(2);
  return failed ? 1 : 0;
}
