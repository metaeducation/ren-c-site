---
title: Combinators
nav_order: 2
has_children: true
---

# Combinators

Each keyword in a PARSE rule, and each type of value that can be a rule,
is handled by a **combinator**.  These are the ones PARSE uses unless you
give it others (`parse:combinators`).  They're grouped the way they are in
`default-combinators` in the interpreter's `uparse.r`, and described in its
words.

Combinators with pages of their own are linked.

### Basic Keywords

| Combinator | What it does |
|---|---|
| [`try`](/docs/dialects/parse/combinators/try/) | If parser fails, succeed and return NULL; don't advance input |
| [`optional`](/docs/dialects/parse/combinators/optional/) (`opt`) | If parser fails, succeed and return VOID!, don't advance input |
| `not` | If the parser argument is negatable, invoke it in the negated sense |
| `conditional` (`cond`) | If parser's synthesized result is null, skip to next alternate |
| `veto` | Stop the current rule chain, and skip to the next `\|` alternate |
| `spread` | Return splice antiform group for list arguments |
| `ahead` | Leave the parse position at the same location, but fail if no match |
| `further` | Pass through the result only if the input was advanced by the rule |

### Looping

| Combinator | What it does |
|---|---|
| [`some`](/docs/dialects/parse/combinators/some/) | Run parser in a loop, require at least one match; return last result |
| `while` | Run parser in a loop as long as condition matches; return last result |
| `until` | Run parser in a loop, until condition matches; return last result |
| `cycle` | Run parser continuously in a loop until return STOP result (or BREAK) |
| `tally` | Iterate a rule and count the number of times it matches (can be 0) |
| `repeat` | Call parser the number of times the times-parser synthesizes |
| `break` | Break an iterated construct like SOME or REPEAT, failing the match |
| `stop` | Break an iterated construct like SOME or REPEAT, succeeding the match |
| `accept` | Return a value explicitly from the parse, terminating early |

### Seeking and Positions

| Combinator | What it does |
|---|---|
| `to` | Match up TO position before parser success; return parser's result |
| `thru` | Match up THRU position after parser success; return parser's result |
| `seek` | SEEK to another position in INPUT, synthesize that series position |
| `between` | Synthesize a copy of INPUT after LEFT parser and before RIGHT |
| `skip` | Skip integral number of items, and synthesize position after the skip |
| `one` (`@`) | Match any one series item in input |
| `two` `three` `four` `five` | Match any N series items in input, make SPLICE! if input is list |
| `next` | Advance input to next position so long as not `<end>`, return position |
| `<here>` | Synthesize the current INPUT position, without advancing INPUT |
| `<end>` | Only match if the input is at the end |
| `<index>` | Synthesize the current series INDEX OF of the PARSE operation |
| `<input>` | Get original INPUT series position passed to this PARSE operation |
| `<subinput>` | Get original INPUT series position passed to this SUBPARSE operation |
| `measure` | Synthesize the length of a matched portion of content in series units |

### Building Results

| Combinator | What it does |
|---|---|
| [`across`](/docs/dialects/parse/combinators/across/) | Synthesize copied series from current parse position through a rule |
| [`collect`](/docs/dialects/parse/combinators/collect/) | Return a block of collected values from usage of the KEEP combinator |
| [`keep`](/docs/dialects/parse/combinators/collect/) | KEEP parser's result for COLLECT, and synthesize that same result |
| `accumulate` | Accumulate values, synonym for `[collect [opt some keep ...]]` |
| `gather` | GATHER an object from EMIT combinator calls in the passed-in parser |
| `emit` | Emit object field for GATHER with name and value; synthesize value |
| `word:` | Assign a rule's result to a variable, if the rule matches |
| `just` `the` | Synthesize literal value (not matched against INPUT) |
| `literal` (`lit`) | Match a value literally, e.g. `lit ''x` instead of `'''x` |

### Changing the Input

| Combinator | What it does |
|---|---|
| `change` | Substitute a match with new data |
| `remove` | Remove data that matches a parse rule |
| `insert` | Insert literal data into the input series |

### Nested Input

| Combinator | What it does |
|---|---|
| `subparse` | Recursion into other data with a rule, result of rule if match |
| `into` | Arity-1 variation of SUBPARSE (presumes current position as input) |

### Running Code

| Combinator | What it does |
|---|---|
| `(...)` | Synthesize result of evaluating the group (invisible if `<delay>`) |
| `phase` | Make a phase for capturing `<delay>` groups |
| `inline` | Synthesizes result of running combinator from evaluating the parser |
| `/name` | Run an ordinary action with parse rule products as its arguments |
| `match` | Match a series element against the same rules used for function args |
| `panic` | Panic, pointing at the current position in the input |

### Invisible

| Combinator | What it does |
|---|---|
| `elide` | Transform a result-bearing combinator into one that has no result |
| `comment` | Comment out an arbitrary amount of PARSE material |

### Values as Rules

Values that aren't keywords are rules too.  How each type of value matches
is up to its combinator:

| Rule | What it does |
|---|---|
| `[...]` | Sequence parse rules together, and return any alternate that matches (`\|` and `\|\|` are handled here; see [Sequencing](/docs/dialects/parse/concepts/sequencing/)) |
| `"text"` | Match TEXT! and return the rule matched against |
| `#rune` | Match RUNE! and return rule rune matched against |
| `#{...}` | Match BLOB! and return rule blob matched against |
| `'value` | Match the value literally; returns the matched value |
| `@value` | Match what a variable holds (or a group or block produces) literally |
| `integer!` | Match a value of a datatype (transcoded, for string input) |
| bitset | Match one character, byte or item in the set |
| `10` | Synthesize just the INTEGER! (see REPEAT for repeating rules) |
| `word` | Use the rule, or value to match, that the word holds |
| `any (...)` | Handle BLOCK! of rules as if each item in the block is an alternate |

`copy` and `set` aren't combinators any more.  They give an error saying
to use ACROSS and SET-WORD! instead.
