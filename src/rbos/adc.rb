class ADC
  def read_raw
    __measure(false)
  end

  def read_voltage
    __measure(true)
  end

  alias read read_voltage

  def __measure(voltage)
    request = __start(voltage)
    begin
      loop do
        result = __poll(request)
        return result unless result.nil?
        sleep_ms(1)
      end
    ensure
      __finish(request)
    end
  end
end
