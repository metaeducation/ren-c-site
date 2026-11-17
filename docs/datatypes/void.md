---
layout: datatype
title: VOID!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 5
permalink: /docs/datatypes/void/
datatype: void!
antiform-of: blank!
stable: false
summary: panics on WORD! access, multi-step evaluations discard
sample: 'comment "nothing"'
---

VOID! is the absence of a value.  Its quasiform is a bare tilde, so it
lifts to `~`:

```
>> comment "nothing"
== \~\  ; antiform (void!)

>> lift comment "nothing"
== ~

>> void? comment "nothing"
== \~okay~\  ; antiform (logic!)
```

`COMMENT`, `ELIDE`, an `IF` whose condition was false, and `OPT` of a
null all produce it:

```
>> void? elide 5
== \~okay~\  ; antiform (logic!)

>> void? if null [1]
== \~okay~\  ; antiform (logic!)

>> void? opt null
== \~okay~\  ; antiform (logic!)
```

What a void is mostly *for* is vanishing.

## Vanishing

Some functions leave no trace in an evaluation.  It's as if they weren't
there at all:

```
>> 1 + 2 comment "this is ignored"
== 3

>> 1 + 2 elide 5
== 3

>> 1 + 2 ghost
== 3
```

The `1 + 2` is still the result, even though something else ran after
it.  These are **vanishing** functions, and what they return is a void.
A void at the end of a step means "this step produced nothing", and the
result of the step before it is kept.  That's the whole mechanism.

The harder question, covered [below](#the-danger), is how to *stop*
things from vanishing when they shouldn't.

### What It's For

Vanishing lets you put things in the middle of code without disturbing
what the code produces.

**Comments that are part of the code** can go anywhere, even in the
middle of an ALL:

```
>> all [comment "begin" 1 + 2 10 + 20 comment "end"]
== 30
```

**Side effects between steps** don't change the steps' results.  ELIDE
runs its argument and throws the result away:

<!-- doctest: positive-test -->
```
log: copy []
result: case [
    1 = 2 [<a>]
    elide append log "first condition was false"
    2 = 2 [<b>]
]
assert [result = <b>]
assert [log = ["first condition was false"]]
```

The same works for a debugging `elide print ...` dropped into a
calculation.

## The Danger

If *every* void vanished, though, that would be a problem, because voids
come from lots of places besides COMMENT: an IF whose condition is false,
or EVAL of a block with nothing in it but comments.

Suppose you write:

```text
mode: <reading>, eval code
```

expecting the result to be whatever `code` produced.  If `code` is
`[comment "TODO"]`, and voids from EVAL vanished, the result would be
`<reading>`.  Code that looks like it gives back the last thing it ran
would instead give back something from earlier.  The same goes for a loop
body that ends in an IF:

<!-- doctest: positive-test -->
```
plusones: copy []
result: map-each 'x [1 2 3 4 5] [
    append plusones x + 1
    if odd? x [x * 10]
]
assert [result = [10 30 50]]
```

When `x` is even, the IF gives a void.  If that vanished, the body's
result would be the APPEND's, and the even numbers would add the whole
`plusones` block to the result.  Instead, they add nothing, which is what
you'd expect.

## Ghost Busting

The rule that makes vanishing safe is that **only functions marked
VANISHABLE get to vanish.**  COMMENT, ELIDE and GHOST are vanishable, but
IF and EVAL, and every other function unless you say so, are not:

```
>> vanishable? comment/
== \~okay~\  ; antiform (logic!)

>> vanishable? if/
== \~null~\  ; antiform (logic!)

>> vanishable? eval/
== \~null~\  ; antiform (logic!)
```

When a function that isn't vanishable returns a void as the result of a
step, the evaluator "busts the ghost": it turns the void into a **heavy
void**, which doesn't vanish.  So in a multi-step evaluation, a void from
IF is a result in its own right, and the value before it is a result that
got thrown away, which is an error:

```
>> 1 + 2 if null [3]
** PANIC: Pure evaluation product discarded: 3
```

<!-- doctest: negative-test match="discarded-value" -->
```
mode: <reading>
1 + 2 eval [comment "TODO"]
```

(Passed straight to a function, as in `void? if null [1]` above, the void
stays light.  Busting is about what a step leaves behind.)

### Heavy Void

The heavy void is an empty [PACK!](/docs/datatypes/pack/), written
`~()~`.  Like VOID!, it's nothing.  Unlike VOID!, it isn't the "nothing"
that vanishes.  It's what EVAL gives back when a block's last step was
an IF that didn't run, and it lifts to `~()~`, not `~`:

```
>> eval [if null [1]]
== \~()~\  ; antiform (pack!)

>> lift eval [if null [1]]
== ~()~
```

EVAL of a GROUP! doesn't bust the ghost, and neither does the console,
so typing the IF directly gives the light void:

```
>> eval $(if null [1])
== \~\  ; antiform (void!)

>> if null [1]
== \~\  ; antiform (void!)

>> lift if null [1]
== ~
```

ANY-VOID? is true of either one.  VOID? is only for the light one, and
refuses to answer for the heavy one, so that you notice which question
you're asking:

```
>> any-void? pack []
== \~okay~\  ; antiform (logic!)

>> void? comment "light"
== \~okay~\  ; antiform (logic!)
```

<!-- doctest: negative-test match="ANY-VOID?" -->
```
void? pack []
```

The two kinds of void also let ELSE tell "the branch didn't run" from
"the branch ran and produced nothing".  An IF that runs a branch which
produces a void gives back a heavy void, so ELSE doesn't run:

```
>> if 10 = 10 [comment "branch ran"] else [<else>]
== \~()~\  ; antiform (pack!)

>> if 10 = 20 [comment "branch ran"] else [<else>]
== <else>
```

## Asking for Vanishing

When you *do* want a void from a non-vanishable function to vanish, say
so.

**`^`** is the IDENTITY function, which is vanishable.  Put in front of an
expression that gives a light void, it lets that void vanish:

```
>> 1 + 2 ^ eval [comment "TODO"]
== 3
```

**GHOSTLY** goes further, and makes *either* kind of void vanish, heavy
ones included:

```
>> 1 + 2 ghostly if null [3]
== 3

>> 1 + 2 ghostly if 10 = 10 [comment "branch ran"] else [<else>]
== 3
```

**VANISHABLE** marks your own function as one that's allowed to vanish:

<!-- doctest: positive-test -->
```
note: vanishable func [message] [return ~]
assert [3 = (1 + 2 note "this vanishes")]
```

Without VANISHABLE, the same function busts its own ghost:

<!-- doctest: negative-test match="discarded-value" -->
```
note-heavy: func [message] [return ~]
1 + 2 note-heavy "this does not vanish"
```

Be sparing with VANISHABLE.  ELIDE already gives any expression the
vanishing behavior when you want it at a call site.  A function should be
vanishable only when vanishing is its whole point, as with COMMENT.

## Where Vanishing Applies

ALL and ANY step through their blocks, so vanishing values drop out:

```
>> any [comment "begin" 1 + 2 10 + 20 comment "end"]
== 3
```

A heavy void isn't a value ALL or ANY can test, so it's an error there:

<!-- doctest: negative-test match="Empty PACK! cannot decay" -->
```
all [1 = 1 if null [2]]
```

A GROUP! is transparent: if it vanishes, it's as if it weren't there.

```
>> 1 + 2 ()
== 3
```

## Voids and Lists

A void can't go in a list.  Operations that build a list from evaluated
expressions differ in what they do with one: [REDUCE](/docs/natives/reduce/)
makes one value per expression, so it refuses, while COMPOSE and JOIN let
it drop out:

```
>> reduce [1 if null [3] 2]
** PANIC: Cannot decay VOID! to a stable value

>> compose [a (if null [1]) b]
== [a b]

>> join block! [1 comment "x" 2]
== [1 2]
```

This is the usual way to say "include this item only if...": produce a
void when it shouldn't be there.  `OPT` turns a null into a void for
exactly that purpose:

```
>> compose [a (opt select [x 1] 'z) b]
== [a b]
```

## Voids and Variables

Like other unstable antiforms, a VOID! can't be held in a plain variable.
Assigning one *unsets* the variable, and reading it is then an error:

```
>> v: comment "nothing"
== \~\  ; antiform (void!)

>> unset? $v
== \~okay~\  ; antiform (logic!)

>> v
** PANIC: Unexpected unstable in non-^META pick of ^v
```

A [`^` variable](/docs/datatypes/metaform/) can hold one and give it
back.

## Names

Getting here took many years and many names.  Vanishing functions were
once "invisible", and the vanishing state has been called NIHIL, GHOST!
and NOTHING.  As of 2026:

| Name | What it is |
|---|---|
| VOID! | The antiform of BLANK!, `~`.  The "nothing" that vanishes. |
| heavy void | An empty PACK!, `~()~`.  The "nothing" that doesn't. |
| GHOST | A vanishable function with no arguments.  It returns a VOID!. |
| GHOSTLY | Makes VOID! and heavy void vanish. |
| VANISHABLE | Marks a function as allowed to vanish. |
| `^` | IDENTITY, which is vanishable, so a light void it passes on vanishes. |

## See Also

* [PACK!](/docs/datatypes/pack/) -- the empty pack is the heavy void
* [LOGIC!](/docs/datatypes/logic/) -- `~null~` is "false", not "nothing"
* [REDUCE](/docs/natives/reduce/) -- why it refuses voids
* [Evaluation](/docs/concepts/evaluation/) -- what a step is
* [Isotopes](/docs/concepts/isotopes/) -- stable and unstable antiforms
* [Why COMMENT Vanishes, But Not EVAL of COMMENT](https://revolt.metaeducation.com/forum/t/why-comment-vanishes-but-not-eval-of-comment/2563)
  (forum, 2025-2026)
* [Making Invisible Functions (e.g. COMMENT, ELIDE)](https://revolt.metaeducation.com/forum/t/making-invisible-functions-e-g-comment-elide/2034)
  (forum, 2023; uses older names)
