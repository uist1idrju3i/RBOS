begin
  puts ->(value) { value + 1 }.call(2)
rescue StandardError
  puts "unexpected StandardError rescue"
end
