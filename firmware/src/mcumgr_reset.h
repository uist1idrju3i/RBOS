#ifndef RBOS_MCUMGR_RESET_H
#define RBOS_MCUMGR_RESET_H

#include <stdint.h>

int rbos_mcumgr_init(void);
void rbos_mcumgr_connected(uint16_t handle);
void rbos_mcumgr_disconnected(uint16_t handle);
void rbos_mcumgr_notification_sent(uint16_t handle);
void rbos_mcumgr_poll(void);

#endif
