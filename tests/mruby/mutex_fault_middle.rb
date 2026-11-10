Task.current.name = "mutex_middle"
Task.current.priority = 100
until $fault_mid_start
  sleep_ms 100
end
$fault_mid_busy = true
until $fault_mid_stop
  $fault_mid_count = ($fault_mid_count + 1) % 1000000
end
$fault_mid_busy = false
$fault_mid_stopped = true
