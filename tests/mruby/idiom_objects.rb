module ReadableLevel
  def level
    1
  end
end

class SensorReading
  DEFAULT_SCALE = 2
  include ReadableLevel
  attr_accessor :value

  def ready?
    !@value.nil?
  end

  def scaled_value(scale: DEFAULT_SCALE)
    return nil unless ready?

    @value * scale
  end

  def apply
    yield @value
  end
end

class CalibratedReading < SensorReading
  def level
    super + 1
  end
end

reading = CalibratedReading.new
raise "unset reading" if reading.ready?
raise "guard clause" unless reading.scaled_value.nil?
reading.value = 3
raise "predicate" unless reading.ready?
raise "default keyword" unless reading.scaled_value == 6
raise "explicit keyword" unless reading.scaled_value(scale: 4) == 12
raise "mixin and super" unless reading.level == 2
raise "yield" unless reading.apply { |value| value + 1 } == 4

increment = Proc.new { |value| value + 1 }
raise "proc" unless increment.call(3) == 4

begin
  reading.scaled_value(unknown: 1)
  raise "unknown keyword accepted"
rescue ArgumentError
end

puts "PASS: idiom objects / naming / guards / keywords / blocks / Proc.new"
