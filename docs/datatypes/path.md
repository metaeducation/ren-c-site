---
layout: datatype
title: PATH!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 29
permalink: /docs/datatypes/path/
datatype: path!
summary: 'member or refinement selection with execution bias'
---

A sequence of elements joined by slashes, such as `lib/append`.  A trailing slash, as in `append/`, gives the function itself without running it.

Sequences are immutable.  They are not ANY-SERIES?, so they have no position or index, and can't be changed in place.  Elements can still be picked by index or walked with FOR-EACH; to restructure one, convert it to a BLOCK! and back.  A sequence has at least two elements, and can't contain a sequence of the same kind directly.

Historically PATH! was a series, which allowed paths that looked like words (`next 'a/b`) or that were empty.  Making paths immutable removed those problems.
