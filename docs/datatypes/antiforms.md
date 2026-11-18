---
layout: default
title: Antiform Types
parent: Datatypes
nav_order: 4
has_children: true
permalink: /docs/datatypes/antiforms/
---

# Antiform Types

The types a value has when it **can't be put in a list**.  Each is the
antiform of one [fundamental type](/docs/datatypes/fundamentals/), and is
used as a signal rather than as data.

| Antiform | Of | What it signals | Stable? |
|---|---|---|---|
| [`LOGIC!`](/docs/datatypes/logic/) | [`WORD!`](/docs/datatypes/word/) | `~okay~` and `~null~`: true, and the one false | yes |
| [`SPLICE!`](/docs/datatypes/splice/) | [`BLOCK!`](/docs/datatypes/block/) | items to be spliced into a list, not added as one | yes |
| [`DATATYPE!`](/docs/datatypes/datatype/) | [`FENCE!`](/docs/datatypes/fence/) | the type of a value | yes |
| [`ACTION!`](/docs/datatypes/action/) | [`FRAME!`](/docs/datatypes/frame/) | a function that runs when its word is evaluated | yes |
| [`VOID!`](/docs/datatypes/void/) | [`BLANK!`](/docs/datatypes/blank/) | no value | no |
| [`TRASH!`](/docs/datatypes/trash/) | [`TAG!`](/docs/datatypes/tag/) | an unusable value, with a note saying why | no |
| [`PACK!`](/docs/datatypes/pack/) | [`GROUP!`](/docs/datatypes/group/) | several results at once | no |
| [`FAILURE!`](/docs/datatypes/failure/) | [`ERROR!`](/docs/datatypes/error/) | an error that must be dealt with | no |

An antiform is written as its [quasiform](/docs/datatypes/quasiform/),
the same value with tildes around it.  The console shows it between
backslashes, and evaluating the quasiform gives the antiform:

```
>> ~[a b]~
== \~[a b]~\  ; antiform (splice!)
```

**Stable** antiforms can be held in a variable and passed as an argument.
**Unstable** ones can't even do that: assigning one to a plain variable
decays it (a pack to its first item), or panics (a failure).  Only a
[`^` variable or parameter](/docs/datatypes/metaform/) holds one as it is.

To put any antiform in a list, LIFT it to its quasiform, and UNLIFT to
get it back.

How antiforms fit together with quasiforms and quoting, and why they're
one general mechanism rather than eight special cases, is explained in
**[Isotopes](/docs/concepts/isotopes/)**, under Concepts.  The pages here
are the reference for each type.
