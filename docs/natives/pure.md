---
layout: native
title: PURE
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/pure/
native: pure
spec: |
  "Modifier: Can't call IMPURE functions or consult non-FINAL external state"
  return: [action! frame!]
  ^value [action! frame!]
  :off "Give back non-pure version of the passed in function"
---

PURE takes a function and makes it a *pure function*: one whose result
depends only on its arguments.  While it runs, the function (and anything
it calls) may not:

* call an [IMPURE](/docs/natives/impure/) function, such as RANDOM, NOW,
  PRINT, or READ
* read or write a variable from outside the function, unless that variable
  is [FINAL](/docs/natives/final/)

```
>> /slow-is-word?: pure lambda [value] [word! = type of value]

>> slow-is-word? 'abba
== \~okay~\  ; antiform (logic!)

>> slow-is-word? 1020
== \~null~\  ; antiform (logic!)
```

`word!`, `=`, `type`, and `of` all come from outside the function, but
they're FINAL, so pure code can use them.

## Calling Impure Functions Is an Error

<!-- doctest: negative-test match="impure-call" -->
```
roll: pure does [random 6]
roll
```

It doesn't matter how indirect the call is.  If a function that isn't
marked either way calls an IMPURE one, that's an error when it runs under a
pure function too:

<!-- doctest: negative-test match="impure-call" -->
```
/helper: does [random 6]
roll: pure does [helper]
roll
```

## Outside Variables Must Be FINAL

Reading or writing a non-FINAL variable from outside the function is an
error, because nothing stops that variable from changing between calls:

<!-- doctest: negative-test match="pure-non-final" -->
```
x: 10
peek-x: pure does [x]
peek-x
```

<!-- doctest: negative-test match="pure-non-final" -->
```
x: 10
poke-x: pure does [x: 20]
poke-x
```

If the variable is FINAL, reading it is fine:

<!-- doctest: positive-test -->
```
x: final [a b c]
peek-x: pure does [x]
assert [peek-x = [a b c]]
```

## Local State Is Fine

Pure doesn't mean "nothing changes".  A pure function can have local
variables, and can create new series and modify them, because nobody
outside can see them:

<!-- doctest: positive-test -->
```
/evens-of: pure lambda [block] [
    let result: copy []
    for-each 'item block [
        if even? item [append result item]
    ]
    result
]
assert [[2 4] = evens-of [1 2 3 4 5]]
```

## Results Can't Be Thrown Away

A pure function has no side effects.  So calling one and ignoring the
result can't have been what you meant, and the evaluator treats it like
discarding a literal value:

<!-- doctest: negative-test match="discarded-value" -->
```
ten-twenty: pure does [1000 + 20]
ten-twenty 304
```

(`ten-twenty` takes no arguments, so its result was dropped on the floor
before the evaluator moved on to `304`.)

## PURE:OFF

`pure:off` gives back a function that isn't pure.  A function can't be both
PURE and IMPURE, so trying to mark an IMPURE function PURE is an error:

<!-- doctest: negative-test match="Can't mark impure function pure" -->
```
pure impure does [random 6]
```

{: .note }
> PURE currently changes the function it's given, rather than making a
> pure copy.  Other references to the same function become pure too.

## See Also

* [IMPURE](/docs/natives/impure/) -- mark a function as having side effects
* [FINAL](/docs/natives/final/) -- the variables pure code may see
* [Purity](/docs/concepts/purity/) -- how it works
* [Pure Functional Programming in Revolt](https://revolt.metaeducation.com/forum/t/pure-functional-programming-in-ren-c/2675)
  (forum)
