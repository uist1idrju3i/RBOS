deadline = NativeFixture.adc_time + 1000
until $adc_go
  raise 'ADC concurrent setup timeout' if NativeFixture.adc_time >= deadline
  sleep_ms(1)
end
begin
  ADC.internal(:dvdd).read_raw
  raise 'ADC concurrent read was accepted'
rescue RuntimeError => error
  raise 'ADC concurrent wrong error' unless error.message == 'Device busy'
  $adc_busy = true
end
deadline = NativeFixture.adc_time + 1000
until $adc_done
  raise 'ADC concurrent completion timeout' if NativeFixture.adc_time >= deadline
  $adc_progress += 1
  sleep_ms(1)
end
