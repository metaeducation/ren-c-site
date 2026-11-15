---
layout: native
title: ELSE
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/else/
native: else
spec: |
  "If LEFT is NULL or VOID!, return EVAL BRANCH, else return LEFT"
  return: [any-value?]
  ^left [<null> void! any-value?]
  @branch [any-branch?]
---

ELSE runs a branch if the expression on its left produced NULL or VOID!.
Otherwise it passes along what it got:

```
>> null else [<alternative>]
== <alternative>

>> 10 else [<alternative>]
== 10
```

Since a failed search gives NULL, and a false IF gives VOID!, this is the
usual way to say what happens otherwise:

```
>> find [a b c] 'z else [<missing>]
== <missing>

>> if null [10] else [20]
== 20

>> if ok [10] else [20]
== 10

>> any [1 = 2 3 = 4] else [<none-true>]
== <none-true>
```

## With THEN

THEN and ELSE together make a complete conditional.  Each runs for its own
case, and the one that doesn't run passes the value along:

```
>> if 1 = 1 [<a>] then [<x>] else [<y>]
== <x>

>> if 1 = 2 [<a>] then [<x>] else [<y>]
== <y>

>> all [1 = 1 null] then [<ok>] else [<no>]
== <no>
```

## A Function As the Branch

A function is called with the value from the left.  For ELSE that value is
normally a NULL or VOID!, so a function taking no arguments is the usual
choice:

```
>> null else (does [<alternative>])
== <alternative>
```

## Failures

A FAILURE! on the left also counts as "nothing" to ELSE, but an ordinary
branch can't quietly swallow one: the failure becomes a panic unless the
branch is a function that takes its argument as `^`.

<!-- doctest: negative-test match="oops" -->
```
(fail "oops") else [<handled>]
```

## It Is Deferred

Like [THEN](/docs/natives/then/), ELSE is `infix:defer`: it lets the
function call in progress on its left finish, and takes that call's result.
Here that call is the IF, with its condition and block:

```
>> if 3 = 1 + 2 [<yes>] else [<no>]
== <yes>
```

It waits for one call only, the innermost.  THEN's page shows what that
means after a chain of operators.

See [The Modes](/docs/concepts/infix/#the-modes).

## See Also

* [THEN](/docs/natives/then/)
* [ALSO](/docs/natives/also/)
* [INFIX](/docs/natives/infix/), [Infix](/docs/concepts/infix/)
