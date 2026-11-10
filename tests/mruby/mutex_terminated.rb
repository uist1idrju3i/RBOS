def fault_check(condition, item)
  unless condition
    puts "FAIL: #{item}"
    raise item
  end
  puts "PASS: #{item}"
end

Task.current.priority = 0
$fault_mutex = Mutex.new
$fault_mode = "terminate"
$fault_owner_ready = false
$fault_waiter_entered = false
$fault_acquired = false
$fault_high_start = false
20.times do
  break if $fault_owner_ready
  sleep_ms 100
end
fault_check($fault_owner_ready, "terminated owner holds lock")
$fault_high_start = true
20.times do
  break if $fault_waiter_entered && Task.get("mutex_waiter").status == "WAITING MUTEX"
  sleep_ms 100
end
owner = Task.get("mutex_owner")
waiter = Task.get("mutex_waiter")
fault_check(waiter && waiter.status == "WAITING MUTEX", "termination waiter blocked")
owner.terminate
fault_check(owner.status == "DORMANT" && $fault_mutex.locked?, "terminated owner leaves mutex locked")
sleep_ms 200
fault_check(!$fault_acquired && waiter.status == "WAITING MUTEX", "terminated mutex waiter cannot acquire")
waiter.terminate
fault_check(waiter.status == "DORMANT", "terminated mutex waiter cleaned up")
puts "PASS: mutex owner termination"
