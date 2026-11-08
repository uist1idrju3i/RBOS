# 非対応 idiom の実行入力

[版・実行コマンド・結果と hash](capability-probes.md)に対応する入力です。各 ID を別々の UTF-8 / LF の `.rb` として保存し、独立した runner process で実行しました。下記は実験入力であり、製品コードの書式例ではありません。

## freeze

```ruby
puts [1].freeze
```

## symbol-proc

```ruby
puts [1,2].map(&:to_s)
```

## reduce

```ruby
puts [1,2,3].reduce(0) { |sum,n| sum+n }
```

## inject

```ruby
puts [1,2,3].inject(0) { |sum,n| sum+n }
```

## enumerator

```ruby
puts Enumerator
```

## each-no-block

```ruby
puts [1,2].each
```

## lambda

```ruby
puts ->(v) { v+1 }.call(2)
```

## fiber

```ruby
puts Fiber
```

## regexp

```ruby
puts /x/.match("x")
```

## time

```ruby
puts Time
```

## io

```ruby
puts IO
```

## classvar

```ruby
class Reading; @@value=1; end
```

## undef

```ruby
class Reading; def read; 1; end; undef read; end
```

## outer-const

```ruby
module Board; end; Board::PIN=1
```

## int64-literal

```ruby
puts 2147483648
```

[調査索引へ戻る](../README.md)
