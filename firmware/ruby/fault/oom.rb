Task.current.name = "oom"
puts "OOM: start"
retained = []
while true
  retained << "x" * 1024
end
