from pathlib import Path
import unittest

import test_temperature


ROOT = Path(__file__).resolve().parents[2]


class RuntimeEventTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_irq_keys_atomic_snapshot_and_queue_paths(self):
        headers = {
            'mrubyc.h': '''#pragma once
#include <stdint.h>
struct MRBC_ALLOC_STATISTICS { unsigned used, total; };
void mrbc_alloc_statistics(struct MRBC_ALLOC_STATISTICS *);
''',
            'rbos/native.h': '#pragma once\n',
            'rbos/bindings.h': 'void rbos_bindings_service(void);\n',
            'bm/bm_scheduler.h': 'void bm_scheduler_process(void);\n',
            'zephyr/logging/log_ctrl.h': '#include <stdbool.h>\nbool log_process(void);\n',
            'zephyr/logging/log.h': '''#define LOG_MODULE_REGISTER(...)
void test_log(const char *, ...);
#define LOG_INF(...) test_log(__VA_ARGS__)
''',
            'zephyr/kernel.h': '''#pragma once
#include <stdint.h>
#define CONFIG_MAIN_STACK_SIZE 1024
#define CONFIG_MP_MAX_NUM_CPUS 1
#define CONFIG_ISR_STACK_SIZE 128
#define CONFIG_RBOS_STATS_INTERVAL_MS 1000
#define K_THREAD_STACK_DECLARE(name, size) extern uint8_t name[size]
#define K_KERNEL_STACK_ARRAY_DECLARE(name, count, size) extern uint8_t name[count][size]
#define K_THREAD_STACK_BUFFER(name) (name)
#define K_KERNEL_STACK_BUFFER(name) (name)
unsigned irq_lock(void);
void irq_unlock(unsigned);
uintptr_t __get_PSP(void);
uint32_t k_cycle_get_32(void);
uint32_t k_cyc_to_us_floor32(uint32_t);
int64_t k_uptime_get(void);
struct rbos_tick_stats { unsigned min_us, max_us, catchups, count; };
void rbos_tick_take_interval(struct rbos_tick_stats *);
''',
        }
        program = r'''
#include <assert.h>
#include <stdarg.h>
#define rbos_event_queue_push locked_push
#define rbos_event_queue_pop locked_pop
#include "RUNTIME_SOURCE"
#undef rbos_event_queue_push
#undef rbos_event_queue_pop
#include "QUEUE_SOURCE"
static unsigned masked, depth, locks, unlocks;
static bool inject;
uint8_t z_main_stack[1024], z_interrupt_stacks[1][128];
unsigned irq_lock(void) { unsigned previous = masked; masked = 1; ++depth; ++locks; return previous; }
void irq_unlock(unsigned key) {
  assert(depth && masked && key <= 1);
  --depth; ++unlocks; masked = key;
  if (inject && !masked) {
    inject = false;
    struct rbos_event e = { .type = RBOS_EVENT_BUTTON, .source = 123 };
    assert(rbos_event_post(&e));
    assert(rbos_event_post(&e));
    e.type = RBOS_EVENT_COMPLETION;
    for (unsigned i = 1; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) assert(rbos_event_post(&e));
    assert(!rbos_event_post(&e));
  }
}
bool locked_push(struct rbos_event_queue *q, const struct rbos_event *e) {
  assert(masked && depth); return rbos_event_queue_push(q, e);
}
bool locked_pop(struct rbos_event_queue *q, struct rbos_event *e) {
  assert(masked && depth); return rbos_event_queue_pop(q, e);
}
uintptr_t __get_PSP(void) { return 0; }
uint32_t k_cycle_get_32(void) { return 0; }
uint32_t k_cyc_to_us_floor32(uint32_t c) { return c; }
int64_t k_uptime_get(void) { return 0; }
void rbos_tick_take_interval(struct rbos_tick_stats *s) { *s = (struct rbos_tick_stats){0}; }
void mrbc_alloc_statistics(struct MRBC_ALLOC_STATISTICS *s) { *s = (struct MRBC_ALLOC_STATISTICS){0}; }
void bm_scheduler_process(void) {}
void rbos_mcumgr_poll(void) {}
void rbos_bindings_service(void) {}
bool log_process(void) { return false; }
void test_log(const char *format, ...) {}
int main(void) {
  struct rbos_event out = { .source = 999 };
  struct rbos_event_stats stats;
  assert(!rbos_event_take(&out) && out.source == 999);
  assert(locks == 1 && unlocks == 1 && !masked);
  rbos_event_snapshot(&stats);
  assert(!stats.pending && !stats.overflow && !stats.coalesced);
  unsigned key = irq_lock();
  struct rbos_event e = { .type = RBOS_EVENT_BUTTON, .source = 45, .generation = 7 };
  assert(rbos_event_post(&e) && masked && depth == 1);
  assert(rbos_event_post(&e) && masked && depth == 1);
  rbos_event_snapshot(&stats);
  assert(stats.pending == 1 && stats.coalesced == 1 && depth == 1 && masked);
  irq_unlock(key);
  assert(!masked && !depth);
  for (unsigned i = 1; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) {
    e.type = RBOS_EVENT_COMPLETION; e.source = i; assert(rbos_event_post(&e));
  }
  assert(!rbos_event_post(&e));
  rbos_event_snapshot(&stats);
  assert(stats.pending == RBOS_EVENT_QUEUE_CAPACITY && stats.overflow == 1 && stats.coalesced == 1);
  assert(rbos_event_take(&out) && out.count == 2 && out.generation == 7);
  while (rbos_event_take(&out)) {}
  inject = true;
  rbos_event_snapshot(&stats);
  assert(!stats.pending && stats.overflow == 1 && stats.coalesced == 1);
  assert(event_queue.size == RBOS_EVENT_QUEUE_CAPACITY && event_queue.overflow == 2 && event_queue.coalesced == 2);
  assert(rbos_event_take(&out) && out.source == 123 && out.count == 2);
  assert(locks == unlocks && !depth && !masked);
}
'''.replace('RUNTIME_SOURCE', str(ROOT / 'firmware/src/runtime.c')).replace(
            'QUEUE_SOURCE', str(ROOT / 'src/rbos/event_queue.c'))
        self.compile_and_run(headers, program, [])
