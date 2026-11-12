def expect_native_error(kind, message)
  begin
    yield
  rescue StandardError => error
    raise "wrong native exception" unless error.is_a?(kind) && error.message == message
    return
  end
  raise "missing native exception"
end

initial_calls = NativeFixture.calls
expect_native_error(ArgumentError, "Wrong number of arguments") { NativeFixture.sample }
expect_native_error(ArgumentError, "Wrong number of arguments") { NativeFixture.sample(1, 2) }
[nil, false, true, "", "1", :pin, [], {}, 1.0].each do |value|
  expect_native_error(TypeError, "Unexpected argument type") { NativeFixture.sample(value) }
end
[-101, 101, -2147483647, 2147483647].each do |value|
  expect_native_error(RangeError, "Integer out of range") { NativeFixture.sample(value) }
end
raise "invalid input reached backend" unless NativeFixture.calls == initial_calls
[-100, 0, 100].each do |value|
  raise "native value" unless NativeFixture.sample(value) == value
end
raise "optional count" unless NativeFixture.optional == 0 && NativeFixture.optional(nil) == 1
expect_native_error(ArgumentError, "Wrong number of arguments") { NativeFixture.optional(1, 2) }
expect_native_error(ArgumentError, "Expected no arguments") { NativeFixture.calls(1) }

["Driver failure", "Device busy", "Device timeout", "Driver failure"].each_with_index do |message, index|
  NativeFixture.failure = index + 1
  expect_native_error(RuntimeError, message) { NativeFixture.sample(0) }
end
NativeFixture.failure = 0
raise "backend recovery" unless NativeFixture.sample(0) == 0
raise "backend call count" unless NativeFixture.calls == initial_calls + 8

500.times do
  text = "borrowed"
  returned = NativeFixture.echo(text)
  text << "!"
  raise "borrowed string" unless returned == "borrowed!"
  array = ["kept"]
  returned = NativeFixture.echo(array)
  array << "!"
  raise "borrowed array" unless returned == ["kept", "!"]
  raise "owned string" unless NativeFixture.fresh == "native"
end
object = NativeFixture.new
raise "aliased receiver" unless object.itself == object
[nil, false, 0, :pin, "", []].each do |value|
  raise "immediate value" unless NativeFixture.echo(value) == value
end
raise "reference accounting" unless NativeFixture.ownership
puts "PASS: native helpers / validation / backend failures / ownership"
