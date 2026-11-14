---
layout: datatype
title: TUPLE!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 27
permalink: /docs/datatypes/tuple/
datatype: tuple!
summary: 'member selection with inert bias'
---

A sequence of elements joined by dots, such as `obj.field` or `1.2.3`.  Evaluating one picks a member, such as a field of an object.

Historical Rebol's TUPLE! held only small numbers (as in versions and colors).  It is now a general sequence like [PATH!](/docs/datatypes/path/), just with dots.

Sequences are immutable.  They are not ANY-SERIES?, so they have no position or index, and can't be changed in place.  Elements can still be picked by index or walked with FOR-EACH; to restructure one, convert it to a BLOCK! and back.  A sequence has at least two elements, and can't contain a sequence of the same kind directly.
