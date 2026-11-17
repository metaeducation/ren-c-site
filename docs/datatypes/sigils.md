---
layout: default
title: Sigil Types
parent: Datatypes
grand_parent: Documentation
nav_order: 5
has_children: true
permalink: /docs/datatypes/sigils/
---

# Sigil Types

![The three sigils, labelled TIE, PIN and META](/assets/images/sigils-tie-pin-meta.webp)

A **sigil** is one of three marks that can go on the front of a value.
Each gives the value a type of its own:

| Sigil | Name | Type | In ordinary code |
|---|---|---|---|
| `$` | **TIE** | [`TIED!`](/docs/datatypes/tied/) | [binds](/docs/concepts/binding/) the value to where it's written |
| `@` | **PIN** | [`PINNED!`](/docs/datatypes/pinned/) | stays as it is (but bound) |
| `^` | **META** | [`METAFORM!`](/docs/datatypes/metaform/) | reads or writes a variable with nothing converted |

The names are meant to be easy to hold on to.  A `$` looks like a knot, and
it ties a word to a context.  A pin `@` holds a value in place, so it
comes through evaluation unchanged, apart from picking up a binding.  META is the one that deals with the
values an ordinary variable can't.

{: .note }
> The right column is what the *evaluator* does when it meets one.  A
> sigil is a part of the value, like the brackets of a block.  In a
> dialect of your own, `@name` and `$name` can mean whatever you want them
> to.  The evaluator's meanings are worth keeping in mind, since a reader
> will bring them along, but they aren't binding on you.

## What Can Have One

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

So there's one type per sigil, not one for each combination.  The value
underneath is the *heart*:

```
>> heart of '@[a b]
== \~{block!}~\  ; antiform (datatype!)

>> sigil of '@[a b]
== @

>> sigil of 'plain-word
== \~null~\  ; antiform (logic!)
```

A value has one sigil or none.  They don't stack.

## Adding and Removing

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

TIED?, PINNED? and METAFORM? test for each.  When the heart matters too,
a type check can name both:

```
>> match [@word!] '@foo
== @foo

>> match [@word!] 'foo
== \~null~\  ; antiform (logic!)
```

## Each Sigil Alone Is an Operator

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
[allowed to vanish](/docs/concepts/vanishing/#asking-for-vanishing).

## Compared to Quoting

A quote mark `'` is not a sigil.  Sigils are a fixed set of three, and a
value has at most one.  Quotes can be added to any value, any number of
times, on top of whatever sigil it has, and the evaluator removes one
each time:

```
>> '@foo
== @foo

>> type of first ['@foo]
== \~{quoted!}~\  ; antiform (datatype!)
```

## See Also

* [Binding](/docs/concepts/binding/) -- what `$` is for
* [Quasiforms](/docs/concepts/quasiforms/) -- the other decoration, `~`
* [New Names for ^FOO, @FOO, and $FOO](https://revolt.metaeducation.com/forum/t/new-names-for-foo-foo-and-foo/2447)
  (forum, 2025)
