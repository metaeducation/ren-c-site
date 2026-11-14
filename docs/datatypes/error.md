---
layout: datatype
title: ERROR!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 22
permalink: /docs/datatypes/error/
datatype: error!
summary: 'context with id, arguments, and stack origin'
antiform: failure!
---

A context describing an error: its `id`, `message`, and where it happened.  As a plain value it can be stored and inspected like any object.

Its antiform is [FAILURE!](/docs/datatypes/failure/), an error that is being returned and must be dealt with.
