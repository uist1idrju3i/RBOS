while !$interrupt_now
  Task.pass
end
Task.get("subject").raise
