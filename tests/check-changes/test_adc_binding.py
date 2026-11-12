import unittest
import test_temperature


class ADCFloatDisabledTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_float_disabled_rejects_voltage_but_allows_raw_start(self):
        headers = {"mrubyc.h": r'''#ifndef TEST_MRBC_H
#define TEST_MRBC_H
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
typedef int32_t mrbc_int_t;
typedef int mrbc_vtype;
typedef int mrbc_sym;
typedef struct mrbc_class { int id; } mrbc_class;
typedef struct instance { mrbc_class *cls; } instance;
typedef struct value { int tt; int32_t i; mrbc_sym sym_id;
                       mrbc_class *cls; instance *instance; } mrbc_value;
typedef struct VM { const char *error; } mrbc_vm;
enum { MRBC_TT_EMPTY, MRBC_TT_CLASS, MRBC_TT_OBJECT, MRBC_TT_SYMBOL,
       MRBC_TT_TRUE, MRBC_TT_FALSE, MRBC_TT_INTEGER, MRBC_TT_HASH };
typedef void (*callback)(mrbc_vm *, mrbc_value *, int);
#define MRBC_CLASS(name) #name
#define mrbc_type(v) ((v).tt)
#define mrbc_integer(v) ((v).i)
#define SET_NIL_RETURN() ((void)0)
#define SET_INT_RETURN(n) ((void)(n))
#define MRBC_KW_END() ((v[argc+1].tt == MRBC_TT_HASH && v[argc+1].i) ? \
                     (mrbc_raise(vm, "ArgumentError", "keyword"), 0) : 1)
static inline void mrbc_incref(mrbc_value *v) { (void)v; }
static inline void mrbc_decref(mrbc_value *v) { (void)v; }
static inline void mrbc_decref_empty(mrbc_value *v) { v->tt = MRBC_TT_EMPTY; }
void mrbc_raise(mrbc_vm *, const char *, const char *);
mrbc_class *mrbc_define_class(mrbc_vm *, const char *, mrbc_class *);
void mrbc_define_method(mrbc_vm *, mrbc_class *, const char *, callback);
mrbc_value mrbc_instance_new(mrbc_vm *, mrbc_class *, int);
void mrbc_instance_setiv(mrbc_value *, mrbc_sym, mrbc_value *);
mrbc_value mrbc_instance_getiv(mrbc_value *, mrbc_sym);
mrbc_sym mrbc_str_to_symid(const char *);
const char *mrbc_symid_to_str(mrbc_sym);
int mrbc_run_mrblib(const void *);
void hal_abort(const char *);
#endif
'''}
        program = r'''#include <assert.h>
#include <string.h>
#include "rbos/native.h"
#include "rbos/bindings.h"
static mrbc_class adc_class, req_class;
static callback start_method;
static int calls, allocations;
const uint8_t rbos_adc_bytecode[] = {0};
void mrbc_raise(mrbc_vm *vm, const char *error, const char *message) {
  (void)message;
  vm->error = error;
}
mrbc_class *mrbc_define_class(mrbc_vm *vm, const char *name, mrbc_class *parent) {
  (void)vm; (void)parent;
  return strcmp(name, "ADC") == 0 ? &adc_class : &req_class;
}
void mrbc_define_method(mrbc_vm *vm, mrbc_class *cls, const char *name, callback fn) {
  (void)vm; (void)cls;
  if (!strcmp(name, "__start")) start_method = fn;
}
mrbc_value mrbc_instance_new(mrbc_vm *vm, mrbc_class *cls, int size) {
  (void)vm; (void)size;
  static instance object;
  ++allocations;
  object.cls = cls;
  return (mrbc_value){ .tt = MRBC_TT_OBJECT, .instance = &object };
}
void mrbc_instance_setiv(mrbc_value *v, mrbc_sym s, mrbc_value *a) { (void)v;(void)s;(void)a; }
mrbc_value mrbc_instance_getiv(mrbc_value *v, mrbc_sym s) {
  (void)v; (void)s;
  return (mrbc_value){ .tt = MRBC_TT_SYMBOL, .sym_id = 1 };
}
mrbc_sym mrbc_str_to_symid(const char *s) { (void)s; return 1; }
const char *mrbc_symid_to_str(mrbc_sym s) { (void)s; return "vdd"; }
int mrbc_run_mrblib(const void *b) { (void)b; return 1; }
void hal_abort(const char *message) { (void)message; assert(0); }
static uint32_t uptime(void *c) { (void)c; return 0; }
static enum rbos_status adc_start(void *c, enum rbos_adc_input input, uint32_t token) {
  (void)c; (void)token;
  assert(input == RBOS_ADC_VDD);
  ++calls;
  return RBOS_IO_ERROR;
}
static enum rbos_status adc_poll(void *c, uint32_t token, struct rbos_adc_sample *s) {
  (void)c;(void)token;(void)s; assert(0); return RBOS_IO_ERROR;
}
static void adc_cancel(void *c, uint32_t token) { (void)c;(void)token; assert(0); }
int main(void) {
  struct rbos_backend backend = {
    .uptime_ms = uptime, .adc_start = adc_start, .adc_poll = adc_poll, .adc_cancel = adc_cancel,
  };
  rbos_adc_define(&backend);
  instance object = { .cls = &adc_class };
  mrbc_value v[3] = { { .tt = MRBC_TT_OBJECT, .instance = &object },
                       { .tt = MRBC_TT_TRUE }, {0} };
  mrbc_vm vm = {0};
  start_method(&vm, v, 1);
  assert(!strcmp(vm.error, "NotImplementedError") && !calls && !allocations);
  v[2] = (mrbc_value){ .tt = MRBC_TT_HASH, .i = 1 };
  start_method(&vm, v, 1);
  assert(!strcmp(vm.error, "ArgumentError") && !calls);
  v[2].i = 0;
  v[1].tt = MRBC_TT_INTEGER;
  start_method(&vm, v, 1);
  assert(!strcmp(vm.error, "TypeError") && !calls);
  v[1].tt = MRBC_TT_FALSE;
  start_method(&vm, v, 1);
  assert(!strcmp(vm.error, "RuntimeError") && calls == 1 && allocations == 1);
}
'''
        self.compile_and_run(headers, program,
                             ["src/rbos/adc_binding.c", "src/rbos/adc.c", "src/rbos/native.c"],
                             ["-DMRBC_USE_FLOAT=0"])
