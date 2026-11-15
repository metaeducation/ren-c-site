# docs/concepts

Explanations of ideas that cut across many natives and datatypes.

This README is not part of the site, and its examples are not tested.  See
`docs/README.md` for how examples are written and tested.

## What Belongs Here

**A page goes in Concepts only if no single native or datatype page could
be its home.**

| Page | Why it passes |
|---|---|
| `constness.md` | Spans CONST, MUTABLE, COPY, EVAL, and every function and loop body. |
| `purity.md` | Spans PURE, IMPURE, FINAL, and the evaluator's binding. |

If an idea has an obvious home, put it there instead, even if it's
conceptual.  Antiforms are the example: the explanation lives in
`datatypes/antiforms.md`, because that page is the parent of the eight
antiform type pages.  The rule is what keeps this folder from becoming a
junk drawer.

## How Concept Pages and Reference Pages Divide the Work

* The **native page** says what one function does, briefly, with enough
  examples to use it.  It links here for the reasons.

* The **concept page** tells the whole story once: the problem, the
  design, how the pieces interact, and the history.  It links to the native
  pages for details of each function.

Don't explain the same thing at length in both places.  When a native page
needs more than a couple of paragraphs of background, that background
belongs here.

## Splitting and Merging

Related ideas get separate pages when they answer different questions.
Constness is about whether code may *change* a series it was handed.
Purity is about what outside state a function may *see*.  Each page has a
short section linking to the other.

A section of some other page should move here when pages outside its
section start wanting to link to that one section, rather than to the whole
page.  (The likely first case: the mechanics of lifting and quasiforms,
currently in `datatypes/antiforms.md`, which matter to native pages that
have nothing to do with datatypes.)

## Page Format

```yaml
---
layout: default
title: Constness
parent: Concepts
grand_parent: Documentation
nav_order: 1
permalink: /docs/concepts/constness/
---
```

`nav_order` puts pages in reading order, so a page comes after the ones
it builds on.  The parent page is `docs/concepts.md`.

End with links to the forum threads where the design was worked out.
Forum threads record the thinking at one point in time, and the page
describes how things are now, so check claims against the interpreter (and
its tests) rather than copying them from a thread.  If the design is still
in flux, say so in a `{: .warning }` callout near the top.
