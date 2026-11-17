---
layout: datatype
title: URL!
parent: Fundamental Types
grand_parent: Datatypes
nav_order: 15
permalink: /docs/datatypes/url/
datatype: url!
summary: 'uniform resource locator or identifier'
---

{: .warning }
> URL! is being redesigned, and the work isn't finished.  This page
> describes where it stands now.

A URL is written as a [TAG!](/docs/datatypes/tag/), and functions that
take a location, like READ, accept one:

```
>> type of <http://example.com>
== \~{tag!}~\  ; antiform (datatype!)
```

Without the angle brackets, `http://example.com` isn't a URL at all.
Since [sequences](/docs/datatypes/sequences/#in-the-middle) can have
blanks in the middle, it's an ordinary PATH!:

```
>> type of 'http://example.com
== \~{path!}~\  ; antiform (datatype!)
```

URL! itself is now the *structured* form: what DECODE-URL gives back,
with the parts of the URL as fields:

<!-- doctest: positive-test -->
```
u: decode-url <http://example.com:8080/index.html>

assert [url? u]
assert [u.scheme = 'http]
assert [u.host = "example.com"]
assert [u.port-id = 8080]
assert [u.path = "/index.html"]
```

In historical Rebol, URL! was a string type.  Tags already had the
delimiters to hold any text, so they took over the textual form, and the
syntax `http://...` was freed for sequences.
