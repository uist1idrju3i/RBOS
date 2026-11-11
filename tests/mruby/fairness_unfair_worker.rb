Task.current.name = "worker_a"
Task.current.priority = 128
deadline = VM.tick + 3000
while $p1_phase == "busy" && VM.tick < deadline
  $p1_counts[0] = ($p1_counts[0] + 100) % 1000000
end
Task.get("worker_b").terminate
