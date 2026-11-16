---
layout: default
title: Sigils
parent: Concepts
grand_parent: Documentation
nav_order: 13
permalink: /docs/concepts/sigils/
---

# Sigils

A **sigil** is one of three marks that can go on the front of a value:

| Sigil | Name | Type of the result | In ordinary code |
|---|---|---|---|
| `$` | **TIE** | TIED! | [binds](/docs/concepts/binding/) the value to where it's written |
| `@` | **PIN** | PINNED! | stays as it is |
| `^` | **META** | METAFORM! | reads or writes a variable with nothing converted |

![The three sigils, labelled TIE, PIN and META](/assets/images/sigils-tie-pin-meta.webp)

The names are meant to be easy to hold on to.  A `$` looks like a knot, and
it ties a word to a context.  A pin `@` holds a value in place, so it
comes through evaluation unchanged.  META is the one that deals with the
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

## PIN: `@`
{: #pin }

A pinned value evaluates to itself, sigil included:

```
>> @foo
== @foo

>> @[a b]
== @[a b]

>> reduce [1 + 2 @(1 + 2)]
== [3 @(1 + 2)]
```

That makes it a way to hand something to a function with a mark on it
that says "take this as it is".  Several built-in functions read it that
way.  ANY and ALL treat a pinned block as values to test, not expressions
to run.  JOIN doesn't evaluate one:

```
>> any [1 + 2]
== 3

>> any @[1 + 2]
== 1

>> join text! @[1 + 1]
== "1+1"
```

In a function's parameter list, `@name` means the argument is taken
literally from the call:

<!-- doctest: positive-test -->
```
name-of: func [@what] [return what]

assert ['foo = name-of foo]
assert ['(1 + 2) = name-of (1 + 2)]
```

{: .warning }
> What `@word` does in the evaluator is likely to change.  The idea being
> explored is that `@iter` would give the current item of an iterator, as
> the word AT would, since `@` is read "at".  Nothing about that is
> decided.

## TIE: `$`
{: #tie }

Code starts out unbound.  A tied value gets the binding of the place
where it's evaluated, and loses the sigil:

```
>> x: 10
== 10

>> $x
== x

>> get $x
== 10
```

The plain quoted word `'x` wouldn't work there, because it would still be
unbound when GET received it.  [Binding](/docs/concepts/binding/) covers
this, and why it's needed.

## META: `^`
{: #meta }

This is the sigil with the most behind it.

A plain variable holds a single, ordinary value.  Assigning to one
converts whatever arrives.  A [pack](/docs/concepts/packs/) decays to its
first item.  A [failure](/docs/concepts/failure/) isn't stored at all,
and becomes a panic.  A [void](/docs/concepts/vanishing/) leaves the
variable unset.

`^` turns the conversion off, in both directions.  `^name:` stores exactly
what it's given.  `^name` fetches exactly what's there.

<!-- doctest: positive-test -->
```
both: func [] [return pack [1 2]]

first-only: both
assert [first-only = 1]         ; decayed

^whole: both
[a b]: ^whole                   ; still a pack
assert [[1 2] = reduce [a b]]
```

Once a variable holds something unstable, a plain fetch of it is refused.
The plain word is the gate:

<!-- doctest: negative-test match="unstable-non-meta" -->
```
whole
```

It works for a failure too.  (The TRY is there because the assignment
passes the failure along as its result, and something has to handle
that.)

<!-- doctest: positive-test -->
```
try ^problem: fail "oops"
assert [failure? ^problem]
```

And for a void:

<!-- doctest: positive-test -->
```
^nothing: comment "hi"
assert [void? ^nothing]
```

When a variable holds an ordinary value, `^name` and `name` give the same
thing.  The exception is a function: `^name` fetches it without calling
it.

### Meta Parameters

The same gate is on function arguments.  A plain parameter decays a pack,
and won't accept a failure or a void.  A `^` parameter receives whatever
the caller's expression produced:

<!-- doctest: positive-test -->
```
describe: func [^value] [
    if failure? ^value [return <failure>]
    if pack? ^value [return <pack>]
    if void? ^value [return <void>]
    return <ordinary>
]

assert [<failure> = describe fail "oops"]
assert [<pack> = describe pack [1 2]]
assert [<void> = describe comment "hi"]
assert [<ordinary> = describe 1 + 2]
```

This is how TRY, EXCEPT, THEN and ELSE can be ordinary functions.  They
take their input through a `^` parameter, and so they see the failure or
the heavy null that a plain parameter would never be given.

The `^` works inside the block of a multiple assignment too:

<!-- doctest: positive-test -->
```
[^inner count]: pack [pack [1 2] 3]
assert [pack? ^inner]
assert [count = 3]
```

### Frames Hold Values As They Are

A [FRAME!](/docs/datatypes/frame/) is a function call that hasn't run
yet: an object with a field for each argument.  Its fields hold arguments
exactly as the function would receive them.  You reach an unstable one
the same way as with any variable, by putting `^` on the access:

<!-- doctest: positive-test -->
```
takes-plain: func [x] [return x]
takes-meta: func [^x] [let [a b]: ^x, return reduce [a b]]

f: make frame! takes-plain/
^f.x: pack [1 2]
assert [1 = eval f]             ; the plain parameter decayed it

g: make frame! takes-meta/
^g.x: pack [1 2]
assert [[1 2] = eval g]         ; the meta parameter got the pack
```

The code that filled in the frame was the same for both.  It didn't have
to know which kind of parameter it was filling.  And code that only deals
in ordinary values needs no `^` at all:

<!-- doctest: positive-test -->
```
double-first: enclose add/ func [f] [
    f.value1: f.value1 * 2
    return eval f
]

assert [25 = double-first 10 5]
```

### How It Got This Way

This is the third design, and older writing describes the first two.

**First: `^` meant "lifted".**  For years no variable could hold an
unstable antiform, with no exceptions.  A `^` parameter worked by
receiving its argument [lifted](/docs/concepts/quasiforms/#the-lifting-ladder):
a pack arrived as a quasiform, an ordinary value arrived with a quote on
it, and the function body had to UNLIFT it.  That meant a frame's fields
were lifted for `^` parameters and not for plain ones.  Anything that
built or adjusted a frame had to know which was which, and changing a
parameter from one kind to the other broke every wrapper around the
function.

**Second: lift everything.**  The fix proposed in 2025 was called "lift
the universe".  Every field of every frame would be lifted, always, so
that a frame had one format whatever the parameters were.  That was
consistent, but then *every* access to a frame field needed a `^`, and
the simple wrapper above came out as:

```text
f.^value1: f.^value1 * 2
```

A mark that has to be on everything says nothing.  It was called the
"pox", and it showed the design was wrong.

**Third: store things as they are.**  The way out was to give up the old
rule.  A variable *can* hold an unstable antiform.  It's the plain
assignment and the plain fetch that won't deal with one.  `^` stopped
meaning "lifted" and started meaning "not converted".  Frames hold the
real values, ordinary code has no marks on it, and the `^` appears only
where something unusual is being handled.

So the statement "an unstable antiform can't be stored in a variable",
which is all over the forum and was all over this site, is now a
statement about plain variables.  The truth is narrower: it can't get in
or out without a `^`.

{: .warning }
> This is the newest part of the design, and several things about it are
> open: whether storing a failure should need more than a `^`, how loops
> like FOR-EACH should hand unstable values to a `^` variable, and
> whether META is still the right name for a sigil that now means
> "as is".

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
* [Packs](/docs/concepts/packs/), [Failure](/docs/concepts/failure/) and
  [Vanishing](/docs/concepts/vanishing/) -- what `^` lets through
* [Quasiforms](/docs/concepts/quasiforms/) -- lifting, which `^` used to
  mean
* [New Names for ^FOO, @FOO, and $FOO](https://revolt.metaeducation.com/forum/t/new-names-for-foo-foo-and-foo/2447)
  (forum, 2025)
* [Solving the Pox of the (^)... LIFT the Universe?](https://revolt.metaeducation.com/forum/t/solving-the-pox-of-the-lift-the-universe/2477)
  (forum, 2025)
* [Impedance Matching LIFT the Universe With Baseline](https://revolt.metaeducation.com/forum/t/impedance-matching-lift-the-universe-with-baseline/2483)
  (forum, 2025)
* [Iterator Framework](https://revolt.metaeducation.com/forum/t/rgchriss-iterator-framework-in-oldes-rebol3/2564)
  (forum, 2025-2026; where `@` for iterators is discussed)
