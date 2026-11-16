---
layout: default
title: Failure
parent: Concepts
grand_parent: Documentation
nav_order: 5
permalink: /docs/concepts/failure/
---

# Failure

Revolt has three ways for something to go wrong, and they're kept strictly
apart:

| | What it is | What happens | Who can deal with it |
|---|---|---|---|
| **Failure** | A [FAILURE!](/docs/datatypes/failure/) value, *returned* by a function | Goes back to the caller like any result | The caller, right there |
| **Panic** | An abrupt stop | Unwinds everything, back to the console (or a script's exit) | Nobody, in normal code |
| **Crash** | The interpreter ending | No more code runs at all | Nobody |

Most of what's new here is the first one.  A failure isn't an exception
that flies up through the stack until something catches it.  It's a value
that one function hands back to the code that called it, saying "I
understood what you asked for, and I couldn't do it."  And it's a value
that can't be ignored.

## The Problem With Catching Everything

In historical Rebol, as in most languages with exceptions, an error raised
anywhere would travel up through every function until something caught it.
The trouble is what gets caught.  Suppose you want to read a file if it's
there:

```text
rebol2>> attempt [read %settings.txt]
== none
```

That's NONE if the file doesn't exist, which is what you wanted.  But it's
also NONE if you'd misspelled `read`, or if something three functions down
inside READ had a bug.  ATTEMPT and TRY couldn't tell "the thing I asked
for didn't work out" from "the code is broken", so the "safe" versions
hid bugs.  In practice they were too dangerous to use.

(Rebol2 tried something else first: "hot" ERROR! values, which went off
like an exception if a caller didn't defuse them.  But every error was hot,
wherever it came from, so it had the same problem.  R3-Alpha and Red went
back to ordinary exceptions.)

## Failures Are Definitional

Revolt's answer is that a function decides, as part of what it *is*, which
of its problems are failures for the caller to handle.  It does that by
*returning* them:

<!-- doctest: positive-test -->
```
bigtest: func [n] [
    if n < 1020 [panic [n "is not big"]]
    return n
]

definitional-bigtest: func [n] [
    if n < 1020 [return fail [n "is not big"]]
    return n
]
```

The first one panics, which stops everything.  The second returns a
failure, which the console shows differently:

```
>> bigtest 304
** PANIC: 304 is not big

>> definitional-bigtest 304
** Failure: 304 is not big
```

Only the second can be handled by its caller.  [TRY](#try) turns a failure
into NULL, but it can't do anything about a panic:

<!-- doctest: positive-test -->
```
assert [null = try definitional-bigtest 304]
assert [2000 = try definitional-bigtest 2000]
```

<!-- doctest: negative-test match="is not big" -->
```
try bigtest 304
```

The word *definitional* comes from this: the failure is part of the
function's definition, the way its return value is.  `PICK` with an index
that's out of range, `TAKE` from an empty block, and dividing by zero all
return failures, because those are things a caller can reasonably expect
and want to handle:

```
>> pick [a b] 3
** Failure: cannot pick 3

>> try pick [a b] 3
== \~null~\  ; antiform (logic!)

>> try take []
== \~null~\  ; antiform (logic!)
```

### Failures Don't Leak Out of Functions

The other half of the rule: a failure from somewhere *inside* a function
doesn't come out of that function as a failure, unless the function
returns it.  If the function body ignores it, it becomes a panic:

<!-- doctest: positive-test -->
```
average: func [block] [
    let total: 0
    for-each 'n block [total: total + n]
    let result: total / length of block  ; empty block: divides by zero
    return result
]
```

<!-- doctest: negative-test match="zero-divide" -->
```
try average []
```

The `/` returned a failure to AVERAGE, and AVERAGE didn't handle it or pass
it on.  So TRY on the outside can't see it as a failure.  If it could, a
caller asking "did AVERAGE fail?" would also be told yes about every bug
inside AVERAGE, and that's the problem from historical Rebol all over again.

A function passes a failure on by returning it.  That happens when it
returns the result of a call that failed:

<!-- doctest: positive-test -->
```
ratio: func [a b] [return a / b]
assert [null = try ratio 1 0]
```

or, from the middle of a function, with TRAP.  TRAP passes a value
through, unless it's a failure, in which case it returns that failure from
the function right away:

<!-- doctest: positive-test -->
```
second-or-fail: func [block] [
    let item: trap pick block 2
    return item
]
assert ['b = second-or-fail [a b c]]
assert [null = try second-or-fail [a]]
```

## A Failure Can't Be Ignored

FAILURE! is an *unstable* [antiform](/docs/concepts/antiforms/): the
antiform of [ERROR!](/docs/datatypes/error/).  Unstable means it can't be
stored in a plain variable or passed as an ordinary argument.  If a failure
reaches anywhere it would have to be stored or skipped over, it turns into
a panic.

Assigning one doesn't store it.  The failure goes on, and the variable
keeps the value it had:

<!-- doctest: positive-test -->
```
x: 10
```

<!-- doctest: negative-test match="oops" -->
```
x: fail "oops"
print "this never runs"
```

<!-- doctest: positive-test -->
```
assert [x = 10]
```

A failure in the middle of a longer expression panics, since nothing used
it:

<!-- doctest: negative-test match="oops" -->
```
(fail "oops" 10)
```

The functions that see results go by one rule: a failure is not "nothing".
[THEN](/docs/natives/then/) and [ALSO](/docs/natives/also/) pass a failure
along untouched.  [ELSE](/docs/natives/else/) doesn't treat it as the NULL
or VOID! it's looking for, so an ordinary ELSE branch can't swallow it:

<!-- doctest: negative-test match="oops" -->
```
fail "oops" else [<handled?>]
```

## Handling Failures

| | What it does |
|---|---|
| [TRY](#try) | Turns a failure into NULL |
| [EXCEPT](#except) | Runs a branch if there was a failure, with access to the ERROR! |
| [RESCUE](#rescue) | Runs a block, gives back the ERROR! of a failure in it, or NULL |
| [TRAP](#failures-dont-leak-out-of-functions) | Returns a failure from the current function |
| [LIFT](#keeping-one-with-lift) | Turns a failure into a quasiform ERROR! you can store |

### TRY

TRY is for when a failure just means "no answer".  It turns a failure into
NULL, and passes anything else through, so it fits with ELSE, ALL and the
other things that react to NULL:

```
>> try fail "oops"
== \~null~\  ; antiform (logic!)

>> try pick [a b] 1
== a

>> (try pick [a b] 3) else [<no-such-item>]
== <no-such-item>
```

The group matters.  ELSE is [deferred](/docs/concepts/infix/#deferred), so
it attaches to the innermost call in progress on its left, which is PICK,
not TRY.  Without the group, the failure from PICK reaches ELSE before TRY
ever sees it:

<!-- doctest: negative-test match="cannot pick" -->
```
try pick [a b] 3 else [<no-such-item>]
```

### EXCEPT

EXCEPT is like ELSE, for failures.  If the expression on its left failed,
it runs its branch, and if the branch is a function, the function gets the
ERROR!.  Otherwise EXCEPT passes the value along:

```
>> fail "oops" except [<handled>]
== <handled>

>> fail "oops" except (e -> [e.message])
== "oops"

>> 10 except [<not-run>]
== 10
```

It's deferred infix like THEN and ELSE, and chains with them.  THEN passes
the failure along to the EXCEPT:

```
>> fail "oops" then [<then>] except [<except>]
== <except>
```

### RESCUE

RESCUE runs a block, and gives back the ERROR! (as a plain, storable
value) of a failure the block produced.  If there wasn't one, it gives
NULL:

```
>> e: rescue [1 / 0]

>> e.id
== zero-divide

>> rescue [1 + 1]
== \~null~\  ; antiform (logic!)
```

RESCUE only reacts to failures that the block's own expressions return,
not to panics from anywhere inside.  A typo is a panic, so RESCUE doesn't
hide it:

<!-- doctest: negative-test match="no-binding" -->
```
rescue [prnit "hello"]
```

### Keeping One With LIFT

A plain variable can't hold a failure, but it can hold the
[lifted](/docs/concepts/quasiforms/#the-lifting-ladder) form.  LIFT gives
a quasiform ERROR!, and UNLIFT turns it back into the failure later:

<!-- doctest: positive-test -->
```
kept: lift fail "oops"
assert [quasiform? kept]
assert ["oops" = (unquasi kept).message]
assert [failure? unlift kept]
```

The other way is a [`^` variable](/docs/concepts/sigils/#meta), which
stores the failure itself:

<!-- doctest: positive-test -->
```
try ^held: fail "oops"
assert [failure? ^held]
```

### Making Your Own

FAIL makes a failure from a message, an ERROR! object, or an id:

<!-- doctest: positive-test -->
```
e: rescue [fail 'not-ready]
assert [e.id = 'not-ready]

e: rescue [fail "Not ready yet"]
assert [e.message = "Not ready yet"]
```

Remember that FAIL only makes the value.  For the caller to get it, the
function has to `return fail ...`.

## Panics

A panic is for a problem that the code itself didn't expect: a typo, the
wrong type of argument, a failure nobody handled, an assertion that didn't
hold.  It stops everything and goes back to the console:

```
>> panic "boom"
** PANIC: boom
```

Use PANIC, not `return fail`, when the call itself is wrong: when the
caller has misunderstood how the function works, rather than asked for
something that couldn't be done this time.

### Intercepting Panics

You *can* catch a panic, with `sys.util/recover`.  It runs a block, and
gives back the ERROR! for any panic at any depth, typos included:

<!-- doctest: positive-test -->
```
e: sys.util/recover [prnit "hello"]
assert [e.id = 'no-binding]
```

It's kept out of the way, under `sys.util`, on purpose.  Catching
everything is exactly what made ATTEMPT dangerous in historical Rebol.
It's for things like test harnesses and consoles, which have to keep going
whatever the code they run does.  In ordinary code, if you find you want
it, it usually means some function should be returning a failure instead.

## Crashes

CRASH ends the interpreter.  It's for when something has gone so wrong that
running any more code would be a mistake, such as finding that data has
been corrupted:

<!-- doctest: skip -->
```
crash "Index file is corrupt, refusing to continue"
```

CRASH takes its argument *literally*.  It accepts a message, an ERROR!, a
`$word` naming a variable to report, or nothing at all, but not an
expression to evaluate:

<!-- doctest: skip -->
```
crash $index        ; reports the variable INDEX
crash               ; just crashes
```

That's deliberate.  If CRASH evaluated its argument, then a mistake in
working out the message, like `crash form revrese name`, would *panic*
instead, and a panic can be intercepted.  The crash could be stopped by the
very thing that went wrong.  With nothing to evaluate, there's nothing to
go wrong before the crash happens.

(PANIC used to be the name for this, before the names were reorganized:
what's now PANIC used to be FAIL, and what's now FAIL used to be RAISE.
Older forum posts use the old names.)

## Compared to Historical Rebol

| | Rebol2 | R3-Alpha and Red | Revolt |
|---|---|---|---|
| A function reports a problem the caller should handle | Return a "hot" ERROR! | Raise an exception | `return fail ...` |
| A bug, a typo, an unexpected situation | The same hot ERROR! | The same exception | A panic |
| "No result, quietly" | `attempt [...]`, catching everything | `attempt [...]`, catching everything | `try ...`, catching only the failure that was returned |
| Catch absolutely everything | `try [...]` | `try [...]` | `sys.util/recover [...]`, discouraged |

## See Also

* [FAILURE!](/docs/datatypes/failure/) and [ERROR!](/docs/datatypes/error/)
* [Antiforms](/docs/concepts/antiforms/) -- stable and unstable
* [PANIC vs. RETURN FAIL: The Age of Definitional Errors](https://revolt.metaeducation.com/forum/t/panic-vs-return-fail-the-age-of-definitional-errors/1852)
  (forum, 2022; examples use older names)
* [Rebol2's Hot Errors, Abandoned by R3-Alpha and Red](https://revolt.metaeducation.com/forum/t/rebol2s-hot-errors-abandoned-by-r3-alpha-red/2505)
  (forum, 2025-2026)
* [TRY Again](https://revolt.metaeducation.com/forum/t/try-again/2025)
  (forum, 2023)
* [Designing a Crashing Function: CRASH](https://revolt.metaeducation.com/forum/t/designing-a-crashing-function-crash/2434)
  (forum, 2025)
