def boundary_denied
  caught = false
  begin
    yield
  rescue RuntimeError => error
    raise 'wrong management refusal' unless error.message == 'Pin is reserved'
    caught = true
  end
  raise 'management permission gained' unless caught
end

class RBOSSystem
  def self.service
    raise 'original Ruby management definition was not replaced'
  end
end

class RBOSSystem
  def self.service
    [:led0, 73, 'P2.9'].each do |pin|
      boundary_denied { GPIO.new(pin, GPIO::OUT) }
      boundary_denied { GPIO.read_at(pin) }
      boundary_denied { GPIO.write_at(pin, 1) }
      boundary_denied { Button.new(pin) }
    end
  end
end

class Supervisor
  def self.poll
    raise 'Ruby supervisor was dispatched'
  end
end

RBOSSystem.service
Probe.report
while true
  1 + 1
end
