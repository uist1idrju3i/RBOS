raise 'Bytecode retained method failed' unless BytecodeLifetime.retained_bytecode_probe == :retained_bytecode_symbol
puts 'PASS: bytecode lifetime consumer'
