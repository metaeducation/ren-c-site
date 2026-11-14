---
layout: datatype
title: FRAME!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 24
permalink: /docs/datatypes/frame/
datatype: frame!
summary: 'arguments and locals of a function state'
antiform: action!
---

The arguments and locals of one call of a function.  `make frame! append/` gives an unfilled frame for APPEND; fill it in and EVAL it to make the call.

Its antiform is [ACTION!](/docs/datatypes/action/): a frame that runs when a word holding it is evaluated.
