Task.current.name = "mutex_owner"
Task.current.priority = 180
$fault_mutex.lock
$fault_owner_ready = true
if $fault_mode == "ensure"
  begin
    begin
      sleep_ms 10000
    ensure
      $fault_mutex.unlock
      $fault_unlocked = true
    end
  rescue RuntimeError
    $fault_rescued = true
  end
elsif $fault_mode == "inversion"
  until $fault_mid_start
    sleep_ms 100
  end
  sleep_ms 50
  $fault_mutex.unlock
  $fault_unlocked = true
else
  sleep_ms 10000
end
