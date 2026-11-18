---
layout: default
title: Evaluation
parent: Concepts
nav_order: 1
permalink: /docs/concepts/evaluation/
---

# Evaluation

Code in Revolt is a block of values, and running it means walking the
block from left to right.  The walk goes one **step** at a time.  A step
is one complete expression: `1 + 2`, or `append block 10`, or just `5`.

This page covers what a step is, what the evaluator does *between* steps,
and why a BLOCK! and a GROUP! are evaluated a little differently.

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

A block evaluates to itself, but with a binding into the "current context".
That's what lets a function like IF receive its branch as data and decide
whether to run it.

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

## How It's Built

In R3-Alpha and Red, the evaluator is a recursive C function, so every
level of Rebol recursion is several levels of C recursion.  Revolt's
evaluator is **stackless**: each evaluation in progress is a structure on
the heap, and one loop drives them all.  Recursion is limited by memory
rather than by the C stack, and a running evaluation can be set aside and
resumed, which is how generators work.

[Stacklessness](/docs/concepts/stacklessness/) explains why it's built
that way, how it works, and what it costs.

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
* [Stacklessness](/docs/concepts/stacklessness/) -- how the evaluator
  runs without using the C stack
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
