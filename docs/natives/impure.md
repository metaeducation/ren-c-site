---
layout: native
title: IMPURE
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/impure/
native: impure
spec: |
  "Modifier: Non-deterministic or consults non-FINAL external state"
  return: [action! frame!]
  ^value [action! frame!]
  :off "Give back non-pure version of the passed in function"
---

IMPURE marks a function as one that [PURE](/docs/natives/pure/) code is not
allowed to call.  Use it on a function whose result can vary even with the
same arguments, or which has effects beyond its arguments: talking to the
user, the filesystem or the network, reading the clock, or generating
random numbers.

<!-- doctest: positive-test -->
```
/coin-flip: impure does [random-pick [heads tails]]
assert [find [heads tails] coin-flip]
```

Calling an IMPURE function from pure code is an error, even through a
FINAL variable and even indirectly:

<!-- doctest: negative-test match="impure-call" -->
```
best-of-three: pure does [reduce [coin-flip coin-flip coin-flip]]
best-of-three
```

## Most Functions Are Neither

Functions start out neither PURE nor IMPURE.  That's on purpose: it lets
things like IF and APPEND work in both pure and impure code.  A function
that isn't marked only causes an error if it *actually* does something
impure while it's running under a pure function.

So why mark anything IMPURE, when the system would notice it reading a
non-FINAL variable anyway?  Because for natives, and for functions that
get their non-determinism from outside the interpreter, there's no variable
access to notice.  RANDOM doesn't read a variable to pick its number.

## Impure Natives

The natives marked IMPURE include:

* **Randomness**: RANDOM, RANDOM-BETWEEN, RANDOM-PICK, RANDOMIZE, SHUFFLE,
  SHUFFLE-OF
* **Time**: NOW
* **Output**: WRITE-STDOUT (and so PRINT, which uses it)
* **Ports and files**: CREATE, DELETE, OPEN, CLOSE, READ, WRITE, QUERY,
  MODIFY, RENAME
* **Undoing protections**: [MUTABLE](/docs/natives/mutable/), UNPROTECT

Some mezzanine functions written in Revolt are marked IMPURE as well, like
ASK, CONFIRM, EXISTS?, and MAKE-DIR.

## IMPURE:OFF

`impure:off` gives back a function that isn't marked impure.  A function
can't be both PURE and IMPURE, so to make an impure function pure you have
to take the IMPURE mark off first.

{: .note }
> IMPURE currently changes the function it's given, rather than making a
> copy.  Other references to the same function become impure too.

## See Also

* [PURE](/docs/natives/pure/)
* [Purity](/docs/concepts/purity/)
