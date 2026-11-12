def expect_temperature_error(kind, message)
  begin
    yield
  rescue StandardError => error
    raise "wrong temperature exception" unless error.is_a?(kind) && error.message == message
    return
  end
  raise "missing temperature exception"
end

calls = NativeFixture.temperature_calls
[nil, false, true, 0, 1.0, "", :pin, [], {}].each do |argument|
  expect_temperature_error(ArgumentError, "Expected no arguments") { Temperature.read(argument) }
end
expect_temperature_error(ArgumentError, "Expected no arguments") { Temperature.read(0, 1) }
expect_temperature_error(TypeError, "Temperature cannot be instantiated") { Temperature.new }
expect_temperature_error(TypeError, "Temperature cannot be instantiated") { Temperature.new(nil) }
raise "invalid temperature input reached backend" unless NativeFixture.temperature_calls == calls

[[-160, -40.0], [-1, -0.25], [0, 0.0], [1, 0.25], [100, 25.0], [500, 125.0]].each do |sample|
  NativeFixture.temperature_configure(sample[0], 0)
  value = Temperature.read
  raise "temperature type or signed scale" unless value.is_a?(Float) && value == sample[1]
end
raise "temperature success call count" unless NativeFixture.temperature_calls == calls + 6

["Driver failure", "Device busy", "Device timeout", "Driver failure"].each_with_index do |message, index|
  NativeFixture.temperature_configure(100, index + 1)
  expect_temperature_error(RuntimeError, message) { Temperature.read }
end
raise "temperature error call count" unless NativeFixture.temperature_calls == calls + 10
NativeFixture.temperature_available = 0
expect_temperature_error(RuntimeError, "Driver failure") { Temperature.read }
raise "unavailable temperature reached backend" unless NativeFixture.temperature_calls == calls + 10
NativeFixture.temperature_available = 1
NativeFixture.temperature_configure(-1, 0)
raise "temperature recovery" unless Temperature.read == -0.25

memory = NativeFixture.memory_used
1000.times do
  raise "temperature repeat" unless Temperature.read == -0.25
end
raise "temperature reference leak" unless NativeFixture.memory_used == memory
raise "temperature repeated call count" unless NativeFixture.temperature_calls == calls + 1011
puts "PASS: Temperature.read arguments, signed scale, failures, recovery and lifetime"
