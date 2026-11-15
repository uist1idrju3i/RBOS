begin
  Privileged.mark
rescue RuntimeError
end
class RBOSSystem
  def self.service
    Privileged.mark
    1
  end
end
