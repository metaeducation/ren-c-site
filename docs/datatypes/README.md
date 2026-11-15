# docs/datatypes

One reference page per datatype, plus the two pages that group them.

This README is not part of the site, and its examples are not tested.  See
`docs/README.md` for how examples are written and tested, and for the
`layout: datatype` front matter.

## What Belongs Here

**One page per datatype, named for the type without its `!`** (`text.md`
for TEXT!).  All the pages sit in this one folder, and their URLs are flat
(`/docs/datatypes/text/`).  The grouping is done by `parent:` in the front
matter, not by subfolders.

Every datatype is in exactly one of two groups:

| Parent page | Holds | `parent:` |
|---|---|---|
| `fundamentals.md` | Types a value in a list can have (TEXT!, BLOCK!, WORD!...) | `Fundamental Types` |
| `antiforms.md` | Types that can't be put in a list (VOID!, SPLICE!, LOGIC!...) | `Antiform Types` |

The index of all of them, with one-line summaries, is `docs/datatypes.md`.

### "Fundamental" Is a Technical Term

It means "can be put in a list", and every antiform is the antiform *of* a
fundamental type.  It doesn't mean "important" or "basic".  So the
Fundamental Types section holds datatype pages only.  A notable topic that
isn't a datatype (constness, binding) goes in `docs/concepts/`.

### The Explanation of Antiforms Is in Concepts

`antiforms.md` here is a short page: a table of the eight antiform types,
and a link.  The explanation of what antiforms are and how they work is
`docs/concepts/antiforms.md`, where people look for explanations.

The same split applies to anything else here that grows into an idea.  The
reference for a type stays in this folder, and the idea goes in
`docs/concepts/` (see the README there).

## Keeping in Step With the Interpreter

* `summary:` is the one-line description from the interpreter's
  `types.r`, word for word.  Put the page's own explanation in the body.

* `nav_order:` follows the order of the tables in `docs/datatypes.md`, so
  the sidebar and the index agree.

* A fundamental type with an antiform says so with `antiform:`, and the
  antiform's page says `antiform-of:` back.  The tests check the pairing
  using the antiform page's `sample:`.  (Which type an antiform belongs to
  has changed over time.)

* A new datatype needs its page here *and* a row in `docs/datatypes.md`.

## Stubs Are Fine

Most pages here are a few lines: what the type looks like, and what's
changed from historical Rebol (a rename, a new meaning).  That's enough to
start.  A page grows when there's something to say that isn't about one
native, the way `text.md` covers dashed strings.

What a *function* does with the type belongs on that function's page in
`docs/natives/`.
