$adc_lifetime_started = true
if $adc_lifetime_round == 1
  ADC.internal(:vdd).read_raw
  raise 'ADC terminated worker unexpectedly returned'
elsif $adc_lifetime_round == 2
  begin
    ADC.internal(:avdd).read_raw
    raise 'ADC reused VM stole old request'
  rescue RuntimeError => error
    raise 'ADC reused VM wrong error' unless error.message == 'Device busy'
    $adc_reused_busy = true
  end
else
  $adc_reused_result = ADC.internal(:dvdd).read_raw
end
