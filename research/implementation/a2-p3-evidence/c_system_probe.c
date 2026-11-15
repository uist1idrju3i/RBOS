#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mrubyc.h"
#include "c_system_code.c"
#include "c_spin_code.c"
#include "c_sleep_code.c"
#include "c_block_code.c"
#include "c_error_code.c"
#include "c_empty_code.c"

#define NOINSTR __attribute__((no_instrument_function))
static uint8_t pool[1024 * 1024];
static int active, simulating, irq_depth, due, blocked;
static unsigned work, ticks, services, idle_calls, returns, last_service;
static unsigned feeds, withheld, denied, user_writes, reports;
static unsigned admin_led, blocked_withheld;
static const char *mode;

static void NOINSTR simulate_irq(void)
{
  ++ticks;
  mrbc_tick();
  due = 1;
  if (ticks - last_service <= 25) ++feeds;
  else ++withheld;
  if (!strcmp(mode, "idle-only") && ticks == 200) {
    assert(services == 0 && idle_calls == 0 && withheld > 0);
    puts("PASS idle-only: timer preemption does not execute idle or foreground service for always-ready Ruby");
    exit(0);
  }
}

void NOINSTR __cyg_profile_func_enter(void *fn, void *caller)
{
  (void)fn;
  (void)caller;
  if (!active || simulating || irq_depth || blocked) return;
  simulating = 1;
  if (++work == 100) { work = 0; simulate_irq(); }
  simulating = 0;
}
void NOINSTR __cyg_profile_func_exit(void *fn, void *caller)
{ (void)fn; (void)caller; }

static void NOINSTR maintenance(void)
{
  if (!active || !due) return;
  due = 0;
  ++services;
  ++admin_led;
  last_service = ticks;
  if (!strcmp(mode, "spin") && services == 30) {
    assert(idle_calls == 0 && returns >= 30 && withheld == 0);
    puts("PASS spin: wrapped mrbc_vm_run returns to native maintenance without Ruby yield or idle");
    exit(0);
  }
}

int __real_mrbc_vm_run(mrbc_vm *vm);
int NOINSTR __wrap_mrbc_vm_run(mrbc_vm *vm)
{
  int ret = __real_mrbc_vm_run(vm);
  if (active) {
    ++returns;
    if (strcmp(mode, "idle-only")) maintenance();
  }
  return ret;
}
void mrbc_hal_init(void) {}
void mrbc_hal_disable_irq(void) { ++irq_depth; }
void mrbc_hal_enable_irq(void) { assert(irq_depth > 0); --irq_depth; }
void NOINSTR mrbc_hal_idle_cpu(void)
{
  ++idle_calls;
  simulating = 1;
  simulate_irq();
  simulating = 0;
  maintenance();
}
int mrbc_hal_write(int fd, const void *buf, int count)
{ return fwrite(buf, 1, count, fd == 2 ? stderr : stdout); }
int mrbc_hal_flush(int fd) { return fflush(fd == 2 ? stderr : stdout); }
_Noreturn void mrbc_hal_abort(const char *message)
{ fprintf(stderr, "ABORT %s\n", message ? message : "none"); exit(90); }

static void write_pin(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (argc != 1 || mrbc_type(v[1]) != MRBC_TT_INTEGER || v[1].i != 1) {
    ++denied;
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "C policy: reserved pin");
    return;
  }
  ++user_writes;
  SET_NIL_RETURN();
}
static void report(mrbc_vm *vm, mrbc_value v[], int argc)
{ (void)vm; (void)argc; ++reports; SET_NIL_RETURN(); }
static void NOINSTR blocking_native(mrbc_vm *vm, mrbc_value v[], int argc)
{
  (void)vm; (void)argc;
  unsigned before = services, missed = withheld;
  blocked = 1;
  for (int i = 0; i < 80; ++i) simulate_irq();
  blocked = 0;
  assert(before == services && withheld > missed);
  blocked_withheld = withheld - missed;
  SET_NIL_RETURN();
}

int main(int argc, char **argv)
{
  assert(argc == 2);
  mode = argv[1];
  const void *code;
  if (!strcmp(mode, "normal")) code = c_system_code;
  else if (!strcmp(mode, "spin") || !strcmp(mode, "idle-only")) code = c_spin_code;
  else if (!strcmp(mode, "sleep")) code = c_sleep_code;
  else if (!strcmp(mode, "block")) code = c_block_code;
  else if (!strcmp(mode, "error")) code = c_error_code;
  else { assert(!strcmp(mode, "empty")); code = c_empty_code; }
  mrbc_init(pool, sizeof(pool));
  mrbc_class *cls = mrbc_define_class(NULL, "Probe", NULL);
  mrbc_define_method(NULL, cls, "write", write_pin);
  mrbc_define_method(NULL, cls, "report", report);
  mrbc_define_method(NULL, cls, "block", blocking_native);
  mrbc_tcb *task = mrbc_create_task(code, NULL);
  assert(task);
  active = 1;
  int status = mrbc_run();
  active = 0;
  assert(task->state == TASKSTATE_DORMANT);
  if (!strcmp(mode, "normal")) {
    assert(status == 0 && denied == 1 && user_writes == 1 && reports == 1);
    assert(services > 0 && admin_led == services);
    puts("PASS normal: user replacement executes only as user; reserved native operation denied; C-only supervisor unaffected");
  } else if (!strcmp(mode, "sleep")) {
    assert(status == 0 && reports == 1 && idle_calls > 0 && services > 0);
    puts("PASS sleep: native idle maintenance advances sleeping user");
  } else if (!strcmp(mode, "block")) {
    assert(status == 0 && reports == 1 && blocked_withheld > 0);
    puts("PASS block: timer cannot preempt native callback; stale foreground heartbeat withholds simulated watchdog feed");
  } else if (!strcmp(mode, "error")) {
    assert(status == 2);
    puts("PASS error: uncaught user exception returns error to native owner");
  } else {
    assert(!strcmp(mode, "empty") && status == 0);
    puts("PASS empty: empty user program completes under native ownership");
  }
  printf("evidence mode=%s ticks=%u returns=%u service=%u idle=%u feeds=%u withheld=%u\n",
         mode, ticks, returns, services, idle_calls, feeds, withheld);
  return 0;
}
