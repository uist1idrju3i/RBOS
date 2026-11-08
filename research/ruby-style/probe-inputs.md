# 成功した idiom の実行入力

[版・実行コマンド・結果と hash](capability-probes.md)に対応する入力です。各 ID を別々の UTF-8 / LF の `.rb` として保存し、独立した runner process で実行しました。下記は実験入力であり、製品コードの書式例ではありません。

## names

```ruby
class SensorReading
  attr_accessor :value
  def ready?; @value != nil; end
  def reset!; @value = 0; end
end
s = SensorReading.new
raise unless !s.ready?
s.value = 3
s.reset!
raise unless s.ready? && s.value == 0
```

## guard-case

```ruby
def scale(value)
  return nil if value.nil?
  return 0 unless value > 0
  case value
  when 1 then 10
  else value * 2
  end
end
raise unless scale(nil) == nil && scale(0) == 0 && scale(1) == 10 && scale(2) == 4
```

## truth-memo

```ruby
raise unless (0 ? true : false) && ("" ? true : false) && ([] ? true : false)
x = false
x ||= 7
raise unless x == 7
y = false
y &&= 8
raise unless y == false
z = false
z = 9 if z.nil?
raise unless z == false
```

## safe-nav

```ruby
raise unless nil&.size == nil && [1]&.size == 1
```

## collections

```ruby
raise unless [1,2,3].map { |n| n*2 } == [2,4,6]
raise unless [].map { |n| n*2 } == []
raise unless [1,2,3].select { |n| n>1 } == [2,3]
raise unless [].select { |n| n>1 } == []
raise unless [1,2,3].reject { |n| n>1 } == [1]
raise unless [1,2].all? { |n| n>0 } && [].all? { |n| false }
raise unless [1,2].any? { |n| n>1 } && ![].any? { |n| true }
a=[]
[4,5].each_with_index { |v,i| a << v+i }
raise unless a == [4,6]
```

## bounded-loop

```ruby
total=0
3.times { |i| total += i }
raise unless total == 3
i=0
while i<3
  i+=1
end
raise unless i==3
```

## hash

```ruby
h={level: 1}
raise unless h[:level] == 1 && h[:missing] == nil
sum=0
h.each { |k,v| sum+=v }
raise unless sum==1 && {}.size==0
```

## keyword

```ruby
def reading(unit: :raw, scale: 1)
  [unit,scale]
end
raise unless reading == [:raw,1] && reading(scale: 2) == [:raw,2]
begin
  reading(unknown: 1)
  raise "not rejected"
rescue ArgumentError
end
```

## block-proc

```ruby
def apply(value)
  yield value
end
raise unless apply(2) { |v| v+1 } == 3
p=Proc.new { |v| v+1 }
raise unless p.call(2)==3
```

## mixin

```ruby
module Readable
  def level; 1; end
end
class Reading
  include Readable
end
class ScaledReading < Reading
  def level; super + 1; end
end
raise unless ScaledReading.new.level == 2
```

## ensure

```ruby
m=Mutex.new
begin
  m.lock
  raise ArgumentError, "bad sample"
rescue ArgumentError => e
  raise unless e.message == "bad sample"
ensure
  m.unlock if m.owned?
end
raise if m.locked?
```

## standard-rescue

```ruby
begin
  raise Exception, "root failure"
rescue
  puts "WRONG default rescue"
rescue Exception
  puts "root caught explicitly"
end
```

## pattern-array

```ruby
result=case [1,2]
in [first,second]
  first+second
else
  0
end
raise unless result==3
```

## pattern-hash

```ruby
result=case {id: 7}
in {id: id}
  id
else
  0
end
raise unless result==7
```

## pattern-miss

```ruby
begin
  case [1]
  in [a,b]
    puts "wrong"
  end
  raise "not rejected"
rescue NoMatchingPatternError
end
```

## count

```ruby
raise unless [2,3,2].count(2) == 3
raise unless [2,3,2].select { |n| n==2 }.size == 2
```

## privacy

```ruby
class Device
  private
  def secret; 7; end
end
raise unless Device.new.secret == 7
```

## sleep-mutex

```ruby
m=Mutex.new
raise unless m.try_lock && m.owned? && m.locked?
m.unlock
raise if m.locked?
Task.current.priority=128
Task.pass
sleep_ms 1
raise unless Task.current.priority==128
```

## int32

```ruby
x=2147483647
puts x+1
```

## strings

```ruby
name="pin"
raise unless "#{name}=#{2}" == "pin=2"
raise unless %w[on off] == ["on","off"] && %i[on off] == [:on,:off]
s=""
s << "a"
raise unless s == "a"
```

## sum-alternative

```ruby
sum=0
[1,2,3].each { |n| sum += n }
raise unless sum == 6
empty_sum=0
[].each { |n| empty_sum += n }
raise unless empty_sum == 0
```

## bytes

```ruby
raise unless "あ".size == 3
values=[]
"あ".each_char { |c| values << c.size }
raise unless values == [1,1,1]
raise unless "".size == 0 && "\x00A".bytesize == 2
```

[調査索引へ戻る](../README.md)
