---
layout: native
title: ALSO
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/also/
native: also
spec: |
  "If LEFT is a FAILURE!, return it, else EVAL BRANCH but return LEFT"
  return: [any-value?]
  ^left [failure! any-value?]
  @branch [any-branch?]
---

ALSO runs a branch for its side effects, and passes along the value from
its left unchanged.  Whatever the branch produces is thrown away:

<!-- doctest: positive-test -->
```
trail: copy []
result: 1 + 2 also [append trail <ran>]
assert [result = 3]
assert [trail = [<ran>]]
```

It's the pass-through version of [THEN](/docs/natives/then/).  A
`then (x -> [... x])` that needs to give back `x` at the end is written
more clearly as ALSO.

## A Function As the Branch

A function is called with the value from the left, and its result is
discarded the same way:

<!-- doctest: positive-test -->
```
seen: copy []
result: 10 also (x -> [append seen x])
assert [result = 10]
assert [seen = [10]]
```

## Errors Pass Through

A FAILURE! on the left isn't given to the branch.  The branch doesn't run,
and the failure comes out of ALSO as it went in.

## It Is Deferred

Like [THEN](/docs/natives/then/) and [ELSE](/docs/natives/else/), ALSO is
`infix:defer`: it follows the whole call on its left, and is still part of
the step it's in.  See [The Modes](/docs/concepts/infix/#the-modes).

## See Also

* [THEN](/docs/natives/then/)
* [ELSE](/docs/natives/else/)
* [INFIX](/docs/natives/infix/), [Infix](/docs/concepts/infix/)
