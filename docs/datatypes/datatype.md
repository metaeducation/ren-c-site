---
layout: datatype
title: DATATYPE!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 3
permalink: /docs/datatypes/datatype/
datatype: datatype!
antiform-of: fence!
stable: true
summary: the type of a value expressed as an antiform
sample: "type of 1"
---

A DATATYPE! is the type of a value.  `TYPE OF` gives one, and the words
ending in `!` hold them:

```
>> type of 1
== \~{integer!}~\  ; antiform (datatype!)

>> integer!
== \~{integer!}~\  ; antiform (datatype!)

>> integer! = type of 1
== \~okay~\  ; antiform (logic!)

>> type of type of 1
== \~{datatype!}~\  ; antiform (datatype!)
```

Being an antiform of a FENCE!, a datatype can't itself be put in a list.
Its quasiform can, and evaluates back to the datatype:

```
>> lift integer!
== ~{integer!}~

>> first [~{integer!}~]
== ~{integer!}~

>> type of unlift first [~{block!}~]
== \~{datatype!}~\  ; antiform (datatype!)
```

## Checking Types

The `?` functions answer for one type.  `MATCH` returns the value if it
has one of the given types and `~null~` if not; `ENSURE` returns the
value or panics:

```
>> integer? 1
== \~okay~\  ; antiform (logic!)

>> match [integer! text!] "abc"
== "abc"

>> match [integer! text!] 1.5
== \~null~\  ; antiform (logic!)

>> ensure integer! 1
== 1

>> ensure integer! "x"
** PANIC: ENSURE failed with argument of type ~{text!}~
```

Since datatypes compare equal to themselves, `SWITCH` can dispatch on
one:

```
>> switch type of "abc" [text! [<text>] integer! [<int>]]
== <text>
```

Type constraints such as `ANY-LIST?` or `ANY-NUMBER?` answer for a family
of types; see [Datatypes](/docs/datatypes/#type-constraints).

## Making Values From Types

`MAKE` builds a new value of a type, and `TO` converts one:

```
>> make block! 3
== []

>> make text! 10
== ""

>> to integer! "10"
== 10

>> to block! "a b"
== [a b]

>> to word! "hello"
== hello
```

## Datatypes Are Values

```
>> datatype? integer!
== \~okay~\  ; antiform (logic!)

>> datatype? 1
== \~null~\  ; antiform (logic!)

>> t: type of 1.5
== \~{decimal!}~\  ; antiform (datatype!)

>> t = decimal!
== \~okay~\  ; antiform (logic!)
```

## See Also

* [Datatypes](/docs/datatypes/) -- the list of types
* [Antiforms](/docs/concepts/antiforms/) -- the general mechanism
