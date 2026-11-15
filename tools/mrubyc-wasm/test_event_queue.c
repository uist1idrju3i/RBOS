#include <assert.h>
#include <stdio.h>
#include <string.h>
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

static void generations(void)
{
  struct rbos_event_queue queue = {0};
  struct rbos_event input = event(RBOS_EVENT_BUTTON, 45, 0), output;
  input.generation = 1;
  assert(rbos_event_queue_push(&queue, &input));
  input.generation = 2;
  assert(rbos_event_queue_push(&queue, &input));
  assert(queue.size == 2 && queue.coalesced == 0);
  assert(rbos_event_queue_pop(&queue, &output) && output.generation == 1);
  assert(rbos_event_queue_pop(&queue, &output) && output.generation == 2);
}

static uint32_t random_word(uint32_t *state)
{
  *state = *state * 1664525u + 1013904223u;
  return *state;
}

static void reference_model(void)
{
  const uint32_t seeds[] = { 1, 0x5a17cafe, UINT32_MAX };
  for (unsigned int seed = 0; seed < sizeof(seeds) / sizeof(*seeds); ++seed) {
    uint32_t state = seeds[seed], size = 0, overflow = 0, coalesced = 0;
    struct rbos_event_queue queue = {0};
    struct rbos_event model[RBOS_EVENT_QUEUE_CAPACITY];
    for (unsigned int step = 0; step < 20000; ++step) {
      uint32_t op = random_word(&state);
      if (op % 4 == 0) {
        struct rbos_event actual = event(RBOS_EVENT_COMPLETION, 999, 888);
        assert(rbos_event_queue_pop(&queue, &actual) == (size != 0));
        if (size) {
          assert(actual.type == model[0].type && actual.source == model[0].source &&
                 actual.value == model[0].value && actual.count == model[0].count &&
                 actual.generation == model[0].generation);
          memmove(model, model + 1, --size * sizeof(*model));
        } else assert(actual.source == 999 && actual.value == 888);
      } else {
        struct rbos_event input = event((op >> 4) & 1, (op >> 8) % 5, (op >> 12) & 1);
        input.generation = (op >> 16) % 3;
        uint32_t i = 0;
        if (input.type == RBOS_EVENT_BUTTON) {
          for (; i < size; ++i)
            if (model[i].type == input.type && model[i].source == input.source &&
                model[i].generation == input.generation) break;
        } else i = size;
        bool accepted = i < size || size < RBOS_EVENT_QUEUE_CAPACITY;
        if (i < size) { ++model[i].count; model[i].value = input.value; ++coalesced; }
        else if (accepted) { model[size] = input; model[size++].count = 1; }
        else ++overflow;
        assert(rbos_event_queue_push(&queue, &input) == accepted);
      }
      assert(queue.size == size && queue.overflow == overflow && queue.coalesced == coalesced);
      for (uint32_t i = 0; i < size; ++i) {
        struct rbos_event *actual = &queue.events[(queue.head + i) % RBOS_EVENT_QUEUE_CAPACITY];
        assert(actual->type == model[i].type && actual->source == model[i].source &&
               actual->generation == model[i].generation && actual->value == model[i].value &&
               actual->count == model[i].count);
      }
    }
  }
  puts("PASS: event queue reference model seeds=1,0x5a17cafe,0xffffffff steps=60000");
}

int main(void)
{
  fifo_and_wrap();
  coalesce_and_overflow();
  saturating_counters();
  generations();
  reference_model();
  puts("PASS: event queue / FIFO / wrap / drop-newest / coalesce / saturation");
  return 0;
}
