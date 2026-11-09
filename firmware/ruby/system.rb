while true
  begin
    sleep_ms RBOSSystem.service
  rescue Exception => error
    puts "System service error: #{error}"
    sleep_ms 10
  end
end
