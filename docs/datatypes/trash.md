---
layout: datatype
title: TRASH!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 6
permalink: /docs/datatypes/trash/
datatype: trash!
antiform-of: tag!
stable: false
summary: panics on WORD! access, console does not display
sample: "~<unused>~"
---

A TRASH! is a value that is not meant to be used, carrying a note that
says why.  It is the antiform of a TAG!, so the note is the tag's text:

```rebol
>> ~<deprecated>~
== \~<deprecated>~\  ; antiform (trash!)

>> trash? ~<deprecated>~
== \~okay~\  ; antiform (logic!)
```

## Reading One Is an Error

A variable can be *set* to a trash, which marks it as unusable.  Reading
it through its word is an error that repeats the note:

```rebol
>> t: ~<deprecated>~
== \~<deprecated>~\  ; antiform (trash!)

>> t
** PANIC: ^t is ~<deprecated>~ antiform (see ^(...) and GET:ANY)
```

The variable is set, not unset, and the trash can be got at deliberately
with `GET` or a `^` access:

```rebol
>> unset? $t
== \~null~\  ; antiform (logic!)

>> trash? get $t
== \~okay~\  ; antiform (logic!)

>> lift get $t
== ~<deprecated>~
```

## Where Trash Comes From

Functions that are run for their effect return a trash naming
themselves, so that using their "result" by mistake is caught:

```rebol
>> print "hi"
hi
== \~<print>~\  ; antiform (trash!)
```

## Unstable

A trash can't be put in a list, and can't be decayed to an ordinary
value, so it can't take part in an expression that wants one:

```rebol
>> all [1 ~<x>~ 2]
** PANIC: Cannot decay TRASH! to a stable value

>> type of ~<x>~
** PANIC: Cannot decay TRASH! to a stable value
```

An evaluation step that produces a trash and moves on is allowed, which
is what makes it usable as a marker at the start of a line.  It does not
vanish the way a [VOID!](/docs/datatypes/void/) from `COMMENT` does:

```rebol
>> ~<note>~ 1 + 2
== 3

>> 1 + 2 ~<note>~
** PANIC: Pure evaluation product discarded: 3
```

## See Also

* [VOID!](/docs/datatypes/void/) -- "no value", for when there is nothing
  to say about why
* [Antiforms](/docs/concepts/antiforms/) -- the general mechanism, and
  the history of this one (it has been the antiform of RUNE! as well)
