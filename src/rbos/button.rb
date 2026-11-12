class Button
  def wait
    loop do
      event = poll
      return event unless event.nil?
      sleep_ms(1)
    end
  end

  def each_event
    raise ArgumentError, 'Button.each_event requires a block' unless block_given?
    loop do
      event = wait
      yield event[0], event[1]
    end
  end
end
