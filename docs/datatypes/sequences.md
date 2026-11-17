---
layout: default
title: Sequence Types
parent: Datatypes
grand_parent: Documentation
nav_order: 3
has_children: true
permalink: /docs/datatypes/sequences/
---

# Sequence Types

A **sequence** is two or more elements joined by a separator.  There are
three, one for each separator:

| Type | Written | Used for |
|---|---|---|
| [`TUPLE!`](/docs/datatypes/tuple/) | `a.b` | picking a member, such as a field of an object |
| [`CHAIN!`](/docs/datatypes/chain/) | `a:b` | setting and getting (`a:`, `:a`), and refinements (`append:dup`) |
| [`PATH!`](/docs/datatypes/path/) | `a/b` | running a function, or a member that is one |

They can be mixed.  Slashes bind loosest and dots tightest, so
`foo/bar.baz:mumble` is a PATH! whose second element is a CHAIN!, which
starts with a TUPLE!:

```
>> type of 'foo/bar.baz:mumble
== \~{path!}~\  ; antiform (datatype!)

>> type of second 'foo/bar.baz:mumble
== \~{chain!}~\  ; antiform (datatype!)
```

## Sequences Are Immutable

[Lists](/docs/datatypes/lists/) are series: they have a position, and can
be changed in place.  Sequences are neither.  That one decision fixes a
family of old problems.

In historical Rebol, a PATH! was a series like a block.  So it had a
position, and moving it could leave something that looked like a word, or
like nothing at all:

```text
rebol2>> p: to path! [a b]
== a/b

rebol2>> next p
== b                ; a PATH!, though it looks like a WORD!

rebol2>> next next p
==                  ; still a PATH!, with nothing to show
```

And because anything could be put into one, a path could hold a path, and
two different paths would print the same:

```text
rebol2>> left: make path! [x x]  clear left
rebol2>> append left 'a/b  append left 'c

rebol2>> right: make path! [x x]  clear right
rebol2>> append right 'a  append right 'b/c

rebol2>> left
== a/b/c
rebol2>> right
== a/b/c            ; but FIRST LEFT is a/b, and FIRST RIGHT is a
```

In Revolt, sequences aren't series.  There's no position to move, and
nothing that modifies one:

<!-- doctest: positive-test -->
```
p: 'a/b/c

assert [not any-series? p]
assert [3 = length of p]
assert ['b = pick p 2]
```

<!-- doctest: negative-test match="expect-arg" -->
```
next 'a/b/c
```

<!-- doctest: negative-test match="expect-arg" -->
```
append 'a/b/c 'd
```

Since a sequence can only be made by a few routes (the scanner, AS, and
the like), each can enforce the rules, and once made, nothing can break
them:

* **A sequence has at least two elements.**  There's no one-element or
  empty path.

* **Sequences nest in one order only.**  A path can hold chains and
  tuples, and a chain can hold tuples, but never the other way around,
  and never one of its own kind.  So `a/b/c` can only mean one thing.

* **Only some types can be elements.**  Words, integers, groups, blocks,
  text, tags, runes, and their quasiforms and sigil forms.  A BLOB!, for
  instance, can't be.

<!-- doctest: positive-test -->
```
assert [path? as path! [a b:c]]
assert [chain? as chain! [a b.c]]
```

<!-- doctest: negative-test match="sequence-too-short" -->
```
as path! [a]
```

<!-- doctest: negative-test match="bad-sequence-item" -->
```
as path! [a b/c]
```

<!-- doctest: negative-test match="bad-sequence-item" -->
```
as tuple! [a b:c]
```

When dots or slashes could be read as part of a TAG! or as separators,
the tag wins, so a tag can hold a file name like `<../foo/bar.txt>`.  The
separators on their own (`/`, `//`, `.`, `..`, `:`) are words.

{: .note }
> Almost nothing used paths as general containers anyway.  Compared to
> blocks and groups they were bad at it: never long, and with no line
> breaks between their items.  So taking that role away from them cost
> very little.

## Working With One

Elements can be picked by position, or walked with FOR-EACH:

<!-- doctest: positive-test -->
```
seen: copy []
for-each 'item 'a/b/c [append seen item]
assert [seen = [a b c]]
```

To restructure one, turn it into a block, change the block, and turn it
back.  AS gives a read-only view of the elements, so COPY it before
changing it:

<!-- doctest: positive-test -->
```
b: copy as block! 'a/b/c
append b 'd
assert ['a/b/c/d = as path! b]
```

{: .note }
> TO BLOCK! doesn't do this.  It makes a block *holding* the sequence, so
> `to block! 'a/b/c` is `[a/b/c]`.  AS is the conversion that takes the
> elements out.

## Blanks

A sequence can start or end with its separator: `/a`, `a/`, `.a`, `a:`.
The empty position is a [BLANK!](/docs/datatypes/blank/), the same value
a comma is in a block:

```
>> as block! '/a
== [, a]

>> as block! 'a/
== [a,]
```

That's how `a:` (set) and `:a` (get) are chains, and how `append/` (the
function itself, not a call to it) is a path.  A blank can be at both ends
at once (`/a/`), and the start of a file path in the home directory,
`~/projects/`, is a path beginning with the quasiform `~`.

### In the Middle

Blanks can be in the middle of a sequence too.  Two separators in a row
have a blank between them:

```
>> as block! 'a//b
== [a, b]

>> as block! 'a..b
== [a, b]
```

That makes something familiar into an ordinary path.
`http://example.com` is a PATH! of three elements: the CHAIN! `http:`, a
blank, and the TUPLE! `example.com`:

```
>> type of 'http://example.com
== \~{path!}~\  ; antiform (datatype!)

>> as block! 'http://example.com
== [http:, example.com]
```

(To write a URL as a value, use a [TAG!](/docs/datatypes/tag/), as in
`<http://example.com>`.  See [URL!](/docs/datatypes/url/).)

Chains can have them as well, so even this is a CHAIN!:

<!-- doctest: positive-test -->
```
assert [chain? transcode:one ":a:::<b>::"]
```

{: .warning }
> Blanks in the middle are new, and the rules are still settling.  Two
> separators at the *end* aren't allowed (`a//` is an error), and how a
> run of separators splits into blanks and words like `/` or `::` is
> being worked out.

## See Also

* [List Types](/docs/datatypes/lists/) -- the mutable containers
* [BLANK!](/docs/datatypes/blank/) -- what fills an empty position
* `tests/scanner/sequence.scan.test.r` in the interpreter's source --
  how each spelling scans
