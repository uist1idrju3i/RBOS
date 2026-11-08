cached = false
cached = true if cached.nil?
raise "false cache" unless cached == false
missing = nil
missing = 7 if missing.nil?
raise "nil cache" unless missing == 7

raise "nil navigation" unless nil&.size.nil?
raise "empty navigation" unless ""&.size == 0
raise "value navigation" unless "data"&.size == 4

payload = "\x00A"
raise "binary length" unless payload.bytesize == 2
bytes = []
payload.each_byte { |byte| bytes << byte }
raise "binary bytes" unless bytes == [0, 65]
raise "empty bytes" unless "".bytesize == 0
raise "UTF-8 bytes" unless "あ".bytesize == 3

def bounded_count(value)
  raise RangeError, "count out of range" if value < 0 || value > 65_535

  value
end

raise "zero count" unless bounded_count(0) == 0
raise "positive count" unless bounded_count(12) == 12
raise "maximum count" unless bounded_count(65_535) == 65_535
[-1, 65_536].each do |value|
  begin
    bounded_count(value)
    raise "invalid count accepted"
  rescue RangeError
  end
end

puts "PASS: idiom values / false cache / safe navigation / bytes / bounded integers"
