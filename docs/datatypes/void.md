---
layout: datatype
title: VOID!
parent: Antiforms
grand_parent: Datatypes
nav_order: 5
permalink: /docs/datatypes/void/
datatype: void!
antiform-of: blank!
stable: false
summary: panics on WORD! access, multi-step evaluations discard
sample: 'comment "nothing"'
---

VOID! is the absence of a value.  Its quasiform is a bare tilde, so it
lifts to `~`:

```rebol
>> comment "nothing"
== \~\  ; antiform (void!)

>> lift comment "nothing"
== ~

>> void? comment "nothing"
== \~okay~\  ; antiform (logic!)
```

`COMMENT`, `ELIDE`, an `IF` whose condition was false, and `OPT` of a
null all produce it:

```rebol
>> void? elide 5
== \~okay~\  ; antiform (logic!)

>> void? if null [1]
== \~okay~\  ; antiform (logic!)

>> void? opt null
== \~okay~\  ; antiform (logic!)
```

## Vanishing

Some voids *vanish*: the evaluator treats the expression as if it weren't
there, so the value before it is kept.  `COMMENT`, `ELIDE`, and `GHOST`
produce vanishing voids:

```rebol
>> 1 + 2 comment "nothing"
== 3

>> 1 + 2 elide 5
== 3
```

The void from a false `IF` does not vanish.  It is a result, and an
unused result before it is an error:

```rebol
>> 1 + 2 if null [3]
** PANIC: Pure evaluation product discarded: 3
```

## Heavy Void

When a void is the last thing a block of code produces, the block's
result is the **heavy void**: an empty [PACK!](/docs/datatypes/pack/),
written `~()~`.  That is what the console shows for an `IF` that didn't
run, since the console evaluates your input as a block:

```rebol
>> if null [1]
== \~()~\  ; antiform (pack!)

>> lift if null [1]
== ~
```

`ANY-VOID?` is true of both the light and heavy forms.  `VOID?` is only
for the light one, and says so if given the heavy one:

```rebol
>> any-void? pack []
== \~okay~\  ; antiform (logic!)

>> void? pack []
** PANIC: HEAVY VOID passed to VOID?; use ANY-VOID? to test both
```

## Unstable

A VOID! can't be held in a variable.  Assigning one *unsets* the variable,
and reading it is then an error:

```rebol
>> v: comment "nothing"
== \~\  ; antiform (void!)

>> unset? $v
== \~okay~\  ; antiform (logic!)

>> v
** PANIC: Unexpected unstable in non-^META pick of ^v
```

Nor can it go in a list.  Operations that build a list from evaluated
expressions differ in what they do with one: `REDUCE` refuses, while
`COMPOSE` and `JOIN` let it drop out:

```rebol
>> reduce [1 if null [3] 2]
** PANIC: Cannot decay VOID! to a stable value

>> compose [a (if null [1]) b]
== [a b]

>> join block! [1 if null [3] 2]
== [1 2]
```

This is the usual way to say "include this item only if...": produce a
void when it shouldn't be there.  `OPT` turns a null into a void for
exactly that purpose:

```rebol
>> compose [a (opt select [x 1] 'z) b]
== [a b]
```

## See Also

* [PACK!](/docs/datatypes/pack/) -- the empty pack is the heavy void
* [LOGIC!](/docs/datatypes/logic/) -- `~null~` is "false", not "nothing"
* [REDUCE](/docs/natives/reduce/) -- why REDUCE refuses voids
* [Antiforms](/docs/datatypes/antiforms/) -- the general mechanism
