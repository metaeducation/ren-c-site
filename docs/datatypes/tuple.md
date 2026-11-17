---
layout: datatype
title: TUPLE!
parent: Sequence Types
grand_parent: Datatypes
nav_order: 1
permalink: /docs/datatypes/tuple/
datatype: tuple!
summary: 'member selection with inert bias'
---

A sequence of elements joined by dots, such as `obj.field` or `1.2.3`.  Evaluating one picks a member, such as a field of an object.

Historical Rebol's TUPLE! held only small numbers (as in versions and colors).  It is now a general sequence like [PATH!](/docs/datatypes/path/), just with dots.

Like all [sequences](/docs/datatypes/sequences/), it is immutable, has at least two elements, and can't directly contain one of its own kind.
