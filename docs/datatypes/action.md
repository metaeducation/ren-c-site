---
layout: datatype
title: ACTION!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 4
permalink: /docs/datatypes/action/
datatype: action!
antiform-of: frame!
stable: true
summary: will trigger function execution from words
sample: "append/"
---

An ACTION! is a function that runs when the word holding it is evaluated.
Writing the word with a trailing slash gives the action itself, without
running it:

```
>> f: lambda [x] [x * 2]
== \~&[frame! [
    x: ~null~  ; hole
]]~\  ; antiform (action!)

>> f 21
== 42

>> f/
== \~&[frame! [
    x: ~null~  ; hole
]]~\  ; antiform (action!)

>> action? f/
== \~okay~\  ; antiform (logic!)
```

The display shows what an action is underneath: a FRAME! (the function's
arguments, not yet filled) in its antiform state.  That is why its type
answers as FRAME!:

```
>> type of f/
== \~{frame!}~\  ; antiform (datatype!)
```

A plain FRAME! does nothing when a word holding it is evaluated; the
antiform is what makes it run.  `GET` on the word also gives the action
without running it:

```
>> get $f
== \~&[frame! [
    x: ~null~  ; hole
]]~\  ; antiform (action!)
```

An action in a group is applied like any other:

```
>> (lambda [x] [x]) 5
== 5
```

## Frames

`MAKE FRAME!` on an action gives its plain frame.  Fill in the arguments
and `EVAL` it to run the function:

```
>> fr: make frame! f/
== &[frame! [
    x: ~null~  ; hole
]]

>> type of fr
== \~{frame!}~\  ; antiform (datatype!)

>> action? fr
== \~null~\  ; antiform (logic!)

>> fr.x: 21
== 21

>> eval fr
== 42
```

`UNRUN` goes the other way, from an action to its plain frame:

```
>> type of unrun append/
== \~{frame!}~\  ; antiform (datatype!)

>> action? unrun append/
== \~null~\  ; antiform (logic!)
```

## Not In Lists

Like every antiform, an action can't be put in a list, which is what
keeps a block of data from accidentally holding something that runs.  A
word for the action, or its plain frame, goes in a list instead.

## See Also

* [Isotopes](/docs/concepts/isotopes/) -- the general mechanism
