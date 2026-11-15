#ifndef A2_PROBE_HAL_H
#define A2_PROBE_HAL_H
#ifndef SUDO_TIMER_STYLE
#define MRBC_NO_TIMER
#endif
#define MRBC_TICK_UNIT 1
#define MRBC_TIMESLICE_TICK_COUNT 10
#define MRBC_SCHEDULER_EXIT 1
void mrbc_hal_init(void);
void mrbc_hal_enable_irq(void);
void mrbc_hal_disable_irq(void);
void mrbc_hal_idle_cpu(void);
int mrbc_hal_write(int fd, const void *buf, int nbytes);
int mrbc_hal_flush(int fd);
_Noreturn void mrbc_hal_abort(const char *message);
#endif
