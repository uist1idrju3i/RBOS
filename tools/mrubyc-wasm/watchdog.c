#include "rbos/watchdog.h"

unsigned rbos_wasm_wdt_feeds;
int rbos_wasm_wdt_error;

int rbos_wdt_start(void) { return rbos_wasm_wdt_error; }
void rbos_wdt_feed(void) { ++rbos_wasm_wdt_feeds; }
