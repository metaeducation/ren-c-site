---
title: ACROSS
parent: Combinators
nav_order: 4
---

# ACROSS

Runs a rule, and gives back a copy of the input it moved across:

```
>> parse "aaabbb" [across some "a" some "b"]
== "b"

>> x: null
== \~null~\  ; antiform (logic!)

>> parse "aaabbb" [x: across some "a" some "b"]
== "b"

>> x
== "aaa"

>> parse "hello world" [thru space across to <end>]
== "world"
```

Text input gives a TEXT!, and list input gives a BLOCK!:

```
>> parse [a b 1 2] [across some word! some integer!]
== 2

>> parse [a b 1 2] [across [some word! some integer!]]
== [a b 1 2]
```

## Why Not COPY?

Historical PARSE used COPY for this.  That allowed writing `y: copy x:
...`, where `x` and `y` could end up holding different things.  ACROSS
names what's copied: the span of input the rule moved across.  In Revolt,
COPY in a rule gives an error pointing to ACROSS.

## See Also

* [Synthesis](/docs/dialects/parse/concepts/synthesis/)
