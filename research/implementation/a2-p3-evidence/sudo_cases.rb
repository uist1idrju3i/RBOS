def check(condition, name)
  raise name unless condition
end

class Privilege
  def self.sudo(token)
    ticket = enter(token)
    begin
      yield
    ensure
      leave(ticket)
    end
  end
end

check(!Proof.active?, "initial privilege")
Privilege.sudo("fixture") {}
check(!Proof.active?, "empty block cleanup")
begin
  Privilege.sudo("bad") {}
  raise "bad token accepted"
rescue ArgumentError
end
check(!Proof.active?, "bad token cleanup")
begin
  Privilege.sudo("fixture")
rescue Exception
end
check(!Proof.active?, "missing block cleanup")

Privilege.sudo("fixture") do
  check(Proof.active?, "entry")
  Privilege.sudo("fixture") { check(Proof.active?, "nested entry") }
  check(Proof.active?, "nested restoration")
  child = Task.create(Proof.bytecode("child"))
  child.run
  while !$child_checked
    Task.pass
  end
  check($child_checked, "child scheduler progress")
  check(Proof.active?, "parent restore after task switch")
  $escaped = Proc.new { Proof.active? }
end
check(!Proof.active?, "normal cleanup")
check(!$escaped.call, "escaped proc privilege")
puts "PASS TCB-local scope, nested scope, empty/error input, child isolation and noncapturing escaped Proc"

begin
  Privilege.sudo("fixture") { raise ArgumentError, "inside" }
rescue ArgumentError
end
check(!Proof.active?, "exception cleanup")
result = Privilege.sudo("fixture") { break 17 }
check(result == 17 && !Proof.active?, "break cleanup")
def return_from_scope
  Privilege.sudo("fixture") { return 23 }
end
check(return_from_scope == 23 && !Proof.active?, "return cleanup")
puts "PASS ensure cleanup on exception, break and nonlocal return"

Task.current.name = "subject"
killer = Task.create(Proof.bytecode("raise"))
killer.run
begin
  Privilege.sudo("fixture") do
    $interrupt_now = true
    sleep_ms 20
    raise "external raise did not arrive"
  end
rescue RuntimeError => error
  check(error.message != "external raise did not arrive", "external delivery")
end
check(!Proof.active?, "Task raise cleanup")
puts "PASS ensure cleanup after another Task raises into sleeping elevated task"

class SharedHook
  def self.run
    Proof.active?
  end
end
Privilege.sudo("fixture") do
  check(SharedHook.run, "shared method runs elevated")
end
puts "REPRODUCED user-defined shared method runs with caller elevated privilege"

Privilege.native_scope("fixture") do
  check(!Proof.active?, "native callback returned before block")
end
puts "REPRODUCED C callback after Proc.call runs before Ruby block executes"

victim = Task.create(Proof.bytecode("victim"))
victim.run
while !$victim_elevated
  Task.pass
end
victim.terminate
check(!$victim_ensured && Proof.death_revocations > 0, "terminate bypasses ensure")
puts "REPRODUCED terminate skips Ruby ensure; native HAL observer revoked capability"

class Privilege
  def self.leave(ticket)
  end
end
Privilege.sudo("fixture") {}
check(Proof.active?, "redefined leave bypass")
Proof.reset
puts "REPRODUCED shared Ruby cleanup method replacement bypasses ensure-based demotion"
puts "PASS sudo semantic probe complete (authentication is a fixture, not HMAC)"
