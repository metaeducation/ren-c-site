---
layout: native
title: FINAL
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/final/
native: final
spec: |
  "Make an immutable value that has CELL_FLAG_FINAL for a variable"
  return: [any-value?]
  ^value [any-value?]
---

FINAL does two things to a value:

1. It deeply freezes it, so the value (and anything it contains) can never
   be modified again.

2. It marks it so that the variable it's assigned to can't be changed
   afterward.

```rebol
>> x: final [a b c]
== [a b c]
```

Now the series can't be changed:

<!-- doctest: negative-test match="series-frozen" -->
```rebol
append x 'd
```

And neither can the variable:

<!-- doctest: negative-test match="final-variable" -->
```rebol
x: [d e f]
```

## What FINAL Is For

FINAL is what makes [PURE](/docs/natives/pure/) functions possible.  A pure
function's answer may only depend on its arguments and on outside state
that can never change.  FINAL is how a variable promises that:

```rebol
>> /length-of-x: pure lambda [] [length of x]

>> length-of-x
== 3
```

If `x` hadn't been FINAL, calling `length-of-x` would be an error.  See
[Purity](/docs/concepts/purity/).

## Reading a FINAL Variable

Finality belongs to the variable.  When you read a FINAL variable, you get
a value that's still frozen, but assigning it somewhere else doesn't make
another FINAL variable:

```rebol
>> y: x
== [a b c]

>> y: 10
== 10
```

## Functions Defined With /NAME:

Assigning with a leading slash, as in `/name: ...`, makes the variable
FINAL for you.  It only accepts actions, so it's the way to define a
function that can't be redefined out from under the code that calls it:

<!-- doctest: positive-test -->
```rebol
/double: lambda [n] [n * 2]
assert [20 = double 10]
```

<!-- doctest: negative-test match="final-variable" -->
```rebol
double: lambda [n] [n * 3]
```

## Undoing FINAL

UNPROTECT can release a FINAL variable so it can be assigned again:

<!-- doctest: positive-test -->
```rebol
unprotect $double
double: lambda [n] [n * 3]
assert [30 = double 10]
```

UNPROTECT is IMPURE, so pure code can't do this.  The *value* stays frozen:
FINAL's freezing is permanent.

## FINAL vs. CONST vs. FREEZE vs. PROTECT

| | Affects | Undo with |
|---|---|---|
| [CONST](/docs/natives/const/) | One reference to a series | [MUTABLE](/docs/natives/mutable/) |
| PROTECT | A series (all references to it), or a variable | UNPROTECT |
| FREEZE | A series, permanently (deeply with `:deep`) | Can't |
| FINAL | The variable, plus a deep FREEZE of the value | UNPROTECT (variable only) |

## See Also

* [PURE](/docs/natives/pure/) -- functions that may only see FINAL outside state
* [Purity](/docs/concepts/purity/)
* [Pure Functional Programming in Revolt](https://revolt.metaeducation.com/forum/t/pure-functional-programming-in-ren-c/2675)
  (forum)
