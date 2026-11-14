---
layout: datatype
title: CHAIN!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 28
permalink: /docs/datatypes/chain/
datatype: chain!
summary: 'refinement and function call dialect'
---

A sequence of elements joined by colons.  Setting and getting are spelled with chains: `a:` sets, and `:a` gets.  A function's refinements are chained on, as in `append:dup`.

CHAIN! replaced the historical SET-WORD!, GET-WORD!, SET-PATH! (and so on) types, which were special cases of this.

In a mixed sequence, slashes bind loosest and dots tightest: `foo/bar.baz:mumble` is a PATH! whose second element is a CHAIN! starting with a TUPLE!.

Sequences are immutable.  They are not ANY-SERIES?, so they have no position or index, and can't be changed in place.  Elements can still be picked by index or walked with FOR-EACH; to restructure one, convert it to a BLOCK! and back.  A sequence has at least two elements, and can't contain a sequence of the same kind directly.
