---
layout: default
title: Evaluation
parent: Concepts
grand_parent: Documentation
nav_order: 12
permalink: /docs/concepts/evaluation/
---

# Evaluation

Code in Revolt is a block of values, and running it means walking the
block from left to right.  The walk goes one **step** at a time.  A step
is one complete expression: `1 + 2`, or `append block 10`, or just `5`.

This page covers what a step is, what the evaluator does *between* steps,
why a BLOCK! and a GROUP! are evaluated a little differently, and how the
interpreter is built to run all of this without using the C stack.

{: .warning }
> The second half of this page describes the inside of the interpreter.
> That's where the design is least settled.  It's recorded here because
> the reasons behind it are hard to recover from the source alone.

## What Each Kind of Value Does

A step starts by looking at one value.  What happens next depends on its
type:

| You write | The evaluator |
|---|---|
| `5`, `"text"`, `<tag>`, `[a b]` | gives the value back as it is |
| `word` | fetches the variable, and if it holds a function, calls it |
| `word:` | runs one more step, and assigns the result |
| `(1 + 2)` | evaluates the contents |
| `'word` | removes one quote |
| `~null~` | gives the [antiform](/docs/concepts/isotopes/) |
| `obj.field` | picks the field |
| `@word` | gives the value back, sigil and all |
| `$word` | [binds](/docs/concepts/binding/) the word and gives it back |
| `,` | ends the expression (see [Commas](#commas)) |

```
>> 5
== 5

>> [a b]
== [a b]

>> 'foo
== foo

>> (1 + 2)
== 3

>> @foo
== @foo

>> ~null~
== \~null~\  ; antiform (logic!)
```

A block evaluates to itself.  That's what lets a function like IF receive
its branch as data and decide whether to run it.

## A Step

EVAL runs a whole block.  EVAL:STEP runs one step, and gives back a
[pack](/docs/datatypes/pack/) of two things: the position where the next
step would start, and the result of the step it ran.

```
>> eval:step [1 + 2 10 + 20]
== \~('[10 + 20] '3)~\  ; antiform (pack!)
```

The step didn't stop at the `1`.  A step isn't finished until the
evaluator has looked at what comes next and found that it isn't an
[infix](/docs/concepts/infix/) function.  So `1 + 2 * 3` is all one step:

```
>> eval:step [1 + 2 * 3 <next>]
== \~('[<next>] '7)~\  ; antiform (pack!)
```

A function call is one step too, however many arguments it takes.  Each
argument is gathered by running a step of its own:

```
>> eval:step [append [a] 1 + 2 <next>]
== \~('[<next>] '[a 3])~\  ; antiform (pack!)
```

At the end of the block there's no step to run, and EVAL:STEP gives NULL:

```
>> eval:step []
== \~null~\  ; antiform (logic!)
```

The position comes first in the pack so that the common test, "was there
anything left?", needs no unpacking.

### The Three Parts of a Step

Inside the interpreter a step has three parts, always in this order:

1. **Look right for a function that wants its left side literally.**  In
   `length of block`, OF takes the word `length` without evaluating it.
   That has to be noticed before `length` is looked up, so it's the first
   thing checked.

2. **Act on the value**, by its type, as in the table above.

3. **Look right for an infix function.**  If there is one, it takes the
   result so far as its first argument, and when it finishes this part is
   repeated.

There's no fourth part, and no state carried from one step to another.
Rebol2 and R3-Alpha had a flag that turned off part 3 while the right side
of an infix function was being gathered.  It made `1 + 2 * 3` give 9 where
`add 1 2 * 3` gave 7.  Revolt removed the flag, so a step behaves the same
wherever it appears.  [Infix](/docs/concepts/infix/#why-it-is-like-this)
tells that story.

## Between Steps

EVAL runs steps until the block ends, and gives back the result of the
last one.  It applies three rules along the way.

### Voids Don't Replace the Result

If a step produces a [VOID!](/docs/datatypes/void/), the result of the
step before it is kept:

```
>> eval [1 + 2 comment "this vanishes"]
== 3
```

### A Failure Can't Be Passed Over

A [failure](/docs/datatypes/failure/) may be the result of the *last* step,
and then it's the result of the EVAL.  Anywhere earlier, nothing is going
to handle it, so it becomes a panic at once:

<!-- doctest: negative-test match="boom" -->
```
eval [fail "boom" 10 + 20]
```

It can't wait to see whether the next step vanishes.  If it did, then in
code like this, the second command would already have run:

```text
call "make-backup"       ; a failure if the exit code isn't zero
call "delete-originals"  ; depends on the backup having worked
```

### A Computed Value Can't Be Thrown Away

This is the rule that most surprises people who know Rebol.  A step whose
result is a plain value, with no side effect, can't be followed by another
step:

<!-- doctest: negative-test match="discarded-value" -->
```
eval [1 + 2 10 + 20]
```

Nothing could have been wanted from the `1 + 2` except its result, and the
result is being dropped.  That's nearly always a mistake: a forgotten
assignment, an argument that ended up outside the call it was meant for, a
function that takes fewer arguments than you thought.  In historical Rebol
all of those ran without complaint.

What can and can't be passed over:

| Step | Can another step follow it? |
|---|---|
| A literal value, or a variable fetch: `10`, `[a b]`, `x` | no |
| A call to a [pure](/docs/concepts/purity/) function: `1 + 2` | no |
| A call to a function that isn't pure: `print "hi"`, `append list 1` | yes |
| An assignment: `x: 10` | yes |
| A [TRASH!](/docs/datatypes/trash/) value | yes |
| Anything that vanishes | yes (it isn't a result at all) |

```
>> eval [append [a] 'b 10 + 20]
== 30
```

When you really do want to compute something and ignore it, ELIDE says so:

```
>> eval [elide 1 + 2 10 + 20]
== 30
```

Which built-in functions are marked pure is still being worked through, so
some calls that could be caught by this rule aren't yet.

## Commas

A comma marks the end of an expression.  In the block it's a value of its
own, a [BLANK!](/docs/datatypes/blank/), so it survives being loaded and
passed around as data.

Between complete expressions it does nothing but help the reader:

```
>> all [1 = 1, 2 = 2]
== \~okay~\  ; antiform (logic!)
```

Its real job is that an argument can't be gathered across one.  A function
that reaches a comma while it still needs arguments has run out:

<!-- doctest: negative-test match="no-arg" -->
```
add 1, 2
```

Without the comma, a call that's missing an argument quietly takes the
start of the next expression instead.

## EVAL, One Step at a Time

Because EVAL:STEP hands back the position, you can write EVAL yourself as a
loop.  This is what a dialect does when it wants to evaluate expressions
out of a block and do something of its own with each result:

<!-- doctest: positive-test -->
```
position: product: ~
position: [1 + 2 if null [<skipped>] 10 + 20]
results: copy []

while [[position ^product]: eval:step position] [
    if not any-void? ^product [append results ^product]
]

assert [results = [3 30]]
```

The [`^`](/docs/datatypes/metaform/) on `^product` is needed because a
step can produce a void, and a plain variable can't hold one.

## Blocks and Groups Are Evaluated Differently

EVAL accepts a GROUP! as well as a BLOCK!, and treats them differently in
one respect: what happens to a void from a function that isn't
[VANISHABLE](/docs/datatypes/void/#ghost-busting), like the void from
an IF that didn't run its branch.

**In a block, every step is treated alike.**  Such a void becomes a heavy
void, whichever step it is, even the first:

```
>> eval:step [if null [<a>] <next>]
== \~('[<next>] ~()~)~\  ; antiform (pack!)
```

<!-- doctest: negative-test match="ANY-VOID?" -->
```
void? eval [if null [<a>]]
```

**In a group, voids are left alone until a step has produced a value.**
So a group with one expression in it gives what the expression gives:

```
>> void? (if null [<a>])
== \~okay~\  ; antiform (logic!)

>> void? eval $(if null [<a>])
== \~okay~\  ; antiform (logic!)
```

Each has a reason.

A group is punctuation.  `(expr)` has to mean the same as `expr`, or
putting parentheses around something for clarity would change what it
does.

A block is something a program steps through.  If the first step were
treated differently from the others, then the result of a step would
depend on where in the block you started.  The loop in the previous
section couldn't reproduce what EVAL does, because it would need to know
whether "a value has been seen yet", and that isn't part of the position.
With one rule for every step, a position is all there is to know.

That's why EVAL:STEP refuses a group:

<!-- doctest: negative-test match="only BLOCK!s" -->
```
eval:step $(1 + 2)
```

A refinement could have chosen the behavior instead of the type.  Using
the type means you get the right one without having to know the choice
exists.

## How It's Built: No C Stack

The rest of this page is about the interpreter's own structure.

In R3-Alpha and Red, the evaluator is a recursive function.  To evaluate
an argument, the C (or Red/System) function that runs a step calls itself.
A Rebol function that calls another Rebol function goes several C calls
deeper.  The state of the running program lives on the machine stack,
where nothing but the function that put it there can get at it.

Revolt's evaluator is **stackless**.  Each evaluation in progress is a
**Level**: a small structure allocated on the heap, with an output cell, a
position in the code, a state byte, and a pointer to an **executor**,
which is the C function that knows how to advance it.

One loop runs everything.  It's called the **trampoline**.  It calls the
top Level's executor, and the executor does a small amount of work and
*returns*.  What it returns says what should happen next:

| The executor returns | The trampoline |
|---|---|
| "My result is in my output cell" | goes back to the Level underneath, which was waiting for it |
| "Run this other Level, then come back to me" | runs that Level's executor |
| "Something was thrown" | drops Levels until one of them catches it |

When an executor needs a sub-expression evaluated, it doesn't call the
evaluator.  It pushes a Level, records in its state byte where it was, and
returns.  Later it's called again with the answer waiting, and uses the
state byte to pick up where it left off.  Every executor is written as a
state machine for this reason.

### What This Buys

**Depth is limited by memory, not by the C stack.**

<!-- doctest: positive-test -->
```
countdown: func [n] [
    if n = 0 [return <bottom>]
    return countdown n - 1
]

assert [<bottom> = countdown 50000]
```

**A running evaluation can be put aside and resumed.**  Since the Levels
aren't on the C stack, a group of them can be unhooked and kept.  That's
how a generator works: YIELD sets the generator's Levels aside, and the
next call puts them back.

<!-- doctest: positive-test -->
```
numbers: generator [yield 10 yield 20 yield 30]

assert [[10 20 30] = reduce [numbers numbers numbers]]
```

**There's one place where anything can happen between steps.**  Garbage
collection, noticing a Ctrl-C, and (one day) stopping at a breakpoint are
all done in the trampoline loop, at a moment when no C function is halfway
through changing something.

**Unwinding is a jump to a Level.**
[Definitional](/docs/concepts/definitionality/) RETURN names the Level it
belongs to, and the trampoline drops Levels until it gets there.

**Errors don't need `longjmp`.**  A native reports a panic by returning,
like any other result, and each Level above it gets a turn to clean up.
The `longjmp` or C++ exception path still exists, for panics from deep
inside C code that can't return, but the interpreter doesn't depend on it.
That matters on platforms like WebAssembly, where it may not be available.

### What It Costs

Every native that runs code has to be a state machine, and that's much
harder to write and to read than a loop that calls the evaluator.  The
conversion isn't finished.  A native that hasn't been converted starts a
second trampoline on the C stack, and a YIELD can't cross it.

It also costs speed.  A tight recursive evaluator can keep its state in
registers, and a trampoline can't.  Revolt wins some of that back with
shortcuts.  For example, each step always pushes one spare Level, which is
reused for whatever the step needs, whether that's a function call or a
group.

## Built for a Debugger That Doesn't Exist Yet

Many of the choices inside the evaluator were made so that a stepping
debugger could be written later.  The debugger hasn't been written.  This
section records what was done in advance, and why, because the code looks
strangely indirect unless you know.

**Stepping and running-to-the-end are separate executors.**  The
*stepper* runs one step.  The *evaluator* calls the stepper over and over,
holding on to the last result.  It would be simpler and faster as one
function with a "keep going" flag.  But then a block being run would give
the trampoline only one result, at the end.  With the two apart, the
stepper can have a Level of its own, and each step's result passes through
the trampoline, where a debugger could see it.

**The fast path is used when nobody is watching.**  When not debugging,
the evaluator and stepper share one Level, and the evaluator calls the
stepper directly without going back to the trampoline.  There are several
shortcuts like this.  A comma is normally skipped over, but in debug mode
it's a step of its own that produces a void, so the debugger would see the
comma.  One function call that leads directly to another normally doesn't
bounce in between, but in debug mode it does, so that a breakpoint could
be put there.

**The debug paths are tested without a debugger.**  A path that's never
run will rot.  So in builds with runtime checks, the question "are we in
debug mode?" is answered *yes* about one time in 64, decided by the
trampoline's tick count.  Every test run goes through both the fast and
the slow paths, and since the tick count is the same on each run, a
failure can be reproduced.

This forces a discipline.  The answer can be different the next time the
question is asked, so code that takes the slow path has to remember that
it did.  A real debugger could be switched on at any moment, so it would
need the same discipline.

**Every bounce has a number.**  In checked builds the trampoline counts
its bounces.  Values and Levels record the tick at which they were made,
and the interpreter can be told to break at a given tick.  A crash seen at
tick 1,203,881 can be approached again by stopping at tick 1,203,880.

R3-Alpha and Red made no provision of this kind.  Whether it pays off
can't be known until the debugger exists.  Until then the cost is extra
states and extra code paths, and the benefit so far is the testing above
and the generators.

## Compared to Historical Rebol

| | Rebol2, R3-Alpha, Red | Revolt |
|---|---|---|
| Running one step | `do/next`, which wrote the new position to a variable you named | EVAL:STEP, which returns a [pack](/docs/datatypes/pack/) of position and result |
| A result nobody uses | dropped without comment | an error, if getting it had no side effect |
| Marking the end of an expression | nothing; line breaks mean nothing to the evaluator | `,` |
| The right side of an infix function | gathered with a hidden "no lookahead" flag | a step like any other |
| A function's stack frame | on the C stack | a Level on the heap |
| Recursion limit | the C stack | memory |
| Suspending code that's running | not possible | YIELD |

## See Also

* [Infix](/docs/concepts/infix/) -- the third part of a step
* [VOID!](/docs/datatypes/void/) -- voids, and why EVAL isn't
  vanishable
* [Purity](/docs/concepts/purity/) -- which results can't be discarded
* [PACK!](/docs/datatypes/pack/) -- what EVAL:STEP returns
* [Re-imagining EVAL:NEXT](https://revolt.metaeducation.com/forum/t/re-imagining-eval-next/767)
  (forum; uses older names)
* [Why COMMENT Vanishes, But Not EVAL of COMMENT](https://revolt.metaeducation.com/forum/t/why-comment-vanishes-but-not-eval-of-comment/2563)
  (forum, 2025-2026)
* [(1 + 2 * 3) is 9 and not 7... But Why?](https://revolt.metaeducation.com/forum/t/1-2-3-is-9-and-not-7-but-why/2693)
  (forum, 2026)
