#ifndef RBOS_EVENT_QUEUE_H
#define RBOS_EVENT_QUEUE_H

#include <stdbool.h>
#include <stdint.h>

#define RBOS_EVENT_QUEUE_CAPACITY 16

enum rbos_event_type {
  RBOS_EVENT_BUTTON,
  RBOS_EVENT_COMPLETION,
};

struct rbos_event {
  enum rbos_event_type type;
  uint32_t source;
  uint32_t value;
  uint32_t count;
  uint32_t generation;
};

struct rbos_event_stats { uint32_t pending, overflow, coalesced; };

struct rbos_event_queue {
  struct rbos_event events[RBOS_EVENT_QUEUE_CAPACITY];
  uint32_t head;
  uint32_t size;
  uint32_t overflow;
  uint32_t coalesced;
};

/* Zero-initialize once. Callers must serialize push, pop and stats with an IRQ lock.
 * Each push represents one event; input count is ignored. No Ruby or allocation. */
bool rbos_event_queue_push(struct rbos_event_queue *queue, const struct rbos_event *event);
bool rbos_event_queue_pop(struct rbos_event_queue *queue, struct rbos_event *event);

#endif
