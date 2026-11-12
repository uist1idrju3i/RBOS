def check_adc_error(error)
  caught = false
  begin
    yield
  rescue error
    caught = true
  end
  raise 'ADC expected error missing' unless caught
end

before = NativeFixture.adc_calls
[nil, false, true, 1, 1.0, 'vdd', [], {}].each do |value|
  check_adc_error(TypeError) { ADC.internal(value) }
end
[:VDD, :internal_vdd, :unknown].each do |value|
  check_adc_error(ArgumentError) { ADC.internal(value) }
end
check_adc_error(ArgumentError) { ADC.internal }
check_adc_error(ArgumentError) { ADC.internal(:vdd, :avdd) }
check_adc_error(ArgumentError) { ADC.internal(:vdd, bad: 1) }
check_adc_error(ArgumentError) { ADC.new }
check_adc_error(NotImplementedError) { ADC.new(45) }
check_adc_error(TypeError) { RBOSADCRequest.new }
raise 'ADC invalid input reached backend' unless NativeFixture.adc_calls == before

[:dvdd, :avdd, :vdd].each_with_index do |source, index|
  adc = ADC.internal(source)
  NativeFixture.adc_configure(1024, 0, 0, 0)
  raise 'ADC selector raw' unless adc.read_raw == 1024
  raise 'ADC selector mapping' unless NativeFixture.adc_input == index
  raise 'ADC volts' unless (adc.read_voltage - 0.9).abs < 0.00001
  raise 'ADC read alias' unless adc.read == adc.read_voltage
  raise 'ADC duplicate object' unless adc.dup.read_raw == 1024
end

adc = ADC.internal(:vdd, **{})
[-32768, -1, 0, 1, 4095, 32767].each do |raw|
  NativeFixture.adc_configure(raw, 0, 0, 0)
  raise 'ADC signed raw' unless adc.read_raw == raw
  raise 'ADC signed volts' unless (adc.read - raw * 3.6 / 4096).abs < 0.0001
end

before = NativeFixture.adc_calls
check_adc_error(ArgumentError) { adc.read_raw(1) }
check_adc_error(ArgumentError) { adc.read_voltage(bad: 1) }
check_adc_error(ArgumentError) { adc.read(bad: 1) }
check_adc_error(ArgumentError) { adc.__start(false, bad: 1) }
check_adc_error(TypeError) { adc.__start(nil) }
check_adc_error(TypeError) { adc.__poll(nil) }
check_adc_error(TypeError) { adc.__finish(1) }
raise 'ADC invalid read reached backend' unless NativeFixture.adc_calls == before

[1, 2, 3].each do |status|
  NativeFixture.adc_configure(123, status, 0, 0)
  check_adc_error(RuntimeError) { adc.read_raw }
end
[-32769, 32768].each do |raw|
  NativeFixture.adc_configure(raw, 0, 0, 0)
  check_adc_error(RuntimeError) { adc.read_raw }
end

NativeFixture.adc_configure(100, 0, 1000, 30)
request = adc.__start(false)
before = NativeFixture.adc_calls
check_adc_error(RuntimeError) { ADC.internal(:avdd).read_raw }
check_adc_error(RuntimeError) { adc.__poll(request.dup) }
raise 'ADC busy started driver' unless NativeFixture.adc_calls == before
adc.__finish(request)
check_adc_error(RuntimeError) { adc.read_raw }
deadline = NativeFixture.adc_time + 1000
while NativeFixture.adc_active
  raise 'ADC cancel STOPPED timeout' if NativeFixture.adc_time >= deadline
  sleep_ms(1)
  NativeFixture.adc_service
end
NativeFixture.adc_configure(0, 0, 0, 0)
raise 'ADC cancel recovery' unless adc.read_raw == 0
check_adc_error(RuntimeError) { adc.__poll(request) }
request = nil

NativeFixture.adc_configure(500, 0, 1000, 0)
check_adc_error(RuntimeError) { adc.read_voltage }
NativeFixture.adc_configure(1024, 0, 0, 0)
raise 'ADC timeout recovery' unless adc.read_raw == 1024

# Warm method/ivar allocations before comparing live reference usage.
10.times { ADC.internal(:dvdd).read_raw }
before = NativeFixture.memory_used
200.times { ADC.internal(:dvdd).read_raw }
raise 'ADC reference leak' unless NativeFixture.memory_used == before
puts 'PASS: ADC input voltage errors cancellation and ownership'
