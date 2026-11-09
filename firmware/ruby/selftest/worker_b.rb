Task.current.name = "worker_b"
Task.current.priority = 128
while $p1_phase == "busy"
  $p1_counts[1] = ($p1_counts[1] + 1) % 1000000
end
4.times do
  $p1_mutex.lock
  begin
    count = $p1_shared
    sleep_ms 5
    $p1_shared = count + 1
  ensure
    $p1_mutex.unlock
  end
end
