Task.current.name = "spinner_b"
Task.current.priority = 128
until $p1_done
  sleep_ms 100
end
puts "STRESS: spinner b started"
count = 0
last = VM.tick
while true
  count = (count + 1) % 1000000
  now = VM.tick
  if now - last >= 10000
    puts "stress b=#{count}"
    last = now
  end
end
