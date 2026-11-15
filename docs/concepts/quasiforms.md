---
layout: default
title: Quasiforms
parent: Concepts
grand_parent: Documentation
nav_order: 2
permalink: /docs/concepts/quasiforms/
---

# Quasiforms

A **quasiform** is a value written with tildes around it: `~foo~`,
`~[a b]~`, `~<tag>~`.  It's an ordinary value that can be put in a list,
and it has its own type:

```
>> first [~foo~ ~[a b]~]
== ~foo~

>> type of first [~foo~]
== \~{quasiform!}~\  ; antiform (datatype!)
```

Quasiforms have two jobs:

1. **They're how an [antiform](/docs/concepts/antiforms/) is written down.**
   An antiform can't go in a list, so wherever one needs to be stored, or
   shown, its quasiform stands in for it.

2. **They're values in their own right.**  A quasiform in a block is just
   data, and a dialect can give it any meaning it likes.

Antiforms and quasiforms together were once called *isotopes*, a name
you'll still meet on the forum.

## Making Them

QUASI puts the tildes on, and UNQUASI takes them off:

```
>> quasi 'foo
== ~foo~

>> quasi [a b]
== ~[a b]~

>> unquasi first [~foo~]
== foo
```

The types that have quasiforms are exactly the eight that have
[antiforms](/docs/concepts/antiforms/): WORD!, BLOCK!, GROUP!, FENCE!,
TAG!, BLANK!, FRAME! and ERROR!.  (The quasiform of BLANK!, the comma, is
written as a tilde by itself: `~`.)  Other types, like numbers and strings,
don't have them:

<!-- doctest: negative-test match="non-isotopic-type" -->
```
quasi 10
```

NOQUASI is the forgiving version of UNQUASI: it takes the tildes off a
quasiform, and passes anything else through unchanged.

```
>> noquasi first [~foo~]
== foo

>> noquasi 'foo
== foo
```

## Evaluating Them

Evaluating a quasiform gives its antiform:

```
>> ~[a b]~
== \~[a b]~\  ; antiform (splice!)

>> ~null~
== \~null~\  ; antiform (logic!)
```

That's why the console can show an antiform as its quasiform between
backslashes: type the part between the backslashes, and you get the
antiform back.

Not every quasiform has a legal antiform.  Any word can be a quasiform, but
the only words that can be antiforms are `~okay~` and `~null~`:

<!-- doctest: negative-test match="illegal-anti-word" -->
```
~foo~
```

So if you want a quasiform *as a value* in code that's evaluated, quote it,
just as you'd quote a word to keep it from being looked up:

```
>> '~foo~
== ~foo~
```

## The Lifting Ladder

Quoting and quasiforms stack up in a fixed order.  From the bottom:

```text
    antiform        ~null~ (evaluated)     can't go in a list
    quasiform       ~null~                 a value in a list
    quoted          '~null~                one quote
    quoted twice    ''~null~               two quotes, and so on
```

A plain value has the same ladder without the bottom two rungs:

```text
    plain           foo
    quoted          'foo
    quoted twice    ''foo
```

[LIFT](/docs/concepts/antiforms/#quasiforms-lift-and-unlift) moves any
value up one rung, and UNLIFT moves it down one.  LIFT of an antiform is
its quasiform, and LIFT of anything else adds a quote:

```
>> lift null
== ~null~

>> lift lift null
== '~null~

>> lift 'foo
== 'foo

>> lift lift 'foo
== ''foo
```

### You Can Quote a Quasiform, but Not Quasi a Quote

The quasi rung is always directly above the antiform, and there is only one
of it.  So a quasiform can be quoted any number of times:

```
>> quote first [~foo~]
== '~foo~
```

but a quoted value can't be made quasi, because the result would have a
quasi rung *above* a quote:

<!-- doctest: negative-test match="expect-arg" -->
```
quasi first ['foo]
```

The ladder has no gaps and no branches.  That's what makes LIFT and UNLIFT
exact: whatever you lift, unlifting gives back exactly what you started
with, antiform or not.

## Quasiforms in Dialects

Quasiforms don't need to have anything to do with antiforms.  Like any
other value that appears in a block, they are material for
[dialects](https://revolt.metaeducation.com/forum/c/domains/dialects-dsls/18)
to give meaning to.  The tildes give a word a different look, which a dialect
can use to set it apart from the plain words around it.

The interpreter's own test files do this.  A plain group is a test that
should come out true, and a quasiform word followed by `!!` says which error
the next group should raise:

```text
(2 = 8 / 4)
~zero-divide~ !! (1 / 0)
```

Here's a small version of that dialect:

<!-- doctest: positive-test -->
```
/run-tests: func [
    "Run tests: (code) must be true, ~error-id~ !! (code) must raise that error"
    return: [integer!]
    tests [block!]
][
    let count: 0
    let pos: tests
    while [not tail? pos] [
        either quasiform? pos.1 [
            assert ['!! = pos.2]
            let e: sys.util/recover as block! pos.3
            assert [e.id = unquasi pos.1]
            pos: skip pos 3
        ][
            assert [eval pos.1]
            pos: next pos
        ]
        count: count + 1
    ]
    return count
]

assert [3 = run-tests [
    (2 = 8 / 4)
    ~zero-divide~ !! (1 / 0)
    ([a b] = reduce ['a 'b])
]]
```

The `~zero-divide~` is never evaluated, so it doesn't matter that it has no
antiform.  The dialect looks at it with QUASIFORM? and takes the word out
with UNQUASI.

When a quasiform has to be compared or matched in evaluated code, quote it
there too.  SWITCH evaluates its cases, so:

```
>> switch first [~zero-divide~] ['~zero-divide~ [<matched>]]
== <matched>

>> '~foo~ = first [~foo~]
== \~okay~\  ; antiform (logic!)
```

## Binding

A quasiform word is still a word, and it carries a
[binding](/docs/concepts/binding/) like any other.
Taking the tildes off gives back a word that can be looked up, so a dialect
can use `~x~` to mean something special about the *variable* `x`:

<!-- doctest: positive-test -->
```
x: 10
o: make object! [x: 20]
assert [10 = get unquasi first [~x~]]
assert [20 = get unquasi first bind o [~x~]]
```

### It Doesn't Survive the Trip to an Antiform

Antiforms carry no binding of their own.  So *evaluating* a quasiform drops
its binding, and lifting the antiform back gives a quasiform without one.
The things inside a list keep whatever bindings they had themselves, but
the list's binding, which is what the words in source code are looked up
through, is gone:

<!-- doctest: positive-test -->
```
x: 10
assert [11 = eval unquasi first [~[x + 1]~]]  ; from a block: bound

lifted: lift ~[x + 1]~  ; evaluated to a splice, then lifted back
e: sys.util/recover [eval unquasi lifted]
assert [e.id = 'no-binding]
```

So a dialect that relies on binding should take quasiforms from the block
it was given, not evaluate them.

## See Also

* [Antiforms](/docs/concepts/antiforms/) -- what quasiforms stand in for
* [A Justification of Generalized Isotopes](https://revolt.metaeducation.com/forum/t/a-justification-of-generalized-isotopes/1918)
  (forum, 2022, kept current)
