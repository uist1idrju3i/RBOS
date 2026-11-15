value = 'bytecode original'
value[0] = 'B'
raise 'Bytecode String mutation missing' unless value == 'Bytecode original'
puts 'PASS: bytecode String changed'

rescued = false
ensured = false
begin
  raise 'bytecode catch table probe'
rescue RuntimeError
  rescued = true
ensure
  ensured = true
end
raise 'Bytecode rescue missing' unless rescued
puts 'PASS: bytecode rescue executed'
raise 'Bytecode ensure missing' unless ensured
puts 'PASS: bytecode ensure executed'
