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

Rebol made a promise: because code is data, and control constructs are
ordinary functions, you can build your own languages inside it, cheaply.
At the console, in small examples, the promise holds.  It breaks when you
try to *factor* your code: wrap a construct, nest one inside another, or
combine pieces written by different people.

**Revolt** (previously codenamed "Ren-C") is a long-running effort to make
the promise hold.  It keeps what made Rebol a pleasure, and rebuilds the
parts underneath that kept it from composing.

## One Example

Here is the simplest test of "control constructs are just functions":
write UNLESS, using IF.  In historical Rebol, the obvious way gives a wrong
answer, silently:

```text
rebol2>> unless: func [cond block] [if not cond block]

rebol2>> check: func [x] [unless x = 10 [return "not 10"] return "it's 10!"]

rebol2>> check 20
== "it's 10!"    ; UNLESS caught the RETURN that was meant for CHECK
```

In Revolt, a RETURN belongs to the function it was written in, so the
wrapper just works:

<!-- doctest: positive-test -->
```
my-unless: func [cond block] [return if not cond (block)]

check: func [x] [
    my-unless x = 10 [return "not 10"]
    return "it's 10!"
]

assert ["not 10" = check 20]
```

That's [definitionality](/docs/concepts/definitionality/), and it is one of
a set of changes that work together.

## Every Claim Here Is Run

That last example isn't an illustration.  It was executed.  **Every example
in this documentation is run by a current Revolt interpreter each time the
site is built**, and the result has to match what the page shows:

```
>> reduce [1 + 2 3 + 4]
== [3 7]
```

That includes the examples that are *supposed* to fail.  A block marked as
an error must produce an error, or the site doesn't deploy:

<!-- doctest: negative-test match="bad-antiform" -->
```
reduce [null]
```

When the interpreter changes, the pages that are now wrong turn red.  So
what you read here is what the interpreter does, not what somebody
remembers it doing.

## What Was Wrong, and What Changed

Each of these was a known problem in Rebol2, R3-Alpha and Red.  Each has a
page here showing the fix, with tested examples.

| In historical Rebol | In Revolt | |
|---|---|---|
| RETURN, BREAK and THROW go to whatever is nearest on the stack, so wrappers intercept them | They belong to where they were written | [Definitionality](/docs/concepts/definitionality/) |
| A typo and "file not found" arrive the same way, so catching one catches both | Functions *return* failures to their caller; bugs are panics | [Failure](/docs/concepts/failure/) |
| NONE means "nothing found", "false", "loop broke" and "no value", and can be sitting in your data | Signals are *antiforms*, which can't be put in a block | [Antiforms](/docs/concepts/antiforms/) |
| Two false values, one of which prints like the word `false` | One false state, NULL, and it can't be in a block | [Flexible Logic](/docs/concepts/flexible-logic/) |
| Extra results come back in a block, or by writing to variables you name | Functions return a *pack*, which wrappers can see and callers can ignore | [Packs](/docs/concepts/packs/) |
| Loaded code is bound to one global context, and rebinding is destructive | Code starts unbound and gets its meaning from where it's written | [Binding](/docs/concepts/binding/) |
| A literal `[]` in a function body is silently modified on every call | Bodies are read-only unless you say MUTABLE | [Constness](/docs/concepts/constness/) |
| `1 + 2 * 3` and `add 1 2 * 3` disagree, because of a hidden evaluator state | One rule for infix and prefix, with no exceptions | [Infix](/docs/concepts/infix/) |
| No way to have a function leave no result without tricks | Vanishing is built in, and made safe | [Vanishing](/docs/concepts/vanishing/) |

These aren't independent patches.  Failures and vanishing are built on
antiforms.  Definitional RETURN is built on binding.  Each mechanism got
used again by things it wasn't designed for, which is the best evidence
that it's a design.

## What Didn't Change

The best thing about Rebol was never just that code is data.  It's the
*literals*: dates, URLs, email addresses, files, tags and more are all
values you can simply write, so a dialect can read like its subject instead
of like a programming language.  All of that is here:

```
>> type of 12-Sep-2026
== \~{date!}~\  ; antiform (datatype!)

>> type of %notes.txt
== \~{file!}~\  ; antiform (datatype!)

>> type of user@example.com
== \~{email!}~\  ; antiform (datatype!)
```

## Where It Stands

{: .warning }
> Revolt is experimental, and isn't being offered as something to build on.
> There is no stable release, and names and behaviors still change.  This
> site is a record of the experiments and what they found, kept so that the
> results aren't lost, and so the remaining work can be prioritized.  Pages
> about the parts in flux say so at the top.

## Start Here

* **[Why Revolt](/why/)** -- what the experiment is for, in terms of
  problems you know from other languages

* **[Web Console](/console/)** -- the interpreter running in your browser
  (WebAssembly; nothing to install)

* **[Concepts](/docs/concepts/)** -- the ideas, starting with
  [antiforms](/docs/concepts/antiforms/)

* **[Datatypes](/docs/datatypes/)** -- every kind of value

* **[Natives](/docs/natives/)** -- the functions built into the interpreter

* **[Downloads](/downloads/)** -- there aren't any, and why

## Community

* [Forum](https://revolt.metaeducation.com/forum/) -- design discussion and
  questions
* [Revolt on GitHub](https://github.com/metaeducation/revolt) -- source and
  issues
* [This site on GitHub](https://github.com/metaeducation/revolt-site) --
  every page has a link at the bottom to edit it, or to report a problem
