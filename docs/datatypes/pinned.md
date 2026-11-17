---
layout: datatype
title: PINNED!
parent: Decorated Types
grand_parent: Datatypes
nav_order: 4
permalink: /docs/datatypes/pinned/
datatype: pinned!
sigil: '@'
---

A value with the PIN sigil, `@`, on the front: `@x`, `@[a b]`, `@(a b)`.
See [Sigils](/docs/datatypes/decorated/#sigils) for what all three sigils have
in common.

## What the Evaluator Does With It

A pinned value is inert: it evaluates to itself, sigil included.

```
>> @foo
== @foo

>> @[a b]
== @[a b]

>> reduce [1 + 2 @(1 + 2)]
== [3 @(1 + 2)]
```

What it picks up on the way is a binding, the same one a
[tied](/docs/datatypes/tied/) value would get.  So the word that comes
out still knows where it was written, which a quoted one doesn't:

<!-- doctest: positive-test -->
```
x: 10
v: @x
assert [10 = get unpin v]
assert [null = binding of '@x]
```

That makes it a way to hand something to a function with a mark on it
that says "take this as it is".  Several built-in functions read it that
way.  ANY and ALL treat a pinned block as values to test, not expressions
to run.  JOIN doesn't evaluate one:

```
>> any [1 + 2]
== 3

>> any @[1 + 2]
== 1

>> join text! @[1 + 1]
== "1+1"
```

## In a Parameter List

`@name` means the argument is taken literally from the call:

<!-- doctest: positive-test -->
```
name-of: func [@what] [return what]

assert ['foo = name-of foo]
assert ['(1 + 2) = name-of (1 + 2)]
```

## Making One

PIN adds the sigil and UNPIN takes it off:

```
>> pin 'x
== @x

>> unpin '@x
== x
```

Written alone, `@` takes what follows literally:

```
>> @ foo
== foo
```

## See Also

* [Decorated Types](/docs/datatypes/decorated/) -- TIE, PIN and META, and the other decorations
* [Binding](/docs/concepts/binding/) -- why a value needs one
