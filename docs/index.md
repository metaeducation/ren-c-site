---
layout: default
title: Home
nav_order: 1
permalink: /
---

# Ren-C

Ren-C is a deeply redesigned branch of the Rebol language, developed at
[github.com/metaeducation/ren-c](https://github.com/metaeducation/ren-c).

This site is the beginning of its reference documentation.  It is small for
now, but it is built so that it can be trusted: **every example is tested**.

## Tested Examples

When the site is built, each console example is pulled out of the page and
run by a current Ren-C interpreter.  The result has to match what the page
shows, or the site doesn't deploy.

```rebol
>> reduce [1 + 2 3 + 4]
== [3 7]
```

That includes the examples that are *supposed* to fail.  An example showing
an error has to produce that error:

```rebol
>> reduce [null]
** PANIC: Invalid use of ~null~ antiform
```

So when a page says something doesn't work, that's checked too.

## Start Here

* [REDUCE](/reduce) -- the first reference page

## Feedback

Found something wrong or unclear?  Every page has a link at the bottom to
edit it on GitHub, and one to report a problem with it.  For deeper
discussion, see [the forum](https://rebol.metaeducation.com).
