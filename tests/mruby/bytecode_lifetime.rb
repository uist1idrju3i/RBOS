class BytecodeLifetime
  def self.retained_bytecode_probe
    :retained_bytecode_symbol
  end
end
puts 'PASS: bytecode lifetime producer'
