#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mrubyc.h"

extern const uint8_t priority_code[], untrusted_code[], trusted_code[];
static uint8_t pool[1024 * 1024];
static mrbc_tcb *observed, *system_task;
static int dormant_observations, priority_calls, denied_calls, privileged_calls;
static int original_service_calls;
static mrbc_func_t original_priority;
static mrbc_class *task_class;

static void require(int condition, const char *message)
{
  if (!condition) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
  }
}

void mrbc_hal_init(void) {}
void mrbc_hal_disable_irq(void) {}
void mrbc_hal_enable_irq(void)
{
  if (observed && observed->state == TASKSTATE_DORMANT) dormant_observations++;
}
void mrbc_hal_idle_cpu(void) { mrbc_tick(); }
int mrbc_hal_write(int fd, const void *buf, int nbytes)
{
  return fwrite(buf, 1, nbytes, fd == 2 ? stderr : stdout);
}
int mrbc_hal_flush(int fd) { return fflush(fd == 2 ? stderr : stdout); }
_Noreturn void mrbc_hal_abort(const char *message)
{
  fprintf(stderr, "ABORT: %s\n", message ? message : "none");
  exit(90);
}

static void checked_priority(mrbc_vm *vm, mrbc_value v[], int argc)
{
  mrbc_tcb *target = mrbc_type(v[0]) == MRBC_TT_CLASS ? mrbc_get_tcb(vm) :
                    *(mrbc_tcb **)v[0].instance->data;
  require(target == mrbc_get_tcb(vm), "priority wrapper caller/target");
  priority_calls++;
  original_priority(vm, v, argc);
}

static void native_service(mrbc_vm *vm, mrbc_value v[], int argc)
{
  (void)vm;
  (void)argc;
  original_service_calls++;
  SET_INT_RETURN(1);
}

static void privileged_mark(mrbc_vm *vm, mrbc_value v[], int argc)
{
  (void)argc;
  if (vm != &system_task->vm) {
    denied_calls++;
    mrbc_raise(vm, MRBC_CLASS(RuntimeError), "System task only");
    return;
  }
  privileged_calls++;
  SET_NIL_RETURN();
}

static mrbc_tcb *create(const void *code, int priority)
{
  mrbc_tcb *tcb = mrbc_tcb_new(MAX_REGS_SIZE, TASKSTATE_READY, priority);
  require(tcb && mrbc_create_task(code, tcb), "task creation");
  return tcb;
}

int main(void)
{
  mrbc_init(pool, sizeof(pool));
  task_class = mrbc_get_const(mrbc_str_to_symid("Task"))->cls;
  mrbc_method method;
  require(mrbc_find_method(&method, task_class, mrbc_str_to_symid("priority=")) &&
          method.c_func == 2, "builtin priority lookup");
  original_priority = method.func;
  puts("PASS builtin callback captured before shadow");
  mrbc_define_method(NULL, task_class, "priority=", checked_priority);
  require(mrbc_find_method(&method, task_class, mrbc_str_to_symid("priority=")) &&
          method.func == checked_priority, "shadow takes precedence");

  mrbc_tcb *task = create(priority_code, 128);
  observed = task;
  mrbc_value old_handle = mrbc_immediate_value(MRBC_TT_CLASS, .cls = task_class);
  require(mrbc_find_method(&method, task_class, mrbc_str_to_symid("get")) != NULL,
          "get callback lookup");
  method.func(&task->vm, &old_handle, 0);
  require(*(mrbc_tcb **)old_handle.instance->data == task, "get instance payload");
  require(mrbc_run() == 0 && task->priority == 33 && priority_calls == 1,
          "Ruby priority fixture");
  puts("PASS shadowed priority= delegates saved builtin (get/list/current)");
  require(task->state == TASKSTATE_DORMANT && dormant_observations > 0,
          "mrbc_run completion observation");
  puts("PASS normal completion observed via HAL enable callback");

  observed = NULL;
  require(!task->vm.flag_need_memfree, "embedded VM storage ownership");
  require(mrbc_delete_task(task) == 0, "delete first lifetime");
  memset(task, 0, sizeof(*task) + sizeof(mrbc_value) * MAX_REGS_SIZE);
  task->vm.regs_size = MAX_REGS_SIZE;
  task->state = TASKSTATE_READY;
  task->priority = 128;
  require(mrbc_create_task(priority_code, task) == task, "reuse TCB storage");
  mrbc_value status_args = old_handle;
  mrbc_incref(&status_args);
  require(mrbc_find_method(&method, task_class, mrbc_str_to_symid("status")) != NULL,
          "status callback lookup");
  method.func(&task->vm, &status_args, 0);
  require(!strcmp(mrbc_string_cstr(&status_args), "READY"), "old handle sees new lifetime");
  mrbc_decref(&status_args);
  puts("REPRODUCED old pointer-only Task handle resolves new lifetime after explicit TCB storage reuse");
  observed = task;
  dormant_observations = 0;
  extern int mrbc_run_step(void);
  int steps = 0;
  while (task->state != TASKSTATE_DORMANT && steps++ < 1000) mrbc_run_step();
  require(task->state == TASKSTATE_DORMANT && dormant_observations > 0 && priority_calls == 2,
          "mrbc_run_step completion observation");
  puts("PASS Emscripten run_step completion observed via HAL enable callback");
  observed = NULL;
  mrbc_decref(&old_handle);
  require(mrbc_delete_task(task) == 0, "delete second lifetime");
  mrbc_raw_free(task);

  mrbc_class *system = mrbc_define_class(NULL, "RBOSSystem", MRBC_CLASS(Object));
  mrbc_define_method(NULL, system, "service", native_service);
  mrbc_class *privileged = mrbc_define_class(NULL, "Privileged", MRBC_CLASS(Object));
  mrbc_define_method(NULL, privileged, "mark", privileged_mark);
  system_task = create(trusted_code, 128);
  create(untrusted_code, 1);
  require(mrbc_run() == 0, "shared method fixture completion");
  require(denied_calls == 1, "direct user call denied");
  puts("PASS direct user privileged call denied");
  require(privileged_calls == 1 && original_service_calls == 0,
          "redefined service runs privileged callback as system VM");
  puts("REPRODUCED user-defined RBOSSystem.service executes privileged callback as system VM");
  return 0;
}
