---
layout: default
title: Flexible Logic
parent: Concepts
grand_parent: Documentation
nav_order: 3
permalink: /docs/concepts/flexible-logic/
---

# Flexible Logic

Revolt has exactly one "false" state, and it's NULL.  Everything else you
can test is true, including `0`, the empty string, an empty block, and the
*word* `false`.

There are no TRUE and FALSE values built into the language.  The results of
tests are `~okay~` and `~null~`, a pair of
[antiforms](/docs/concepts/antiforms/) that can't be put in a block.  When
you want to *store* a yes-or-no answer, you store a word, and the choice of
words is yours: `true` and `false`, `yes` and `no`, `on` and `off`.  That
freedom is what "flexible" means.

## The Logic Pair

A comparison gives back one of two values:

```
>> 1 = 1
== \~okay~\  ; antiform (logic!)

>> 1 = 2
== \~null~\  ; antiform (logic!)
```

OKAY and NULL are the two values of the type
[LOGIC!](/docs/datatypes/logic/).  Both are antiforms of WORD!.  NULL is
not specific to logic: it's the same "nothing here" that a failed search
gives.  OKAY exists so that a test has something to say when the answer is
yes and there's no more interesting value to give.

## Conditions Test One Thing

IF, and everything else that takes a condition, asks a single question:
*is it NULL?*

```
>> if 0 [<ran>]
== <ran>

>> if "" [<ran>]
== <ran>

>> if [] [<ran>]
== <ran>

>> if 'false [<ran>]
== <ran>
```

There's nothing to memorize about which numbers or strings count as false.
None do.

A [VOID!](/docs/concepts/vanishing/) isn't true or false.  It's not an
answer at all, so testing one is an error:

<!-- doctest: negative-test match="Cannot decay VOID!" -->
```
if () [<ran>]
```

## Nothing in a Block Is False

OKAY and NULL can't be put in a block:

<!-- doctest: negative-test match="bad-antiform" -->
```
reduce [1 = 1 1 = 2]
```

That's deliberate, and it fixes an old trap.  In historical Rebol the false
value *could* go in a block, where it looked exactly like the word `false`:

```text
rebol2>> a: [false]             ; a block holding the word FALSE
rebol2>> b: reduce [false]      ; a block holding the LOGIC! value

rebol2>> a
== [false]
rebol2>> b
== [false]                      ; identical on screen

rebol2>> if first a [print "ran"]
ran                             ; a word, and words are true
rebol2>> if first b [print "ran"]
== none                         ; a LOGIC! false
```

Two blocks that look the same and behave oppositely.  The same went for
NONE: "is there an item here?" and "is the item NONE?" were the same test,
so the common `any [pick block index <default>]` broke as soon as the data
contained a NONE.

In Revolt, **every item in a block is true**, with no exceptions.  So the
only NULL you can get from looking in a block is the one that means
"there's nothing there":

<!-- doctest: positive-test -->
```
block: copy [a false 0 ""]
count: 0
for-each 'item block [if item [count: count + 1]]
assert [count = 4]

assert [null = try pick block 5]
```

and a loop can safely run until a value isn't there:

<!-- doctest: positive-test -->
```
block: copy [a b false c]
seen: copy []
item: ~
while [item: try take block] [append seen item]
assert [seen = [a b false c]]
```

In a language where a false value can sit in the data, that loop would
stop at the `false`.

## TRUE and FALSE Are Words

The system doesn't define `true` or `false`:

<!-- doctest: negative-test match="no-binding" -->
```
true
```

They're just words, and words are true.  When your data uses them, you ask
which one you have with a predicate that knows the pair:

```
>> true? 'true
== \~okay~\  ; antiform (logic!)

>> true? 'false
== \~null~\  ; antiform (logic!)

>> yes? 'no
== \~null~\  ; antiform (logic!)

>> off? 'off
== \~okay~\  ; antiform (logic!)
```

Each predicate accepts only its own two words.  Anything else is an error,
so a typo or a value from the wrong vocabulary is caught instead of quietly
taking a branch:

<!-- doctest: negative-test match="expect-arg" -->
```
flag: 'ture
if true? flag [<on>]
```

<!-- doctest: negative-test match="expect-arg" -->
```
true? 'yes
```

So `if true? flag [...]` is a real check.  Compare that with testing a
variable that's supposed to hold true or false in a language where any
value can be tested: nothing notices if it holds something else.

| Words | Ask with | Is it one of the pair? |
|---|---|---|
| `true`, `false` | TRUE?, FALSE? | BOOLEAN? |
| `yes`, `no` | YES?, NO? | YESNO? |
| `on`, `off` | ON?, OFF? | ONOFF? |

## From Logic to Words

To store the result of a test, turn it into a word.  BOOLEAN gives `true`
or `false`, TO-YESNO gives `yes` or `no`, and TO-ONOFF gives `on` or `off`:

```
>> boolean 1 = 2
== false

>> to-yesno 1 = 1
== yes

>> to-onoff 1 = 2
== off

>> append [flag:] boolean 1 = 2
== [flag: false]
```

For a whole block of tests, REDUCE with a predicate does the conversion as
it goes:

```
>> reduce:predicate [1 = 1 1 = 2] boolean/
== [true false]
```

### NOT Works on Logic, Not on Words

NOT asks "is it NULL?" like everything else, so it can't be used to flip a
word.  `not 'false` isn't `true`: the word is true, so NOT gives NULL.

```
>> not 'false
== \~null~\  ; antiform (logic!)
```

To flip a word, test it, negate the logic, and turn it back into a word:

```
>> boolean not true? 'true
== false
```

This is the clumsiest part of the design at present.  There isn't yet a
good short name for "the opposite word".

## ALL and ANY Give Back Values

Since anything but NULL is true, ALL and ANY don't need to reduce their
answer to a yes or no.  ALL gives the last value, and ANY gives the first
one that isn't NULL:

```
>> all [1 = 1 'done]
== done

>> any [null 'fallback]
== fallback
```

## Compared to Other Languages

Most languages have several false values, and the list is different in each
one.  A few chose a single one:

| Language | What counts as false | Can a false value be stored in a list? |
|---|---|---|
| C, JavaScript, Python | `0`, empty strings, and more: it varies by language | yes |
| Common Lisp | `nil`, which is also the empty list | yes |
| Ruby, Clojure, Lua | `nil` and `false` | yes (in Lua, `nil` can't be a table value, but `false` can) |
| Scheme | only `#f` | yes |
| Rebol2, Red | `none` and `false` | yes |
| **Revolt** | only NULL | **no** |

Scheme is the closest: one false value, and `0` and the empty list are
true.  The difference is the last column.  A `#f` can be an element of a
list, so "I ran out of elements" and "the element is false" still need
different tests.  Because Revolt's NULL can't be in a block, they're the
same test, and it's always right.

## See Also

* [LOGIC!](/docs/datatypes/logic/) -- the datatype
* [Antiforms](/docs/concepts/antiforms/) -- why OKAY and NULL can't be in a
  block
* [Flexible Logic System: Terminology](https://revolt.metaeducation.com/forum/t/flexible-logic-system-terminology/2252)
  (forum, 2024)
* [Why Can't LOGIC Be In a BLOCK!?](https://revolt.metaeducation.com/forum/t/why-cant-logic-e-g-result-of-10-20-be-in-block/2095)
  (forum, 2024; uses the older `~true~` and `~false~`)
