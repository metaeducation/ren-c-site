---
layout: default
title: Infix
parent: Concepts
nav_order: 5
permalink: /docs/concepts/infix/
---

# Infix

In Revolt, an **infix function** is any function that **runs in the same
step as what's on its left**, and gets its first argument from there.  The
function can have any number of parameters.

| Parameters | What it looks like | Example |
|---|---|---|
| 2 | what you'd traditionally call infix | `1 + 2` |
| 1 | what you'd traditionally call postfix | `10 double` |
| 0 | just runs in the same step as its left | `10 chime` |
| 3 | the first from the left, the other two to the right | `1 between 2 3` |

Most people only meet the two-parameter case, in operators like `+`, `=`
and `and`, and in control words like [THEN](/docs/natives/then/) and
[ELSE](/docs/natives/else/).  But the one rule covers all of them, so
there's no separate machinery for "postfix".

```
>> 1 + 2
== 3

>> add 1 2
== 3
```

{: .note }
> Internal to the interpreter's implementation, this mechanism is called
> "lookback"--to avoid the expectation that an "infix" function has exactly two
> parameters.  But since almost every "lookback function" a user will encounter
> is infix, the more familiar term is used in client code.  Just be aware that
> if you give an infix function other than 2 parameters, there will be some
> weirdness (see [Other Numbers of Parameters](#other-numbers-of-parameters)).

## Making One

[INFIX](/docs/natives/infix/) takes a function and gives back an infix
version of it.  The original is left alone:

```
>> infix? add/
== \~null~\  ; antiform (logic!)

>> infix? infix add/
== \~okay~\  ; antiform (logic!)
```

That's how the operators are defined, and how you'd define your own:

<!-- doctest: positive-test -->
```
average-with: infix lambda [a b] [(a + b) / 2]
assert [15 = (10 average-with 20)]
```

(AVERAGE-WITH is a function with no side-effects.  So frequently in library
code you'd see such functions this written as `/average-with:`, with a leading
slash.  That makes the variable [FINAL](/docs/natives/final/), which
matters to [pure](/docs/concepts/purity/) functions.  You don't *need* it to
define a function, but using the slash with pure functions offers benefits.)

## The Left Side Is One Unit

An ordinary infix function takes **one unit** from its left: the single
value that was just evaluated there, whether it came from a literal, a
word, or a group.  It doesn't take "everything written so far", and it
doesn't wait for a function call in progress to finish.  In `add 1 2 * 3`,
the `*` takes the `2`, not the result of `add 1 2`.  (Functions that *do*
wait are covered in [The Modes](#the-modes).)

An infix function can also ask to take its left argument *literally*,
without evaluating it.  That's how `head of x` works: OF takes the word
`head` as a word, so HEAD is never called, and OF looks up `head-of`.  It's
also how `x: me + 20` can update the variable `x`:

<!-- doctest: positive-test -->
```
x: 10
x: me + 20
assert [x = 30]
```

When a word is followed by an infix function that wants its left argument
literally, that function gets the word, and the word isn't run as a
function call.

## The Right Side Is a Full Step

Everything to the *right* of an infix function is gathered the way it would
be for any function: each argument is a full step of evaluation, and a step
includes any infix function that comes after it.

```
>> 1 + 2 * 3
== 7
```

The `+` needs a second argument, so it evaluates a step starting at `2`.
That step finds the `*` after the `2`, so it runs `2 * 3` and gets 6.  Then
`1 + 6` is 7.  It's just what happens with `add`:

```
>> add 1 2 * 3
== 7
```

That's the whole rule: **an infix function takes what's on its left and
makes it the first argument.**  Nothing else about the call is different.
So you can always work out what an expression does by moving each infix
function in front of its left-hand side, one at a time:

```text
10 - 2       is   subtract 10 2

1 + 2 * 3    is   add 1 2 * 3
             is   add 1 multiply 2 3
```

### Chains Nest to the Right

Do the same with a chain of the same operator:

```text
10 - 2 - 3   is   subtract 10 2 - 3
             is   subtract 10 subtract 2 3
```

The first `-` took the `10`.  The second took the `2`, because that's
what was on *its* left.  So the chain groups from the right:

```
>> 10 - 2 - 3
== 11

>> subtract 10 subtract 2 3
== 11

>> 3 * 2 + 1
== 9
```

This is not precedence, and it is not left-to-right.  `1 + 2 * 3` is 7
only because the `*` happens to be on the right.  When you want the other
grouping, use a group:

```
>> (10 - 2) - 3
== 5

>> subtract subtract 10 2 3
== 5
```

### Why It Is Like This

In Rebol2, `1 + 2 * 3` was 9, not 7:

```text
rebol2>> 1 + 2 * 3
== 9
```

There was a hidden rule: while the evaluator gathered the right argument of
an infix function, it did *not* look ahead for another infix function.  In
`1 + 2 * 3` the `+` was gathering `2` and wasn't allowed to see the `*`, so
it finished (1 + 2) first, and then the result was multiplied by 3.  That
gave a simple pattern, left to right, with no precedence.

But the pattern needed a flag inside the evaluator, "I'm already running an
infix function", and the flag meant something was different about the
*same* code depending on whether it ran as an argument to an infix function
or a prefix one: `1 + 2 * 3` was 9, while `add 1 2 * 3` was 7.  The flag
was an invisible state that anyone trying to predict the evaluator had to
account for.

The flag is gone, and so is the exception.  A step is a step, wherever it
appears.

### Why `10 = length of block` Works

Under the old rule, this shouldn't have.  The `=` is an infix function
gathering its right argument, so it wasn't supposed to look past `length`
to see the OF, and the expression should have acted like
`(10 = length) of block`.  That it worked anyway needed a special
explanation.

Now there's nothing to explain.  The `=` gathers a full step starting at
`length`.  That step finds OF, which takes `length` as a literal word, and
produces the length of the block.  Then the comparison is made:

```
>> block: [a b c]
== [a b c]

>> 3 = length of block
== \~okay~\  ; antiform (logic!)

>> 10 = length of block
== \~null~\  ; antiform (logic!)
```

### The Catch: Prefix Functions Want "Yoda Conditions"

The same rule applies to prefix functions, which gather their arguments
as full steps too.  So an infix function after the last argument of a
prefix function belongs to the *argument*:

<!-- doctest: negative-test match="expect-arg" -->
```
length of block = 3
```

That's `length of (block = 3)`, which is not what was meant.  The fix is to
put the constant first:

```
>> 3 = length of block
== \~okay~\  ; antiform (logic!)
```

Programmers in other languages will recognize this.  Writing the constant
on the left of a comparison, as in `if (3 == x)`, is called a
[**Yoda condition**](https://en.wikipedia.org/wiki/Yoda_conditions), after
the *Star Wars* character's way of putting words in reverse order: "three,
the length is."  In C, it's a defense against typing `=` when you meant
`==`.  `if (x = 3)` silently assigns, but `if (3 = x)` won't compile.  Some
style guides (WordPress's, for one) require Yoda conditions for that
reason.

In Revolt, the reason is different but the habit is the same.  When one
side of a comparison is a function call, put that call on the *right*:

| Instead of | Write |
|---|---|
| `length of block = 3` | `3 = length of block` |
| `first block = 'a` | `'a = first block` |
| `index of pos > 1` | `1 < index of pos` |

If you'd rather read it the other way around, a group works too:

```
>> (length of block) = 3
== \~okay~\  ; antiform (logic!)
```

This is the price of one rule with no exceptions, and the habit soon
becomes second nature.

## The Modes

Each function has two bits that say how infix it is:

| Mode | How it's made | When it runs |
|---|---|---|
| **prefix** | the default | Not infix at all.  Runs in its own step. |
| **tight** | `infix` | Right away, taking the one value on its left. |
| **deferred** | `infix:defer` | After the *one* function call in progress on its left has finished, taking that call's result. |
| **postponed** | `infix:postpone` | After *every* function call in progress on its left has finished. |

You can see all three at once with a function that just collects its two
arguments:

<!-- doctest: positive-test -->
```
tight: infix lambda [a b] [reduce [a b]]
deferred: infix:defer lambda [a b] [reduce [a b]]
postponed: infix:postpone lambda [a b] [reduce [a b]]
```

### Tight

Tight is the normal mode, and it's what the right-hand rule above describes.
In `1 + 2 tight 3 * 4`, the `+` gathers a step at `2`, and the step finds
`tight`, which takes the 2 and `3 * 4`.  The `+` is left with a block:

<!-- doctest: negative-test match="expect-arg" -->
```
1 + 2 tight 3 * 4
```

### Deferred

A deferred function passes up its first chance to run.  It lets the one
function call that's in progress on its left finish, and takes *that
call's result*:

```
>> all [1 = 1 2 = 2] then [<both>]
== <both>

>> 1 + 2 deferred 3 * 4
== [3 12]
```

When THEN is reached, ALL is in the middle of taking the block as its
argument.  A tight function would take the block, as in
`all ([...] then [...])`.  THEN waits for ALL to finish.  Likewise
`deferred` waited for the `+`, where `tight` took the `2`.

It waits for *one* call, the innermost.  If that call is itself an argument
to something else, the deferred function's result is what the outer call
gets:

```
>> append [a] 1 + 2 deferred 10
== [a [3 10]]
```

The `+` was the call in progress, so `deferred` took 3 (and 10), and APPEND
got the result.

[THEN](/docs/natives/then/), [ELSE](/docs/natives/else/) and
[ALSO](/docs/natives/also/) are deferred, which is why they work after an
IF, an ALL, or a FIND.  But "the innermost call" is worth remembering when
they follow an operator:

```
>> if 3 = 1 + 2 [<yes>] else [<no>]
== <yes>

>> 3 = 1 + 2 then [<yes>]
== \~null~\  ; antiform (logic!)
```

In the second, the call in progress was the `+`.  THEN took 3 and gave
`<yes>`, which became the right argument of `=`.  So it compared 3 to
`<yes>`.

A deferred or postponed function can only come after the *last* argument
of a call.  In the middle of one, there's no telling what was meant:

<!-- doctest: negative-test match="ambiguous-infix" -->
```
add 1 deferred 2 3
```

### Postponed

A postponed function waits for *every* call in progress on its left to
finish, not just the innermost.  The same expression that deferred gave
`[a [3 10]]` gives:

```
>> append [a] 1 + 2 postponed 10
== [[a 3] 10]
```

and so a postponed function can take the result of nested calls:

```
>> add 1 add 2 3 postponed 10
== [6 10]
```

`so` is postponed.  It checks the logic on its left, and stops with an
error if it's false:

```
>> 1 = 1 so 10 + 20
== 30
```

<!-- doctest: negative-test match="assertion-failure" -->
```
(1 = 2) so 10
```

## Other Numbers of Parameters

One parameter is a postfix function.  What's on its left is its only
argument, so there's nothing to gather on the right, and it's a step like
any other:

<!-- doctest: positive-test -->
```
double: infix lambda [x] [x * 2]
assert [20 = (10 double)]
assert [21 = (10 double + 1)]
assert [21 = (1 + 10 double)]
```

Zero parameters is a function that runs in the same step as its left, and
nothing is passed to it.  What comes out of the step is the function's
result:

<!-- doctest: positive-test -->
```
chime: infix func [] [return <ding>]
assert [<ding> = (1020 chime)]
```

(Without INFIX, a zero-parameter function would run in a step of its own,
after the one that produced `1020`.)

Three parameters take the first from the left, and the other two from the
right, each a full step:

<!-- doctest: positive-test -->
```
between: infix lambda [a b c] [reduce [a b c]]
assert [[1 3 6] = (1 between 2 + 1 3 * 2)]
```

How a function with three parameters should treat a step on its left that
itself wants to continue to the right, as in `1 between 2 + 3 4 * 5`, isn't
fully settled.  Expect weirdness.

## Infix and Purity

A [pure function](/docs/concepts/purity/) can only use variables that are
FINAL, and that includes the operators, which are defined as FINAL
(`+: final infix add/`).  How pure code should treat a word that might be
taken literally by the infix function after it, as in
`value: type of value`, is one of the open questions on that page.

## History

* [The Infix Covenant](https://revolt.metaeducation.com/forum/t/the-ren-c-infix-covenant/1023)
  (2019).  The rules for what an infix function may do with its left side.
  The `#tight` convention and TIGHTEN it mentions are gone, and its
  examples predate the removal of the flag.

* [(1 + 2 * 3) is 9 and not 7... But Why?](https://revolt.metaeducation.com/forum/t/1-2-3-is-9-and-not-7-but-why/2693)
  (2026).  Removing the flag.

## See Also

* [INFIX](/docs/natives/infix/) -- make an infix function, and INFIX? to
  ask
* [THEN](/docs/natives/then/), [ELSE](/docs/natives/else/),
  [ALSO](/docs/natives/also/) -- the deferred functions
* [Purity](/docs/concepts/purity/)
