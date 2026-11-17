---
layout: datatype
title: CHAIN!
parent: Sequence Types
grand_parent: Datatypes
nav_order: 2
permalink: /docs/datatypes/chain/
datatype: chain!
summary: 'refinement and function call dialect'
---

A sequence of elements joined by colons.  Setting and getting are spelled with chains: `a:` sets, and `:a` gets.  A function's refinements are chained on, as in `append:dup`.

CHAIN! replaced the historical SET-WORD!, GET-WORD!, SET-PATH! (and so on) types, which were special cases of this.

In a mixed sequence, slashes bind loosest and dots tightest: `foo/bar.baz:mumble` is a PATH! whose second element is a CHAIN! starting with a TUPLE!.

Like all [sequences](/docs/datatypes/sequences/), it is immutable, has at least two elements, and can't directly contain one of its own kind.
