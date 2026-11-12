$peripheral_events = 0
$peripheral_last_event = nil
class Button
  alias fixture_poll poll
  def poll
    event = fixture_poll
    unless event.nil?
      $peripheral_events += 1
      $peripheral_last_event = event
    end
    event
  end
end

$p1_done = true
NativeFixture.peripherals_spawn
begin
  deadline = NativeFixture.adc_time + 1000
  while NativeFixture.button_generation(4) == 0
    raise 'P2 diagnostic setup timeout' if NativeFixture.adc_time > deadline
    sleep_ms(1)
  end
  [45, 41, 40, 4].each do |pin|
    [0, 1].each do |level|
      before = $peripheral_events
      NativeFixture.button_edge(pin, level, 0)
      deadline = NativeFixture.adc_time + 1000
      while $peripheral_events == before
        raise 'P2 diagnostic edge timeout' if NativeFixture.adc_time >= deadline
        sleep_ms(1)
      end
      raise 'P2 diagnostic edge not consumed' unless $peripheral_last_event == [level, 1]
    end
  end
  before = NativeFixture.adc_calls
  deadline = NativeFixture.adc_time + 10000
  # The next request starts only after two six-request sweeps have returned.
  while NativeFixture.adc_calls < before + 13
    if NativeFixture.adc_time > deadline
      raise 'P2 diagnostic ADC repeats missing'
    end
    sleep_ms(10)
  end
ensure
  NativeFixture.peripherals_delete
  NativeFixture.adc_service
end
[45, 41, 40, 4].each do |pin|
  raise 'P2 diagnostic termination leaked watch' unless NativeFixture.button_generation(pin) == 0
end
puts 'PASS: P2 diagnostic task repeated samples and cleanup'
