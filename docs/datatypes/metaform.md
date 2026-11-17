---
layout: datatype
title: METAFORM!
parent: Decorated Types
grand_parent: Datatypes
nav_order: 5
permalink: /docs/datatypes/metaform/
datatype: metaform!
sigil: ^
---

A value with the META sigil, `^`, on the front: `^x`, `^x:`, `^a.b`.
See [Sigils](/docs/datatypes/decorated/#sigils) for what all three sigils have
in common.

This is the sigil with the most behind it.  In ordinary code, `^` means
**nothing is converted**.

## Plain Variables Convert, `^` Variables Don't

A plain variable holds a single, ordinary value.  Assigning to one
converts whatever arrives.  A [pack](/docs/datatypes/pack/) decays to its
first item.  A [failure](/docs/datatypes/failure/) isn't stored at all,
and becomes a panic.  A [void](/docs/concepts/vanishing/) leaves the
variable unset.

`^` turns the conversion off, in both directions.  `^name:` stores exactly
what it's given.  `^name` fetches exactly what's there:

```
>> ^var: pack [1 + 2, 3 + 4]
== \~('3 '7)~\  ; antiform (pack!)

>> ^var
== \~('3 '7)~\  ; antiform (pack!)
```

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

## Meta Parameters

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

### Types Decide What Gets Through

A `^` parameter with types listed receives an unstable value only if its
type is listed.  If it isn't, the value decays, and the result is checked
again.  So a pack reaches the function as a pack only where PACK! is
asked for:

<!-- doctest: positive-test -->
```
takes-integer: func [^x [integer!]] [return ^x]
assert [1 = takes-integer pack [1 2]]       ; decayed to its first item

takes-either: func [^x [integer! pack!]] [return ^x]
^r: takes-either pack [1 2]
assert [pack? ^r]                           ; kept
```

A failure can't decay to anything, so if FAILURE! isn't listed, it
becomes a panic before the function runs:

<!-- doctest: negative-test match="oops" -->
```
takes-integer fail "oops"
```

### Multiple Assignment

The `^` works inside the block of a multiple assignment too:

<!-- doctest: positive-test -->
```
[^inner count]: pack [pack [1 2] 3]
assert [pack? ^inner]
assert [count = 3]
```

## Frames Hold Values As They Are

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

## How It Got This Way

This is the third design, and older writing describes the first two.

**First: `^` meant "lifted".**  For years no variable could hold an
unstable antiform, with no exceptions.  A `^` parameter worked by
receiving its argument [lifted](/docs/concepts/isotopes/#the-lifting-ladder):
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

## Making One

META adds the sigil and UNMETA takes it off:

```
>> meta 'a.b
== ^a.b

>> unmeta '^a.b
== a.b
```

Written alone, `^` evaluates what follows and passes the result on
untouched:

```
>> ^ pack [1 2]
== \~('1 '2)~\  ; antiform (pack!)
```

## See Also

* [Decorated Types](/docs/datatypes/decorated/) -- TIE, PIN and META, and the other decorations
* [PACK!](/docs/datatypes/pack/), [FAILURE!](/docs/datatypes/failure/) and
  [Vanishing](/docs/concepts/vanishing/) -- what `^` lets through
* [Isotopes](/docs/concepts/isotopes/) -- lifting, which `^` used to
  mean
* [Solving the Pox of the (^)... LIFT the Universe?](https://revolt.metaeducation.com/forum/t/solving-the-pox-of-the-lift-the-universe/2477)
  (forum, 2025)
* [Impedance Matching LIFT the Universe With Baseline](https://revolt.metaeducation.com/forum/t/impedance-matching-lift-the-universe-with-baseline/2483)
  (forum, 2025)
