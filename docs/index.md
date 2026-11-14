---
layout: default
title: Home
nav_order: 1
permalink: /
---

<h1 class="revolt-visually-hidden">REVOLT</h1>

<header class="revolt-hero">
  <p class="revolt-hero-wordmark" role="img" aria-label="REVOLT"><span aria-hidden="true">REV</span><img src="{{ '/assets/images/revolt-3d.png' | relative_url }}" alt="" width="371" height="391"><span aria-hidden="true">LT</span></p>
  <p class="revolt-hero-tagline">A deeply redesigned branch of the Rebol language.</p>
  <p class="revolt-hero-actions"><a class="btn btn-primary" href="{{ '/console/' | relative_url }}">Open the Web Console</a> <a class="btn" href="https://github.com/metaeducation/ren-c">Source on GitHub</a></p>
</header>

REVOLT is developed at
[github.com/metaeducation/ren-c](https://github.com/metaeducation/ren-c).
(The project was called Ren-C for most of its history, and the repository
keeps that name.)

## Try It

* **[Web Console](/console/)** -- the interpreter running in your browser
  (WebAssembly; nothing to install)

## Documentation

* **[Natives](/docs/natives/)** -- the functions built into the interpreter
  * [REDUCE](/docs/natives/reduce/)

Every example in the documentation is run by a current REVOLT interpreter
each time this site is built, and the result has to match what the page
shows:

```rebol
>> reduce [1 + 2 3 + 4]
== [3 7]
```

That includes the examples that are *supposed* to fail.  When a page shows
an error, the interpreter has to produce that error:

```rebol
>> reduce [null]
** PANIC: Invalid use of ~null~ antiform
```

## Community

* [Forum](https://rebol.metaeducation.com) -- design discussion and questions
* [REVOLT on GitHub](https://github.com/metaeducation/ren-c) -- source and
  issues
* [This site on GitHub](https://github.com/metaeducation/ren-c-site) --
  every page has a link at the bottom to edit it, or to report a problem
