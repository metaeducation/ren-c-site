#!/usr/bin/env python3
"""
check-text.py - Fail if the site's text files break its formatting rules

The rules:

* Plain ASCII punctuation: ' and " rather than curly quotes, -- rather
  than a dash character, ... rather than an ellipsis.  (_config.yml stops
  kramdown from converting them when the site is built; this catches them
  when they're typed or pasted in directly.)  Emoji and other non-ASCII
  characters are allowed; only the punctuation in FORBIDDEN is reported.

* Line feeds only: no carriage returns (CRLF or lone CR line endings).

* No tab characters.

Usage: python3 tools/check-text.py [path ...]
       (default: docs/, tools/, .github/ and README.md)

Exits with status 1 and a list of file:line:column if anything is found.
"""

import sys
from pathlib import Path

FORBIDDEN = {
    chr(0x2018): ("left single quote", "'"),
    chr(0x2019): ("right single quote", "'"),
    chr(0x201A): ("low single quote", "'"),
    chr(0x201B): ("reversed single quote", "'"),
    chr(0x201C): ("left double quote", '"'),
    chr(0x201D): ("right double quote", '"'),
    chr(0x201E): ("low double quote", '"'),
    chr(0x201F): ("reversed double quote", '"'),
    chr(0x2032): ("prime", "'"),
    chr(0x2033): ("double prime", '"'),
    chr(0x2010): ("hyphen", "-"),
    chr(0x2011): ("non-breaking hyphen", "-"),
    chr(0x2012): ("figure dash", "-"),
    chr(0x2013): ("en dash", "--"),
    chr(0x2014): ("em dash", "--"),
    chr(0x2015): ("horizontal bar", "--"),
    chr(0x2212): ("minus sign", "-"),
    chr(0x2026): ("ellipsis", "..."),
    chr(0x00AB): ("left guillemet", "<<"),
    chr(0x00BB): ("right guillemet", ">>"),
    chr(0x2039): ("single left guillemet", "<"),
    chr(0x203A): ("single right guillemet", ">"),
    chr(0x00A0): ("non-breaking space", "a space"),
    '\t': ("tab", "spaces"),
}

TEXT_SUFFIXES = {
    '.md', '.html', '.yml', '.yaml', '.scss', '.css', '.js', '.r', '.py',
    '.txt', '.svg',
}

SKIP_DIRS = {'_site', '.jekyll-cache', '.sass-cache', 'node_modules', '__pycache__', '.git'}

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ROOTS = [REPO / 'docs', REPO / 'tools', REPO / '.github', REPO / 'README.md']


def check_file(path: Path):
    data = path.read_bytes()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return [(path, 0, 0, "file is not valid UTF-8", None)]

    problems = []
    for lineno, line in enumerate(text.split('\n'), 1):
        for col, ch in enumerate(line, 1):
            if ch in FORBIDDEN:
                name, fix = FORBIDDEN[ch]
                problems.append((path, lineno, col, name, fix))
            elif ch == '\r':
                at_end = (col == len(line))
                name = "CRLF line ending" if at_end else "carriage return"
                problems.append((path, lineno, col, name, "LF only"))
    return problems


def files_under(root: Path):
    if root.is_file():
        yield root
        return
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def main(argv):
    roots = [Path(a) for a in argv[1:]] or [r for r in DEFAULT_ROOTS if r.exists()]
    problems = []
    checked = 0
    for root in roots:
        for path in files_under(root):
            checked += 1
            problems.extend(check_file(path))

    for path, lineno, col, name, fix in problems:
        hint = f" (use {fix})" if fix else ""
        print(f"{path}:{lineno}:{col}: {name}{hint}")

    if problems:
        print(f"\n{len(problems)} problem(s) found in {checked} files checked.  The"
              " site's text uses ASCII punctuation, LF line endings and no tabs.")
        return 1
    print(f"{checked} files checked: ASCII punctuation, LF line endings, no tabs.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
