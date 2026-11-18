---
layout: native
title: INFIX
parent: Natives
permalink: /docs/natives/infix/
native: infix
spec: |
  "For functions that gets 1st argument from left, e.g (+: infix add/)"
  return: [action! frame!]
  ^value [action! frame!]
  :off "Give back a non-infix version of the passed in function"
  :defer "Allow one full expression on the left to evaluate"
  :postpone "Allow arbitrary numbers of expressions on left to evaluate"
---

INFIX gives back a version of a function that gets its first argument from
the *left*, and runs in the same step as the expression there.

Giving the result a name is how the operators are made (`+: final infix
add/`).  After that, `add 1 2` can be written the other way around:

<!-- doctest: positive-test -->
```
plus: infix add/
assert [3 = (1 plus 2)]
```

What "infix" means, and how it affects the way an expression is evaluated,
is explained in [Infix](/docs/concepts/infix/).

## The Original Isn't Changed

INFIX returns a modified copy.  The function you gave it stays a prefix
function:

```
>> infix? add/
== \~null~\  ; antiform (logic!)

>> infix? infix add/
== \~okay~\  ; antiform (logic!)
```

## Modes

With no refinements, the function is **tight**: it runs as soon as the
value on its left is available.  `:defer` and `:postpone` give the two
modes that run later.

```
>> deferred: infix:defer lambda [a b] [reduce [a b]]

>> append [a] 1 + 2 deferred 10
== [a [3 10]]

>> postponed: infix:postpone lambda [a b] [reduce [a b]]

>> append [a] 1 + 2 postponed 10
== [[a 3] 10]
```

Where these matter is explained in
[The Modes](/docs/concepts/infix/#the-modes).  The standard
[THEN](/docs/natives/then/), [ELSE](/docs/natives/else/) and
[ALSO](/docs/natives/also/) are `infix:defer`.

## INFIX:OFF

`:off` turns it back around, and gives a prefix version of an infix
function:

```
>> infix? infix:off +/
== \~null~\  ; antiform (logic!)
```

Asking for `:off` together with `:defer` or `:postpone` is an error, as is
asking for both `:defer` and `:postpone`:

<!-- doctest: negative-test match="bad-refines" -->
```
infix:defer:postpone add/
```

## INFIX? Tells You

INFIX? asks if a function is infix of any mode:

```
>> infix? +/
== \~okay~\  ; antiform (logic!)

>> infix? then/
== \~okay~\  ; antiform (logic!)
```

Giving it something that's not a function is an error:

<!-- doctest: negative-test match="expect-arg" -->
```
infix? 10
```

## Not Just Two Parameters

An infix function can have any number of parameters.  With one, it's a
postfix function; with three, the second and third come from the right.

<!-- doctest: positive-test -->
```
twice: infix lambda [x] [x * 2]
assert [20 = (10 twice)]
```

See [Other Numbers of Parameters](/docs/concepts/infix/#other-numbers-of-parameters).

## See Also

* [Infix](/docs/concepts/infix/) -- the concept
* [THEN](/docs/natives/then/), [ELSE](/docs/natives/else/),
  [ALSO](/docs/natives/also/)
* [The Infix Covenant](https://revolt.metaeducation.com/forum/t/the-ren-c-infix-covenant/1023)
  (forum, 2019)
