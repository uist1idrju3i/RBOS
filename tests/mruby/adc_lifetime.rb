def await_adc_fixture(message)
  deadline = NativeFixture.adc_time + 1000
  until yield
    raise message if NativeFixture.adc_time >= deadline
    sleep_ms(1)
  end
end

worker = false
begin
  $adc_lifetime_round = 1
  $adc_lifetime_started = false
  $adc_reused_busy = false
  $adc_reused_result = nil
  NativeFixture.adc_configure(999, 0, 1000, 0)
  old_id = NativeFixture.adc_spawn
  worker = true
  await_adc_fixture('ADC worker start timeout') { $adc_lifetime_started && NativeFixture.adc_calls == 1 }
  NativeFixture.adc_delete
  worker = false

  $adc_lifetime_round = 2
  new_id = NativeFixture.adc_spawn
  worker = true
  raise 'ADC fixture did not reuse VM ID' unless old_id == new_id
  await_adc_fixture('ADC reused VM timeout') { NativeFixture.adc_done }
  raise 'ADC reused VM did not see busy' unless $adc_reused_busy
  NativeFixture.adc_delete
  worker = false

  # The idle foreground hook must reap the abandoned request, not a Ruby ensure.
  await_adc_fixture('ADC idle hook did not stop abandoned DMA') { !NativeFixture.adc_active }
  NativeFixture.adc_configure(2048, 0, 0, 0)
  $adc_lifetime_round = 3
  new_id = NativeFixture.adc_spawn
  worker = true
  raise 'ADC fixture VM ID changed' unless old_id == new_id
  await_adc_fixture('ADC recovery worker timeout') { NativeFixture.adc_done }
  raise 'ADC old result delivered to reused VM' unless $adc_reused_result == 2048
  raise 'ADC busy called backend' unless NativeFixture.adc_calls == 2
ensure
  NativeFixture.adc_delete if worker
  NativeFixture.adc_service
end
puts 'PASS: ADC termination VM-ID reuse and foreground recovery'
