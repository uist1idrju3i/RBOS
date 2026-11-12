sleep_ms(10) until $p1_done
led = GPIO.new(:led0, GPIO::OUT)
led.write(1)
buttons = [:sw0, :sw1, :sw2, :sw3].map { |pin| Button.new(pin) }
rails = [:dvdd, :avdd, :vdd]
adcs = rails.map { |rail| ADC.internal(rail) }
cycles = 0
puts 'PASS: P2 native setup'
loop do
  buttons.each_with_index do |button, index|
    event = button.poll
    unless event.nil?
      puts "button index=#{index} level=#{event[0]} count=#{event[1]}"
    end
  end
  cycles += 1
  if cycles == 100
    begin
      puts "temperature c=#{Temperature.read}"
      adcs.each_with_index do |adc, index|
        puts "adc rail=#{rails[index]} raw=#{adc.read_raw} volts=#{adc.read_voltage}"
      end
    rescue RuntimeError => error
      puts "p2 error=#{error.message}"
    end
    cycles = 0
  end
  sleep_ms(10)
end
