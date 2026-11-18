---
title: TRY
parent: Combinators
nav_order: 2
---

# TRY

Runs a rule, and if it fails, succeeds anyway without moving through the
input.  The result is NULL when the rule failed:

<!-- doctest: positive-test -->
```
assert [null = parse "" [try "x"]]
assert ["x" = parse "x" [try "x"]]
```

So TRY is the one to use when you'll capture the result, and want to tell
"didn't match" apart afterward:

<!-- doctest: positive-test -->
```
prefix: ~
parse "aaa" [prefix: try "b", some "a"]
assert [null = prefix]
```

## See Also

* [OPTIONAL](/docs/dialects/parse/combinators/optional/), which gives a
  VOID! instead of NULL
* [Mismatches](/docs/dialects/parse/concepts/mismatches/)
