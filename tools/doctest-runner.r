Rebol [
    title: "Ren-C Documentation Example Runner"
    file: %doctest-runner.r
    purpose: --[
        Runs the code examples that tools/extract-doctests.py pulls out of
        the Markdown in docs/, and checks that the interpreter behaves the
        way the documentation says it does.

        Invoked once per documentation page, with the extracted block files
        for that page as arguments (in page order):

            r3 tools/doctest-runner.r build/doctests/reduce/*.r

        All blocks from one page share system.contexts.user, so a later
        example on a page may use definitions made by an earlier one (much
        like reading a console session top to bottom).

        Exit code is 0 if every block passed, 1 if any failed.  Any other
        exit code means the interpreter itself fell over.
    ]--
    notes: --[
      * This is deliberately written in Ren-C, not Python: deciding whether
        a result "matches" means molding values, telling antiforms from
        quasiforms, and telling a PANIC from a FAILURE!.  Only the
        interpreter can do that faithfully.

      * Printed output (from PRINT, PROBE, etc.) shown in a transcript is
        not verified yet.  Lines that aren't `>>`, `==` or `**` lines are
        tallied as "unchecked" so they don't silently look tested.
    ]--
]


=== RESULT TALLY ===

passed: 0
failed: 0
unchecked: 0


=== HEADER PARSING ===

; Each extracted file begins with `; KEY: value` lines, ended by `;---`.
; Everything after that is the example's code (or transcript) verbatim.

parse-block-file: func [
    "Split an extracted file into a header object and body text"
    return: [object!]
    file [file!]
][
    let text: read:string file
    let lines: split text newline
    let header: make object! [
        source: "?"
        kind: "?"
        native: null
        datatype: null
        antiform-of: null
        match: copy []
        body: null
    ]
    let body-lines: copy []
    let in-header: okay
    for-each 'line lines [
        case [
            not in-header [append body-lines line]
            line = ";---" [in-header: null]
            let pos: find line ": " [
                let key: copy:part next line (pos)
                let val: copy skip pos 2
                key: trim key
                switch key [
                    "SOURCE" [header.source: val]
                    "KIND" [header.kind: val]
                    "NATIVE" [header.native: val]
                    "DATATYPE" [header.datatype: val]
                    "ANTIFORM-OF" [header.antiform-of: val]
                    "MATCH-ERROR-TEXT" [append header.match val]
                ]
            ]
        ]
    ]
    header.body: delimit newline body-lines
    return header
]


=== EVALUATION ===

; Evaluate code the way the console does: bound into the user context,
; intercepting panics.  Returns an object saying which of the three
; outcomes happened, with the text the console would show for it.
;
; 1. The LIFT is inside the ENRECOVER so that a definitional error (a
;    FAILURE! antiform) comes back as a value we can inspect, instead of
;    being escalated into a panic on its way out.
;
; 2. EVAL of a BLOCK! busts the ghost of a void from a non-vanishable last
;    step, giving a heavy void (`eval [if null [1]]` is `~()~`).  EVAL of
;    a GROUP! doesn't, which matches what the console shows for the same
;    input typed in (`if null [1]` shows the light void).

evaluate: func [
    return: [object!]
    source [text!]
][
    let code: transcode source
    wrap* system.contexts.user code
    code: inside system.contexts.user code

    code: as group! code  ; [2]
    let r: sys.util/enrecover [lift eval code]  ; [1]

    if error? r [
        return make object! [
            outcome: 'panic
            message: form r
            id: if r.id [form r.id]
            shown: unspaced ["** PANIC: " message]
        ]
    ]

    let lifted: unlift r  ; quoted if plain value, quasiform if antiform

    if all [quasi? lifted, error? unquasi lifted] [
        let e: unquasi lifted
        return make object! [
            outcome: 'failure
            message: form e
            id: if e.id [form e.id]
            shown: unspaced ["** Failure: " message]
        ]
    ]

    if all [quasi? lifted, tag? unquasi lifted] [  ; TRASH!
        return make object! [
            outcome: 'silent  ; the console doesn't display a trash
            molded: mold lifted
            shown: unspaced ["(nothing shown: trash " molded ")"]
        ]
    ]

    if quasi? lifted [
        return make object! [
            outcome: 'antiform
            molded: mold lifted  ; e.g. ~null~
            shown: unspaced ["== \" molded "\  ; antiform"]
        ]
    ]

    return make object! [
        outcome: 'value
        molded: mold-or-explain unlift lifted
        shown: unspaced ["== " molded]
    ]
]

; Not every value can be molded (a bare BLANK! has no representation, for
; instance).  An example that produces one should fail its check, not take
; the whole page's run down with it.
;
mold-or-explain: func [return: [text!] value [element?]] [
    let molded: ~
    let e: sys.util/recover [molded: mold value]  ; NULL if no panic
    if e [return unspaced ["(unmoldable: " form e ")"]]
    return molded
]

error-matches: func [
    "Does an error outcome satisfy any of the MATCH-ERROR-TEXT phrases?"
    return: [logic!]
    result [object!]
    phrases [block!]
][
    if empty? phrases [return okay]  ; no phrase given, any error will do
    for-each 'phrase phrases [
        if find result.message phrase [return okay]
        if all [result.id, phrase = result.id] [return okay]
    ]
    return null
]


=== TRANSCRIPT BLOCKS ===

; A transcript looks like a console session:
;
;     >> reduce [1 + 2 3 + 4]
;     == [3 7]
;
;     >> reduce [null]
;     ** PANIC: Invalid use of ~null~ antiform
;
; Rules:
;
; * `>>` starts an input.  If the input doesn't TRANSCODE on its own, the
;   following lines are added until it does (multi-line input).
;
; * `== X` must match MOLD of the result.  Continuation lines (up to a
;   blank line or the next `>>`) are part of the expected mold.
;
; * `== \X\  ; antiform (...)` is how the console shows antiforms.  The
;   result must then be an antiform whose LIFT molds as X.  Writing `== X`
;   for an antiform result (or `\X\` for a plain one) is a mismatch.
;
; * A TRASH! result shows nothing in the console, so an input that gives
;   one must have no `==` line.  (LIFT it to show which trash it was.)
;
; * `** PANIC: msg` or `** Failure: msg` must match the error's message,
;   and the kind (panic vs. definitional failure) must agree.  `** Id: x`
;   lines are also checked; other `**` lines (Where, Near...) are ignored.
;
; * An input with no `==` or `**` line is still run, and must not error.

starts-with: func [return: [logic!] line [text!] prefix [text!]] [
    return did all [
        (length of line) >= (length of prefix)
        prefix = copy:part line (length of prefix)
    ]
]

marker?: func [return: [logic!] line [text!]] [
    return any [
        starts-with line ">>"
        starts-with line "=="
        starts-with line "**"
    ]
]

parses?: func [return: [logic!] text [text!]] [
    return null? rescue [transcode text]  ; RESCUE gives NULL if no error
]

run-transcript: func [
    return: [block!] "problems found (empty if passed)"
    header [object!]
][
    let problems: copy []
    let lines: split header.body newline
    let i: 1
    let n: length of lines

    while [i <= n] [
        let line: lines.(i)
        if not starts-with line ">>" [
            if not empty? trim copy line [
                unchecked: unchecked + 1  ; stray line outside any input
            ]
            i: i + 1
            continue
        ]

        ; Gather the input, adding lines until it transcodes
        ;
        let input: trim:head copy skip line 2
        i: i + 1
        while [all [
            not parses? input
            i <= n
            not marker? lines.(i)
        ]] [
            append input newline
            append input lines.(i)
            i: i + 1
        ]

        ; Gather expectations until the next input
        ;
        let expect-value: null
        let expect-error-kind: null
        let expect-error-text: null
        let expect-id: null
        while [all [i <= n, not starts-with lines.(i) ">>"]] [
            let l: lines.(i)
            case [
                starts-with l "==" [
                    expect-value: trim:head copy skip l 2
                    i: i + 1
                    while [all [
                        i <= n
                        not marker? lines.(i)
                        not empty? trim copy lines.(i)
                    ]] [
                        append expect-value newline
                        append expect-value lines.(i)
                        i: i + 1
                    ]
                    continue
                ]
                starts-with l "** PANIC:" [
                    expect-error-kind: 'panic
                    expect-error-text: trim copy skip l 9
                ]
                starts-with l "** Failure:" [
                    expect-error-kind: 'failure
                    expect-error-text: trim copy skip l 11
                ]
                starts-with l "** Id:" [
                    expect-id: trim copy skip l 6
                ]
                starts-with l "**" [noop]  ; Where:, Near:, File:, Line:
                not empty? trim copy l [
                    unchecked: unchecked + 1  ; printed output, not verified
                ]
            ]
            i: i + 1
        ]

        let result: evaluate input
        let label: unspaced [">> " input]

        case [
            expect-error-kind [
                case [
                    not find [panic failure] result.outcome [
                        append problems label
                        append problems unspaced [
                            "  expected: ** "
                            either expect-error-kind = 'panic ["PANIC"] ["Failure"]
                            ": " expect-error-text
                        ]
                        append problems unspaced ["    actual: " result.shown]
                    ]
                    any [
                        result.outcome <> expect-error-kind
                        result.message <> expect-error-text
                    ][
                        append problems label
                        append problems unspaced [
                            "  expected: ** "
                            either expect-error-kind = 'panic ["PANIC"] ["Failure"]
                            ": " expect-error-text
                        ]
                        append problems unspaced ["    actual: " result.shown]
                    ]
                    all [expect-id, expect-id <> any [result.id "(none)"]] [
                        append problems label
                        append problems unspaced ["  expected: ** Id: " expect-id]
                        append problems unspaced [
                            "    actual: ** Id: " any [result.id "(none)"]
                        ]
                    ]
                ]
            ]
            expect-value [
                let anti: null
                let want: expect-value
                let pos: all [starts-with want "\", find next want "\"]
                if pos [
                    anti: okay
                    want: copy:part next want pos
                ]
                case [
                    find [panic failure] result.outcome [
                        append problems label
                        append problems unspaced ["  expected: == " expect-value]
                        append problems unspaced ["    actual: " result.shown]
                    ]
                    any [
                        result.outcome = 'silent
                        all [anti, result.outcome <> 'antiform]
                        all [not anti, result.outcome = 'antiform]
                        want <> result.molded
                    ][
                        append problems label
                        append problems unspaced ["  expected: == " expect-value]
                        append problems unspaced ["    actual: " result.shown]
                    ]
                ]
            ]
            find [panic failure] result.outcome [
                append problems label
                append problems "  expected: (no error)"
                append problems unspaced ["    actual: " result.shown]
            ]
        ]
    ]
    return problems
]


=== SCRIPT BLOCKS (POSITIVE AND NEGATIVE) ===

; Same vocabulary as the Needful doctests: a positive test must run
; without error, a negative test must error (and if MATCH-ERROR-TEXT lines
; are given, the message or error id must match one of them).

run-positive: func [return: [block!] header [object!]] [
    let result: evaluate header.body
    if find [panic failure] result.outcome [
        return reduce ["  expected: (no error)" unspaced ["    actual: " result.shown]]
    ]
    return []
]

run-negative: func [return: [block!] header [object!]] [
    let result: evaluate header.body
    if not find [panic failure] result.outcome [
        return reduce [
            "  expected: an error"
            unspaced ["    actual: " result.shown]
        ]
    ]
    if not error-matches result header.match [
        let lines: reduce [unspaced ["    actual: " result.shown]]
        for-each 'phrase header.match [
            insert lines unspaced ["  expected error matching: " phrase]
        ]
        return lines
    ]
    return []
]


=== SPEC BLOCKS ===

; The front matter of a native's page carries its spec.  Make a dummy FUNC
; from that spec so the interpreter parses it, then check that its
; parameters match the real function's.

run-spec: func [return: [block!] header [object!]] [
    if not header.native [
        return ["  spec block has no NATIVE: name"]
    ]
    let name: to word! header.native
    if not has lib name [
        return reduce [unspaced ["  no function named " name " in LIB"]]
    ]
    let real: get inside lib name
    if not action? real/ [
        return reduce [unspaced ["  LIB." name " is not a function"]]
    ]
    let spec: inside lib transcode header.body
    let dummy: ~
    let e: sys.util/recover [dummy: func spec []]  ; NULL if no panic
    if e [
        return reduce [unspaced ["  documented spec is invalid: " form e]]
    ]
    let documented: words of dummy/
    let actual: words of real/
    if documented <> actual [
        return reduce [
            unspaced ["  documented parameters: " mold documented]
            unspaced ["      actual parameters: " mold actual]
        ]
    ]
    return []
]


=== DATATYPE BLOCKS ===

; The front matter of a datatype's page names the type (`datatype:`), and
; for an antiform, which fundamental type it is the antiform of
; (`antiform-of:`) along with a `sample:` expression that produces one.
; The pairing has changed historically (SPLICE! was the antiform of GROUP!
; for a while), so it is checked: LIFT the sample's result into a quasiform,
; take the quasi off, and the type of what's left must be the documented
; fundamental type.

; Evaluates source text the way an example would be (bound into the user
; context) and gives back the LIFTed result, or an ERROR! if it panicked.
; (The antiform datatypes such as SPLICE! aren't in LIB, but the user
; context sees them, so names are resolved by evaluation rather than by
; looking in LIB.)
;
eval-lifted: func [return: [element? error!] source [text!]] [
    let r: sys.util/enrecover [
        let code: transcode source  ; may panic on bad source, that's a result
        wrap* system.contexts.user code
        lift eval inside system.contexts.user code
    ]
    if error? r [return r]
    return unlift r
]

lookup-datatype: func [
    "The DATATYPE! a name refers to, or NULL (with a problem added)"
    return: [null? datatype!]
    name [text!]
    problems [block!]
][
    let lifted: eval-lifted name
    if error? lifted [
        append problems unspaced ["  " name " is not a known word: " form lifted]
        return null
    ]
    if not quasi? lifted [
        append problems unspaced ["  " name " is not a datatype"]
        return null
    ]
    let value: unlift lifted
    if not datatype? value [
        append problems unspaced ["  " name " is not a datatype"]
        return null
    ]
    return value
]

run-datatype: func [return: [block!] header [object!]] [
    if not header.datatype [
        return ["  datatype block has no DATATYPE: name"]
    ]
    let problems: copy []
    let type: lookup-datatype header.datatype problems
    if not type [return problems]

    if not header.antiform-of [
        return []  ; a fundamental type's page, nothing more to check
    ]
    let heart: lookup-datatype header.antiform-of problems
    if not heart [return problems]

    if empty? trim copy header.body [
        return ["  antiform page needs a SAMPLE: expression in its front matter"]
    ]
    let lifted: eval-lifted header.body
    if error? lifted [
        return reduce [unspaced ["  sample panicked: " form lifted]]
    ]
    if not quasi? lifted [
        return reduce [
            unspaced ["  sample " trim copy header.body " did not produce an antiform"]
        ]
    ]
    let actual: type of unquasi lifted
    if actual <> heart [
        return reduce [
            unspaced ["  documented as antiform of: " mold lift heart]
            unspaced ["       sample is antiform of: " mold lift actual]
        ]
    ]
    return []
]


=== MAIN ===

files: map-each 'arg system.script.args [local-to-file arg]

if empty? files [
    print "usage: r3 doctest-runner.r <extracted-block-file> ..."
    quit 2
]

for-each 'file files [
    let header: parse-block-file file
    let where: unspaced [header.source " (" header.kind ")"]
    let problems: switch header.kind [
        "transcript" [run-transcript header]
        "positive-test" [run-positive header]
        "negative-test" [run-negative header]
        "spec" [run-spec header]
        "datatype" [run-datatype header]
    ] else [
        reduce [unspaced ["  unknown block kind: " header.kind]]
    ]
    either empty? problems [
        passed: passed + 1
        print unspaced ["ok   " where]
    ][
        failed: failed + 1
        print unspaced ["FAIL " where]
        for-each 'p problems [print unspaced ["    " p]]
    ]
]

print unspaced [
    "== " passed " passed, " failed " failed"
    if unchecked > 0 [unspaced [", " unchecked " output line(s) unchecked"]]
]

quit either failed = 0 [0] [1]
