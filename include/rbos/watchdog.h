#ifndef RBOS_WATCHDOG_H
#define RBOS_WATCHDOG_H

int rbos_wdt_start(void);
void rbos_wdt_feed(void);
void rbos_wdt_stop(void);
void rbos_reset_reason_log(void);

#endif
