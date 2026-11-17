---
layout: datatype
title: QUOTED!
parent: Decorated Types
grand_parent: Datatypes
nav_order: 1
permalink: /docs/datatypes/quoted/
datatype: quoted!
decoration: 'any element, with one or more <code>&#39;</code> on the front'
---

A value with one or more quote marks on the front: `'foo`, `'[a b]`,
`''10`.  Evaluating it takes one quote off:

```
>> 'foo
== foo

>> ''foo
== 'foo

>> type of first ['foo]
== \~{quoted!}~\  ; antiform (datatype!)
```

That's how code mentions a value without running it.  `'foo` is the word
`foo` rather than the variable's value, and `'(a b)` is a group rather
than the result of evaluating one.

Any element can be quoted, any number of times: words, lists, sequences,
numbers, [quasiforms](/docs/datatypes/quasiform/), and values with
[sigils](/docs/datatypes/decorated/#sigils).  Historical Rebol only had
LIT-WORD! and LIT-PATH!.

## Adding and Removing Quotes

QUOTE adds one, UNQUOTE takes one off, and NOQUOTE takes off however many
there are.  QUOTES OF counts them:

```
>> quote [a b]
== '[a b]

>> unquote first [''a]
== 'a

>> noquote first ['''a]
== a

>> quotes of first ['''a]
== 3

>> quotes of 'a
== 0
```

QUOTE and UNQUOTE take `:depth` to add or remove several at once:

```
>> quote:depth 'a 3
== '''a
```

UNQUOTE won't take off quotes that aren't there:

<!-- doctest: negative-test match="not quoted enough" -->
```
unquote 'a
```

## What Can't Be Quoted

An [antiform](/docs/datatypes/antiforms/) can't be quoted.  To store one,
[LIFT](/docs/concepts/isotopes/#the-lifting-ladder) it, which makes its
quasiform, and quote that if you need more levels:

<!-- doctest: negative-test match="expect-arg" -->
```
quote null
```

```
>> lift null
== ~null~

>> quote lift null
== '~null~
```

And quotes always go on the outside.  A quoted value can't be made quasi,
or be given a sigil.  See [How They
Stack](/docs/datatypes/decorated/#how-they-stack).

## Checking for Them

QUOTED? tells you if a value has any quotes.  To check for a particular
heart, a type check can put quotes in front of the type, one for each
level:

```
>> quoted? first ['a]
== \~okay~\  ; antiform (logic!)

>> match ['word!] first ['a]
== 'a

>> match ['word!] first [''a]
== \~null~\  ; antiform (logic!)

>> match [''word!] first [''a]
== ''a
```

HEART OF gives the type underneath:

```
>> heart of first [''[a]]
== \~{block!}~\  ; antiform (datatype!)
```

## Quoting and Lifting

LIFT of anything that isn't an antiform adds a quote, and UNLIFT of a
quoted value takes one off.  So for ordinary values, lifting *is*
quoting.  That's what lets a [PACK!](/docs/datatypes/pack/) hold its items
lifted (`~('1 '2)~`): each item is quoted, unless it's an antiform, in
which case it's a quasiform.  See [Isotopes](/docs/concepts/isotopes/).

## See Also

* [Isotopes](/docs/concepts/isotopes/) -- the lifting ladder
* [Decorated Types](/docs/datatypes/decorated/) -- quotes, quasiforms,
  and sigils together
* [QUASIFORM!](/docs/datatypes/quasiform/) -- the rung below
