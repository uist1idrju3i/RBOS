Task.current.priority = 0
$fault_mutex = Mutex.new
$fault_mode = "terminate"
$fault_owner_ready = false
20.times do
  break if $fault_owner_ready
  sleep_ms 100
end
unless $fault_owner_ready && $fault_mutex.locked?
  puts "FAIL: non-owner unlock setup"
  raise "non-owner unlock setup"
end
Task.get("mutex_owner").terminate
puts "PASS: non-owner unlock ready"
$fault_mutex.unlock
puts "FAIL: non-owner unlock returned"
raise "non-owner unlock returned"
