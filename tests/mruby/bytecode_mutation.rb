value = 'bytecode original'
value[0] = 'B'
raise 'Bytecode String mutation missing' unless value == 'Bytecode original'
puts 'PASS: bytecode String changed'
