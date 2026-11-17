---
layout: datatype
title: TIED!
parent: Sigil Types
grand_parent: Datatypes
nav_order: 1
permalink: /docs/datatypes/tied/
datatype: tied!
sigil: $
---

A value with the TIE sigil, `$`, on the front: `$x`, `$[a b]`, `$a.b`.
See [Sigil Types](/docs/datatypes/sigils/) for what all three sigils have
in common.

## What the Evaluator Does With It

Code starts out unbound.  A tied value gets the binding of the place
where it's evaluated, and loses the sigil:

```
>> x: 10
== 10

>> $x
== x

>> get $x
== 10
```

The plain quoted word `'x` wouldn't work there, because it would still be
unbound when GET received it.  [Binding](/docs/concepts/binding/) covers
this, and why it's needed.

The same goes for a block.  `$[...]` gives the block with this place's
binding, which is what a function that evaluates a block it was handed
needs:

```
>> type of $[a b]
== \~{block!}~\  ; antiform (datatype!)
```

## Making One

TIE adds the sigil and UNTIE takes it off.  Neither binds anything:

```
>> tie 'x
== $x

>> untie '$x
== x
```

Written alone, `$` evaluates what follows and binds the result here.

## See Also

* [Sigil Types](/docs/datatypes/sigils/) -- TIE, PIN and META together
* [Binding](/docs/concepts/binding/) -- what `$` is for
