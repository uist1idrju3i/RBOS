vm_id = NativeFixture.button_spawn
deadline = NativeFixture.adc_time + 1000
while NativeFixture.button_generation(45) == 0
  raise 'Button worker start timeout' if NativeFixture.adc_time > deadline
  sleep_ms(1)
end
old = NativeFixture.button_generation(45)
NativeFixture.button_edge(45, 0, old)
NativeFixture.button_delete
NativeFixture.adc_service
raise 'Button task termination leaked watch' unless NativeFixture.button_generation(45) == 0
reused = NativeFixture.button_spawn
raise 'Button VM ID not reused' unless reused == vm_id
deadline = NativeFixture.adc_time + 1000
while NativeFixture.button_generation(45) == 0
  raise 'Button reused worker start timeout' if NativeFixture.adc_time > deadline
  sleep_ms(1)
end
NativeFixture.button_edge(45, 0, old)
NativeFixture.adc_service
sleep_ms(3)
NativeFixture.button_edge(45, 1, 0)
sleep_ms(5)
NativeFixture.button_delete
NativeFixture.adc_service
raise 'Button normal completion leaked watch' unless NativeFixture.button_generation(45) == 0
puts 'PASS: Button cooperative wait termination and VM-ID reuse'
