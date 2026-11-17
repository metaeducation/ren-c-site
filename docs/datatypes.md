---
layout: default
title: Datatypes
parent: Documentation
nav_order: 2
has_children: true
permalink: /docs/datatypes/
---

# Datatypes

Every value has a type, and `type of` tells you which:

```
>> type of [a b c]
== \~{block!}~\  ; antiform (datatype!)

>> type of 1.5
== \~{decimal!}~\  ; antiform (datatype!)
```

The type is itself a value (a [DATATYPE!](/docs/datatypes/datatype/)),
so it can be compared, matched against, and used to make new values:

```
>> integer! = type of 1
== \~okay~\  ; antiform (logic!)

>> match [integer! text!] "abc"
== "abc"

>> make block! 3
== []
```

## Fundamental Types

These are the types a value in a list can have.  The one-line summaries
are the ones the interpreter's own `types.r` table gives them.

### Numbers and other scalars

| Type | Summary | Example |
|---|---|---|
| [`INTEGER!`](/docs/datatypes/integer/) | 64 bit integer | `1` |
| [`DECIMAL!`](/docs/datatypes/decimal/) | 64bit floating point number (IEEE standard) | `1.5` |
| [`PERCENT!`](/docs/datatypes/percent/) | special form of decimals (used mainly for layout) | `10%` |
| [`PAIR!`](/docs/datatypes/pair/) | two dimensional point or size | `10x20` |
| [`TIME!`](/docs/datatypes/time/) | time of day or duration | `12:30` |
| [`DATE!`](/docs/datatypes/date/) | day, month, year, time of day, and timezone | `1-Jan-2026` |

### Strings and other UTF-8 values

| Type | Summary | Example |
|---|---|---|
| [`TEXT!`](/docs/datatypes/text/) | text string series of characters | `"abc"` |
| [`FILE!`](/docs/datatypes/file/) | file name or path | `%file.txt` |
| [`TAG!`](/docs/datatypes/tag/) | markup string (HTML or XML) | `<div>` |
| [`URL!`](/docs/datatypes/url/) | uniform resource locator or identifier | `decode-url <http://example.com>` |
| [`EMAIL!`](/docs/datatypes/email/) | email address | `user@example.com` |
| [`RUNE!`](/docs/datatypes/rune/) | immutable codepoint or codepoint sequence | `#a` |
| [`BLOB!`](/docs/datatypes/blob/) | series of bytes | `#{DECAFBAD}` |

### Lists

Mutable series, as in historical Rebol.  See
[List Types](/docs/datatypes/lists/).

| Type | Summary | Example |
|---|---|---|
| [`BLOCK!`](/docs/datatypes/block/) | list of elements that blocks evaluation unless EVAL is used | `[a b]` |
| [`GROUP!`](/docs/datatypes/group/) | list that evaluates expressions as an isolated group | `(a b)` |
| [`FENCE!`](/docs/datatypes/fence/) | list of elements that are used in construction via MAKE | `{a b}` |

### Sequences

Immutable, and not series.  See
[Sequence Types](/docs/datatypes/sequences/).

| Type | Summary | Example |
|---|---|---|
| [`TUPLE!`](/docs/datatypes/tuple/) | member selection with inert bias | `a.b` |
| [`CHAIN!`](/docs/datatypes/chain/) | refinement and function call dialect | `a:b` |
| [`PATH!`](/docs/datatypes/path/) | member or refinement selection with execution bias | `a/b` |

### Words

| Type | Summary | Example |
|---|---|---|
| [`WORD!`](/docs/datatypes/word/) | evaluates a variable or action | `a` |

Setting and getting are spelled with CHAIN!s: `a:` is the word with an
empty slot after it, and `:a` with one before.

### Contexts

| Type | Summary | Example |
|---|---|---|
| [`OBJECT!`](/docs/datatypes/object/) | context of names with values | `make object! [a: 1]` |
| [`MODULE!`](/docs/datatypes/module/) | loadable context of code and data | |
| [`ERROR!`](/docs/datatypes/error/) | context with id, arguments, and stack origin | `make error! "oops"` |
| [`PORT!`](/docs/datatypes/port/) | external series, an I/O channel | |
| [`FRAME!`](/docs/datatypes/frame/) | arguments and locals of a function state | `make frame! append/` |
| [`LET!`](/docs/datatypes/let/) | context containing a single variable | |

### Other

| Type | Summary | Example |
|---|---|---|
| [`BLANK!`](/docs/datatypes/blank/) | evaluation separator, no rendering (shows in lists via commas) | the `,` in `[a, b]` |
| [`MAP!`](/docs/datatypes/map/) | name-value pairs (hash associative) | `make map! [a 1]` |
| [`BITSET!`](/docs/datatypes/bitset/) | set of bit flags | `make bitset! "abc"` |
| [`HANDLE!`](/docs/datatypes/handle/) | arbitrary internal object or value | |
| [`OPAQUE!`](/docs/datatypes/opaque/) | extension cell which uses its type information slot for data | |
| [`VARARGS!`](/docs/datatypes/varargs/) | evaluator position for variable numbers of arguments | |
| [`PARAMETER!`](/docs/datatypes/parameter/) | function parameter description | |

## Decorated Forms

Any element can be decorated, which gives it a different type while it
keeps the same payload.  Evaluating a decorated value undoes one level of
decoration (a quoted value evaluates to the plain value, a quasiform to
the antiform) or changes how the value is looked up:

| Type | Written | Means |
|---|---|---|
| `QUOTED!` | `'a` | the value itself, not evaluated |
| `QUASIFORM!` | `~a~` | evaluates to the antiform (see below) |
| [`TIED!`](/docs/datatypes/tied/) | `$a` | the value bound to the current context, without the `$` |
| [`PINNED!`](/docs/datatypes/pinned/) | `@a` | the value itself, sigil kept, bound |
| [`METAFORM!`](/docs/datatypes/metaform/) | `^a` | get or set the variable with nothing converted |

The last three are the [sigil types](/docs/datatypes/sigils/).

```
>> type of first ['a]
== \~{quoted!}~\  ; antiform (datatype!)

>> type of first [@a]
== \~{pinned!}~\  ; antiform (datatype!)

>> type of first [$a]
== \~{tied!}~\  ; antiform (datatype!)
```

## Antiforms

Some fundamental types have an **antiform**: a variant of the value that
can't be put in a list, used to carry signals (such as "nothing", "splice
these", "this failed") in a way that ordinary data can't be mistaken for.
See [Antiforms](/docs/concepts/antiforms/) for how they work.

| Antiform | Of | Summary | Stable? |
|---|---|---|---|
| [`LOGIC!`](/docs/datatypes/logic/) | [`WORD!`](/docs/datatypes/word/) | either ~okay~, or ~null~ (the only "falsey" state) | yes |
| [`SPLICE!`](/docs/datatypes/splice/) | [`BLOCK!`](/docs/datatypes/block/) | fragment of multiple values without a surrounding container | yes |
| [`DATATYPE!`](/docs/datatypes/datatype/) | [`FENCE!`](/docs/datatypes/fence/) | the type of a value expressed as an antiform | yes |
| [`ACTION!`](/docs/datatypes/action/) | [`FRAME!`](/docs/datatypes/frame/) | will trigger function execution from words | yes |
| [`VOID!`](/docs/datatypes/void/) | [`BLANK!`](/docs/datatypes/blank/) | panics on WORD! access, multi-step evaluations discard | no |
| [`TRASH!`](/docs/datatypes/trash/) | [`TAG!`](/docs/datatypes/tag/) | panics on WORD! access, console does not display | no |
| [`PACK!`](/docs/datatypes/pack/) | [`GROUP!`](/docs/datatypes/group/) | multi-return that decays to first item, empty is HEAVY VOID | no |
| [`FAILURE!`](/docs/datatypes/failure/) | [`ERROR!`](/docs/datatypes/error/) | failure state that is escalated to a panic if not triaged | no |

## Type Constraints

Besides the exact types, there are *type constraint* functions that answer
whether a value belongs to a family.  They are what a function's spec uses
when it accepts more than one type:

```
>> any-string? "abc"
== \~okay~\  ; antiform (logic!)

>> any-list? first [(a)]
== \~okay~\  ; antiform (logic!)

>> any-number? 10%
== \~okay~\  ; antiform (logic!)
```

| Constraint | True of |
|---|---|
| `ANY-NUMBER?` | INTEGER!, DECIMAL!, PERCENT! |
| `ANY-SCALAR?` | the numbers, plus PAIR!, TIME!, and TUPLE! |
| `ANY-STRING?` | TEXT!, FILE!, TAG! |
| `ANY-UTF8?` | the strings, plus EMAIL!, RUNE!, and WORD! |
| `ANY-SERIES?` | the strings, BLOB!, and the lists |
| `ANY-LIST?` | BLOCK!, GROUP!, FENCE! |
| `ANY-SEQUENCE?` | TUPLE!, CHAIN!, PATH! |
| `ANY-CONTEXT?` | OBJECT!, MODULE!, ERROR!, PORT!, FRAME!, LET!, and now URL! |
| `ANY-BRANCH?` | what IF and friends accept as a branch: the lists, PATH!, and FRAME! |
| `ANY-INERT?` | types that evaluate to themselves |
| `ELEMENT?` | anything that can be put in a list (so, not an antiform) |
| `ANY-STABLE?` | anything that can be held in a variable (elements and stable antiforms) |
