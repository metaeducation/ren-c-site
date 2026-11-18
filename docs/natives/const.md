---
layout: native
title: CONST
parent: Natives
permalink: /docs/natives/const/
native: const
spec: |
  "Return value whose access level doesn't allow mutation to its content"
  return: [element?]
  value "Argument to change access to (can be locked or not)"
      [element?]
---

CONST gives back a *read-only view* of a value.  The series it points to
isn't changed in any way.  Only the reference that CONST hands back is
marked, so other references to the same series can still modify it.

```
>> data: [a b c]
== [a b c]

>> data-readonly: const data
== [a b c]
```

Modifying through the const reference is an error:

<!-- doctest: negative-test match="const-value" -->
```
append data-readonly <readonly>
```

But the original reference still works, and the const view sees the change,
because there's only one series:

```
>> append data <readwrite>
== [a b c <readwrite>]

>> data-readonly
== [a b c <readwrite>]
```

CONST is a property of the *value*, not the variable.  `data-readonly` can
still be assigned something else.  To lock the variable, see
[FINAL](/docs/natives/final/).

## Where You'll Meet CONST Without Asking For It

You won't often call CONST yourself.  The evaluator applies it for you to
the literal source of function bodies and loop bodies, so code like this
can't quietly modify itself on each pass:

<!-- doctest: negative-test match="const-value" -->
```
repeat 2 [append [] <item>]
```

This "wave of constness", and how to get around it with
[MUTABLE](/docs/natives/mutable/), is explained in
[Constness](/docs/concepts/constness/).

## No Native Can Forget to Check

Natives can't modify a series through a const value by accident.  The
interpreter's own C++ build refuses to compile code that gets write access
to a series without doing the const check.  See
[Enforced by the C++ Compiler](/docs/concepts/constness/#enforced-by-the-c-compiler).

## CONST Is Pure

CONST is a [PURE](/docs/natives/pure/) native: adding protection doesn't
depend on, or change, anything outside its argument.  Its opposite,
[MUTABLE](/docs/natives/mutable/), is IMPURE, because it takes protection
away.

## See Also

* [MUTABLE](/docs/natives/mutable/) -- the opposite of CONST
* [FINAL](/docs/natives/final/) -- lock a variable, and deeply freeze its value
* [Constness](/docs/concepts/constness/) -- the full story
* [Value vs. Series Modification Bit: CONST and MUTABLE](https://revolt.metaeducation.com/forum/t/value-vs-series-modification-bit-const-and-mutable/976)
  (forum)
