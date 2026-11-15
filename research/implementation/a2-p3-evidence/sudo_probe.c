#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mrubyc.h"
#include "sudo_cases_code.c"
#include "sudo_child_code.c"
#include "sudo_raise_code.c"
#include "sudo_victim_code.c"

static uint8_t pool[1024 * 1024];
static struct { mrbc_tcb *task; int depth; } registry[32];
static int deaths;
static int *depth(mrbc_vm *vm)
{
  mrbc_tcb *task = mrbc_get_tcb(vm);
  for (int i=0; i<32; i++) {
    if (!registry[i].task) registry[i].task = task;
    if (registry[i].task == task) return &registry[i].depth;
  }
  abort();
}
void mrbc_hal_init(void) {}
void mrbc_hal_disable_irq(void) {}
void mrbc_hal_enable_irq(void)
{
  for (int i=0; i<32; i++) {
    if (registry[i].task && registry[i].task->state == TASKSTATE_DORMANT && registry[i].depth) {
      registry[i].depth = 0;
      deaths++;
    }
  }
}
void mrbc_hal_idle_cpu(void) { mrbc_tick(); }
int mrbc_hal_write(int fd, const void *buf, int nbytes)
{ return fwrite(buf, 1, nbytes, fd == 2 ? stderr : stdout); }
int mrbc_hal_flush(int fd) { return fflush(fd == 2 ? stderr : stdout); }
_Noreturn void mrbc_hal_abort(const char *message)
{ fprintf(stderr, "ABORT %s\n", message ? message : "none"); exit(90); }
void uncaught(struct VM *vm) { mrbc_print_vm_exception(vm); exit(91); }

static int authenticate(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (argc != 1 || mrbc_type(v[1]) != MRBC_TT_STRING ||
      strcmp(mrbc_string_cstr(&v[1]), "fixture")) {
    mrbc_raise(vm, MRBC_CLASS(ArgumentError), "fixture token rejected");
    return 0;
  }
  return 1;
}
static void enter(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!authenticate(vm, v, argc)) return;
  int ticket = ++*depth(vm);
  SET_INT_RETURN(ticket);
}
static void leave(mrbc_vm *vm, mrbc_value v[], int argc)
{
  (void)v; (void)argc;
  if (*depth(vm)) --*depth(vm);
}
static void active(mrbc_vm *vm, mrbc_value v[], int argc)
{ (void)argc; SET_BOOL_RETURN(*depth(vm) != 0); }
static void reset(mrbc_vm *vm, mrbc_value v[], int argc)
{ (void)v; (void)argc; *depth(vm) = 0; }
static void death_count(mrbc_vm *vm, mrbc_value v[], int argc)
{ (void)vm; (void)argc; SET_INT_RETURN(deaths); }
static void bytecode(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (argc != 1 || mrbc_type(v[1]) != MRBC_TT_STRING) abort();
  const char *name = mrbc_string_cstr(&v[1]);
  const void *data; int size;
  if (!strcmp(name, "child")) { data = sudo_child_code; size = sizeof(sudo_child_code); }
  else if (!strcmp(name, "raise")) { data = sudo_raise_code; size = sizeof(sudo_raise_code); }
  else { data = sudo_victim_code; size = sizeof(sudo_victim_code); }
  mrbc_value result = mrbc_string_new(vm, data, size);
  SET_RETURN(result);
}
static void native_scope(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (!authenticate(vm, v, argc)) return;
  if (mrbc_type(v[argc+1]) != MRBC_TT_PROC) abort();
  ++*depth(vm);
  mrbc_method method;
  if (!mrbc_find_method(&method, MRBC_CLASS(Proc), mrbc_str_to_symid("call"))) abort();
  mrbc_value proc = v[argc+1];
  mrbc_incref(&proc);
  mrbc_decref(&v[0]);
  v[0] = proc;
  method.func(vm, v, 0);
  --*depth(vm);
}
int main(void)
{
  mrbc_init(pool, sizeof(pool));
  mrbc_class *p = mrbc_define_class(NULL, "Privilege", NULL);
  mrbc_define_method(NULL, p, "enter", enter);
  mrbc_define_method(NULL, p, "leave", leave);
  mrbc_define_method(NULL, p, "native_scope", native_scope);
  mrbc_class *proof = mrbc_define_class(NULL, "Proof", NULL);
  mrbc_define_method(NULL, proof, "active?", active);
  mrbc_define_method(NULL, proof, "reset", reset);
  mrbc_define_method(NULL, proof, "death_revocations", death_count);
  mrbc_define_method(NULL, proof, "bytecode", bytecode);
  if (!mrbc_create_task(sudo_cases_code, NULL)) return 1;
  return mrbc_run();
}
