---
layout: datatype
title: SPLICE!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 2
permalink: /docs/datatypes/splice/
datatype: splice!
antiform-of: block!
stable: true
summary: fragment of multiple values without a surrounding container
sample: "spread [a b c]"
---

A SPLICE! is a run of values with no container around them.  When one is
added to a list, its items go in individually.  A plain block goes in as
one item:

```
>> append [1 2] [a b c]
== [1 2 [a b c]]

>> append [1 2] spread [a b c]
== [1 2 a b c]
```

`SPREAD` makes a splice from any list:

```
>> spread [a b c]
== \~[a b c]~\  ; antiform (splice!)

>> type of spread [a b c]
== \~{splice!}~\  ; antiform (datatype!)
```

The intent to splice travels with the value.  So it can be held in a
variable and used later, and the operation that receives it needs no
refinement to say what to do:

```
>> s: spread [a b c]
== \~[a b c]~\  ; antiform (splice!)

>> append [1 2] s
== [1 2 a b c]

>> compose [x (s) y]
== [x a b c y]

>> collect [keep s, keep [d]]
== [a b c [d]]
```

## Empty Splices

Splicing nothing is allowed, and adds nothing:

```
>> spread []
== \~[]~\  ; antiform (splice!)

>> append [1 2] spread []
== [1 2]
```

## Not a Series

A splice is not itself a list.  The series operations don't take one:

```
>> splice? s
== \~okay~\  ; antiform (logic!)

>> element? s
== \~null~\  ; antiform (logic!)
```

To get at the items as a block, lift the splice (which gives its
quasiform) and take the quasi off:

```
>> lift s
== ~[a b c]~

>> unquasi lift s
== [a b c]
```

And a quasiform block in a list evaluates to a splice:

```
>> first [~[a b]~]
== ~[a b]~

>> unlift first [~[a b]~]
== \~[a b]~\  ; antiform (splice!)
```

## What Can Be Spread

`SPREAD` takes any list (BLOCK!, GROUP!, FENCE!).  It does not take a
string or a single value; there is nothing to splice, and asking is an
error:

<!-- doctest: negative-test match="plain lists become splices" -->
```
spread "abc"
```

## See Also

* [REDUCE](/docs/natives/reduce/) -- accepts a splice only if it holds one
  item, unless given a predicate
* [Isotopes](/docs/concepts/isotopes/) -- the general mechanism, and
  the history of this one, which started life as the antiform of GROUP!
