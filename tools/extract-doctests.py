#!/usr/bin/env python3
"""
extract-doctests.py - Extract Ren-C examples from docs/**/*.md for testing

Follows the same conventions as needful-enhanced's tools/extract-doctests.py:
an HTML comment on the line immediately before a fenced code block says how
the block is to be tested.  Jekyll ignores the comment, so it is invisible
on the rendered page.

    <!-- doctest: positive-test -->
    ```rebol
    ; Script code -- must run without error.
    ```

    <!-- doctest: negative-test match="phrase1|phrase2" -->
    ```rebol
    ; Script code -- must PANIC or produce a FAILURE!, and the message (or
    ; the error's id) must contain one of the phrases.
    ```

    <!-- doctest: transcript -->
    ```rebol
    >> reduce [1 + 2 3 + 4]
    == [3 7]
    ```

    <!-- doctest: skip -->
    ```rebol
    >> this block looks like a transcript but is not tested
    ```

A ```rebol block whose first non-blank line starts with `>>` is a transcript
even without a tag.  (So every console-style example is tested unless it
opts out with `skip`.)  Other untagged ```rebol blocks are not tested, and
are counted in the summary so they're visible.

Pages whose front matter has `native:` and a `spec: |` literal block also
produce a "spec" test, which checks the documented spec's parameters
against the real function's.

Pages whose front matter has `datatype:` produce a "datatype" test, which
checks the name is a datatype; if the page also has `antiform-of:` and a
`sample:` expression, the sample must produce an antiform of that type.

Output is one directory per page, one file per block, in page order:

    <out-dir>/<page-stem>/001-transcript.r
    <out-dir>/<page-stem>/002-negative-test.r
    ...

Each file starts with `; KEY: value` header lines ended by `;---`, then the
block's text verbatim.  Files are written with LF line endings (the
interpreter rejects CR).  The output directory is wiped on each run.

Usage:
    python tools/extract-doctests.py
    python tools/extract-doctests.py --docs-dir docs --out-dir build/doctests
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


# <!-- doctest: positive-test -->
# <!-- doctest: negative-test match="cannot decay|bad-antiform" -->
# <!-- doctest: transcript -->
# <!-- doctest: skip -->
#
_DOCTEST_COMMENT = re.compile(
    r'^<!--\s*doctest:\s*'
    r'(?P<kind>positive-test|negative-test|transcript|skip)'
    r'(?:\s+match="(?P<match>[^"]+)")?'
    r'\s*-->\s*$'
)

_FENCE_OPEN = re.compile(r'^```(?:rebol|ren-c|r3)\s*$')
_ANY_FENCE_OPEN = re.compile(r'^```')
_FENCE_CLOSE = re.compile(r'^```\s*$')


class Block:
    def __init__(self, kind, line, text, match=None, native=None, extra=None):
        self.kind = kind          # transcript, positive-test, negative-test, spec, datatype
        self.line = line          # 1-based line of the opening fence in the .md
        self.text = text
        self.match = match or []
        self.native = native
        self.extra = extra or {}  # further `; KEY: value` header lines


def parse_front_matter(lines):
    """
    Minimal front matter reader (no PyYAML dependency): returns
    (fields, spec_text, spec_line, end_index).  Only `native:` and a
    `spec: |` literal block are needed.
    """
    if not lines or lines[0].rstrip() != '---':
        return {}, None, None, 0

    fields = {}
    spec_lines = None
    spec_line = None
    i = 1
    while i < len(lines):
        raw = lines[i].rstrip('\n')
        if raw.rstrip() == '---':
            break
        if spec_lines is not None:
            if raw.startswith('  ') or raw.strip() == '':
                spec_lines.append(raw[2:] if raw.startswith('  ') else '')
                i += 1
                continue
            fields['spec'] = '\n'.join(spec_lines).rstrip() + '\n'
            spec_lines = None  # literal block ended, fall through to parse
        m = re.match(r'^(\w[\w-]*):\s*(.*)$', raw)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key == 'spec' and val in ('|', '|-', '|+'):
                spec_lines = []
                spec_line = i + 2  # first content line, 1-based
            else:
                # one pair of matching quotes, if any (not every quote char)
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                fields[key] = val
        i += 1
    if spec_lines is not None:
        fields['spec'] = '\n'.join(spec_lines).rstrip() + '\n'
    return fields, fields.get('spec'), spec_line, i + 1


def extract_from_file(md_path: Path):
    """Return (blocks, untested_count) for one Markdown file."""
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    blocks = []
    untested = 0

    fields, spec, spec_line, start = parse_front_matter(lines)
    if fields.get('native') and spec:
        blocks.append(Block('spec', spec_line, spec, native=fields['native']))
    if fields.get('datatype'):
        extra = {'DATATYPE': fields['datatype']}
        if fields.get('antiform-of'):
            extra['ANTIFORM-OF'] = fields['antiform-of']
        blocks.append(Block('datatype', 1, fields.get('sample', '') + '\n', extra=extra))

    pending = None  # (kind, match) from a doctest comment on previous line
    i = start
    while i < len(lines):
        stripped = lines[i].rstrip('\n').rstrip('\r')

        cm = _DOCTEST_COMMENT.match(stripped)
        if cm:
            pending = (cm.group('kind'), cm.group('match'))
            i += 1
            continue

        if _ANY_FENCE_OPEN.match(stripped):
            is_rebol = bool(_FENCE_OPEN.match(stripped))
            fence_line = i + 1
            body = []
            i += 1
            while i < len(lines) and not _FENCE_CLOSE.match(lines[i].rstrip('\n').rstrip('\r')):
                body.append(lines[i].rstrip('\n').rstrip('\r'))
                i += 1
            i += 1  # skip closing fence

            if not is_rebol:
                if pending and pending[0] != 'skip':
                    print(f"{md_path}:{fence_line}: doctest tag on a non-rebol fence",
                          file=sys.stderr)
                pending = None
                continue

            kind, match = pending if pending else (None, None)
            pending = None

            if kind == 'skip':
                continue
            if kind is None:
                first = next((b for b in body if b.strip()), '')
                if first.startswith('>>'):
                    kind = 'transcript'
                else:
                    untested += 1
                    continue

            phrases = [p.strip() for p in match.split('|')] if match else []
            phrases = [p for p in phrases if p]
            blocks.append(Block(kind, fence_line, '\n'.join(body) + '\n', match=phrases))
            continue

        pending = None  # any other line clears a pending tag
        i += 1

    return blocks, untested


def render(block: Block, source: str) -> str:
    out = [
        '; AUTO-GENERATED by tools/extract-doctests.py -- DO NOT EDIT',
        f'; SOURCE: {source}:{block.line}',
        f'; KIND: {block.kind}',
    ]
    if block.native:
        out.append(f'; NATIVE: {block.native}')
    for key, val in block.extra.items():
        out.append(f'; {key}: {val}')
    for phrase in block.match:
        out.append(f'; MATCH-ERROR-TEXT: {phrase}')
    out.append(';---')
    return '\n'.join(out) + '\n' + block.text


def run(docs_dir: Path, out_dir: Path, quiet=False):
    """Extract everything.  Returns (page_dirs, total_blocks, untested)."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    md_files = sorted(
        p for p in docs_dir.rglob('*.md')
        if p.name.upper() != 'README.MD'
        and not any(part.startswith(('_', '.')) for part in p.relative_to(docs_dir).parts)
    )

    page_dirs = []
    total = 0
    untested_total = 0
    for md_path in md_files:
        rel = md_path.relative_to(docs_dir).as_posix()
        blocks, untested = extract_from_file(md_path)
        untested_total += untested
        if untested and not quiet:
            print(f"  note: {rel} has {untested} untagged rebol block(s), not tested")
        if not blocks:
            continue
        page_dir = out_dir / rel[:-3].replace('/', '--')
        page_dir.mkdir(parents=True)
        for n, block in enumerate(blocks, 1):
            dest = page_dir / f'{n:03d}-{block.kind}.r'
            with open(dest, 'w', encoding='utf-8', newline='\n') as f:
                f.write(render(block, rel))
        if not quiet:
            print(f"  extracted {len(blocks)} block(s) from {rel}")
        page_dirs.append(page_dir)
        total += len(blocks)

    return page_dirs, total, untested_total


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root = Path(__file__).resolve().parent.parent
    parser.add_argument('--docs-dir', default=str(root / 'docs'))
    parser.add_argument('--out-dir', default=str(root / 'build' / 'doctests'))
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.is_dir():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1

    _, total, untested = run(docs_dir, Path(args.out_dir).resolve())
    print(f"Wrote {total} doctest block(s); {untested} untagged rebol block(s) untested.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
