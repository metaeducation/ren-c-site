---
layout: datatype
title: FENCE!
parent: List Types
grand_parent: Datatypes
nav_order: 3
permalink: /docs/datatypes/fence/
datatype: fence!
summary: 'list of elements that are used in construction via MAKE'
antiform: datatype!
---

A list in braces, such as `{a: 1}`.  It is new: historical Rebol used braces for strings.

Besides its use with MAKE, a fence has a role in code.  Evaluating one gives its contents as a BLOCK!, bound into a new context that holds its top-level assignments (a WRAP).  So running that block sets its own variables, not the ones outside:

<!-- doctest: positive-test -->
```
a: 0
code: {a: 10 b: a + 1}

assert [block? code]
assert [11 = eval code]
assert [a = 0]
```

See [FENCE!'s Higher Calling: WRAP](https://revolt.metaeducation.com/forum/t/fence-s-higher-calling-wrap/2613) (2025).

Its antiform is [DATATYPE!](/docs/datatypes/datatype/).
