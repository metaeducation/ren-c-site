---
layout: datatype
title: FENCE!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 31
permalink: /docs/datatypes/fence/
datatype: fence!
summary: 'list of elements that are used in construction via MAKE'
antiform: datatype!
---

A list in braces, such as `{a: 1}`.  It is new: historical Rebol used braces for strings.

Along with MAKE, the forum has proposed giving FENCE! a role in code: evaluating one could return its contents as a BLOCK! bound into a new context that holds its top-level assignments (a WRAP).  See [FENCE!'s Higher Calling: WRAP](https://revolt.metaeducation.com/forum/t/fence-s-higher-calling-wrap/2613) (2025).

Its antiform is [DATATYPE!](/docs/datatypes/datatype/).
