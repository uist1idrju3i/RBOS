def check(condition, item)
  unless condition
    puts "FAIL: #{item}"
    raise "P1 selftest: #{item}"
  end
  puts "PASS: #{item}"
end

Task.current.name = "coordinator"
Task.current.priority = 20
$p1_counts = [0, 0]
$p1_phase = "busy"
$p1_mutex = Mutex.new
$p1_shared = 0
sleep_ms 100
a = Task.get("worker_a")
b = Task.get("worker_b")
check(a && b && $p1_counts[0] > 0 && $p1_counts[1] > 0, "concurrent workers")
before_a = $p1_counts[0]
before_b = $p1_counts[1]
sleep_ms 100
check($p1_counts[0] != before_a && $p1_counts[1] != before_b, "same-priority round robin")

a.priority = 100
before_a = $p1_counts[0]
before_b = $p1_counts[1]
sleep_ms 100
check(a.priority == 100 && $p1_counts[0] != before_a && $p1_counts[1] == before_b,
      "priority change")
a.priority = 128
a.suspend
before_a = $p1_counts[0]
before_b = $p1_counts[1]
sleep_ms 100
check($p1_counts[0] == before_a && $p1_counts[1] != before_b, "suspend")
a.resume
sleep_ms 100
check($p1_counts[0] != before_a, "resume")

$p1_phase = "mutex"
a.join
b.join
check($p1_shared == 8, "mutex with sleeping owner")
check(a.status == "DORMANT" && b.status == "DORMANT", "workers joined")
started = VM.tick
sleep_ms 30
check(VM.tick > started, "idle wakeup")
puts "PASS: P1 selftest"
