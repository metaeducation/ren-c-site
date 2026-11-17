---
layout: datatype
title: TRASH!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 6
permalink: /docs/datatypes/trash/
datatype: trash!
antiform-of: tag!
stable: false
summary: panics on WORD! access, console does not display
sample: "~<unused>~"
---

A TRASH! is a value that is not meant to be used, carrying a note that
says why.  It is the antiform of a TAG!, so the note is the tag's text:

```
>> ~<deprecated>~
== \~<deprecated>~\  ; antiform (trash!)

>> trash? ~<deprecated>~
== \~okay~\  ; antiform (logic!)
```

That sounds modest.  But a value that *refuses to be used, and says
why*, turns out to replace a lot of comments, stub functions and
conventions.  It's the sleeper hit of the antiforms.

## An Unset Variable That Explains Itself

Setting a variable to [VOID!](/docs/datatypes/void/) unsets it, and
reading it tells you only that it's unset:

<!-- doctest: negative-test match="unstable-non-meta" -->
```
state: ~
state
```

Set it to a trash instead, and reading it tells you *why*:

<!-- doctest: negative-test match="INITIALIZE-STATE not called yet" -->
```
state: ~<INITIALIZE-STATE not called yet>~
state
```

A trashed variable counts as **vacant**, the same as a void or null one:
it's waiting for a value.  VACANT? asks that of a variable, and VACANCY?
asks it of a value:

<!-- doctest: positive-test -->
```
state: ~<INITIALIZE-STATE not called yet>~
assert [vacant? $state]
assert [vacancy? ~<INITIALIZE-STATE not called yet>~]

assert [vacancy? null]
assert [not vacancy? 10]
```

DEFAULT fills in a vacant variable, and leaves any other alone:

<!-- doctest: positive-test -->
```
state: ~<INITIALIZE-STATE not called yet>~
state: default [10 + 20]
assert [state = 30]

state: default [40 + 50]
assert [state = 30]
```

### Better Than a Comment

A comment explains a placeholder to someone reading the source.  A trash
explains it to whoever runs into it, at the moment they do.  Compare:

```text
; !!! UPARSE is not available in SYS because it is higher level.  We hack it
; up so that when %uparse.r runs it pokes itself into sys.util/parse
;
parse: ~
```

with:

```text
parse: ~<higher-level %uparse.r hasn't set SYS.UTIL/PARSE yet>~
```

The information is the same.  The second one shows up in the error
message, which is where it's needed.

## Better Than a Stub Function

The traditional way to make a name that mustn't be used is a function
that fails when called:

<!-- doctest: positive-test -->
```
add-sym: does [panic "Symbol table finalized, can't ADD-SYM now"]
```

That has two problems.  First, **the name still looks like a function.**
Code that fetches it without calling it, as `add-sym/` does, gets a
perfectly good function back, and carries on until something much later
goes wrong:

<!-- doctest: positive-test -->
```
assert [action? add-sym/]
```

Second, **the stub has to match the real function's interface.**  If the
real ADD-SYM had a `:relax` refinement, a call to `add-sym:relax` gets an
error about the refinement, not your message:

<!-- doctest: negative-test match="bad-parameter" -->
```
add-sym:relax "foo"
```

A trash has neither problem:

<!-- doctest: negative-test match="Symbol table finalized" -->
```
add-sym: ~<Symbol table finalized, can't ADD-SYM now>~
add-sym "foo"
```

<!-- doctest: negative-test match="must retrieve an action" -->
```
add-sym/
```

<!-- doctest: negative-test match="did not evaluate to an ACTION" -->
```
add-sym:relax "foo"
```

There's nothing to keep in step, and the error is reported where the
name was used, rather than inside a stub.  (The errors for a slash or a
refinement don't quote the trash's note yet.)

The interpreter uses this for definitional words like RETURN* and
CONTINUE* in places where no function or loop provides them:

```text
return*: ~<RETURN* used when no function generator is providing it>~
continue*: ~<CONTINUE* used when no loop is providing it>~
```

{: .note }
> A [FAILURE!](/docs/datatypes/failure/) stored in a `^` variable can
> do some of the same job (reading it plainly panics).  But it has to be
> assigned with `^` and explicitly ignored, and it's a heavier thing to
> keep around.  TRASH! is the lightweight "don't use this" value.

## Labels in Code

An evaluation step that produces a *literal* trash and moves on is
allowed.  It doesn't count as a value being thrown away, the way
`1 + 2 10` does, because a trash was never a value anyone wanted.  So a
trash can label what follows it:

<!-- doctest: positive-test -->
```
make-person: func [name address] [return reduce [name address]]

person: make-person (~<name>~ "Bob") (~<address>~ "12 Main St")
assert [person = ["Bob" "12 Main St"]]
```

Unlike a comment, the label is part of the code: it moves with the
argument, and a dialect could even check it.

It has to be the literal.  A trash that comes from a variable is an error
like any other read of it, and a trash *after* a value would throw that
value away:

<!-- doctest: negative-test match="discarded-value" -->
```
(1 + 2 ~<sum>~ 10)
```

Nor does it vanish the way a [VOID!](/docs/datatypes/void/) from COMMENT
does.  If a trash is the last thing in an expression, it's the result:

```
>> 1 + 2 ~<note>~
** PANIC: Pure evaluation product discarded: 3
```

## Results Nobody Should Use

Functions that are run for their effect return a trash naming
themselves, so that using their "result" by mistake is caught:

```
>> print "hi"
hi
== \~<print>~\  ; antiform (trash!)
```

The console doesn't show a trash result, so in practice you just see
`hi`.  (The listings on this site show it, so you can see what came
back.)

## Getting at One Deliberately

A trashed variable is set, not unset, and the trash can be got at
deliberately with `GET` or a `^` access:

```
>> t: ~<deprecated>~
== \~<deprecated>~\  ; antiform (trash!)

>> unset? $t
== \~null~\  ; antiform (logic!)

>> trash? get $t
== \~okay~\  ; antiform (logic!)

>> lift get $t
== ~<deprecated>~
```

## Unstable

A trash can't be put in a list, and can't be decayed to an ordinary
value, so it can't take part in an expression that wants one:

```
>> all [1 ~<x>~ 2]
** PANIC: Cannot decay TRASH! to a stable value

>> type of ~<x>~
** PANIC: Cannot decay TRASH! to a stable value
```

## See Also

* [VOID!](/docs/datatypes/void/) -- "no value", for when there is nothing
  to say about why
* [TAG!](/docs/datatypes/tag/) -- what the note is made of
* [Isotopes](/docs/concepts/isotopes/) -- the general mechanism, and
  the history of this one (it has been the antiform of RUNE! as well)
* [Labeled TRASH! (forum)](https://revolt.metaeducation.com/forum/t/2278)
  -- where the uses on this page were worked out.  It was first called a
  "tripwire".
