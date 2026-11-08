struct VM;
void wasm_uncaught_exception(struct VM *vm);
#define MRBC_ABORT_BY_EXCEPTION(vm) wasm_uncaught_exception(vm)
