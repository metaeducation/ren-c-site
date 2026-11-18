---
layout: default
title: Downloads
nav_order: 7
permalink: /downloads/
---

# Downloads

There are no downloads.

{: .warning }
> Revolt isn't ready for general use, and no native binaries are packaged
> or distributed.  The project is experimental and its resources are
> limited, so the table stakes for taking part are that you're a developer
> who can build the interpreter yourself.

## If You Just Want to Try It

The one prebuilt experience is the **[Web Console](/console/)**.  It's the
whole interpreter compiled to WebAssembly, and it runs in your browser
with nothing to install.  The examples in this documentation can be pasted
into it.

## If You Want to Work on It

Build it from [the source on GitHub](https://github.com/metaeducation/revolt).
The repository's
[README](https://github.com/metaeducation/revolt#readme) has the full
instructions.  In outline:

**You need a C compiler.**  C99 is the baseline.  Building with a C++11
compiler instead adds a large number of compile-time checks, and those
checks are what the project's continuous integration runs.  If you plan to
submit changes, build that way.

**You don't need Make or CMake.**  The build is driven by a Revolt script,
`make.r`, which calls the C compiler itself.  So building Revolt takes an
existing Revolt executable.  A few are kept in the repository's `prebuilt/`
directory for this purpose.  They're old, they exist only to run the
build, and they aren't the "download" this page doesn't have.

A build on Linux looks like this:

```text
~/revolt$ export R3_MAKE="$(pwd)/prebuilt/r3-linux-x64-8994d23"

~/revolt$ cd build

~/revolt/build$ "$R3_MAKE" ../make.r \
    config: ../configs/default-config.r \
    debug: asserts \
    optimize: 2
```

Run `make.r` with `--help` for the options.  Configurations for other
platforms, including Windows, Android and WebAssembly, are in the
`configs/` directory.

{: .note }
> The build process is more complicated than it should be, and hasn't had
> the attention it deserves.  Help streamlining and documenting it is
> welcome.  It's written entirely in Revolt.

## If You Want a Rebol to Use

Revolt changes names and behaviors without notice, and code written for
it today may not run next month.  If you want a Rebol 3 interpreter for
work that has to keep running, a more conservative evolution of the same
original codebase is maintained by Oldes, at
[github.com/Oldes/Rebol3](https://github.com/Oldes/Rebol3).

## Getting Involved

* [The forum](https://revolt.metaeducation.com/forum/) is the place to
  ask questions, and to introduce yourself.
* [GitHub Issues](https://github.com/metaeducation/revolt/issues) reach
  the developers directly.
