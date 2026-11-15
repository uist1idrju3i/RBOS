#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mrubyc.h"
#include "bytecode_empty.c"
#include "bytecode_mutation.c"
#include "bytecode_lifetime.c"
#include "bytecode_lifetime_consumer.c"
#include "bytecode_wrong_magic.c"
#include "bytecode_wrong_version.c"

static uint8_t heap[1024 * 1024];
static unsigned int uncaught_exceptions;

static void require(int condition, const char *message)
{
  if (condition) return;
  fprintf(stderr, "FAIL: %s\n", message);
  exit(1);
}

void wasm_uncaught_exception(struct VM *vm)
{
  ++uncaught_exceptions;
  mrbc_print_vm_exception(vm);
  mrbc_decref_empty(&vm->exception);
}

static int inside(const void *pointer, size_t length, const uint8_t *blob, size_t size)
{
  uintptr_t address = (uintptr_t)pointer;
  uintptr_t start = (uintptr_t)blob;
  return address >= start && address - start <= size && length <= size - (address - start);
}

static unsigned int check_irep(const mrbc_irep *irep, const uint8_t *blob, size_t size)
{
  require(irep != NULL, "missing IREP");
  require(inside(irep->inst, irep->ilen + sizeof(mrbc_irep_catch_handler) * irep->clen, blob, size),
          "IREP instructions/catch table outside const blob");
  require(inside(irep->pool, 2, blob, size), "IREP pool outside const blob");
  unsigned int catch_handlers = irep->clen;
  for (unsigned int i = 0; i < irep->rlen; ++i) {
    catch_handlers += check_irep(mrbc_irep_child_irep(irep, i), blob, size);
  }
  return catch_handlers;
}

static void check_unchanged(const uint8_t *blob, const uint8_t *before, size_t size)
{
  const volatile uint8_t *bytes = blob;
  for (size_t i = 0; i < size; ++i) {
    require(bytes[i] == before[i], "const bytecode blob changed");
  }
}

static unsigned int run_fixture(const uint8_t *blob, size_t size)
{
  uint8_t *before = malloc(size);
  require(before != NULL, "snapshot allocation failed");
  memcpy(before, blob, size);
  mrbc_tcb *task = mrbc_create_task(blob, NULL);
  require(task != NULL, "const task creation failed");
  unsigned int catch_handlers = check_irep(task->vm.top_irep, blob, size);
  require(mrbc_run() == 0 && uncaught_exceptions == 0, "const task execution failed");
  check_unchanged(blob, before, size);
  require(task->state == TASKSTATE_DORMANT, "const task did not finish");
  require(mrbc_delete_task(task) == 0, "const task deletion failed");
  mrbc_raw_free(task);
  free(before);
  return catch_handlers;
}

static void check_retained_symbol(void)
{
  const char *name = mrbc_symid_to_str(mrbc_str_to_symid("retained_bytecode_probe"));
  require(inside(name, strlen(name) + 1, bytecode_lifetime, sizeof(bytecode_lifetime)),
          "retained symbol does not reference producer blob");
}

int main(void)
{
  mrbc_init(heap, sizeof(heap));
  run_fixture(bytecode_empty, sizeof(bytecode_empty));
  puts("PASS: const empty Ruby accepted");
  require(run_fixture(bytecode_mutation, sizeof(bytecode_mutation)) > 0,
          "const fixture has no catch table");
  puts("PASS: const nonempty catch table inside blob");
  puts("PASS: const blob unchanged after String mutation");

  uint8_t before[sizeof(bytecode_lifetime)];
  memcpy(before, bytecode_lifetime, sizeof(before));
  run_fixture(bytecode_lifetime, sizeof(bytecode_lifetime));
  check_retained_symbol();
  run_fixture(bytecode_lifetime_consumer, sizeof(bytecode_lifetime_consumer));
  check_retained_symbol();
  check_unchanged(bytecode_lifetime, before, sizeof(before));
  puts("PASS: const symbol and method retained after producer deletion");

  require(mrbc_create_task(bytecode_wrong_magic, NULL) == NULL, "bad magic accepted");
  puts("PASS: const bad magic task rejected");
  require(mrbc_create_task(bytecode_wrong_version, NULL) == NULL, "bad version accepted");
  puts("PASS: const bad version task rejected");

  for (unsigned int i = 0; i < MAX_VM_COUNT; ++i) {
    require(mrbc_create_task(bytecode_empty, NULL) != NULL, "premature VM ID exhaustion");
  }
  require(mrbc_create_task(bytecode_empty, NULL) == NULL, "VM ID exhaustion not rejected");
  puts("PASS: task creation refused on VM ID exhaustion");
  return 0;
}
