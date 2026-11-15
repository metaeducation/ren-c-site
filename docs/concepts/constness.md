---
layout: default
title: Constness
parent: Concepts
grand_parent: Documentation
nav_order: 2
permalink: /docs/concepts/constness/
---

# Constness

Revolt code is made of the same lists that programs work with as data.
That's powerful, but it creates an old trap: a function or loop whose body
contains a literal series can modify that series.  Because there's only
one copy of the body, the change shows up the next time the body runs.

Revolt's answer is a *const bit* on each value that refers to a series.
A const reference can be used to read the series, but not to change it.
The evaluator gives you const references to the literal source of function
and loop bodies, so modifying them is an error unless you say you mean it.

## The Old Gotcha

In historical Rebol, this function remembered every value it had ever been
called with:

<!-- doctest: skip -->
```
accumulate: func [x] [
    data: []
    append data x
]

>> accumulate 10
== [10]

>> accumulate 20
== [10 20]  ; the [] in the body isn't empty anymore
```

The `[]` isn't a fresh block on each call.  It's one block, sitting in the
function's body, and APPEND modifies it.  The usual fix was to write
`copy []`, and forgetting the COPY was one of the most common bugs in
Rebol code.

It's worse when a function hands out a literal from its body, because
then the *caller* can modify the function:

<!-- doctest: positive-test -->
```
symbol-to-string: func [s] [
    return switch s [
        '+ ["plus"]
        '- ["minus"]
    ]
]
```

In historical Rebol, a caller doing `append symbol-to-string '+ "-good"`
would change what the function returned from then on.

## The Wave of Constness

In Revolt, functions and loops make their bodies const as they run, and
anything the evaluator pulls out of a const body is const too.  So that
caller gets an error instead:

<!-- doctest: negative-test match="const-value" -->
```
p: symbol-to-string '+
insert p "double-"
```

Loops do the same:

<!-- doctest: negative-test match="const-value" -->
```
repeat 2 [append [] <item>]
```

This is called the *wave of constness*: it starts at a body that might run
more than once and spreads to everything evaluated from it, including
nested blocks and groups.

It only applies to the body's literal source.  A value fetched through a
WORD! carries whatever constness it had when it was stored, so this is
fine:

<!-- doctest: positive-test -->
```
block: []
repeat 2 [append block <item>]
assert [block = [<item> <item>]]
```

## Asking For Mutability

When you really do want to modify a literal, say so with
[MUTABLE](/docs/natives/mutable/):

```
>> repeat 2 [append mutable [] <legal>]
== [<legal> <legal>]
```

That's sometimes called a *magic static*: storage that lives in the body,
and lasts from one run to the next.  Revolt doesn't forbid the technique, it
just won't let it happen by accident.

A caller can use MUTABLE on a const value it was handed, too:

<!-- doctest: positive-test -->
```
p: mutable symbol-to-string '+
insert p "you-" append p "-asked-for-it"
assert ["you-plus-asked-for-it" = symbol-to-string '+]
```

## COPY Makes Mutable Copies, Shallowly

A COPY of a const series is a new series, and the reference to it is
mutable.  But a shallow COPY doesn't copy the series inside it, so those
are the same series as before, still viewed as const:

<!-- doctest: positive-test -->
```
data: ~
repeat 1 [data: copy [a [b [c]]]]

append data <success>
assert [data = [a [b [c]] <success>]]

e: sys.util/recover [append data.2 <oops>]
assert [e.id = 'const-value]
```

COPY:DEEP copies the nested series as well, so they're all mutable:

<!-- doctest: positive-test -->
```
data: ~
repeat 1 [data: copy:deep [a [b [c]]]]
append data <success>
append data.2 <success>
append data.2.2 <success>
assert [data = [a [b [c <success>] <success>] <success>]]
```

## EVAL Doesn't Add Constness

EVAL runs a block once, so it doesn't make it const.  If the block you
give it is mutable, it runs as mutable:

<!-- doctest: positive-test -->
```
d: ~
block: [append d: [] <item>]
assert [[<item> <item>] = repeat 2 [eval block]]
```

But EVAL doesn't take constness *away*, either.  If the block is const,
because you made it const or because it was written out in a loop body,
it runs as const:

<!-- doctest: negative-test match="const-value" -->
```
d: ~
repeat 2 [eval [append d: [] <item>]]
```

### COMPOSE Into a Loop

Watch out when you COMPOSE a series into code that loops.  Once it's been
composed in, the series is part of the loop body's literal source, and the
loop makes it const, even if you made it mutable:

<!-- doctest: negative-test match="const-value" -->
```
block: mutable []
eval compose:deep [repeat 2 [append (block) <illegal>]]
```

Either put MUTABLE in the composed code, or quote the group so the series
is fetched as a literal value instead of evaluated from the body:

<!-- doctest: positive-test -->
```
block: []
eval compose:deep [repeat 2 [append mutable (block) <legal>]]
assert [block = [<legal> <legal>]]

block: []
eval compose:deep [repeat 2 [append '(block) <legal>]]
assert [block = [<legal> <legal>]]
```

## CONST Is Not a Lock

The const bit is on the *reference*, not the series.  Another reference to
the same series can still change it, and the const reference sees the
change.  When you need a series that nobody can change, lock the series
itself:

| | What it affects | Undo with |
|---|---|---|
| [CONST](/docs/natives/const/) | One reference to a series | [MUTABLE](/docs/natives/mutable/) |
| PROTECT | The series (every reference to it), or a variable | UNPROTECT |
| FREEZE | The series, permanently (`:deep` for nested series) | Can't |
| [FINAL](/docs/natives/final/) | A variable, plus a deep FREEZE of its value | UNPROTECT (variable only) |

MUTABLE can't get around a lock:

<!-- doctest: negative-test match="series-frozen" -->
```
frozen: freeze [a b c]
append mutable frozen 'd
```

Why not just lock all source code, as some languages do?  Because it rules
out techniques like the magic static, and the const bit already catches the
bugs that locking would.  Source loaded by TRANSCODE isn't locked by
default.

## Enforced by the C++ Compiler

A protection feature is only as good as its checks.  R3-Alpha's PROTECT was
buggy for exactly this reason: every native that modified a series had to
remember to test the protection bit first, and some didn't.  Each missed
test was a hole, and nothing pointed out where the holes were.

Revolt doesn't rely on remembering.  Inside the interpreter, the function
that gets a series out of a value returns a C `const` pointer:

```c
INLINE const Binary* Cell_Binary(const Cell* cell) { ... }
```

The routines that modify a series won't accept a `const` pointer.  The
only way to get a non-const one is through an accessor that does the
runtime check, and panics if the value is const or the series is locked:

```c
#define Cell_Binary_Ensure_Mutable(cell) \
    m_cast(Binary*, Cell_Binary(Ensure_Mutable(cell)))
```

So a native that modifies a series without checking doesn't have a bug
waiting to be found at runtime.  It doesn't compile.

This needs a trick, because a helper like "get the item at index N" has to
give back a `const` pointer when it's given a `const` series, and a mutable
one otherwise.  C has no overloading to express that.  Revolt's sources are
written so they build as either C or C++: the C build is permissive, and
the C++ build makes the output's constness follow the input's.  Building
with a C++ compiler is what finds the missing checks, and the continuous
integration builds do that on every commit.

The same accessors check PROTECT and FREEZE, so those features are covered
by the compiler too.

See [Using C's `const` Keyword to Power CONST](https://revolt.metaeducation.com/forum/t/using-c-s-const-keyword-to-power-const/2501)
for the details.

## Constness and Purity

CONST and MUTABLE are about whether code may change a series it was handed.
[Purity](/docs/concepts/purity/) is about a different question: what state
outside its arguments a function may *see*.  They work together.  A pure
function can modify its arguments only if they aren't const, and
[MUTABLE](/docs/natives/mutable/) is IMPURE, so pure code can't take
constness off.

## History

* [Value vs. Series Modification Bit: CONST and MUTABLE](https://revolt.metaeducation.com/forum/t/value-vs-series-modification-bit-const-and-mutable/976)
  (forum, 2018 to 2025).  The original design, and later changes.
