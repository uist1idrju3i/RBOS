$adc_go = false
$adc_done = false
$adc_busy = false
$adc_progress = 0
NativeFixture.adc_configure(2048, 0, 40, 0)
$adc_go = true
value = ADC.internal(:vdd).read_raw
raise 'ADC cooperative result' unless value == 2048
raise 'ADC other task stalled' unless $adc_busy && $adc_progress > 0
$adc_done = true
puts 'PASS: ADC cooperative waiting and concurrent busy'
