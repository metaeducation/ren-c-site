# docs/natives

One reference page per function built into the interpreter.

This README is not part of the site, and its examples are not tested.  See
`docs/README.md` for how examples are written and tested, and for the
`layout: native` front matter.

## What Belongs Here

**One page per function, named for the function** (`reduce.md` for REDUCE).
The page says what the function does and shows enough examples to use it.

Functions written in Revolt itself (the "mezzanine") get pages here too, if
they're part of what a user thinks of as the language.

### Companion Functions Share a Page

A function that only makes sense next to another is a section on that
function's page, not a page of its own.  CONST? is a section of
`const.md`.  This goes for `?` predicates in general, and for things like
a `:off` refinement's opposite.

Give the companion a page of its own when it has enough to say, or when
people would look it up by name without knowing the main function.

### Background Goes in Concepts

When explaining a function needs more than a couple of paragraphs about an
idea shared with other functions, that explanation belongs in
`docs/concepts/`.  The native page gets a short version and a link.  (See
`const.md`, and where it links to Constness.)

## The Spec

The `spec:` in the front matter is copied from the `native [...]` comment
above the function's C source, and the tests check its parameter names
against the interpreter.

* Leave out the modifiers before `native` (`pure`, `impure`,
  `vanishable`).  They aren't part of the spec block.  Say in the text of
  the page if the function is PURE or IMPURE, since that decides whether
  pure code can call it.

* Leave out the source's `; !!!` comments.

## Examples

* Prefer examples adapted from the interpreter's own test suite
  (`tests/` in the interpreter repository).  They're known to work, and
  they show what the designers thought was worth pinning down.

* For an example that shows an error, a `negative-test` that matches the
  error's **id** survives changes to the wording of messages.  Use a
  transcript with the message when the message itself is the point.

* Transcripts need results whose molded form is predictable.  Don't show
  the result of defining a function, or anything with fields that vary.

* If an example can't be made to pass, don't publish a guess at what it
  would do.  Leave it out, and find out whether the page or the
  interpreter is wrong.

## Usual Order of a Page

1. What it does, in a sentence or two, and the simplest example.
2. Sections on its rules and refinements, each with an example.
3. Companion functions.
4. Purity, if it's PURE or IMPURE.
5. "See Also": related natives, the concept page, and forum threads.
