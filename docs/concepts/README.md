# docs/concepts

Explanations of ideas that cut across many natives and datatypes.

This README is not part of the site, and its examples are not tested.  See
`docs/README.md` for how examples are written and tested.

## What Belongs Here

**A page goes in Concepts if it explains an idea, rather than documenting
one function or one type.**

| Page | The idea |
|---|---|
| `antiforms.md` | Values that can't be put in a list: quasiforms, LIFT and UNLIFT, stable and unstable. |
| `constness.md` | Read-only views of series.  Spans CONST, MUTABLE, COPY, EVAL, and every function and loop body. |
| `purity.md` | Functions that depend only on their arguments.  Spans PURE, IMPURE, FINAL, and the evaluator's binding. |
| `infix.md` | Functions that run in the same step as their left side.  Spans INFIX, THEN, ELSE, ALSO, the operators, and how every expression is evaluated. |

The reason is discoverability.  Someone learning the language looks in
Concepts for "what is this and why", and shouldn't have to know that the
explanation of antiforms happens to sit above eight type pages in another
section.

So an idea belongs here **even when it has a matching group of reference
pages**.  Antiforms are the example: the explanation is here, and the
reference pages for the eight antiform types stay in `docs/datatypes/`
under a short "Antiform Types" page that links back.

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

When a reference page finds itself explaining an idea that other pages
also need, that explanation moves here, and the reference page links to
it.

## Page Format

```yaml
---
layout: default
title: Constness
parent: Concepts
grand_parent: Documentation
nav_order: 2
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
