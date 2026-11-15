---
layout: default
title: Purity
parent: Concepts
grand_parent: Documentation
nav_order: 6
permalink: /docs/concepts/purity/
---

# Purity

A *pure* function is one whose result depends only on its arguments.
Call it twice with the same arguments and you get the same answer, and
calling it doesn't affect anything else.  Pure functions are easier to
reason about, test, cache and optimize.

Revolt lets you mark a function [PURE](/docs/natives/pure/), and then checks
while it runs that it stays that way.

{: .warning }
> Purity is new (2026) and still being worked out.  The basic rules on
> this page are in place, but details may change.

## The Two Rules

While a pure function is running, code inside it may not:

1. **Call an IMPURE function.**  Natives that read the clock, generate
   random numbers, do input or output, or take away protections are marked
   [IMPURE](/docs/natives/impure/).

2. **Look at outside state that could change.**  Any variable from outside
   the function that it reads or writes must be [FINAL](/docs/natives/final/).

<!-- doctest: positive-test -->
```
/square: pure lambda [n] [n * n]
assert [100 = square 10]
```

`*` comes from outside SQUARE, but it's FINAL, so SQUARE may use it.

## Why the Second Rule?

Just banning IMPURE calls isn't enough, because functions are values held
in variables.  Here's a function that isn't marked IMPURE, but whose answer
depends on what day it is:

<!-- doctest: positive-test -->
```
/square-of: func [x] [
    if now:weekday > 5 [  ; 6 = Saturday, 7 = Sunday
        return "I don't do math on weekends!"
    ]
    return x * x
]
```

Calling it from pure code fails when it reaches NOW:

<!-- doctest: negative-test match="impure-call" -->
```
1 + eval pure does [square-of 2]
```

(SQUARE-OF was defined with `/square-of:`, which makes the variable FINAL.
Otherwise the call would have failed even sooner, as described next.)

Now imagine SQUARE-OF had read a variable `weekday` instead of calling NOW.
No IMPURE call would be involved, but anyone could set `weekday`, or
replace SQUARE-OF itself, and the same call would give different answers.
So pure code may only see variables that can never change, which is what
FINAL means:

<!-- doctest: negative-test match="pure-non-final" -->
```
x: 10
foo: pure does [x]
foo
```

<!-- doctest: positive-test -->
```
x: final [a b c]
foo: pure does [x]
assert [foo = [a b c]]
```

That's why the `/name:` way of defining functions makes the variable
FINAL: so pure code can call them.

## Neither Pure Nor Impure

Most functions aren't marked either way, and that's deliberate.  IF,
APPEND, FOR-EACH and so on need to work in pure code and impure code
alike.  A function that isn't marked only breaks the rules if it *does*
something impure when called from a pure function.  It doesn't matter how
far down the call is:

<!-- doctest: negative-test match="impure-call" -->
```
/bad: impure does [print "side effect"]
/middleman: does [bad]
caller: pure does [middleman]
caller
```

## What Pure Code *Can* Change

Pure doesn't mean nothing changes.  A pure function can:

* **Use its own variables**, including LET variables and loop variables,
  because nobody outside can see them.

* **Make new series and modify them**, for the same reason.

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

* **Modify its arguments**, if they aren't [const](/docs/concepts/constness/).
  APPEND isn't impure: what it changes is a series you passed it.  Whether
  that's allowed is the const bit's job, not purity's.

And since [MUTABLE](/docs/natives/mutable/) is IMPURE, pure code can't take
the const bit off anything.  [CONST](/docs/natives/const/) is pure, since
adding protection is always safe.

## How It Works: Purity Follows Binding

Revolt doesn't keep a global "now in pure mode" flag.  Pure-ness is part of
the [binding](/docs/concepts/binding/) that code runs with, the same
machinery that makes local variables visible to a function body.  When pure
code looks up a word, the search goes from the innermost scopes outward.
Variables found before it reaches the pure function's own frame belong to
that function and may be used freely.  Anything found beyond it is outside
state, and has to be FINAL.

One effect of this: a pure function nested inside another pure function
can't touch the outer one's local variables.  To the inner function, those
are outside state.

## Pure Results Can't Be Discarded

If a pure function has no side effects, then calling it and ignoring the
result is pointless, and is almost certainly a mistake.  The evaluator
treats it like discarding a literal value:

<!-- doctest: negative-test match="discarded-value" -->
```
ten-twenty: pure does [1000 + 20]
ten-twenty 304
```

## Open Questions

The forum thread on purity discusses problems still being worked on, such
as:

* Infix functions that can take their left-hand argument literally, as in
  `value: type of value`, where TYPE should not be asked whether it wants
  to take VALUE literally.

* Whether adding a new FINAL definition to a module should be allowed, if
  it could change which variable pure code sees for a word.

## See Also

* [PURE](/docs/natives/pure/), [IMPURE](/docs/natives/impure/),
  [FINAL](/docs/natives/final/)
* [Constness](/docs/concepts/constness/)
* [Pure Functional Programming in Revolt](https://revolt.metaeducation.com/forum/t/pure-functional-programming-in-ren-c/2675)
  (forum, 2026)
