---
layout: default
title: Stacklessness
parent: Concepts
nav_order: 8
permalink: /docs/concepts/stacklessness/
---

# Stacklessness

When a Revolt function calls another Revolt function, the interpreter
doesn't go any deeper on the C stack.  Every evaluation in progress is kept
in a structure on the heap, and one loop drives them all.  So how deeply
code can recurse depends on memory, not on the size of the machine stack:

<!-- doctest: positive-test -->
```
countdown: func [n] [
    if n = 0 [return <bottom>]
    return countdown n - 1
]

assert [<bottom> = countdown 50000]
```

This is called being **stackless**, after
[Stackless Python](https://en.wikipedia.org/wiki/Stackless_Python), which
did the same for Python.  This page is about the inside of the
interpreter: why it's built this way, how it works, and what it costs.

{: .warning }
> This describes the interpreter's implementation, which is where the
> design is least settled.  It's recorded here because the reasons behind
> it are hard to recover from the source alone.

## Why

### A Stack Overflow Can't Be Caught

Running out of heap memory is an ordinary error.  `malloc()` returns
NULL, and the program can report it and carry on.  Running out of C
stack is different.  The C standard gives no way to ask whether there's
room for another call, and once the stack has overflowed, the program is
in an undefined state.  Nothing can reliably recover from it, in C or in
languages built on C.

R3-Alpha and Red evaluate by having C functions call each other, so every
level of Rebol recursion is several levels of C recursion.  To avoid
crashing, R3-Alpha guessed.  It assumed the stack grew in one direction
through consecutive memory, and compared the address of a local variable
against a limit, raising an error when it got close:

```text
>> foo: func [] [foo]
>> foo
** Internal Error: Stack overflow
```

Nothing in the C standard says variables are laid out that way, and over
time the platforms stopped cooperating:

* **WebAssembly** broke it.  After an Emscripten upgrade the stack no
  longer grew in a predictable direction, so the check had to be turned
  off, and `foo: func [] [foo]` would crash the browser console.

* **Size optimization** made it worse.  Building the WebAssembly version
  for small size meant fewer inlined functions and more calls per
  evaluation step, and those compete with JavaScript's own stack.  Code
  that wasn't even recursive could overflow.

* **Address sanitizer** broke it on the desktop.  From GCC 13 and Clang
  15, sanitized builds allocate stack frames from a pool in no particular
  order, so there's no "direction" to measure.
  [MySQL hit the same problem](https://bugs.mysql.com/bug.php?id=111432).

With every level of evaluation on the heap, a recursion that goes too deep
runs out of *memory*, and that can be handled.  The address check has
since been removed from the interpreter.

### Suspending Code That's Running

The other reason is what the C stack prevents.  A computation whose state
is on the C stack can't be set aside and resumed later, because the C
functions holding that state would have to stay in the middle of running.

Once that state is in data structures instead, a computation can be
paused and picked up again.  That's what makes
[generators](#a-running-evaluation-can-be-put-aside-and-resumed) possible,
and it's how the browser console can stop in the middle of a loop to ask
for input without the special
[Asyncify](https://emscripten.org/docs/porting/asyncify.html) build of the
interpreter it once needed.

## How It Works

Each evaluation in progress is a **Level**: a small structure allocated on
the heap, with an output cell, a position in the code, a state byte, and a
pointer to an **executor**, which is the C function that knows how to
advance it.

One loop runs everything.  It's called the **trampoline**.  It calls the
top Level's executor, and the executor does a small amount of work and
*returns*.  What it returns says what should happen next:

| The executor returns | The trampoline |
|---|---|
| "My result is in my output cell" | goes back to the Level underneath, which was waiting for it |
| "Run this other Level, then come back to me" | runs that Level's executor |
| "Something was thrown" | drops Levels until one of them catches it |

When an executor needs a sub-expression evaluated, it doesn't call the
evaluator.  It pushes a Level, records in its state byte where it was, and
returns.  Later it's called again with the answer waiting, and uses the
state byte to pick up where it left off.

### Natives Are State Machines

This changes how every native that runs code has to be written.  Here's
WHILE in R3-Alpha.  `Do_Blk()` is a recursive call into the evaluator,
and the C function stays on the stack until the whole loop is over:

```c
REBNATIVE(while)
{
    ...
    do {
        ds = Do_Blk(b1, i1);      /* evaluate condition, recursively */
        ...
        if (!IS_TRUE(ds)) return R_RET;
        ds = Do_Blk(b2, i2);      /* evaluate body, recursively */
        ...
    } while (TRUE);
}
```

Revolt's WHILE never calls the evaluator.  It returns a request to
evaluate (CONTINUE), saying in STATE what it was waiting for, and is
called again when the result is ready.  Shortened from
`src/core/natives/n-loop.c`:

```c
DECLARE_NATIVE(WHILE)
{
    enum {
        ST_WHILE_INITIAL_ENTRY = STATE_0,
        ST_WHILE_EVALUATING_CONDITION,
        ST_WHILE_EVALUATING_BODY
    };

    switch (STATE) {
      case ST_WHILE_INITIAL_ENTRY: goto initial_entry;
      case ST_WHILE_EVALUATING_CONDITION: goto condition_result_in_spare;
      case ST_WHILE_EVALUATING_BODY: goto body_result_in_out_or_thrown;
    }

  initial_entry: {
    Add_Definitional_Continue(body, LEVEL);
    goto evaluate_condition;

} evaluate_condition: {
    STATE = ST_WHILE_EVALUATING_CONDITION;
    return CONTINUE(condition);  // trampoline runs it, then calls us back

} condition_result_in_spare: {
    ...
    if (not logic)
        goto return_out;  // falsey condition => last body result

} invoke_loop_body: {
    STATE = ST_WHILE_EVALUATING_BODY;
    return CONTINUE_BRANCH(body, SPARE);

} body_result_in_out_or_thrown: {
    ...  // handle BREAK and CONTINUE
    goto evaluate_condition;

} return_out: {
    ...
}}
```

Each `return CONTINUE(...)` goes back to the trampoline, so a WHILE inside
a WHILE inside a WHILE takes no more C stack than one WHILE does.

## What This Buys

**Depth is limited by memory, not by the C stack.**  In a 2022 test of a
function that recursed until something gave out, Red crashed at about
1,900 levels and Rebol2 stopped with an error at 14,262.  A 32-bit
optimized Revolt build got past 4,700,000.

### A Running Evaluation Can Be Put Aside and Resumed

Since the Levels aren't on the C stack, a group of them can be unhooked
and kept.  That's how a generator works: YIELD sets the generator's Levels
aside, and the next call puts them back.

<!-- doctest: positive-test -->
```
numbers: generator [yield 10 yield 20 yield 30]

assert [[10 20 30] = reduce [numbers numbers numbers]]
```

### And More

**There's one place where anything can happen between steps.**  Garbage
collection, noticing a Ctrl-C, and (one day) stopping at a breakpoint are
all done in the trampoline loop, at a moment when no C function is halfway
through changing something.

**Unwinding is a jump to a Level.**
[Definitional](/docs/concepts/definitionality/) RETURN names the Level it
belongs to, and the trampoline drops Levels until it gets there.

**Errors don't need `longjmp`.**  A native reports a panic by returning,
like any other result, and each Level above it gets a turn to clean up.
The `longjmp` or C++ exception path still exists, for panics from deep
inside C code that can't return, but the interpreter doesn't depend on it.
That matters on platforms like WebAssembly, where it may not be available.

**The garbage collector never has to read the machine stack.**  Every
live value is in a Level or another structure the interpreter owns.  Red
went the other way: its stack *is* the machine stack, so as of
[0.6.6](https://www.red-lang.org/2025/03/066-memory-management-improvements.html)
its garbage collector walks native call frames looking for Red values.
That depends on frame pointers the compiler may leave out, and has to
skip frames belonging to OS callbacks.  It's tied to how particular
platforms and compilers lay out the stack, and may not be possible at
all on a platform like WebAssembly, which doesn't expose the machine
stack.

## What It Costs

**Natives are harder to write.**  Every native that runs code has to be a
state machine, as WHILE is above, and that's much harder to write and to
read than a loop that calls the evaluator.

**Not everything is converted.**  A native that hasn't been converted
starts a second trampoline on the C stack, and a YIELD can't cross it.
Some operations on data are still ordinary C recursion, proportional to
how deeply blocks are nested inside each other.  As of 2024 that included
binding, copying, comparing and molding.  (The scanner was converted,
since API calls use it, so a partial scan can be unwound.)

**It's slower in places.**  A tight recursive evaluator can keep its state
in registers, and a trampoline can't.  Revolt wins some of that back with
shortcuts.  For example, each step always pushes one spare Level, which is
reused for whatever the step needs, whether that's a function call or a
group.

**C debuggers see less.**  In a recursive interpreter you can stop in a C
debugger and see the native CASE right there on the C stack, partway
through the branch it's running.  In a stackless one, that state is in
Levels, which have to be inspected as data.

## Built for a Debugger That Doesn't Exist Yet

Many of the choices inside the evaluator were made so that a stepping
debugger could be written later.  The debugger hasn't been written.  This
section records what was done in advance, and why, because the code looks
strangely indirect unless you know.

**Stepping and running-to-the-end are separate executors.**  The
*stepper* runs one step.  The *evaluator* calls the stepper over and over,
holding on to the last result.  It would be simpler and faster as one
function with a "keep going" flag.  But then a block being run would give
the trampoline only one result, at the end.  With the two apart, the
stepper can have a Level of its own, and each step's result passes through
the trampoline, where a debugger could see it.

**The fast path is used when nobody is watching.**  When not debugging,
the evaluator and stepper share one Level, and the evaluator calls the
stepper directly without going back to the trampoline.  There are several
shortcuts like this.  A comma is normally skipped over, but in debug mode
it's a step of its own that produces a void, so the debugger would see the
comma.  One function call that leads directly to another normally doesn't
bounce in between, but in debug mode it does, so that a breakpoint could
be put there.

**The debug paths are tested without a debugger.**  A path that's never
run will rot.  So in builds with runtime checks, the question "are we in
debug mode?" is answered *yes* about one time in 64, decided by the
trampoline's tick count.  Every test run goes through both the fast and
the slow paths, and since the tick count is the same on each run, a
failure can be reproduced.

This forces a discipline.  The answer can be different the next time the
question is asked, so code that takes the slow path has to remember that
it did.  A real debugger could be switched on at any moment, so it would
need the same discipline.

**Every bounce has a number.**  In checked builds the trampoline counts
its bounces.  Values and Levels record the tick at which they were made,
and the interpreter can be told to break at a given tick.  A crash seen at
tick 1,203,881 can be approached again by stopping at tick 1,203,880.

R3-Alpha and Red made no provision of this kind.  Whether it pays off
can't be known until the debugger exists.  Until then the cost is extra
states and extra code paths, and the benefit so far is the testing above
and the generators.

## Compared to Historical Rebol

| | Rebol2, R3-Alpha, Red | Revolt |
|---|---|---|
| A function's stack frame | on the C stack | a Level on the heap |
| Recursion limit | the C stack | memory |
| Too deep a recursion | a guessed-at error, or a crash | runs out of memory |
| Suspending code that's running | not possible | YIELD |
| A native that runs code | a C loop that calls the evaluator | a state machine |
| Finding live values for garbage collection | Red scans the machine stack | they're all in Levels on the heap |

## See Also

* [Evaluation](/docs/concepts/evaluation/) -- what the evaluator does,
  step by step
* [Definitionality](/docs/concepts/definitionality/) -- RETURN and BREAK
  unwind to the Level they belong to
* [Switching to Stackless: Why This, Why Now?](https://revolt.metaeducation.com/forum/t/switching-to-stackless-why-this-why-now/1247)
  (forum, 2020-2024)
* [Stackless Is Here, Today, Now!](https://revolt.metaeducation.com/forum/t/stackless-is-here-today-now/1844)
  (forum, 2022-2025), with the recursion comparison and the WHILE code
* [YIELDER and GENERATOR](https://revolt.metaeducation.com/forum/t/yielder-and-generator-and-thinking-about-coroutines/1311)
  (forum)
* [Why the C Stack Should Vanish](http://www.stackless.com/spcpaper.htm#_Toc470444066),
  from Stackless Python
