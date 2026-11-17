---
layout: datatype
title: LOGIC!
parent: Antiform Types
grand_parent: Datatypes
nav_order: 1
permalink: /docs/datatypes/logic/
datatype: logic!
antiform-of: word!
stable: true
summary: 'either ~okay~, or ~null~ (the only "falsey" state)'
sample: "1 = 1"
---

LOGIC! has exactly two values: `~okay~` and `~null~`.  They are the
antiforms of the words `okay` and `null`, and those words evaluate to them:

```
>> okay
== \~okay~\  ; antiform (logic!)

>> null
== \~null~\  ; antiform (logic!)

>> type of null
== \~{logic!}~\  ; antiform (datatype!)
```

Comparisons and tests produce them:

```
>> 1 = 1
== \~okay~\  ; antiform (logic!)

>> 1 = 2
== \~null~\  ; antiform (logic!)

>> integer? 1
== \~okay~\  ; antiform (logic!)

>> not null
== \~okay~\  ; antiform (logic!)
```

## NULL Is the Only False

Conditionals treat `~null~` as false, and **everything else as true**.
That includes zero, empty strings, and empty blocks:

```
>> if okay [<yes>]
== <yes>

>> if 0 [<yes>]
== <yes>

>> if "" [<yes>]
== <yes>

>> either null [<a>] [<b>]
== <b>
```

Because `~null~` can be held in a variable, a value that may or may not be
there can be tested directly, with no special "missing" case:

```
>> select [a 1 b 2] 'b
== 2

>> select [a 1 b 2] 'z
== \~null~\  ; antiform (logic!)

>> x: select [a 1 b 2] 'z
== \~null~\  ; antiform (logic!)

>> if x [<found>] else [<missing>]
== <missing>
```

`ANY` and `ALL` return the value that decided them, or `~null~`:

```
>> all [1 = 1, 'done]
== done

>> any [null, 'found]
== found

>> any [null null]
== \~null~\  ; antiform (logic!)
```

The infix `AND` and `OR` take a group (or a word) on their right, so that
the right side is only evaluated if it has to be:

```
>> okay and (print "evaluated" 2)
evaluated
== \~okay~\  ; antiform (logic!)

>> null and (print "not evaluated", 2)
== \~null~\  ; antiform (logic!)

>> null or (print "not evaluated", 1)
== \~okay~\  ; antiform (logic!)

>> null or (print "evaluated" 1)
evaluated
== \~okay~\  ; antiform (logic!)
```

## Testing For Them

```
>> null? null
== \~okay~\  ; antiform (logic!)

>> null? 1
== \~null~\  ; antiform (logic!)

>> okay? okay
== \~okay~\  ; antiform (logic!)

>> logic? okay
== \~okay~\  ; antiform (logic!)

>> logic? 1
== \~null~\  ; antiform (logic!)
```

`TO-LOGIC` (or `DID`) turns any value into a LOGIC! by the same rule the
conditionals use.  `BOOLEAN` gives the words `true` or `false` instead, for
when the answer is to be shown or stored:

```
>> to-logic 1
== \~okay~\  ; antiform (logic!)

>> did 1
== \~okay~\  ; antiform (logic!)

>> boolean 1
== true
```

## Not In Lists

Like every antiform, a LOGIC! can't be put in a list.  A `~null~` that
reaches a list-building operation is an error, not a silently skipped
item:

```
>> reduce [null]
** PANIC: Invalid use of ~null~ antiform

>> compose [a (null) b]
** PANIC: Invalid use of ~null~ antiform
```

To drop a null on purpose, turn it into a [VOID!](/docs/datatypes/void/)
with `OPT`; operations such as `COMPOSE` and `JOIN` let voids vanish:

```
>> compose [a (opt null) b]
== [a b]

>> join block! [1 opt null 2]
== [1 2]
```

The quasiforms `~okay~` and `~null~` can be put in lists, and evaluating
them gives the antiforms back:

```
>> first [~null~]
== ~null~

>> lift null
== ~null~

>> unlift first [~okay~]
== \~okay~\  ; antiform (logic!)
```

## See Also

* [VOID!](/docs/datatypes/void/) -- "no value", as distinct from "false"
* [Isotopes](/docs/concepts/isotopes/) -- the general mechanism
