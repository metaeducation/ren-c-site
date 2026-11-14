# ren-c-site

Source for the REVOLT documentation website (REVOLT is the new name of
Ren-C; the repositories keep the old name).  Every example on the site is
run against a current REVOLT interpreter before the site deploys, including
the ones that are supposed to fail.

| Path | What |
|---|---|
| `docs/` | The site (Jekyll + just-the-docs).  See `docs/README.md` for how to write tested examples. |
| `tools/extract-doctests.py` | Pulls tagged/transcript ```` ```rebol ```` blocks out of the Markdown (same tag vocabulary as the Needful docs). |
| `tools/doctest-runner.r` | Ren-C script that runs the extracted blocks and checks results, errors, and native specs. |
| `tools/run-doctests.py` | Runs extraction, then the runner once per page.  Exit code 0 means everything matched. |
| `.github/workflows/pages.yml` | Installs the interpreter (`metaeducation/ren-c-action`), runs the tests, builds and deploys. |

```sh
python tools/run-doctests.py --r3 path/to/r3
```
