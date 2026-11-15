---
layout: datatype
title: PACK!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 7
permalink: /docs/datatypes/pack/
datatype: pack!
antiform-of: group!
stable: false
summary: multi-return that decays to first item, empty is HEAVY VOID
sample: "pack [1 2]"
---

A PACK! carries several results at once.  It is how a function returns
more than one value.  `PACK` makes one from a block of expressions:

```
>> pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)

>> pack? pack [1 2]
== \~okay~\  ; antiform (logic!)
```

The items inside are shown lifted (`'1` rather than `1`), because a pack
can hold any result, including antiforms, and lifting is how those are
kept in a group.

## Decay

A pack is unstable: it can't be held in a variable.  Where a single value
is wanted, the pack *decays* to its first item:

```
>> p: pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)

>> p
== 1

>> add pack [1 2] 10
== 11

>> decay pack [1 2]
== 1

>> reduce [pack [1 2]]
== [1]
```

## Unpacking

A block of words on the left of a `:` takes the items apart:

```
>> [a b]: pack [10 20]
== \~('10 '20)~\  ; antiform (pack!)

>> a
== 10

>> b
== 20
```

Extra items are dropped:

```
>> [c]: pack [1 2 3]
== \~('1 '2 '3)~\  ; antiform (pack!)

>> c
== 1
```

`FIND` is an example of a function that returns a pack: the position of
the match, and the position after it.  Used plainly it decays to the
first, and unpacking gets both:

```
>> [pos rest]: find [a b c] 'b
== \~('[b c] '[c])~\  ; antiform (pack!)

>> pos
== [b c]

>> rest
== [c]

>> first find [a b c] 'b
== b
```

## Keeping the Whole Pack

Lifting a pack gives a quasiform group, which can be stored like any
other element:

```
>> lift pack [1 2]
== ~('1 '2)~

>> reduce:predicate [pack [1 2]] lift/
== [~('1 '2)~]
```

## The Empty Pack Is the Heavy Void

A pack with nothing in it is the **heavy void**, written `~()~`.  It has
no first item to decay to:

```
>> pack []
== \~()~\  ; antiform (pack!)

>> x: pack []
** PANIC: Empty PACK! cannot decay to single value

>> any-void? pack []
== \~okay~\  ; antiform (logic!)
```

It is also what a block of code evaluates to when its last expression
produced a [VOID!](/docs/datatypes/void/), which is why the console shows
`~()~` for an `IF` that did not run.

## See Also

* [VOID!](/docs/datatypes/void/) -- the light void, and how it becomes the
  heavy one
* [REDUCE](/docs/natives/reduce/) -- `:predicate lift/` keeps packs intact
* [Antiforms](/docs/concepts/antiforms/) -- the general mechanism
