---
title: OPTIONAL
parent: Combinators
nav_order: 3
---

# OPTIONAL

Runs a rule, and if it fails, succeeds anyway without moving through the
input.  `opt` is the short name.

```
>> parse "ab" [opt "x" "a" "b"]
== "b"
```

When the rule fails, the result is a [VOID!](/docs/datatypes/void/), not
NULL as with [TRY](/docs/dialects/parse/combinators/try/).

## See Also

* [TRY](/docs/dialects/parse/combinators/try/)
* [SOME](/docs/dialects/parse/combinators/some/), with which `opt some`
  means "zero or more"
