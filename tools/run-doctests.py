#!/usr/bin/env python3
"""
run-doctests.py - Extract the examples from docs/ and run them through Ren-C

Extracts with tools/extract-doctests.py, then runs tools/doctest-runner.r
once per documentation page (one interpreter process per page, so a crash
or stray state in one page can't affect another).

Exit code is 0 only if every block on every page passed.  If the runner
doesn't get as far as printing its summary line, that is reported as the
runner (or interpreter) failing, as distinct from an example failing.

The interpreter is found from --r3, then the R3 environment variable, then
`r3` on the PATH (which is where metaeducation/ren-c-action puts it).

Usage:
    python tools/run-doctests.py
    python tools/run-doctests.py --r3 C:/Projects/ren-c/build/r3.exe
    python tools/run-doctests.py --page reduce      # only pages matching
"""

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / 'tools'


def load_extractor():
    spec = importlib.util.spec_from_file_location(
        'extract_doctests', TOOLS / 'extract-doctests.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_r3(explicit):
    for candidate in (explicit, os.environ.get('R3')):
        if candidate:
            return candidate
    return shutil.which('r3') or shutil.which('r3.exe')


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--r3', help='path to the Ren-C interpreter')
    parser.add_argument('--docs-dir', default=str(ROOT / 'docs'))
    parser.add_argument('--out-dir', default=str(ROOT / 'build' / 'doctests'))
    parser.add_argument('--page', help='only run pages whose name contains this')
    parser.add_argument('--timeout', type=int, default=300,
                        help='seconds allowed per page (default 300)')
    args = parser.parse_args()

    r3 = find_r3(args.r3)
    if not r3:
        print("ERROR: no Ren-C interpreter found (use --r3, R3=..., or put r3 on PATH)",
              file=sys.stderr)
        return 2

    extractor = load_extractor()
    page_dirs, total, untested = extractor.run(
        Path(args.docs_dir).resolve(), Path(args.out_dir).resolve(), quiet=True)

    if args.page:
        page_dirs = [d for d in page_dirs if args.page in d.name]

    print(f"Interpreter: {r3}")
    print(f"{total} block(s) extracted from {len(page_dirs)} page(s); "
          f"{untested} untagged rebol block(s) untested")
    print()

    runner = TOOLS / 'doctest-runner.r'
    failed_pages = []
    for page_dir in page_dirs:
        files = sorted(page_dir.glob('*.r'))
        print(f"=== {page_dir.name} ===", flush=True)
        try:
            proc = subprocess.run(
                [r3, str(runner)] + [str(f) for f in files],
                capture_output=True, text=True, encoding='utf-8',
                errors='replace', timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT after {args.timeout}s")
            failed_pages.append(page_dir.name)
            continue

        sys.stdout.write(proc.stdout)
        if proc.stderr.strip():
            sys.stdout.write(proc.stderr)
        # The runner's last line is its summary.  Without it, the runner
        # itself died (a PANIC in the runner also exits with code 1, so the
        # exit code alone can't tell a failed example from a broken run).
        #
        finished = any(line.startswith('== ') and ' passed, ' in line
                       for line in proc.stdout.splitlines()[-3:])
        if not finished:
            print(f"RUNNER DID NOT FINISH (exit code {proc.returncode})")
            failed_pages.append(page_dir.name)
        elif proc.returncode != 0:
            failed_pages.append(page_dir.name)
        print(flush=True)

    if failed_pages:
        print(f"FAILED pages: {', '.join(failed_pages)}")
        return 1
    print("All documentation examples behave as documented.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
