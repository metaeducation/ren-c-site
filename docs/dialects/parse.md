---
layout: default
title: PARSE
parent: Dialects
nav_order: 1
permalink: /docs/dialects/parse/
universe: parse
---

# PARSE

PARSE matches an input against a block of **rules**.  The input can be a
string, a binary or a block, and the rules say what should be found in it,
in order:

```
>> parse "aaabbb" [some "a" some "b"]
== "b"

>> parse [1 2 3] [some integer!]
== 3
```

The rules have to account for the *whole* input.  If they don't, PARSE
gives back a [FAILURE!](/docs/datatypes/failure/):

<!-- doctest: negative-test match="parse-incomplete" -->
```
parse "aab" [some "a"]
```

## Rules Give Back Values

A successful PARSE doesn't just say "yes".  Every rule produces a value,
and PARSE gives back the value of the last one.  `some "b"` produced the
last `"b"` it matched, so that's what the first example returned.

Rules like ACROSS and COLLECT exist to produce something useful:

```
>> parse "hello world" [thru space across to <end>]
== "world"

>> parse [1 a 2 b] [collect [some [keep integer! | word!]]]
== [1 2]
```

See [Synthesis](/docs/dialects/parse/concepts/synthesis/).

## Built From Combinators

Every keyword in a rule, like SOME or ACROSS, is a **combinator**: a
function that takes the input and gives back what it matched, and how far
it got.  Combinators are ordinary functions, so PARSE can be extended
with new ones, or given a different set entirely.  (The Rebol2-compatible
PARSE in the Redbol module is UPARSE with a different set of combinators.)

The [Combinators](/docs/dialects/parse/combinators/) page lists them.

{: .warning }
> This section is a skeleton.  Most combinators don't have pages yet.

## See Also

* [`tests/parse/`](https://github.com/metaeducation/revolt/tree/master/tests/parse)
  in the interpreter's repository, with a file of tests for each combinator
