#include <assert.h>
#include <stdio.h>
#include "rbos/event_queue.h"

static struct rbos_event event(enum rbos_event_type type, uint32_t source, uint32_t value)
{
  return (struct rbos_event){ .type = type, .source = source, .value = value, .count = 99 };
}

static void fifo_and_wrap(void)
{
  struct rbos_event_queue queue = {0};
  struct rbos_event output = event(RBOS_EVENT_COMPLETION, 123, 456);
  assert(!rbos_event_queue_pop(&queue, &output));
  assert(output.source == 123 && output.value == 456);
  for (uint32_t round = 0; round < 100; ++round) {
    for (uint32_t i = 0; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) {
      struct rbos_event input = event(RBOS_EVENT_COMPLETION, i, round);
      assert(rbos_event_queue_push(&queue, &input));
    }
    struct rbos_event dropped = event(RBOS_EVENT_COMPLETION, 999, 0);
    assert(!rbos_event_queue_push(&queue, &dropped));
    for (uint32_t i = 0; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) {
      assert(rbos_event_queue_pop(&queue, &output));
      assert(output.type == RBOS_EVENT_COMPLETION && output.source == i);
      assert(output.value == round && output.count == 1);
    }
    assert(!rbos_event_queue_pop(&queue, &output));
    /* Shift the next full ring across the array boundary. */
    assert(rbos_event_queue_push(&queue, &dropped));
    assert(rbos_event_queue_pop(&queue, &output));
  }
  assert(queue.size == 0 && queue.overflow == 100 && queue.coalesced == 0);
}

static void coalesce_and_overflow(void)
{
  struct rbos_event_queue queue = {0};
  struct rbos_event a = event(RBOS_EVENT_BUTTON, 45, 0);
  struct rbos_event b = event(RBOS_EVENT_BUTTON, 46, 1);
  struct rbos_event output;
  assert(rbos_event_queue_push(&queue, &a));
  assert(rbos_event_queue_push(&queue, &b));
  for (uint32_t i = 0; i < RBOS_EVENT_QUEUE_CAPACITY - 2; ++i) {
    struct rbos_event completion = event(RBOS_EVENT_COMPLETION, 45, i);
    assert(rbos_event_queue_push(&queue, &completion));
  }
  a.value = 1;
  assert(rbos_event_queue_push(&queue, &a));
  assert(queue.size == RBOS_EVENT_QUEUE_CAPACITY && queue.coalesced == 1);
  struct rbos_event newest = event(RBOS_EVENT_BUTTON, 47, 1);
  assert(!rbos_event_queue_push(&queue, &newest));
  assert(queue.overflow == 1);
  assert(rbos_event_queue_pop(&queue, &output));
  assert(output.source == 45 && output.value == 1 && output.count == 2);
  assert(rbos_event_queue_pop(&queue, &output));
  assert(output.source == 46 && output.value == 1 && output.count == 1);
  assert(rbos_event_queue_push(&queue, &a));
  a.value = 0;
  assert(rbos_event_queue_push(&queue, &a));
  for (uint32_t i = 0; i < RBOS_EVENT_QUEUE_CAPACITY - 2; ++i) {
    assert(rbos_event_queue_pop(&queue, &output));
    assert(output.type == RBOS_EVENT_COMPLETION && output.count == 1 && output.value == i);
  }
  assert(rbos_event_queue_pop(&queue, &output));
  assert(output.type == RBOS_EVENT_BUTTON && output.value == 0 && output.count == 2);
  assert(!rbos_event_queue_pop(&queue, &output));
}

static void saturating_counters(void)
{
  struct rbos_event_queue queue = {0};
  struct rbos_event input = event(RBOS_EVENT_BUTTON, 45, 0);
  assert(rbos_event_queue_push(&queue, &input));
  queue.events[queue.head].count = UINT32_MAX - 1;
  queue.coalesced = UINT32_MAX;
  assert(rbos_event_queue_push(&queue, &input));
  assert(queue.events[queue.head].count == UINT32_MAX && queue.coalesced == UINT32_MAX);
  input.value = 1;
  assert(!rbos_event_queue_push(&queue, &input));
  assert(queue.overflow == 1 && queue.events[queue.head].value == 0);
  queue.overflow = UINT32_MAX;
  assert(!rbos_event_queue_push(&queue, &input));
  assert(queue.overflow == UINT32_MAX);
  struct rbos_event output;
  assert(rbos_event_queue_pop(&queue, &output));
  assert(output.count == UINT32_MAX && output.value == 0);
  for (uint32_t i = 0; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) {
    input = event(RBOS_EVENT_COMPLETION, i, 0);
    assert(rbos_event_queue_push(&queue, &input));
  }
  assert(!rbos_event_queue_push(&queue, &input));
  assert(queue.overflow == UINT32_MAX);
}

int main(void)
{
  fifo_and_wrap();
  coalesce_and_overflow();
  saturating_counters();
  puts("PASS: event queue / FIFO / wrap / drop-newest / coalesce / saturation");
  return 0;
}
