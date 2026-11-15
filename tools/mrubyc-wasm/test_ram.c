#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol.c"
#include "bytecode_empty.c"
#include "alloc.c"

static uint8_t heap[1024 * 1024];
static unsigned int baseline_used, baseline_blocks;

void wasm_uncaught_exception(struct VM *vm)
{
  mrbc_print_vm_exception(vm);
  exit(1);
}

static void require(int condition)
{
  if (!condition) {
    fputs("FAIL: RAM accounting\n", stderr);
    exit(1);
  }
}

static unsigned int blocks(void)
{
  unsigned int count = 0;
  USED_BLOCK *block = BPOOL_TOP(memory_pool);
  while (block < (USED_BLOCK *)BPOOL_END(memory_pool)) {
    count += !!IS_USED_BLOCK(block);
    block = PHYS_NEXT(block);
  }
  return count;
}

static void report(const char *stage, size_t tcb, size_t regs, size_t irep, size_t other)
{
  struct MRBC_ALLOC_STATISTICS stat;
  mrbc_alloc_statistics(&stat);
  size_t overhead = (blocks() - baseline_blocks) * sizeof(USED_BLOCK);
  size_t payload = tcb + regs + irep + other;
  require(stat.used >= baseline_used + payload + overhead);
  size_t padding = stat.used - baseline_used - payload - overhead;
  printf("RAM: Wasm stage=%s used=%u baseline=%u IREP_payload=%zu register=%zu "
         "symbol_table_pool=0 symbol_table_static=%zu TCB=%zu other_payload=%zu "
         "allocator_overhead=%zu padding=%zu\n", stage, stat.used, baseline_used,
         irep, regs, sizeof(sym_index), tcb, other, overhead, padding);
}

int main(void)
{
  mrbc_init(heap, sizeof(heap));
  struct MRBC_ALLOC_STATISTICS stat;
  mrbc_alloc_statistics(&stat);
  baseline_used = stat.used;
  baseline_blocks = blocks();
  report("init", 0, 0, 0, 0);
  const int count = 32;
  mrbc_tcb *task = mrbc_tcb_new(count, TASKSTATE_DORMANT, 128);
  require(task != NULL);
  size_t regs = count * sizeof(mrbc_value);
  report("tcb", sizeof(*task), regs, 0, 0);
  require(mrbc_vm_open(&task->vm) != NULL);
  require(mrbc_load_mrb(&task->vm, bytecode_empty) == 0);
  mrbc_irep *irep = task->vm.top_irep;
  require(irep->rlen == 0 && irep->ofs_pools == 0 && irep->ofs_ireps == 0);
  report("load", sizeof(*task), regs, sizeof(*irep), 0);
  mrbc_vm_begin(&task->vm);
  report("begin", sizeof(*task), regs, sizeof(*irep), sizeof(mrbc_instance));
  mrbc_value string = mrbc_string_new_cstr(&task->vm, "seed");
  require(string.string != NULL && string.string->size == 4);
  report("string_new", sizeof(*task), regs, sizeof(*irep),
         sizeof(mrbc_instance) + sizeof(mrbc_string) + 5);
  require(mrbc_string_append_cbuf(&string, "01234567890123456789012345678901", 32) == 0);
  require(string.string->size == 36 && memcmp(string.string->data, "seed0123", 8) == 0);
  report("string_changed", sizeof(*task), regs, sizeof(*irep),
         sizeof(mrbc_instance) + sizeof(mrbc_string) + 37);
  mrbc_decref(&string);
  mrbc_vm_end(&task->vm);
  mrbc_vm_close(&task->vm);
  mrbc_raw_free(task);
  puts("PASS: Wasm RAM stages and accounting");
  return 0;
}
