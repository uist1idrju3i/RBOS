values = [1, 2, 1]
raise "map" unless values.map { |value| value * 2 } == [2, 4, 2]
raise "select" unless values.select { |value| value > 1 } == [2]
raise "reject" unless values.reject { |value| value > 1 } == [1, 1]
raise "matching count" unless values.select { |value| value == 1 }.size == 2
raise "explicit block" unless values.map { |value| value.to_s } == ["1", "2", "1"]

sum = 0
values.each { |value| sum += value }
raise "accumulator" unless sum == 4

indexed = []
values.each_with_index { |value, index| indexed << value + index }
raise "indexed iteration" unless indexed == [1, 3, 3]
raise "predicate" unless values.all? { |value| value > 0 }
raise "existence" unless values.any? { |value| value == 2 }

empty = []
raise "empty map" unless empty.map { |value| value.to_s } == []
raise "empty select" unless empty.select { |value| value == 1 }.size == 0
raise "empty reject" unless empty.reject { |value| value == 1 } == []
raise "empty all" unless empty.all? { |value| false }
raise "empty any" if empty.any? { |value| true }
empty_sum = 0
empty.each { |value| empty_sum += value }
raise "empty accumulator" unless empty_sum == 0

puts "PASS: idiom collections / explicit blocks / matching count / empty inputs"
