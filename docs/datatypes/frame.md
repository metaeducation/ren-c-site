---
layout: datatype
title: FRAME!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 24
permalink: /docs/datatypes/frame/
datatype: frame!
summary: 'arguments and locals of a function state'
antiform: action!
---

The arguments and locals of one call of a function.  `make frame! append/` gives an unfilled frame for APPEND; fill it in and EVAL it to make the call.

Its antiform is [ACTION!](/docs/datatypes/action/): a frame that runs when a word holding it is evaluated.

A frame is a function call as a value.  You can build one, look at it,
change it, copy it, and run it later.  Every tool Revolt has for making
one function out of another (SPECIALIZE, ADAPT, ENCLOSE, AUGMENT, APPLY)
is built on frames, and so can your own.

## Making a Call by Hand

MAKE FRAME! gives a frame with a field for each argument:

```
>> f: make frame! append/
== &[frame! [
    series: ~null~  ; hole
    value: ~null~  ; hole
    part: ~null~  ; hole
    dup: ~null~  ; hole
    line: ~null~  ; hole
]]
```

Fill in what you want, and EVAL runs it:

<!-- doctest: positive-test -->
```
f: make frame! append/
f.series: copy [a b c]
f.value: <d>

assert [[a b c <d>] = eval f]
```

The refinements `part`, `dup` and `line` were left alone, and the call
went ahead without them.  The required arguments can't be left out:

<!-- doctest: negative-test match="no-arg" -->
```
f: make frame! append/
f.series: copy [a b c]
eval f
```

EVAL doesn't use the frame up.  It can be run again, and the fields can be
read afterwards:

<!-- doctest: positive-test -->
```
f: make frame! append/
f.series: copy [a b c]
f.value: <d>

eval f
eval f
assert [f.series = [a b c <d> <d>]]
```

EVAL-FREE is the faster form for a frame you're finished with.  It runs
the call in the frame's own memory, so the frame can't be used again:

<!-- doctest: positive-test -->
```
f: make frame! append/
f.series: copy [a b c]
f.value: <d>

assert [[a b c <d>] = eval-free f]

e: sys.util/recover [f.series]
assert [e.id = 'expired-frame]
```

## Holes

A field that hasn't been filled is a **hole**.  If you read one, you get
NULL:

```
>> f: make frame! append/

>> f.value
== \~null~\  ; antiform (logic!)
```

But a hole isn't a NULL.  HOLE? tells them apart, and so does the
function when it runs.  Assigning NULL fills the hole, with a NULL:

<!-- doctest: positive-test -->
```
f: make frame! append/
assert [hole? $f.value]

f.value: null
assert [not hole? $f.value]
```

<!-- doctest: negative-test match="expect-arg" -->
```
f: make frame! append/
f.series: copy [a b c]
f.value: null
eval f
```

APPEND doesn't accept NULL as its value, so that call is an error about
the *type* of the argument.  A hole in the same place is an error about
the argument being *missing*.

A hole reads as NULL so that ordinary code does the sensible thing with
one.  `f.dup: default [2]` fills the field if nobody else has, and
`if f.part [...]` is false for a refinement that wasn't given.

### Why a Hole Has to Be Something Else

It took several attempts to find out what an unfilled field should be.
Each earlier answer was a value, and any value has the same problem: it's
something a caller might want to pass on purpose.

| Unfilled fields were | The problem |
|---|---|
| NULL | Functions that reject NULL couldn't tell "not given" from "given NULL".  The error for a missing argument was a type error. |
| a void or trash value | `specialize set/ [value: ~]` should make a function that unsets a variable.  It did nothing instead, because `~` meant "not specialized". |
| the parameter itself, as an antiform | A type test like INTEGER? could then be handed "a parameter" as its argument, and had to treat it specially. |

The answer in use now is that a hole isn't a value at all.  It's a state
of the *slot*, one level beneath values, which the interpreter's source
calls "bedrock".  No expression can evaluate to it, so no function can be
passed one, and nothing a caller legitimately wants to say is taken away.
What you see when you read the slot (NULL) is how that state chooses to
show itself.

So the specialization from the table now does what it says:

<!-- doctest: positive-test -->
```
my-unset: specialize set/ [value: ~]

counter: 10
my-unset $counter
assert [unset? $counter]
```

{: .warning }
> Bedrock states are recent, and holes aren't the only use being made of
> them.  The details here are likely to change.

### Fields Hold Arguments As They Are

A field holds exactly what the function will receive.  For a parameter
that accepts unstable values, that includes packs and failures, and those
are written and read with the
[`^` sigil](/docs/datatypes/metaform/#frames-hold-values-as-they-are) like
any other variable.  Code that only handles ordinary values needs no
sigil.

## Frames and Actions

A function is a frame too.  What makes `append` *run* when the evaluator
reaches the word is that the variable holds the frame as an
[antiform](/docs/concepts/isotopes/), an ACTION!.  RUNS turns a frame
into an action, and UNRUN goes the other way:

<!-- doctest: positive-test -->
```
f: make frame! append/
f.series: copy [a b c]
f.value: <d>

add-d: runs f
assert [[a b c <d>] = add-d]
```

When a frame that still has holes is run as an action, the holes are
filled from the call.  That's the difference between EVAL and running:
EVAL treats a hole in a required argument as an error, and running
treats it as a place to put the next argument.

## Building Functions From Frames

Each of these takes a function and gives back another.  None of them
makes a new body in the usual sense.  They arrange for a frame to be
filled or adjusted on the way to the original.

**SPECIALIZE** fills some fields ahead of time.  Those arguments
disappear from the new function:

<!-- doctest: positive-test -->
```
append-d: specialize append/ [value: <d>]

assert [[a <d>] = append-d copy [a]]
assert [[series part dup line] = words of make frame! append-d/]
```

**ADAPT** runs some code first, with the arguments in scope, and then
goes on to the original:

<!-- doctest: positive-test -->
```
append-twice: adapt append/ [value: reduce [value value]]

assert [[a [1 1]] = append-twice copy [a] 1]
```

**ENCLOSE** hands the filled frame to a function of yours.  You decide
whether to run it, and what to do with the result:

<!-- doctest: positive-test -->
```
append-count: enclose append/ func [f] [
    let series: f.series
    eval f
    return length of series
]

assert [2 = append-count copy [a] <b>]
```

**AUGMENT** adds parameters, for an ADAPT or ENCLOSE around it to use:

<!-- doctest: positive-test -->
```
append-extra: augment append/ [extra [integer!]]

assert [[series value part dup line extra] = words of make frame! append-extra/]
```

**APPLY** builds and runs a frame in one step, from a block.  Arguments
can be given in order or by name:

```
>> apply append/ [copy [a b c] <d> dup: 2]
== [a b c <d> <d>]
```

These stack.  A specialization of an adaptation of an augmentation is one
frame, and its memory is reused by each layer in turn.  The usual way of
wrapping functions has each layer make a new call and copy the arguments
across.

## Views of a Frame

One frame can be shared by several layers, and each layer should see only
what belongs to it.  So a FRAME! value is a *view*: the same memory, seen
through the parameter list of one particular layer.  (The source calls
the view a "lens".)

From outside, a frame shows the function's arguments.  From inside the
running function, it shows the locals too.  Here `{private}` declares a
local, and the function returns its own frame:

<!-- doctest: positive-test -->
```
inside-view: func [return: [frame!] public {private}] [
    private: 304
    return binding of $public
]

outer: make frame! inside-view/
outer.public: 1020
assert [[public] = words of outer]

inner: eval copy outer
assert [inner.public = 1020]
assert [inner.private = 304]
```

The outside view can't reach the local:

<!-- doctest: negative-test match="bad-pick" -->
```
outer.private
```

That's what makes it safe for a wrapper to add a parameter whose name
happens to match something hidden inside the function it wraps.  Here
AUGMENT adds a `private` *argument* to a function that already has a
`private` *local*.  They share a frame, and they're different variables:

<!-- doctest: positive-test -->
```
prelude-view: null

wrapped: adapt (augment inside-view/ [:private [tag!]]) [
    prelude-view: binding of $private
]

outer: make frame! wrapped/
outer.public: 1020
outer.private: <different>

inner: eval outer

assert [prelude-view.private = <different>]  ; what the wrapper sees
assert [inner.private = 304]                 ; what the function sees
```

The author of the wrapper didn't need to know what locals the inner
function has, and the author of the inner function is free to rename
them.

### How a View Works

A frame's memory is one row of slots.  Next to it, each layer of a
composed function has a *parameter list*, which says what each slot is to
that layer: an argument, a local, or nothing it's allowed to see.  A
FRAME! value is the memory plus one of those lists, and field access goes
through the list.

That makes the layers cheap:

* **SPECIALIZE** needs only a new parameter list.  In it, the entry for a
  specialized argument holds the value itself, in the place where the
  argument's type information was.  So the argument is gone from the
  interface, and the value is ready to be copied in when a call starts.

* **AUGMENT** needs only a new parameter list too.  It adds slots on the
  end.  If a new name matches a hidden one from an inner layer, the old
  entry is marked sealed, and the name now leads to the new slot.

* **ADAPT** and **ENCLOSE** have code of their own to run, so they need
  more than a list.  While an ADAPT's prelude runs, the frame is seen
  through the list of the function being adapted.  That's why the prelude
  can use the arguments and can't touch the locals.

When the function at the bottom finally runs, its body sees the frame
through the function's own full list, with the locals and its RETURN.

{: .note }
> This is the simple account.  The implementation has more cases, for
> the sake of speed, and its author describes the full picture as hard to
> explain.

## See Also

* [ACTION!](/docs/datatypes/action/) -- the antiform
* [METAFORM!](/docs/datatypes/metaform/) -- `^` for fields holding unstable
  values
* [Definitionality](/docs/concepts/definitionality/) -- why wrappers
  compose
* [Understanding FRAME! Lensing](https://revolt.metaeducation.com/forum/t/understanding-frame-lensing/1645)
  (forum, 2021-2026)
* [Default Values and MAKE FRAME! (2024 Edition)](https://revolt.metaeducation.com/forum/t/default-values-and-make-frame-2024-edition/2347)
  (forum, 2024-2026; the first posts predate holes)
