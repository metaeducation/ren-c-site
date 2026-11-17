---
layout: datatype
title: TAG!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 14
permalink: /docs/datatypes/tag/
datatype: tag!
summary: 'markup string (HTML or XML)'
antiform: trash!
---

A string in angle brackets, such as `<div>`.  Besides markup, tags are used as labels and markers in dialects, such as `<opt>` in a function spec.

Tags are also how URLs are written: `read <http://example.com>`.  Where dots and slashes could be read either as part of a tag or as [sequence](/docs/datatypes/sequences/) separators, the tag wins, so `<../foo/bar.txt>` is one tag.  See [URL!](/docs/datatypes/url/).

Its antiform is [TRASH!](/docs/datatypes/trash/), where the tag's text says why a value is unusable.
