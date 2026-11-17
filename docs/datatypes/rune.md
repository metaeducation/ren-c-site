---
layout: datatype
title: RUNE!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 17
permalink: /docs/datatypes/rune/
datatype: rune!
summary: 'immutable codepoint or codepoint sequence'
---

A rune is an immutable bit of text, used for character literals.  It
takes the place of two historical Rebol types: CHAR! and ISSUE!.

Most runes are written with a leading `#`.  Picking a character out of a
string gives one:

```
>> first "abc"
== #a

>> append "abc" #d
== "abcd"
```

The name comes from other languages.  In Go a `rune` is a Unicode
codepoint, and in Rust's `runestr` crate it's a "user-perceived
character".

## More Than One Character

Like the old ISSUE!, a rune can hold more than one codepoint:

```
>> length of #abcd
== 4
```

A rune that holds a delimiter, or a space among other characters, is
written in quotes:

```
>> third "[x]"
== #"]"
```

<!-- doctest: positive-test -->
```
assert [7 = length of #"abc def"]
assert [#"abc def" = to rune! "abc def"]
```

`#]` isn't allowed as a spelling, since `[a b #]]` would be confusing to
read, and it would rule out giving `#(...)` or `#[...]` meanings of
their own later.

## Two Spellings With No `#`

Two runes are written specially, because they're the characters you can't
see.

**`_` is the space character.**  A run of underscores is that many
spaces:

<!-- doctest: positive-test -->
```
assert [rune? _]
assert [" " = to text! _]
assert [_ = second "a b"]
assert [_ = space]

assert ["    " = as text! ____]
```

**`#` alone is newline.**  `##` is two newlines, and so on.  A literal
hash mark is `#"#"`:

<!-- doctest: positive-test -->
```
assert [# = newline]
assert ["^/^/" = as text! ##]
assert ["#" = as text! #"#"]
```

Underscores are otherwise ordinary word characters.  Only a token made
entirely of underscores is a rune, so `my_var` is a word.

## Runes Aren't Delimited

When SPACED (and PRINT, which uses it) puts spaces between items, it
doesn't put them around runes:

<!-- doctest: positive-test -->
```
assert ["abc defghijklm no" = spaced ["abc" "def" #ghij "klm no"]]
```

That may seem arbitrary for a rune like `#ghij`, but it matters a lot for
NEWLINE.  Without the rule, every line but the first would start with a
space, and every line but the last would end with one:

<!-- doctest: positive-test -->
```
assert ["line one^/line two" = spaced ["line" "one" newline "line" "two"]]
```

(Historical Rebol gets this wrong.  The stray spaces go unnoticed on the
screen, and only show up in the bytes of a file.)

It's also how an indent can be written:

<!-- doctest: positive-test -->
```
assert ["    indented text" = spaced [____ "indented" "text"]]
```

## The Space Rune as a Placeholder

`_` has an older job too.  In early Revolt it was the way to write what
historical Rebol called NONE!, and it still means "nothing here" where a
slot would otherwise hold a variable name.  It can't be a variable, so it can only mean "skip
this one":

<!-- doctest: positive-test -->
```
[_ second]: pack [1 2]          ; don't assign the first result
assert [second = 2]

assert [[5 11] = map [_ a b] each [1 2 3 4 5 6] [a + b]]
```

Being able to put it in a block, and not being reassignable, were the
two properties that made `_` useful from the start, and both are still
here.  Two others have gone:

* **It isn't "empty".**  `for-each 'x _ [...]` used to act like an empty
  block.  But APPEND has to add a `_` to a block like any other value,
  so treating it as nothing in other places became inconsistent.  It's a
  one-character piece of text now, and nothing more.

* **It isn't false.**  The only false state is the
  [NULL](/docs/concepts/flex-logic/) antiform, which can't be put in a
  block.

<!-- doctest: positive-test -->
```
assert [[a b c _] = append [a b c] _]
assert [1 = length of _]
assert [_ = any [null _]]       ; truthy
```

For "no value" that can't sneak into data, Revolt uses
[antiforms](/docs/concepts/antiforms/) instead.

## Not the Same as BLANK!

The comma, which separates expressions, is a
[BLANK!](/docs/datatypes/blank/).  That's also what fills the empty
position at the end of a [sequence](/docs/datatypes/sequences/), as in
`a/`.  Some older writing calls `_` "blank", but it's the space rune,
and it's a different value:

<!-- doctest: positive-test -->
```
assert [not blank? _]
assert [space? _]
```

## See Also

* [TEXT!](/docs/datatypes/text/) -- mutable text
* [BLANK!](/docs/datatypes/blank/) -- the comma
* [Reified Unreassignable Nothingness: Space Runes](https://revolt.metaeducation.com/forum/t/reified-unreassignable-nothingness-space-runes/2457)
  (forum, 2025)
* [Why Does FORM Use Space, Not Underscore?](https://revolt.metaeducation.com/forum/t/why-does-form-as-space-not-underscore/2455)
  (forum, 2025)
* [Taking Delimiters Literally in the RUNE! Datatype](https://revolt.metaeducation.com/forum/t/taking-delimiters-literally-in-the-rune-datatype/2386)
  (forum)
