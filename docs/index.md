---
layout: default
title: Home
nav_order: 1
permalink: /
---

<h1 class="revolt-visually-hidden">Revolt</h1>

<header class="revolt-hero">
  <p class="revolt-hero-wordmark" role="img" aria-label="Revolt"><span aria-hidden="true">REV</span><img src="{{ '/assets/images/revolt-3d.png' | relative_url }}" alt="" width="371" height="391"><span aria-hidden="true">LT</span></p>
  <p class="revolt-hero-tagline">A deeply redesigned branch of the Rebol language.</p>
  <p class="revolt-hero-actions"><a class="btn btn-primary" href="{{ '/console/' | relative_url }}">Open the Web Console</a> <a class="btn" href="https://github.com/metaeducation/revolt">Source on GitHub</a></p>
</header>

**Revolt** (previously codenamed "Ren-C") is developed at
[github.com/metaeducation/revolt](https://github.com/metaeducation/revolt).

## Try It

* **[Web Console](/console/)** -- the interpreter running in your browser
  (WebAssembly; nothing to install)

## Documentation

* **[Datatypes](/docs/datatypes/)** -- every kind of value, and the
  [antiforms](/docs/datatypes/antiforms/) that carry signals

* **[Natives](/docs/natives/)** -- the functions built into the interpreter
  * [REDUCE](/docs/natives/reduce/)
  * *(more to come, just a demo of the statically validated example mechanic)*

Every example in the documentation is run by a current Revolt interpreter
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

* [Forum](https://revolt.metaeducation.com/forum/) -- design discussion and
  questions
* [Revolt on GitHub](https://github.com/metaeducation/revolt) -- source and
  issues
* [This site on GitHub](https://github.com/metaeducation/revolt-site) --
  every page has a link at the bottom to edit it, or to report a problem
