---
layout: native
title: MUTABLE
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/mutable/
native: mutable
spec: |
  "Return reference with mutable access to its argument (if not LOCK-ed)"
  return: [element?]
  value "Argument to change access to (if such access can be granted)"
      [element?]
---

MUTABLE clears the const bit on a value, giving back a reference that can
be used to modify the series it points to.  It undoes
[CONST](/docs/natives/const/):

```
>> data: [a b c]
== [a b c]

>> data-readonly: const data
== [a b c]

>> append mutable data-readonly 'd
== [a b c d]

>> data
== [a b c d]
```

## Getting Past the Wave of Constness

The most common use of MUTABLE is in function bodies and loop bodies, whose
literal source the evaluator makes const (see
[Constness](/docs/concepts/constness/)).  If you really do want a literal
series in a body to be modified each time through, say so:

```
>> repeat 2 [append mutable [] <legal>]
== [<legal> <legal>]
```

The `[]` is one series that lives in the body, so the second pass appended
to the same block as the first.  That's the "magic static" pattern, and
it's something you have to ask for: without MUTABLE it's an error.

<!-- doctest: negative-test match="const-value" -->
```
repeat 2 [append [] <illegal>]
```

A function returning a literal from its body gives back a const value, so
callers can't change the function's source by accident.  MUTABLE lets a
caller do it on purpose:

<!-- doctest: positive-test -->
```
symbol-to-string: func [s] [
    return switch s [
        '+ ["plus"]
        '- ["minus"]
    ]
]

p: symbol-to-string '+
p: mutable p
insert p "you-" append p "-asked-for-it"
assert ["you-plus-asked-for-it" = symbol-to-string '+]
```

## It Can't Undo PROTECT or FREEZE

MUTABLE only affects the const bit on the value.  It can't make a series
writable if the series itself has been locked:

<!-- doctest: negative-test match="series-frozen" -->
```
frozen: freeze [a b c]
append mutable frozen 'd
```

## MUTABLE Is Impure

MUTABLE is an [IMPURE](/docs/natives/impure/) native.  Code running in a
[PURE](/docs/natives/pure/) function relies on const values staying const,
so it isn't allowed to call MUTABLE.

## See Also

* [CONST](/docs/natives/const/) -- the opposite of MUTABLE
* [Constness](/docs/concepts/constness/) -- the full story
