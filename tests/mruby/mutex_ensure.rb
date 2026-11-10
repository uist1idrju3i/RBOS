def fault_check(condition, item)
  unless condition
    puts "FAIL: #{item}"
    raise item
  end
  puts "PASS: #{item}"
end

Task.current.priority = 0
$fault_mutex = Mutex.new
$fault_mode = "ensure"
$fault_owner_ready = false
$fault_waiter_entered = false
$fault_acquired = false
$fault_unlocked = false
$fault_rescued = false
$fault_high_start = false
20.times do
  break if $fault_owner_ready
  sleep_ms 100
end
fault_check($fault_owner_ready, "ensure owner holds lock")
$fault_high_start = true
20.times do
  break if $fault_waiter_entered && Task.get("mutex_waiter").status == "WAITING MUTEX"
  sleep_ms 100
end
owner = Task.get("mutex_owner")
waiter = Task.get("mutex_waiter")
fault_check(waiter && waiter.status == "WAITING MUTEX", "ensure waiter blocked")
owner.raise(RuntimeError.new("mutex ensure fault"))
20.times do
  break if $fault_acquired && $fault_rescued
  sleep_ms 100
end
fault_check($fault_unlocked && $fault_rescued && $fault_acquired, "ensure unlock hands mutex to waiter")
owner.join
waiter.join
fault_check(!$fault_mutex.locked?, "ensure mutex unlocked after waiter")
puts "PASS: mutex ensure release"
