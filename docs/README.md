# revolt-site docs

This directory is the source for the Revolt documentation site, built with
Jekyll and the [just-the-docs](https://just-the-docs.com) theme (the same
setup as [needful.metaeducation.com](https://needful.metaeducation.com)).

This README is not part of the site, and its examples are not tested.

## Every Example Is Tested

Before the site deploys, `tools/run-doctests.py` pulls the Rebol code
blocks out of these pages and runs them with a current interpreter.  If
anything doesn't behave as the page says, the site doesn't deploy.

### Code blocks are Rebol unless they say otherwise

A fenced block with no language named is Rebol: it's tested, and it's
styled as a console on the site.  There's no need to write
```` ```rebol ```` (though it still works).  To show something else, name
the language, as in ```` ```c ````, ```` ```yaml ```` or ```` ```text ````,
and the block is left alone.

Three places follow this rule and have to agree: `default_lang` in
`_config.yml`, `tools/extract-doctests.py`, and
`assets/js/revolt-console.js`.

### Console transcripts (the usual case)

Any Rebol block whose first line starts with `>>` is a
transcript, and is tested without needing a tag:

```
>> reduce [1 + 2 3 + 4]
== [3 7]

>> reduce [null]
** PANIC: Invalid use of ~null~ antiform
** Id: bad-antiform

>> 1 / 0
** Failure: attempt to divide by zero

>> reduce [1 veto 2]
== \~null~\  ; antiform (logic!)
```

| Line | Checked how |
|---|---|
| `>> code` | Evaluated.  If it doesn't load on its own line, following lines are added until it does (multi-line input). |
| `== X` | Must equal MOLD of the result.  Lines after it, up to a blank line, are part of X (multi-line molds). |
| `== \X\  ; antiform (...)` | The console's notation for antiforms.  The result must be an antiform whose LIFT molds as X.  An antiform shown without the backslashes (or a plain value shown with them) fails. |
| `** PANIC: msg` | Must panic, with exactly this message. |
| `** Failure: msg` | Must produce a FAILURE! (definitional error), with exactly this message.  A PANIC doesn't count. |
| `** Id: x` | The error's id must be `x`. |
| other `** ...` lines | Ignored (Where, Near, File, Line vary too much). |
| anything else | Printed output.  **Not checked yet**; counted as "unchecked" in the test summary. |

An input with no `==` or `**` line after it is still run, and must not
error.

All blocks on a page run in one interpreter session, top to bottom, so a
later example can use something an earlier one defined.

### Scripts

Same tags as the Needful docs.  The tag is an HTML comment on the line
immediately before the fence (Jekyll doesn't show it):

````markdown
<!-- doctest: positive-test -->
```
data: reduce [1 + 1, 2 * 3]
assert [data = [2 6]]
```

<!-- doctest: negative-test match="Cannot decay VOID!|bad-antiform" -->
```
reduce [1 elide 2 3]
```
````

A `positive-test` must run without error.  A `negative-test` must error,
and if `match=` is given, the error message must contain one of the
`|`-separated phrases (or the error id must equal one).

Untagged Rebol blocks that aren't transcripts are not tested,
and the test summary counts them.  To show a transcript that should not be
tested, tag it `<!-- doctest: skip -->`.

Examples inside callouts (`> ` quoted blocks) are not extracted, so keep
tested examples outside of them.

### Native spec pages

A native's page uses `layout: native` and puts its spec in the front matter:

```yaml
---
layout: native
title: REDUCE
parent: Natives
grand_parent: Documentation
permalink: /docs/natives/reduce/
native: reduce
spec: |
  "Evaluates N expressions to produce N results (but discards BLANK!)"
  return: [<null> element?]
  value "Lists evaluate each item, single values evaluate"
      [element?]
  :predicate "Applied after evaluation, default is IDENTITY"
      [frame!]
---
```

The layout shows the spec at the top of the page.  The tests check that the
spec is valid and that its parameter names match the interpreter's own
function.  (Copy the spec from the `native [...]` comment above the
function's C source.)

## The Look

The site is black and white with dim grays, after
[rebolsource.net](https://rebolsource.net): a `#fdfdfd` page, `#ddd`
hairlines, `#333` text, black for headings and links.  Where it lives:

| File | What |
|---|---|
| `_sass/custom/setup.scss` | Palette (`$revolt-*`), fonts (Archivo, Inter, JetBrains Mono), type scale (19px body). |
| `_sass/color_schemes/revolt.scss` | Maps the palette onto just-the-docs' named variables (`color_scheme: revolt` in `_config.yml`). |
| `_sass/custom/custom.scss` | Everything decorative: wordmark, nav, dark console blocks, callouts, tables, homepage hero. |
| `_includes/title.html` | The sidebar wordmark, REV[o]LT, with the mark standing in for the O. |
| `_includes/head_custom.html` | Web fonts, icons, social image, and the console script. |
| `assets/js/revolt-console.js` | Marks up `>>` / `==` / `**` lines in transcripts so input is bright and results dim.  Cosmetic; the blocks work without it. |
| `assets/js/revolt-nav.js` | Expands the sidebar's top-level sections (Documentation) on every page, including Home.  The expander button still collapses them. |
| `assets/images/revolt-mark.svg` | The flat `[o]` mark (also `favicon.svg`); `favicon.ico`, `icon-*.png` and `apple-touch-icon.png` are rendered from it (the 16px icon is the original hand-pixelled one). |
| `assets/images/revolt-3d.png` | The 3-D render of the mark, used in the homepage hero and `og-image.png`. |

### Datatype pages

A datatype's page uses `layout: datatype`.  For an antiform:

```yaml
---
layout: datatype
title: SPLICE!
parent: Antiforms
grand_parent: Datatypes
permalink: /docs/datatypes/splice/
datatype: splice!
antiform-of: block!
stable: true
summary: fragment of multiple values without a surrounding container
sample: "spread [a b c]"
---
```

The layout shows these as a fact box at the top.  The tests check that
`datatype:` names a datatype and, when `antiform-of:` is given, that the
`sample:` expression produces an antiform of that type (the pairing has
changed historically, so it's worth checking).  `summary:` is the one-line
description from the interpreter's `%types.r`.  A fundamental type's page
leaves out `antiform-of:` and `stable:`, and may give `antiform:` to name
its antiform.

Molds of frames and errors include fields that vary between sessions
(`line:`, `where:`, `file:`), so transcripts shouldn't show them; show
`type of` or a field instead.

## Running the tests locally

```sh
python tools/run-doctests.py --r3 C:/Projects/revolt/build/r3.exe
python tools/run-doctests.py --page reduce     # just one page
```

## Building the site locally

```sh
gem install bundler
cd docs
bundle init
bundle add jekyll just-the-docs webrick
bundle exec jekyll serve
```

Then open `http://localhost:4000`.
