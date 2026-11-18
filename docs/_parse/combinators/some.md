---
title: SOME
parent: Combinators
nav_order: 1
---

# SOME

Runs a rule in a loop, requiring at least one match.  Gives back the
result of the last match.

```
>> parse "aaa" [some "a"]
== "a"

>> parse [1 2 3] [some integer!]
== 3
```

With no match at all, SOME fails:

<!-- doctest: negative-test match="parse-mismatch" -->
```
parse "bbb" [some "a"]
```

## Zero or More

To allow zero matches, use `try some` or `opt some`.  This takes the place
of historical PARSE's ANY and WHILE, which have new meanings:

```
>> parse "aaa" [try some "b" some "a"]
== "a"
```

## See Also

* `tally`, which counts matches instead
* `repeat`, for a fixed number of matches
* [TRY](/docs/dialects/parse/combinators/try/) and
  [OPTIONAL](/docs/dialects/parse/combinators/optional/)
