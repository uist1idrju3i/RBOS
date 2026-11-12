$button_polls = 0
class Button
  alias fixture_poll poll
  def poll
    $button_polls += 1
    fixture_poll
  end
end

def await_button_fixture(message)
  deadline = NativeFixture.adc_time + 1000
  until yield
    raise message if NativeFixture.adc_time >= deadline
    sleep_ms(1)
  end
end

worker = false
begin
  vm_id = NativeFixture.button_spawn
  worker = true
  await_button_fixture('Button worker start timeout') { NativeFixture.button_generation(45) != 0 }
  old = NativeFixture.button_generation(45)
  NativeFixture.button_edge(45, 0, old)
  NativeFixture.button_delete
  worker = false
  NativeFixture.adc_service
  raise 'Button task termination leaked watch' unless NativeFixture.button_generation(45) == 0
  reused = NativeFixture.button_spawn
  worker = true
  raise 'Button VM ID not reused' unless reused == vm_id
  await_button_fixture('Button reused worker start timeout') { NativeFixture.button_generation(45) != 0 }
  polls = $button_polls
  NativeFixture.button_edge(45, 0, old)
  NativeFixture.adc_service
  await_button_fixture('Button stale event poll timeout') { $button_polls > polls }
  raise 'Button stale event ended watch' if NativeFixture.button_generation(45) == 0
  NativeFixture.button_edge(45, 1, 0)
  await_button_fixture('Button current edge timeout') { NativeFixture.button_generation(45) == 0 }
ensure
  NativeFixture.button_delete if worker
  NativeFixture.adc_service
end
raise 'Button normal completion leaked watch' unless NativeFixture.button_generation(45) == 0
puts 'PASS: Button cooperative wait termination and VM-ID reuse'
