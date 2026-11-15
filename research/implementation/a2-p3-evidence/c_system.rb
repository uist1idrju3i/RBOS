$replacement_calls = 0
class RBOSSystem
  def self.service
    $replacement_calls += 1
    Probe.write(99)
  end
end
begin
  RBOSSystem.service
rescue RuntimeError
end
raise "replacement did not execute" unless $replacement_calls == 1
Probe.write(1)
n = 0
while n < 2000
  n += 1
end
raise "C invoked Ruby replacement" unless $replacement_calls == 1
Probe.report
