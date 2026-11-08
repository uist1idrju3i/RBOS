Task.name = "scheduler"
$mutex = Mutex.new
$count = 0
Task.current.priority = 200
a = Task.get("worker_a")
b = Task.get("worker_b")
raise "missing worker" unless a && b
a.join
b.join
raise "incorrect task values" unless a.value == 42 && b.value == 43
raise "mutex lost updates" unless $count == 6
begin
  raise "rescued exception"
rescue RuntimeError
  puts "PASS: rescued exception"
end
puts "PASS: scheduler / sleep_ms / priority / pass / Mutex / join / value"
