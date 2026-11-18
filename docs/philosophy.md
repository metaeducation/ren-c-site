---
layout: default
title: Philosophy
nav_order: 3
permalink: /philosophy/
---

# Philosophy

Languages are usually compared on what their programs are like: how much
code a problem takes, how big and fast the result is, and how well the
language guards against mistakes.  Revolt cares about all of that.  But it
also counts something most languages leave out: **what it takes to build
the interpreter itself.**

Revolt isn't just a language spec that any implementation could satisfy.
The implementation is part of the point.  An interpreter that's small to
use but needs a giant compiler, a deep stack of libraries, and a build
system with dependencies of its own hasn't gotten rid of complexity.  It
has moved the complexity somewhere you weren't looking.

> Saying your design is simple, but relying on a giant pile of
> scaffolding, puts people in the position of analyzing a perpetual
> motion machine and looking to find the battery.
>
> What I am doing is providing the receipts.  C99 compiler.  Source you
> can read.
>
> The magic is, there is no magic.

## A Forth Principle

The Forth community has the same instinct.  Ask a Forth programmer about
an implementation that needs a heavyweight toolchain, and you'll often hear
that it "isn't really Forth", even if it runs Forth programs correctly.
The language is more than the semantics a user sees.  How it's built, and
what it depends on, is part of what it is.

Rebol's creator, Carl Sassenrath, wrote about this long before Revolt
existed.  In [Back to Personal Computing](https://sassenrath.com/computing.html)
(1997), written as he was starting on what became Rebol, he wrote that "it has become
universally acceptable for software technology to be absurdly complex", and
he counted the development systems needed to create software as part of its
bloat.  In [Fight Software Complexity Pollution](https://www.rebol.com/article/0497.html)
(2010), updating a web server whose executable was about 350 KB would have
meant installing a package "nearly 50 times larger than the software we're
trying to update":

> You need one little thing, but then it requires another, and another...

His advice was to say "no" to software complexity.  Revolt applies that to
its own build.

## Why C, and Not C++

If the interpreter were written in C++, programs written in Revolt wouldn't
change.  C++ and its standard library would probably make the interpreter
smaller, faster and less buggy.  C++ was designed so that its abstractions
cost nothing at runtime.

The cost is somewhere else.  To understand a self-hosting C compiler, you
only have to understand something like
[TCC](https://en.wikipedia.org/wiki/Tiny_C_Compiler), whose modern forms
are around 300 kilobytes on x86, and that's enough to build Revolt.  The
smallest full C++ compilers are around 3 megabytes, and the size reflects
how much there is to understand.  Even something as ordinary as
`std::vector` depends on deep features of the compiler to work.

So the interpreter is written in C.

## C99, with Needful as an Option

The baseline for building the interpreter is C99.  The only features it
uses that C89 didn't define are:

* `__VA_ARGS__` variadic macros
* `//` comments
* declaring variables in the middle of functions
* declaring variables in the conditions of `for` loops

Many compilers from before C99 could do these things, so older systems may
well be able to build it too.  Code that only uses the API can be C89.

C99 alone doesn't check much, though, and an interpreter as deep as Revolt
needs a lot of checking.  That comes from
[Needful](https://needful.metaeducation.com), a single header that adds
things like `Option(T)`, `Result(T)` and type-safe casts to C.  In a C
build, each of these is a macro that disappears:

```c
#define Option(T)  T
```

Build the **same source** as C++ (C++11 or later) with Needful's checks
switched on, and those macros become wrapper types that the C++ compiler
checks: a value that might be null can't be used as if it isn't, and a cast
can't quietly change what it means.  The checks happen at compile time, so
the C build's binary is unchanged.

This follows rule CPL.2 of the
[C++ Core Guidelines](https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md#S-cpl):
"If you must use C, use the common subset of C and C++, and compile the C
code as C++."  GCC itself is written that way.

Needful is **purely optional**.  Nobody needs a C++ compiler to build
Revolt.  The project's continuous integration runs the C++ build to catch
mistakes, the way you'd run a static analyzer.  You get C++'s checking
without C++ becoming a dependency.

## Where It's Going

The longer-term hope is to go further: build the interpreter from a
systems dialect of Revolt itself, along the lines of
[Red/System](https://static.red-lang.org/red-system-specs-light.html).
"User natives" could then write their bodies as blocks of that dialect,
instead of strings of C code as the TCC extension does today.  The
checking Needful gets from C++ would ideally come from that dialect too,
without pulling in all of C++.

## See Also

* [Stacklessness](/docs/concepts/stacklessness/) -- another case where how
  the interpreter is built is part of the design
* [Needful](https://needful.metaeducation.com) -- its documentation
* [Amish Programming](http://2019.reb4.me/talks) (talk, 2019)
* [The forum thread on C, C++ and dependencies](https://revolt.metaeducation.com/forum/t/1343),
  where most of this page comes from
