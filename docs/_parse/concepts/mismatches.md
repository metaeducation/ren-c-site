---
title: Mismatches
parent: Concepts
nav_order: 2
---

# Mismatches

Since a successful PARSE gives back the value of its last rule, and that
value could be anything (including NULL), "didn't match" can't be signaled
by a value.  Instead PARSE gives back a
[FAILURE!](/docs/datatypes/failure/).

Rules that match only part of the input fail with `parse-incomplete`:

<!-- doctest: negative-test match="parse-incomplete" -->
```
parse "aab" [some "a"]
```

Rules that don't match at all fail with `parse-mismatch`:

<!-- doctest: negative-test match="parse-mismatch" -->
```
parse "aaa" [some "b"]
```

## Reacting to a Failure

A failure that isn't handled becomes a panic, so a mismatch can't be
silently ignored.  Handle it like any other failure.  TRY turns it into a
NULL, and EXCEPT runs code instead:

```
>> try parse "aab" [some "a"]
== \~null~\  ; antiform (logic!)

>> parse "aab" [some "a"] except [<no match>]
== <no match>
```

When all you want to know is whether the input matched, PARSE-MATCH gives
back the input if it did, and NULL if it didn't:

```
>> parse-match "aaa" [some "a"]
== "aaa"

>> parse-match "aab" [some "a"]
== \~null~\  ; antiform (logic!)
```

## Failing Inside the Rules

Inside the rules, a rule that doesn't match isn't an error.  It sends PARSE
on to the next alternative after a `|`:

```
>> parse "b" ["a" | "b"]
== "b"
```

Only when every alternative has failed does the failure reach the caller.

## See Also

* [Synthesis](/docs/dialects/parse/concepts/synthesis/)
* [FAILURE!](/docs/datatypes/failure/), how failures work everywhere
