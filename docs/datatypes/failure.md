---
layout: datatype
title: FAILURE!
parent: Antiforms
grand_parent: Datatypes
nav_order: 8
permalink: /docs/datatypes/failure/
datatype: failure!
antiform-of: error!
stable: false
summary: failure state that is escalated to a panic if not triaged
sample: 'fail "oops"'
---

A FAILURE! is an error being *returned*.  `FAIL` produces one from a
message or an ERROR! object, and many natives return one when given
something they can't handle:

```rebol
>> fail "oops"
** Failure: oops

>> 1 / 0
** Failure: attempt to divide by zero

>> pick [a b] 3
** Failure: cannot pick 3

>> failure? fail "oops"
== \~okay~\  ; antiform (logic!)
```

The console shows `** Failure:` for one of these, as against `** PANIC:`
for a `PANIC`, which stops execution outright and can't be returned:

```rebol
>> panic "boom"
** PANIC: boom
```

## Triage

A failure is unstable: it can't be stored, and it can't be ignored.  If
the code that receives one doesn't deal with it, it is escalated to a
panic.  So `THEN` won't run on it, and assigning it is an error:

```rebol
>> fail "oops" then [1]
** Failure: oops

>> x: fail "oops"
** Failure: oops
```

The ways to deal with one:

`TRY` turns a failure into `~null~`:

```rebol
>> try fail "oops"
== \~null~\  ; antiform (logic!)

>> try pick [a b] 3
== \~null~\  ; antiform (logic!)
```

`EXCEPT` runs a branch instead.  Given a function (in a group, since the
branch is taken literally), the function receives the ERROR!:

```rebol
>> fail "oops" except [<handled>]
== <handled>

>> fail "oops" except (lambda [e] [e.message])
== "oops"
```

`RESCUE` runs a block and gives back the ERROR! object of the first
failure in it, or `~null~` if there was none:

```rebol
>> e: rescue [1 / 0]

>> type of e
== \~{error!}~\  ; antiform (datatype!)

>> e.id
== zero-divide

>> rescue [1 + 1]
== \~null~\  ; antiform (logic!)
```

## ERROR! and FAILURE!

The ERROR! is the plain object: a context with an `id`, a `message`, and
where it came from.  It can be stored, inspected, and put in lists like
any other value.  The FAILURE! is that object in its antiform state, which
is what makes it demand attention:

```rebol
>> e: make error! "custom"

>> error? e
== \~okay~\  ; antiform (logic!)

>> e.message
== "custom"

>> fail e
** Failure: custom

>> type of unquasi lift fail e
== \~{error!}~\  ; antiform (datatype!)
```

## See Also

* [Antiforms](/docs/datatypes/antiforms/) -- the general mechanism, and
  the history of this one (it has been called RAISED!, and the plain
  object has been called WARNING!)
