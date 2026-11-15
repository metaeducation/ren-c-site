---
layout: native
title: REDUCE
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/reduce/
native: reduce
spec: |
  "Evaluates N expressions to produce N results (but discards BLANK!)"
  return: [<null> element?]
  value "Lists evaluate each item, single values evaluate"
      [element?]
  :predicate "Applied after evaluation, default is IDENTITY"
      [frame!]
---

REDUCE evaluates each expression in a list, and collects the results into a
new list of the same type.

<!-- doctest: transcript -->
```
>> reduce [1 + 2 3 + 4]
== [3 7]

>> x: 10
== 10

>> reduce [x 'x (x * 2)]
== [10 x 20]
```

Commas can be used to make the boundaries between expressions clear.  They
don't produce anything themselves:

```
>> reduce [1 + 2, 3 + 4]
== [3 7]
```

## N Expressions In, N Values Out

The defining rule of REDUCE is that **every expression produces exactly one
value** in the result.  If you see three expressions in the input, you know
there will be three values in the output.

This means that an expression which produces "nothing" (a VOID!) is an
error, not something that silently drops out:

```
>> reduce [1 elide 2 3]
** PANIC: Cannot decay VOID! to a stable value
```

The same goes for anything else that produces VOID!, such as COMMENT, or an
IF whose condition was false:

```
>> reduce [comment "hi" 1]
** PANIC: Cannot decay VOID! to a stable value

>> reduce [if null [1]]
** PANIC: Cannot decay VOID! to a stable value
```

Antiforms such as NULL can't be put in a list, so they are errors too:

```
>> reduce [null]
** PANIC: Invalid use of ~null~ antiform
** Id: bad-antiform
```

A SPLICE! is accepted only if it holds exactly one item, because that keeps
the one-expression-one-value rule:

```
>> reduce [spread [a]]
== [a]

>> reduce [spread [a b]]
** PANIC: SPLICE! used in REDUCE w/no predicate must be 1 item
```

{: .tip }
> **If you want VOID! to vanish, use JOIN.**  JOIN with a type evaluates the
> list the way REDUCE does, but drops VOID! results and splices SPLICE!s.

```
>> join block! [1 elide 2 3]
== [1 3]
```

## Predicates

The `:predicate` refinement runs a function on each result before it is
collected.  The predicate is allowed to break the one-to-one rule: if it
returns VOID! the value is dropped, and if it returns a SPLICE! all of its
items are added.

```
>> reduce:predicate [1 2 3] lambda [x] [x * 10]
== [10 20 30]

>> reduce:predicate [1 null 2] opt/
== [1 2]

>> reduce:predicate [1 + 2 spread [a b]] identity/
== [3 a b]
```

The predicate LIFT keeps antiforms as quasiforms, which is how PACK gets
its values:

```
>> reduce:predicate [1 null 2] lift/
== ['1 ~null~ '2]
```

## VETO

If any expression produces a VETO, the whole REDUCE returns NULL:

```
>> reduce [1 veto 2]
== \~null~\  ; antiform (logic!)
```

## Non-List Input

Values that don't evaluate to anything other than themselves are returned
as is:

```
>> reduce "text"
== "text"
```

## A Full Script Example

Blocks tagged `positive-test` run as scripts and must not error.

<!-- doctest: positive-test -->
```
data: reduce [1 + 1, 2 * 3, length of "abc"]
assert [data = [2 6 3]]
```

Blocks tagged `negative-test` must error, and the error must match the
phrase given in the tag:

<!-- doctest: negative-test match="Cannot decay VOID!" -->
```
reduce [1 + 1, elide print "side effect", 3]
```

## Why Not Just Drop VOID!?

Earlier versions of REDUCE did erase VOID!, and the decision to stop doing
that is discussed on the forum:

* [VOID! Behavior in REDUCE](https://revolt.metaeducation.com/forum/t/void-behavior-in-reduce/2703)
* [REDUCE Religiosity: N Expressions In, N Values Out](https://revolt.metaeducation.com/forum/t/reduce-religiosity-n-expressions-in-n-values-out/2642)
* [Should VOID! Be Offered to Predicates for REDUCE, ANY, ALL, etc.?](https://revolt.metaeducation.com/forum/t/should-void-be-offered-to-predicates-for-reduce-any-all-etc/1872)

## See Also

* JOIN -- evaluate a list, dropping VOID! and splicing SPLICE!s
* PACK -- REDUCE with LIFT, producing a multi-return antiform
* COMPOSE -- evaluate only the GROUP!s in a list
