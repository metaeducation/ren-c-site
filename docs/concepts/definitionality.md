---
layout: default
title: Definitionality
parent: Concepts
nav_order: 3
permalink: /docs/concepts/definitionality/
---

# Definitionality

Rebol's big promise is that control constructs like IF and WHILE are
ordinary functions, so you can write your own.  That promise breaks
whenever something in the language finds its target by searching up the
stack at runtime: whatever happens to be in between can intercept it.

Revolt's answer, applied again and again, is to make things
**definitional**: tied to the function or loop that *defined* them, so
that nothing in between can catch them by accident.

| | Belongs to | Instead of |
|---|---|---|
| RETURN | the function it's written in | the nearest function on the stack |
| BREAK, CONTINUE | the loop whose body it's written in | the nearest loop on the stack |
| THROW | the CATCH it's written in | the nearest CATCH on the stack |
| A [failure](/docs/datatypes/failure/) | the function that returns it, to its caller | any code anywhere above that catches errors |

## Definitional Return

### The Problem

In historical Rebol, RETURN went to whichever function happened to be
nearest on the stack when it ran.  So the obvious way to write UNLESS, in
terms of IF, silently gave wrong answers:

```text
rebol2>> unless: func [cond block] [if not cond block]

rebol2>> bar: func [x] [unless x = 10 [return "not 10"] return "it's 10!"]

rebol2>> bar 20
== "it's 10!"    ; UNLESS caught the RETURN meant for BAR
```

The RETURN in BAR's block was caught by UNLESS, the nearest function, and
BAR carried on.  No error: just the wrong answer.  Rebol2 had a `[throw]`
attribute to make a function let RETURNs through, but every wrapper author
had to remember it, and it didn't cover BREAK.

### In Revolt

The same wrapper works, with nothing to opt into:

<!-- doctest: positive-test -->
```
my-unless: func [cond block] [return if not cond (block)]

bar: func [x] [
    my-unless x = 10 [return "not 10"]
    return "it's 10!"
]

assert ["not 10" = bar 20]
assert ["it's 10!" = bar 10]
```

The block `[return "not 10"]` was written inside BAR, so its RETURN is
BAR's, wherever the block ends up being run.  MY-UNLESS has a RETURN of
its own, and uses it, but the two can't be confused.

(The group around `block` is needed because IF takes its branch literally.
Passing a variable holding a block means evaluating it first.)

This works for the same reason that a block written in a function sees
that function's variables: see [Binding](/docs/concepts/binding/).  RETURN
is found through the binding of the code, like any other word, not by
searching the stack.

## Definitional Break: Loops That Compose

BREAK is definitional too, which matters as soon as you build a loop out
of other loops.  Here is FOR-BOTH, which runs a body over two blocks in
turn:

<!-- doctest: positive-test -->
```
for-both: lambda [@(var) blk1 blk2 body] [
    unlift* all [
        ^ lift* for-each (var) blk1 body
        ^ lift* for-each (var) blk2 body
    ]
]
```

A BREAK in the body stops the whole thing, not just the first loop:

<!-- doctest: positive-test -->
```
seen: copy []
for-both 'x [1 2] [3 4] [
    if x = 2 [break]
    append seen x
]
assert [seen = [1]]
```

And the result is the last thing the body produced, even when the second
block is empty:

<!-- doctest: positive-test -->
```
assert [40 = for-both 'x [1 2] [3 4] [x * 10]]
assert [20 = for-both 'x [1 2] [] [x * 10]]
```

In historical Rebol neither works.  A broken FOREACH returned NONE, and so
did a FOREACH whose body ended in NONE, so a wrapper couldn't tell whether
to run the second loop.  And an empty second loop's NONE replaced the
first loop's result.  The information wasn't lost by the wrapper.  There
was nowhere to put it.

In Revolt, "the loop was broken" is a distinct signal (a NULL that no
body result can be mistaken for, since the result of a body that gives NULL
comes back "heavy"), so ALL can stop on it.  LIFT and UNLIFT carry each
loop's result through ALL without anything being decayed or lost.

## Definitional THROW

THROW goes to the CATCH it was written inside, so a function that uses
CATCH for its own purposes can run your code without intercepting your
THROWs:

<!-- doctest: positive-test -->
```
run-and-tag: func [code] [
    let result: catch [eval code, throw <wrapper-done>]
    return reduce [result]
]

assert [<from-caller> = catch [run-and-tag [throw <from-caller>]]]
assert [[<wrapper-done>] = catch [throw run-and-tag [10 + 20]]]
```

The THROW in `[throw <from-caller>]` was written in the outer CATCH, so it
goes there, straight past RUN-AND-TAG and its CATCH.  If THROW went to the
nearest CATCH on the stack, RUN-AND-TAG would have caught it and given back
`[<from-caller>]`.

## Definitional Errors

The same idea applies to errors.  In historical Rebol an error raised
anywhere travels up until something catches it, so code meant to handle
"this function couldn't do it" also catches every bug in everything that
function calls.

In Revolt, a function that wants its caller to handle a problem *returns*
a failure, and only that caller sees it.  A failure inside the function
that the function doesn't return becomes a panic instead, so it can't be
mistaken for the function's own answer.  That's covered in
[FAILURE!](/docs/datatypes/failure/#failures-are-definitional).

## See Also

* [Binding](/docs/concepts/binding/) -- how RETURN finds its function
* [FAILURE!](/docs/datatypes/failure/) -- definitional errors
* [Isotopes](/docs/concepts/isotopes/) -- how a loop's result can carry
  "broken" without being mistaken for data
* [What Are Definitional Returns?](https://revolt.metaeducation.com/forum/t/what-are-definitional-returns/2191)
  (forum)
* [FOR-BOTH: Loop Composability For The Win](https://revolt.metaeducation.com/forum/t/for-both-loop-composability-for-the-win/1833)
  (forum)
