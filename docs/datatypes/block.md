---
layout: datatype
title: BLOCK!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 30
permalink: /docs/datatypes/block/
datatype: block!
summary: 'list of elements that blocks evaluation unless EVAL is used'
antiform: splice!
---

A list in square brackets, such as `[a b c]`.  Evaluating a block gives the block itself; EVAL runs it as code.

Its antiform is [SPLICE!](/docs/datatypes/splice/): a block's items with no container around them.
