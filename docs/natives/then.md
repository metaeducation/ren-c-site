---
layout: native
title: THEN
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/then/
native: then
spec: |
  "If LEFT is NULL or VOID!, return it, otherwise return EVAL BRANCH"
  return: [any-value?]
  ^left [<null> void! any-value?]
  @branch [any-branch?]
---

THEN runs a branch if the expression on its left produced something.  If it
produced NULL or VOID!, that is passed along and the branch doesn't run.

```
>> find [a b c] 'b then [<found>]
== <found>

>> find [a b c] 'z then [<found>]
== \~null~\  ; antiform (logic!)
```

An IF whose condition is false gives VOID!, so THEN works to run something
after an IF that ran:

```
>> if ok [10] then [20]
== 20
```

## A Function As the Branch

If the branch is a function, it's called with the value from the left:

```
>> find [a b c] 'b then (pos -> [index of pos])
== 2

>> 10 then (x -> [x * 2]) then (y -> [y + 1])
== 21
```

## It Is Deferred

THEN is `infix:defer`: it lets the function call in progress on its left
finish, and takes that call's result, not just the call's last argument.
That's what lets it go after things like ALL, ANY, CASE and IF:

```
>> all [1 = 1 2 = 2] then [<both>]
== <both>

>> case [1 = 2 [<a>] 2 = 2 [<b>]] then [<ok>]
== <ok>
```

It waits for *one* call, the innermost.  After a chain of operators, that's
only the last operator:

```
>> 3 = 1 + 2 then [<yes>]
== \~null~\  ; antiform (logic!)
```

THEN took the result of the `+`, so that compared 3 to `<yes>`.  Use a
group to say what THEN applies to:

```
>> (3 = 1 + 2) then [<yes>]
== <yes>
```

See [The Modes](/docs/concepts/infix/#the-modes).

## Failures Pass Through

A FAILURE! on the left isn't NULL or VOID!, but the branch doesn't run for
it either.  The failure comes out of THEN as it went in, to be handled
further along.

## See Also

* [ELSE](/docs/natives/else/) -- the other way around: runs for NULL or VOID!
* [ALSO](/docs/natives/also/) -- runs the branch, but keeps the left value
* THENCE -- the same as THEN, but not infix: the branch comes first, as in
  `thence [<x>] 10`
* [INFIX](/docs/natives/infix/), [Infix](/docs/concepts/infix/)
