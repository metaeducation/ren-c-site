---
layout: datatype
title: PATH!
parent: Sequence Types
grand_parent: Datatypes
nav_order: 3
permalink: /docs/datatypes/path/
datatype: path!
summary: 'member or refinement selection with execution bias'
---

A sequence of elements joined by slashes, such as `lib/append`.  A trailing slash, as in `append/`, gives the function itself without running it.

Like all [sequences](/docs/datatypes/sequences/), it is immutable, has at least two elements, and can't directly contain one of its own kind.

Historically PATH! was a series, which allowed paths that looked like words (`next 'a/b`) or that were empty.  Making paths immutable removed those problems.  [Sequence Types](/docs/datatypes/sequences/#sequences-are-immutable) shows them.
