$p1_done = true
NativeFixture.peripherals_spawn
deadline = NativeFixture.adc_time + 1000
while NativeFixture.button_generation(4) == 0
  raise 'P2 diagnostic setup timeout' if NativeFixture.adc_time > deadline
  sleep_ms(1)
end
[45, 41, 40, 4].each do |pin|
  NativeFixture.button_edge(pin, 0, 0)
  sleep_ms(20)
  NativeFixture.button_edge(pin, 1, 0)
  sleep_ms(20)
end
before = NativeFixture.adc_calls
deadline = NativeFixture.adc_time + 10000
while NativeFixture.adc_calls < before + 6
  if NativeFixture.adc_time > deadline
    NativeFixture.peripherals_delete
    raise 'P2 diagnostic ADC repeats missing'
  end
  sleep_ms(10)
end
NativeFixture.peripherals_delete
NativeFixture.adc_service
[45, 41, 40, 4].each do |pin|
  raise 'P2 diagnostic termination leaked watch' unless NativeFixture.button_generation(pin) == 0
end
puts 'PASS: P2 diagnostic task repeated samples and cleanup'
