def host_argument_case(id, error, no_backend = false)
  before = [NativeFixture.gpio_calls, NativeFixture.adc_calls, NativeFixture.temperature_calls]
  total = NativeFixture.backend_calls
  caught = false
  begin
    yield
  rescue error
    caught = true
  end
  raise id unless caught
  after = [NativeFixture.gpio_calls, NativeFixture.adc_calls, NativeFixture.temperature_calls]
  raise id + " hardware side effect" unless before == after
  raise id + " backend reached" if no_backend && total != NativeFixture.backend_calls
end

gpio = GPIO.new(:led1, GPIO::OUT)
button = Button.new(:sw0)
adc = ADC.internal(:vdd)
request = adc.__start(false)

host_argument_case("native-arg-1", ArgumentError, false) { Temperature.read(0) }
host_argument_case("native-arg-2", ArgumentError, false) { Temperature.read(nil) }
host_argument_case("native-arg-3", ArgumentError, false) { Temperature.read([]) }
host_argument_case("native-arg-4", ArgumentError, false) { Temperature.read(unexpected: nil) }
host_argument_case("native-arg-5", ArgumentError, true) { Temperature.read(unexpected: nil) }

host_argument_case("native-arg-6", TypeError, false) { Temperature.new(0) }
host_argument_case("native-arg-7", TypeError, false) { Temperature.new(nil) }
host_argument_case("native-arg-8", TypeError, false) { Temperature.new([]) }
host_argument_case("native-arg-9", TypeError, false) { Temperature.new(unexpected: nil) }
host_argument_case("native-arg-10", TypeError, true) { Temperature.new(unexpected: nil) }

host_argument_case("native-arg-11", ArgumentError, false) { ADC.internal() }
host_argument_case("native-arg-12", ArgumentError, false) { ADC.internal(:vdd, 0) }
host_argument_case("native-arg-13", TypeError, false) { ADC.internal(nil) }
host_argument_case("native-arg-14", TypeError, false) { ADC.internal([]) }
host_argument_case("native-arg-15", ArgumentError, false) { ADC.internal(:vdd, unexpected: nil) }
host_argument_case("native-arg-16", ArgumentError, true) { ADC.internal(:vdd, unexpected: nil) }

host_argument_case("native-arg-17", ArgumentError, false) { ADC.new() }
host_argument_case("native-arg-18", NotImplementedError, false) { ADC.new(nil) }
host_argument_case("native-arg-19", NotImplementedError, false) { ADC.new([]) }
host_argument_case("native-arg-20", ArgumentError, false) { ADC.new(0, unexpected: nil) }
host_argument_case("native-arg-21", ArgumentError, true) { ADC.new(0, unexpected: nil) }

host_argument_case("native-arg-22", ArgumentError, false) { adc.read_raw(0) }
host_argument_case("native-arg-23", ArgumentError, false) { adc.read_raw(nil) }
host_argument_case("native-arg-24", ArgumentError, false) { adc.read_raw([]) }
host_argument_case("native-arg-25", ArgumentError, false) { adc.read_raw(unexpected: nil) }
host_argument_case("native-arg-26", ArgumentError, true) { adc.read_raw(unexpected: nil) }

host_argument_case("native-arg-27", ArgumentError, false) { adc.read_voltage(0) }
host_argument_case("native-arg-28", ArgumentError, false) { adc.read_voltage(nil) }
host_argument_case("native-arg-29", ArgumentError, false) { adc.read_voltage([]) }
host_argument_case("native-arg-30", ArgumentError, false) { adc.read_voltage(unexpected: nil) }
host_argument_case("native-arg-31", ArgumentError, true) { adc.read_voltage(unexpected: nil) }

host_argument_case("native-arg-32", ArgumentError, false) { adc.read(0) }
host_argument_case("native-arg-33", ArgumentError, false) { adc.read(nil) }
host_argument_case("native-arg-34", ArgumentError, false) { adc.read([]) }
host_argument_case("native-arg-35", ArgumentError, false) { adc.read(unexpected: nil) }
host_argument_case("native-arg-36", ArgumentError, true) { adc.read(unexpected: nil) }

host_argument_case("native-arg-37", ArgumentError, false) { adc.__start() }
host_argument_case("native-arg-38", ArgumentError, false) { adc.__start(false, 0) }
host_argument_case("native-arg-39", TypeError, false) { adc.__start(nil) }
host_argument_case("native-arg-40", TypeError, false) { adc.__start([]) }
host_argument_case("native-arg-41", ArgumentError, false) { adc.__start(false, unexpected: nil) }
host_argument_case("native-arg-42", ArgumentError, true) { adc.__start(false, unexpected: nil) }

host_argument_case("native-arg-43", ArgumentError, false) { adc.__poll() }
host_argument_case("native-arg-44", ArgumentError, false) { adc.__poll(request, 0) }
host_argument_case("native-arg-45", TypeError, false) { adc.__poll(nil) }
host_argument_case("native-arg-46", TypeError, false) { adc.__poll([]) }
host_argument_case("native-arg-47", ArgumentError, false) { adc.__poll(request, unexpected: nil) }
host_argument_case("native-arg-48", ArgumentError, true) { adc.__poll(request, unexpected: nil) }

host_argument_case("native-arg-49", ArgumentError, false) { adc.__finish() }
host_argument_case("native-arg-50", ArgumentError, false) { adc.__finish(request, 0) }
host_argument_case("native-arg-51", TypeError, false) { adc.__finish(nil) }
host_argument_case("native-arg-52", TypeError, false) { adc.__finish([]) }
host_argument_case("native-arg-53", ArgumentError, false) { adc.__finish(request, unexpected: nil) }
host_argument_case("native-arg-54", ArgumentError, true) { adc.__finish(request, unexpected: nil) }

host_argument_case("native-arg-55", ArgumentError, false) { adc.__measure() }
host_argument_case("native-arg-56", ArgumentError, false) { adc.__measure(false, 0) }
host_argument_case("native-arg-57", TypeError, false) { adc.__measure(nil) }
host_argument_case("native-arg-58", TypeError, false) { adc.__measure([]) }
host_argument_case("native-arg-59", ArgumentError, false) { adc.__measure(false, unexpected: nil) }
host_argument_case("native-arg-60", ArgumentError, true) { adc.__measure(false, unexpected: nil) }

host_argument_case("native-arg-61", TypeError, false) { RBOSADCRequest.new(0) }
host_argument_case("native-arg-62", TypeError, false) { RBOSADCRequest.new(nil) }
host_argument_case("native-arg-63", TypeError, false) { RBOSADCRequest.new([]) }
host_argument_case("native-arg-64", TypeError, false) { RBOSADCRequest.new(unexpected: nil) }
host_argument_case("native-arg-65", TypeError, true) { RBOSADCRequest.new(unexpected: nil) }

host_argument_case("native-arg-66", TypeError, false) { RBOSButtonSubscription.new(0) }
host_argument_case("native-arg-67", TypeError, false) { RBOSButtonSubscription.new(nil) }
host_argument_case("native-arg-68", TypeError, false) { RBOSButtonSubscription.new([]) }
host_argument_case("native-arg-69", TypeError, false) { RBOSButtonSubscription.new(unexpected: nil) }
host_argument_case("native-arg-70", TypeError, true) { RBOSButtonSubscription.new(unexpected: nil) }

host_argument_case("native-arg-71", ArgumentError, false) { Button.new() }
host_argument_case("native-arg-72", ArgumentError, false) { Button.new(:sw1, 0) }
host_argument_case("native-arg-73", TypeError, false) { Button.new(nil) }
host_argument_case("native-arg-74", TypeError, false) { Button.new([]) }
host_argument_case("native-arg-75", RangeError, false) { Button.new(-1) }
host_argument_case("native-arg-76", RangeError, false) { Button.new(2147483647) }
host_argument_case("native-arg-77", ArgumentError, false) { Button.new(:sw1, unexpected: nil) }
host_argument_case("native-arg-78", ArgumentError, true) { Button.new(:sw1, unexpected: nil) }

host_argument_case("native-arg-79", ArgumentError, false) { Button.stats(0) }
host_argument_case("native-arg-80", ArgumentError, false) { Button.stats(nil) }
host_argument_case("native-arg-81", ArgumentError, false) { Button.stats([]) }
host_argument_case("native-arg-82", ArgumentError, false) { Button.stats(unexpected: nil) }
host_argument_case("native-arg-83", ArgumentError, true) { Button.stats(unexpected: nil) }

host_argument_case("native-arg-84", ArgumentError, false) { button.poll(0) }
host_argument_case("native-arg-85", ArgumentError, false) { button.poll(nil) }
host_argument_case("native-arg-86", ArgumentError, false) { button.poll([]) }
host_argument_case("native-arg-87", ArgumentError, false) { button.poll(unexpected: nil) }
host_argument_case("native-arg-88", ArgumentError, true) { button.poll(unexpected: nil) }

host_argument_case("native-arg-89", ArgumentError, false) { button.wait(0) }
host_argument_case("native-arg-90", ArgumentError, false) { button.wait(nil) }
host_argument_case("native-arg-91", ArgumentError, false) { button.wait([]) }
host_argument_case("native-arg-92", ArgumentError, false) { button.wait(unexpected: nil) }
host_argument_case("native-arg-93", ArgumentError, true) { button.wait(unexpected: nil) }

host_argument_case("native-arg-94", ArgumentError, false) { button.each_event(0) }
host_argument_case("native-arg-95", ArgumentError, false) { button.each_event(nil) }
host_argument_case("native-arg-96", ArgumentError, false) { button.each_event([]) }
host_argument_case("native-arg-97", ArgumentError, false) { button.each_event(unexpected: nil) }
host_argument_case("native-arg-98", ArgumentError, true) { button.each_event(unexpected: nil) }

host_argument_case("native-arg-99", ArgumentError, false) { button.pressed?(0) }
host_argument_case("native-arg-100", ArgumentError, false) { button.pressed?(nil) }
host_argument_case("native-arg-101", ArgumentError, false) { button.pressed?([]) }
host_argument_case("native-arg-102", ArgumentError, false) { button.pressed?(unexpected: nil) }
host_argument_case("native-arg-103", ArgumentError, true) { button.pressed?(unexpected: nil) }

host_argument_case("native-arg-104", ArgumentError, false) { button.close(0) }
host_argument_case("native-arg-105", ArgumentError, false) { button.close(nil) }
host_argument_case("native-arg-106", ArgumentError, false) { button.close([]) }
host_argument_case("native-arg-107", ArgumentError, false) { button.close(unexpected: nil) }
host_argument_case("native-arg-108", ArgumentError, true) { button.close(unexpected: nil) }

host_argument_case("native-arg-109", ArgumentError, false) { GPIO.new() }
host_argument_case("native-arg-110", ArgumentError, false) { GPIO.new(:led2, GPIO::OUT, 0) }
host_argument_case("native-arg-111", TypeError, false) { GPIO.new(:led2, nil) }
host_argument_case("native-arg-112", TypeError, false) { GPIO.new(:led2, []) }
host_argument_case("native-arg-113", RangeError, false) { GPIO.new(:led2, -1) }
host_argument_case("native-arg-114", ArgumentError, false) { GPIO.new(:led2, 2147483647) }
host_argument_case("native-arg-115", ArgumentError, false) { GPIO.new(:led2, GPIO::OUT, unexpected: nil) }
host_argument_case("native-arg-116", ArgumentError, true) { GPIO.new(:led2, GPIO::OUT, unexpected: nil) }

host_argument_case("native-arg-117", ArgumentError, false) { GPIO.setmode() }
host_argument_case("native-arg-118", ArgumentError, false) { GPIO.setmode(:led2, GPIO::OUT, 0) }
host_argument_case("native-arg-119", TypeError, false) { GPIO.setmode(:led2, nil) }
host_argument_case("native-arg-120", TypeError, false) { GPIO.setmode(:led2, []) }
host_argument_case("native-arg-121", RangeError, false) { GPIO.setmode(:led2, -1) }
host_argument_case("native-arg-122", ArgumentError, false) { GPIO.setmode(:led2, 2147483647) }
host_argument_case("native-arg-123", ArgumentError, false) { GPIO.setmode(:led2, GPIO::OUT, unexpected: nil) }
host_argument_case("native-arg-124", ArgumentError, true) { GPIO.setmode(:led2, GPIO::OUT, unexpected: nil) }

host_argument_case("native-arg-125", ArgumentError, false) { GPIO.read_at() }
host_argument_case("native-arg-126", ArgumentError, false) { GPIO.read_at(:led1, 0) }
host_argument_case("native-arg-127", TypeError, false) { GPIO.read_at(nil) }
host_argument_case("native-arg-128", TypeError, false) { GPIO.read_at([]) }
host_argument_case("native-arg-129", RangeError, false) { GPIO.read_at(-1) }
host_argument_case("native-arg-130", RangeError, false) { GPIO.read_at(2147483647) }
host_argument_case("native-arg-131", ArgumentError, false) { GPIO.read_at(:led1, unexpected: nil) }
host_argument_case("native-arg-132", ArgumentError, true) { GPIO.read_at(:led1, unexpected: nil) }

host_argument_case("native-arg-133", ArgumentError, false) { GPIO.high_at?() }
host_argument_case("native-arg-134", ArgumentError, false) { GPIO.high_at?(:led1, 0) }
host_argument_case("native-arg-135", TypeError, false) { GPIO.high_at?(nil) }
host_argument_case("native-arg-136", TypeError, false) { GPIO.high_at?([]) }
host_argument_case("native-arg-137", RangeError, false) { GPIO.high_at?(-1) }
host_argument_case("native-arg-138", RangeError, false) { GPIO.high_at?(2147483647) }
host_argument_case("native-arg-139", ArgumentError, false) { GPIO.high_at?(:led1, unexpected: nil) }
host_argument_case("native-arg-140", ArgumentError, true) { GPIO.high_at?(:led1, unexpected: nil) }

host_argument_case("native-arg-141", ArgumentError, false) { GPIO.low_at?() }
host_argument_case("native-arg-142", ArgumentError, false) { GPIO.low_at?(:led1, 0) }
host_argument_case("native-arg-143", TypeError, false) { GPIO.low_at?(nil) }
host_argument_case("native-arg-144", TypeError, false) { GPIO.low_at?([]) }
host_argument_case("native-arg-145", RangeError, false) { GPIO.low_at?(-1) }
host_argument_case("native-arg-146", RangeError, false) { GPIO.low_at?(2147483647) }
host_argument_case("native-arg-147", ArgumentError, false) { GPIO.low_at?(:led1, unexpected: nil) }
host_argument_case("native-arg-148", ArgumentError, true) { GPIO.low_at?(:led1, unexpected: nil) }

host_argument_case("native-arg-149", ArgumentError, false) { GPIO.write_at() }
host_argument_case("native-arg-150", ArgumentError, false) { GPIO.write_at(:led1, 0, 0) }
host_argument_case("native-arg-151", TypeError, false) { GPIO.write_at(:led1, nil) }
host_argument_case("native-arg-152", TypeError, false) { GPIO.write_at(:led1, []) }
host_argument_case("native-arg-153", RangeError, false) { GPIO.write_at(:led1, -1) }
host_argument_case("native-arg-154", RangeError, false) { GPIO.write_at(:led1, 2) }
host_argument_case("native-arg-155", ArgumentError, false) { GPIO.write_at(:led1, 0, unexpected: nil) }
host_argument_case("native-arg-156", ArgumentError, true) { GPIO.write_at(:led1, 0, unexpected: nil) }

host_argument_case("native-arg-157", ArgumentError, false) { gpio.read(0) }
host_argument_case("native-arg-158", ArgumentError, false) { gpio.read(nil) }
host_argument_case("native-arg-159", ArgumentError, false) { gpio.read([]) }
host_argument_case("native-arg-160", ArgumentError, false) { gpio.read(unexpected: nil) }
host_argument_case("native-arg-161", ArgumentError, true) { gpio.read(unexpected: nil) }

host_argument_case("native-arg-162", ArgumentError, false) { gpio.high?(0) }
host_argument_case("native-arg-163", ArgumentError, false) { gpio.high?(nil) }
host_argument_case("native-arg-164", ArgumentError, false) { gpio.high?([]) }
host_argument_case("native-arg-165", ArgumentError, false) { gpio.high?(unexpected: nil) }
host_argument_case("native-arg-166", ArgumentError, true) { gpio.high?(unexpected: nil) }

host_argument_case("native-arg-167", ArgumentError, false) { gpio.low?(0) }
host_argument_case("native-arg-168", ArgumentError, false) { gpio.low?(nil) }
host_argument_case("native-arg-169", ArgumentError, false) { gpio.low?([]) }
host_argument_case("native-arg-170", ArgumentError, false) { gpio.low?(unexpected: nil) }
host_argument_case("native-arg-171", ArgumentError, true) { gpio.low?(unexpected: nil) }

host_argument_case("native-arg-172", ArgumentError, false) { gpio.write() }
host_argument_case("native-arg-173", ArgumentError, false) { gpio.write(0, 0) }
host_argument_case("native-arg-174", TypeError, false) { gpio.write(nil) }
host_argument_case("native-arg-175", TypeError, false) { gpio.write([]) }
host_argument_case("native-arg-176", RangeError, false) { gpio.write(-1) }
host_argument_case("native-arg-177", RangeError, false) { gpio.write(2) }
host_argument_case("native-arg-178", ArgumentError, false) { gpio.write(0, unexpected: nil) }
host_argument_case("native-arg-179", ArgumentError, true) { gpio.write(0, unexpected: nil) }

host_argument_case("native-arg-180", ArgumentError, false) { gpio.setmode() }
host_argument_case("native-arg-181", ArgumentError, false) { gpio.setmode(GPIO::OUT, 0) }
host_argument_case("native-arg-182", TypeError, false) { gpio.setmode(nil) }
host_argument_case("native-arg-183", TypeError, false) { gpio.setmode([]) }
host_argument_case("native-arg-184", RangeError, false) { gpio.setmode(-1) }
host_argument_case("native-arg-185", ArgumentError, false) { gpio.setmode(2147483647) }
host_argument_case("native-arg-186", ArgumentError, false) { gpio.setmode(GPIO::OUT, unexpected: nil) }
host_argument_case("native-arg-187", ArgumentError, true) { gpio.setmode(GPIO::OUT, unexpected: nil) }

host_argument_case("native-arg-188", TypeError, false) { GPIO.new(nil, GPIO::OUT) }
host_argument_case("native-arg-189", TypeError, false) { GPIO.new([], GPIO::OUT) }
host_argument_case("native-arg-190", RangeError, false) { GPIO.new(-1, GPIO::OUT) }
host_argument_case("native-arg-191", RangeError, false) { GPIO.new(2147483647, GPIO::OUT) }
host_argument_case("native-arg-192", ArgumentError, false) { GPIO.new(:led1) }
host_argument_case("native-arg-193", TypeError, false) { GPIO.setmode(nil, GPIO::OUT) }
host_argument_case("native-arg-194", TypeError, false) { GPIO.setmode([], GPIO::OUT) }
host_argument_case("native-arg-195", RangeError, false) { GPIO.setmode(-1, GPIO::OUT) }
host_argument_case("native-arg-196", RangeError, false) { GPIO.setmode(2147483647, GPIO::OUT) }
host_argument_case("native-arg-197", ArgumentError, false) { GPIO.setmode(:led1) }
host_argument_case("native-arg-198", TypeError, false) { GPIO.write_at(nil, 0) }
host_argument_case("native-arg-199", TypeError, false) { GPIO.write_at([], 0) }
host_argument_case("native-arg-200", RangeError, false) { GPIO.write_at(-1, 0) }
host_argument_case("native-arg-201", RangeError, false) { GPIO.write_at(2147483647, 0) }
host_argument_case("native-arg-202", ArgumentError, false) { GPIO.write_at(:led1) }
adc.__finish(request)
NativeFixture.adc_service
button.close
puts 'PASS: native argument matrix'
