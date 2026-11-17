---
layout: default
title: List Types
parent: Datatypes
grand_parent: Documentation
nav_order: 2
has_children: true
permalink: /docs/datatypes/lists/
---

# List Types

A **list** holds any number of elements between a pair of delimiters.
There are three, and the delimiters decide what the evaluator does with
one:

| Type | Written | Evaluating it gives | Antiform |
|---|---|---|---|
| [`BLOCK!`](/docs/datatypes/block/) | `[a b]` | the block itself, unevaluated | [SPLICE!](/docs/datatypes/splice/) |
| [`GROUP!`](/docs/datatypes/group/) | `(a b)` | the result of running it | [PACK!](/docs/datatypes/pack/) |
| [`FENCE!`](/docs/datatypes/fence/) | `{a b}` | a block bound into a new context, for MAKE or EVAL | [DATATYPE!](/docs/datatypes/datatype/) |

```
>> [1 + 2]
== [1 + 2]

>> (1 + 2)
== 3

>> any-list? first [{a: 1}]
== \~okay~\  ; antiform (logic!)
```

## Lists Are Series

Lists work much as they did in historical Rebol.  Each is a *series*: a
list value has a position in it, and the same items can be seen from more
than one position.  NEXT, BACK, SKIP and INDEX OF move and report the
position, and APPEND, INSERT, CHANGE and REMOVE modify the list in place:

```
>> next [a b c]
== [b c]

>> index of next [a b c]
== 2

>> append copy [a b] 'c
== [a b c]
```

What's different is about *who may modify* a list.  A literal list in a
function body is read-only unless you say otherwise, so that the classic
bug of a `[]` in a body silently growing on each call can't happen.  See
[Constness](/docs/concepts/constness/).

Lists also keep the line breaks they were written with, which is how
code that's been loaded and molded back out still looks like what was
written.

## Lists Compared to Sequences

The other kind of container is the
[sequence](/docs/datatypes/sequences/): `a/b`, `a.b`, `a:b`.  Sequences
aren't series.  They're immutable, have no position, and have rules about
what they can hold.  To work on one as if it were a list, convert it to a
block and back:

```
>> as block! 'a/b/c
== [a b c]

>> as path! [a b c]
== a/b/c
```

## See Also

* [Sequence Types](/docs/datatypes/sequences/) -- the immutable containers
* [Constness](/docs/concepts/constness/) -- when a list may be modified
* [Evaluation](/docs/concepts/evaluation/#blocks-and-groups-are-evaluated-differently) -- why BLOCK!
  and GROUP! evaluate differently
