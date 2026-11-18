---
title: Synthesis
parent: Concepts
nav_order: 1
---

# Synthesis

Historical Rebol PARSE answered one question: did the rules match the whole
input?  In Revolt, every rule also **synthesizes a value**, and PARSE gives
back the value of the last rule that ran:

```
>> parse "aaabbb" [some "a" some "b"]
== "b"

>> parse [1 2 3] [some integer!]
== 3
```

What a rule gives back depends on what it's for.  A rule that matches
something gives back what it matched.  A loop like SOME gives back the
result of its last iteration.  Rules that exist to build a value, like
ACROSS and COLLECT, give back what they built:

```
>> parse "aaabbb" [across some "a" some "b"]
== "b"

>> parse "aaabbb" [across [some "a" some "b"]]
== "aaabbb"
```

## Capturing a Value

A SET-WORD! in front of a rule stores that rule's value, if the rule
matches.  The variable has to exist already:

<!-- doctest: positive-test -->
```
rest: null
parse "hello world" [to space, rest: across to <end>]
assert [rest = " world"]
```

## Rules That Don't Match Anything

A GROUP! runs ordinary code, without moving through the input, and its
value is the rule's value.  So is an INTEGER!, which stands for itself:

```
>> parse "abc" [one one one (10 + 20)]
== 30

>> parse "abc" [one one one 1020]
== 1020
```

ELIDE runs a rule but throws its value away, so the rule before it
supplies the result:

```
>> parse "ab" ["a" elide "b"]
== "a"
```

## See Also

* [Mismatches](/docs/dialects/parse/concepts/mismatches/)
* [Combinators](/docs/dialects/parse/combinators/), the rules themselves
