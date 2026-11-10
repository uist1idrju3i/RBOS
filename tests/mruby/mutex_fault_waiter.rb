Task.current.name = "mutex_waiter"
Task.current.priority = 40
until $fault_high_start
  sleep_ms 100
end
$fault_waiter_entered = true
$fault_mutex.lock
$fault_acquired = true
$fault_mutex.unlock
