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

Sometimes a function has more than one thing to give back.  A search can
report where the match started *and* where it ended.  A scanner can give
the item it read *and* what's left to read.

In Revolt such a function returns a **pack**: several values travelling as
one result.  A pack is the [antiform](/docs/concepts/isotopes/) of
GROUP!, and PACK makes one from a block of expressions:

```
>> pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)

>> pack? pack [1 2]
== \~okay~\  ; antiform (logic!)
```

Multiple return values are the best known use of packs, but not the only
one.  Packs are also how "heavy" nulls and voids work, which is how a
branch can say it ran even when it produced nothing.

## If You Don't Ask, You Get the First Value

The first value of a pack is the main result.  A caller that just wants
*the* answer doesn't have to know a pack is involved: assigning a pack to
a variable, or passing it to an ordinary function, **decays** it to its
first value.

<!-- doctest: positive-test -->
```
both-ends: func [block] [
    return pack [first block, last block]
]

x: both-ends [10 20 30]
assert [x = 10]

assert [15 = (5 + both-ends [10 20 30])]
```

So a function can start returning extra information without breaking
anyone who was already calling it.  Anywhere a single value is wanted,
the same thing happens:

```
>> p: pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)

>> p
== 1

>> decay pack [1 2]
== 1

>> reduce [pack [1 2]]
== [1]
```

## Unpacking

To get the other values, put a block of variables on the left of the
assignment:

<!-- doctest: positive-test -->
```
[low high]: both-ends [10 20 30]
assert [low = 10]
assert [high = 30]
```

FIND is a built-in example.  It returns the position of the match, and
the position just after it.  Used plainly it decays to the first, and
unpacking gets both:

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

The block on the left has a little vocabulary of its own:

<!-- doctest: positive-test -->
```
[_ high]: both-ends [10 20 30]          ; _ skips a value
assert [high = 30]

[low :extra]: pack [10]                 ; :word is optional, NULL if absent
assert [extra = null]

result: ([low {high}]: both-ends [10 20 30])  ; {word} is the overall result
assert [result = 30]
```

Extra values in the pack are dropped.  And unpacking doesn't use the pack
up, so assignments can be chained:

<!-- doctest: positive-test -->
```
[a b]: [c d]: pack [1 2]
assert [[1 2 1 2] = reduce [a b c d]]
```

## Why Not Just Return a Block?

Getting here took three earlier designs, each used for real before being
abandoned.  The reasons they failed say what a pack has to be.

| Design | Why it failed |
|---|---|
| **Return a block**, and unpack it | A caller who didn't know got a block instead of a value.  A block is always true, so the result couldn't be tested.  And a block can't hold a NULL. |
| **Pass in the names of variables** to be written (as historical `do/next code 'pos` did) | The variable name is an *input*, so a function that wraps another can change the main result but not the extra ones.  And a function that fails halfway may already have written some of the caller's variables. |
| **A special value that acts like its first item** | If it can be stored, it shows up in data, and code enumerating a block sees only part of it. |

A pack avoids all three.  It decays for callers who don't care.  Nothing is
written to the caller's variables until the function has returned.  It
can't be put in a block, so it can't leak into data.  And since the values
are in the *result*, a wrapper sees all of them.

### Wrappers See Everything

Here ENCLOSE makes a version of BOTH-ENDS that adjusts the first result
and passes the second along.  With the variable-name designs, this couldn't
be written:

<!-- doctest: positive-test -->
```
both-ends-plus: enclose both-ends/ lambda [f] [
    let [low high]: eval-free f
    pack [low + 100, high]
]

[low high]: both-ends-plus [10 20 30]
assert [low = 110]
assert [high = 30]
```

## What's Inside a Pack

A pack holds its values [lifted](/docs/concepts/isotopes/#the-lifting-ladder),
which is why the items display with quote marks (`'1` rather than `1`).
Lifting is what lets a pack carry values that couldn't go in an ordinary
block, like NULL:

```
>> pack [null 2]
== \~(~null~ '2)~\  ; antiform (pack!)
```

<!-- doctest: positive-test -->
```
[found count]: pack [null 2]
assert [found = null]
assert [count = 2]
```

## Packs of One and of None

A pack doesn't have to have several items.  The smallest packs do an
important job: they distinguish "nothing" from "something happened, and
the result was nothing".

A pack holding just a NULL is a **heavy null**.  It decays to NULL, so
stored in a variable it's a plain NULL.  But before that, THEN and ELSE can
tell the difference.  That's how an IF whose branch ran and produced NULL
doesn't also run its ELSE:

```
>> if okay [null] else [<else>]
== \~(~null~)~\  ; antiform (pack!)

>> if null [null] else [<else>]
== <else>
```

<!-- doctest: positive-test -->
```
x: if okay [null]
assert [x = null]
```

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
`~()~` for an `IF` that did not run.  [Vanishing](/docs/concepts/vanishing/#heavy-void)
explains the part it plays there.

## Keeping a Pack

A pack is unstable, so a plain variable can't hold one: assigning it
keeps only the first value.  A variable written with the
[`^` sigil](/docs/datatypes/metaform/) holds the pack as it is:

<!-- doctest: positive-test -->
```
^whole: pack [1 2]
[a b]: ^whole
assert [[1 2] = reduce [a b]]
```

To put one somewhere a pack can't go, such as in a block, LIFT turns it
into a quasiform group, and UNLIFT brings the pack back:

<!-- doctest: positive-test -->
```
kept: lift pack [1 2]
[a b]: unlift kept
assert [[1 2] = reduce [a b]]
```

```
>> lift pack [1 2]
== ~('1 '2)~

>> reduce:predicate [pack [1 2]] lift/
== [~('1 '2)~]
```

## See Also

* [Isotopes](/docs/concepts/isotopes/) -- stable and unstable
* [METAFORM!](/docs/datatypes/metaform/) -- `^` variables and parameters,
  which keep a pack whole
* [VOID!](/docs/datatypes/void/) -- the light void, and how it becomes the
  heavy one
* [REDUCE](/docs/natives/reduce/) -- `:predicate lift/` keeps packs intact
* [The History of Multi-Return](https://revolt.metaeducation.com/forum/t/the-history-of-multi-return-in-ren-c/1134)
  (forum, 2019-2022)
