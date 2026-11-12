#include <board-config.h>
#include <bm/bm_irq.h>
#include <nrfx_gpiote.h>
#include <nrfx_saadc.h>
#include <nrf_soc.h>
#include <zephyr/devicetree.h>
#include <zephyr/irq.h>
#include <zephyr/kernel.h>
#include CONFIG_NRFX_RESERVED_RESOURCES_HEADER

#define BANK DT_NODELABEL(rbos_gpio_pins)
BUILD_ASSERT(!DT_NODE_EXISTS(DT_NODELABEL(gpio0)) &&
             !DT_NODE_EXISTS(DT_NODELABEL(gpio1)) &&
             !DT_NODE_EXISTS(DT_NODELABEL(gpio2)) &&
             !DT_NODE_EXISTS(DT_NODELABEL(gpiote20)) &&
             !DT_NODE_EXISTS(DT_NODELABEL(gpiote30)), "BM must delete Zephyr GPIO/GPIOTE nodes");
BUILD_ASSERT(DT_PROP_LEN(BANK, port_pin_counts) == 3 &&
             DT_PROP_BY_IDX(BANK, port_pin_counts, 0) == 7 &&
             DT_PROP_BY_IDX(BANK, port_pin_counts, 1) == 16 &&
             DT_PROP_BY_IDX(BANK, port_pin_counts, 2) == 11, "Unexpected RBOS pin metadata");
BUILD_ASSERT(DT_PROP(DT_ALIAS(sw0), pin) == 45 && DT_PROP(DT_ALIAS(sw1), pin) == 41 &&
             DT_PROP(DT_ALIAS(sw2), pin) == 40 && DT_PROP(DT_ALIAS(sw3), pin) == 4,
             "Unexpected Button aliases");
BUILD_ASSERT(DT_PROP(DT_NODELABEL(led0), pin) == 73 &&
             DT_PROP(DT_NODELABEL(led1), pin) == 42 &&
             DT_PROP(DT_NODELABEL(led2), pin) == 71 &&
             DT_PROP(DT_NODELABEL(led3), pin) == 46, "Unexpected LED metadata");
BUILD_ASSERT(DT_PROP(DT_ALIAS(sw0), active_low) && DT_PROP(DT_ALIAS(sw1), active_low) &&
             DT_PROP(DT_ALIAS(sw2), active_low) && DT_PROP(DT_ALIAS(sw3), active_low),
             "Unexpected Button polarity");
BUILD_ASSERT(GPIOTE20_0_IRQn == 218 && GPIOTE30_0_IRQn == 268 &&
             NRFX_IRQ_NUMBER_GET(NRF_SAADC) == 213, "Unexpected peripheral IRQs");
BUILD_ASSERT(IS_ENABLED(CONFIG_NRFX_GPIOTE20) && IS_ENABLED(CONFIG_NRFX_GPIOTE30) &&
             CONFIG_NRFX_GPIOTE_NUM_OF_EVT_HANDLERS == 4 && IS_ENABLED(CONFIG_NRFX_SAADC),
             "Missing native drivers");
BUILD_ASSERT(IS_ENABLED(CONFIG_SOFTDEVICE_S115) && IS_ENABLED(CONFIG_LOG_BACKEND_BM_UARTE) &&
             !IS_ENABLED(CONFIG_GPIO) && !IS_ENABLED(CONFIG_SHELL) && !IS_ENABLED(CONFIG_BM_ZMS),
             "Unexpected peripheral owners");
BUILD_ASSERT(BOARD_CONSOLE_UARTE_PIN_TX == 36 && BOARD_CONSOLE_UARTE_PIN_CTS == 39,
             "Unexpected UARTE20 pins");
BUILD_ASSERT((NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK & SD_GRTC_CC_CHANNELS_USED) == 0 &&
             (NRFX_DPPI20_CHANNELS_USED & SD_DPPIC20_CHANNELS_USED) == SD_DPPIC20_CHANNELS_USED,
             "SoftDevice resource reservations overlap");
BUILD_ASSERT((NRFX_DPPI00_CHANNELS_USED & SD_DPPIC00_CHANNELS_USED) == SD_DPPIC00_CHANNELS_USED &&
             (NRFX_DPPI10_CHANNELS_USED & SD_DPPIC10_CHANNELS_USED) == SD_DPPIC10_CHANNELS_USED &&
             (NRFX_PPIB_INTERCONNECT_00_10_CHANNELS_USED & (SD_PPIB00_CHANNELS_USED | SD_PPIB10_CHANNELS_USED)) ==
                 (SD_PPIB00_CHANNELS_USED | SD_PPIB10_CHANNELS_USED) &&
             (NRFX_PPIB_INTERCONNECT_11_21_CHANNELS_USED & (SD_PPIB11_CHANNELS_USED | SD_PPIB21_CHANNELS_USED)) ==
                 (SD_PPIB11_CHANNELS_USED | SD_PPIB21_CHANNELS_USED), "Missing SoftDevice reservations");
BUILD_ASSERT(!IS_ENABLED(CONFIG_NFC_T2T_NRFXLIB) && !IS_ENABLED(CONFIG_NFC_T4T_NRFXLIB) &&
             BM_IRQ_OFFSET == 2 && __NVIC_PRIO_BITS == 3 &&
             CONFIG_ZERO_LATENCY_LEVELS == 1 && CONFIG_BM_TIMER_IRQ_PRIO >= 2 &&
             CONFIG_BM_TIMER_IRQ_PRIO <= 7 && CONFIG_LOG_BACKEND_BM_UARTE_IRQ_PRIO >= 2 &&
             CONFIG_LOG_BACKEND_BM_UARTE_IRQ_PRIO <= 7 &&
             (NRFX_GRTC_CONFIG_ALLOWED_CC_CHANNELS_MASK & BIT(0)) != 0 &&
             (SD_GRTC_CC_CHANNELS_USED & BIT(0)) == 0 && SD_GRTC_IRQn_USED != GRTC_2_IRQn,
             "Unexpected timer/console/interrupt reservations");

ISR_DIRECT_DECLARE(preflight_gpiote20) { return 0; }
ISR_DIRECT_DECLARE(preflight_gpiote30) { return 0; }
ISR_DIRECT_DECLARE(preflight_saadc) { return 0; }
static volatile bool exercise;
static nrf_saadc_value_t buffer[1];

int main(void)
{
  BM_IRQ_DIRECT_CONNECT(GPIOTE20_0_IRQn, 7, preflight_gpiote20, 0);
  BM_IRQ_DIRECT_CONNECT(GPIOTE30_0_IRQn, 7, preflight_gpiote30, 0);
  BM_IRQ_DIRECT_CONNECT(NRFX_IRQ_NUMBER_GET(NRF_SAADC), 7, preflight_saadc, 0);
  /* Link the audited SDK operations without running a hardware exercise. */
  if (exercise) {
    nrfx_gpiote_t instance = NRFX_GPIOTE_INSTANCE(NRF_GPIOTE20);
    uint8_t channel;
    uint32_t pin = DT_PROP(DT_ALIAS(sw0), pin);
    NRF_GPIO_Type *port = nrf_gpio_pin_port_decode(&pin);
    uint32_t previous = port->PIN_CNF[pin];
    (void)nrfx_gpiote_init(&instance, 7);
    (void)nrfx_gpiote_channel_alloc(&instance, &channel);
    nrfx_gpiote_trigger_config_t trigger = {
      .trigger = NRFX_GPIOTE_TRIGGER_TOGGLE, .p_in_channel = &channel };
    nrfx_gpiote_input_pin_config_t config = { .p_trigger_config = &trigger };
    (void)nrfx_gpiote_input_configure(&instance, 45, &config);
    (void)nrfx_gpiote_pin_uninit(&instance, 45);
    (void)nrfx_gpiote_channel_free(&instance, channel);
    port->PIN_CNF[pin] = previous;
    (void)nrfx_saadc_init(7);
    nrfx_saadc_channel_t adc = NRFX_SAADC_DEFAULT_CHANNEL_SE(NRFX_ANALOG_INTERNAL_VDD, 0);
    adc.channel_config.gain = NRF_SAADC_GAIN1_4;
    (void)nrfx_saadc_channels_config(&adc, 1);
    (void)nrfx_saadc_simple_mode_set(1, NRF_SAADC_RESOLUTION_12BIT,
                                    NRF_SAADC_OVERSAMPLE_DISABLED, NULL);
    (void)nrfx_saadc_buffer_set(buffer, 1);
    nrfx_saadc_abort();
    nrfx_saadc_uninit();
    int32_t temperature;
    (void)sd_temp_get(&temperature);
  }
  return 0;
}
