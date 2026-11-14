---
layout: default
title: Antiforms
parent: Datatypes
grand_parent: Documentation
nav_order: 1
has_children: true
permalink: /docs/datatypes/antiforms/
---

# Antiforms

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

## How They Look

The console shows an antiform between backslashes, with a comment giving
its type.  The notation inside the backslashes is the antiform's
*quasiform*: the same payload with tildes around it.

```rebol
>> spread [a b]
== \~[a b]~\  ; antiform (splice!)

>> null
== \~null~\  ; antiform (logic!)

>> type of 1
== \~{integer!}~\  ; antiform (datatype!)
```

## Quasiforms, LIFT, and UNLIFT

An antiform can't go in a list, but its quasiform can.  Evaluating a
quasiform gives the antiform back:

```rebol
>> first [~[a b]~]
== ~[a b]~

>> ~[a b]~
== \~[a b]~\  ; antiform (splice!)
```

`LIFT` turns any value into something that can be stored: antiforms become
quasiforms, and everything else gains a level of quoting.  `UNLIFT` undoes
it exactly.  So a signal can be put into "suspended animation" in a list,
and brought back later:

```rebol
>> lift spread [a b]
== ~[a b]~

>> lift 1
== '1

>> unlift first [~[a b]~]
== \~[a b]~\  ; antiform (splice!)

>> unlift first ['1]
== 1
```

This one pair of operations works for every antiform, current and future,
which is the reason antiforms are a general mechanism rather than a
collection of special types.

## Stable and Unstable

Antiforms come in two grades.

**Stable** antiforms (LOGIC!, SPLICE!, DATATYPE!, ACTION!) can be held in
a variable and passed as an argument.  They just can't be put in a list.

```rebol
>> s: spread [a b]
== \~[a b]~\  ; antiform (splice!)

>> append [x] s
== [x a b]

>> reduce [null]
** PANIC: Invalid use of ~null~ antiform
```

**Unstable** antiforms (VOID!, TRASH!, PACK!, FAILURE!) can't even be
held in a variable.  Assigning one either *decays* it to a stable value
(a PACK! becomes its first item), unsets the variable (VOID!), or errors
(FAILURE!).  They have to be dealt with where they are produced, or
`LIFT`ed first.

```rebol
>> p: pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)

>> p
== 1

>> x: fail "oops"
** Failure: oops
```

The practical consequence: anything that can sit in a variable can be
tested by `IF` without special handling, because the antiforms that
can't be tested are exactly the ones that can't sit in a variable.

## Telling Them Apart

```rebol
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

>> type of first [~[a]~]
== \~{quasiform!}~\  ; antiform (datatype!)
```

To ask which fundamental type an antiform came from, lift it, take the
quasi off, and ask that:

```rebol
>> type of unquasi lift spread [a]
== \~{block!}~\  ; antiform (datatype!)

>> type of unquasi lift null
== \~{word!}~\  ; antiform (datatype!)
```

## Why

The design argument, and the history of how the eight came to be the eight,
is on the forum rather than here:

* [A Justification of Generalized Isotopes](https://rebol.metaeducation.com/t/a-justification-of-generalized-isotopes/1918)
  (2022, kept current) -- why one lift/unlift mechanism beats a pile of
  special types, starting from the old `APPEND/ONLY` problem.  ("Isotopes"
  was the earlier name for antiforms and quasiforms together.)
* [Which Antiforms Are In Use?](https://rebol.metaeducation.com/t/which-antiforms-are-in-use/2276)
  (2024, kept current) -- the table above, and a history of which type
  each antiform has been attached to over time.
