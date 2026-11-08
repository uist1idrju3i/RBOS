Task.name = "worker_a"
Task.current.priority = 100
3.times do
  $mutex.lock
  value = $count
  sleep_ms 10
  $count = value + 1
  $mutex.unlock
  Task.pass
end
42
