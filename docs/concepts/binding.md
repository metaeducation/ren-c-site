---
layout: default
title: Binding
parent: Concepts
grand_parent: Documentation
nav_order: 7
permalink: /docs/concepts/binding/
---

# Binding

When Revolt evaluates a word like `x`, it needs to know which variable
named `x` to use.  The connection between code and the context that gives
its words meaning is called **binding**.

Most of the time, this works as you'd expect: a function sees its arguments
and local variables, as well as definitions from outside it.  Binding
becomes especially important when code is treated as data.  A block can be
built in one place and evaluated in another.  Should an `x` in that block
mean the variable where the code was built, or one where it is used?

Revolt lets code carry a binding when that meaning is known, and leave
parts unbound when the meaning needs to be supplied later.

{: .warning }
> Binding is still being worked on.  The examples on this page show
> behavior that works today, but the operations and their names may change.

## A Variable, Not Its Value

A binding identifies where to find a variable, not a snapshot of its value.
Here `$x` gives us the word `x` bound in the current context.  GET looks
up the variable named by that word:

<!-- doctest: positive-test -->
```
x: 10
word: $x
assert [10 = get word]

x: 20
assert [20 = get word]
```

The word hasn't changed which variable it refers to, but the value in that
variable has changed.

## Source Starts Unbound

When text is read into values, its words start out unbound.  They aren't
attached to variables just because their spelling happens to match one.
Evaluating freshly loaded code fails, because nothing has said what its
words mean:

<!-- doctest: negative-test match="no-binding" -->
```
eval transcode "x + 1"
```

The standalone `$` binds a value to the context where the `$` is written:

<!-- doctest: positive-test -->
```
x: 10
assert [11 = eval $ transcode "x + 1"]
```

## Literals Get the Binding of Where They're Written

Code you write in a script or function was loaded too, so how does it
work?  When the evaluator reaches a block literal in running code, the
result is the block bound to the place it's written: the function call
it's in, any LETs above it, and the module around that.

<!-- doctest: positive-test -->
```
x: 10
code: [x + 1]
assert [11 = eval code]
```

A quoted literal is *not* evaluated, so it doesn't get that binding.  It
comes out the way it was loaded, unbound:

<!-- doctest: negative-test match="no-binding" -->
```
eval '[x + 1]
```

This is how a function body works without ever being rebound.  The `x` in
this body refers to the argument of each call, because the body is
evaluated in that call:

<!-- doctest: positive-test -->
```
twice: func [x] [return x + x]
assert [20 = twice 10]
assert [40 = twice 20]
```

A block written in the body is bound to the call too, so it keeps access
to that call's `x` after the function returns:

<!-- doctest: positive-test -->
```
make-adder: func [x] [return [x + 1]]
code: make-adder 10
assert [11 = eval code]
```

The next call returns a block that sees a different `x`:

<!-- doctest: positive-test -->
```
other-code: make-adder 20
assert [21 = eval other-code]
assert [11 = eval code]
```

LET counts as part of "where it's written".  A block after a LET sees the
variable it made:

<!-- doctest: positive-test -->
```
x: 10
code: eval [let x: 5, [x + 1]]
assert [6 = eval code]
```

## Lexical, Not Dynamic

A block's meaning comes from where it was *written*, not from where it ends
up being evaluated.  Here `run` has its own `x`, but the block it's given
was written outside, so it sees the outside `x`:

<!-- doctest: positive-test -->
```
x: 10
run: func [code] [let x: 99, return eval code]
assert [10 = run [x]]
```

An *unbound* block doesn't pick up the `x` inside `run` either.  It has no
meaning until someone gives it one:

<!-- doctest: negative-test match="no-binding" -->
```
run collect [keep 'x]
```

So there's no way for code to reach into the local variables of whatever
function happens to evaluate it.  That's the property programmers mean by
*lexical scope*, and it's what makes the code you read predictable.

## Binding at the Place Code Is Built

Code that's assembled, rather than written out, starts unbound like any
other data.  COLLECT builds this block out of quoted words:

<!-- doctest: negative-test match="no-binding" -->
```
eval collect [keep 'x keep '+ keep 'y]
```

The collected block has no binding to tell EVAL where to find its words.
EVAL doesn't automatically attach the context of its caller to an unbound
block.  Binding the block supplies a context for its words:

<!-- doctest: positive-test -->
```
x: 10
y: 20
code: $ collect [keep 'x keep '+ keep 'y]
assert [30 = eval code]
```

This doesn't mean every word inside the block has to be changed.  The
block carries a context that can be used as the evaluator goes through
its contents.

When the value is written directly in the code, `$` can be attached to it.
`$x` is a bound word, and `$[x + y]` is a bound block.  Values written with
a `$` are called **tied**.

## Mixing Meanings

Suppose a function makes a fragment containing `x`.  A fragment left
unbound can take its meaning from the code it's added to.  A fragment
bound in the function can keep referring to that function call:

<!-- doctest: positive-test -->
```
make-unbound: func [x] [return '(x)]
make-bound: func [x] [return $ '(x)]

x: 1020
assert [1021 = eval append [1 +] make-unbound 304]
assert [305 = eval append [1 +] make-bound 304]
```

In the first result, `x` gets its meaning from the surrounding block and
refers to `1020`.  In the second, the fragment carries the binding from
the call to MAKE-BOUND, so `x` refers to `304`.  Both fragments look like
`(x)`; their binding is not shown in that spelling.

The choice can be made for an individual word, not just a whole block.
Here COMPOSE puts the `x` bound outside the function into its body.  The
other `x`, added when the function runs, gets the function call's context:

<!-- doctest: positive-test -->
```
x: 1000
sub-from-1000: func [x] (compose:deep [
    let code: copy [subtract ($x)]
    append code to word! "x"
    return eval code
])

assert [980 = sub-from-1000 20]
assert [970 = sub-from-1000 30]
```

The first `x` in the generated code refers to the outside variable (1000);
the second refers to the argument.  They have the same spelling but
different bindings.  This control is useful when assembling code from
pieces that come from different places, including code generated by
dialects.

## Quoting Neither Adds Nor Removes Binding

A quoted literal is unbound because it was never evaluated, so it never
got a binding.  Quoting something that *is* bound leaves the binding
alone, and it's still there when the quote comes off:

<!-- doctest: positive-test -->
```
x: 10
quoted: quote $x
assert [10 = get unquote quoted]
```

## Why Start Unbound?

Historical Rebol applied bindings deeply when code was loaded.  A word
that was meant to be a function local could already be bound to a global
with the same spelling.  The function then had to replace that binding.
But if the code was assembled from other pieces, an existing binding might
have been intentional.  Overriding it could change what the assembled code
meant; leaving it alone could prevent a local from working.

Starting unbound avoids putting those incidental bindings on the source in
the first place.  Code can receive the context it needs as it is used,
while deliberately bound pieces can retain their meaning.  This doesn't
make every combination of code sensible: the pieces still have to be
designed to work together.

## See Also

* [QUASIFORM!: Binding](/docs/datatypes/quasiform/#binding) -- how binding
  interacts with quasiforms and antiforms
* [Purity](/docs/concepts/purity/) -- how pure code uses binding to tell
  local variables from outside state
* [Revolt Binding in a Nutshell](https://revolt.metaeducation.com/forum/t/ren-c-binding-in-a-nutshell/2614)
  (forum, 2025)
* [Joe Marshall on Rebol 1.0 vs. Rebol 2.0 Binding](https://revolt.metaeducation.com/forum/t/joe-marshall-on-rebol-1-0-vs-rebol-2-0-binding/2074)
  (forum, historical discussion)
