---
layout: default
title: Isotopes
parent: Concepts
grand_parent: Documentation
nav_order: 1
permalink: /docs/concepts/isotopes/
---

# Isotopes

Most values in Revolt come in a family of forms.  Take the word `null`:

| Form | Written | What it is |
|---|---|---|
| antiform | `~null~`, evaluated | the "false" signal: can't be put in a list |
| quasiform | `~null~` | a value in a list that stands for the antiform |
| plain | `null` | an ordinary word |
| quoted | `'null` | the word, with one level of quoting |
| quoted twice | `''null` | and so on, as many levels as you like |

The payload (the spelling `null`) is the same in each.  What changes is
how the evaluator and the rest of the system treat it.  Like isotopes in
chemistry, they're one element in different forms, which is where the
name comes from.

The forms are put in a fixed order, the **lifting ladder**, and one pair
of operations, LIFT and UNLIFT, moves any value one step up or down it.
That's the whole mechanism.  This page tells the story; the reference for
each form is on its type's page:

* [Antiform Types](/docs/datatypes/antiforms/) -- LOGIC!, SPLICE!,
  PACK! and the rest
* [QUASIFORM!](/docs/datatypes/quasiform/) and
  [QUOTED!](/docs/datatypes/quoted/), under
  [Decorated Types](/docs/datatypes/decorated/)

## Antiforms: Values That Can't Go in a List

An antiform is a variant of a value that **can't be put in a list**.  It
carries the same payload as the ordinary value, but it exists to be a
signal rather than data: "nothing here", "splice these", "this failed",
"here are several results".  Because an antiform can't end up inside a
block by accident, code that doesn't know about the signal can't mistake
it for data.

Eight fundamental types have antiforms, each with its own meaning:

| Antiform | Of | What it signals |
|---|---|---|
| [`LOGIC!`](/docs/datatypes/logic/) | `WORD!` | `~okay~` and `~null~`: true, and the one false |
| [`SPLICE!`](/docs/datatypes/splice/) | `BLOCK!` | items to be spliced into a list, not added as one |
| [`DATATYPE!`](/docs/datatypes/datatype/) | `FENCE!` | the type of a value |
| [`ACTION!`](/docs/datatypes/action/) | `FRAME!` | a function that runs when its word is evaluated |
| [`VOID!`](/docs/datatypes/void/) | `BLANK!` | no value |
| [`TRASH!`](/docs/datatypes/trash/) | `TAG!` | an unusable value, with a note saying why |
| [`PACK!`](/docs/datatypes/pack/) | `GROUP!` | several results at once |
| [`FAILURE!`](/docs/datatypes/failure/) | `ERROR!` | an error that must be dealt with |

These eight are the *isotopic* types.  Other types, such as numbers and
strings, have no antiform and no quasiform: just the plain form and the
quoted ones.

The console shows an antiform between backslashes, with a comment giving
its type:

```
>> spread [a b]
== \~[a b]~\  ; antiform (splice!)

>> null
== \~null~\  ; antiform (logic!)

>> type of 1
== \~{integer!}~\  ; antiform (datatype!)
```

But while antiforms can't be put *literally* in lists, they can be
signals that direct list operations.  A SPLICE! tells APPEND to add the
items rather than the block:

```
>> s: spread [a b]
== \~[a b]~\  ; antiform (splice!)

>> append [x] s
== [x a b]
```

## Quasiforms: How an Antiform Is Written Down

The notation between the console's backslashes is the antiform's
**quasiform**: the same payload with tildes around it.  A quasiform is
an ordinary value that *can* go in a list, and evaluating one gives the
antiform:

```
>> first [~[a b]~]
== ~[a b]~

>> ~[a b]~
== \~[a b]~\  ; antiform (splice!)
```

So whenever an antiform needs to be stored, or shown, its quasiform
stands in for it.  Quasiforms are values in their own right too, which
dialects can give meanings of their own.  See
[QUASIFORM!](/docs/datatypes/quasiform/).

## Quoting: Values That Evaluate to Values

Above the plain form are the quoted ones.  Any element can have any
number of `'` marks on the front, and each evaluation takes one off:

```
>> 'foo
== foo

>> ''foo
== 'foo
```

Quoting is what lets code mention a value without running it.  See
[QUOTED!](/docs/datatypes/quoted/).

## The Lifting Ladder

Quoting and quasiforms stack up in a fixed order.  From the bottom:

```text
    antiform        ~null~ (evaluated)     can't go in a list
    quasiform       ~null~                 a value in a list
    quoted          '~null~                one quote
    quoted twice    ''~null~               two quotes, and so on
```

A plain value has the same ladder above it, without the bottom two rungs:

```text
    plain           foo
    quoted          'foo
    quoted twice    ''foo
```

**LIFT** moves any value up one rung, and **UNLIFT** moves it down one.
LIFT of an antiform is its quasiform, and LIFT of anything else adds a
quote:

```
>> lift null
== ~null~

>> lift lift null
== '~null~

>> lift 1
== '1

>> lift lift 'foo
== ''foo

>> unlift first [~[a b]~]
== \~[a b]~\  ; antiform (splice!)

>> unlift first ['1]
== 1
```

What comes out of LIFT can always be put in a list.  So a signal can be
put into "suspended animation" in a block, and brought back later with
nothing lost.  This one pair of operations works for every antiform,
current and future, which is the reason antiforms are a general mechanism
rather than a collection of special types.

LIFT is used all over the system.  A [PACK!](/docs/datatypes/pack/) holds
its values lifted, which is how a pack can contain a null or another
pack.  Before there was a `^` sigil to [store an antiform
directly](/docs/datatypes/metaform/), lifting was how you held on to one.

### You Can Quote a Quasiform, but Not Quasi a Quote

The quasi rung is always directly above the antiform, and there is only
one of it.  So a quasiform can be quoted any number of times:

```
>> quote first [~foo~]
== '~foo~
```

but a quoted value can't be made quasi, because the result would have a
quasi rung *above* a quote:

<!-- doctest: negative-test match="expect-arg" -->
```
quasi first ['foo]
```

And an antiform can't be quoted, since that would skip the quasi rung:

<!-- doctest: negative-test match="expect-arg" -->
```
quote null
```

The ladder has no gaps and no branches.  That's what makes LIFT and
UNLIFT exact: whatever you lift, unlifting gives back exactly what you
started with, antiform or not.

## Stable and Unstable

Antiforms come in two grades.

**Stable** antiforms (LOGIC!, SPLICE!, DATATYPE!, ACTION!) can be held in
a variable and passed as an argument.  They just can't be put in a list:

```
>> reduce [null]
** PANIC: Invalid use of ~null~ antiform
```

**Unstable** antiforms (VOID!, TRASH!, PACK!, FAILURE!) go further: they
can't be fetched from WORD! variables or passed as normal arguments.
Assigning one either *decays* it to a stable value (a PACK! becomes its
first item), unsets the variable (VOID!), or errors (FAILURE!).  They
have to be dealt with where they are produced, or LIFTed first, or stored
and fetched with the [`^` sigil](/docs/datatypes/metaform/), which turns
those conversions off.

```
>> p: pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)

>> p
== 1

>> x: fail "oops"
** Failure: oops
```

The practical consequence: anything you can get from a plain variable can
be tested by `IF` without special handling.

## Telling Them Apart

```
>> antiform? spread [a]
== \~okay~\  ; antiform (logic!)

>> element? spread [a]
== \~null~\  ; antiform (logic!)

>> element? 1
== \~okay~\  ; antiform (logic!)

>> any-stable? spread [a]
== \~okay~\  ; antiform (logic!)

>> quasiform? first [~[a]~]
== \~okay~\  ; antiform (logic!)

>> quoted? first ['a]
== \~okay~\  ; antiform (logic!)
```

The type of a quasiform or a quoted value is QUASIFORM! or QUOTED!, not
the type underneath.  HEART OF gives the underlying type:

```
>> type of first ['[a b]]
== \~{quoted!}~\  ; antiform (datatype!)

>> heart of first ['[a b]]
== \~{block!}~\  ; antiform (datatype!)
```

To ask which fundamental type an antiform came from, lift it, take the
quasi off, and ask that:

```
>> type of unquasi lift spread [a]
== \~{block!}~\  ; antiform (datatype!)

>> type of unquasi lift null
== \~{word!}~\  ; antiform (datatype!)
```

## Why

The design argument, and the history of how the eight came to be the
eight, is on the forum rather than here:

* [A Justification of Generalized Isotopes](https://revolt.metaeducation.com/forum/t/a-justification-of-generalized-isotopes/1918)
  (2022, kept current) -- why one lift/unlift mechanism beats a pile of
  special types, starting from the old `APPEND/ONLY` problem.
* [Which Antiforms Are In Use?](https://revolt.metaeducation.com/forum/t/which-antiforms-are-in-use/2276)
  (2024, kept current) -- the table above, and a history of which type
  each antiform has been attached to over time.
