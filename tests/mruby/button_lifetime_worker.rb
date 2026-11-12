button = Button.new(:sw0)
loop do
  event = button.wait
  raise 'Button stale edge reached reused VM' unless event == [1, 1]
  button.close
  puts 'PASS: Button reused VM received current edge'
  break
end
