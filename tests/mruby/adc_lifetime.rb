$adc_lifetime_round = 1
$adc_lifetime_started = false
$adc_reused_busy = false
$adc_reused_result = nil
NativeFixture.adc_configure(999, 0, 1000, 0)
old_id = NativeFixture.adc_spawn
sleep_ms(1) until $adc_lifetime_started && NativeFixture.adc_calls == 1
raise 'ADC worker did not start' unless $adc_lifetime_started && NativeFixture.adc_calls == 1
NativeFixture.adc_delete

$adc_lifetime_round = 2
new_id = NativeFixture.adc_spawn
raise 'ADC fixture did not reuse VM ID' unless old_id == new_id
sleep_ms(1) until NativeFixture.adc_done
raise 'ADC reused VM did not see busy' unless $adc_reused_busy
NativeFixture.adc_delete

# The idle foreground hook must reap the abandoned request, not a Ruby ensure.
deadline = NativeFixture.adc_time + 150
sleep_ms(10) while NativeFixture.adc_time < deadline
raise 'ADC idle hook did not stop abandoned DMA' if NativeFixture.adc_active
NativeFixture.adc_configure(2048, 0, 0, 0)
$adc_lifetime_round = 3
new_id = NativeFixture.adc_spawn
raise 'ADC fixture VM ID changed' unless old_id == new_id
sleep_ms(1) until NativeFixture.adc_done
raise 'ADC old result delivered to reused VM' unless $adc_reused_result == 2048
raise 'ADC busy called backend' unless NativeFixture.adc_calls == 2
NativeFixture.adc_delete
puts 'PASS: ADC termination VM-ID reuse and foreground recovery'
