sleep_ms(1) until $adc_go
begin
  ADC.internal(:dvdd).read_raw
  raise 'ADC concurrent read was accepted'
rescue RuntimeError => error
  raise 'ADC concurrent wrong error' unless error.message == 'Device busy'
  $adc_busy = true
end
until $adc_done
  $adc_progress += 1
  sleep_ms(1)
end
