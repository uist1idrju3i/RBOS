#include "rbos/event_queue.h"

static void increment(uint32_t *counter)
{
  if (*counter < UINT32_MAX) ++*counter;
}

bool rbos_event_queue_push(struct rbos_event_queue *queue, const struct rbos_event *event)
{
  if (event->type == RBOS_EVENT_BUTTON) {
    for (uint32_t i = 0; i < queue->size; ++i) {
      struct rbos_event *pending = &queue->events[(queue->head + i) % RBOS_EVENT_QUEUE_CAPACITY];
      if (pending->type != RBOS_EVENT_BUTTON || pending->source != event->source) continue;
      if (pending->count == UINT32_MAX) {
        increment(&queue->overflow);
        return false;
      }
      ++pending->count;
      pending->value = event->value;
      increment(&queue->coalesced);
      return true;
    }
  }
  if (queue->size == RBOS_EVENT_QUEUE_CAPACITY) {
    increment(&queue->overflow);
    return false;
  }
  uint32_t tail = (queue->head + queue->size) % RBOS_EVENT_QUEUE_CAPACITY;
  queue->events[tail] = *event;
  queue->events[tail].count = 1;
  ++queue->size;
  return true;
}

bool rbos_event_queue_pop(struct rbos_event_queue *queue, struct rbos_event *event)
{
  if (queue->size == 0) return false;
  *event = queue->events[queue->head];
  queue->head = (queue->head + 1) % RBOS_EVENT_QUEUE_CAPACITY;
  --queue->size;
  return true;
}
