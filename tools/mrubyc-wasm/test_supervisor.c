#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "supervisor.h"
#include "c_spin_code.c"
#include "c_sleep_code.c"
#include "c_error_code.c"
#include "c_empty_code.c"
#ifdef RBOS_BOUNDARY_TEST
#include "rbos/bindings.h"
#include "backend.h"
#include "management_boundary.c"
static unsigned boundary_reports, boundary_first_poll;
#endif

#define NOINSTR __attribute__((no_instrument_function))
static uint8_t pool[1024 * 1024];
static unsigned ticks, calls, idle_calls, work, depth;
static int active, simulating, irq_depth;
static const char *mode;
extern unsigned rbos_wasm_wdt_feeds;
extern int rbos_wasm_wdt_error;

int64_t NOINSTR k_uptime_get(void) { return ticks; }

static void NOINSTR tick(void)
{
  ++ticks;
  mrbc_tick();
#ifdef RBOS_SUPERVISOR_CONTROL
  if (!strcmp(mode, "spin") && ticks == 500) {
    assert(calls == 0 && idle_calls == 0);
    puts("PASS supervisor: no-wrap always-ready control has zero maintenance calls");
    exit(0);
  }
#endif
}

void NOINSTR __cyg_profile_func_enter(void *fn, void *caller)
{
  (void)fn;
  (void)caller;
  if (!active || simulating || irq_depth) return;
  simulating = 1;
  if (++work == 100) { work = 0; tick(); }
  simulating = 0;
}

void NOINSTR __cyg_profile_func_exit(void *fn, void *caller)
{ (void)fn; (void)caller; }

void NOINSTR rbos_maintenance(bool idle)
{
  assert(active && depth == 0);
  ++depth;
  ++calls;
  if (idle) ++idle_calls;
  unsigned before = calls;
  unsigned feeds = rbos_wasm_wdt_feeds;
  ticks += CONFIG_RBOS_SERVICE_INTERVAL_MS;
  if (!strcmp(mode, "stall")) ticks += CONFIG_RBOS_WDT_TIMEOUT_MS;
  rbos_supervisor_poll(!idle);
  assert(calls == before && rbos_wasm_wdt_feeds == feeds);
  --depth;
#ifdef RBOS_BOUNDARY_TEST
  if (!strcmp(mode, "boundary") && boundary_reports && calls >= boundary_first_poll + 30) {
    assert(boundary_reports == 1 && rbos_wasm_gpio_calls() == 0);
    assert(rbos_wasm_button_generation(73) == 0 && rbos_wasm_adc_active() == 0);
    puts("PASS supervisor: Ruby management redefinition gains no permission; native owner progresses");
    exit(0);
  }
#endif
  if (!strcmp(mode, "spin") && calls >= 30) {
    assert(idle_calls == 0);
    puts("PASS supervisor: always-ready user loop reaches 30 native polls without reentry");
    exit(0);
  }
}

#ifdef RBOS_SUPERVISOR_CONTROL
int __real_mrbc_vm_run(mrbc_vm *vm) { return mrbc_vm_run(vm); }
#endif

void mrbc_hal_init(void) {}
void mrbc_hal_disable_irq(void) { ++irq_depth; }
void mrbc_hal_enable_irq(void) { assert(irq_depth > 0); --irq_depth; }
void NOINSTR mrbc_hal_idle_cpu(void)
{
  tick();
  rbos_supervisor_poll(true);
}
int mrbc_hal_write(int fd, const void *buf, int count)
{ return fwrite(buf, 1, count, fd == 2 ? stderr : stdout); }
int mrbc_hal_flush(int fd) { return fflush(fd == 2 ? stderr : stdout); }
_Noreturn void mrbc_hal_abort(const char *message)
{ fprintf(stderr, "ABORT %s\n", message); exit(90); }
static void report(mrbc_vm *vm, mrbc_value v[], int argc)
{
  (void)vm; (void)argc;
#ifdef RBOS_BOUNDARY_TEST
  ++boundary_reports;
  boundary_first_poll = calls;
#endif
  SET_NIL_RETURN();
}

int main(int argc, char **argv)
{
  assert(argc == 2);
  mode = argv[1];
  if (!strcmp(mode, "stall") || !strcmp(mode, "start-error")) {
    active = 1;
    if (!strcmp(mode, "start-error")) {
      rbos_wasm_wdt_error = -1;
      assert(rbos_supervisor_start() == -1);
      rbos_supervisor_poll(true);
      assert(calls == 0 && rbos_wasm_wdt_feeds == 0);
      puts("PASS watchdog: failed start leaves supervisor disabled");
    } else {
      assert(rbos_supervisor_start() == 0);
      rbos_supervisor_poll(true);
      assert(calls == 1 && rbos_wasm_wdt_feeds == 0);
      rbos_supervisor_poll(true);
      assert(calls == 2 && rbos_wasm_wdt_feeds == 0);
      puts("PASS watchdog: stalled native maintenance never feeds or revives expired watchdog");
    }
    return 0;
  }
  const void *code;
#ifdef RBOS_BOUNDARY_TEST
  if (!strcmp(mode, "boundary")) code = management_boundary;
  else
#endif
  if (!strcmp(mode, "spin")) code = c_spin_code;
  else if (!strcmp(mode, "sleep")) code = c_sleep_code;
  else if (!strcmp(mode, "error")) code = c_error_code;
  else { assert(!strcmp(mode, "empty")); code = c_empty_code; }
  mrbc_init(pool, sizeof(pool));
#ifdef RBOS_BOUNDARY_TEST
  rbos_define_classes(rbos_wasm_backend());
#endif
  rbos_supervisor_poll(true);
  assert(calls == 0);
  mrbc_class *cls = mrbc_define_class(NULL, "Probe", NULL);
  mrbc_define_method(NULL, cls, "report", report);
  mrbc_tcb *task = mrbc_create_task(code, NULL);
  assert(task);
  active = 1;
  assert(rbos_supervisor_start() == 0);
  int status = mrbc_run();
  assert(status == (!strcmp(mode, "error") ? 2 : 0));
  assert(task->state == TASKSTATE_DORMANT);
  if (!strcmp(mode, "sleep")) assert(idle_calls > 0);
  unsigned before = calls;
  for (int i = 0; i < 5; ++i) {
    ticks += CONFIG_RBOS_SERVICE_INTERVAL_MS;
    rbos_supervisor_poll(true);
  }
  assert(calls == before + 5 && depth == 0);
  assert(rbos_wasm_wdt_feeds == calls);
  printf("PASS supervisor: %s returns to persistent native owner, init disabled, no reentry\n", mode);
  return 0;
}
