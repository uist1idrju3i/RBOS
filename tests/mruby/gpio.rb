def gpio_error(error)
  caught = false
  begin
    yield
  rescue error
    caught = true
  end
  raise 'GPIO expected error missing' unless caught
end

before = NativeFixture.gpio_calls
[nil, true, false, 1.0, [], {}].each do |pin|
  gpio_error(TypeError) { GPIO.new(pin, GPIO::IN) }
end
['', 'P', 'p1.13', 'P1.', 'P1.32', ' P1.13', "P1.13\0", 'P999999999999.0'].each do |pin|
  gpio_error(ArgumentError) { GPIO.new(pin, GPIO::IN) }
end
[-1, 31, 48, 75, 96, 2147483647, 'P3.0'].each do |pin|
  gpio_error(RangeError) { GPIO.new(pin, GPIO::IN) }
end
[:missing, :SW0, :gpio0].each do |pin|
  gpio_error(ArgumentError) { GPIO.new(pin, GPIO::IN) }
end
[0, 36, 'P1.4', 39].each do |pin|
  gpio_error(RuntimeError) { GPIO.new(pin, GPIO::IN) }
end
[0, GPIO::PULL_UP, GPIO::IN | GPIO::OUT, GPIO::IN | GPIO::OPEN_DRAIN,
 GPIO::IN | GPIO::PULL_UP | GPIO::PULL_DOWN, GPIO::HIGH_Z | GPIO::PULL_UP, 64].each do |mode|
  gpio_error(ArgumentError) { GPIO.new(:sw0, mode) }
end
gpio_error(ArgumentError) { GPIO.new }
gpio_error(ArgumentError) { GPIO.new(:sw0) }
gpio_error(ArgumentError) { GPIO.new(:sw0, GPIO::IN, bad: 1) }
gpio_error(TypeError) { GPIO.new(:sw0, nil) }
gpio_error(RangeError) { GPIO.new(:sw0, -1) }
raise 'GPIO invalid input changed hardware' unless NativeFixture.gpio_calls == before

led = GPIO.new(:led0, GPIO::OUT, **{})
raise 'GPIO write return' unless led.write(1).nil?
raise 'GPIO physical equivalent' unless GPIO.read_at('P2.09') == 1 && GPIO.high_at?(73)
raise 'GPIO predicate' unless led.high? && !led.low?
raise 'GPIO read is integer' unless led.read == 1
GPIO.write_at(73, 0)
raise 'GPIO write_at equivalent' unless led.read == 0 && GPIO.low_at?(:led0)
NativeFixture.gpio_level(73, 1)
raise 'GPIO must read input, not latch' unless led.read == 1

button = GPIO.new(:sw0, GPIO::IN | GPIO::PULL_UP)
raise 'GPIO must not invert active-low' unless button.read == 1 && GPIO.read_at(45) == 1
NativeFixture.gpio_level(45, 0)
raise 'GPIO physical low' unless button.low? && GPIO.low_at?('P1.13')
button.setmode(GPIO::PULL_DOWN)
raise 'GPIO modifier mode' unless NativeFixture.gpio_mode(45) == GPIO::IN | GPIO::PULL_DOWN
button.setmode(GPIO::IN)
raise 'GPIO explicit mode resets pull' unless NativeFixture.gpio_mode(45) == GPIO::IN
GPIO.setmode(:sw0, GPIO::HIGH_Z)
gpio_error(RuntimeError) { button.read }
gpio_error(RuntimeError) { button.write(1) }
button.setmode(GPIO::OUT | GPIO::OPEN_DRAIN)
raise 'GPIO open drain' unless NativeFixture.gpio_mode(45) == GPIO::OUT | GPIO::OPEN_DRAIN

before = NativeFixture.gpio_calls
[nil, false, '1', 1.0].each { |value| gpio_error(TypeError) { led.write(value) } }
[-1, 2].each { |value| gpio_error(RangeError) { led.write(value) } }
gpio_error(ArgumentError) { led.read(1) }
gpio_error(ArgumentError) { led.read(bad: 1) }
gpio_error(ArgumentError) { led.high?(bad: 1) }
gpio_error(ArgumentError) { led.low?(bad: 1) }
gpio_error(ArgumentError) { led.write(1, bad: 1) }
gpio_error(ArgumentError) { led.setmode(GPIO::IN, bad: 1) }
gpio_error(ArgumentError) { GPIO.setmode(:sw0, GPIO::IN, bad: 1) }
gpio_error(ArgumentError) { GPIO.read_at(:sw0, bad: 1) }
gpio_error(ArgumentError) { GPIO.high_at?(:sw0, bad: 1) }
gpio_error(ArgumentError) { GPIO.low_at?(:sw0, bad: 1) }
gpio_error(ArgumentError) { GPIO.write_at(:sw0, 1, bad: 1) }
gpio_error(TypeError) { GPIO.read }
raise 'GPIO argument errors changed hardware' unless NativeFixture.gpio_calls == before

[1, 2, 3, 4, 7].each do |status|
  NativeFixture.gpio_status = status
  error = status == 7 ? NotImplementedError : RuntimeError
  gpio_error(error) { led.read }
  gpio_error(error) { led.write(1) }
  gpio_error(error) { led.setmode(GPIO::IN) }
end
NativeFixture.gpio_status = 0
led.write(1)
raise 'GPIO failed configure changed cached mode' unless led.read == 1
500.times do
  gpio = GPIO.new('P2.9', GPIO::OUT)
  gpio.write(1)
  raise 'GPIO repeated access' unless gpio.high?
end
puts 'PASS: GPIO pin modes physical levels errors and ownership'
