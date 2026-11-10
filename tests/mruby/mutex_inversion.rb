def fault_check(condition, item)
  unless condition
    puts "FAIL: #{item}"
    raise item
  end
  puts "PASS: #{item}"
end

Task.current.priority = 0
$fault_mutex = Mutex.new
$fault_mode = "inversion"
$fault_owner_ready = false
$fault_waiter_entered = false
$fault_acquired = false
$fault_unlocked = false
$fault_high_start = false
$fault_mid_start = false
$fault_mid_stop = false
$fault_mid_busy = false
$fault_mid_stopped = false
$fault_mid_count = 0
20.times do
  break if $fault_owner_ready
  sleep_ms 100
end
fault_check($fault_owner_ready, "inversion low owner holds lock")
$fault_mid_start = true
$fault_high_start = true
20.times do
  break if $fault_waiter_entered && $fault_mid_busy && Task.get("mutex_waiter").status == "WAITING MUTEX"
  sleep_ms 100
end
owner = Task.get("mutex_owner")
middle = Task.get("mutex_middle")
high = Task.get("mutex_waiter")
fault_check(owner && middle && high, "inversion tasks present")
fault_check(high.status == "WAITING MUTEX" && $fault_mid_busy, "inversion high blocked with middle busy")
sleep_ms 500
fault_check(owner.status == "READY" && owner.priority == 180, "inversion owner ready but not boosted")
fault_check($fault_mid_busy && $fault_mid_count > 0 && !$fault_acquired, "inversion high cannot acquire during middle work")
$fault_mid_stop = true
20.times do
  break if $fault_acquired && $fault_mid_stopped
  sleep_ms 100
end
fault_check($fault_unlocked && $fault_acquired && $fault_mid_stopped, "inversion high acquires after middle stops")
owner.join
middle.join
high.join
fault_check(!$fault_mutex.locked?, "inversion mutex unlocked after high")
puts "PASS: mutex priority inversion"
