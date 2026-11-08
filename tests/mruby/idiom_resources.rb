mutex = Mutex.new
[[], [1], nil].each do |values|
  begin
    mutex.lock
    raise ArgumentError, "missing values" if values.nil?

    raise "owner" unless mutex.owned?
    sleep_ms 1
  rescue ArgumentError => error
    raise "wrong error" unless error.message == "missing values"
  ensure
    mutex.unlock if mutex.owned?
  end
  raise "lock leaked" if mutex.locked?
end

Task.current.priority = 128
Task.pass
sleep_ms 1
raise "task priority" unless Task.current.priority == 128

puts "PASS: idiom resources / specific rescue / ensure / Mutex / task sleep"
