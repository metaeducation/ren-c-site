---
title: Sequencing
parent: Concepts
nav_order: 1
---

# Sequencing

A BLOCK! of rules matches each rule in order, and `|` separates
alternatives.  That sounds like what any parser does.  The difference is
where it lives: **there is no SEQUENCE combinator and no ALTERNATIVE
combinator.**  Sequencing and alternatives are what the BLOCK! combinator
does with the block it's given.  Neither `|` nor `||` is a combinator;
they're markers the BLOCK! combinator looks for.

A parser-combinator library in a language like Haskell or Rust has to
build its own syntax out of operators: one to put two parsers in a row,
another for "this or that".  PARSE doesn't need to, because Revolt already
has a way to write things in a row.  It's a block.

## Sequencing

Rules written one after another must all match, in order.  The block's
result is the last rule's result:

```
>> parse "ab" ["a" "b"]
== "b"
```

Commas can go between rules to make the steps easier to see.  They mean
nothing else, and they're only allowed *between* rules, so one inside a
rule is an error:

```
>> parse "ab" ["a", "b"]
== "b"
```

<!-- doctest: negative-test match="Too few parameters" -->
```
parse "ab" [some, "a" "b"]
```

## Alternatives: `|`

`|` separates alternatives.  The BLOCK! combinator tries them in order,
going back to where the block started for each one, and uses the first
whose whole sequence matches:

```
>> parse "b" ["a" | "b"]
== "b"

>> parse "ab" ["a" "x" | "a" "b"]
== "b"
```

`|` isn't a combinator.  It's a marker the BLOCK! combinator looks for.
An "OR combinator" would take the rules on either side as arguments,
which would mean building every alternative into one big function before
any of them ran.  As a marker, `|` lets the block run one step at a time:
a GROUP! that changes a variable is seen by the rules after it, and a
block of a hundred alternatives stops at the first one that matches.

An empty alternative matches without moving through the input, so a `|`
at either end of a block always succeeds there:

```
>> parse-match "x" ["x" |]
== "x"

>> parse-match "" ["x" |]
== ""
```

## Inline Sequencing: `||`

`||` ends a set of alternatives without starting a new block.  These two
are the same:

```
>> parse "bd" ["a" | "b" || "c" | "d"]
== "d"

>> parse "bd" [["a" | "b"] ["c" | "d"]]
== "d"
```

When an alternative matches, the BLOCK! combinator skips ahead to the
next `||` (if there is one) and goes on matching from there.  It saves a
level of brackets in the common case of "one of these, then one of
those".

## See Also

* [Synthesis](/docs/dialects/parse/concepts/synthesis/) -- what a block
  gives back
* [Combinators](/docs/dialects/parse/combinators/) -- the keywords used
  inside blocks
* [`||` as an Inline Sequencing Operator for UPARSE](https://revolt.metaeducation.com/forum/t/as-an-inline-sequencing-operator-for-uparse/1594)
  (forum)
