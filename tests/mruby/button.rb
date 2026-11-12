def button_error(error)
  caught = false
  begin
    yield
  rescue error
    caught = true
  end
  raise 'Button expected error missing' unless caught
end

button_error(ArgumentError) { Button.new }
button_error(ArgumentError) { Button.new(:sw0, bad: 1) }
button_error(TypeError) { Button.new(nil) }
button_error(NotImplementedError) { Button.new(:led0) }
button_error(TypeError) { RBOSButtonSubscription.new }
button = Button.new(:sw0)
raise 'Button idle poll' unless button.poll.nil?
raise 'Button active-low pressed?' if button.pressed?
button_error(RuntimeError) { Button.new('P1.13') }
button_error(RuntimeError) { GPIO.setmode(45, GPIO::OUT) }
raise 'Button GPIO shared physical read' unless GPIO.read_at(45) == 1
button_error(ArgumentError) { button.poll(bad: 1) }
button_error(ArgumentError) { button.pressed?(bad: 1) }
button_error(ArgumentError) { button.close(bad: 1) }
button_error(ArgumentError) { Button.stats(bad: 1) }
button_error(ArgumentError) { button.wait(bad: 1) }
button_error(ArgumentError) { button.each_event }
button_error(ArgumentError) { button.each_event(bad: 1) { |level, count| } }

NativeFixture.button_edge(45, 0, 0)
NativeFixture.button_edge(45, 1, 0)
NativeFixture.button_edge(45, 0, 0)
raise 'Button coalesce stats' unless Button.stats[2] >= 2
raise 'Button coalesce level/count' unless button.poll == [0, 3]
raise 'Button pressed?' unless button.pressed?
raise 'Button consumed' unless button.poll.nil?
NativeFixture.button_edge(45, 1, 0)
button.each_event do |level, count|
  raise 'Button each_event caller delivery' unless level == 1 && count == 1
  break
end

NativeFixture.event_fill
before = Button.stats[1]
NativeFixture.button_edge(45, 1, 0)
raise 'Button newest-drop overflow' unless Button.stats[1] == before + 1
raise 'Button dropped edge delivered' unless button.poll.nil?
old = NativeFixture.button_generation(45)
NativeFixture.button_edge(45, 0, old)
button.close
raise 'Button idempotent close' unless button.close.nil?
button_error(RuntimeError) { button.poll }
button = Button.new(45)
raise 'Button old generation delivered' unless button.poll.nil?
NativeFixture.button_edge(45, 1, old)
raise 'Button delayed old edge delivered' unless button.poll.nil?

NativeFixture.gpio_status = 1
button_error(RuntimeError) { button.close }
button_error(RuntimeError) { GPIO.setmode(45, GPIO::OUT) }
NativeFixture.gpio_status = 0
button.close
GPIO.setmode(45, GPIO::OUT)
GPIO.write_at(45, 1)
NativeFixture.gpio_status = 2
button_error(RuntimeError) { Button.new(45) }
NativeFixture.gpio_status = 0
raise 'Button failed watch lost GPIO mode' unless GPIO.read_at(45) == 1
GPIO.write_at(45, 0)

others = [:sw1, :sw2, :sw3].map { |pin| Button.new(pin) }
button = Button.new(:sw0)
button_error(RuntimeError) { Button.new(:sw0) }
others.each { |other| other.close }
button.close
orphan = Button.new(:sw0)
NativeFixture.gpio_status = 1
orphan = nil
NativeFixture.adc_service
raise 'Button failed stop released generation' if NativeFixture.button_generation(45) == 0
NativeFixture.gpio_status = 0
NativeFixture.adc_service
raise 'Button orphan retry leaked watch' unless NativeFixture.button_generation(45) == 0

500.times do
  temporary = Button.new(:sw0)
  temporary.close
end
puts 'PASS: Button coalescing overflow generation and cleanup'
