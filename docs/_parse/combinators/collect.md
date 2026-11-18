---
title: COLLECT
parent: Combinators
nav_order: 5
---

# COLLECT

Runs a rule, and gives back a block of everything KEEP kept while it ran:

```
>> parse [1 a 2 b] [collect [some [keep integer! | word!]]]
== [1 2]

>> parse "abc" [collect [some [keep one]]]
== [#a #b #c]
```

## Rollback

Things kept by a rule that then fails are dropped.  Here the first
alternative keeps the `1`, then fails on the `b`, so the `1` doesn't stay
kept when the second alternative runs:

```
>> parse [1 b] [collect [keep integer! 'a | one keep word!]]
== [b]
```

(Red's COLLECT, where this feature started, keeps them.)

## See Also

* `accumulate`, a shorter way to write `collect [opt some keep ...]`
* `gather` and `emit`, which build an object instead of a block
