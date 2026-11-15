#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "symbol.c"
#include "bytecode_empty.c"
#include "button_bytecode.c"
#include "alloc.c"

static uint8_t heap[1024 * 1024];
static unsigned int baseline_used, baseline_blocks;
enum { RITE_STRING = 0, RITE_STATIC_STRING = 2, RITE_CATCH_SIZE = 13 };

struct ram_layout {
  size_t irep, symbols, records;
  const char *literal;
  size_t literal_size;
};

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

static void measure_irep(const mrbc_irep *irep, const uint8_t *blob, size_t size,
                         struct ram_layout *layout)
{
  require(irep != NULL);
  require(irep->inst >= blob && irep->inst <= blob + size);
  require(irep->ilen + RITE_CATCH_SIZE * irep->clen <= (size_t)(blob + size - irep->inst));
  require(irep->pool >= blob && irep->pool <= blob + size - 2);
  unsigned int pools = bin_to_uint16(irep->pool);
  layout->records++;
  layout->irep += sizeof(*irep) + pools * sizeof(uint16_t) + irep->rlen * sizeof(mrbc_irep *);
  layout->symbols += irep->ofs_pools;
  require(irep->ofs_ireps >= irep->ofs_pools + pools * sizeof(uint16_t));
  for (unsigned int i = 0; i < pools; i++) {
    const uint8_t *entry = mrbc_irep_pool_ptr(irep, i);
    require(entry >= blob && entry <= blob + size - 3);
    if (*entry == RITE_STRING || *entry == RITE_STATIC_STRING) {
      size_t length = bin_to_uint16(entry + 1);
      require(length + 4 <= (size_t)(blob + size - entry));
      if (layout->literal == NULL) {
        layout->literal = (const char *)entry + 3;
        layout->literal_size = length;
      }
    }
  }
  for (unsigned int i = 0; i < irep->rlen; i++) {
    measure_irep(mrbc_irep_child_irep(irep, i), blob, size, layout);
  }
}

static void report(const char *fixture, const char *stage, size_t tcb, size_t regs,
                   size_t irep, size_t symbols, size_t other)
{
  struct MRBC_ALLOC_STATISTICS stat;
  mrbc_alloc_statistics(&stat);
  size_t overhead = (blocks() - baseline_blocks) * sizeof(USED_BLOCK);
  size_t payload = tcb + regs + irep + symbols + other;
  require(stat.used >= baseline_used + payload + overhead);
  size_t padding = stat.used - baseline_used - payload - overhead;
  printf("RAM: Wasm stage=%s used=%u baseline=%u IREP_payload=%zu register=%zu "
         "symbol_table_pool=%zu symbol_table_static=%zu TCB=%zu other_payload=%zu "
         "allocator_overhead=%zu padding=%zu fixture=%s\n", stage, stat.used, baseline_used,
         irep, regs, symbols, sizeof(sym_index), tcb, other, overhead, padding, fixture);
}

int main(int argc, char **argv)
{
  const char *fixture = argc == 2 ? argv[1] : "empty";
  require(argc <= 2 && (!strcmp(fixture, "empty") || !strcmp(fixture, "button")));
  int product = !strcmp(fixture, "button");
  const uint8_t *blob = product ? rbos_button_bytecode : bytecode_empty;
  size_t blob_size = product ? sizeof(rbos_button_bytecode) : sizeof(bytecode_empty);
  uint8_t snapshot[blob_size];
  memcpy(snapshot, blob, blob_size);
  mrbc_init(heap, sizeof(heap));
  struct MRBC_ALLOC_STATISTICS stat;
  mrbc_alloc_statistics(&stat);
  baseline_used = stat.used;
  baseline_blocks = blocks();
  report(fixture, "init", 0, 0, 0, 0, 0);
  const int count = 32;
  mrbc_tcb *task = mrbc_tcb_new(count, TASKSTATE_DORMANT, 128);
  require(task != NULL);
  size_t regs = count * sizeof(mrbc_value);
  report(fixture, "tcb", sizeof(*task), regs, 0, 0, 0);
  require(mrbc_vm_open(&task->vm) != NULL);
  require(mrbc_load_mrb(&task->vm, blob) == 0);
  require(task->vm.flag_permanence == 0);
  mrbc_irep *irep = task->vm.top_irep;
  struct ram_layout layout = {0};
  measure_irep(irep, blob, blob_size, &layout);
  if (product) {
    require(layout.records > 1 && layout.symbols > 0 && layout.literal_size > 0);
  } else {
    require(irep->rlen == 0 && irep->ofs_pools == 0 && irep->ofs_ireps == 0);
    layout.literal = "seed";
    layout.literal_size = 4;
  }
  report(fixture, "load", sizeof(*task), regs, layout.irep, layout.symbols, 0);
  mrbc_vm_begin(&task->vm);
  report(fixture, "begin", sizeof(*task), regs, layout.irep, layout.symbols, sizeof(mrbc_instance));
  mrbc_value string = mrbc_string_new(&task->vm, layout.literal, layout.literal_size);
  require(string.string != NULL && string.string->size == layout.literal_size);
  require(memcmp(string.string->data, layout.literal, layout.literal_size) == 0);
  report(fixture, "string_new", sizeof(*task), regs, layout.irep, layout.symbols,
         sizeof(mrbc_instance) + sizeof(mrbc_string) + layout.literal_size + 1);
  require(mrbc_string_append_cbuf(&string, "01234567890123456789012345678901", 32) == 0);
  require(string.string->size == layout.literal_size + 32);
  require(memcmp(string.string->data, layout.literal, layout.literal_size) == 0);
  require(memcmp(string.string->data + layout.literal_size, "01234567890123456789012345678901", 32) == 0);
  report(fixture, "string_changed", sizeof(*task), regs, layout.irep, layout.symbols,
         sizeof(mrbc_instance) + sizeof(mrbc_string) + layout.literal_size + 33);
  mrbc_decref(&string);
  mrbc_vm_end(&task->vm);
  mrbc_vm_close(&task->vm);
  mrbc_raw_free(task);
  require(memcmp(snapshot, blob, blob_size) == 0);
  puts("PASS: Wasm RAM stages and accounting");
  return 0;
}
