#ifndef RBOS_EMBEDDED_H
#define RBOS_EMBEDDED_H
#include <stdint.h>
struct rbos_embedded_task {
	const char *name;
	const uint8_t *bytecode;
};
extern const struct rbos_embedded_task rbos_tasks[];
extern const unsigned int rbos_task_count;
#endif
