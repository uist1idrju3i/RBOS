#ifndef RBOS_HAL_H
#define RBOS_HAL_H
#define MRBC_TICK_UNIT 1
#define MRBC_TIMESLICE_TICK_COUNT 10
#define MRBC_SCHEDULER_EXIT 1
#define MRBC_OUT_OF_MEMORY() mrbc_hal_abort("Ruby pool exhausted\n")
void mrbc_hal_init(void);
void mrbc_hal_enable_irq(void);
void mrbc_hal_disable_irq(void);
void mrbc_hal_idle_cpu(void);
int mrbc_hal_write(int fd, const void *buf, int nbytes);
int mrbc_hal_flush(int fd);
_Noreturn void mrbc_hal_abort(const char *message);
#define hal_init() mrbc_hal_init()
#define hal_enable_irq() mrbc_hal_enable_irq()
#define hal_disable_irq() mrbc_hal_disable_irq()
#define hal_idle_cpu() mrbc_hal_idle_cpu()
#define hal_write(fd, buf, n) mrbc_hal_write(fd, buf, n)
#define hal_flush(fd) mrbc_hal_flush(fd)
#define hal_abort(s) mrbc_hal_abort(s)
struct rbos_tick_stats {
	unsigned int min_us;
	unsigned int max_us;
	unsigned int catchups;
};
void rbos_tick_snapshot(struct rbos_tick_stats *stats);
#endif
