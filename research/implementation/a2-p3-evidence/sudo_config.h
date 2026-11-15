struct VM;
void uncaught(struct VM *vm);
#define MRBC_ABORT_BY_EXCEPTION(vm) uncaught(vm)
