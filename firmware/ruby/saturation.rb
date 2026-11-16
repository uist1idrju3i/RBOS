sleep_ms(10) until $p1_done
button = Button.new(:sw0)
loop do
  button.poll
  sleep_ms(10)
end
