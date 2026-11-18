---
layout: default
title: Decorated Types
parent: Datatypes
nav_order: 5
has_children: true
permalink: /docs/datatypes/decorated/
---

# Decorated Types

A **decoration** is a mark added to a value that gives it a different
type, while the value underneath stays the same.  There are five:

| Decoration | Written | Type | In ordinary code |
|---|---|---|---|
| quote | `'a` | [`QUOTED!`](/docs/datatypes/quoted/) | evaluates to the value with one quote fewer |
| quasi | `~a~` | [`QUASIFORM!`](/docs/datatypes/quasiform/) | evaluates to the [antiform](/docs/datatypes/antiforms/) |
| TIE sigil | `$a` | [`TIED!`](/docs/datatypes/tied/) | [binds](/docs/concepts/binding/) the value to where it's written |
| PIN sigil | `@a` | [`PINNED!`](/docs/datatypes/pinned/) | stays as it is (but bound) |
| META sigil | `^a` | [`METAFORM!`](/docs/datatypes/metaform/) | reads or writes a variable with nothing converted |

The undecorated value is the *heart*, and HEART OF gives its type:

```
>> type of first ['[a b]]
== \~{quoted!}~\  ; antiform (datatype!)

>> heart of first ['[a b]]
== \~{block!}~\  ; antiform (datatype!)

>> heart of '@[a b]
== \~{block!}~\  ; antiform (datatype!)
```

So there's one type per decoration, not one for each combination.  In
historical Rebol a quoted word was a LIT-WORD! and a quoted path a
LIT-PATH!, and a quoted block couldn't be written at all.  Here `'a`,
`'a/b` and `'[a b]` are all QUOTED!, and only HEART OF tells them apart.

{: .note }
> The right column of the table is what the *evaluator* does with each
> one.  A decoration is a part of the value, like the brackets of a
> block.  In a dialect of your own, `@name`, `$name` and `~name~` can mean
> whatever you want them to.  The evaluator's meanings are worth keeping
> in mind, since a reader will bring them along, but they aren't binding
> on you.

## How They Stack

Decorations go on in a fixed order, from the inside out:

```text
    heart       foo
    sigil       $foo         at most one: $, @ or ^
    quasi       ~$foo~       at most one
    quotes      '~$foo~      any number
```

Each layer is optional, but they can only be added in that order.  So
quoting can go on top of anything:

```
>> quote first [~$foo~]
== '~$foo~
```

and a sigiled word can be made quasi:

```
>> quasi '$foo
== ~$foo~
```

But nothing can go *under* a decoration that's already there.  A quoted
value can't be made quasi, or be given a sigil, and a quasiform can't be
given a sigil:

<!-- doctest: negative-test match="expect-arg" -->
```
quasi first ['foo]
```

<!-- doctest: negative-test match="Sigil" -->
```
tie first ['foo]
```

<!-- doctest: negative-test match="Sigil" -->
```
pin first [~foo~]
```

The reason for the order is the [lifting
ladder](/docs/concepts/isotopes/#the-lifting-ladder).  Quotes are the
rungs LIFT adds, and quasi is the one rung between them and the antiform.
If either could appear lower down, LIFT and UNLIFT couldn't undo each
other exactly.  Sigils are part of what's being lifted, so they go
underneath.

Only some types can be quasi at all (see
[QUASIFORM!](/docs/datatypes/quasiform/#making-them)).  Sequences can't:
in `~foo~/bar` the tildes belong to
[the first element](/docs/datatypes/sequences/#tildes-belong-to-the-elements),
not the path.

A quasiform with a sigil, like `~$foo~`, is a legal value, and a dialect
can use it.  But it has no antiform, so evaluating it is an error:

<!-- doctest: negative-test match="sigils cannot become antiforms" -->
```
~$foo~
```

A type check can name the decorations along with the heart:

```
>> match ['word!] first ['foo]
== 'foo

>> match [~word!~] first [~foo~]
== ~foo~

>> match [@word!] '@foo
== @foo
```

## Quotes and Quasiforms

These two are the *isotopic* decorations: together with antiforms they
make up the lifting ladder, and LIFT and UNLIFT move a value along it.
The big picture is on the [Isotopes](/docs/concepts/isotopes/) concept
page.  The type pages cover the details:

* [QUOTED!](/docs/datatypes/quoted/) -- QUOTE, UNQUOTE, and how quoting
  keeps code from being evaluated
* [QUASIFORM!](/docs/datatypes/quasiform/) -- QUASI, UNQUASI, and
  quasiforms in dialects

## Sigils

![The three sigils, labelled TIE, PIN and META](/assets/images/sigils-tie-pin-meta.webp)

A **sigil** is one of three marks that can go on the front of a value:
`$` (TIE), `@` (PIN) and `^` (META).

The names are meant to be easy to hold on to.  A `$` looks like a knot,
and it ties a word to a context.  A pin `@` holds a value in place, so it
comes through evaluation unchanged, apart from picking up a binding.
META is the one that deals with the values an ordinary variable can't.

### What Can Have One

A sigil isn't only for words.  It goes on blocks, groups, tuples, and
other values too:

```
>> type of '$x
== \~{tied!}~\  ; antiform (datatype!)

>> type of '@[a b]
== \~{pinned!}~\  ; antiform (datatype!)

>> type of '^a.b
== \~{metaform!}~\  ; antiform (datatype!)
```

SIGIL OF says which one a value has:

```
>> sigil of '@[a b]
== @

>> sigil of 'plain-word
== \~null~\  ; antiform (logic!)
```

A value has one sigil or none.  They don't stack.

### Adding and Removing

TIE, PIN and META add a sigil.  UNTIE, UNPIN and UNMETA take that one
off, and PLAIN takes off whichever is there:

```
>> pin 'x
== @x

>> tie '[a b]
== $[a b]

>> meta 'a.b
== ^a.b

>> unpin '@x
== x

>> plain '$[a b]
== [a b]
```

{: .note }
> TIE the function only adds the `$`.  It doesn't bind anything.  Binding
> is what the *evaluator* does when it reaches a tied value.  The two are
> easy to confuse, because "tie" is the name of the mark and also a
> description of what the mark is for.

TIED?, PINNED? and METAFORM? test for each.

### Each Sigil Alone Is an Operator

Written by itself with a space after it, a sigil acts on the value that
follows:

| | Does |
|---|---|
| `$ value` | evaluates what follows, and binds the result here |
| `@ value` | takes what follows literally, without evaluating it |
| `^ value` | evaluates what follows, and passes the result on untouched |

```
>> @ foo
== foo

>> ^ pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)
```

`^` here is the IDENTITY function, which is also how a void is
[allowed to vanish](/docs/datatypes/void/#asking-for-vanishing).

## See Also

* [Isotopes](/docs/concepts/isotopes/) -- antiforms, quasiforms and
  quoting, and the lifting ladder
* [Binding](/docs/concepts/binding/) -- what `$` is for
* [New Names for ^FOO, @FOO, and $FOO](https://revolt.metaeducation.com/forum/t/new-names-for-foo-foo-and-foo/2447)
  (forum, 2025)
