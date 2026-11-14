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

```rebol
>> type of [a b c]
== \~{block!}~\  ; antiform (datatype!)

>> type of 1.5
== \~{decimal!}~\  ; antiform (datatype!)
```

The type is itself a value (a [DATATYPE!](/docs/datatypes/datatype/)),
so it can be compared, matched against, and used to make new values:

```rebol
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
| `INTEGER!` | 64 bit integer | `1` |
| `DECIMAL!` | 64bit floating point number (IEEE standard) | `1.5` |
| `PERCENT!` | special form of decimals (used mainly for layout) | `10%` |
| `PAIR!` | two dimensional point or size | `10x20` |
| `TIME!` | time of day or duration | `12:30` |
| `DATE!` | day, month, year, time of day, and timezone | `1-Jan-2026` |

### Strings and other UTF-8 values

| Type | Summary | Example |
|---|---|---|
| `TEXT!` | text string series of characters | `"abc"` |
| `FILE!` | file name or path | `%file.txt` |
| `TAG!` | markup string (HTML or XML) | `<div>` |
| `URL!` | uniform resource locator or identifier | `http://example.com` |
| `EMAIL!` | email address | `user@example.com` |
| `RUNE!` | immutable codepoint or codepoint sequence | `#a` |
| `BLOB!` | series of bytes | `#{DECAFBAD}` |

### Lists

| Type | Summary | Example |
|---|---|---|
| `BLOCK!` | list of elements that blocks evaluation unless EVAL is used | `[a b]` |
| `GROUP!` | list that evaluates expressions as an isolated group | `(a b)` |
| `FENCE!` | list of elements that are used in construction via MAKE | `{a b}` |

### Sequences

| Type | Summary | Example |
|---|---|---|
| `TUPLE!` | member selection with inert bias | `a.b` |
| `CHAIN!` | refinement and function call dialect | `a:b` |
| `PATH!` | member or refinement selection with execution bias | `a/b` |

### Words

| Type | Summary | Example |
|---|---|---|
| `WORD!` | evaluates a variable or action | `a` |

Setting and getting are spelled with CHAIN!s: `a:` is the word with an
empty slot after it, and `:a` with one before.

### Contexts

| Type | Summary | Example |
|---|---|---|
| `OBJECT!` | context of names with values | `make object! [a: 1]` |
| `MODULE!` | loadable context of code and data | |
| `ERROR!` | context with id, arguments, and stack origin | `make error! "oops"` |
| `PORT!` | external series, an I/O channel | |
| `FRAME!` | arguments and locals of a function state | `make frame! append/` |
| `LET!` | context containing a single variable | |

### Other

| Type | Summary | Example |
|---|---|---|
| `BLANK!` | evaluation separator, no rendering (shows in lists via commas) | the `,` in `[a, b]` |
| `MAP!` | name-value pairs (hash associative) | `make map! [a 1]` |
| `BITSET!` | set of bit flags | `make bitset! "abc"` |
| `HANDLE!` | arbitrary internal object or value | |
| `OPAQUE!` | extension cell which uses its type information slot for data | |
| `VARARGS!` | evaluator position for variable numbers of arguments | |
| `PARAMETER!` | function parameter description | |

## Decorated Forms

Any element can be decorated, which gives it a different type while it
keeps the same payload.  Evaluating a decorated value undoes one level of
decoration (a quoted value evaluates to the plain value, a quasiform to
the antiform) or changes how the value is looked up:

| Type | Written | Means |
|---|---|---|
| `QUOTED!` | `'a` | the value itself, not evaluated |
| `QUASIFORM!` | `~a~` | evaluates to the antiform (see below) |
| `METAFORM!` | `^a` | get the value without decaying it |
| `PINNED!` | `@a` | the value itself, keeping its binding |
| `TIED!` | `$a` | the value itself, bound to the current context |

```rebol
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
See [Antiforms](/docs/datatypes/antiforms/) for how they work.

| Antiform | Of | Summary | Stable? |
|---|---|---|---|
| [`LOGIC!`](/docs/datatypes/logic/) | `WORD!` | either ~okay~, or ~null~ (the only "falsey" state) | yes |
| [`SPLICE!`](/docs/datatypes/splice/) | `BLOCK!` | fragment of multiple values without a surrounding container | yes |
| [`DATATYPE!`](/docs/datatypes/datatype/) | `FENCE!` | the type of a value expressed as an antiform | yes |
| [`ACTION!`](/docs/datatypes/action/) | `FRAME!` | will trigger function execution from words | yes |
| [`VOID!`](/docs/datatypes/void/) | `BLANK!` | panics on WORD! access, multi-step evaluations discard | no |
| [`TRASH!`](/docs/datatypes/trash/) | `TAG!` | panics on WORD! access, console does not display | no |
| [`PACK!`](/docs/datatypes/pack/) | `GROUP!` | multi-return that decays to first item, empty is HEAVY VOID | no |
| [`FAILURE!`](/docs/datatypes/failure/) | `ERROR!` | failure state that is escalated to a panic if not triaged | no |

## Type Constraints

Besides the exact types, there are *type constraint* functions that answer
whether a value belongs to a family.  They are what a function's spec uses
when it accepts more than one type:

```rebol
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
| `ANY-UTF8?` | the strings, plus URL!, EMAIL!, RUNE!, and WORD! |
| `ANY-SERIES?` | the strings, BLOB!, and the lists |
| `ANY-LIST?` | BLOCK!, GROUP!, FENCE! |
| `ANY-SEQUENCE?` | TUPLE!, CHAIN!, PATH! |
| `ANY-CONTEXT?` | OBJECT!, MODULE!, ERROR!, PORT!, FRAME!, LET! |
| `ANY-BRANCH?` | what IF and friends accept as a branch: the lists, PATH!, and FRAME! |
| `ANY-INERT?` | types that evaluate to themselves |
| `ELEMENT?` | anything that can be put in a list (so, not an antiform) |
| `ANY-STABLE?` | anything that can be held in a variable (elements and stable antiforms) |
