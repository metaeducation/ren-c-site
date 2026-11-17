---
layout: default
title: Why Revolt
nav_order: 2
permalink: /why/
---

# Why Revolt

Every language eventually needs new control constructs, and each one costs
a revision of the language.  Python needed proposals for `with`, `async`
and `match`.  JavaScript needed `??` and `?.`.  Rust needed `?`.  Users
couldn't add these themselves, because a construct written as a function
doesn't behave like one that's built in.

Revolt is an experiment in what a language has to be so that it does.
`if`, `while`, `try`, `else` and `return` are ordinary functions here.
There are no macros and no compile step, and code is plain data that
functions receive and decide what to do with.

Languages have tried this before, and mostly it hasn't composed.  This
page is about what was needed to make it compose.  It turns out to be
mostly one idea, and that idea also removes a set of problems that have
nothing to do with control constructs.

{: .warning }
> Revolt is an experiment, and isn't being offered as something to build
> on.  This page explains what the experiment is for.  It isn't a pitch.

## The Idea: Values That Only Exist in Transit

In most dynamic languages, anything a function can return can also be
stored in a list.  So every signal a function might send, such as "not
found", "false", "failed" or "nothing", is also a thing that might be
sitting in your data.  The two get confused, and a great deal of defensive
code exists to tell them apart.

Typed languages solve this with types like `Option` and `Result`, checked
by a compiler.  Revolt has no compiler.  It solves it with a rule about
*where a value can be*:

* An **[antiform](/docs/concepts/isotopes/)** can be returned from a
  function and held in a variable, but can't be put in a block.  NULL is
  one.  So "nothing was there" can never be an item that was there.

* An **unstable** antiform can't be held in an ordinary variable either.
  Left alone, it exists only between a function returning it and
  something reacting to it.  A [failure](/docs/datatypes/failure/) is one,
  so it can't be ignored.  (Keeping one takes a deliberate mark, the
  [`^` sigil](/docs/datatypes/metaform/).)

Almost everything below follows from those two rules.

## What It Removes

Each of these is a problem you'll recognize from another language.  The
Revolt examples are run every time this site is built.

### Sentinels

"Not found" has to be returned as *something*, so it's `-1`, or `None`, or
a private `_MISSING = object()`.  Then code tests it the natural way and
gets it wrong:

```text
// JavaScript
if (items.indexOf("a")) { ... }     // false when "a" is first: index 0
```

In Revolt the answer is NULL, which nothing in the data can be, and
everything else is true:

```
>> if find [a b c] 'a [<found>]
== <found>

>> find [a b c] 'z
== \~null~\  ; antiform (logic!)
```

### Truthiness

When several values count as false, "use this unless it's missing" breaks
on the ones that weren't missing:

```text
// JavaScript
const count = settings.count || 10;   // a count of 0 becomes 10
```

JavaScript added `??` to fix that.  Revolt has
[one false state](/docs/datatypes/logic/#null-is-the-only-false), so the ordinary form is
already right:

```
>> count: 0
== 0

>> any [count 10]
== 0
```

### Catching Too Much

An exception handler wrapped around a call catches what the call was
expected to do wrong, and everything else too:

```text
# Python
try:
    value = config[key].stirp()      # typo
except Exception:
    value = None                     # ...which is now hidden forever
```

In Revolt a function *returns* its failures, and only the code that made
the call can handle them.  TRY turns the failure from one call into NULL:

```
>> try pick [a b] 3
== \~null~\  ; antiform (logic!)
```

A typo isn't a failure that some function returned.  It's a bug, and it
goes straight through:

<!-- doctest: negative-test match="no-binding" -->
```
try pikc [a b] 3
```

See [FAILURE!](/docs/datatypes/failure/).

### Constructs You Can't Write Yourself

In most languages, code passed to a function is a separate function, so
`return` inside it doesn't mean what it would in a built-in loop:

```text
// JavaScript
function firstBig(items) {
    items.forEach(n => { if (n > 100) return n; });   // returns from the arrow
    return null;                                       // always reached
}
```

In Revolt a RETURN belongs to the function it was written in, however many
other functions the code passes through on the way.  Here TWICE is a
construct made up on the spot:

<!-- doctest: positive-test -->
```
twice: func [body] [eval body, return eval body]

first-try: func [n] [
    twice [if n < 5 [return <early>]]
    return <late>
]

assert [<early> = first-try 1]
assert [<late> = first-try 9]
```

See [Definitionality](/docs/concepts/definitionality/).

### A Second Result Breaks Every Caller

When a function that returned one thing needs to return two, the usual
choices are to return a tuple and break every existing caller, or to add
an output parameter.  A Revolt function returns a
[pack](/docs/datatypes/pack/).  Callers who want one value get the first,
and don't have to know:

<!-- doctest: positive-test -->
```
both-ends: func [block] [return pack [first block, last block]]

x: both-ends [10 20 30]
assert [x = 10]

[low high]: both-ends [10 20 30]
assert [high = 30]
```

### The Shared Mutable Literal

```text
# Python
def remember(x, seen=[]):     # one list, shared by every call
    seen.append(x)
    return seen
```

In Revolt the literals in a function body are
[read-only](/docs/concepts/constness/), so the mistake is caught the first
time it runs:

<!-- doctest: negative-test match="const-value" -->
```
remember: func [x] [
    let seen: []
    append seen x
    return seen
]
remember 1
```

### The Result Nobody Used

A comparison where an assignment was meant, or a calculation whose answer
was never stored, runs without complaint in most languages.  Linters and
attributes like `#[must_use]` exist to catch it.  The Revolt
[evaluator](/docs/concepts/evaluation/#a-computed-value-cant-be-thrown-away)
refuses:

<!-- doctest: negative-test match="discarded-value" -->
```
total: 0
eval [total + 5 total]
```

## What It's For: Small Languages

Removing those problems isn't the goal.  The goal is that you can make a
notation that fits a problem, as easily as you'd write a function.

Revolt has a wide range of literal values: dates, times, files, email
addresses, tags, money and more.  A block of them is data, and can be read
without writing a parser:

<!-- doctest: positive-test -->
```
plan: [
    mon 9:00 "standup"
    wed 14:30 "design review"
]

mornings: copy []
for-each [day time what] plan [
    if time < 12:00 [append mornings what]
]

assert [mornings = ["standup"]]
```

Elsewhere, that notation would be a string to parse, or a configuration
file with its own half-language for the parts that need logic.  Here it's
a block, and the code that gives it meaning is a few lines that can use
every construct on this page.

{: .note }
> This is the part of the case that the site shows least well so far.
> There are pages on each mechanism, and none yet where a dialect replaces
> a larger amount of conventional code.

## Why the Parts Need Each Other

One operation, [lifting](/docs/concepts/isotopes/#the-lifting-ladder),
moves a value between the plane of things that can be stored and the plane
of things in transit.  Everything above is an instance of it:

| In transit | What it gives |
|---|---|
| the words `null` and `okay` | absence, and [logic](/docs/datatypes/logic/) |
| an error | a [failure](/docs/datatypes/failure/) that must be handled |
| a group of values | a [pack](/docs/datatypes/pack/): several results in one |
| an empty marker | a [void](/docs/datatypes/void/): a function that leaves no result |
| a block | a splice: items added, not a block added |
| a function's frame | an action: a function that runs when its word is reached |

And they lean on each other.  ELSE can tell "the branch didn't run" from
"the branch ran and gave nothing" because of packs.  TRY is safe because
a failure can't be stored by accident.  A wrapper can adjust a function's extra results
because they're in the return value.  Taking one away would break the
others.

## Related Work

**Fexprs.**  Functions that receive their arguments unevaluated are an old
idea in Lisp, abandoned in favor of macros because they made programs hard
to reason about.  John Shutt's *Kernel* revived them with first-class
environments.  Revolt is in the same territory, with a different answer:
[binding](/docs/concepts/binding/) is carried by the values themselves.

**R.**  The most widely used language of this kind is R, whose functions
can also capture their arguments as code.  Its tooling had to add
"quosures", code bundled with the environment it came from, to make that
composable.  That's the problem binding solves here.

**Tennent's correspondence principle.**  Wrapping code in a construct
shouldn't change what the code means.  Definitional RETURN is that
principle applied to a language where constructs are functions.

## What It Doesn't Do

**Nothing is checked before it runs.**  There are no static types, and
since any function may decide what its arguments mean, a program can't in
general be analyzed without running it.  Every error on this page is found
at run time.

**There's a lot to learn first.**  Antiforms, quasiforms, lifting, light
and heavy voids, and what may be discarded are all new vocabulary, and the
benefits don't show until several of them are understood together.

**Arithmetic doesn't read the way you expect.**  There's one rule for
[infix](/docs/concepts/infix/), with no precedence, and `10 - 2 - 3` is 11.
It's consistent, and it's still a surprise.

**It isn't fast,** and it isn't finished.

## History

Revolt began as a branch of the open-sourced Rebol 3 interpreter, and for
most of its life was called Ren-C.  It keeps Rebol's central bet: that
code as data, with rich literals, is a good basis for small languages.
Nearly everything underneath has been replaced, because the original
design didn't answer the questions on this page.  The concept pages each
say what changed, and why.
