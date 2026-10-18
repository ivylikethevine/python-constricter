# Corpus runs

What each constricter version found and fixed on the corpus: CPython's standard library and the
pinned `corpus` packages, at every level with `all-scopes`. Recorded by the corpus runner
(`tests/corpus/runs/release.toml`); a section per version, added when the version goes up (see
[CONTRIBUTING](CONTRIBUTING.md)).

## Test suites

Each Python 3 corpus package's own tests, from its source at the corpus's pinned tag with its test
dependencies as its CI installs them (`tests/corpus/corpus_suite.py`; `tests/corpus/corpora.toml`
says which tests and why), as released and after fixing its source at `suffocate` with `all-scopes`,
Unreleased, without `member` (Python 3.14.7):

| Package    | Version | Released                                                  | After `--fix`                           | After `--fix --unsafe-fixes`   |
| ---------- | ------- | --------------------------------------------------------- | --------------------------------------- | ------------------------------ |
| pydantic   | 2.13.5  | 6,439 passed, 329 skipped, 27 xfailed                     | the same (73 files changed, +239 lines) | the same (79 files, +332)      |
| sqlalchemy | 2.0.54  | 26,643 passed, 985 skipped                                | the same (161 files, +333)              | the same (188 files, +436)     |
| django     | 5.2.17  | 17,578 run, 1,149 skipped, 5 expected failures, 1 failure | the same (389 files, +288)              | the same (543 files, +495)     |
| pandas     | 3.0.6   | 165,407 passed, 24,659 skipped, 753 xfailed, 84 xpassed   | the same (1,036 files, +2,104)          | the same (1,190 files, +2,808) |

django's one failure is a message check that fails as released too (this machine's `msgfmt` words
the error differently). pandas runs its CI's selection (not `slow`, `network` or `single_cpu`).

A local's annotation is never evaluated, so the tests can't catch a wrong one:
`corpus_suite.py --types` runs each package's own type checker as its CI does, before and after, and
traces each error it didn't have as released to the fix (and so the mechanism) behind it. Django's
CI has none. On 0.2.4, and since (Unreleased: see [FIXES.md](FIXES.md#what-a-type-checker-sees)):

| Package    | Checker                            | Released errors | New after `--fix` | New after `--fix --unsafe-fixes` |
| ---------- | ---------------------------------- | --------------: | ----------------: | -------------------------------: |
| pydantic   | `pyright pydantic`                 |               0 |         18, now 0 |                        20, now 0 |
| sqlalchemy | `mypy noxfile.py ./lib/sqlalchemy` |               0 |         61, now 0 |                        76, now 0 |
| pandas     | mypy and pyright, as configured    |             259 |        117, now 0 |                       165, now 1 |

`--types --infer-with CHECKERS` adds a run with the checkers' hints' fixes
(`--fix --unsafe-fixes --infer-with CHECKERS`), here basedpyright's and ty's. New errors,
Unreleased:

| Package    | Released errors | After `--fix` | After `--fix --unsafe-fixes` | With the hints' fixes |
| ---------- | --------------: | ------------: | ---------------------------: | --------------------: |
| pydantic   |               0 |             0 |                            0 |                     6 |
| sqlalchemy |               0 |             0 |                            0 |                    10 |
| pandas     |             259 |             0 |                            1 |                    73 |

Each Pyright run reads the checkout's own settings (`--project .`). pandas's one after
`--fix --unsafe-fixes` is a guess's (`oindex: Index | None`, by an unannotated method's `return`s).
With the hints' fixes, pandas's 73 are 55 a hint's own fix's (`checker`), 6 untraced and 12 other
mechanisms' (one without the hints), sqlalchemy's 10 are 7, 2 and 1, and pydantic's 6 are 5 and one
other mechanism's; pandas had 444 before a hint was held to what its function does with the name
(see [FIXES.md](FIXES.md#a-type-checkers-types---infer-with)). The checkers' hints vary from run to
run: one function's 13 errors came and went between runs of the same code. basedpyright's server
hangs twice on `pandas/tests/apply/test_series_apply.py` (on `np.array([np.sum, np.mean])`, as its
command line does), which has no hints from it.

Earlier suites, on 0.2.4-rc.5:

| Package  | Version | Released                                      | After `--fix`                          | After `--fix --unsafe-fixes`         |
| -------- | ------- | --------------------------------------------- | -------------------------------------- | ------------------------------------ |
| flask    | 3.1.3   | 490 passed                                    | the same (16 files changed, +59 lines) | the same (17 files, +74)             |
| fastapi  | 0.141.1 | 3,341 passed, 18 skipped, 4 xfailed, 1 failed | the same (16 files, +154)              | the same (19 files, +185)            |
| requests | 2.34.2  | 617 passed, 15 skipped, 1 xfailed             | —                                      | the same (by hand, on 0.2.3's fixes) |

fastapi's one failure is its CLI test, which fails as released too (it looks for a path this
checkout doesn't have).

## Super corpora

The run `0.3.7-rc.1` (`python -m tests.corpus`) on super: constricter 0.3.7 (`1427ca904b7f`), Python
3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own, started once the CPUs
it's expected to keep busy and the memory it's expected to hold are free. The run took 87 minutes.
Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter    | Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ------------------ | -------- | -------------- | ----: | --------------: | ------------: | -------: | -------------: | -----------: | ---------: | --------: | -------: | ------: |
| standard library   | 3.14.7   | 0.3.7-rc.1+dev | 1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |         14 |         8 |        0 | 113,750 |
| django             | 5.2.17   | 0.3.7-rc.1+dev |   883 |           9,921 |         2,167 |        0 |          5,081 |            0 |          0 |         1 |        0 |  17,170 |
| sqlalchemy         | 2.0.54   | 0.3.7-rc.1+dev |   257 |           8,504 |         1,567 |        0 |          2,339 |          551 |        124 |         1 |        1 |  13,087 |
| pydantic           | 2.13.5   | 0.3.7-rc.1+dev |   105 |           2,023 |           438 |        0 |            631 |          190 |         13 |         0 |        0 |   3,295 |
| pandas             | 3.0.6    | 0.3.7-rc.1+dev | 1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |          2 |         1 |        1 |  77,931 |
| twisted            | 12.3.0   | 0.3.7-rc.1+dev |   819 |          13,310 |         1,349 |        0 |          3,215 |            0 |          0 |         0 |        0 |  17,874 |
| pip                | 20.3.4   | 0.3.7-rc.1+dev |   366 |           5,902 |         1,150 |        0 |          1,872 |            0 |          0 |         0 |        0 |   8,924 |
| structlog          | 26.1.0   | 0.3.7-rc.1+dev |    21 |             156 |            47 |        0 |            113 |           12 |          1 |         0 |        0 |     329 |
| attrs              | 26.1.0   | 0.3.7-rc.1+dev |    13 |             285 |            50 |        0 |             58 |            2 |          0 |         1 |        0 |     396 |
| click              | 8.5.0    | 0.3.7-rc.1+dev |    17 |             481 |            58 |        0 |             69 |           28 |          1 |         0 |        0 |     637 |
| hypercorn          | 0.18.0   | 0.3.7-rc.1+dev |    39 |             220 |            67 |        0 |             68 |            8 |          0 |         0 |        0 |     363 |
| starlette          | 1.7.0    | 0.3.7-rc.1+dev |    36 |             499 |            99 |        0 |            146 |           18 |          0 |         0 |        0 |     762 |
| werkzeug           | 3.1.9    | 0.3.7-rc.1+dev |    52 |             835 |           235 |        0 |            223 |           15 |          1 |         0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | 0.3.7-rc.1+dev |    61 |           1,674 |           198 |        0 |            460 |            8 |          0 |         0 |        0 |   2,340 |
| httpx              | 0.28.1   | 0.3.7-rc.1+dev |    23 |             395 |           112 |        0 |             62 |            1 |          0 |         0 |        0 |     570 |
| black              | 26.10.0  | 0.3.7-rc.1+dev |    25 |             996 |           232 |        0 |             45 |            5 |          4 |         0 |        0 |   1,282 |
| fastapi            | 0.142.2  | 0.3.7-rc.1+dev |    52 |             586 |           105 |        0 |             51 |           98 |          5 |         0 |        0 |     845 |
| cattrs             | 26.2.1   | 0.3.7-rc.1+dev |    36 |             420 |            70 |        0 |             30 |            9 |          1 |         0 |        0 |     530 |
| pytest             | 9.1.1    | 0.3.7-rc.1+dev |    78 |           2,363 |           470 |        0 |            170 |           33 |          9 |         0 |        0 |   3,045 |
| botocore           | 1.43.108 | 0.3.7-rc.1+dev |    76 |           2,825 |           367 |        0 |            594 |            2 |          0 |         0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | 0.3.7-rc.1+dev |    45 |             363 |            71 |        0 |             55 |           11 |          4 |         0 |        0 |     504 |
| mcp                | 2.3.0    | 0.3.7-rc.1+dev |   124 |           1,356 |           173 |        0 |            191 |          105 |          8 |         0 |        0 |   1,833 |
| textual            | 8.2.8    | 0.3.7-rc.1+dev |   247 |           4,979 |           718 |        0 |            786 |           31 |         26 |         0 |        0 |   6,540 |
| pdm                | 2.29.2   | 0.3.7-rc.1+dev |   128 |           2,114 |           417 |        0 |            187 |           37 |          2 |         0 |        0 |   2,757 |
| strawberry-graphql | 0.332.0  | 0.3.7-rc.1+dev |   244 |           1,436 |           243 |        0 |            127 |          137 |          2 |         0 |        0 |   1,945 |
| pygments           | 2.21.0   | 0.3.7-rc.1+dev |   343 |           1,124 |           539 |        0 |          6,003 |            0 |          0 |         0 |        0 |   7,666 |
| streamlink         | 8.6.1    | 0.3.7-rc.1+dev |   227 |           2,080 |           310 |        0 |            639 |           37 |         11 |         0 |        0 |   3,077 |
| sphinx             | 9.1.0    | 0.3.7-rc.1+dev |   243 |           5,505 |         1,336 |        1 |          1,131 |           73 |         29 |         5 |        3 |   8,083 |
| tox                | 4.64.9   | 0.3.7-rc.1+dev |   129 |           1,369 |           286 |        0 |            107 |           18 |          5 |         0 |        0 |   1,785 |
| **Total**          |          | 0.3.7-rc.1+dev | 7,976 | 233,653 (77.3%) | 27,986 (9.3%) | 1 (0.0%) | 38,873 (12.9%) | 1,620 (0.5%) | 262 (0.1%) | 17 (0.0%) | 5 (0.0%) | 302,417 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | -------------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | 0.3.7-rc.1+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,329 (32.8%) |   6,433 (5.7%) | 12,373 (10.9%) |      0 |    0 |            0 |
| django             | 0.3.7-rc.1+dev |  0 / 17,170 |   15,002 / 2,168 |      17,170 / 0 |  17,170 / 0 |  2,618 (15.2%) |     630 (3.7%) |  2,701 (15.7%) |      0 |    0 |            0 |
| sqlalchemy         | 0.3.7-rc.1+dev |  0 / 12,411 |   10,843 / 2,244 |    12,411 / 676 |  13,087 / 0 |  1,668 (12.7%) |     320 (2.4%) |     962 (7.4%) |      0 |    0 |            0 |
| pydantic           | 0.3.7-rc.1+dev |   0 / 3,092 |      2,654 / 641 |     3,092 / 203 |   3,295 / 0 |  1,083 (32.9%) |     148 (4.5%) |    409 (12.4%) |      0 |    0 |            0 |
| pandas             | 0.3.7-rc.1+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,950 (21.8%) | 23,811 (30.6%) | 24,638 (31.6%) |      0 |    0 |            0 |
| twisted            | 0.3.7-rc.1+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,437 (13.6%) |  3,657 (20.5%) |  4,678 (26.2%) |      0 |    0 |            0 |
| pip                | 0.3.7-rc.1+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,253 (25.2%) |     425 (4.8%) |  1,136 (12.7%) |      0 |    0 |            0 |
| structlog          | 0.3.7-rc.1+dev |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |     98 (29.8%) |      15 (4.6%) |      27 (8.2%) |      0 |    0 |            0 |
| attrs              | 0.3.7-rc.1+dev |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |     94 (23.7%) |       9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| click              | 0.3.7-rc.1+dev |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |    285 (44.7%) |      28 (4.4%) |     67 (10.5%) |      0 |    0 |            0 |
| hypercorn          | 0.3.7-rc.1+dev |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |    135 (37.2%) |      20 (5.5%) |     57 (15.7%) |      0 |    0 |            0 |
| starlette          | 0.3.7-rc.1+dev |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |    311 (40.8%) |      56 (7.3%) |     97 (12.7%) |      0 |    0 |            0 |
| werkzeug           | 0.3.7-rc.1+dev |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |    530 (40.5%) |      65 (5.0%) |     128 (9.8%) |      0 |    0 |            0 |
| mkdocs             | 0.3.7-rc.1+dev |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |    811 (34.7%) |    379 (16.2%) |    472 (20.2%) |      0 |    0 |            0 |
| httpx              | 0.3.7-rc.1+dev |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |    235 (41.2%) |     57 (10.0%) |     73 (12.8%) |      0 |    0 |            0 |
| black              | 0.3.7-rc.1+dev |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |    712 (55.5%) |     124 (9.7%) |    163 (12.7%) |      0 |    0 |            0 |
| fastapi            | 0.3.7-rc.1+dev |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |    257 (30.4%) |      40 (4.7%) |      67 (7.9%) |      0 |    0 |            0 |
| cattrs             | 0.3.7-rc.1+dev |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |    106 (20.0%) |      35 (6.6%) |      46 (8.7%) |      0 |    0 |            0 |
| pytest             | 0.3.7-rc.1+dev |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |  1,344 (44.1%) |     160 (5.3%) |     285 (9.4%) |      0 |    0 |            0 |
| botocore           | 0.3.7-rc.1+dev |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |    547 (14.4%) |     166 (4.4%) |    591 (15.6%) |      0 |    0 |            0 |
| uvicorn            | 0.3.7-rc.1+dev |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |    231 (45.8%) |      29 (5.8%) |      43 (8.5%) |      0 |    0 |            0 |
| mcp                | 0.3.7-rc.1+dev |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |    691 (37.7%) |     156 (8.5%) |    235 (12.8%) |      0 |    0 |            0 |
| textual            | 0.3.7-rc.1+dev |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |  2,567 (39.3%) |     478 (7.3%) |    731 (11.2%) |      0 |    0 |            0 |
| pdm                | 0.3.7-rc.1+dev |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |  1,152 (41.8%) |     198 (7.2%) |    313 (11.4%) |      0 |    0 |            0 |
| strawberry-graphql | 0.3.7-rc.1+dev |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |    595 (30.6%) |     165 (8.5%) |    213 (11.0%) |      0 |    0 |            0 |
| pygments           | 0.3.7-rc.1+dev |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |     736 (9.6%) |      80 (1.0%) |     224 (2.9%) |      0 |    0 |            0 |
| streamlink         | 0.3.7-rc.1+dev |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |    674 (21.9%) |     108 (3.5%) |     232 (7.5%) |      0 |    0 |            0 |
| sphinx             | 0.3.7-rc.1+dev |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |  3,136 (38.8%) |     439 (5.4%) |    816 (10.1%) |      0 |    0 |            0 |
| tox                | 0.3.7-rc.1+dev |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |    942 (52.8%) |      79 (4.4%) |     134 (7.5%) |      0 |    0 |            0 |
| **Total**          | 0.3.7-rc.1+dev | 0 / 300,530 | 272,526 / 29,891 | 300,529 / 1,888 | 302,417 / 0 | 80,527 (26.6%) | 38,310 (12.7%) | 51,922 (17.2%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter    | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | -------------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | 0.3.7-rc.1+dev |              1.2% |         33.6% |            39.2% |                  44.4% | +32.5 pts, 32.8% of untyped | +43.2 pts, 43.7% of untyped |
| django             | 0.3.7-rc.1+dev |              0.0% |         15.3% |            18.9% |                  31.0% | +15.2 pts, 15.2% of untyped | +31.0 pts, 31.0% of untyped |
| sqlalchemy         | 0.3.7-rc.1+dev |             14.8% |         26.2% |            28.4% |                  32.8% | +11.4 pts, 13.4% of untyped | +18.1 pts, 21.2% of untyped |
| pydantic           | 0.3.7-rc.1+dev |             21.8% |         49.2% |            53.0% |                  59.6% | +27.4 pts, 35.0% of untyped | +37.7 pts, 48.3% of untyped |
| pandas             | 0.3.7-rc.1+dev |              1.6% |         23.0% |            53.2% |                  54.2% | +21.4 pts, 21.8% of untyped | +52.6 pts, 53.5% of untyped |
| twisted            | 0.3.7-rc.1+dev |              0.0% |         13.6% |            34.1% |                  39.8% | +13.6 pts, 13.6% of untyped | +39.8 pts, 39.8% of untyped |
| pip                | 0.3.7-rc.1+dev |              1.5% |         26.4% |            31.1% |                  38.9% | +24.9 pts, 25.2% of untyped | +37.4 pts, 38.0% of untyped |
| structlog          | 0.3.7-rc.1+dev |             25.6% |         48.7% |            52.2% |                  55.1% | +23.1 pts, 31.0% of untyped | +29.4 pts, 39.6% of untyped |
| attrs              | 0.3.7-rc.1+dev |              0.8% |         24.5% |            26.8% |                  27.3% | +23.7 pts, 23.9% of untyped | +26.5 pts, 26.7% of untyped |
| click              | 0.3.7-rc.1+dev |             31.5% |         63.6% |            66.7% |                  71.1% | +32.1 pts, 46.9% of untyped | +39.7 pts, 57.9% of untyped |
| hypercorn          | 0.3.7-rc.1+dev |             32.4% |         58.1% |            61.9% |                  69.0% | +25.7 pts, 38.0% of untyped | +36.6 pts, 54.1% of untyped |
| starlette          | 0.3.7-rc.1+dev |             10.3% |         47.8% |            54.5% |                  59.5% | +37.5 pts, 41.8% of untyped | +49.2 pts, 54.8% of untyped |
| werkzeug           | 0.3.7-rc.1+dev |             14.3% |         49.4% |            53.7% |                  57.9% | +35.1 pts, 41.0% of untyped | +43.6 pts, 50.9% of untyped |
| mkdocs             | 0.3.7-rc.1+dev |              4.5% |         37.7% |            53.3% |                  57.1% | +33.2 pts, 34.8% of untyped | +52.5 pts, 55.0% of untyped |
| httpx              | 0.3.7-rc.1+dev |              6.3% |         45.0% |            54.4% |                  57.0% | +38.7 pts, 41.3% of untyped | +50.7 pts, 54.1% of untyped |
| black              | 0.3.7-rc.1+dev |             15.9% |         62.9% |            71.1% |                  73.7% | +47.1 pts, 55.9% of untyped | +57.8 pts, 68.7% of untyped |
| fastapi            | 0.3.7-rc.1+dev |             42.0% |         62.1% |            65.2% |                  67.3% | +20.1 pts, 34.6% of untyped | +25.3 pts, 43.7% of untyped |
| cattrs             | 0.3.7-rc.1+dev |              7.0% |         25.9% |            32.2% |                  34.2% | +19.0 pts, 20.4% of untyped | +27.2 pts, 29.2% of untyped |
| pytest             | 0.3.7-rc.1+dev |             12.1% |         51.5% |            56.1% |                  59.8% | +39.3 pts, 44.8% of untyped | +47.7 pts, 54.2% of untyped |
| botocore           | 0.3.7-rc.1+dev |              0.5% |         14.8% |            19.2% |                  30.4% | +14.4 pts, 14.4% of untyped | +29.9 pts, 30.0% of untyped |
| uvicorn            | 0.3.7-rc.1+dev |             23.6% |         59.7% |            64.2% |                  66.4% | +36.1 pts, 47.2% of untyped | +42.8 pts, 56.0% of untyped |
| mcp                | 0.3.7-rc.1+dev |             30.7% |         58.6% |            64.8% |                  68.0% | +27.8 pts, 40.2% of untyped | +37.3 pts, 53.8% of untyped |
| textual            | 0.3.7-rc.1+dev |             15.6% |         49.0% |            55.2% |                  58.5% | +33.4 pts, 39.6% of untyped | +43.0 pts, 50.9% of untyped |
| pdm                | 0.3.7-rc.1+dev |             11.7% |         49.1% |            55.6% |                  59.3% | +37.4 pts, 42.4% of untyped | +47.6 pts, 53.9% of untyped |
| strawberry-graphql | 0.3.7-rc.1+dev |             30.1% |         53.1% |            59.5% |                  61.3% | +23.0 pts, 32.9% of untyped | +31.3 pts, 44.7% of untyped |
| pygments           | 0.3.7-rc.1+dev |              0.0% |          9.6% |            10.6% |                  12.5% |   +9.6 pts, 9.6% of untyped | +12.5 pts, 12.5% of untyped |
| streamlink         | 0.3.7-rc.1+dev |             42.8% |         55.5% |            57.5% |                  59.9% | +12.7 pts, 22.3% of untyped | +17.1 pts, 29.9% of untyped |
| sphinx             | 0.3.7-rc.1+dev |             10.4% |         45.7% |            50.6% |                  54.8% | +35.2 pts, 39.3% of untyped | +44.4 pts, 49.6% of untyped |
| tox                | 0.3.7-rc.1+dev |             16.0% |         60.9% |            64.7% |                  67.3% | +44.9 pts, 53.5% of untyped | +51.3 pts, 61.1% of untyped |
| **Total**          | 0.3.7-rc.1+dev |              4.7% |         30.2% |            42.4% |                  46.7% | +25.5 pts, 26.8% of untyped | +42.0 pts, 44.1% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,329 |  37,329 |        |        |      0 |    0 | 38,658 |  115,001 |    55.8 |
| standard library   | likely             | 43,762 |  37,543 |  6,219 |        |      0 |    0 | 45,091 |  115,001 |    56.9 |
| standard library   | unsafe             | 49,702 |  37,337 |  6,211 |  6,154 |      0 |    0 | 51,031 |  115,001 |    44.8 |
| standard library   | infer-basedpyright | 58,068 |  37,345 |  6,715 | 14,008 |      0 |    9 | 59,397 |  115,001 |   501.5 |
| standard library   | infer-ty           | 55,832 |  37,346 |  6,681 | 11,805 |      0 |   39 | 57,161 |  115,001 |    86.7 |
| standard library   | infer-pyrefly      | 57,693 |  37,344 |  6,797 | 13,552 |      0 |   42 | 59,022 |  115,001 |    94.6 |
| django             | certain            |  2,618 |   2,618 |        |        |      0 |    0 |  2,620 |   17,171 |    11.9 |
| django             | likely             |  3,248 |   2,621 |    627 |        |      0 |    0 |  3,250 |   17,171 |    16.8 |
| django             | unsafe             |  5,319 |   2,618 |    626 |  2,075 |      0 |    0 |  5,321 |   17,171 |     9.9 |
| django             | infer-basedpyright |  5,776 |   2,617 |    642 |  2,517 |      0 |    6 |  5,778 |   17,171 |    39.7 |
| django             | infer-ty           |  5,559 |   2,619 |    635 |  2,305 |      0 |    7 |  5,561 |   17,171 |    26.7 |
| django             | infer-pyrefly      |  6,034 |   2,609 |    648 |  2,777 |      0 |   36 |  6,036 |   17,171 |    17.4 |
| django             | infer-trace        |  5,859 |   2,622 |    660 |  2,577 |      0 |    0 |  5,861 |   17,171 |    12.5 |
| sqlalchemy         | certain            |  1,668 |   1,668 |        |        |      0 |    0 |  3,817 |   14,568 |     9.3 |
| sqlalchemy         | likely             |  1,988 |   1,675 |    313 |        |      0 |    0 |  4,137 |   14,568 |    15.7 |
| sqlalchemy         | unsafe             |  2,630 |   1,668 |    312 |    650 |      0 |    0 |  4,779 |   14,568 |    10.1 |
| sqlalchemy         | infer-basedpyright |  3,509 |   1,669 |    356 |  1,484 |      0 |    0 |  5,658 |   14,568 |    33.9 |
| sqlalchemy         | infer-ty           |  3,446 |   1,669 |    342 |  1,435 |      0 |    4 |  5,595 |   14,568 |    25.9 |
| sqlalchemy         | infer-pyrefly      |  3,741 |   1,668 |    354 |  1,719 |      0 |    2 |  5,890 |   14,568 |    23.1 |
| sqlalchemy         | infer-trace        |  2,810 |   1,668 |    312 |    830 |      0 |    0 |  4,959 |   14,568 |     6.4 |
| pydantic           | certain            |  1,083 |   1,083 |        |        |      0 |    0 |  1,947 |    3,956 |     1.6 |
| pydantic           | likely             |  1,231 |   1,091 |    140 |        |      0 |    0 |  2,095 |    3,956 |     2.6 |
| pydantic           | unsafe             |  1,492 |   1,083 |    139 |    270 |      0 |    0 |  2,356 |    3,956 |     1.7 |
| pydantic           | infer-basedpyright |  1,788 |   1,084 |    143 |    561 |      0 |    0 |  2,652 |    3,956 |    25.0 |
| pydantic           | infer-ty           |  1,669 |   1,084 |    140 |    445 |      0 |    0 |  2,533 |    3,956 |     6.4 |
| pydantic           | infer-pyrefly      |  1,738 |   1,084 |    142 |    512 |      0 |    0 |  2,602 |    3,956 |     6.3 |
| pydantic           | infer-trace        |  1,493 |   1,083 |    139 |    271 |      0 |    0 |  2,357 |    3,956 |     1.7 |
| pandas             | certain            | 16,950 |  16,950 |        |        |      0 |    0 | 18,219 |   79,062 |    39.2 |
| pandas             | likely             | 40,761 |  17,133 | 23,628 |        |      0 |    0 | 42,030 |   79,062 |    89.9 |
| pandas             | unsafe             | 41,588 |  16,946 | 23,409 |  1,233 |      0 |    0 | 42,857 |   79,062 |    47.8 |
| pandas             | infer-basedpyright | 47,330 |  16,938 | 23,430 |  6,962 |      0 |   12 | 48,599 |   79,062 |   442.5 |
| pandas             | infer-ty           | 46,441 |  16,946 | 23,466 |  6,029 |      0 |    2 | 47,710 |   79,062 |   102.2 |
| pandas             | infer-pyrefly      | 47,047 |  16,949 | 23,472 |  6,626 |      0 |    4 | 48,316 |   79,062 |    65.3 |
| pandas             | infer-trace        | 42,980 |  16,946 | 23,370 |  2,664 |      0 |    9 | 44,249 |   79,062 |    31.5 |
| twisted            | certain            |  2,437 |   2,437 |        |        |      0 |    0 |  2,437 |   17,874 |     6.8 |
| twisted            | likely             |  6,094 |   2,561 |  3,533 |        |      0 |    0 |  6,094 |   17,874 |    10.4 |
| twisted            | unsafe             |  7,115 |   2,436 |  3,533 |  1,146 |      0 |    0 |  7,115 |   17,874 |     5.9 |
| twisted            | infer-basedpyright |  8,551 |   2,441 |  3,563 |  2,547 |      0 |    6 |  8,551 |   17,874 |    37.4 |
| twisted            | infer-ty           |  7,547 |   2,436 |  3,576 |  1,535 |      0 |    0 |  7,547 |   17,874 |    15.4 |
| twisted            | infer-pyrefly      |  7,514 |   2,436 |  3,566 |  1,512 |      0 |    0 |  7,514 |   17,874 |    13.9 |
| pip                | certain            |  2,253 |   2,253 |        |        |      0 |    0 |  2,390 |    9,064 |     5.2 |
| pip                | likely             |  2,678 |   2,266 |    412 |        |      0 |    0 |  2,815 |    9,064 |     8.2 |
| pip                | unsafe             |  3,389 |   2,253 |    412 |    724 |      0 |    0 |  3,526 |    9,064 |     6.0 |
| pip                | infer-basedpyright |  4,183 |   2,258 |    466 |  1,459 |      0 |    9 |  4,320 |    9,064 |    30.3 |
| pip                | infer-ty           |  3,716 |   2,255 |    436 |  1,025 |      0 |    9 |  3,853 |    9,064 |    14.1 |
| pip                | infer-pyrefly      |  3,885 |   2,255 |    446 |  1,184 |      0 |    0 |  4,022 |    9,064 |    12.2 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.4 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.7 |
| structlog          | unsafe             |    125 |      98 |     15 |     12 |      0 |    0 |    234 |      425 |     0.5 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     4.2 |
| structlog          | infer-ty           |    136 |      98 |     16 |     22 |      0 |    0 |    245 |      425 |     1.4 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     1.1 |
| structlog          | infer-trace        |    125 |      98 |     15 |     12 |      0 |    0 |    234 |      425 |     0.6 |
| attrs              | certain            |     94 |      94 |        |        |      0 |    0 |     97 |      396 |     0.5 |
| attrs              | likely             |    103 |      95 |      8 |        |      0 |    0 |    106 |      396 |     0.9 |
| attrs              | unsafe             |    105 |      94 |      8 |      3 |      0 |    0 |    108 |      396 |     0.8 |
| attrs              | infer-basedpyright |    132 |      94 |      8 |     30 |      0 |    0 |    135 |      396 |     4.4 |
| attrs              | infer-ty           |    116 |      94 |      8 |     14 |      0 |    0 |    119 |      396 |     2.1 |
| attrs              | infer-pyrefly      |    119 |      94 |      8 |     17 |      0 |    0 |    122 |      396 |     1.8 |
| attrs              | infer-trace        |    108 |      94 |      9 |      5 |      0 |    0 |    111 |      396 |     0.5 |
| click              | certain            |    285 |     285 |        |        |      0 |    0 |    564 |      887 |     0.4 |
| click              | likely             |    313 |     286 |     27 |        |      0 |    0 |    592 |      887 |     0.8 |
| click              | unsafe             |    352 |     285 |     27 |     40 |      0 |    0 |    631 |      887 |     0.5 |
| click              | infer-basedpyright |    434 |     286 |     30 |    118 |      0 |    0 |    713 |      887 |     6.6 |
| click              | infer-ty           |    449 |     286 |     25 |    138 |      0 |    0 |    728 |      887 |     2.0 |
| click              | infer-pyrefly      |    453 |     285 |     31 |    137 |      0 |    0 |    732 |      887 |     1.3 |
| click              | infer-trace        |    352 |     285 |     27 |     40 |      0 |    0 |    631 |      887 |     1.1 |
| hypercorn          | certain            |    135 |     135 |        |        |      0 |    0 |    305 |      525 |     0.6 |
| hypercorn          | likely             |    155 |     135 |     20 |        |      0 |    0 |    325 |      525 |     0.7 |
| hypercorn          | unsafe             |    192 |     135 |     20 |     37 |      0 |    0 |    362 |      525 |     0.5 |
| hypercorn          | infer-basedpyright |    214 |     135 |     21 |     58 |      0 |    0 |    384 |      525 |     3.2 |
| hypercorn          | infer-ty           |    229 |     135 |     21 |     73 |      0 |    0 |    399 |      525 |     1.5 |
| hypercorn          | infer-pyrefly      |    244 |     135 |     26 |     83 |      0 |    0 |    414 |      525 |     1.4 |
| hypercorn          | infer-trace        |    192 |     135 |     20 |     37 |      0 |    0 |    362 |      525 |     0.5 |
| starlette          | certain            |    311 |     311 |        |        |      0 |    0 |    396 |      829 |     0.8 |
| starlette          | likely             |    367 |     311 |     56 |        |      0 |    0 |    452 |      829 |     1.0 |
| starlette          | unsafe             |    408 |     311 |     56 |     41 |      0 |    0 |    493 |      829 |     0.9 |
| starlette          | infer-basedpyright |    487 |     311 |     56 |    120 |      0 |    0 |    572 |      829 |     3.5 |
| starlette          | infer-ty           |    491 |     311 |     55 |    125 |      0 |    0 |    576 |      829 |     1.5 |
| starlette          | infer-pyrefly      |    492 |     311 |     56 |    125 |      0 |    0 |    577 |      829 |     2.1 |
| starlette          | infer-trace        |    408 |     311 |     56 |     41 |      0 |    0 |    493 |      829 |     1.0 |
| werkzeug           | certain            |    530 |     530 |        |        |      0 |    0 |    746 |    1,509 |     1.1 |
| werkzeug           | likely             |    595 |     531 |     64 |        |      0 |    0 |    811 |    1,509 |     1.9 |
| werkzeug           | unsafe             |    658 |     530 |     64 |     64 |      0 |    0 |    874 |    1,509 |     0.8 |
| werkzeug           | infer-basedpyright |    780 |     530 |     76 |    174 |      0 |    0 |    996 |    1,509 |     4.8 |
| werkzeug           | infer-ty           |    802 |     530 |     79 |    193 |      0 |    0 |  1,018 |    1,509 |     2.0 |
| werkzeug           | infer-pyrefly      |    872 |     530 |     78 |    264 |      0 |    0 |  1,088 |    1,509 |     1.6 |
| werkzeug           | infer-trace        |    658 |     530 |     64 |     64 |      0 |    0 |    874 |    1,509 |     1.4 |
| mkdocs             | certain            |    811 |     811 |        |        |      0 |    0 |    922 |    2,443 |     0.9 |
| mkdocs             | likely             |  1,190 |     841 |    349 |        |      0 |    0 |  1,301 |    2,443 |     3.2 |
| mkdocs             | unsafe             |  1,283 |     811 |    349 |    123 |      0 |    0 |  1,394 |    2,443 |     1.9 |
| mkdocs             | infer-basedpyright |  1,386 |     811 |    356 |    219 |      0 |    0 |  1,497 |    2,443 |     7.2 |
| mkdocs             | infer-ty           |  1,422 |     811 |    361 |    250 |      0 |    0 |  1,533 |    2,443 |     2.5 |
| mkdocs             | infer-pyrefly      |  1,554 |     811 |    364 |    379 |      0 |    0 |  1,665 |    2,443 |     2.3 |
| mkdocs             | infer-trace        |  1,295 |     812 |    348 |    135 |      0 |    0 |  1,406 |    2,443 |     1.5 |
| httpx              | certain            |    235 |     235 |        |        |      0 |    0 |    273 |      607 |     1.2 |
| httpx              | likely             |    292 |     244 |     48 |        |      0 |    0 |    330 |      607 |     2.1 |
| httpx              | unsafe             |    308 |     235 |     48 |     25 |      0 |    0 |    346 |      607 |     1.6 |
| httpx              | infer-basedpyright |    409 |     235 |     53 |    121 |      0 |    0 |    447 |      607 |     4.6 |
| httpx              | infer-ty           |    381 |     235 |     52 |     94 |      0 |    0 |    419 |      607 |     2.3 |
| httpx              | infer-pyrefly      |    391 |     235 |     53 |    103 |      0 |    0 |    429 |      607 |     1.9 |
| httpx              | infer-trace        |    308 |     235 |     48 |     25 |      0 |    0 |    346 |      607 |     0.7 |
| black              | certain            |    712 |     712 |        |        |      0 |    0 |    952 |    1,513 |     0.6 |
| black              | likely             |    836 |     725 |    111 |        |      0 |    0 |  1,076 |    1,513 |     1.5 |
| black              | unsafe             |    875 |     712 |    111 |     52 |      0 |    0 |  1,115 |    1,513 |     1.2 |
| black              | infer-basedpyright |    946 |     712 |    110 |    124 |      0 |    0 |  1,186 |    1,513 |     6.9 |
| black              | infer-ty           |  1,068 |     712 |    115 |    241 |      0 |    0 |  1,308 |    1,513 |     3.1 |
| black              | infer-pyrefly      |  1,068 |     712 |    114 |    242 |      0 |    0 |  1,308 |    1,513 |     1.8 |
| black              | infer-trace        |    875 |     712 |    111 |     52 |      0 |    0 |  1,115 |    1,513 |     0.8 |
| fastapi            | certain            |    257 |     257 |        |        |      0 |    0 |    794 |    1,279 |     1.1 |
| fastapi            | likely             |    297 |     263 |     34 |        |      0 |    0 |    834 |    1,279 |     2.9 |
| fastapi            | unsafe             |    324 |     257 |     34 |     33 |      0 |    0 |    861 |    1,279 |     1.1 |
| fastapi            | infer-basedpyright |    350 |     257 |     33 |     60 |      0 |    0 |    887 |    1,279 |     7.1 |
| fastapi            | infer-ty           |    372 |     257 |     32 |     83 |      0 |    0 |    909 |    1,279 |     2.9 |
| fastapi            | infer-pyrefly      |    390 |     257 |     35 |     98 |      0 |    0 |    927 |    1,279 |     2.4 |
| fastapi            | infer-trace        |    324 |     257 |     34 |     33 |      0 |    0 |    861 |    1,279 |     1.2 |
| cattrs             | certain            |    106 |     106 |        |        |      0 |    0 |    145 |      559 |     1.0 |
| cattrs             | likely             |    141 |     113 |     28 |        |      0 |    0 |    180 |      559 |     1.4 |
| cattrs             | unsafe             |    152 |     109 |     27 |     16 |      0 |    0 |    191 |      559 |     1.0 |
| cattrs             | infer-basedpyright |    196 |     108 |     30 |     58 |      0 |    0 |    235 |      559 |     5.7 |
| cattrs             | infer-ty           |    190 |     106 |     28 |     56 |      0 |    0 |    229 |      559 |     1.8 |
| cattrs             | infer-pyrefly      |    177 |     108 |     29 |     40 |      0 |    0 |    216 |      559 |     1.9 |
| cattrs             | infer-trace        |    152 |     109 |     27 |     16 |      0 |    0 |    191 |      559 |     0.9 |
| pytest             | certain            |  1,344 |   1,344 |        |        |      0 |    0 |  1,759 |    3,418 |     2.5 |
| pytest             | likely             |  1,504 |   1,348 |    156 |        |      0 |    0 |  1,919 |    3,418 |     3.1 |
| pytest             | unsafe             |  1,629 |   1,344 |    156 |    129 |      0 |    0 |  2,044 |    3,418 |     2.6 |
| pytest             | infer-basedpyright |  1,982 |   1,343 |    174 |    465 |      0 |    0 |  2,397 |    3,418 |    14.1 |
| pytest             | infer-ty           |  1,988 |   1,343 |    176 |    469 |      0 |    0 |  2,403 |    3,418 |     6.8 |
| pytest             | infer-pyrefly      |  2,057 |   1,343 |    180 |    534 |      0 |    0 |  2,472 |    3,418 |     5.3 |
| pytest             | infer-trace        |  1,647 |   1,344 |    156 |    147 |      0 |    0 |  2,062 |    3,418 |     1.9 |
| botocore           | certain            |    547 |     547 |        |        |      0 |    0 |    565 |    3,806 |     2.3 |
| botocore           | likely             |    713 |     553 |    160 |        |      0 |    0 |    731 |    3,806 |     4.4 |
| botocore           | unsafe             |  1,138 |     545 |    160 |    433 |      0 |    0 |  1,156 |    3,806 |     2.8 |
| botocore           | infer-basedpyright |  1,293 |     540 |    163 |    590 |      0 |    0 |  1,311 |    3,806 |    11.6 |
| botocore           | infer-ty           |  1,200 |     545 |    161 |    494 |      0 |    3 |  1,218 |    3,806 |     6.0 |
| botocore           | infer-pyrefly      |  1,280 |     540 |    166 |    574 |      0 |    0 |  1,298 |    3,806 |     4.2 |
| botocore           | infer-trace        |  1,484 |     545 |    188 |    751 |      0 |    0 |  1,502 |    3,806 |     2.3 |
| uvicorn            | certain            |    231 |     231 |        |        |      0 |    0 |    382 |      640 |     1.1 |
| uvicorn            | likely             |    260 |     231 |     29 |        |      0 |    0 |    411 |      640 |     1.3 |
| uvicorn            | unsafe             |    274 |     231 |     29 |     14 |      0 |    0 |    425 |      640 |     0.9 |
| uvicorn            | infer-basedpyright |    347 |     231 |     32 |     84 |      0 |    0 |    498 |      640 |     6.3 |
| uvicorn            | infer-ty           |    354 |     232 |     29 |     93 |      0 |    0 |    505 |      640 |     2.9 |
| uvicorn            | infer-pyrefly      |    381 |     232 |     34 |    115 |      0 |    0 |    532 |      640 |     1.7 |
| uvicorn            | infer-trace        |    274 |     231 |     29 |     14 |      0 |    0 |    425 |      640 |     1.1 |
| mcp                | certain            |    691 |     691 |        |        |      0 |    0 |  1,454 |    2,483 |     1.4 |
| mcp                | likely             |    847 |     697 |    150 |        |      0 |    0 |  1,610 |    2,483 |     2.5 |
| mcp                | unsafe             |    926 |     691 |    150 |     85 |      0 |    0 |  1,689 |    2,483 |     1.3 |
| mcp                | infer-basedpyright |  1,057 |     691 |    162 |    204 |      0 |    0 |  1,820 |    2,483 |     8.7 |
| mcp                | infer-ty           |  1,160 |     692 |    158 |    310 |      0 |    0 |  1,923 |    2,483 |     4.6 |
| mcp                | infer-pyrefly      |  1,207 |     692 |    155 |    360 |      0 |    0 |  1,970 |    2,483 |     3.2 |
| mcp                | infer-trace        |    926 |     691 |    150 |     85 |      0 |    0 |  1,689 |    2,483 |     1.1 |
| textual            | certain            |  2,567 |   2,567 |        |        |      0 |    0 |  3,761 |    7,677 |     3.4 |
| textual            | likely             |  3,045 |   2,596 |    449 |        |      0 |    0 |  4,239 |    7,677 |     4.4 |
| textual            | unsafe             |  3,298 |   2,567 |    448 |    283 |      0 |    0 |  4,492 |    7,677 |     2.4 |
| textual            | infer-basedpyright |  4,557 |   2,568 |    522 |  1,467 |      0 |   20 |  5,751 |    7,677 |    16.7 |
| textual            | infer-ty           |  4,641 |   2,568 |    529 |  1,544 |      0 |    0 |  5,835 |    7,677 |    10.0 |
| textual            | infer-pyrefly      |  3,762 |   2,568 |    470 |    724 |      0 |    0 |  4,956 |    7,677 |     7.0 |
| pdm                | certain            |  1,152 |   1,152 |        |        |      0 |    0 |  1,513 |    3,079 |     1.1 |
| pdm                | likely             |  1,350 |   1,165 |    185 |        |      0 |    0 |  1,711 |    3,079 |     2.7 |
| pdm                | unsafe             |  1,465 |   1,152 |    184 |    129 |      0 |    0 |  1,826 |    3,079 |     4.2 |
| pdm                | infer-basedpyright |  1,857 |   1,156 |    213 |    488 |      0 |    0 |  2,218 |    3,079 |     9.6 |
| pdm                | infer-ty           |  1,960 |   1,158 |    211 |    591 |      0 |    0 |  2,321 |    3,079 |     4.6 |
| pdm                | infer-pyrefly      |  2,015 |   1,158 |    217 |    640 |      0 |    0 |  2,376 |    3,079 |     3.6 |
| pdm                | infer-trace        |  1,465 |   1,152 |    184 |    129 |      0 |    0 |  1,826 |    3,079 |     1.7 |
| strawberry-graphql | certain            |    595 |     595 |        |        |      0 |    0 |  1,371 |    2,582 |     1.5 |
| strawberry-graphql | likely             |    760 |     597 |    163 |        |      0 |    0 |  1,536 |    2,582 |     2.5 |
| strawberry-graphql | unsafe             |    808 |     595 |    163 |     50 |      0 |    0 |  1,584 |    2,582 |     2.4 |
| strawberry-graphql | infer-basedpyright |    983 |     594 |    163 |    226 |      0 |    0 |  1,759 |    2,582 |    10.3 |
| strawberry-graphql | infer-ty           |  1,022 |     595 |    163 |    264 |      0 |    0 |  1,798 |    2,582 |     6.6 |
| strawberry-graphql | infer-pyrefly      |  1,018 |     595 |    165 |    258 |      0 |    0 |  1,794 |    2,582 |     4.1 |
| strawberry-graphql | infer-trace        |    808 |     595 |    163 |     50 |      0 |    0 |  1,584 |    2,582 |     1.3 |
| pygments           | certain            |    736 |     736 |        |        |      0 |    0 |    736 |    7,666 |     3.0 |
| pygments           | likely             |    816 |     739 |     77 |        |      0 |    0 |    816 |    7,666 |     3.4 |
| pygments           | unsafe             |    960 |     736 |     77 |    147 |      0 |    0 |    960 |    7,666 |     2.7 |
| pygments           | infer-basedpyright |  1,074 |     736 |     84 |    254 |      0 |    0 |  1,074 |    7,666 |    23.8 |
| pygments           | infer-ty           |  1,078 |     736 |     85 |    257 |      0 |    0 |  1,078 |    7,666 |     7.6 |
| pygments           | infer-pyrefly      |  1,139 |     736 |     85 |    318 |      0 |    2 |  1,139 |    7,666 |     5.8 |
| pygments           | infer-trace        |  1,071 |     731 |    101 |    239 |      0 |    0 |  1,071 |    7,666 |     3.1 |
| streamlink         | certain            |    674 |     674 |        |        |      0 |    0 |  2,936 |    5,291 |     1.5 |
| streamlink         | likely             |    782 |     677 |    105 |        |      0 |    0 |  3,044 |    5,291 |     2.8 |
| streamlink         | unsafe             |    906 |     674 |    105 |    127 |      0 |    0 |  3,168 |    5,291 |     1.8 |
| streamlink         | infer-basedpyright |  1,317 |     674 |    127 |    516 |      0 |    0 |  3,579 |    5,291 |    13.6 |
| streamlink         | infer-ty           |  1,469 |     674 |    138 |    657 |      0 |    0 |  3,731 |    5,291 |     5.5 |
| streamlink         | infer-pyrefly      |  1,567 |     674 |    153 |    740 |      0 |    0 |  3,829 |    5,291 |     5.0 |
| streamlink         | infer-trace        |    914 |     674 |    105 |    135 |      0 |    0 |  3,176 |    5,291 |     1.5 |
| sphinx             | certain            |  3,136 |   3,136 |        |        |      0 |    0 |  4,064 |    8,901 |     3.5 |
| sphinx             | likely             |  3,575 |   3,146 |    429 |        |      0 |    0 |  4,503 |    8,901 |     5.1 |
| sphinx             | unsafe             |  3,952 |   3,136 |    426 |    390 |      0 |    0 |  4,880 |    8,901 |     3.8 |
| sphinx             | infer-basedpyright |  4,735 |   3,141 |    455 |  1,139 |      0 |    0 |  5,663 |    8,901 |    18.4 |
| sphinx             | infer-ty           |  4,881 |   3,140 |    457 |  1,284 |      0 |    2 |  5,809 |    8,901 |    10.9 |
| sphinx             | infer-pyrefly      |  5,096 |   3,141 |    471 |  1,484 |      0 |    2 |  6,024 |    8,901 |     7.2 |
| sphinx             | infer-trace        |  3,952 |   3,136 |    426 |    390 |      0 |    0 |  4,880 |    8,901 |     3.4 |
| tox                | certain            |    942 |     942 |        |        |      0 |    0 |  1,278 |    2,098 |     1.1 |
| tox                | likely             |  1,021 |     943 |     78 |        |      0 |    0 |  1,357 |    2,098 |     3.0 |
| tox                | unsafe             |  1,076 |     942 |     78 |     56 |      0 |    0 |  1,412 |    2,098 |     1.5 |
| tox                | infer-basedpyright |  1,340 |     944 |     95 |    301 |      0 |    0 |  1,676 |    2,098 |     7.6 |
| tox                | infer-ty           |  1,375 |     944 |     95 |    336 |      0 |    0 |  1,711 |    2,098 |     5.6 |
| tox                | infer-pyrefly      |  1,425 |     944 |     95 |    386 |      0 |    0 |  1,761 |    2,098 |     3.9 |
| tox                | infer-trace        |  1,076 |     942 |     78 |     56 |      0 |    0 |  1,412 |    2,098 |     1.2 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 19,306 |  19,306 |        |        |
| certain            | stdlib                 | 14,533 |  14,533 |        |        |
| certain            | call                   |  6,669 |   6,669 |        |        |
| certain            | container+literal      |  4,553 |   4,553 |        |        |
| certain            | builtin                |  3,055 |   3,055 |        |        |
| certain            | loop                   |  2,748 |   2,748 |        |        |
| certain            | method                 |  2,431 |   2,431 |        |        |
| certain            | copy+loop              |  2,369 |   2,369 |        |        |
| certain            | container+literal+loop |  1,675 |   1,675 |        |        |
| certain            | open                   |  1,274 |   1,274 |        |        |
| certain            | literal+method         |  1,252 |   1,252 |        |        |
| certain            | returned               |    943 |     943 |        |        |
| likely             | constructor            | 28,592 |     244 | 28,348 |        |
| likely             | literal                | 19,309 |  19,309 |        |        |
| likely             | stdlib                 | 14,590 |  14,590 |        |        |
| likely             | call                   |  7,139 |   6,682 |    457 |        |
| likely             | container+literal      |  4,553 |   4,553 |        |        |
| likely             | method                 |  3,501 |   2,455 |  1,046 |        |
| likely             | builtin                |  3,055 |   3,055 |        |        |
| likely             | loop                   |  2,748 |   2,748 |        |        |
| likely             | copy+loop              |  2,719 |   2,382 |    337 |        |
| likely             | container+literal+loop |  1,675 |   1,675 |        |        |
| likely             | open                   |  1,274 |   1,274 |        |        |
| likely             | literal+method         |  1,252 |   1,252 |        |        |
| unsafe             | constructor            | 28,589 |     244 | 28,345 |        |
| unsafe             | literal                | 19,308 |  19,304 |        |      4 |
| unsafe             | stdlib                 | 14,905 |  14,535 |        |    370 |
| unsafe             | call                   |  7,101 |   6,669 |    432 |        |
| unsafe             | container+literal      |  4,553 |   4,553 |        |        |
| unsafe             | literal+member         |  4,143 |         |        |  4,143 |
| unsafe             | returned               |  3,518 |     945 |        |  2,573 |
| unsafe             | method                 |  3,438 |   2,431 |  1,007 |        |
| unsafe             | builtin                |  3,055 |   3,055 |        |        |
| unsafe             | loop                   |  2,748 |   2,748 |        |        |
| unsafe             | copy+loop              |  2,699 |   2,369 |    330 |        |
| unsafe             | container+literal+loop |  1,675 |   1,675 |        |        |
| infer-basedpyright | constructor            | 28,537 |     243 | 28,294 |        |
| infer-basedpyright | checker                | 19,343 |         |        | 19,343 |
| infer-basedpyright | literal                | 19,309 |  19,305 |        |      4 |
| infer-basedpyright | stdlib                 | 14,971 |  14,426 |        |    545 |
| infer-basedpyright | call                   |  7,214 |   6,664 |    550 |        |
| infer-basedpyright | container+literal      |  4,553 |   4,553 |        |        |
| infer-basedpyright | literal+member         |  4,142 |         |        |  4,142 |
| infer-basedpyright | returned               |  3,805 |     926 |        |  2,879 |
| infer-basedpyright | method                 |  3,622 |   2,431 |  1,191 |        |
| infer-basedpyright | copy+loop              |  3,161 |   2,373 |    788 |        |
| infer-basedpyright | builtin                |  3,055 |   3,055 |        |        |
| infer-basedpyright | loop                   |  2,748 |   2,748 |        |        |
| infer-ty           | constructor            | 28,538 |     244 | 28,294 |        |
| infer-ty           | literal                | 19,308 |  19,304 |        |      4 |
| infer-ty           | checker                | 15,517 |         |        | 15,517 |
| infer-ty           | stdlib                 | 14,980 |  14,444 |        |    536 |
| infer-ty           | call                   |  7,172 |   6,664 |    508 |        |
| infer-ty           | container+literal      |  4,553 |   4,553 |        |        |
| infer-ty           | literal+member         |  4,143 |         |        |  4,143 |
| infer-ty           | returned               |  3,760 |     946 |        |  2,814 |
| infer-ty           | method                 |  3,599 |   2,432 |  1,167 |        |
| infer-ty           | copy+loop              |  3,065 |   2,372 |    693 |        |
| infer-ty           | builtin                |  3,055 |   3,055 |        |        |
| infer-ty           | loop                   |  2,748 |   2,748 |        |        |
| infer-pyrefly      | constructor            | 28,532 |     243 | 28,289 |        |
| infer-pyrefly      | literal                | 19,308 |  19,304 |        |      4 |
| infer-pyrefly      | checker                | 18,821 |         |        | 18,821 |
| infer-pyrefly      | stdlib                 | 15,037 |  14,490 |        |    547 |
| infer-pyrefly      | call                   |  7,171 |   6,664 |    507 |        |
| infer-pyrefly      | container+literal      |  4,553 |   4,553 |        |        |
| infer-pyrefly      | literal+member         |  4,142 |         |        |  4,142 |
| infer-pyrefly      | returned               |  3,705 |     941 |        |  2,764 |
| infer-pyrefly      | method                 |  3,619 |   2,432 |  1,187 |        |
| infer-pyrefly      | copy+loop              |  3,121 |   2,372 |    749 |        |
| infer-pyrefly      | builtin                |  3,055 |   3,055 |        |        |
| infer-pyrefly      | loop                   |  2,748 |   2,748 |        |        |
| infer-trace        | constructor            | 21,072 |      12 | 21,060 |        |
| infer-trace        | literal                |  9,221 |   9,220 |        |      1 |
| infer-trace        | call                   |  6,620 |   6,192 |    428 |        |
| infer-trace        | method                 |  2,889 |   1,893 |    996 |        |
| infer-trace        | stdlib                 |  2,435 |   2,336 |        |     99 |
| infer-trace        | traced                 |  2,411 |         |        |  2,411 |
| infer-trace        | literal+member         |  2,401 |         |        |  2,401 |
| infer-trace        | container+literal      |  2,133 |   2,133 |        |        |
| infer-trace        | builtin                |  1,267 |   1,267 |        |        |
| infer-trace        | copy+loop              |  1,236 |   1,068 |    168 |        |
| infer-trace        | returned               |    835 |     308 |        |    527 |
| infer-trace        | loop                   |    832 |     832 |        |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  12,366 |  63,976 |        0 |
| django             |  17,169 |   2,701 |  11,850 |        0 |
| sqlalchemy         |  12,410 |     962 |   9,780 |        0 |
| pydantic           |   3,092 |     409 |   1,600 |        0 |
| pandas             |  77,793 |  24,637 |  36,206 |        0 |
| twisted            |  17,874 |   4,678 |  10,759 |        0 |
| pip                |   8,924 |   1,136 |   5,535 |        0 |
| structlog          |     316 |      27 |     191 |        0 |
| attrs              |     393 |      11 |     288 |        0 |
| click              |     608 |      67 |     256 |        0 |
| hypercorn          |     355 |      57 |     163 |        0 |
| starlette          |     744 |      97 |     336 |        0 |
| werkzeug           |   1,293 |     128 |     635 |        0 |
| mkdocs             |   2,332 |     472 |   1,049 |        0 |
| httpx              |     569 |      73 |     261 |        0 |
| black              |   1,273 |     163 |     398 |        0 |
| fastapi            |     742 |      67 |     418 |        0 |
| cattrs             |     520 |      38 |     378 |        0 |
| pytest             |   3,003 |     285 |   1,374 |        0 |
| botocore           |   3,786 |     591 |   2,648 |        0 |
| uvicorn            |     489 |      43 |     215 |        0 |
| mcp                |   1,720 |     235 |     794 |        0 |
| textual            |   6,483 |     731 |   3,185 |        0 |
| pdm                |   2,718 |     313 |   1,253 |        0 |
| strawberry-graphql |   1,806 |     213 |     998 |        0 |
| pygments           |   7,666 |     224 |   6,706 |        0 |
| streamlink         |   3,029 |     232 |   2,123 |        0 |
| sphinx             |   7,972 |     816 |   4,021 |        0 |
| tox                |   1,762 |     134 |     686 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library   |    4 |       40.26 |     17.25 |    1 |                       621.2 |     647.0 | hyperfine |
| django             |    4 |        7.89 |      3.29 |    1 |                       116.9 |     124.8 | hyperfine |
| sqlalchemy         |    4 |        6.55 |      2.93 |    1 |                        92.0 |      96.9 | hyperfine |
| pydantic           |    4 |        1.44 |      0.66 |    1 |                        21.3 |      23.6 | hyperfine |
| pandas             |    4 |       50.36 |     16.71 |    1 |                       766.3 |     785.8 | hyperfine |
| twisted            |    4 |        6.09 |      2.42 |    1 |                        90.1 |      96.3 | hyperfine |
| pip                |    4 |        4.04 |      1.68 |    1 |                        64.7 |      69.0 | hyperfine |
| structlog          |    4 |        0.22 |      0.23 |    1 |                         2.8 |       3.9 | hyperfine |
| attrs              |    4 |        0.19 |      0.27 |    1 |                         2.6 |       3.6 | hyperfine |
| click              |    4 |        0.36 |       0.3 |    1 |                         5.0 |       6.0 | hyperfine |
| hypercorn          |    4 |         0.3 |      0.24 |    1 |                         3.7 |       4.9 | hyperfine |
| starlette          |    4 |        0.38 |      0.29 |    1 |                         4.8 |       6.1 | hyperfine |
| werkzeug           |    4 |        0.66 |      0.36 |    1 |                         8.9 |      10.2 | hyperfine |
| mkdocs             |    4 |        0.75 |      0.48 |    1 |                        10.4 |      12.3 | hyperfine |
| httpx              |    4 |        0.31 |      0.25 |    1 |                         4.1 |       5.2 | hyperfine |
| black              |    4 |        0.46 |      0.28 |    1 |                         6.5 |       7.7 | hyperfine |
| fastapi            |    4 |        0.53 |      0.47 |    1 |                         7.8 |       9.3 | hyperfine |
| cattrs             |    4 |        0.32 |       0.3 |    1 |                         4.3 |       5.5 | hyperfine |
| pytest             |    4 |        1.24 |      0.73 |    1 |                        17.6 |      19.5 | hyperfine |
| botocore           |    4 |        1.61 |      0.74 |    1 |                        23.8 |      25.5 | hyperfine |
| uvicorn            |    4 |        0.38 |      0.27 |    1 |                         4.9 |       6.1 | hyperfine |
| mcp                |    4 |        0.94 |      0.51 |    1 |                        12.8 |      14.9 | hyperfine |
| textual            |    4 |        2.33 |      1.03 |    1 |                        33.5 |      36.7 | hyperfine |
| pdm                |    4 |        1.33 |      0.74 |    1 |                        18.4 |      21.3 | hyperfine |
| strawberry-graphql |    4 |         1.4 |      0.68 |    1 |                        19.2 |      22.5 | hyperfine |
| pygments           |    4 |        2.57 |      1.06 |    1 |                        46.8 |      49.5 | hyperfine |
| streamlink         |    4 |        1.84 |      0.79 |    1 |                        26.1 |      28.3 | hyperfine |
| sphinx             |    4 |        3.35 |      1.22 |    1 |                        49.7 |      51.1 | hyperfine |
| tox                |    4 |        0.94 |      0.44 |    1 |                        12.5 |      13.5 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                   tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | ----------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  460 | Ran 17578 tests: FAILED (failures=5, skipped=1129, expected failures=5) |   383.5 |     41.8 |
| django             | certain |    927 |    925 |        2 |                      |                                                                         |         |          |
| django             | likely  |    297 |    296 |        1 |                      |                                                                         |         |          |
| django             | guess   |    302 |    279 |       23 |                      |                                                                         |         |          |
| sqlalchemy         |         |        |        |          |                  177 |                                     1 failed, 26644 passed, 983 skipped |    91.8 |     83.5 |
| sqlalchemy         | certain |  1,041 |  1,021 |       20 |                      |                                                                         |         |          |
| sqlalchemy         | likely  |    167 |    163 |        4 |                      |                                                                         |         |          |
| sqlalchemy         | guess   |    124 |    122 |        2 |                      |                                                                         |         |          |
| pydantic           |         |        |        |          |                    1 |                                    6439 passed, 329 skipped, 27 xfailed |    29.1 |     24.2 |
| pydantic           | certain |    484 |    479 |        5 |                      |                                                                         |         |          |
| pydantic           | likely  |     53 |     53 |        0 |                      |                                                                         |         |          |
| pydantic           | guess   |     32 |     32 |        0 |                      |                                                                         |         |          |
| pandas             |         |        |        |          |                1,415 |                   165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |    91.9 |     83.7 |
| pandas             | certain | 12,892 | 12,813 |       79 |                      |                                                                         |         |          |
| pandas             | likely  | 20,112 | 20,047 |       65 |                      |                                                                         |         |          |
| pandas             | guess   |    833 |    785 |       48 |                      |                                                                         |         |          |
| structlog          |         |        |        |          |                    0 |                            1 failed, 883 passed, 37 skipped, 2 warnings |     1.9 |      1.4 |
| structlog          | certain |     60 |     60 |        0 |                      |                                                                         |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                         |         |          |
| structlog          | guess   |      5 |      5 |        0 |                      |                                                                         |         |          |
| attrs              |         |        |        |          |                    2 |                             1 failed, 1382 passed, 2 skipped, 2 xfailed |     2.5 |      1.9 |
| attrs              | certain |     73 |     73 |        0 |                      |                                                                         |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                         |         |          |
| attrs              | guess   |      1 |      1 |        0 |                      |                                                                         |         |          |
| click              |         |        |        |          |                    0 |                    1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     5.6 |      5.1 |
| click              | certain |    208 |    207 |        1 |                      |                                                                         |         |          |
| click              | likely  |     20 |     19 |        1 |                      |                                                                         |         |          |
| click              | guess   |     28 |     27 |        1 |                      |                                                                         |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                    2 failed, 194 passed |     7.2 |      6.7 |
| hypercorn          | certain |     64 |     64 |        0 |                      |                                                                         |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                         |         |          |
| hypercorn          | guess   |      9 |      9 |        0 |                      |                                                                         |         |          |
| starlette          |         |        |        |          |                    0 |                                       1271 passed, 2 skipped, 2 xfailed |     7.4 |      7.3 |
| starlette          | certain |    190 |    190 |        0 |                      |                                                                         |         |          |
| starlette          | likely  |     46 |     46 |        0 |                      |                                                                         |         |          |
| starlette          | guess   |     30 |     30 |        0 |                      |                                                                         |         |          |
| werkzeug           |         |        |        |          |                    0 |                                        980 passed, 1 skipped, 1 warning |     7.1 |      6.9 |
| werkzeug           | certain |    356 |    351 |        5 |                      |                                                                         |         |          |
| werkzeug           | likely  |     44 |     44 |        0 |                      |                                                                         |         |          |
| werkzeug           | guess   |     34 |     34 |        0 |                      |                                                                         |         |          |
| mkdocs             |         |        |        |          |                   12 |                 Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    10.3 |      9.7 |
| mkdocs             | certain |    629 |    628 |        1 |                      |                                                                         |         |          |
| mkdocs             | likely  |    324 |    324 |        0 |                      |                                                                         |         |          |
| mkdocs             | guess   |    107 |    107 |        0 |                      |                                                                         |         |          |
| httpx              |         |        |        |          |                    0 |                                        1 failed, 1416 passed, 1 skipped |     6.3 |      5.2 |
| httpx              | certain |    182 |    182 |        0 |                      |                                                                         |         |          |
| httpx              | likely  |     41 |     41 |        0 |                      |                                                                         |         |          |
| httpx              | guess   |     16 |     16 |        0 |                      |                                                                         |         |          |
| black              |         |        |        |          |                    0 |                                519 passed, 1 skipped, 9 subtests passed |     9.0 |      5.6 |
| black              | certain |    603 |    602 |        1 |                      |                                                                         |         |          |
| black              | likely  |     99 |     99 |        0 |                      |                                                                         |         |          |
| black              | guess   |     40 |     40 |        0 |                      |                                                                         |         |          |
| fastapi            |         |        |        |          |                    0 |                                      3551 passed, 17 skipped, 4 xfailed |    17.9 |     15.4 |
| fastapi            | certain |    215 |    215 |        0 |                      |                                                                         |         |          |
| fastapi            | likely  |     29 |     29 |        0 |                      |                                                                         |         |          |
| fastapi            | guess   |     24 |     24 |        0 |                      |                                                                         |         |          |
| cattrs             |         |        |        |          |                    0 |                                                  994 passed, 15 xfailed |    21.4 |     17.0 |
| cattrs             | certain |    100 |     98 |        2 |                      |                                                                         |         |          |
| cattrs             | likely  |     24 |     24 |        0 |                      |                                                                         |         |          |
| cattrs             | guess   |     12 |     12 |        0 |                      |                                                                         |         |          |
| pytest             |         |        |        |          |                   15 |                4105 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    44.7 |     20.1 |
| pytest             | certain |  1,077 |  1,064 |       13 |                      |                                                                         |         |          |
| pytest             | likely  |    121 |    120 |        1 |                      |                                                                         |         |          |
| pytest             | guess   |     99 |     99 |        0 |                      |                                                                         |         |          |
| botocore           |         |        |        |          |                  298 |                                       7 failed, 4593 passed, 96 skipped |    27.4 |     25.8 |
| botocore           | certain |    329 |    328 |        1 |                      |                                                                         |         |          |
| botocore           | likely  |    130 |    130 |        0 |                      |                                                                         |         |          |
| botocore           | guess   |     93 |     92 |        1 |                      |                                                                         |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                 1350 passed, 12 skipped |    42.0 |     29.0 |
| uvicorn            | certain |    168 |    164 |        4 |                      |                                                                         |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                         |         |          |
| uvicorn            | guess   |      7 |      7 |        0 |                      |                                                                         |         |          |
| mcp                |         |        |        |          |                    0 |                                       6095 passed, 8 skipped, 1 xfailed |    17.7 |     12.4 |
| mcp                | certain |    503 |    502 |        1 |                      |                                                                         |         |          |
| mcp                | likely  |    129 |    128 |        1 |                      |                                                                         |         |          |
| mcp                | guess   |     53 |     53 |        0 |                      |                                                                         |         |          |
| pdm                |         |        |        |          |                    0 |                                     1472 passed, 1 skipped, 60 warnings |    18.4 |     18.9 |
| pdm                | certain |    890 |    879 |       11 |                      |                                                                         |         |          |
| pdm                | likely  |    133 |    133 |        0 |                      |                                                                         |         |          |
| pdm                | guess   |     78 |     77 |        1 |                      |                                                                         |         |          |
| strawberry-graphql |         |        |        |          |                    0 | 51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    11.8 |     11.7 |
| strawberry-graphql | certain |    377 |    370 |        7 |                      |                                                                         |         |          |
| strawberry-graphql | likely  |     93 |     91 |        2 |                      |                                                                         |         |          |
| strawberry-graphql | guess   |     27 |     27 |        0 |                      |                                                                         |         |          |
| pygments           |         |        |        |          |                   87 |                                       1 failed, 5330 passed, 15 skipped |    17.6 |     10.5 |
| pygments           | certain |    291 |    291 |        0 |                      |                                                                         |         |          |
| pygments           | likely  |     59 |     59 |        0 |                      |                                                                         |         |          |
| pygments           | guess   |     58 |     58 |        0 |                      |                                                                         |         |          |
| streamlink         |         |        |        |          |                    8 |                                                 7248 passed, 36 skipped |    10.3 |     10.0 |
| streamlink         | certain |    267 |    266 |        1 |                      |                                                                         |         |          |
| streamlink         | likely  |     38 |     38 |        0 |                      |                                                                         |         |          |
| streamlink         | guess   |     36 |     36 |        0 |                      |                                                                         |         |          |
| sphinx             |         |        |        |          |                    0 |                          9 failed, 2393 passed, 22 skipped, 35 warnings |    18.8 |     11.4 |
| sphinx             | certain |  2,011 |  1,985 |       26 |                      |                                                                         |         |          |
| sphinx             | likely  |    340 |    339 |        1 |                      |                                                                         |         |          |
| sphinx             | guess   |    192 |    190 |        2 |                      |                                                                         |         |          |
| tox                |         |        |        |          |                    0 |                                       1 failed, 8547 passed, 31 skipped |    22.3 |     16.6 |
| tox                | certain |    714 |    711 |        3 |                      |                                                                         |         |          |
| tox                | likely  |     57 |     57 |        0 |                      |                                                                         |         |          |
| tox                | guess   |     27 |     26 |        1 |                      |                                                                         |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                | same as released | summary                                                              | new failures | gone | named |
| ------------------ | ------------------ | ---------------- | -------------------------------------------------------------------- | -----------: | ---: | ----: |
| django             | released           |                  | 1 errors, 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |              |      |       |
| django             | fix-certain        | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped           |            0 |    0 |     0 |
| django             | fix-likely         | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped           |            0 |    0 |     0 |
| django             | fix-unsafe         | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped           |            0 |    0 |     0 |
| django             | infer-basedpyright | True             | 1 errors, 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |            0 |    0 |     0 |
| django             | infer-pyrefly      | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped           |            0 |    0 |     0 |
| django             | infer-trace        | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped           |            0 |    0 |     0 |
| django             | infer-ty           | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped           |            0 |    0 |     0 |
| sqlalchemy         | released           |                  | 26,645 passed, 983 skipped                                           |              |      |       |
| sqlalchemy         | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | fix-unsafe         | True             | 26,645 passed, 983 skipped                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-basedpyright | True             | 26,645 passed, 983 skipped                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-pyrefly      | True             | 26,645 passed, 983 skipped                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-trace        | True             | 26,645 passed, 983 skipped                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-ty           | True             | 26,645 passed, 983 skipped                                           |            0 |    0 |     0 |
| pydantic           | released           |                  | 6,439 passed, 329 skipped, 27 xfailed                                |              |      |       |
| pydantic           | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pydantic           | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pydantic           | fix-unsafe         | True             | 6,439 passed, 329 skipped, 27 xfailed                                |            0 |    0 |     0 |
| pydantic           | infer-basedpyright | True             | 6,439 passed, 329 skipped, 27 xfailed                                |            0 |    0 |     0 |
| pydantic           | infer-pyrefly      | True             | 6,439 passed, 329 skipped, 27 xfailed                                |            0 |    0 |     0 |
| pydantic           | infer-trace        | True             | 6,439 passed, 329 skipped, 27 xfailed                                |            0 |    0 |     0 |
| pydantic           | infer-ty           | True             | 6,439 passed, 329 skipped, 27 xfailed                                |            0 |    0 |     0 |
| pandas             | released           |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |              |      |       |
| pandas             | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pandas             | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pandas             | fix-unsafe         | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |            0 |    0 |     0 |
| pandas             | infer-basedpyright | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |            0 |    0 |     0 |
| pandas             | infer-pyrefly      | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |            0 |    0 |     0 |
| pandas             | infer-trace        | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |            0 |    0 |     0 |
| pandas             | infer-ty           | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |            0 |    0 |     0 |
| structlog          | released           |                  | 884 passed, 37 skipped                                               |              |      |       |
| structlog          | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| structlog          | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| structlog          | fix-unsafe         | True             | 884 passed, 37 skipped                                               |            0 |    0 |     0 |
| structlog          | infer-basedpyright | True             | 884 passed, 37 skipped                                               |            0 |    0 |     0 |
| structlog          | infer-pyrefly      | True             | 884 passed, 37 skipped                                               |            0 |    0 |     0 |
| structlog          | infer-trace        | True             | 884 passed, 37 skipped                                               |            0 |    0 |     0 |
| structlog          | infer-ty           | True             | 884 passed, 37 skipped                                               |            0 |    0 |     0 |
| attrs              | released           |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |              |      |       |
| attrs              | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| attrs              | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| attrs              | fix-unsafe         | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |            0 |    0 |     0 |
| attrs              | infer-basedpyright | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |            0 |    0 |     0 |
| attrs              | infer-pyrefly      | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |            0 |    0 |     0 |
| attrs              | infer-trace        | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |            0 |    0 |     0 |
| attrs              | infer-ty           | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |            0 |    0 |     0 |
| click              | released           |                  | 1,991 passed, 24 skipped, 1 xfailed                                  |              |      |       |
| click              | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| click              | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| click              | fix-unsafe         | True             | 1,991 passed, 24 skipped, 1 xfailed                                  |            0 |    0 |     0 |
| click              | infer-basedpyright | True             | 1,991 passed, 24 skipped, 1 xfailed                                  |            0 |    0 |     0 |
| click              | infer-pyrefly      | True             | 1,991 passed, 24 skipped, 1 xfailed                                  |            0 |    0 |     0 |
| click              | infer-trace        | True             | 1,991 passed, 24 skipped, 1 xfailed                                  |            0 |    0 |     0 |
| click              | infer-ty           | True             | 1,991 passed, 24 skipped, 1 xfailed                                  |            0 |    0 |     0 |
| hypercorn          | released           |                  | 2 failed, 194 passed                                                 |              |      |       |
| hypercorn          | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | fix-unsafe         | True             | 2 failed, 194 passed                                                 |            0 |    0 |     0 |
| hypercorn          | infer-basedpyright | True             | 2 failed, 194 passed                                                 |            0 |    0 |     0 |
| hypercorn          | infer-pyrefly      | True             | 2 failed, 194 passed                                                 |            0 |    0 |     0 |
| hypercorn          | infer-trace        | True             | 2 failed, 194 passed                                                 |            0 |    0 |     0 |
| hypercorn          | infer-ty           | True             | 2 failed, 194 passed                                                 |            0 |    0 |     0 |
| starlette          | released           |                  | 1,271 passed, 2 skipped, 2 xfailed                                   |              |      |       |
| starlette          | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| starlette          | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| starlette          | fix-unsafe         | True             | 1,271 passed, 2 skipped, 2 xfailed                                   |            0 |    0 |     0 |
| starlette          | infer-basedpyright | True             | 1,271 passed, 2 skipped, 2 xfailed                                   |            0 |    0 |     0 |
| starlette          | infer-pyrefly      | True             | 1,271 passed, 2 skipped, 2 xfailed                                   |            0 |    0 |     0 |
| starlette          | infer-trace        | True             | 1,271 passed, 2 skipped, 2 xfailed                                   |            0 |    0 |     0 |
| starlette          | infer-ty           | True             | 1,271 passed, 2 skipped, 2 xfailed                                   |            0 |    0 |     0 |
| werkzeug           | released           |                  | 980 passed, 1 skipped                                                |              |      |       |
| werkzeug           | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | fix-unsafe         | True             | 980 passed, 1 skipped                                                |            0 |    0 |     0 |
| werkzeug           | infer-basedpyright | True             | 980 passed, 1 skipped                                                |            0 |    0 |     0 |
| werkzeug           | infer-pyrefly      | True             | 980 passed, 1 skipped                                                |            0 |    0 |     0 |
| werkzeug           | infer-trace        | True             | 980 passed, 1 skipped                                                |            0 |    0 |     0 |
| werkzeug           | infer-ty           | True             | 980 passed, 1 skipped                                                |            0 |    0 |     0 |
| mkdocs             | released           |                  | 2 errors, 2 failures, 724 ran, 4 skipped                             |              |      |       |
| mkdocs             | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | fix-unsafe         | True             | 2 errors, 2 failures, 724 ran, 4 skipped                             |            0 |    0 |     0 |
| mkdocs             | infer-basedpyright | True             | 2 errors, 2 failures, 724 ran, 4 skipped                             |            0 |    0 |     0 |
| mkdocs             | infer-pyrefly      | True             | 2 errors, 2 failures, 724 ran, 4 skipped                             |            0 |    0 |     0 |
| mkdocs             | infer-trace        | True             | 2 errors, 2 failures, 724 ran, 4 skipped                             |            0 |    0 |     0 |
| mkdocs             | infer-ty           | True             | 2 errors, 2 failures, 724 ran, 4 skipped                             |            0 |    0 |     0 |
| httpx              | released           |                  | 1 failed, 1,416 passed, 1 skipped                                    |              |      |       |
| httpx              | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| httpx              | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| httpx              | fix-unsafe         | True             | 1 failed, 1,416 passed, 1 skipped                                    |            0 |    0 |     0 |
| httpx              | infer-basedpyright | True             | 1 failed, 1,416 passed, 1 skipped                                    |            0 |    0 |     0 |
| httpx              | infer-pyrefly      | True             | 1 failed, 1,416 passed, 1 skipped                                    |            0 |    0 |     0 |
| httpx              | infer-trace        | True             | 1 failed, 1,416 passed, 1 skipped                                    |            0 |    0 |     0 |
| httpx              | infer-ty           | True             | 1 failed, 1,416 passed, 1 skipped                                    |            0 |    0 |     0 |
| black              | released           |                  | 519 passed, 1 skipped                                                |              |      |       |
| black              | fix-certain        | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | fix-likely         | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | fix-unsafe         | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-basedpyright | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-pyrefly      | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-trace        | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-ty           | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| fastapi            | released           |                  | 3,551 passed, 17 skipped, 4 xfailed                                  |              |      |       |
| fastapi            | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| fastapi            | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| fastapi            | fix-unsafe         | True             | 3,551 passed, 17 skipped, 4 xfailed                                  |            0 |    0 |     0 |
| fastapi            | infer-basedpyright | True             | 3,551 passed, 17 skipped, 4 xfailed                                  |            0 |    0 |     0 |
| fastapi            | infer-pyrefly      | True             | 3,551 passed, 17 skipped, 4 xfailed                                  |            0 |    0 |     0 |
| fastapi            | infer-trace        | True             | 3,551 passed, 17 skipped, 4 xfailed                                  |            0 |    0 |     0 |
| fastapi            | infer-ty           | True             | 3,551 passed, 17 skipped, 4 xfailed                                  |            0 |    0 |     0 |
| cattrs             | released           |                  | 994 passed, 15 xfailed                                               |              |      |       |
| cattrs             | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| cattrs             | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| cattrs             | fix-unsafe         | True             | 994 passed, 15 xfailed                                               |            0 |    0 |     0 |
| cattrs             | infer-basedpyright | True             | 994 passed, 15 xfailed                                               |            0 |    0 |     0 |
| cattrs             | infer-pyrefly      | True             | 994 passed, 15 xfailed                                               |            0 |    0 |     0 |
| cattrs             | infer-trace        | True             | 994 passed, 15 xfailed                                               |            0 |    0 |     0 |
| cattrs             | infer-ty           | True             | 994 passed, 15 xfailed                                               |            0 |    0 |     0 |
| pytest             | released           |                  | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed            |              |      |       |
| pytest             | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pytest             | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pytest             | fix-unsafe         | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed            |            0 |    0 |     0 |
| pytest             | infer-basedpyright | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed            |            0 |    0 |     0 |
| pytest             | infer-pyrefly      | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed            |            0 |    0 |     0 |
| pytest             | infer-trace        | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed            |            0 |    0 |     0 |
| pytest             | infer-ty           | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed            |            0 |    0 |     0 |
| botocore           | released           |                  | 7 failed, 4,593 passed, 96 skipped                                   |              |      |       |
| botocore           | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| botocore           | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| botocore           | fix-unsafe         | True             | 7 failed, 4,593 passed, 96 skipped                                   |            0 |    0 |     0 |
| botocore           | infer-basedpyright | True             | 7 failed, 4,593 passed, 96 skipped                                   |            0 |    0 |     0 |
| botocore           | infer-pyrefly      | True             | 7 failed, 4,593 passed, 96 skipped                                   |            0 |    0 |     0 |
| botocore           | infer-trace        | True             | 7 failed, 4,593 passed, 96 skipped                                   |            0 |    0 |     0 |
| botocore           | infer-ty           | True             | 7 failed, 4,593 passed, 96 skipped                                   |            0 |    0 |     0 |
| uvicorn            | released           |                  | 1,350 passed, 12 skipped                                             |              |      |       |
| uvicorn            | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | fix-unsafe         | True             | 1,350 passed, 12 skipped                                             |            0 |    0 |     0 |
| uvicorn            | infer-basedpyright | True             | 1,350 passed, 12 skipped                                             |            0 |    0 |     0 |
| uvicorn            | infer-pyrefly      | True             | 1,350 passed, 12 skipped                                             |            0 |    0 |     0 |
| uvicorn            | infer-trace        | True             | 1,350 passed, 12 skipped                                             |            0 |    0 |     0 |
| uvicorn            | infer-ty           | True             | 1,350 passed, 12 skipped                                             |            0 |    0 |     0 |
| mcp                | released           |                  | 6,095 passed, 8 skipped, 1 xfailed                                   |              |      |       |
| mcp                | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| mcp                | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| mcp                | fix-unsafe         | True             | 6,095 passed, 8 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| mcp                | infer-basedpyright | True             | 6,095 passed, 8 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| mcp                | infer-pyrefly      | True             | 6,095 passed, 8 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| mcp                | infer-trace        | True             | 6,095 passed, 8 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| mcp                | infer-ty           | True             | 6,095 passed, 8 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| pdm                | released           |                  | 1,472 passed, 1 skipped                                              |              |      |       |
| pdm                | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pdm                | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pdm                | fix-unsafe         | True             | 1,472 passed, 1 skipped                                              |            0 |    0 |     0 |
| pdm                | infer-basedpyright | True             | 1,472 passed, 1 skipped                                              |            0 |    0 |     0 |
| pdm                | infer-pyrefly      | True             | 1,472 passed, 1 skipped                                              |            0 |    0 |     0 |
| pdm                | infer-trace        | True             | 1,472 passed, 1 skipped                                              |            0 |    0 |     0 |
| pdm                | infer-ty           | True             | 1,472 passed, 1 skipped                                              |            0 |    0 |     0 |
| strawberry-graphql | released           |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |              |      |       |
| strawberry-graphql | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | fix-unsafe         | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |            0 |    0 |     0 |
| strawberry-graphql | infer-basedpyright | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |            0 |    0 |     0 |
| strawberry-graphql | infer-pyrefly      | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |            0 |    0 |     0 |
| strawberry-graphql | infer-trace        | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |            0 |    0 |     0 |
| strawberry-graphql | infer-ty           | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |            0 |    0 |     0 |
| pygments           | released           |                  | 1 failed, 5,330 passed, 15 skipped                                   |              |      |       |
| pygments           | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pygments           | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| pygments           | fix-unsafe         | True             | 1 failed, 5,330 passed, 15 skipped                                   |            0 |    0 |     0 |
| pygments           | infer-basedpyright | True             | 1 failed, 5,330 passed, 15 skipped                                   |            0 |    0 |     0 |
| pygments           | infer-pyrefly      | True             | 1 failed, 5,330 passed, 15 skipped                                   |            0 |    0 |     0 |
| pygments           | infer-trace        | True             | 1 failed, 5,330 passed, 15 skipped                                   |            0 |    0 |     0 |
| pygments           | infer-ty           | True             | 1 failed, 5,330 passed, 15 skipped                                   |            0 |    0 |     0 |
| streamlink         | released           |                  | 7,248 passed, 36 skipped                                             |              |      |       |
| streamlink         | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| streamlink         | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| streamlink         | fix-unsafe         | True             | 7,248 passed, 36 skipped                                             |            0 |    0 |     0 |
| streamlink         | infer-basedpyright | True             | 7,248 passed, 36 skipped                                             |            0 |    0 |     0 |
| streamlink         | infer-pyrefly      | True             | 7,248 passed, 36 skipped                                             |            0 |    0 |     0 |
| streamlink         | infer-trace        | True             | 7,248 passed, 36 skipped                                             |            0 |    0 |     0 |
| streamlink         | infer-ty           | True             | 7,248 passed, 36 skipped                                             |            0 |    0 |     0 |
| sphinx             | released           |                  | 10 failed, 2,392 passed, 22 skipped                                  |              |      |       |
| sphinx             | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| sphinx             | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| sphinx             | fix-unsafe         | True             | 10 failed, 2,392 passed, 22 skipped                                  |            0 |    0 |     0 |
| sphinx             | infer-basedpyright | True             | 10 failed, 2,392 passed, 22 skipped                                  |            0 |    0 |     0 |
| sphinx             | infer-pyrefly      | True             | 10 failed, 2,392 passed, 22 skipped                                  |            0 |    0 |     0 |
| sphinx             | infer-trace        | False            | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    1 |     0 |
| sphinx             | infer-ty           | False            | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    1 |     0 |
| tox                | released           |                  | 1 failed, 8,547 passed, 31 skipped                                   |              |      |       |
| tox                | fix-certain        | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| tox                | fix-likely         | True             | as fix-unsafe's (implied)                                            |            0 |    0 |     0 |
| tox                | fix-unsafe         | True             | 1 failed, 8,547 passed, 31 skipped                                   |            0 |    0 |     0 |
| tox                | infer-basedpyright | True             | 1 failed, 8,547 passed, 31 skipped                                   |            0 |    0 |     0 |
| tox                | infer-pyrefly      | True             | 1 failed, 8,547 passed, 31 skipped                                   |            0 |    0 |     0 |
| tox                | infer-trace        | True             | 1 failed, 8,547 passed, 31 skipped                                   |            0 |    0 |     0 |
| tox                | infer-ty           | True             | 1 failed, 8,547 passed, 31 skipped                                   |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                      change |
| ------------------ | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy         | released           |      9 |     |      |                                                             |
| sqlalchemy         | fix-certain        |      9 |   0 |    0 |    164 files changed, 1729 insertions(+), 1327 deletions(-) |
| sqlalchemy         | fix-likely         |      9 |   0 |    0 |    175 files changed, 2054 insertions(+), 1632 deletions(-) |
| sqlalchemy         | fix-unsafe         |      9 |   0 |    0 |    194 files changed, 2726 insertions(+), 2244 deletions(-) |
| sqlalchemy         | infer-basedpyright |     16 |   7 |    0 |    199 files changed, 3641 insertions(+), 3088 deletions(-) |
| sqlalchemy         | infer-pyrefly      |     58 |  49 |    0 |    201 files changed, 3931 insertions(+), 3123 deletions(-) |
| sqlalchemy         | infer-trace        |     15 |   6 |    0 |    196 files changed, 2956 insertions(+), 2408 deletions(-) |
| sqlalchemy         | infer-ty           |     12 |   3 |    0 |    198 files changed, 3589 insertions(+), 2914 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |      73 files changed, 1119 insertions(+), 804 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |      75 files changed, 1274 insertions(+), 933 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     77 files changed, 1547 insertions(+), 1175 deletions(-) |
| pydantic           | infer-basedpyright |      3 |   3 |    0 |     80 files changed, 1878 insertions(+), 1469 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     77 files changed, 1861 insertions(+), 1347 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     77 files changed, 1548 insertions(+), 1176 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     77 files changed, 1737 insertions(+), 1341 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    259 |   0 |    0 | 1067 files changed, 18245 insertions(+), 15225 deletions(-) |
| pandas             | fix-likely         |    259 |   0 |    0 | 1199 files changed, 42324 insertions(+), 38688 deletions(-) |
| pandas             | fix-unsafe         |    260 |   1 |    0 | 1202 files changed, 43193 insertions(+), 39437 deletions(-) |
| pandas             | infer-basedpyright |    297 |  38 |    0 | 1213 files changed, 49460 insertions(+), 45067 deletions(-) |
| pandas             | infer-pyrefly      |    384 | 125 |    0 | 1212 files changed, 48950 insertions(+), 44481 deletions(-) |
| pandas             | infer-trace        |    261 |   2 |    0 | 1205 files changed, 44633 insertions(+), 40796 deletions(-) |
| pandas             | infer-ty           |    341 |  82 |    0 | 1212 files changed, 48318 insertions(+), 44046 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |        14 files changed, 109 insertions(+), 80 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |        15 files changed, 124 insertions(+), 94 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 139 insertions(+), 105 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      9 |   1 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 139 insertions(+), 105 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 150 insertions(+), 115 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 290 insertions(+), 213 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 318 insertions(+), 241 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 357 insertions(+), 272 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 442 insertions(+), 347 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 461 insertions(+), 360 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 357 insertions(+), 272 deletions(-) |
| click              | infer-ty           |      5 |   5 |    0 |       15 files changed, 460 insertions(+), 358 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |        24 files changed, 149 insertions(+), 96 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 169 insertions(+), 109 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 146 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 236 insertions(+), 167 deletions(-) |
| hypercorn          | infer-pyrefly      |     14 |   2 |    0 |       26 files changed, 265 insertions(+), 172 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 146 deletions(-) |
| hypercorn          | infer-ty           |     14 |   2 |    0 |       25 files changed, 250 insertions(+), 174 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       29 files changed, 329 insertions(+), 248 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 386 insertions(+), 296 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-basedpyright |     12 |  12 |    0 |       33 files changed, 525 insertions(+), 408 deletions(-) |
| starlette          | infer-pyrefly      |     12 |  12 |    0 |       34 files changed, 518 insertions(+), 400 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-ty           |     12 |  12 |    0 |       33 files changed, 526 insertions(+), 407 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 542 insertions(+), 368 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 610 insertions(+), 416 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 676 insertions(+), 466 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 806 insertions(+), 572 deletions(-) |
| werkzeug           | infer-pyrefly      |      3 |   3 |    0 |       45 files changed, 898 insertions(+), 596 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 676 insertions(+), 466 deletions(-) |
| werkzeug           | infer-ty           |      1 |   1 |    0 |       45 files changed, 828 insertions(+), 575 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 235 insertions(+), 195 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 293 insertions(+), 238 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 309 insertions(+), 254 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       18 files changed, 417 insertions(+), 347 deletions(-) |
| httpx              | infer-pyrefly      |      2 |   2 |    0 |       17 files changed, 398 insertions(+), 311 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 309 insertions(+), 254 deletions(-) |
| httpx              | infer-ty           |      5 |   5 |    0 |       17 files changed, 388 insertions(+), 311 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       26 files changed, 239 insertions(+), 182 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       26 files changed, 275 insertions(+), 207 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-basedpyright |      7 |   7 |    0 |       29 files changed, 372 insertions(+), 283 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       29 files changed, 407 insertions(+), 306 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 380 insertions(+), 293 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 774 insertions(+), 519 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 933 insertions(+), 667 deletions(-) |
| mcp                | fix-unsafe         |      2 |   2 |    0 |      81 files changed, 1023 insertions(+), 735 deletions(-) |
| mcp                | infer-basedpyright |      4 |   4 |    0 |      82 files changed, 1158 insertions(+), 862 deletions(-) |
| mcp                | infer-pyrefly      |     10 |  10 |    0 |      85 files changed, 1347 insertions(+), 968 deletions(-) |
| mcp                | infer-trace        |      2 |   2 |    0 |      81 files changed, 1023 insertions(+), 735 deletions(-) |
| mcp                | infer-ty           |      4 |   4 |    0 |      84 files changed, 1306 insertions(+), 938 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |      129 files changed, 667 insertions(+), 471 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |      147 files changed, 840 insertions(+), 625 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |      151 files changed, 897 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-basedpyright |     16 |   6 |    0 |     154 files changed, 1095 insertions(+), 838 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     17 |   7 |    0 |     154 files changed, 1142 insertions(+), 862 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |      151 files changed, 897 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-ty           |     18 |   8 |    0 |     155 files changed, 1146 insertions(+), 872 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |     164 files changed, 1034 insertions(+), 532 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |     166 files changed, 1144 insertions(+), 625 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |     168 files changed, 1279 insertions(+), 739 deletions(-) |
| streamlink         | infer-basedpyright |      1 |   1 |    0 |    185 files changed, 1752 insertions(+), 1132 deletions(-) |
| streamlink         | infer-pyrefly      |     41 |  41 |    0 |    186 files changed, 2110 insertions(+), 1170 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |     168 files changed, 1288 insertions(+), 745 deletions(-) |
| streamlink         | infer-ty           |     22 |  22 |    0 |    185 files changed, 2002 insertions(+), 1130 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      3 |   0 |    0 |    194 files changed, 3207 insertions(+), 2162 deletions(-) |
| sphinx             | fix-likely         |      3 |   0 |    0 |    196 files changed, 3648 insertions(+), 2511 deletions(-) |
| sphinx             | fix-unsafe         |      3 |   0 |    0 |    212 files changed, 4040 insertions(+), 2829 deletions(-) |
| sphinx             | infer-basedpyright |      7 |   4 |    0 |    215 files changed, 4851 insertions(+), 3580 deletions(-) |
| sphinx             | infer-pyrefly      |     12 |   9 |    0 |    216 files changed, 5212 insertions(+), 3714 deletions(-) |
| sphinx             | infer-trace        |      3 |   0 |    0 |    212 files changed, 4040 insertions(+), 2829 deletions(-) |
| sphinx             | infer-ty           |     12 |   9 |    0 |    216 files changed, 4993 insertions(+), 3622 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step               | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check              |    44.5 |        93.6 |  2.1 |    3.77 |          3 |     4.51 | False |
| standard library   | fix-certain        |   111.6 |       257.8 |  2.3 |    5.18 |          3 |     5.67 | False |
| standard library   | fix-likely         |    92.9 |       279.4 |  3.0 |    7.83 |          3 |      8.8 | False |
| standard library   | fix-unsafe         |    78.3 |       222.3 |  2.8 |     5.9 |          3 |     6.55 | False |
| standard library   | infer-basedpyright |   619.4 |      1096.7 |  1.8 |   13.01 |          2 |     15.4 | False |
| standard library   | infer-ty           |   126.7 |       467.2 |  3.7 |   16.24 |          4 |    17.79 | False |
| standard library   | infer-pyrefly      |   136.2 |       473.0 |  3.5 |    18.9 |          4 |    19.54 | False |
| standard library   | census             |    27.8 |        27.3 |  1.0 |    0.51 |          3 |     4.51 | False |
| standard library   | coverage           |    10.8 |        31.9 |  3.0 |    1.63 |          3 |     2.06 | False |
| standard library   | timing             |   115.3 |       176.5 |  1.5 |    3.77 |         16 |     4.51 | False |
| django             | check              |     7.2 |        17.0 |  2.4 |    0.85 |          3 |     0.97 | False |
| django             | fix-certain        |    23.7 |        46.0 |  1.9 |    1.12 |          2 |     1.29 | False |
| django             | fix-likely         |    27.3 |        55.8 |  2.0 |    1.52 |          2 |      1.8 | False |
| django             | fix-unsafe         |    19.0 |        46.0 |  2.4 |    1.25 |          3 |     1.34 | False |
| django             | infer-basedpyright |    58.7 |       265.6 |  4.5 |    7.54 |          5 |     9.26 | False |
| django             | infer-ty           |    41.5 |       123.4 |  3.0 |    3.72 |          3 |     4.09 | False |
| django             | infer-pyrefly      |    28.5 |        90.7 |  3.2 |    4.21 |          3 |      4.3 | False |
| django             | census             |     3.0 |         2.9 |  1.0 |    0.09 |          3 |     0.97 | False |
| django             | coverage           |     2.6 |         5.1 |  2.0 |    0.34 |          1 |     0.09 | False |
| django             | timing             |    22.8 |        34.8 |  1.5 |    0.86 |         16 |     0.91 | False |
| django             | traced             |   404.4 |       398.3 |  1.0 |    1.37 |          9 |      9.0 | False |
| django             | tests              |   676.0 |      6662.1 |  9.9 |    5.69 |         16 |     16.0 | False |
| sqlalchemy         | check              |     0.4 |         0.2 |  0.5 |    0.05 |          2 |     0.92 | False |
| sqlalchemy         | fix-certain        |    18.0 |        35.8 |  2.0 |    0.96 |          2 |     1.22 | False |
| sqlalchemy         | fix-likely         |    24.9 |        46.9 |  1.9 |    1.35 |          2 |     1.61 | False |
| sqlalchemy         | fix-unsafe         |    18.8 |        37.1 |  2.0 |     1.0 |          2 |     1.39 | False |
| sqlalchemy         | infer-basedpyright |    49.9 |       232.1 |  4.7 |    7.34 |          5 |     9.12 | False |
| sqlalchemy         | infer-ty           |    40.7 |       119.1 |  2.9 |    3.92 |          3 |     4.02 | False |
| sqlalchemy         | infer-pyrefly      |    33.9 |        72.6 |  2.1 |    3.93 |          2 |     4.92 | False |
| sqlalchemy         | census             |    10.6 |        16.8 |  1.6 |    0.85 |          2 |     0.92 | False |
| sqlalchemy         | coverage           |     3.0 |         5.4 |  1.8 |    0.39 |          1 |     0.12 | False |
| sqlalchemy         | timing             |    19.2 |        27.0 |  1.4 |    0.86 |         16 |     1.11 | False |
| sqlalchemy         | traced             |   102.5 |       908.6 |  8.9 |    5.82 |         14 |     14.0 | False |
| sqlalchemy         | tests              |   480.2 |      5016.9 | 10.4 |    5.27 |         16 |     16.0 | False |
| sqlalchemy         | types              |    41.9 |        41.2 |  1.0 |    0.36 |          1 |     0.41 | False |
| pydantic           | check              |     0.4 |         0.2 |  0.5 |    0.03 |          3 |     0.94 | False |
| pydantic           | fix-certain        |     3.6 |         9.2 |  2.6 |    0.45 |          3 |     1.19 | False |
| pydantic           | fix-likely         |     4.4 |        11.2 |  2.5 |    0.49 |          4 |     1.49 | False |
| pydantic           | fix-unsafe         |     3.8 |         9.9 |  2.6 |    0.38 |          5 |     1.01 | False |
| pydantic           | infer-basedpyright |    43.5 |       114.9 |  2.6 |    3.08 |          3 |     4.17 | False |
| pydantic           | infer-ty           |    10.8 |        32.1 |  3.0 |    1.46 |          3 |     2.02 | False |
| pydantic           | infer-pyrefly      |    10.4 |        25.0 |  2.4 |    1.97 |          2 |     2.51 | False |
| pydantic           | census             |     3.0 |         4.4 |  1.5 |    0.29 |          3 |     0.94 | False |
| pydantic           | coverage           |     1.0 |         1.8 |  1.8 |     0.2 |          3 |     0.45 | False |
| pydantic           | timing             |     4.4 |         6.5 |  1.5 |     0.3 |         16 |     0.17 | False |
| pydantic           | traced             |    32.4 |        36.3 |  1.1 |    0.49 |          1 |      1.0 | False |
| pydantic           | tests              |   138.8 |       132.9 |  1.0 |    0.32 |          1 |      1.0 | False |
| pydantic           | types              |    65.7 |       106.0 |  1.6 |    0.56 |          2 |     0.77 | False |
| pandas             | check              |    23.9 |         1.3 |  0.1 |    0.19 |          3 |     5.14 | False |
| pandas             | fix-certain        |    76.8 |       240.2 |  3.1 |    4.05 |          3 |      5.9 | False |
| pandas             | fix-likely         |   130.0 |       403.1 |  3.1 |    7.27 |          4 |     10.1 | False |
| pandas             | fix-unsafe         |    92.0 |       264.0 |  2.9 |    4.31 |          3 |     6.25 | False |
| pandas             | infer-basedpyright |   746.0 |      1301.6 |  1.7 |   15.88 |          3 |     21.6 | False |
| pandas             | infer-ty           |   144.1 |       628.5 |  4.4 |   14.49 |          5 |    19.12 | False |
| pandas             | infer-pyrefly      |    96.3 |       398.6 |  4.1 |   18.15 |          4 |    21.49 | False |
| pandas             | census             |    53.5 |       119.6 |  2.2 |    3.27 |          3 |     5.14 | False |
| pandas             | coverage           |     7.0 |        21.8 |  3.1 |    1.05 |          3 |     1.44 | False |
| pandas             | timing             |   134.7 |       213.0 |  1.6 |    3.29 |         16 |     4.96 | False |
| pandas             | traced             |   145.3 |       891.2 |  6.1 |    13.3 |         12 |     18.0 | False |
| pandas             | tests              |   504.4 |      3582.4 |  7.1 |   11.61 |         11 |     16.5 | False |
| pandas             | types              |   365.2 |       591.3 |  1.6 |    2.37 |          2 |     2.89 | False |
| twisted            | check              |     6.4 |        13.5 |  2.1 |    0.82 |          2 |      1.0 | False |
| twisted            | fix-certain        |    15.8 |        34.6 |  2.2 |    0.94 |          2 |     1.31 | False |
| twisted            | fix-likely         |    18.3 |        46.1 |  2.5 |    1.41 |          3 |     1.55 | False |
| twisted            | fix-unsafe         |    13.8 |        34.7 |  2.5 |    0.96 |          2 |     1.16 | False |
| twisted            | infer-basedpyright |    54.7 |       258.3 |  4.7 |    8.99 |          5 |    10.97 | False |
| twisted            | infer-ty           |    24.6 |        94.6 |  3.8 |    3.76 |          4 |     3.95 | False |
| twisted            | infer-pyrefly      |    23.1 |        85.3 |  3.7 |    4.19 |          4 |     5.07 | False |
| twisted            | census             |     4.6 |         4.2 |  0.9 |    0.11 |          2 |      1.0 | False |
| twisted            | coverage           |     2.6 |         5.9 |  2.3 |    0.36 |          1 |     0.34 | False |
| twisted            | timing             |    17.2 |        26.6 |  1.5 |    0.82 |         16 |      1.0 | False |
| pip                | check              |     4.8 |         9.4 |  2.0 |    0.54 |          2 |     0.72 | False |
| pip                | fix-certain        |    11.4 |        25.2 |  2.2 |    0.72 |          2 |     0.81 | False |
| pip                | fix-likely         |    14.6 |        31.0 |  2.1 |    0.89 |          2 |     1.09 | False |
| pip                | fix-unsafe         |    10.6 |        25.2 |  2.4 |    0.71 |          2 |     0.85 | False |
| pip                | infer-basedpyright |    45.9 |       198.7 |  4.3 |    5.74 |          4 |     6.75 | False |
| pip                | infer-ty           |    21.3 |        68.2 |  3.2 |    2.93 |          4 |     3.06 | False |
| pip                | infer-pyrefly      |    20.1 |        61.5 |  3.1 |    3.11 |          4 |     3.91 | False |
| pip                | census             |     3.2 |         2.9 |  0.9 |     0.1 |          2 |     0.72 | False |
| pip                | coverage           |     2.4 |         4.0 |  1.7 |    0.32 |          1 |     0.09 | False |
| pip                | timing             |    11.6 |        17.7 |  1.5 |    0.54 |         16 |     0.69 | False |
| structlog          | check              |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| structlog          | fix-certain        |     1.2 |         2.2 |  1.8 |    0.26 |          2 |     0.29 | False |
| structlog          | fix-likely         |     1.6 |         2.6 |  1.6 |    0.26 |          2 |     0.34 | False |
| structlog          | fix-unsafe         |     1.6 |         2.3 |  1.4 |    0.27 |          2 |     0.34 | False |
| structlog          | infer-basedpyright |     7.0 |        11.3 |  1.6 |    0.62 |          2 |     0.65 | False |
| structlog          | infer-ty           |     2.6 |         3.6 |  1.4 |    0.39 |          1 |     0.49 | False |
| structlog          | infer-pyrefly      |     2.2 |         3.3 |  1.5 |    0.39 |          1 |     0.49 | False |
| structlog          | census             |     1.0 |         1.0 |  1.0 |    0.16 |          1 |      0.2 | False |
| structlog          | coverage           |     0.8 |         0.7 |  0.9 |    0.14 |          1 |     0.17 | False |
| structlog          | timing             |     1.2 |         1.3 |  1.1 |    0.16 |         16 |     0.17 | False |
| structlog          | traced             |     3.6 |         4.3 |  1.2 |    0.27 |          1 |      1.0 | False |
| structlog          | tests              |     9.4 |         8.2 |  0.9 |    0.07 |          1 |      1.0 | False |
| structlog          | types              |     2.8 |         2.2 |  0.8 |    0.08 |          1 |     0.17 | False |
| attrs              | check              |     0.8 |         0.1 |  0.1 |    0.03 |          1 |     0.17 | False |
| attrs              | fix-certain        |     1.4 |         1.9 |  1.4 |    0.25 |          2 |     0.31 | False |
| attrs              | fix-likely         |     1.8 |         2.4 |  1.3 |    0.25 |          1 |     0.31 | False |
| attrs              | fix-unsafe         |     1.8 |         2.2 |  1.2 |    0.25 |          1 |     0.31 | False |
| attrs              | infer-basedpyright |     7.6 |        12.5 |  1.6 |    0.57 |          2 |     0.95 | False |
| attrs              | infer-ty           |     3.4 |         3.7 |  1.1 |    0.39 |          1 |     0.49 | False |
| attrs              | infer-pyrefly      |     3.2 |         3.4 |  1.1 |    0.38 |          1 |     0.47 | False |
| attrs              | census             |     1.2 |         1.0 |  0.8 |    0.14 |          1 |     0.17 | False |
| attrs              | coverage           |     0.8 |         0.6 |  0.7 |    0.13 |          1 |     0.16 | False |
| attrs              | timing             |     1.2 |         1.2 |  1.0 |    0.15 |         16 |     0.06 | False |
| attrs              | traced             |     3.6 |        16.1 |  4.5 |    0.73 |          8 |      8.0 | False |
| attrs              | tests              |    12.8 |        66.4 |  5.2 |     0.6 |          8 |      8.0 | False |
| click              | check              |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     0.21 | False |
| click              | fix-certain        |     1.4 |         2.6 |  1.9 |    0.29 |          2 |     0.36 | False |
| click              | fix-likely         |     1.6 |         3.0 |  1.9 |    0.29 |          2 |     0.37 | False |
| click              | fix-unsafe         |     1.4 |         2.7 |  1.9 |    0.29 |          2 |     0.34 | False |
| click              | infer-basedpyright |    10.2 |        18.7 |  1.8 |    0.69 |          2 |     0.97 | False |
| click              | infer-ty           |     3.8 |         5.9 |  1.6 |    0.46 |          2 |     0.57 | False |
| click              | infer-pyrefly      |     2.4 |         4.1 |  1.7 |    0.47 |          2 |     0.59 | False |
| click              | census             |     1.4 |         1.4 |  1.0 |    0.17 |          1 |     0.21 | False |
| click              | coverage           |     0.8 |         0.9 |  1.1 |    0.15 |          1 |     0.19 | False |
| click              | timing             |     1.6 |         1.9 |  1.2 |    0.17 |         16 |     0.07 | False |
| click              | traced             |     7.6 |         9.0 |  1.2 |    0.29 |          1 |      1.0 | False |
| click              | tests              |    31.1 |        29.2 |  0.9 |    0.17 |          1 |      1.0 | False |
| click              | types              |     4.6 |         4.0 |  0.9 |    0.13 |          1 |     0.15 | False |
| hypercorn          | check              |     0.8 |         0.1 |  0.1 |    0.03 |          1 |     0.24 | False |
| hypercorn          | fix-certain        |     1.6 |         2.8 |  1.7 |    0.24 |          2 |     0.27 | False |
| hypercorn          | fix-likely         |     1.6 |         3.1 |  1.9 |    0.24 |          2 |     0.34 | False |
| hypercorn          | fix-unsafe         |     1.6 |         2.8 |  1.7 |    0.25 |          2 |     0.34 | False |
| hypercorn          | infer-basedpyright |     5.8 |        16.1 |  2.8 |     0.9 |          3 |     1.36 | False |
| hypercorn          | infer-ty           |     3.2 |         6.1 |  1.9 |    0.64 |          2 |     0.65 | False |
| hypercorn          | infer-pyrefly      |     2.8 |         5.7 |  2.0 |    0.65 |          2 |     0.96 | False |
| hypercorn          | census             |     1.0 |         1.1 |  1.1 |    0.17 |          1 |     0.24 | False |
| hypercorn          | coverage           |     0.8 |         0.7 |  0.9 |    0.14 |          1 |     0.17 | False |
| hypercorn          | timing             |     1.4 |         1.6 |  1.1 |    0.17 |         16 |     0.12 | False |
| hypercorn          | traced             |     8.6 |         4.1 |  0.5 |    0.26 |          1 |      1.0 | False |
| hypercorn          | tests              |    41.5 |         7.2 |  0.2 |    0.09 |          1 |      1.0 | False |
| hypercorn          | types              |     5.2 |         4.8 |  0.9 |    0.12 |          1 |     0.31 | False |
| starlette          | check              |     1.2 |         0.2 |  0.2 |    0.03 |          1 |     0.21 | False |
| starlette          | fix-certain        |     2.2 |         3.2 |  1.5 |    0.28 |          1 |     0.31 | False |
| starlette          | fix-likely         |     2.4 |         3.8 |  1.6 |    0.26 |          1 |     0.35 | False |
| starlette          | fix-unsafe         |     2.4 |         3.3 |  1.4 |    0.25 |          1 |     0.35 | False |
| starlette          | infer-basedpyright |     6.4 |        18.0 |  2.8 |    1.07 |          3 |      1.6 | False |
| starlette          | infer-ty           |     3.2 |         6.6 |  2.1 |    0.66 |          2 |     0.79 | False |
| starlette          | infer-pyrefly      |     4.2 |         5.9 |  1.4 |    0.67 |          1 |     0.89 | False |
| starlette          | census             |     1.4 |         1.4 |  1.0 |    0.17 |          1 |     0.21 | False |
| starlette          | coverage           |     0.6 |         0.7 |  1.2 |    0.14 |          1 |     0.17 | False |
| starlette          | timing             |     1.6 |         2.0 |  1.2 |    0.18 |         16 |     0.07 | False |
| starlette          | traced             |     9.4 |         9.4 |  1.0 |    0.29 |          1 |      1.0 | False |
| starlette          | tests              |    41.9 |        31.8 |  0.8 |    0.22 |          1 |      1.0 | False |
| starlette          | types              |    11.5 |         8.3 |  0.7 |    0.14 |          1 |     0.39 | False |
| werkzeug           | check              |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.25 | False |
| werkzeug           | fix-certain        |     3.2 |         5.1 |  1.6 |     0.3 |          1 |     0.35 | False |
| werkzeug           | fix-likely         |     4.0 |         6.0 |  1.5 |     0.3 |          1 |     0.41 | False |
| werkzeug           | fix-unsafe         |     1.8 |         4.2 |  2.3 |    0.32 |          2 |     0.37 | False |
| werkzeug           | infer-basedpyright |     8.4 |        26.7 |  3.2 |     1.2 |          3 |     1.54 | False |
| werkzeug           | infer-ty           |     3.8 |         9.8 |  2.6 |    0.75 |          2 |     1.05 | False |
| werkzeug           | infer-pyrefly      |     3.0 |         7.7 |  2.6 |     0.8 |          2 |     0.99 | False |
| werkzeug           | census             |     1.6 |         2.1 |  1.3 |     0.2 |          1 |     0.25 | False |
| werkzeug           | coverage           |     0.8 |         1.0 |  1.2 |    0.16 |          1 |      0.2 | False |
| werkzeug           | timing             |     2.2 |         3.1 |  1.4 |     0.2 |         16 |     0.12 | False |
| werkzeug           | traced             |     9.8 |        11.8 |  1.2 |     0.3 |          1 |      1.0 | False |
| werkzeug           | tests              |    39.9 |        34.5 |  0.9 |    0.16 |          1 |      1.0 | False |
| werkzeug           | types              |     7.2 |         6.2 |  0.9 |    0.11 |          1 |      0.2 | False |
| mkdocs             | check              |     2.2 |         2.2 |  1.0 |    0.24 |          1 |     0.32 | False |
| mkdocs             | fix-certain        |     2.4 |         4.9 |  2.0 |    0.34 |          2 |     0.39 | False |
| mkdocs             | fix-likely         |     5.6 |         7.4 |  1.3 |    0.31 |          1 |     0.42 | False |
| mkdocs             | fix-unsafe         |     4.4 |         5.8 |  1.3 |    0.33 |          1 |     0.44 | False |
| mkdocs             | infer-basedpyright |    12.4 |        33.6 |  2.7 |    1.38 |          3 |      2.0 | False |
| mkdocs             | infer-ty           |     5.0 |        10.9 |  2.2 |    0.88 |          2 |     1.22 | False |
| mkdocs             | infer-pyrefly      |     4.4 |         9.4 |  2.1 |    0.89 |          2 |     1.12 | False |
| mkdocs             | census             |     1.0 |         0.7 |  0.7 |    0.05 |          1 |     0.32 | False |
| mkdocs             | coverage           |     1.2 |         1.3 |  1.1 |    0.17 |          1 |     0.21 | False |
| mkdocs             | timing             |     2.8 |         3.6 |  1.3 |    0.24 |         16 |     0.11 | False |
| mkdocs             | traced             |    13.2 |         8.5 |  0.6 |    0.35 |          1 |      1.0 | False |
| mkdocs             | tests              |    57.7 |        12.8 |  0.2 |    0.07 |          1 |      1.0 | False |
| httpx              | check              |     1.4 |         1.2 |  0.9 |    0.17 |          1 |     0.26 | False |
| httpx              | fix-certain        |     3.0 |         3.0 |  1.0 |    0.25 |          1 |      0.3 | False |
| httpx              | fix-likely         |     4.2 |         3.8 |  0.9 |    0.24 |          1 |     0.32 | False |
| httpx              | fix-unsafe         |     3.4 |         3.2 |  0.9 |    0.24 |          1 |     0.34 | False |
| httpx              | infer-basedpyright |     9.0 |        15.2 |  1.7 |    0.66 |          2 |     0.97 | False |
| httpx              | infer-ty           |     4.6 |         6.2 |  1.3 |    0.49 |          1 |     0.61 | False |
| httpx              | infer-pyrefly      |     4.6 |         5.2 |  1.1 |    0.51 |          1 |     0.65 | False |
| httpx              | census             |     0.6 |         0.3 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | coverage           |     1.2 |         0.9 |  0.8 |    0.14 |          1 |     0.17 | False |
| httpx              | timing             |     1.4 |         1.7 |  1.2 |    0.17 |         16 |     0.07 | False |
| httpx              | traced             |     7.8 |         7.8 |  1.0 |    0.27 |          1 |      1.0 | False |
| httpx              | tests              |    31.9 |        25.2 |  0.8 |     0.2 |          1 |      1.0 | False |
| httpx              | types              |    38.6 |        37.4 |  1.0 |    0.24 |          1 |     0.41 | False |
| black              | check              |     1.4 |         1.5 |  1.1 |    0.19 |          1 |     0.26 | False |
| black              | fix-certain        |     1.4 |         3.0 |  2.1 |    0.31 |          2 |     0.35 | False |
| black              | fix-likely         |     2.8 |         4.9 |  1.8 |    0.31 |          2 |     0.35 | False |
| black              | fix-unsafe         |     3.0 |         4.6 |  1.5 |    0.31 |          2 |     0.39 | False |
| black              | infer-basedpyright |    11.6 |        20.5 |  1.8 |    0.77 |          2 |     1.09 | False |
| black              | infer-ty           |     6.2 |         8.6 |  1.4 |    0.54 |          1 |     0.66 | False |
| black              | infer-pyrefly      |     4.0 |         6.7 |  1.7 |    0.55 |          2 |     0.85 | False |
| black              | census             |     0.8 |         0.5 |  0.6 |    0.04 |          1 |     0.26 | False |
| black              | coverage           |     1.2 |         1.1 |  0.9 |    0.16 |          1 |      0.2 | False |
| black              | timing             |     1.8 |         2.3 |  1.3 |    0.19 |         16 |     0.09 | False |
| black              | traced             |    10.6 |        64.2 |  6.1 |    0.88 |          8 |      8.0 | False |
| black              | tests              |   105.4 |       719.9 |  6.8 |     0.8 |          8 |      8.0 | False |
| fastapi            | check              |     1.4 |         1.5 |  1.1 |    0.21 |          1 |     0.34 | False |
| fastapi            | fix-certain        |     2.6 |         4.1 |  1.6 |    0.32 |          1 |     0.41 | False |
| fastapi            | fix-likely         |     4.8 |         5.6 |  1.2 |    0.36 |          1 |     0.55 | False |
| fastapi            | fix-unsafe         |     2.4 |         3.9 |  1.6 |    0.29 |          1 |      0.4 | False |
| fastapi            | infer-basedpyright |    11.8 |        28.5 |  2.4 |     1.2 |          2 |     1.77 | False |
| fastapi            | infer-ty           |     5.2 |         9.2 |  1.8 |    0.82 |          2 |     1.02 | False |
| fastapi            | infer-pyrefly      |     4.2 |         7.8 |  1.9 |    0.87 |          2 |      1.3 | False |
| fastapi            | census             |     0.8 |         0.4 |  0.5 |    0.04 |          1 |     0.34 | False |
| fastapi            | coverage           |     0.8 |         1.0 |  1.2 |    0.16 |          1 |      0.2 | False |
| fastapi            | timing             |     2.2 |         2.6 |  1.2 |    0.21 |         16 |     0.41 | False |
| fastapi            | traced             |    20.2 |       119.0 |  5.9 |    2.33 |          8 |      8.0 | False |
| fastapi            | tests              |    84.0 |       562.3 |  6.7 |    2.06 |          8 |      8.0 | False |
| cattrs             | check              |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| cattrs             | fix-certain        |     2.4 |         2.9 |  1.2 |    0.26 |          1 |     0.32 | False |
| cattrs             | fix-likely         |     2.6 |         3.3 |  1.3 |    0.21 |          1 |     0.27 | False |
| cattrs             | fix-unsafe         |     2.4 |         3.2 |  1.3 |    0.24 |          1 |     0.34 | False |
| cattrs             | infer-basedpyright |     8.6 |        20.2 |  2.3 |    0.95 |          2 |     1.45 | False |
| cattrs             | infer-ty           |     4.0 |         5.6 |  1.4 |    0.61 |          1 |     0.77 | False |
| cattrs             | infer-pyrefly      |     3.4 |         4.8 |  1.4 |    0.62 |          1 |     0.79 | False |
| cattrs             | census             |     1.4 |         1.3 |  0.9 |    0.17 |          1 |     0.21 | False |
| cattrs             | coverage           |     0.6 |         0.7 |  1.2 |    0.14 |          1 |     0.17 | False |
| cattrs             | timing             |     1.4 |         1.8 |  1.3 |    0.17 |         16 |     0.07 | False |
| cattrs             | traced             |    23.2 |       156.5 |  6.7 |    1.38 |          8 |      8.0 | False |
| cattrs             | tests              |   113.5 |       734.5 |  6.5 |    1.02 |          8 |      8.0 | False |
| pytest             | check              |     1.8 |         3.1 |  1.7 |    0.26 |          2 |     0.47 | False |
| pytest             | fix-certain        |     5.4 |         8.5 |  1.6 |     0.4 |          1 |     0.51 | False |
| pytest             | fix-likely         |     5.6 |        10.6 |  1.9 |    0.41 |          2 |     0.51 | False |
| pytest             | fix-unsafe         |     4.8 |         9.0 |  1.9 |     0.4 |          2 |     0.51 | False |
| pytest             | infer-basedpyright |    22.6 |        62.9 |  2.8 |    2.21 |          2 |     3.07 | False |
| pytest             | infer-ty           |    10.2 |        21.7 |  2.1 |    1.25 |          2 |     1.76 | False |
| pytest             | infer-pyrefly      |     9.0 |        17.3 |  1.9 |     1.3 |          2 |      1.8 | False |
| pytest             | census             |     2.2 |         0.9 |  0.4 |    0.04 |          2 |     0.47 | False |
| pytest             | coverage           |     0.8 |         1.6 |  2.0 |    0.19 |          2 |     0.39 | False |
| pytest             | timing             |     4.2 |         5.7 |  1.4 |    0.27 |         16 |      0.4 | False |
| pytest             | traced             |    48.1 |       339.3 |  7.1 |     1.7 |          8 |      8.0 | False |
| pytest             | tests              |   112.8 |       861.3 |  7.6 |    1.64 |          8 |      8.0 | False |
| botocore           | check              |     2.0 |         0.2 |  0.1 |    0.03 |          1 |     0.34 | False |
| botocore           | fix-certain        |     4.8 |         9.9 |  2.1 |    0.35 |          2 |     0.46 | False |
| botocore           | fix-likely         |     6.6 |        12.4 |  1.9 |    0.45 |          2 |     0.56 | False |
| botocore           | fix-unsafe         |     5.4 |        10.7 |  2.0 |    0.39 |          2 |     0.49 | False |
| botocore           | infer-basedpyright |    19.6 |        61.8 |  3.2 |    2.29 |          3 |     3.09 | False |
| botocore           | infer-ty           |    10.4 |        21.7 |  2.1 |    1.23 |          2 |     1.65 | False |
| botocore           | infer-pyrefly      |     8.2 |        17.3 |  2.1 |    1.29 |          2 |     1.84 | False |
| botocore           | census             |     3.8 |         4.8 |  1.3 |    0.28 |          1 |     0.34 | False |
| botocore           | coverage           |     1.4 |         1.5 |  1.1 |    0.18 |          1 |     0.22 | False |
| botocore           | timing             |     5.0 |         7.2 |  1.4 |    0.28 |         16 |     0.36 | False |
| botocore           | traced             |    31.2 |       110.5 |  3.5 |    5.16 |          8 |      8.0 | False |
| botocore           | tests              |   151.8 |       477.6 |  3.1 |    4.92 |          8 |      8.0 | False |
| uvicorn            | check              |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| uvicorn            | fix-certain        |     2.6 |         3.2 |  1.2 |     0.2 |          1 |     0.31 | False |
| uvicorn            | fix-likely         |     2.8 |         3.7 |  1.3 |    0.27 |          1 |      0.3 | False |
| uvicorn            | fix-unsafe         |     2.4 |         3.2 |  1.3 |    0.27 |          1 |     0.31 | False |
| uvicorn            | infer-basedpyright |    12.4 |        23.5 |  1.9 |    1.04 |          2 |     1.57 | False |
| uvicorn            | infer-ty           |     6.2 |         7.6 |  1.2 |    0.66 |          2 |     1.01 | False |
| uvicorn            | infer-pyrefly      |     3.6 |         6.5 |  1.8 |    0.68 |          2 |     0.86 | False |
| uvicorn            | census             |     1.6 |         1.4 |  0.9 |    0.17 |          1 |     0.21 | False |
| uvicorn            | coverage           |     1.0 |         0.8 |  0.8 |    0.14 |          1 |     0.17 | False |
| uvicorn            | timing             |     1.6 |         2.0 |  1.2 |    0.18 |         16 |     0.12 | False |
| uvicorn            | traced             |    44.5 |        30.4 |  0.7 |    0.97 |          1 |      1.0 | False |
| uvicorn            | tests              |   213.1 |       126.9 |  0.6 |    0.87 |          1 |      1.0 | False |
| uvicorn            | types              |    10.6 |        10.0 |  0.9 |    0.14 |          1 |     0.32 | False |
| mcp                | check              |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     0.31 | False |
| mcp                | fix-certain        |     3.4 |         6.7 |  2.0 |    0.31 |          2 |     0.44 | False |
| mcp                | fix-likely         |     4.6 |         8.8 |  1.9 |    0.41 |          2 |     0.51 | False |
| mcp                | fix-unsafe         |     3.2 |         6.8 |  2.1 |    0.36 |          2 |     0.46 | False |
| mcp                | infer-basedpyright |    15.0 |        62.0 |  4.1 |    2.41 |          4 |     3.01 | False |
| mcp                | infer-ty           |     7.8 |        20.9 |  2.7 |     1.5 |          2 |     2.09 | False |
| mcp                | infer-pyrefly      |     6.0 |        16.7 |  2.8 |    1.32 |          3 |     2.22 | False |
| mcp                | census             |     1.8 |         2.7 |  1.5 |    0.25 |          1 |     0.31 | False |
| mcp                | coverage           |     1.4 |         1.4 |  1.0 |    0.17 |          1 |     0.21 | False |
| mcp                | timing             |     3.2 |         4.4 |  1.4 |    0.25 |         16 |     0.42 | False |
| mcp                | traced             |    19.8 |       101.2 |  5.1 |    2.31 |          8 |      8.0 | False |
| mcp                | tests              |    73.6 |       348.4 |  4.7 |    2.03 |          8 |      8.0 | False |
| mcp                | types              |    95.3 |       162.8 |  1.7 |    1.29 |          2 |     1.66 | False |
| textual            | check              |     2.6 |         5.5 |  2.1 |    0.42 |          2 |     0.55 | False |
| textual            | fix-certain        |     7.8 |        15.6 |  2.0 |    0.53 |          2 |     0.66 | False |
| textual            | fix-likely         |     7.6 |        18.8 |  2.5 |     0.6 |          2 |     0.85 | False |
| textual            | fix-unsafe         |     5.4 |        14.6 |  2.7 |    0.54 |          2 |     0.81 | False |
| textual            | infer-basedpyright |    26.3 |       120.2 |  4.6 |    3.76 |          4 |     4.75 | False |
| textual            | infer-ty           |    17.0 |        48.5 |  2.9 |    2.07 |          3 |     2.77 | False |
| textual            | infer-pyrefly      |    11.4 |        40.3 |  3.5 |    2.37 |          3 |     3.19 | False |
| textual            | census             |     2.0 |         1.5 |  0.8 |    0.06 |          2 |     0.55 | False |
| textual            | coverage           |     1.4 |         2.8 |  2.0 |    0.24 |          2 |      0.3 | False |
| textual            | timing             |     7.0 |        10.4 |  1.5 |    0.42 |         16 |     0.27 | False |
| pdm                | check              |     3.0 |         3.8 |  1.3 |    0.41 |          1 |     0.55 | False |
| pdm                | fix-certain        |     3.0 |         7.5 |  2.5 |    0.44 |          2 |     0.64 | False |
| pdm                | fix-likely         |     5.4 |        11.6 |  2.1 |    0.53 |          2 |     0.65 | False |
| pdm                | fix-unsafe         |     8.6 |        10.6 |  1.2 |    0.45 |          1 |     0.55 | False |
| pdm                | infer-basedpyright |    14.2 |        65.9 |  4.6 |     2.7 |          5 |     3.64 | False |
| pdm                | infer-ty           |     8.0 |        25.3 |  3.2 |     1.6 |          3 |     1.79 | False |
| pdm                | infer-pyrefly      |     6.2 |        18.3 |  3.0 |    1.74 |          2 |     2.37 | False |
| pdm                | census             |     3.6 |         0.9 |  0.2 |    0.04 |          1 |     0.55 | False |
| pdm                | coverage           |     1.4 |         1.7 |  1.2 |    0.18 |          1 |     0.22 | False |
| pdm                | timing             |     4.4 |         6.3 |  1.4 |    0.42 |         16 |     0.17 | False |
| pdm                | traced             |    21.6 |       114.6 |  5.3 |    1.53 |          8 |      8.0 | False |
| pdm                | tests              |    99.8 |       608.7 |  6.1 |    2.53 |          8 |      8.0 | False |
| strawberry-graphql | check              |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.41 | False |
| strawberry-graphql | fix-certain        |     4.0 |         9.0 |  2.2 |    0.42 |          2 |     0.55 | False |
| strawberry-graphql | fix-likely         |     4.6 |        11.7 |  2.5 |    0.56 |          2 |     0.87 | False |
| strawberry-graphql | fix-unsafe         |     4.8 |         9.5 |  2.0 |    0.42 |          1 |     0.67 | False |
| strawberry-graphql | infer-basedpyright |    17.0 |        84.1 |  4.9 |    3.01 |          5 |     3.97 | False |
| strawberry-graphql | infer-ty           |    10.8 |        29.8 |  2.8 |    1.65 |          3 |     2.09 | False |
| strawberry-graphql | infer-pyrefly      |     7.6 |        21.2 |  2.8 |    1.76 |          3 |     2.44 | False |
| strawberry-graphql | census             |     2.8 |         4.2 |  1.5 |    0.33 |          1 |     0.41 | False |
| strawberry-graphql | coverage           |     1.0 |         1.5 |  1.5 |    0.18 |          1 |     0.21 | False |
| strawberry-graphql | timing             |     4.4 |         6.5 |  1.5 |    0.33 |         16 |      0.2 | False |
| strawberry-graphql | traced             |    14.4 |        76.8 |  5.3 |    1.47 |          8 |      8.0 | False |
| strawberry-graphql | tests              |    76.5 |       490.6 |  6.4 |    1.27 |          8 |      8.0 | False |
| strawberry-graphql | types              |    14.6 |        12.7 |  0.9 |    0.25 |          1 |      0.5 | False |
| pygments           | check              |     2.8 |         0.2 |  0.1 |    0.04 |          1 |      0.5 | False |
| pygments           | fix-certain        |     7.0 |        16.5 |  2.4 |    0.58 |          2 |     0.64 | False |
| pygments           | fix-likely         |     7.0 |        17.8 |  2.5 |    0.57 |          2 |     0.72 | False |
| pygments           | fix-unsafe         |     7.0 |        16.6 |  2.4 |    0.58 |          2 |     0.67 | False |
| pygments           | infer-basedpyright |    35.5 |       114.4 |  3.2 |    3.28 |          3 |      4.2 | False |
| pygments           | infer-ty           |    12.2 |        35.8 |  2.9 |    1.73 |          3 |      2.2 | False |
| pygments           | infer-pyrefly      |    10.4 |        30.6 |  2.9 |    2.03 |          3 |     2.74 | False |
| pygments           | census             |     5.8 |         8.5 |  1.5 |    0.41 |          1 |      0.5 | False |
| pygments           | coverage           |     1.6 |         3.3 |  2.1 |    0.27 |          2 |     0.44 | False |
| pygments           | timing             |     7.6 |        11.3 |  1.5 |     0.4 |         16 |      0.5 | False |
| pygments           | traced             |    23.4 |        30.9 |  1.3 |     0.6 |          1 |      1.0 | False |
| pygments           | tests              |    71.3 |        70.4 |  1.0 |    0.23 |          1 |      1.0 | False |
| streamlink         | check              |     2.0 |         4.1 |  2.0 |     0.3 |          2 |     0.42 | False |
| streamlink         | fix-certain        |     3.6 |        10.0 |  2.8 |     0.4 |          2 |     0.49 | False |
| streamlink         | fix-likely         |     5.4 |        13.6 |  2.5 |    0.47 |          2 |     0.59 | False |
| streamlink         | fix-unsafe         |     4.4 |        10.8 |  2.5 |    0.39 |          2 |     0.55 | False |
| streamlink         | infer-basedpyright |    18.8 |        80.1 |  4.3 |    2.97 |          4 |     3.94 | False |
| streamlink         | infer-ty           |    11.8 |        29.9 |  2.5 |    1.52 |          3 |     2.12 | False |
| streamlink         | infer-pyrefly      |     8.6 |        23.1 |  2.7 |    1.67 |          2 |     2.04 | False |
| streamlink         | census             |     1.2 |         1.0 |  0.8 |    0.05 |          2 |     0.42 | False |
| streamlink         | coverage           |     1.6 |         2.1 |  1.3 |    0.21 |          1 |     0.26 | False |
| streamlink         | timing             |     5.4 |         8.1 |  1.5 |     0.3 |         16 |     0.47 | False |
| streamlink         | traced             |    13.4 |        17.4 |  1.3 |    0.39 |          1 |      1.0 | False |
| streamlink         | tests              |    60.1 |        59.0 |  1.0 |    0.17 |          1 |      1.0 | False |
| streamlink         | types              |    44.5 |        42.9 |  1.0 |    0.38 |          1 |     0.42 | False |
| sphinx             | check              |     1.0 |         0.2 |  0.2 |    0.04 |          2 |     0.67 | False |
| sphinx             | fix-certain        |     7.8 |        20.8 |  2.7 |    0.61 |          2 |     0.75 | False |
| sphinx             | fix-likely         |     9.0 |        26.4 |  2.9 |    0.82 |          3 |     1.04 | False |
| sphinx             | fix-unsafe         |     8.0 |        22.4 |  2.8 |    0.64 |          2 |     0.97 | False |
| sphinx             | infer-basedpyright |    26.8 |       127.7 |  4.8 |    4.35 |          5 |     5.59 | False |
| sphinx             | infer-ty           |    17.5 |        58.7 |  3.4 |    2.23 |          3 |     2.91 | False |
| sphinx             | infer-pyrefly      |    13.2 |        40.0 |  3.0 |     2.4 |          3 |     3.31 | False |
| sphinx             | census             |     4.6 |         8.6 |  1.9 |    0.44 |          2 |     0.67 | False |
| sphinx             | coverage           |     2.2 |         3.9 |  1.8 |    0.27 |          2 |     0.34 | False |
| sphinx             | timing             |     9.6 |        14.5 |  1.5 |    0.44 |         16 |     0.69 | False |
| sphinx             | traced             |    24.6 |       151.1 |  6.1 |    1.67 |          8 |      8.0 | False |
| sphinx             | tests              |   110.1 |       817.7 |  7.4 |    1.66 |          8 |      8.0 | False |
| sphinx             | types              |    39.7 |        38.8 |  1.0 |    0.33 |          1 |     0.49 | False |
| tox                | check              |     1.8 |         2.4 |  1.3 |    0.23 |          1 |     0.32 | False |
| tox                | fix-certain        |     3.4 |         6.4 |  1.9 |    0.33 |          2 |     0.44 | False |
| tox                | fix-likely         |     5.6 |         8.5 |  1.5 |    0.36 |          2 |     0.45 | False |
| tox                | fix-unsafe         |     3.6 |         6.6 |  1.8 |    0.34 |          2 |     0.42 | False |
| tox                | infer-basedpyright |    12.6 |        56.8 |  4.5 |     2.2 |          4 |      3.1 | False |
| tox                | infer-ty           |     9.8 |        18.3 |  1.9 |    1.31 |          2 |     1.84 | False |
| tox                | infer-pyrefly      |     6.0 |        13.5 |  2.2 |    1.38 |          2 |     1.82 | False |
| tox                | census             |     1.2 |         0.6 |  0.5 |    0.04 |          1 |     0.32 | False |
| tox                | coverage           |     1.4 |         1.3 |  0.9 |    0.16 |          1 |      0.2 | False |
| tox                | timing             |     3.0 |         4.3 |  1.4 |    0.23 |         16 |     0.15 | False |
| tox                | traced             |    24.6 |       137.7 |  5.6 |     1.6 |          8 |      8.0 | False |
| tox                | tests              |   110.5 |       625.7 |  5.7 |    1.44 |          8 |      8.0 | False |

- sphinx, 0.3.7-rc.1+dev, tests: the tests differ after infer-trace: 0 new
- sphinx, 0.3.7-rc.1+dev, tests: the tests differ after infer-ty: 0 new
- standard library, 0.3.7-rc.1+dev, infer-basedpyright: held 13.01 GB beside other steps
- standard library, 0.3.7-rc.1+dev, infer-ty: held 16.24 GB beside other steps
- standard library, 0.3.7-rc.1+dev, infer-pyrefly: held 18.9 GB beside other steps
- pandas, 0.3.7-rc.1+dev, infer-basedpyright: held 15.88 GB beside other steps
- pandas, 0.3.7-rc.1+dev, infer-ty: held 14.49 GB beside other steps
- pandas, 0.3.7-rc.1+dev, infer-pyrefly: held 18.15 GB beside other steps
- pandas, 0.3.7-rc.1+dev, traced: held 13.3 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests: held 11.61 GB beside other steps
- twisted, 0.3.7-rc.1+dev, infer-basedpyright: held 8.99 GB beside other steps

## Mega corpora

The run `0.4.0-rc.3` (`python -m tests.corpus`) on mega: constricter 0.3.10.dev30+ge8f67eb1e
(`8393ccd35128`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 105 minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter    |  Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |     `LVA006` |  `LVA009` | `LVA010` | `LVA011` |   Total |
| ------------------ | -------- | -------------- | -----: | --------------: | ------------: | -------: | -------------: | -----------: | -----------: | --------: | -------: | -------: | ------: |
| standard library   | 3.14.7   | 0.4.0-rc.3+dev |  1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |           14 |         8 |        0 |        0 | 113,750 |
| django             | 5.2.18   | 0.4.0-rc.3+dev |    883 |           9,926 |         2,166 |        0 |          5,084 |            0 |            0 |         1 |        0 |        0 |  17,177 |
| sqlalchemy         | 2.1.4    | 0.4.0-rc.3+dev |    258 |           8,825 |         1,636 |        0 |          2,501 |          572 |          128 |         2 |        0 |        1 |  13,665 |
| pydantic           | 2.14.0   | 0.4.0-rc.3+dev |    105 |           2,072 |           440 |        0 |            605 |          184 |           15 |         0 |        0 |        0 |   3,316 |
| pandas             | 3.0.6    | 0.4.0-rc.3+dev |  1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |            2 |         1 |        0 |        1 |  77,931 |
| twisted            | 12.3.0   | 0.4.0-rc.3+dev |    819 |          13,310 |         1,349 |        0 |          3,215 |            0 |            0 |         0 |        0 |        0 |  17,874 |
| pip                | 20.3.4   | 0.4.0-rc.3+dev |    366 |           5,902 |         1,150 |        0 |          1,872 |            0 |            0 |         0 |        0 |        0 |   8,924 |
| structlog          | 26.1.0   | 0.4.0-rc.3+dev |     21 |             156 |            47 |        0 |            113 |           12 |            1 |         0 |        0 |        0 |     329 |
| attrs              | 26.1.0   | 0.4.0-rc.3+dev |     13 |             285 |            50 |        0 |             58 |            2 |            0 |         1 |        0 |        0 |     396 |
| click              | 8.5.0    | 0.4.0-rc.3+dev |     17 |             481 |            58 |        0 |             69 |           28 |            1 |         0 |        0 |        0 |     637 |
| hypercorn          | 0.18.0   | 0.4.0-rc.3+dev |     39 |             220 |            67 |        0 |             68 |            8 |            0 |         0 |        0 |        0 |     363 |
| starlette          | 1.7.0    | 0.4.0-rc.3+dev |     36 |             499 |            99 |        0 |            146 |           18 |            0 |         0 |        0 |        0 |     762 |
| werkzeug           | 3.1.9    | 0.4.0-rc.3+dev |     52 |             835 |           235 |        0 |            223 |           15 |            1 |         0 |        0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | 0.4.0-rc.3+dev |     61 |           1,674 |           198 |        0 |            460 |            8 |            0 |         0 |        0 |        0 |   2,340 |
| httpx              | 0.28.1   | 0.4.0-rc.3+dev |     23 |             395 |           112 |        0 |             62 |            1 |            0 |         0 |        0 |        0 |     570 |
| black              | 26.10.0  | 0.4.0-rc.3+dev |     25 |             996 |           232 |        0 |             45 |            5 |            4 |         0 |        0 |        0 |   1,282 |
| fastapi            | 0.142.2  | 0.4.0-rc.3+dev |     52 |             586 |           105 |        0 |             51 |           98 |            5 |         0 |        0 |        0 |     845 |
| cattrs             | 26.2.1   | 0.4.0-rc.3+dev |     36 |             420 |            70 |        0 |             30 |            9 |            1 |         0 |        0 |        0 |     530 |
| pytest             | 9.1.1    | 0.4.0-rc.3+dev |     78 |           2,363 |           470 |        0 |            170 |           33 |            9 |         0 |        0 |        0 |   3,045 |
| botocore           | 1.43.108 | 0.4.0-rc.3+dev |     76 |           2,825 |           367 |        0 |            594 |            2 |            0 |         0 |        0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | 0.4.0-rc.3+dev |     45 |             363 |            71 |        0 |             55 |           11 |            4 |         0 |        0 |        0 |     504 |
| mcp                | 2.3.0    | 0.4.0-rc.3+dev |    124 |           1,356 |           173 |        0 |            191 |          105 |            8 |         0 |        0 |        0 |   1,833 |
| textual            | 8.2.8    | 0.4.0-rc.3+dev |    247 |           4,979 |           718 |        0 |            786 |           31 |           26 |         0 |        0 |        0 |   6,540 |
| pdm                | 2.29.2   | 0.4.0-rc.3+dev |    128 |           2,114 |           417 |        0 |            187 |           37 |            2 |         0 |        0 |        0 |   2,757 |
| strawberry-graphql | 0.332.0  | 0.4.0-rc.3+dev |    244 |           1,436 |           243 |        0 |            127 |          137 |            2 |         0 |        0 |        0 |   1,945 |
| pygments           | 2.21.0   | 0.4.0-rc.3+dev |    343 |           1,124 |           539 |        0 |          6,003 |            0 |            0 |         0 |        0 |        0 |   7,666 |
| streamlink         | 8.6.1    | 0.4.0-rc.3+dev |    227 |           2,080 |           310 |        0 |            639 |           37 |           11 |         0 |        0 |        0 |   3,077 |
| sphinx             | 9.1.0    | 0.4.0-rc.3+dev |    243 |           5,505 |         1,336 |        1 |          1,131 |           73 |           29 |         5 |        0 |        3 |   8,083 |
| tox                | 4.64.9   | 0.4.0-rc.3+dev |    129 |           1,369 |           286 |        0 |            107 |           18 |            5 |         0 |        0 |        0 |   1,785 |
| pint               | 0.26.1   | 0.4.0-rc.3+dev |    109 |           2,591 |           297 |        0 |            190 |           14 |            2 |         0 |        0 |        0 |   3,094 |
| altair             | 6.3.0    | 0.4.0-rc.3+dev |     55 |             814 |           130 |        0 |            756 |           60 |            8 |         0 |        0 |        0 |   1,768 |
| seaborn            | 0.13.2   | 0.4.0-rc.3+dev |     54 |           2,361 |           370 |        0 |            164 |           23 |            3 |         0 |        0 |        0 |   2,921 |
| aiohttp            | 3.14.4   | 0.4.0-rc.3+dev |     54 |           1,307 |           195 |        0 |            355 |           13 |            5 |         1 |        0 |        0 |   1,876 |
| websockets         | 17.2     | 0.4.0-rc.3+dev |     52 |             605 |            85 |        0 |            101 |            0 |            0 |         0 |        0 |        0 |     791 |
| anyio              | 4.15.1   | 0.4.0-rc.3+dev |     46 |             615 |            77 |        0 |             23 |           26 |            6 |         0 |        0 |        0 |     747 |
| zarr               | 3.4.0    | 0.4.0-rc.3+dev |     98 |           1,874 |           370 |        0 |            167 |           26 |           35 |         0 |        0 |        0 |   2,472 |
| joblib             | 1.6.0    | 0.4.0-rc.3+dev |     73 |           1,842 |           158 |        0 |            239 |            1 |            0 |         0 |        0 |        0 |   2,240 |
| networkx           | 3.7      | 0.4.0-rc.3+dev |    583 |          18,854 |         3,221 |        0 |            381 |            8 |            0 |         0 |        0 |        0 |  22,464 |
| nibabel            | 5.4.2    | 0.4.0-rc.3+dev |    229 |           6,504 |         1,032 |        0 |            932 |            5 |            1 |         0 |        0 |        0 |   8,474 |
| narwhals           | 2.26.0   | 0.4.0-rc.3+dev |    162 |           2,775 |           106 |        0 |            239 |           62 |            5 |         0 |        0 |        0 |   3,187 |
| xarray             | 2026.9.0 | 0.4.0-rc.3+dev |    199 |          18,968 |         1,599 |        0 |            777 |          255 |           20 |         0 |        0 |        0 |  21,619 |
| litestar           | 2.24.0   | 0.4.0-rc.3+dev |    374 |           1,474 |           306 |        0 |            125 |          166 |           12 |         4 |        0 |        0 |   2,087 |
| stripe             | 16.0.0   | 0.4.0-rc.3+dev |  1,460 |           1,772 |            49 |        0 |          1,536 |           16 |          854 |         0 |        0 |        0 |   4,227 |
| celery             | 5.6.3    | 0.4.0-rc.3+dev |    161 |           2,202 |           331 |        0 |          1,215 |            0 |            0 |         2 |        0 |        0 |   3,750 |
| optuna             | 5.0.0    | 0.4.0-rc.3+dev |    220 |           2,740 |           446 |        0 |            412 |           28 |            4 |         0 |        0 |        0 |   3,630 |
| dask               | 2026.8.0 | 0.4.0-rc.3+dev |    361 |          20,748 |         1,691 |        0 |          1,733 |           76 |            5 |         2 |        0 |        1 |  24,256 |
| mypy               | 2.4.0    | 0.4.0-rc.3+dev |    195 |           9,008 |         2,197 |        0 |            196 |          340 |           45 |         0 |        1 |        1 |  11,788 |
| **Total**          |          | 0.4.0-rc.3+dev | 12,462 | 331,082 (78.0%) | 40,716 (9.6%) | 1 (0.0%) | 48,553 (11.4%) | 2,754 (0.6%) | 1,273 (0.3%) | 27 (0.0%) | 1 (0.0%) | 7 (0.0%) | 424,414 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |           Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | -------------- | ----------: | ---------------: | --------------: | ----------: | --------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | 0.4.0-rc.3+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 |  37,415 (32.9%) |   6,530 (5.7%) | 12,304 (10.8%) |      0 |    0 |            0 |
| django             | 0.4.0-rc.3+dev |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |   2,627 (15.3%) |     634 (3.7%) |  2,693 (15.7%) |      0 |    0 |            0 |
| sqlalchemy         | 0.4.0-rc.3+dev |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |   1,881 (13.8%) |     334 (2.4%) |     818 (6.0%) |      0 |    0 |            0 |
| pydantic           | 0.4.0-rc.3+dev |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |   1,185 (35.7%) |     146 (4.4%) |    404 (12.2%) |      0 |    0 |            0 |
| pandas             | 0.4.0-rc.3+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 |  16,910 (21.7%) | 23,550 (30.2%) | 24,299 (31.2%) |      0 |    0 |            0 |
| twisted            | 0.4.0-rc.3+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |   2,439 (13.6%) |  3,620 (20.3%) |  4,624 (25.9%) |      0 |    0 |            0 |
| pip                | 0.4.0-rc.3+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |   2,254 (25.3%) |     421 (4.7%) |  1,109 (12.4%) |      0 |    0 |            0 |
| structlog          | 0.4.0-rc.3+dev |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |      98 (29.8%) |      15 (4.6%) |      27 (8.2%) |      0 |    0 |            0 |
| attrs              | 0.4.0-rc.3+dev |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |      93 (23.5%) |       9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| click              | 0.4.0-rc.3+dev |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |     285 (44.7%) |      28 (4.4%) |     65 (10.2%) |      0 |    0 |            0 |
| hypercorn          | 0.4.0-rc.3+dev |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |     134 (36.9%) |      20 (5.5%) |     58 (16.0%) |      0 |    0 |            0 |
| starlette          | 0.4.0-rc.3+dev |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |     311 (40.8%) |      57 (7.5%) |     97 (12.7%) |      0 |    0 |            0 |
| werkzeug           | 0.4.0-rc.3+dev |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |     526 (40.2%) |      65 (5.0%) |     126 (9.6%) |      0 |    0 |            0 |
| mkdocs             | 0.4.0-rc.3+dev |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |     810 (34.6%) |    379 (16.2%) |    473 (20.2%) |      0 |    0 |            0 |
| httpx              | 0.4.0-rc.3+dev |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |     234 (41.1%) |     57 (10.0%) |     72 (12.6%) |      0 |    0 |            0 |
| black              | 0.4.0-rc.3+dev |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |     704 (54.9%) |     127 (9.9%) |    164 (12.8%) |      0 |    0 |            0 |
| fastapi            | 0.4.0-rc.3+dev |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |     257 (30.4%) |      40 (4.7%) |      65 (7.7%) |      0 |    0 |            0 |
| cattrs             | 0.4.0-rc.3+dev |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |     105 (19.8%) |      34 (6.4%) |      46 (8.7%) |      0 |    0 |            0 |
| pytest             | 0.4.0-rc.3+dev |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |   1,344 (44.1%) |     159 (5.2%) |     283 (9.3%) |      0 |    0 |            0 |
| botocore           | 0.4.0-rc.3+dev |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |     543 (14.3%) |     166 (4.4%) |    591 (15.6%) |      0 |    0 |            0 |
| uvicorn            | 0.4.0-rc.3+dev |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |     231 (45.8%) |      29 (5.8%) |      43 (8.5%) |      0 |    0 |            0 |
| mcp                | 0.4.0-rc.3+dev |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |     683 (37.3%) |     154 (8.4%) |    234 (12.8%) |      0 |    0 |            0 |
| textual            | 0.4.0-rc.3+dev |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |   2,553 (39.0%) |     471 (7.2%) |    707 (10.8%) |      0 |    0 |            0 |
| pdm                | 0.4.0-rc.3+dev |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |   1,146 (41.6%) |     198 (7.2%) |    310 (11.2%) |      0 |    0 |            0 |
| strawberry-graphql | 0.4.0-rc.3+dev |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |     596 (30.6%) |     164 (8.4%) |    213 (11.0%) |      0 |    0 |            0 |
| pygments           | 0.4.0-rc.3+dev |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |      735 (9.6%) |      79 (1.0%) |     221 (2.9%) |      0 |    0 |            0 |
| streamlink         | 0.4.0-rc.3+dev |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |     670 (21.8%) |     108 (3.5%) |     226 (7.3%) |      0 |    0 |            0 |
| sphinx             | 0.4.0-rc.3+dev |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |   3,121 (38.6%) |     440 (5.4%) |     791 (9.8%) |      0 |    0 |            0 |
| tox                | 0.4.0-rc.3+dev |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |     941 (52.7%) |      80 (4.5%) |     133 (7.5%) |      0 |    0 |            0 |
| pint               | 0.4.0-rc.3+dev |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |     576 (18.6%) |     104 (3.4%) |     154 (5.0%) |      0 |    0 |            0 |
| altair             | 0.4.0-rc.3+dev |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |     373 (21.1%) |      47 (2.7%) |      60 (3.4%) |      0 |    0 |            0 |
| seaborn            | 0.4.0-rc.3+dev |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |     639 (21.9%) |     136 (4.7%) |     222 (7.6%) |      0 |    0 |            0 |
| aiohttp            | 0.4.0-rc.3+dev |   0 / 1,858 |      1,662 / 214 |      1,858 / 18 |   1,876 / 0 |     677 (36.1%) |     141 (7.5%) |    250 (13.3%) |      0 |    0 |            0 |
| websockets         | 0.4.0-rc.3+dev |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |     326 (41.2%) |      59 (7.5%) |    106 (13.4%) |      0 |    0 |            0 |
| anyio              | 0.4.0-rc.3+dev |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |     208 (27.8%) |      32 (4.3%) |      59 (7.9%) |      0 |    0 |            0 |
| zarr               | 0.4.0-rc.3+dev |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |   1,067 (43.2%) |      72 (2.9%) |     109 (4.4%) |      0 |    0 |            0 |
| joblib             | 0.4.0-rc.3+dev |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |     525 (23.4%) |     178 (7.9%) |    244 (10.9%) |      0 |    0 |            0 |
| networkx           | 0.4.0-rc.3+dev |  0 / 22,456 |   19,235 / 3,229 |      22,456 / 8 |  22,464 / 0 |   3,969 (17.7%) |   2,186 (9.7%) |  2,389 (10.6%) |      0 |    0 |            0 |
| nibabel            | 0.4.0-rc.3+dev |   0 / 8,468 |    7,436 / 1,038 |       8,468 / 6 |   8,474 / 0 |   1,849 (21.8%) |     680 (8.0%) |    921 (10.9%) |      0 |    0 |            0 |
| narwhals           | 0.4.0-rc.3+dev |   0 / 3,120 |      3,014 / 173 |      3,120 / 67 |   3,187 / 0 |     974 (30.6%) |      67 (2.1%) |     117 (3.7%) |      0 |    0 |            0 |
| xarray             | 0.4.0-rc.3+dev |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |   3,540 (16.4%) |  3,118 (14.4%) |  3,311 (15.3%) |      0 |    0 |            0 |
| litestar           | 0.4.0-rc.3+dev |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |     596 (28.6%) |     104 (5.0%) |     163 (7.8%) |      0 |    0 |            0 |
| stripe             | 0.4.0-rc.3+dev |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |     564 (13.3%) |     161 (3.8%) |    662 (15.7%) |      0 |    0 |            0 |
| celery             | 0.4.0-rc.3+dev |   0 / 3,750 |      3,417 / 333 |       3,750 / 0 |   3,750 / 0 |     508 (13.5%) |     118 (3.1%) |     357 (9.5%) |      0 |    0 |            0 |
| optuna             | 0.4.0-rc.3+dev |   0 / 3,598 |      3,152 / 478 |      3,598 / 32 |   3,630 / 0 |   1,473 (40.6%) |     199 (5.5%) |     293 (8.1%) |      0 |    0 |            0 |
| dask               | 0.4.0-rc.3+dev |  0 / 24,174 |   22,481 / 1,775 |     24,174 / 82 |  24,256 / 0 |   3,118 (12.9%) |   1,945 (8.0%) |  2,599 (10.7%) |      0 |    3 |            0 |
| mypy               | 0.4.0-rc.3+dev |  0 / 11,401 |    9,204 / 2,583 |    11,401 / 387 |  11,788 / 0 |   4,727 (40.1%) |  1,179 (10.0%) |  1,546 (13.1%) |      0 |    0 |            0 |
| **Total**          | 0.4.0-rc.3+dev | 0 / 420,379 | 379,635 / 44,778 | 420,378 / 4,036 | 424,414 / 0 | 106,540 (25.1%) | 48,640 (11.5%) | 64,769 (15.3%) |      0 |    3 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter    | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | -------------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | 0.4.0-rc.3+dev |              1.2% |         33.7% |            39.4% |                  44.4% | +32.5 pts, 32.9% of untyped | +43.2 pts, 43.7% of untyped |
| django             | 0.4.0-rc.3+dev |              0.0% |         15.3% |            19.0% |                  31.0% | +15.3 pts, 15.3% of untyped | +31.0 pts, 31.0% of untyped |
| sqlalchemy         | 0.4.0-rc.3+dev |             15.3% |         27.5% |            29.7% |                  32.9% | +12.3 pts, 14.5% of untyped | +17.6 pts, 20.8% of untyped |
| pydantic           | 0.4.0-rc.3+dev |             22.4% |         51.9% |            55.6% |                  62.0% | +29.5 pts, 38.0% of untyped | +39.5 pts, 51.0% of untyped |
| pandas             | 0.4.0-rc.3+dev |              1.6% |         23.0% |            52.8% |                  53.7% | +21.4 pts, 21.7% of untyped | +52.1 pts, 53.0% of untyped |
| twisted            | 0.4.0-rc.3+dev |              0.0% |         13.6% |            33.9% |                  39.5% | +13.6 pts, 13.6% of untyped | +39.5 pts, 39.5% of untyped |
| pip                | 0.4.0-rc.3+dev |              1.5% |         26.4% |            31.0% |                  38.6% | +24.9 pts, 25.2% of untyped | +37.1 pts, 37.7% of untyped |
| structlog          | 0.4.0-rc.3+dev |             25.6% |         48.7% |            52.2% |                  55.1% | +23.1 pts, 31.0% of untyped | +29.4 pts, 39.6% of untyped |
| attrs              | 0.4.0-rc.3+dev |              0.8% |         24.2% |            26.5% |                  27.0% | +23.5 pts, 23.7% of untyped | +26.3 pts, 26.5% of untyped |
| click              | 0.4.0-rc.3+dev |             31.5% |         63.6% |            66.7% |                  70.9% | +32.1 pts, 46.9% of untyped | +39.5 pts, 57.6% of untyped |
| hypercorn          | 0.4.0-rc.3+dev |             32.4% |         57.9% |            61.7% |                  69.0% | +25.5 pts, 37.7% of untyped | +36.6 pts, 54.1% of untyped |
| starlette          | 0.4.0-rc.3+dev |             10.3% |         47.8% |            54.6% |                  59.5% | +37.5 pts, 41.8% of untyped | +49.2 pts, 54.8% of untyped |
| werkzeug           | 0.4.0-rc.3+dev |             14.3% |         49.2% |            53.5% |                  57.5% | +34.9 pts, 40.7% of untyped | +43.2 pts, 50.4% of untyped |
| mkdocs             | 0.4.0-rc.3+dev |              4.5% |         37.7% |            53.2% |                  57.1% | +33.2 pts, 34.7% of untyped | +52.5 pts, 55.0% of untyped |
| httpx              | 0.4.0-rc.3+dev |              6.3% |         44.8% |            54.2% |                  56.7% | +38.6 pts, 41.1% of untyped | +50.4 pts, 53.8% of untyped |
| black              | 0.4.0-rc.3+dev |             15.9% |         62.4% |            70.8% |                  73.2% | +46.5 pts, 55.3% of untyped | +57.4 pts, 68.2% of untyped |
| fastapi            | 0.4.0-rc.3+dev |             42.0% |         62.1% |            65.2% |                  67.2% | +20.1 pts, 34.6% of untyped | +25.2 pts, 43.4% of untyped |
| cattrs             | 0.4.0-rc.3+dev |              7.0% |         25.8% |            31.8% |                  34.0% | +18.8 pts, 20.2% of untyped | +27.0 pts, 29.0% of untyped |
| pytest             | 0.4.0-rc.3+dev |             12.1% |         51.5% |            56.1% |                  59.7% | +39.3 pts, 44.8% of untyped | +47.6 pts, 54.2% of untyped |
| botocore           | 0.4.0-rc.3+dev |              0.5% |         14.7% |            19.1% |                  30.3% | +14.3 pts, 14.3% of untyped | +29.8 pts, 29.9% of untyped |
| uvicorn            | 0.4.0-rc.3+dev |             23.6% |         59.7% |            64.2% |                  66.4% | +36.1 pts, 47.2% of untyped | +42.8 pts, 56.0% of untyped |
| mcp                | 0.4.0-rc.3+dev |             30.7% |         58.2% |            64.4% |                  67.7% | +27.5 pts, 39.7% of untyped | +36.9 pts, 53.3% of untyped |
| textual            | 0.4.0-rc.3+dev |             15.6% |         48.8% |            54.9% |                  58.0% | +33.3 pts, 39.4% of untyped | +42.5 pts, 50.3% of untyped |
| pdm                | 0.4.0-rc.3+dev |             11.7% |         48.9% |            55.4% |                  59.0% | +37.2 pts, 42.2% of untyped | +47.3 pts, 53.6% of untyped |
| strawberry-graphql | 0.4.0-rc.3+dev |             30.1% |         53.1% |            59.5% |                  61.4% | +23.1 pts, 33.0% of untyped | +31.3 pts, 44.8% of untyped |
| pygments           | 0.4.0-rc.3+dev |              0.0% |          9.6% |            10.6% |                  12.5% |   +9.6 pts, 9.6% of untyped | +12.5 pts, 12.5% of untyped |
| streamlink         | 0.4.0-rc.3+dev |             42.8% |         55.4% |            57.5% |                  59.7% | +12.7 pts, 22.1% of untyped | +16.9 pts, 29.6% of untyped |
| sphinx             | 0.4.0-rc.3+dev |             10.4% |         45.5% |            50.4% |                  54.4% | +35.1 pts, 39.1% of untyped | +43.9 pts, 49.1% of untyped |
| tox                | 0.4.0-rc.3+dev |             16.0% |         60.9% |            64.7% |                  67.2% | +44.9 pts, 53.4% of untyped | +51.2 pts, 61.0% of untyped |
| pint               | 0.4.0-rc.3+dev |              5.1% |         22.8% |            26.1% |                  27.6% | +17.8 pts, 18.7% of untyped | +22.5 pts, 23.7% of untyped |
| altair             | 0.4.0-rc.3+dev |             49.7% |         60.7% |            62.1% |                  62.5% | +11.0 pts, 21.9% of untyped | +12.8 pts, 25.5% of untyped |
| seaborn            | 0.4.0-rc.3+dev |              6.9% |         27.5% |            31.8% |                  34.6% | +20.5 pts, 22.1% of untyped | +27.7 pts, 29.7% of untyped |
| aiohttp            | 0.4.0-rc.3+dev |             23.7% |         51.5% |            57.3% |                  61.8% | +27.8 pts, 36.5% of untyped | +38.1 pts, 49.9% of untyped |
| websockets         | 0.4.0-rc.3+dev |             13.8% |         49.3% |            55.8% |                  60.9% | +35.5 pts, 41.2% of untyped | +47.1 pts, 54.6% of untyped |
| anyio              | 0.4.0-rc.3+dev |             27.8% |         48.8% |            52.0% |                  54.7% | +21.0 pts, 29.1% of untyped | +27.0 pts, 37.3% of untyped |
| zarr               | 0.4.0-rc.3+dev |             21.7% |         56.3% |            58.7% |                  59.9% | +34.7 pts, 44.3% of untyped | +38.2 pts, 48.8% of untyped |
| joblib             | 0.4.0-rc.3+dev |              0.0% |         23.5% |            31.4% |                  34.4% | +23.4 pts, 23.4% of untyped | +34.3 pts, 34.3% of untyped |
| networkx           | 0.4.0-rc.3+dev |              0.3% |         17.9% |            27.6% |                  28.5% | +17.6 pts, 17.7% of untyped | +28.2 pts, 28.3% of untyped |
| nibabel            | 0.4.0-rc.3+dev |              1.0% |         22.6% |            30.5% |                  33.4% | +21.6 pts, 21.8% of untyped | +32.4 pts, 32.7% of untyped |
| narwhals           | 0.4.0-rc.3+dev |             21.7% |         46.1% |            47.8% |                  49.1% | +24.4 pts, 31.2% of untyped | +27.4 pts, 35.0% of untyped |
| xarray             | 0.4.0-rc.3+dev |              4.6% |         20.4% |            34.4% |                  35.2% | +15.8 pts, 16.6% of untyped | +30.6 pts, 32.1% of untyped |
| litestar           | 0.4.0-rc.3+dev |             44.9% |         62.2% |            65.2% |                  66.9% | +17.2 pts, 31.3% of untyped | +21.9 pts, 39.8% of untyped |
| stripe             | 0.4.0-rc.3+dev |             89.5% |         91.3% |            91.8% |                  93.4% |  +1.8 pts, 16.8% of untyped |  +3.8 pts, 36.5% of untyped |
| celery             | 0.4.0-rc.3+dev |              0.4% |         13.9% |            17.1% |                  23.4% | +13.5 pts, 13.6% of untyped | +23.0 pts, 23.1% of untyped |
| optuna             | 0.4.0-rc.3+dev |              7.5% |         45.4% |            50.5% |                  52.9% | +37.9 pts, 40.9% of untyped | +45.4 pts, 49.1% of untyped |
| dask               | 0.4.0-rc.3+dev |              1.1% |         13.8% |            21.8% |                  24.5% | +12.8 pts, 12.9% of untyped | +23.4 pts, 23.7% of untyped |
| mypy               | 0.4.0-rc.3+dev |             16.8% |         51.3% |            59.9% |                  62.6% | +34.5 pts, 41.5% of untyped | +45.8 pts, 55.0% of untyped |
| **Total**          | 0.4.0-rc.3+dev |             11.4% |         33.8% |            44.1% |                  47.5% | +22.5 pts, 25.3% of untyped | +36.1 pts, 40.8% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,415 |  37,415 |        |        |      0 |    0 | 38,744 |  115,001 |    52.3 |
| standard library   | likely             | 43,945 |  37,648 |  6,297 |        |      0 |    0 | 45,274 |  115,001 |    81.4 |
| standard library   | unsafe             | 49,719 |  37,422 |  6,289 |  6,008 |      0 |    0 | 51,048 |  115,001 |    61.3 |
| standard library   | infer-basedpyright | 58,005 |  37,433 |  6,797 | 13,775 |      0 |   10 | 59,334 |  115,001 |   902.5 |
| standard library   | infer-ty           | 55,681 |  37,436 |  6,753 | 11,492 |      0 |   11 | 57,010 |  115,001 |   119.1 |
| standard library   | infer-pyrefly      | 58,001 |  37,432 |  6,832 | 13,737 |      0 |   42 | 59,330 |  115,001 |   105.1 |
| django             | certain            |  2,627 |   2,627 |        |        |      0 |    0 |  2,632 |   17,181 |    11.6 |
| django             | likely             |  3,261 |   2,633 |    628 |        |      0 |    0 |  3,266 |   17,181 |    14.4 |
| django             | unsafe             |  5,320 |   2,627 |    627 |  2,066 |      0 |    0 |  5,325 |   17,181 |    10.3 |
| django             | infer-basedpyright |  5,766 |   2,626 |    645 |  2,495 |      0 |    0 |  5,771 |   17,181 |    56.4 |
| django             | infer-ty           |  5,552 |   2,628 |    636 |  2,288 |      0 |    0 |  5,557 |   17,181 |    45.7 |
| django             | infer-pyrefly      |  6,023 |   2,616 |    651 |  2,756 |      0 |    4 |  6,028 |   17,181 |    20.5 |
| django             | infer-trace        |  5,861 |   2,627 |    659 |  2,575 |      0 |    0 |  5,866 |   17,181 |    14.9 |
| sqlalchemy         | certain            |  1,881 |   1,881 |        |        |      0 |    0 |  4,216 |   15,304 |     8.5 |
| sqlalchemy         | likely             |  2,215 |   1,888 |    327 |        |      0 |    0 |  4,550 |   15,304 |    10.9 |
| sqlalchemy         | unsafe             |  2,699 |   1,881 |    327 |    491 |      0 |    0 |  5,034 |   15,304 |    10.5 |
| sqlalchemy         | infer-basedpyright |  3,517 |   1,876 |    366 |  1,275 |      0 |    0 |  5,852 |   15,304 |    42.6 |
| sqlalchemy         | infer-ty           |  3,465 |   1,876 |    353 |  1,236 |      0 |    0 |  5,800 |   15,304 |    19.0 |
| sqlalchemy         | infer-pyrefly      |  3,201 |   1,875 |    345 |    981 |      0 |    0 |  5,536 |   15,304 |    14.5 |
| sqlalchemy         | infer-trace        |  2,841 |   1,881 |    327 |    633 |      0 |    0 |  5,176 |   15,304 |    14.5 |
| pydantic           | certain            |  1,185 |   1,185 |        |        |      0 |    0 |  2,087 |    4,019 |     1.7 |
| pydantic           | likely             |  1,331 |   1,193 |    138 |        |      0 |    0 |  2,233 |    4,019 |     2.4 |
| pydantic           | unsafe             |  1,589 |   1,185 |    137 |    267 |      0 |    0 |  2,491 |    4,019 |     4.1 |
| pydantic           | infer-basedpyright |  1,817 |   1,186 |    141 |    490 |      0 |    0 |  2,719 |    4,019 |    29.2 |
| pydantic           | infer-ty           |  1,730 |   1,185 |    136 |    409 |      0 |    0 |  2,632 |    4,019 |     4.0 |
| pydantic           | infer-pyrefly      |  1,794 |   1,185 |    137 |    472 |      0 |    0 |  2,696 |    4,019 |     4.9 |
| pydantic           | infer-trace        |  1,590 |   1,185 |    137 |    268 |      0 |    0 |  2,492 |    4,019 |     6.0 |
| pandas             | certain            | 16,910 |  16,910 |        |        |      0 |    0 | 18,179 |   79,062 |    36.9 |
| pandas             | likely             | 40,460 |  17,097 | 23,363 |        |      0 |    0 | 41,729 |   79,062 |    82.1 |
| pandas             | unsafe             | 41,209 |  16,906 | 23,142 |  1,161 |      0 |    0 | 42,478 |   79,062 |    38.3 |
| pandas             | infer-basedpyright | 47,166 |  16,897 | 23,339 |  6,930 |      0 |    3 | 48,435 |   79,062 |   999.2 |
| pandas             | infer-ty           | 46,900 |  16,905 | 23,338 |  6,657 |      0 |    3 | 48,169 |   79,062 |   115.1 |
| pandas             | infer-pyrefly      | 48,140 |  16,908 | 23,352 |  7,880 |      0 |    9 | 49,409 |   79,062 |    66.5 |
| pandas             | infer-trace        | 42,604 |  16,906 | 23,103 |  2,595 |      0 |    9 | 43,873 |   79,062 |    37.4 |
| twisted            | certain            |  2,439 |   2,439 |        |        |      0 |    0 |  2,439 |   17,874 |     5.3 |
| twisted            | likely             |  6,059 |   2,562 |  3,497 |        |      0 |    0 |  6,059 |   17,874 |     8.9 |
| twisted            | unsafe             |  7,063 |   2,438 |  3,497 |  1,128 |      0 |    0 |  7,063 |   17,874 |     5.8 |
| twisted            | infer-basedpyright |  8,495 |   2,443 |  3,526 |  2,526 |      0 |    0 |  8,495 |   17,874 |    52.7 |
| twisted            | infer-ty           |  7,475 |   2,438 |  3,521 |  1,516 |      0 |    0 |  7,475 |   17,874 |    15.5 |
| twisted            | infer-pyrefly      |  7,492 |   2,438 |  3,511 |  1,543 |      0 |    0 |  7,492 |   17,874 |    14.6 |
| pip                | certain            |  2,254 |   2,254 |        |        |      0 |    0 |  2,391 |    9,064 |     4.8 |
| pip                | likely             |  2,675 |   2,267 |    408 |        |      0 |    0 |  2,812 |    9,064 |     6.3 |
| pip                | unsafe             |  3,363 |   2,254 |    408 |    701 |      0 |    0 |  3,500 |    9,064 |     4.2 |
| pip                | infer-basedpyright |  4,155 |   2,259 |    463 |  1,433 |      0 |    3 |  4,292 |    9,064 |    31.4 |
| pip                | infer-ty           |  3,685 |   2,256 |    434 |    995 |      0 |    2 |  3,822 |    9,064 |    10.4 |
| pip                | infer-pyrefly      |  3,904 |   2,256 |    445 |  1,203 |      0 |    0 |  4,041 |    9,064 |     9.4 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.5 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.6 |
| structlog          | unsafe             |    125 |      98 |     15 |     12 |      0 |    0 |    234 |      425 |     0.5 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     4.0 |
| structlog          | infer-ty           |    136 |      98 |     16 |     22 |      0 |    0 |    245 |      425 |     1.0 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     0.8 |
| structlog          | infer-trace        |    125 |      98 |     15 |     12 |      0 |    0 |    234 |      425 |     1.0 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     0.6 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     0.7 |
| attrs              | unsafe             |    104 |      93 |      8 |      3 |      0 |    0 |    107 |      396 |     2.2 |
| attrs              | infer-basedpyright |    130 |      93 |      8 |     29 |      0 |    0 |    133 |      396 |     5.6 |
| attrs              | infer-ty           |    115 |      93 |      8 |     14 |      0 |    0 |    118 |      396 |     1.5 |
| attrs              | infer-pyrefly      |    120 |      93 |      8 |     19 |      0 |    0 |    123 |      396 |     1.6 |
| attrs              | infer-trace        |    107 |      93 |      9 |      5 |      0 |    0 |    110 |      396 |     0.6 |
| click              | certain            |    285 |     285 |        |        |      0 |    0 |    564 |      887 |     0.5 |
| click              | likely             |    313 |     286 |     27 |        |      0 |    0 |    592 |      887 |     1.1 |
| click              | unsafe             |    350 |     285 |     27 |     38 |      0 |    0 |    629 |      887 |     1.8 |
| click              | infer-basedpyright |    432 |     286 |     30 |    116 |      0 |    0 |    711 |      887 |     7.1 |
| click              | infer-ty           |    451 |     286 |     27 |    138 |      0 |    0 |    730 |      887 |     1.4 |
| click              | infer-pyrefly      |    438 |     285 |     32 |    121 |      0 |    0 |    717 |      887 |     1.5 |
| click              | infer-trace        |    350 |     285 |     27 |     38 |      0 |    0 |    629 |      887 |     1.0 |
| hypercorn          | certain            |    134 |     134 |        |        |      0 |    0 |    304 |      525 |     0.5 |
| hypercorn          | likely             |    154 |     134 |     20 |        |      0 |    0 |    324 |      525 |     0.6 |
| hypercorn          | unsafe             |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     2.0 |
| hypercorn          | infer-basedpyright |    214 |     134 |     21 |     59 |      0 |    0 |    384 |      525 |     2.0 |
| hypercorn          | infer-ty           |    219 |     134 |     21 |     64 |      0 |    0 |    389 |      525 |     0.8 |
| hypercorn          | infer-pyrefly      |    201 |     134 |     20 |     47 |      0 |    0 |    371 |      525 |     1.1 |
| hypercorn          | infer-trace        |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     0.7 |
| starlette          | certain            |    311 |     311 |        |        |      0 |    0 |    396 |      829 |     0.6 |
| starlette          | likely             |    368 |     311 |     57 |        |      0 |    0 |    453 |      829 |     0.7 |
| starlette          | unsafe             |    408 |     311 |     57 |     40 |      0 |    0 |    493 |      829 |     2.6 |
| starlette          | infer-basedpyright |    484 |     311 |     57 |    116 |      0 |    0 |    569 |      829 |     2.4 |
| starlette          | infer-ty           |    467 |     311 |     56 |    100 |      0 |    0 |    552 |      829 |     1.2 |
| starlette          | infer-pyrefly      |    446 |     311 |     56 |     79 |      0 |    0 |    531 |      829 |     1.6 |
| starlette          | infer-trace        |    408 |     311 |     57 |     40 |      0 |    0 |    493 |      829 |     1.3 |
| werkzeug           | certain            |    526 |     526 |        |        |      0 |    0 |    742 |    1,509 |     1.0 |
| werkzeug           | likely             |    591 |     527 |     64 |        |      0 |    0 |    807 |    1,509 |     1.2 |
| werkzeug           | unsafe             |    652 |     526 |     64 |     62 |      0 |    0 |    868 |    1,509 |     0.8 |
| werkzeug           | infer-basedpyright |    775 |     526 |     76 |    173 |      0 |    0 |    991 |    1,509 |     4.7 |
| werkzeug           | infer-ty           |    799 |     526 |     79 |    194 |      0 |    0 |  1,015 |    1,509 |     1.5 |
| werkzeug           | infer-pyrefly      |    809 |     527 |     69 |    213 |      0 |    0 |  1,025 |    1,509 |     2.2 |
| werkzeug           | infer-trace        |    652 |     526 |     64 |     62 |      0 |    0 |    868 |    1,509 |     2.2 |
| mkdocs             | certain            |    810 |     810 |        |        |      0 |    0 |    921 |    2,443 |     1.2 |
| mkdocs             | likely             |  1,189 |     840 |    349 |        |      0 |    0 |  1,300 |    2,443 |     1.4 |
| mkdocs             | unsafe             |  1,283 |     810 |    349 |    124 |      0 |    0 |  1,394 |    2,443 |     1.2 |
| mkdocs             | infer-basedpyright |  1,382 |     810 |    356 |    216 |      0 |    0 |  1,493 |    2,443 |     6.9 |
| mkdocs             | infer-ty           |  1,416 |     810 |    361 |    245 |      0 |    0 |  1,527 |    2,443 |     2.0 |
| mkdocs             | infer-pyrefly      |  1,381 |     810 |    357 |    214 |      0 |    0 |  1,492 |    2,443 |     2.3 |
| mkdocs             | infer-trace        |  1,295 |     811 |    348 |    136 |      0 |    0 |  1,406 |    2,443 |     4.4 |
| httpx              | certain            |    234 |     234 |        |        |      0 |    0 |    272 |      607 |     0.4 |
| httpx              | likely             |    291 |     243 |     48 |        |      0 |    0 |    329 |      607 |     0.9 |
| httpx              | unsafe             |    306 |     234 |     48 |     24 |      0 |    0 |    344 |      607 |     2.1 |
| httpx              | infer-basedpyright |    391 |     234 |     53 |    104 |      0 |    0 |    429 |      607 |     5.4 |
| httpx              | infer-ty           |    375 |     235 |     52 |     88 |      0 |    0 |    413 |      607 |     2.9 |
| httpx              | infer-pyrefly      |    352 |     234 |     51 |     67 |      0 |    0 |    390 |      607 |     1.0 |
| httpx              | infer-trace        |    306 |     234 |     48 |     24 |      0 |    0 |    344 |      607 |     0.9 |
| black              | certain            |    704 |     704 |        |        |      0 |    0 |    944 |    1,513 |     0.8 |
| black              | likely             |    831 |     717 |    114 |        |      0 |    0 |  1,071 |    1,513 |     0.8 |
| black              | unsafe             |    868 |     704 |    114 |     50 |      0 |    0 |  1,108 |    1,513 |     1.2 |
| black              | infer-basedpyright |    942 |     704 |    114 |    124 |      0 |    0 |  1,182 |    1,513 |     8.8 |
| black              | infer-ty           |    927 |     704 |    114 |    109 |      0 |    0 |  1,167 |    1,513 |     1.1 |
| black              | infer-pyrefly      |    913 |     704 |    112 |     97 |      0 |    0 |  1,153 |    1,513 |     1.8 |
| black              | infer-trace        |    868 |     704 |    114 |     50 |      0 |    0 |  1,108 |    1,513 |     1.1 |
| fastapi            | certain            |    257 |     257 |        |        |      0 |    0 |    794 |    1,279 |     0.9 |
| fastapi            | likely             |    297 |     263 |     34 |        |      0 |    0 |    834 |    1,279 |     2.5 |
| fastapi            | unsafe             |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     3.2 |
| fastapi            | infer-basedpyright |    348 |     257 |     33 |     58 |      0 |    0 |    885 |    1,279 |     7.5 |
| fastapi            | infer-ty           |    371 |     257 |     32 |     82 |      0 |    0 |    908 |    1,279 |     2.4 |
| fastapi            | infer-pyrefly      |    345 |     257 |     34 |     54 |      0 |    0 |    882 |    1,279 |     2.3 |
| fastapi            | infer-trace        |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     1.0 |
| cattrs             | certain            |    105 |     105 |        |        |      0 |    0 |    144 |      559 |     0.5 |
| cattrs             | likely             |    139 |     112 |     27 |        |      0 |    0 |    178 |      559 |     0.8 |
| cattrs             | unsafe             |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     0.7 |
| cattrs             | infer-basedpyright |    194 |     107 |     29 |     58 |      0 |    0 |    233 |      559 |     6.0 |
| cattrs             | infer-ty           |    195 |     105 |     27 |     63 |      0 |    0 |    234 |      559 |     1.1 |
| cattrs             | infer-pyrefly      |    182 |     105 |     28 |     49 |      0 |    0 |    221 |      559 |     1.9 |
| cattrs             | infer-trace        |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     0.9 |
| pytest             | certain            |  1,344 |   1,344 |        |        |      0 |    0 |  1,759 |    3,418 |     1.7 |
| pytest             | likely             |  1,503 |   1,348 |    155 |        |      0 |    0 |  1,918 |    3,418 |     2.5 |
| pytest             | unsafe             |  1,627 |   1,344 |    155 |    128 |      0 |    0 |  2,042 |    3,418 |     2.5 |
| pytest             | infer-basedpyright |  1,980 |   1,342 |    173 |    465 |      0 |    0 |  2,395 |    3,418 |     8.4 |
| pytest             | infer-ty           |  1,989 |   1,342 |    175 |    472 |      0 |    0 |  2,404 |    3,418 |     3.3 |
| pytest             | infer-pyrefly      |  2,055 |   1,342 |    175 |    538 |      0 |    0 |  2,470 |    3,418 |     4.2 |
| pytest             | infer-trace        |  1,639 |   1,344 |    155 |    140 |      0 |    0 |  2,054 |    3,418 |     2.2 |
| botocore           | certain            |    543 |     543 |        |        |      0 |    0 |    561 |    3,806 |     2.1 |
| botocore           | likely             |    709 |     549 |    160 |        |      0 |    0 |    727 |    3,806 |     2.6 |
| botocore           | unsafe             |  1,134 |     541 |    160 |    433 |      0 |    0 |  1,152 |    3,806 |     2.1 |
| botocore           | infer-basedpyright |  1,282 |     536 |    163 |    583 |      0 |    0 |  1,300 |    3,806 |    10.0 |
| botocore           | infer-ty           |  1,196 |     541 |    161 |    494 |      0 |    3 |  1,214 |    3,806 |     3.2 |
| botocore           | infer-pyrefly      |  1,277 |     537 |    166 |    574 |      0 |    0 |  1,295 |    3,806 |     3.5 |
| botocore           | infer-trace        |  1,480 |     541 |    186 |    753 |      0 |    0 |  1,498 |    3,806 |     3.3 |
| uvicorn            | certain            |    231 |     231 |        |        |      0 |    0 |    382 |      640 |     0.5 |
| uvicorn            | likely             |    260 |     231 |     29 |        |      0 |    0 |    411 |      640 |     0.9 |
| uvicorn            | unsafe             |    274 |     231 |     29 |     14 |      0 |    0 |    425 |      640 |     0.8 |
| uvicorn            | infer-basedpyright |    347 |     231 |     32 |     84 |      0 |    0 |    498 |      640 |     6.3 |
| uvicorn            | infer-ty           |    324 |     231 |     29 |     64 |      0 |    0 |    475 |      640 |     1.5 |
| uvicorn            | infer-pyrefly      |    300 |     231 |     32 |     37 |      0 |    0 |    451 |      640 |     1.8 |
| uvicorn            | infer-trace        |    274 |     231 |     29 |     14 |      0 |    0 |    425 |      640 |     1.0 |
| mcp                | certain            |    683 |     683 |        |        |      0 |    0 |  1,446 |    2,483 |     1.2 |
| mcp                | likely             |    837 |     689 |    148 |        |      0 |    0 |  1,600 |    2,483 |     1.9 |
| mcp                | unsafe             |    917 |     683 |    148 |     86 |      0 |    0 |  1,680 |    2,483 |     2.1 |
| mcp                | infer-basedpyright |  1,049 |     683 |    160 |    206 |      0 |    0 |  1,812 |    2,483 |     7.6 |
| mcp                | infer-ty           |  1,037 |     683 |    155 |    199 |      0 |    0 |  1,800 |    2,483 |     2.3 |
| mcp                | infer-pyrefly      |  1,008 |     683 |    153 |    172 |      0 |    0 |  1,771 |    2,483 |     2.7 |
| mcp                | infer-trace        |    917 |     683 |    148 |     86 |      0 |    0 |  1,680 |    2,483 |     1.3 |
| textual            | certain            |  2,553 |   2,553 |        |        |      0 |    0 |  3,747 |    7,677 |     2.4 |
| textual            | likely             |  3,024 |   2,577 |    447 |        |      0 |    0 |  4,218 |    7,677 |     3.4 |
| textual            | unsafe             |  3,260 |   2,553 |    446 |    261 |      0 |    0 |  4,454 |    7,677 |     2.0 |
| textual            | infer-basedpyright |  4,537 |   2,554 |    524 |  1,459 |      0 |   20 |  5,731 |    7,677 |    16.6 |
| textual            | infer-ty           |  4,658 |   2,554 |    530 |  1,574 |      0 |    0 |  5,852 |    7,677 |     4.7 |
| textual            | infer-pyrefly      |  3,742 |   2,554 |    469 |    719 |      0 |    0 |  4,936 |    7,677 |     5.2 |
| pdm                | certain            |  1,146 |   1,146 |        |        |      0 |    0 |  1,507 |    3,079 |     1.7 |
| pdm                | likely             |  1,344 |   1,159 |    185 |        |      0 |    0 |  1,705 |    3,079 |     2.6 |
| pdm                | unsafe             |  1,456 |   1,146 |    184 |    126 |      0 |    0 |  1,817 |    3,079 |     6.4 |
| pdm                | infer-basedpyright |  1,850 |   1,149 |    213 |    488 |      0 |    0 |  2,211 |    3,079 |     8.9 |
| pdm                | infer-ty           |  1,842 |   1,149 |    213 |    480 |      0 |    0 |  2,203 |    3,079 |     3.7 |
| pdm                | infer-pyrefly      |  1,619 |   1,147 |    194 |    278 |      0 |    0 |  1,980 |    3,079 |     4.1 |
| pdm                | infer-trace        |  1,456 |   1,146 |    184 |    126 |      0 |    0 |  1,817 |    3,079 |     2.1 |
| strawberry-graphql | certain            |    596 |     596 |        |        |      0 |    0 |  1,372 |    2,582 |     1.5 |
| strawberry-graphql | likely             |    760 |     598 |    162 |        |      0 |    0 |  1,536 |    2,582 |     2.3 |
| strawberry-graphql | unsafe             |    809 |     596 |    162 |     51 |      0 |    0 |  1,585 |    2,582 |     2.5 |
| strawberry-graphql | infer-basedpyright |    982 |     595 |    162 |    225 |      0 |    0 |  1,758 |    2,582 |     9.4 |
| strawberry-graphql | infer-ty           |    975 |     595 |    161 |    219 |      0 |    0 |  1,751 |    2,582 |     3.2 |
| strawberry-graphql | infer-pyrefly      |    872 |     595 |    163 |    114 |      0 |    0 |  1,648 |    2,582 |     3.7 |
| strawberry-graphql | infer-trace        |    809 |     596 |    162 |     51 |      0 |    0 |  1,585 |    2,582 |     1.8 |
| pygments           | certain            |    735 |     735 |        |        |      0 |    0 |    735 |    7,666 |     2.2 |
| pygments           | likely             |    814 |     738 |     76 |        |      0 |    0 |    814 |    7,666 |     3.1 |
| pygments           | unsafe             |    956 |     735 |     76 |    145 |      0 |    0 |    956 |    7,666 |     2.3 |
| pygments           | infer-basedpyright |  1,070 |     735 |     83 |    252 |      0 |    0 |  1,070 |    7,666 |    13.4 |
| pygments           | infer-ty           |  1,070 |     735 |     84 |    251 |      0 |    0 |  1,070 |    7,666 |     4.5 |
| pygments           | infer-pyrefly      |  1,133 |     735 |     84 |    314 |      0 |    0 |  1,133 |    7,666 |     6.0 |
| pygments           | infer-trace        |  1,067 |     730 |    100 |    237 |      0 |    0 |  1,067 |    7,666 |     3.8 |
| streamlink         | certain            |    670 |     670 |        |        |      0 |    0 |  2,932 |    5,291 |     1.7 |
| streamlink         | likely             |    778 |     673 |    105 |        |      0 |    0 |  3,040 |    5,291 |     2.5 |
| streamlink         | unsafe             |    896 |     670 |    105 |    121 |      0 |    0 |  3,158 |    5,291 |     2.3 |
| streamlink         | infer-basedpyright |  1,309 |     671 |    127 |    511 |      0 |    0 |  3,571 |    5,291 |     9.8 |
| streamlink         | infer-ty           |  1,462 |     670 |    138 |    654 |      0 |    0 |  3,724 |    5,291 |     4.5 |
| streamlink         | infer-pyrefly      |  1,088 |     670 |    118 |    300 |      0 |    0 |  3,350 |    5,291 |     7.0 |
| streamlink         | infer-trace        |    904 |     670 |    105 |    129 |      0 |    0 |  3,166 |    5,291 |     3.4 |
| sphinx             | certain            |  3,121 |   3,121 |        |        |      0 |    0 |  4,049 |    8,901 |     2.5 |
| sphinx             | likely             |  3,561 |   3,131 |    430 |        |      0 |    0 |  4,489 |    8,901 |     4.2 |
| sphinx             | unsafe             |  3,912 |   3,121 |    429 |    362 |      0 |    0 |  4,840 |    8,901 |     3.9 |
| sphinx             | infer-basedpyright |  4,709 |   3,122 |    458 |  1,129 |      0 |    0 |  5,637 |    8,901 |    14.9 |
| sphinx             | infer-ty           |  4,780 |   3,121 |    453 |  1,206 |      0 |    0 |  5,708 |    8,901 |     8.2 |
| sphinx             | infer-pyrefly      |  5,070 |   3,122 |    472 |  1,476 |      0 |    0 |  5,998 |    8,901 |     5.7 |
| sphinx             | infer-trace        |  3,912 |   3,121 |    429 |    362 |      0 |    0 |  4,840 |    8,901 |     4.1 |
| tox                | certain            |    941 |     941 |        |        |      0 |    0 |  1,277 |    2,098 |     1.0 |
| tox                | likely             |  1,021 |     942 |     79 |        |      0 |    0 |  1,357 |    2,098 |     1.5 |
| tox                | unsafe             |  1,074 |     941 |     79 |     54 |      0 |    0 |  1,410 |    2,098 |     2.0 |
| tox                | infer-basedpyright |  1,335 |     943 |     96 |    296 |      0 |    0 |  1,671 |    2,098 |    12.9 |
| tox                | infer-ty           |  1,370 |     943 |     95 |    332 |      0 |    0 |  1,706 |    2,098 |     2.5 |
| tox                | infer-pyrefly      |  1,419 |     943 |     95 |    381 |      0 |    0 |  1,755 |    2,098 |     2.5 |
| tox                | infer-trace        |  1,074 |     941 |     79 |     54 |      0 |    0 |  1,410 |    2,098 |     1.3 |
| pint               | certain            |    576 |     576 |        |        |      0 |    0 |    741 |    3,243 |     2.6 |
| pint               | likely             |    680 |     582 |     98 |        |      0 |    0 |    845 |    3,243 |     3.8 |
| pint               | unsafe             |    730 |     576 |     98 |     56 |      0 |    0 |    895 |    3,243 |     2.2 |
| pint               | infer-basedpyright |  1,011 |     572 |    102 |    337 |      0 |    0 |  1,176 |    3,243 |    27.8 |
| pint               | infer-ty           |    913 |     572 |     95 |    246 |      0 |    0 |  1,078 |    3,243 |     4.8 |
| pint               | infer-pyrefly      |    807 |     572 |     92 |    143 |      0 |    0 |    972 |    3,243 |     3.7 |
| pint               | infer-trace        |    735 |     576 |     98 |     61 |      0 |    0 |    900 |    3,243 |     2.8 |
| altair             | certain            |    373 |     373 |        |        |      0 |    0 |  2,055 |    3,383 |     3.2 |
| altair             | likely             |    420 |     373 |     47 |        |      0 |    0 |  2,102 |    3,383 |     5.8 |
| altair             | unsafe             |    433 |     373 |     47 |     13 |      0 |    0 |  2,115 |    3,383 |     6.1 |
| altair             | infer-basedpyright |    506 |     370 |     51 |     85 |      0 |    0 |  2,188 |    3,383 |    13.6 |
| altair             | infer-ty           |    499 |     370 |     48 |     81 |      0 |    3 |  2,181 |    3,383 |     8.0 |
| altair             | infer-pyrefly      |    493 |     370 |     48 |     75 |      0 |    0 |  2,175 |    3,383 |     8.6 |
| altair             | infer-trace        |    440 |     373 |     48 |     19 |      0 |    0 |  2,122 |    3,383 |     3.8 |
| seaborn            | certain            |    639 |     639 |        |        |      0 |    0 |    854 |    3,110 |     2.5 |
| seaborn            | likely             |    775 |     647 |    128 |        |      0 |    0 |    990 |    3,110 |     3.7 |
| seaborn            | unsafe             |    861 |     639 |    128 |     94 |      0 |    0 |  1,076 |    3,110 |     4.5 |
| seaborn            | infer-basedpyright |    975 |     639 |    131 |    205 |      0 |    4 |  1,190 |    3,110 |    23.4 |
| seaborn            | infer-ty           |    950 |     638 |    130 |    182 |      0 |    0 |  1,165 |    3,110 |     5.1 |
| seaborn            | infer-pyrefly      |  1,036 |     639 |    131 |    266 |      0 |    0 |  1,251 |    3,110 |     6.2 |
| seaborn            | infer-trace        |    898 |     639 |    130 |    129 |      0 |    0 |  1,113 |    3,110 |     3.4 |
| aiohttp            | certain            |    677 |     677 |        |        |      0 |    0 |  1,253 |    2,433 |     1.3 |
| aiohttp            | likely             |    818 |     683 |    135 |        |      0 |    0 |  1,394 |    2,433 |     2.4 |
| aiohttp            | unsafe             |    927 |     677 |    135 |    115 |      0 |    0 |  1,503 |    2,433 |     1.5 |
| aiohttp            | infer-basedpyright |  1,130 |     681 |    143 |    306 |      0 |    0 |  1,706 |    2,433 |    19.5 |
| aiohttp            | infer-ty           |  1,157 |     681 |    142 |    334 |      0 |    0 |  1,733 |    2,433 |     4.7 |
| aiohttp            | infer-pyrefly      |  1,266 |     681 |    148 |    437 |      0 |    0 |  1,842 |    2,433 |     5.9 |
| aiohttp            | infer-trace        |    927 |     677 |    135 |    115 |      0 |    0 |  1,503 |    2,433 |     1.6 |
| websockets         | certain            |    326 |     326 |        |        |      0 |    0 |    453 |      918 |     0.7 |
| websockets         | likely             |    385 |     327 |     58 |        |      0 |    0 |    512 |      918 |     1.2 |
| websockets         | unsafe             |    432 |     326 |     58 |     48 |      0 |    0 |    559 |      918 |     1.5 |
| websockets         | infer-basedpyright |    551 |     328 |     58 |    165 |      0 |    0 |    678 |      918 |     3.9 |
| websockets         | infer-ty           |    558 |     328 |     58 |    172 |      0 |    0 |    685 |      918 |     1.2 |
| websockets         | infer-pyrefly      |    587 |     328 |     58 |    201 |      0 |    0 |    714 |      918 |     1.5 |
| websockets         | infer-trace        |    432 |     326 |     58 |     48 |      0 |    0 |    559 |      918 |     1.4 |
| anyio              | certain            |    208 |     208 |        |        |      0 |    0 |    483 |      990 |     1.1 |
| anyio              | likely             |    240 |     208 |     32 |        |      0 |    0 |    515 |      990 |     1.4 |
| anyio              | unsafe             |    267 |     208 |     32 |     27 |      0 |    0 |    542 |      990 |     1.3 |
| anyio              | infer-basedpyright |    363 |     208 |     40 |    115 |      0 |    0 |    638 |      990 |     5.4 |
| anyio              | infer-ty           |    397 |     208 |     43 |    146 |      0 |    0 |    672 |      990 |     2.5 |
| anyio              | infer-pyrefly      |    374 |     208 |     39 |    127 |      0 |    0 |    649 |      990 |     2.1 |
| anyio              | infer-trace        |    267 |     208 |     32 |     27 |      0 |    0 |    542 |      990 |     1.7 |
| zarr               | certain            |  1,067 |   1,067 |        |        |      0 |    0 |  1,735 |    3,079 |     1.4 |
| zarr               | likely             |  1,139 |   1,068 |     71 |        |      0 |    0 |  1,807 |    3,079 |     3.0 |
| zarr               | unsafe             |  1,176 |   1,067 |     71 |     38 |      0 |    0 |  1,844 |    3,079 |     2.3 |
| zarr               | infer-basedpyright |  1,639 |   1,067 |     98 |    474 |      0 |    0 |  2,307 |    3,079 |    12.6 |
| zarr               | infer-ty           |  1,590 |   1,067 |     97 |    426 |      0 |    0 |  2,258 |    3,079 |     3.1 |
| zarr               | infer-pyrefly      |  1,345 |   1,067 |     79 |    199 |      0 |    0 |  2,013 |    3,079 |     3.7 |
| zarr               | infer-trace        |  1,176 |   1,067 |     71 |     38 |      0 |    0 |  1,844 |    3,079 |     2.4 |
| joblib             | certain            |    525 |     525 |        |        |      0 |    0 |    526 |    2,241 |     1.7 |
| joblib             | likely             |    703 |     526 |    177 |        |      0 |    0 |    704 |    2,241 |     4.1 |
| joblib             | unsafe             |    769 |     525 |    177 |     67 |      0 |    0 |    770 |    2,241 |     2.3 |
| joblib             | infer-basedpyright |    897 |     525 |    186 |    186 |      0 |    0 |    898 |    2,241 |    27.0 |
| joblib             | infer-ty           |    843 |     525 |    183 |    135 |      0 |    0 |    844 |    2,241 |     3.0 |
| joblib             | infer-pyrefly      |    889 |     523 |    185 |    181 |      0 |    0 |    890 |    2,241 |     3.1 |
| joblib             | infer-trace        |    780 |     525 |    179 |     76 |      0 |    0 |    781 |    2,241 |     2.2 |
| networkx           | certain            |  3,969 |   3,969 |        |        |      0 |    0 |  4,031 |   22,518 |     5.1 |
| networkx           | likely             |  6,155 |   4,018 |  2,137 |        |      0 |    0 |  6,217 |   22,518 |    11.0 |
| networkx           | unsafe             |  6,358 |   3,969 |  2,084 |    305 |      0 |    0 |  6,420 |   22,518 |     6.7 |
| networkx           | infer-basedpyright |  7,408 |   3,969 |  2,193 |  1,246 |      0 |    0 |  7,470 |   22,518 |    55.3 |
| networkx           | infer-ty           |  6,857 |   3,969 |  2,149 |    739 |      0 |    0 |  6,919 |   22,518 |    16.0 |
| networkx           | infer-pyrefly      |  6,942 |   3,971 |  2,157 |    814 |      0 |    2 |  7,004 |   22,518 |    17.2 |
| networkx           | infer-trace        |  6,786 |   3,969 |  2,113 |    704 |      0 |    0 |  6,848 |   22,518 |     6.8 |
| nibabel            | certain            |  1,849 |   1,849 |        |        |      0 |    0 |  1,931 |    8,550 |     4.3 |
| nibabel            | likely             |  2,529 |   1,873 |    656 |        |      0 |    0 |  2,611 |    8,550 |     9.2 |
| nibabel            | unsafe             |  2,770 |   1,849 |    655 |    266 |      0 |    0 |  2,852 |    8,550 |     4.5 |
| nibabel            | infer-basedpyright |  3,385 |   1,850 |    695 |    840 |      0 |    0 |  3,467 |    8,550 |    51.2 |
| nibabel            | infer-ty           |  3,361 |   1,850 |    712 |    799 |      0 |    0 |  3,443 |    8,550 |    32.0 |
| nibabel            | infer-pyrefly      |  3,204 |   1,849 |    665 |    690 |      0 |    0 |  3,286 |    8,550 |    11.6 |
| nibabel            | infer-trace        |  2,853 |   1,849 |    661 |    343 |      0 |    0 |  2,935 |    8,550 |     5.6 |
| narwhals           | certain            |    974 |     974 |        |        |      0 |    0 |  1,839 |    3,985 |     1.7 |
| narwhals           | likely             |  1,041 |     975 |     66 |        |      0 |    0 |  1,906 |    3,985 |     3.7 |
| narwhals           | unsafe             |  1,091 |     974 |     66 |     51 |      0 |    0 |  1,956 |    3,985 |     6.8 |
| narwhals           | infer-basedpyright |  1,419 |     983 |     79 |    357 |      0 |    4 |  2,284 |    3,985 |    12.8 |
| narwhals           | infer-ty           |  1,383 |     983 |     86 |    314 |      0 |    0 |  2,248 |    3,985 |     5.8 |
| narwhals           | infer-pyrefly      |  1,604 |     983 |     80 |    541 |      0 |    3 |  2,469 |    3,985 |     6.9 |
| narwhals           | infer-trace        |  1,091 |     974 |     66 |     51 |      0 |    0 |  1,956 |    3,985 |     2.7 |
| xarray             | certain            |  3,540 |   3,540 |        |        |      0 |    0 |  4,569 |   22,373 |    17.4 |
| xarray             | likely             |  6,658 |   3,583 |  3,075 |        |      0 |    0 |  7,687 |   22,373 |    30.3 |
| xarray             | unsafe             |  6,851 |   3,540 |  3,075 |    236 |      0 |    0 |  7,880 |   22,373 |    21.1 |
| xarray             | infer-basedpyright |  8,899 |   3,507 |  3,139 |  2,253 |      0 |    0 |  9,928 |   22,373 |   104.3 |
| xarray             | infer-ty           |  8,938 |   3,507 |  3,140 |  2,291 |      0 |    0 |  9,967 |   22,373 |    37.9 |
| xarray             | infer-pyrefly      |  7,316 |   3,508 |  3,089 |    719 |      0 |    0 |  8,345 |   22,373 |    31.3 |
| xarray             | infer-trace        |  6,869 |   3,540 |  3,074 |    255 |      0 |    0 |  7,898 |   22,373 |    21.5 |
| litestar           | certain            |    596 |     596 |        |        |      0 |    0 |  2,150 |    3,459 |     2.2 |
| litestar           | likely             |    700 |     597 |    103 |        |      0 |    0 |  2,254 |    3,459 |     6.0 |
| litestar           | unsafe             |    759 |     596 |    103 |     60 |      0 |    0 |  2,313 |    3,459 |     5.2 |
| litestar           | infer-basedpyright |  1,010 |     593 |    114 |    303 |      0 |    0 |  2,564 |    3,459 |    18.6 |
| litestar           | infer-ty           |  1,014 |     593 |    117 |    304 |      0 |    0 |  2,568 |    3,459 |     5.9 |
| litestar           | infer-pyrefly      |    875 |     593 |    110 |    172 |      0 |    0 |  2,429 |    3,459 |     6.0 |
| litestar           | infer-trace        |    759 |     596 |    103 |     60 |      0 |    0 |  2,313 |    3,459 |     2.1 |
| stripe             | certain            |    564 |     564 |        |        |      0 |    0 | 29,314 |   32,107 |     5.1 |
| stripe             | likely             |    725 |     564 |    161 |        |      0 |    0 | 29,475 |   32,107 |     6.6 |
| stripe             | unsafe             |  1,226 |     564 |    161 |    501 |      0 |    0 | 29,976 |   32,107 |     3.1 |
| stripe             | infer-basedpyright |  1,947 |     564 |    161 |  1,222 |      0 |    0 | 30,697 |   32,107 |   790.8 |
| stripe             | infer-ty           |  1,281 |     564 |    161 |    556 |      0 |    0 | 30,031 |   32,107 |     7.9 |
| stripe             | infer-pyrefly      |  1,269 |     564 |    161 |    544 |      0 |    0 | 30,019 |   32,107 |    14.0 |
| celery             | certain            |    508 |     508 |        |        |      0 |    0 |    524 |    3,764 |     2.6 |
| celery             | likely             |    626 |     511 |    115 |        |      0 |    0 |    642 |    3,764 |     5.0 |
| celery             | unsafe             |    865 |     508 |    115 |    242 |      0 |    0 |    881 |    3,764 |    13.8 |
| celery             | infer-basedpyright |  1,032 |     508 |    124 |    400 |      0 |    0 |  1,048 |    3,764 |    15.5 |
| celery             | infer-ty           |    935 |     508 |    116 |    311 |      0 |    0 |    951 |    3,764 |     5.5 |
| celery             | infer-pyrefly      |    973 |     508 |    117 |    348 |      0 |    0 |    989 |    3,764 |     6.8 |
| celery             | infer-trace        |    929 |     508 |    114 |    307 |      0 |    0 |    945 |    3,764 |     4.3 |
| optuna             | certain            |  1,473 |   1,473 |        |        |      0 |    0 |  1,764 |    3,889 |     4.1 |
| optuna             | likely             |  1,672 |   1,480 |    192 |        |      0 |    0 |  1,963 |    3,889 |     9.2 |
| optuna             | unsafe             |  1,766 |   1,473 |    192 |    101 |      0 |    0 |  2,057 |    3,889 |    39.6 |
| optuna             | infer-basedpyright |  2,115 |   1,473 |    212 |    430 |      0 |    0 |  2,406 |    3,889 |    19.3 |
| optuna             | infer-ty           |  2,152 |   1,473 |    229 |    450 |      0 |    5 |  2,443 |    3,889 |     8.3 |
| optuna             | infer-pyrefly      |  1,955 |   1,473 |    209 |    273 |      0 |    5 |  2,246 |    3,889 |     9.1 |
| optuna             | infer-trace        |  1,766 |   1,473 |    192 |    101 |      0 |    0 |  2,057 |    3,889 |     3.5 |
| dask               | certain            |  3,118 |   3,118 |        |        |      0 |    3 |  3,376 |   24,430 |    17.5 |
| dask               | likely             |  5,063 |   3,188 |  1,875 |        |      0 |    0 |  5,321 |   24,430 |    53.2 |
| dask               | unsafe             |  5,717 |   3,153 |  1,873 |    691 |      0 |    3 |  5,975 |   24,430 |    45.0 |
| dask               | infer-basedpyright |  6,688 |   3,153 |  1,909 |  1,626 |      0 |   36 |  6,946 |   24,430 |   133.4 |
| dask               | infer-ty           |  6,150 |   3,153 |  1,894 |  1,103 |      0 |   25 |  6,408 |   24,430 |    54.6 |
| dask               | infer-pyrefly      |  6,413 |   3,157 |  1,903 |  1,353 |      0 |    2 |  6,671 |   24,430 |    37.6 |
| dask               | infer-trace        |  5,845 |   3,153 |  1,878 |    814 |      0 |    3 |  6,103 |   24,430 |    26.3 |
| mypy               | certain            |  4,727 |   4,727 |        |        |      0 |    0 |  7,027 |   13,701 |     6.1 |
| mypy               | likely             |  5,906 |   4,753 |  1,153 |        |      0 |    0 |  8,206 |   13,701 |     7.3 |
| mypy               | unsafe             |  6,273 |   4,727 |  1,151 |    395 |      0 |    0 |  8,572 |   13,701 |     8.0 |
| mypy               | infer-basedpyright |  8,212 |   4,732 |  1,267 |  2,213 |      0 |    0 | 10,511 |   13,701 |    26.4 |
| mypy               | infer-ty           |  8,543 |   4,731 |  1,274 |  2,538 |      0 |    0 | 10,842 |   13,701 |    10.3 |
| mypy               | infer-pyrefly      |  8,811 |   4,727 |  1,282 |  2,802 |      0 |    0 | 11,110 |   13,701 |     8.4 |
| mypy               | infer-trace        |  6,273 |   4,727 |  1,151 |    395 |      0 |    0 |  8,572 |   13,701 |     8.8 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 23,989 |  23,989 |        |        |
| certain            | stdlib                 | 16,228 |  16,228 |        |        |
| certain            | call                   |  9,591 |   9,591 |        |        |
| certain            | container+literal      |  6,848 |   6,848 |        |        |
| certain            | builtin                |  4,404 |   4,404 |        |        |
| certain            | loop                   |  3,942 |   3,942 |        |        |
| certain            | copy+loop              |  3,599 |   3,599 |        |        |
| certain            | method                 |  3,456 |   3,456 |        |        |
| certain            | container+literal+loop |  2,079 |   2,079 |        |        |
| certain            | literal+method         |  1,630 |   1,630 |        |        |
| certain            | call+unpack            |  1,572 |   1,572 |        |        |
| certain            | open                   |  1,493 |   1,493 |        |        |
| likely             | constructor            | 36,170 |     257 | 35,913 |        |
| likely             | literal                | 23,997 |  23,997 |        |        |
| likely             | stdlib                 | 16,316 |  16,316 |        |        |
| likely             | call                   | 10,092 |   9,606 |    486 |        |
| likely             | container+literal      |  6,848 |   6,848 |        |        |
| likely             | method                 |  4,877 |   3,487 |  1,390 |        |
| likely             | builtin                |  4,405 |   4,405 |        |        |
| likely             | copy+loop              |  4,088 |   3,624 |    464 |        |
| likely             | loop                   |  3,946 |   3,946 |        |        |
| likely             | container+literal+loop |  2,079 |   2,079 |        |        |
| likely             | literal+method         |  1,630 |   1,630 |        |        |
| likely             | call+unpack            |  1,572 |   1,572 |        |        |
| unsafe             | constructor            | 36,169 |     257 | 35,912 |        |
| unsafe             | literal                | 23,992 |  23,987 |        |      5 |
| unsafe             | stdlib                 | 16,682 |  16,230 |        |    452 |
| unsafe             | call                   | 10,052 |   9,591 |    461 |        |
| unsafe             | container+literal      |  6,848 |   6,848 |        |        |
| unsafe             | literal+member         |  5,057 |         |        |  5,057 |
| unsafe             | method                 |  4,807 |   3,456 |  1,351 |        |
| unsafe             | builtin                |  4,406 |   4,404 |        |      2 |
| unsafe             | copy+loop              |  4,055 |   3,599 |    456 |        |
| unsafe             | returned               |  4,054 |   1,182 |        |  2,872 |
| unsafe             | loop                   |  3,942 |   3,942 |        |        |
| unsafe             | container+literal+loop |  2,079 |   2,079 |        |        |
| infer-basedpyright | constructor            | 36,102 |     256 | 35,846 |        |
| infer-basedpyright | checker                | 27,629 |         |        | 27,629 |
| infer-basedpyright | literal                | 23,997 |  23,992 |        |      5 |
| infer-basedpyright | stdlib                 | 16,736 |  16,114 |        |    622 |
| infer-basedpyright | call                   | 10,194 |   9,579 |    615 |        |
| infer-basedpyright | container+literal      |  6,851 |   6,851 |        |        |
| infer-basedpyright | literal+member         |  5,056 |         |        |  5,056 |
| infer-basedpyright | method                 |  5,040 |   3,424 |  1,616 |        |
| infer-basedpyright | copy+loop              |  4,710 |   3,601 |  1,109 |        |
| infer-basedpyright | returned               |  4,455 |   1,163 |        |  3,292 |
| infer-basedpyright | builtin                |  4,406 |   4,404 |        |      2 |
| infer-basedpyright | loop                   |  3,942 |   3,942 |        |        |
| infer-ty           | constructor            | 36,101 |     257 | 35,844 |        |
| infer-ty           | literal                | 23,996 |  23,991 |        |      5 |
| infer-ty           | checker                | 22,324 |         |        | 22,324 |
| infer-ty           | stdlib                 | 16,744 |  16,136 |        |    608 |
| infer-ty           | call                   | 10,140 |   9,580 |    560 |        |
| infer-ty           | container+literal      |  6,852 |   6,852 |        |        |
| infer-ty           | literal+member         |  5,057 |         |        |  5,057 |
| infer-ty           | method                 |  5,007 |   3,424 |  1,583 |        |
| infer-ty           | copy+loop              |  4,620 |   3,600 |  1,020 |        |
| infer-ty           | builtin                |  4,406 |   4,404 |        |      2 |
| infer-ty           | returned               |  4,378 |   1,182 |        |  3,196 |
| infer-ty           | loop                   |  3,942 |   3,942 |        |        |
| infer-pyrefly      | constructor            | 36,088 |     256 | 35,832 |        |
| infer-pyrefly      | literal                | 23,996 |  23,991 |        |      5 |
| infer-pyrefly      | checker                | 23,950 |         |        | 23,950 |
| infer-pyrefly      | stdlib                 | 16,815 |  16,185 |        |    630 |
| infer-pyrefly      | call                   | 10,117 |   9,581 |    536 |        |
| infer-pyrefly      | container+literal      |  6,855 |   6,855 |        |        |
| infer-pyrefly      | literal+member         |  5,056 |         |        |  5,056 |
| infer-pyrefly      | method                 |  4,967 |   3,424 |  1,543 |        |
| infer-pyrefly      | copy+loop              |  4,608 |   3,600 |  1,008 |        |
| infer-pyrefly      | builtin                |  4,406 |   4,404 |        |      2 |
| infer-pyrefly      | returned               |  4,375 |   1,179 |        |  3,196 |
| infer-pyrefly      | loop                   |  3,942 |   3,942 |        |        |
| infer-trace        | constructor            | 28,647 |      25 | 28,622 |        |
| infer-trace        | literal                | 13,888 |  13,886 |        |      2 |
| infer-trace        | call                   |  9,560 |   9,104 |    456 |        |
| infer-trace        | container+literal      |  4,347 |   4,347 |        |        |
| infer-trace        | method                 |  4,244 |   2,899 |  1,345 |        |
| infer-trace        | stdlib                 |  4,085 |   3,899 |        |    186 |
| infer-trace        | traced                 |  3,018 |         |        |  3,018 |
| infer-trace        | literal+member         |  2,825 |         |        |  2,825 |
| infer-trace        | builtin                |  2,616 |   2,614 |        |      2 |
| infer-trace        | copy+loop              |  2,600 |   2,293 |    307 |        |
| infer-trace        | loop                   |  2,024 |   2,024 |        |        |
| infer-trace        | call+unpack            |  1,485 |   1,485 |        |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  12,298 |  63,958 |        0 |
| django             |  17,176 |   2,693 |  11,856 |        0 |
| sqlalchemy         |  12,962 |     818 |  10,263 |        0 |
| pydantic           |   3,117 |     404 |   1,528 |        0 |
| pandas             |  77,793 |  24,298 |  36,585 |        0 |
| twisted            |  17,874 |   4,624 |  10,811 |        0 |
| pip                |   8,924 |   1,109 |   5,561 |        0 |
| structlog          |     316 |      27 |     191 |        0 |
| attrs              |     393 |      11 |     289 |        0 |
| click              |     608 |      65 |     258 |        0 |
| hypercorn          |     355 |      58 |     163 |        0 |
| starlette          |     744 |      97 |     336 |        0 |
| werkzeug           |   1,293 |     126 |     641 |        0 |
| mkdocs             |   2,332 |     473 |   1,049 |        0 |
| httpx              |     569 |      72 |     263 |        0 |
| black              |   1,273 |     164 |     405 |        0 |
| fastapi            |     742 |      65 |     420 |        0 |
| cattrs             |     520 |      37 |     380 |        0 |
| pytest             |   3,003 |     283 |   1,376 |        0 |
| botocore           |   3,786 |     591 |   2,652 |        0 |
| uvicorn            |     489 |      43 |     215 |        0 |
| mcp                |   1,720 |     234 |     803 |        0 |
| textual            |   6,483 |     707 |   3,223 |        0 |
| pdm                |   2,718 |     310 |   1,262 |        0 |
| strawberry-graphql |   1,806 |     213 |     997 |        0 |
| pygments           |   7,666 |     221 |   6,710 |        0 |
| streamlink         |   3,029 |     226 |   2,133 |        0 |
| sphinx             |   7,972 |     791 |   4,061 |        0 |
| tox                |   1,762 |     133 |     688 |        0 |
| pint               |   3,078 |     154 |   2,348 |        0 |
| altair             |   1,700 |      60 |   1,267 |        0 |
| seaborn            |   2,895 |     222 |   2,034 |        0 |
| aiohttp            |   1,857 |     250 |     930 |        0 |
| websockets         |     791 |     106 |     359 |        0 |
| anyio              |     715 |      59 |     448 |        0 |
| zarr               |   2,411 |     109 |   1,235 |        0 |
| joblib             |   2,239 |     244 |   1,470 |        0 |
| networkx           |  22,456 |   2,389 |  16,098 |        0 |
| nibabel            |   8,468 |     921 |   5,698 |        0 |
| narwhals           |   3,120 |     117 |   2,029 |        0 |
| xarray             |  21,344 |   3,311 |  14,493 |        0 |
| litestar           |   1,905 |     163 |   1,146 |        0 |
| stripe             |   3,357 |     662 |   2,131 |        0 |
| celery             |   3,748 |     357 |   2,883 |        0 |
| optuna             |   3,598 |     293 |   1,832 |        0 |
| dask               |  24,172 |   2,441 |  18,613 |        0 |
| mypy               |  11,401 |   1,545 |   5,130 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library   |    4 |       43.79 |     18.29 |    1 |                       692.5 |     715.2 | hyperfine |
| django             |    4 |         8.4 |      3.35 |    1 |                       126.1 |     133.9 | hyperfine |
| sqlalchemy         |    4 |        7.26 |      3.26 |    1 |                       104.5 |     109.3 | hyperfine |
| pydantic           |    4 |        1.58 |      0.73 |    1 |                        24.0 |      26.1 | hyperfine |
| pandas             |    4 |       53.16 |     17.43 |    1 |                       826.3 |     844.0 | hyperfine |
| twisted            |    4 |        6.42 |      2.53 |    1 |                        98.8 |     104.9 | hyperfine |
| pip                |    4 |        4.28 |      1.77 |    1 |                        71.1 |      75.3 | hyperfine |
| structlog          |    4 |        0.24 |      0.23 |    1 |                         3.0 |       4.1 | hyperfine |
| attrs              |    4 |        0.21 |      0.27 |    1 |                         2.9 |       3.8 | hyperfine |
| click              |    4 |        0.39 |       0.3 |    1 |                         5.5 |       6.6 | hyperfine |
| hypercorn          |    4 |        0.31 |      0.24 |    1 |                         4.0 |       5.2 | hyperfine |
| starlette          |    4 |        0.39 |      0.29 |    1 |                         5.2 |       6.5 | hyperfine |
| werkzeug           |    4 |        0.71 |      0.37 |    1 |                         9.8 |      11.1 | hyperfine |
| mkdocs             |    4 |         0.8 |       0.5 |    1 |                        11.7 |      13.7 | hyperfine |
| httpx              |    4 |        0.33 |      0.25 |    1 |                         4.4 |       5.6 | hyperfine |
| black              |    4 |        0.49 |      0.29 |    1 |                         7.3 |       8.5 | hyperfine |
| fastapi            |    4 |        0.56 |      0.47 |    1 |                         8.5 |      10.0 | hyperfine |
| cattrs             |    4 |        0.35 |      0.31 |    1 |                         4.8 |       6.1 | hyperfine |
| pytest             |    4 |        1.33 |      0.75 |    1 |                        19.4 |      21.3 | hyperfine |
| botocore           |    4 |        1.69 |      0.76 |    1 |                        25.7 |      27.4 | hyperfine |
| uvicorn            |    4 |         0.4 |      0.28 |    1 |                         5.4 |       6.6 | hyperfine |
| mcp                |    4 |         1.0 |      0.53 |    1 |                        14.1 |      16.2 | hyperfine |
| textual            |    4 |         2.5 |      1.06 |    1 |                        36.8 |      40.1 | hyperfine |
| pdm                |    4 |        1.43 |      0.77 |    1 |                        20.1 |      23.1 | hyperfine |
| strawberry-graphql |    4 |        1.48 |      0.69 |    1 |                        20.7 |      23.9 | hyperfine |
| pygments           |    4 |        2.73 |       1.1 |    1 |                        50.4 |      53.2 | hyperfine |
| streamlink         |    4 |        1.94 |      0.82 |    1 |                        28.6 |      30.8 | hyperfine |
| sphinx             |    4 |         3.6 |      1.27 |    1 |                        54.7 |      56.0 | hyperfine |
| tox                |    4 |         1.0 |      0.45 |    1 |                        13.7 |      14.6 | hyperfine |
| pint               |    4 |        1.56 |      0.97 |    1 |                        24.0 |      28.4 | hyperfine |
| altair             |    4 |        1.75 |      1.41 |    1 |                        30.2 |      36.0 | hyperfine |
| seaborn            |    4 |        1.92 |      1.14 |    1 |                        30.3 |      36.9 | hyperfine |
| aiohttp            |    4 |        1.12 |      0.56 |    1 |                        16.6 |      18.0 | hyperfine |
| websockets         |    4 |        0.57 |      0.32 |    1 |                         7.8 |       9.3 | hyperfine |
| anyio              |    4 |         0.6 |       0.4 |    1 |                         8.6 |       9.8 | hyperfine |
| zarr               |    4 |        1.44 |      0.68 |    1 |                        21.7 |      24.7 | hyperfine |
| joblib             |    4 |        1.13 |      0.77 |    1 |                        16.8 |      19.9 | hyperfine |
| networkx           |    4 |         7.8 |      3.09 |    1 |                       126.0 |     131.0 | hyperfine |
| nibabel            |    4 |        4.33 |      2.01 |    1 |                        64.7 |      74.4 | hyperfine |
| narwhals           |    4 |        2.13 |      0.95 |    1 |                        33.0 |      38.0 | hyperfine |
| xarray             |    4 |       14.64 |      7.43 |    1 |                       255.5 |     269.6 | hyperfine |
| litestar           |    4 |        1.98 |      0.96 |    1 |                        27.6 |      31.3 | hyperfine |
| stripe             |    4 |        7.25 |      2.55 |    1 |                       123.3 |     129.3 | hyperfine |
| celery             |    4 |        2.25 |      1.45 |    1 |                        33.5 |      39.8 | hyperfine |
| optuna             |    4 |         3.2 |      1.76 |    1 |                        50.4 |      56.3 | hyperfine |
| dask               |    4 |       19.07 |      9.63 |    1 |                       369.3 |     384.7 | hyperfine |
| mypy               |    4 |        5.16 |      1.74 |    1 |                        80.9 |      82.9 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                             tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | --------------------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  470 | Ran 17585 tests: FAILED (failures=5, errors=7, skipped=1129, expected failures=5) |   642.9 |     64.6 |
| django             | certain |    924 |    923 |        1 |                      |                                                                                   |         |          |
| django             | likely  |    296 |    295 |        1 |                      |                                                                                   |         |          |
| django             | guess   |    289 |    273 |       16 |                      |                                                                                   |         |          |
| sqlalchemy         |         |        |        |          |                  140 |                                              29525 passed, 971 skipped, 1 warning |   119.0 |     97.1 |
| sqlalchemy         | certain |  1,023 |  1,006 |       17 |                      |                                                                                   |         |          |
| sqlalchemy         | likely  |    147 |    144 |        3 |                      |                                                                                   |         |          |
| sqlalchemy         | guess   |    105 |    103 |        2 |                      |                                                                                   |         |          |
| pydantic           |         |        |        |          |                    1 |                                   65 failed, 6900 passed, 350 skipped, 29 xfailed |    84.1 |     59.8 |
| pydantic           | certain |    519 |    514 |        5 |                      |                                                                                   |         |          |
| pydantic           | likely  |     47 |     47 |        0 |                      |                                                                                   |         |          |
| pydantic           | guess   |     31 |     31 |        0 |                      |                                                                                   |         |          |
| pandas             |         |        |        |          |                1,420 |                             165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   112.9 |    100.2 |
| pandas             | certain | 12,850 | 12,773 |       77 |                      |                                                                                   |         |          |
| pandas             | likely  | 19,890 | 19,832 |       58 |                      |                                                                                   |         |          |
| pandas             | guess   |    783 |    739 |       44 |                      |                                                                                   |         |          |
| structlog          |         |        |        |          |                    0 |                                     24 failed, 860 passed, 37 skipped, 2 warnings |     2.2 |      2.0 |
| structlog          | certain |     59 |     59 |        0 |                      |                                                                                   |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                                   |         |          |
| structlog          | guess   |      5 |      5 |        0 |                      |                                                                                   |         |          |
| attrs              |         |        |        |          |                    2 |                                       1 failed, 1382 passed, 2 skipped, 2 xfailed |     4.2 |      5.6 |
| attrs              | certain |     72 |     72 |        0 |                      |                                                                                   |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                                   |         |          |
| attrs              | guess   |      1 |      1 |        0 |                      |                                                                                   |         |          |
| click              |         |        |        |          |                    0 |                              1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     5.4 |      6.5 |
| click              | certain |    208 |    208 |        0 |                      |                                                                                   |         |          |
| click              | likely  |     20 |     19 |        1 |                      |                                                                                   |         |          |
| click              | guess   |     26 |     26 |        0 |                      |                                                                                   |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                              2 failed, 194 passed |     9.5 |      6.9 |
| hypercorn          | certain |     63 |     63 |        0 |                      |                                                                                   |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                                   |         |          |
| hypercorn          | guess   |     10 |     10 |        0 |                      |                                                                                   |         |          |
| starlette          |         |        |        |          |                    0 |                                                 1271 passed, 2 skipped, 2 xfailed |    16.1 |      8.2 |
| starlette          | certain |    190 |    190 |        0 |                      |                                                                                   |         |          |
| starlette          | likely  |     47 |     47 |        0 |                      |                                                                                   |         |          |
| starlette          | guess   |     29 |     29 |        0 |                      |                                                                                   |         |          |
| werkzeug           |         |        |        |          |                    0 |                                        1 failed, 979 passed, 1 skipped, 1 warning |    11.2 |     12.2 |
| werkzeug           | certain |    353 |    349 |        4 |                      |                                                                                   |         |          |
| werkzeug           | likely  |     43 |     43 |        0 |                      |                                                                                   |         |          |
| werkzeug           | guess   |     33 |     33 |        0 |                      |                                                                                   |         |          |
| mkdocs             |         |        |        |          |                   12 |                           Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    14.4 |     13.8 |
| mkdocs             | certain |    628 |    627 |        1 |                      |                                                                                   |         |          |
| mkdocs             | likely  |    324 |    324 |        0 |                      |                                                                                   |         |          |
| mkdocs             | guess   |    107 |    107 |        0 |                      |                                                                                   |         |          |
| httpx              |         |        |        |          |                    0 |                                                  1 failed, 1416 passed, 1 skipped |     6.9 |      6.4 |
| httpx              | certain |    181 |    181 |        0 |                      |                                                                                   |         |          |
| httpx              | likely  |     41 |     41 |        0 |                      |                                                                                   |         |          |
| httpx              | guess   |     15 |     15 |        0 |                      |                                                                                   |         |          |
| black              |         |        |        |          |                    0 |                                          519 passed, 1 skipped, 9 subtests passed |    10.0 |      8.5 |
| black              | certain |    594 |    593 |        1 |                      |                                                                                   |         |          |
| black              | likely  |    101 |    101 |        0 |                      |                                                                                   |         |          |
| black              | guess   |     40 |     40 |        0 |                      |                                                                                   |         |          |
| fastapi            |         |        |        |          |                    0 |                                                3551 passed, 17 skipped, 4 xfailed |    19.4 |     18.8 |
| fastapi            | certain |    215 |    215 |        0 |                      |                                                                                   |         |          |
| fastapi            | likely  |     30 |     30 |        0 |                      |                                                                                   |         |          |
| fastapi            | guess   |     22 |     22 |        0 |                      |                                                                                   |         |          |
| cattrs             |         |        |        |          |                    0 |                                                            994 passed, 15 xfailed |    18.6 |     18.4 |
| cattrs             | certain |     99 |     97 |        2 |                      |                                                                                   |         |          |
| cattrs             | likely  |     23 |     23 |        0 |                      |                                                                                   |         |          |
| cattrs             | guess   |     13 |     13 |        0 |                      |                                                                                   |         |          |
| pytest             |         |        |        |          |                    9 |               46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    48.2 |     20.5 |
| pytest             | certain |  1,082 |  1,071 |       11 |                      |                                                                                   |         |          |
| pytest             | likely  |    121 |    121 |        0 |                      |                                                                                   |         |          |
| pytest             | guess   |    102 |    102 |        0 |                      |                                                                                   |         |          |
| botocore           |         |        |        |          |                  299 |                                                 7 failed, 4593 passed, 96 skipped |    35.3 |     26.5 |
| botocore           | certain |    327 |    326 |        1 |                      |                                                                                   |         |          |
| botocore           | likely  |    130 |    130 |        0 |                      |                                                                                   |         |          |
| botocore           | guess   |     93 |     92 |        1 |                      |                                                                                   |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                           1350 passed, 12 skipped |    39.7 |     39.0 |
| uvicorn            | certain |    168 |    164 |        4 |                      |                                                                                   |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                                   |         |          |
| uvicorn            | guess   |      7 |      7 |        0 |                      |                                                                                   |         |          |
| mcp                |         |        |        |          |                    0 |                                       3 failed, 6092 passed, 8 skipped, 1 xfailed |    15.6 |     14.8 |
| mcp                | certain |    501 |    501 |        0 |                      |                                                                                   |         |          |
| mcp                | likely  |    128 |    127 |        1 |                      |                                                                                   |         |          |
| mcp                | guess   |     54 |     53 |        1 |                      |                                                                                   |         |          |
| pdm                |         |        |        |          |                    0 |                                               1472 passed, 1 skipped, 60 warnings |    17.4 |     18.8 |
| pdm                | certain |    870 |    864 |        6 |                      |                                                                                   |         |          |
| pdm                | likely  |    123 |    123 |        0 |                      |                                                                                   |         |          |
| pdm                | guess   |     72 |     72 |        0 |                      |                                                                                   |         |          |
| strawberry-graphql |         |        |        |          |                    0 |           51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    14.3 |     11.3 |
| strawberry-graphql | certain |    378 |    372 |        6 |                      |                                                                                   |         |          |
| strawberry-graphql | likely  |     92 |     91 |        1 |                      |                                                                                   |         |          |
| strawberry-graphql | guess   |     29 |     29 |        0 |                      |                                                                                   |         |          |
| pygments           |         |        |        |          |                   87 |                                                 1 failed, 5330 passed, 15 skipped |    23.4 |     14.2 |
| pygments           | certain |    290 |    290 |        0 |                      |                                                                                   |         |          |
| pygments           | likely  |     58 |     58 |        0 |                      |                                                                                   |         |          |
| pygments           | guess   |     57 |     57 |        0 |                      |                                                                                   |         |          |
| streamlink         |         |        |        |          |                    8 |                                      15 failed, 7233 passed, 36 skipped, 9 errors |    17.1 |     14.3 |
| streamlink         | certain |    265 |    264 |        1 |                      |                                                                                   |         |          |
| streamlink         | likely  |     38 |     38 |        0 |                      |                                                                                   |         |          |
| streamlink         | guess   |     30 |     30 |        0 |                      |                                                                                   |         |          |
| sphinx             |         |        |        |          |                    0 |                                    9 failed, 2393 passed, 22 skipped, 35 warnings |    15.0 |     14.6 |
| sphinx             | certain |  2,001 |  1,976 |       25 |                      |                                                                                   |         |          |
| sphinx             | likely  |    344 |    344 |        0 |                      |                                                                                   |         |          |
| sphinx             | guess   |    173 |    171 |        2 |                      |                                                                                   |         |          |
| tox                |         |        |        |          |                    0 |                                      17 failed, 8525 passed, 31 skipped, 6 errors |    24.3 |     16.9 |
| tox                | certain |    702 |    699 |        3 |                      |                                                                                   |         |          |
| tox                | likely  |     58 |     58 |        0 |                      |                                                                                   |         |          |
| tox                | guess   |     27 |     26 |        1 |                      |                                                                                   |         |          |
| pint               |         |        |        |          |                    3 |  1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    38.6 |     26.7 |
| pint               | certain |    180 |    177 |        3 |                      |                                                                                   |         |          |
| pint               | likely  |     12 |     12 |        0 |                      |                                                                                   |         |          |
| pint               | guess   |     24 |     22 |        2 |                      |                                                                                   |         |          |
| altair             |         |        |        |          |                    6 |             28 failed, 1866 passed, 12 skipped, 6 xfailed, 4 xpassed, 90 warnings |    28.8 |     25.1 |
| altair             | certain |    197 |    196 |        1 |                      |                                                                                   |         |          |
| altair             | likely  |     33 |     33 |        0 |                      |                                                                                   |         |          |
| altair             | guess   |      6 |      5 |        1 |                      |                                                                                   |         |          |
| seaborn            |         |        |        |          |                   32 |             20 failed, 2178 passed, 11 skipped, 6 xfailed, 958 warnings, 8 errors |    60.8 |     69.7 |
| seaborn            | certain |    487 |    485 |        2 |                      |                                                                                   |         |          |
| seaborn            | likely  |    115 |    114 |        1 |                      |                                                                                   |         |          |
| seaborn            | guess   |     47 |     44 |        3 |                      |                                                                                   |         |          |
| aiohttp            |         |        |        |          |                    0 |                  3 failed, 4840 passed, 535 skipped, 2 xfailed, 4 subtests passed |    91.0 |     81.2 |
| aiohttp            | certain |    494 |    476 |       18 |                      |                                                                                   |         |          |
| aiohttp            | likely  |    106 |    105 |        1 |                      |                                                                                   |         |          |
| aiohttp            | guess   |     76 |     71 |        5 |                      |                                                                                   |         |          |
| websockets         |         |        |        |          |                    0 |                                                    Ran 2589 tests: OK (skipped=8) |    32.8 |     27.6 |
| websockets         | certain |    236 |    235 |        1 |                      |                                                                                   |         |          |
| websockets         | likely  |     50 |     50 |        0 |                      |                                                                                   |         |          |
| websockets         | guess   |     30 |     30 |        0 |                      |                                                                                   |         |          |
| anyio              |         |        |        |          |                    0 |                                3824 passed, 19 skipped, 388 deselected, 5 xfailed |   106.8 |     89.8 |
| anyio              | certain |      0 |      0 |        0 |                      |                                                                                   |         |          |
| anyio              | likely  |      0 |      0 |        0 |                      |                                                                                   |         |          |
| anyio              | guess   |      0 |      0 |        0 |                      |                                                                                   |         |          |
| zarr               |         |        |        |          |                    0 |                                              8422 passed, 1205 skipped, 4 xfailed |   111.5 |    127.7 |
| zarr               | certain |    719 |    709 |       10 |                      |                                                                                   |         |          |
| zarr               | likely  |     46 |     46 |        0 |                      |                                                                                   |         |          |
| zarr               | guess   |     22 |     21 |        1 |                      |                                                                                   |         |          |
| joblib             |         |        |        |          |                    9 |                        10 failed, 1482 passed, 45 skipped, 4 xpassed, 86 warnings |   140.2 |    168.4 |
| joblib             | certain |    127 |    127 |        0 |                      |                                                                                   |         |          |
| joblib             | likely  |     16 |     16 |        0 |                      |                                                                                   |         |          |
| joblib             | guess   |     16 |     16 |        0 |                      |                                                                                   |         |          |
| networkx           |         |        |        |          |                  351 |                                             10083 passed, 62 skipped, 741 xfailed |    25.7 |     26.4 |
| networkx           | certain |    930 |    929 |        1 |                      |                                                                                   |         |          |
| networkx           | likely  |    176 |    175 |        1 |                      |                                                                                   |         |          |
| networkx           | guess   |    105 |    102 |        3 |                      |                                                                                   |         |          |
| nibabel            |         |        |        |          |                   73 |                       109 failed, 5167 passed, 304 skipped, 40 xfailed, 19 errors |    19.6 |     14.8 |
| nibabel            | certain |    406 |    403 |        3 |                      |                                                                                   |         |          |
| nibabel            | likely  |    126 |    126 |        0 |                      |                                                                                   |         |          |
| nibabel            | guess   |     79 |     79 |        0 |                      |                                                                                   |         |          |
| narwhals           |         |        |        |          |                    0 |                                972 failed, 11116 passed, 235 skipped, 699 xfailed |    26.9 |     21.2 |
| narwhals           | certain |    538 |    537 |        1 |                      |                                                                                   |         |          |
| narwhals           | likely  |     45 |     45 |        0 |                      |                                                                                   |         |          |
| narwhals           | guess   |     22 |     22 |        0 |                      |                                                                                   |         |          |
| xarray             |         |        |        |          |                   19 |   3 failed, 6333 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    18.2 |     24.3 |
| xarray             | certain |    815 |    810 |        5 |                      |                                                                                   |         |          |
| xarray             | likely  |    115 |    114 |        1 |                      |                                                                                   |         |          |
| xarray             | guess   |     49 |     49 |        0 |                      |                                                                                   |         |          |
| litestar           |         |        |        |          |                    0 |            5 failed, 5646 passed, 256 skipped, 13 xfailed, 30 xpassed, 3 warnings |    27.8 |     25.4 |
| litestar           | certain |    452 |    451 |        1 |                      |                                                                                   |         |          |
| litestar           | likely  |     89 |     89 |        0 |                      |                                                                                   |         |          |
| litestar           | guess   |     39 |     39 |        0 |                      |                                                                                   |         |          |
| celery             |         |        |        |          |                   64 |                                      3 failed, 3521 passed, 36 skipped, 3 xfailed |   158.1 |     61.0 |
| celery             | certain |    219 |    215 |        4 |                      |                                                                                   |         |          |
| celery             | likely  |     34 |     34 |        0 |                      |                                                                                   |         |          |
| celery             | guess   |     28 |     25 |        3 |                      |                                                                                   |         |          |
| optuna             |         |        |        |          |                    0 |                      263 failed, 4203 passed, 43 skipped, 327 warnings, 16 errors |   143.9 |    123.8 |
| optuna             | certain |    616 |    615 |        1 |                      |                                                                                   |         |          |
| optuna             | likely  |    104 |    104 |        0 |                      |                                                                                   |         |          |
| optuna             | guess   |     43 |     43 |        0 |                      |                                                                                   |         |          |
| dask               |         |        |        |          |                  117 |          5 failed, 16196 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   144.5 |    126.3 |
| dask               | certain |  1,064 |  1,057 |        7 |                      |                                                                                   |         |          |
| dask               | likely  |    163 |    162 |        1 |                      |                                                                                   |         |          |
| dask               | guess   |     99 |     96 |        3 |                      |                                                                                   |         |          |
| mypy               |         |        |        |          |                    0 |                         14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   344.7 |    326.8 |
| mypy               | certain |  3,006 |  3,006 |        0 |                      |                                                                                   |         |          |
| mypy               | likely  |    694 |    694 |        0 |                      |                                                                                   |         |          |
| mypy               | guess   |    236 |    236 |        0 |                      |                                                                                   |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                | same as released | summary                                                               | new failures | gone | named |
| ------------------ | ------------------ | ---------------- | --------------------------------------------------------------------- | -----------: | ---: | ----: |
| django             | released           |                  | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            |              |      |       |
| django             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| django             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| django             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| django             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| django             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| django             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| django             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | released           |                  | 29,523 passed, 973 skipped                                            |              |      |       |
| sqlalchemy         | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | released           |                  | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      |              |      |       |
| pydantic           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pydantic           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | released           |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |              |      |       |
| pandas             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pandas             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | released           |                  | 24 failed, 860 passed, 37 skipped                                     |              |      |       |
| structlog          | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| structlog          | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | released           |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |              |      |       |
| attrs              | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| attrs              | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | released           |                  | 1,991 passed, 24 skipped, 1 xfailed                                   |              |      |       |
| click              | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| click              | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | released           |                  | 2 failed, 194 passed                                                  |              |      |       |
| hypercorn          | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| hypercorn          | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | released           |                  | 1,271 passed, 2 skipped, 2 xfailed                                    |              |      |       |
| starlette          | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| starlette          | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | released           |                  | 1 failed, 979 passed, 1 skipped                                       |              |      |       |
| werkzeug           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| werkzeug           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | released           |                  | 2 errors, 2 failures, 724 ran, 4 skipped                              |              |      |       |
| mkdocs             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mkdocs             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | released           |                  | 1 failed, 1,416 passed, 1 skipped                                     |              |      |       |
| httpx              | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| httpx              | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| black              | released           |                  | 519 passed, 1 skipped                                                 |              |      |       |
| black              | fix-certain        | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | fix-likely         | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | fix-unsafe         | True             | as infer-trace's (implied)                                            |            0 |    0 |     1 |
| black              | infer-basedpyright | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-pyrefly      | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-trace        | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-ty           | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| fastapi            | released           |                  | 3,551 passed, 17 skipped, 4 xfailed                                   |              |      |       |
| fastapi            | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| fastapi            | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| fastapi            | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| fastapi            | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| fastapi            | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| fastapi            | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| fastapi            | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | released           |                  | 994 passed, 15 xfailed                                                |              |      |       |
| cattrs             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| cattrs             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | released           |                  | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  |              |      |       |
| pytest             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pytest             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | released           |                  | 7 failed, 4,593 passed, 96 skipped                                    |              |      |       |
| botocore           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| botocore           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | released           |                  | 1,350 passed, 12 skipped                                              |              |      |       |
| uvicorn            | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| uvicorn            | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | released           |                  | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          |              |      |       |
| mcp                | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mcp                | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | released           |                  | 1,472 passed, 1 skipped                                               |              |      |       |
| pdm                | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pdm                | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | released           |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |              |      |       |
| strawberry-graphql | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| strawberry-graphql | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | released           |                  | 1 failed, 5,330 passed, 15 skipped                                    |              |      |       |
| pygments           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pygments           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | released           |                  | 9 error, 15 failed, 7,233 passed, 36 skipped                          |              |      |       |
| streamlink         | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| streamlink         | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| sphinx             | released           |                  | 10 failed, 2,392 passed, 22 skipped                                   |              |      |       |
| sphinx             | fix-certain        | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| sphinx             | fix-likely         | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| sphinx             | fix-unsafe         | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| sphinx             | infer-basedpyright | True             | 10 failed, 2,392 passed, 22 skipped                                   |            0 |    0 |     0 |
| sphinx             | infer-pyrefly      | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-trace        | True             | 10 failed, 2,392 passed, 22 skipped                                   |            0 |    0 |     0 |
| sphinx             | infer-ty           | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| tox                | released           |                  | 6 error, 17 failed, 8,525 passed, 31 skipped                          |              |      |       |
| tox                | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| tox                | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| tox                | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| tox                | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| tox                | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| tox                | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| tox                | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | released           |                  | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |              |      |       |
| pint               | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| pint               | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | released           |                  | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |              |      |       |
| altair             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| altair             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | released           |                  | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |              |      |       |
| seaborn            | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| seaborn            | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | released           |                  | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        |              |      |       |
| aiohttp            | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| aiohttp            | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | released           |                  | 2,589 ran, 8 skipped                                                  |              |      |       |
| websockets         | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| websockets         | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | released           |                  | 3,824 passed, 19 skipped, 5 xfailed                                   |              |      |       |
| anyio              | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| anyio              | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | released           |                  | 8,422 passed, 1,205 skipped, 4 xfailed                                |              |      |       |
| zarr               | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| zarr               | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | released           |                  | 8 failed, 1,484 passed, 45 skipped, 4 xpassed                         |              |      |       |
| joblib             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| joblib             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | released           |                  | 10,083 passed, 62 skipped, 741 xfailed                                |              |      |       |
| networkx           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| networkx           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| nibabel            | released           |                  | 20 error, 110 failed, 5,166 passed, 304 skipped, 40 xfailed           |              |      |       |
| nibabel            | fix-certain        | False            | 20 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            1 |    0 |     0 |
| nibabel            | fix-likely         | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-unsafe         | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-basedpyright | True             | 21 error, 108 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-pyrefly      | True             | 19 error, 109 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-trace        | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-ty           | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| narwhals           | released           |                  | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |              |      |       |
| narwhals           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| narwhals           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| narwhals           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| narwhals           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| narwhals           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| narwhals           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| narwhals           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | released           |                  | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |              |      |       |
| xarray             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| xarray             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | released           |                  | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |              |      |       |
| litestar           | fix-certain        | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| litestar           | fix-likely         | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| litestar           | fix-unsafe         | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| litestar           | infer-basedpyright | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-pyrefly      | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-trace        | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-ty           | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| celery             | released           |                  | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |              |      |       |
| celery             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| celery             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| celery             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| celery             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| celery             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| celery             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| celery             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | released           |                  | 16 error, 263 failed, 4,203 passed, 43 skipped                        |              |      |       |
| optuna             | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| optuna             | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | released           |                  | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |              |      |       |
| dask               | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| dask               | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | released           |                  | 14,464 passed, 366 skipped, 12 xfailed                                |              |      |       |
| mypy               | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| mypy               | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                      change |
| ------------------ | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy         | released           |      0 |     |      |                                                             |
| sqlalchemy         | fix-certain        |      0 |   0 |    0 |    198 files changed, 2786 insertions(+), 2308 deletions(-) |
| sqlalchemy         | fix-likely         |      0 |   0 |    0 |    198 files changed, 2786 insertions(+), 2308 deletions(-) |
| sqlalchemy         | fix-unsafe         |      0 |   0 |    0 |    198 files changed, 2786 insertions(+), 2308 deletions(-) |
| sqlalchemy         | infer-basedpyright |      5 |   5 |    0 |    204 files changed, 3627 insertions(+), 3098 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      9 |   9 |    0 |    203 files changed, 3306 insertions(+), 2656 deletions(-) |
| sqlalchemy         | infer-trace        |      6 |   6 |    0 |    200 files changed, 2963 insertions(+), 2437 deletions(-) |
| sqlalchemy         | infer-ty           |      4 |   4 |    0 |    205 files changed, 3583 insertions(+), 2940 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1903 insertions(+), 1492 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1903 insertions(+), 1492 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1903 insertions(+), 1492 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1903 insertions(+), 1492 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1933 insertions(+), 1406 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1664 insertions(+), 1266 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1807 insertions(+), 1399 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    259 |   0 |    0 | 1199 files changed, 42019 insertions(+), 38393 deletions(-) |
| pandas             | fix-likely         |    259 |   0 |    0 | 1199 files changed, 42019 insertions(+), 38393 deletions(-) |
| pandas             | fix-unsafe         |    261 |   2 |    0 | 1202 files changed, 42808 insertions(+), 39079 deletions(-) |
| pandas             | infer-basedpyright |    314 |  55 |    0 | 1213 files changed, 49287 insertions(+), 44912 deletions(-) |
| pandas             | infer-pyrefly      |    358 |  99 |    0 | 1209 files changed, 50170 insertions(+), 45515 deletions(-) |
| pandas             | infer-trace        |    262 |   3 |    0 | 1205 files changed, 44253 insertions(+), 40441 deletions(-) |
| pandas             | infer-ty           |    271 |  12 |    0 | 1214 files changed, 48800 insertions(+), 44453 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 139 insertions(+), 105 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 139 insertions(+), 105 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 139 insertions(+), 105 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      9 |   1 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 139 insertions(+), 105 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 355 insertions(+), 271 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 355 insertions(+), 271 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 355 insertions(+), 271 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 440 insertions(+), 346 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 445 insertions(+), 346 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 355 insertions(+), 271 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 459 insertions(+), 359 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 236 insertions(+), 166 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 219 insertions(+), 150 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-ty           |     12 |   0 |    0 |       25 files changed, 240 insertions(+), 164 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 522 insertions(+), 404 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 470 insertions(+), 361 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 502 insertions(+), 386 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 670 insertions(+), 461 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 670 insertions(+), 461 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 670 insertions(+), 461 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 801 insertions(+), 568 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 835 insertions(+), 564 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 670 insertions(+), 461 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 824 insertions(+), 573 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 307 insertions(+), 252 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 307 insertions(+), 252 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 307 insertions(+), 252 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 398 insertions(+), 329 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       16 files changed, 355 insertions(+), 283 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 307 insertions(+), 252 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 382 insertions(+), 305 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-basedpyright |      7 |   7 |    0 |       29 files changed, 372 insertions(+), 283 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 323 insertions(+), 232 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-ty           |      2 |   2 |    0 |       29 files changed, 351 insertions(+), 265 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 926 insertions(+), 657 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 926 insertions(+), 657 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1017 insertions(+), 726 deletions(-) |
| mcp                | infer-basedpyright |      3 |   3 |    0 |      82 files changed, 1153 insertions(+), 854 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      82 files changed, 1109 insertions(+), 799 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1017 insertions(+), 726 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      82 files changed, 1155 insertions(+), 823 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |      151 files changed, 898 insertions(+), 668 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |      151 files changed, 898 insertions(+), 668 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |      151 files changed, 898 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-basedpyright |     16 |   6 |    0 |     154 files changed, 1094 insertions(+), 836 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     14 |   4 |    0 |      152 files changed, 963 insertions(+), 723 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |      151 files changed, 898 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-ty           |     14 |   4 |    0 |     154 files changed, 1087 insertions(+), 826 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |     168 files changed, 1278 insertions(+), 735 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |     168 files changed, 1278 insertions(+), 735 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |     168 files changed, 1278 insertions(+), 735 deletions(-) |
| streamlink         | infer-basedpyright |      1 |   1 |    0 |    185 files changed, 1744 insertions(+), 1125 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |     172 files changed, 1461 insertions(+), 874 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |     168 files changed, 1278 insertions(+), 735 deletions(-) |
| streamlink         | infer-ty           |     22 |  22 |    0 |    185 files changed, 1995 insertions(+), 1123 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      4 |   1 |    0 |    194 files changed, 3192 insertions(+), 2147 deletions(-) |
| sphinx             | fix-likely         |      4 |   1 |    0 |    197 files changed, 3634 insertions(+), 2493 deletions(-) |
| sphinx             | fix-unsafe         |      4 |   1 |    0 |    212 files changed, 4000 insertions(+), 2804 deletions(-) |
| sphinx             | infer-basedpyright |      8 |   5 |    0 |    215 files changed, 4825 insertions(+), 3567 deletions(-) |
| sphinx             | infer-pyrefly      |     13 |  10 |    0 |    216 files changed, 5186 insertions(+), 3693 deletions(-) |
| sphinx             | infer-trace        |      4 |   1 |    0 |    212 files changed, 4000 insertions(+), 2804 deletions(-) |
| sphinx             | infer-ty           |      6 |   3 |    0 |    215 files changed, 4891 insertions(+), 3543 deletions(-) |
| pint               | released           |    659 |     |      |                                                             |
| pint               | fix-certain        |    659 |   0 |    0 |       75 files changed, 775 insertions(+), 526 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |       75 files changed, 775 insertions(+), 526 deletions(-) |
| pint               | fix-unsafe         |    659 |   0 |    0 |       75 files changed, 775 insertions(+), 526 deletions(-) |
| pint               | infer-basedpyright |    660 |   1 |    0 |      79 files changed, 1115 insertions(+), 771 deletions(-) |
| pint               | infer-pyrefly      |    664 |   5 |    0 |       76 files changed, 850 insertions(+), 575 deletions(-) |
| pint               | infer-trace        |    659 |   0 |    0 |       75 files changed, 775 insertions(+), 526 deletions(-) |
| pint               | infer-ty           |    660 |   2 |    1 |       78 files changed, 984 insertions(+), 681 deletions(-) |
| altair             | released           |      1 |     |      |                                                             |
| altair             | fix-certain        |      1 |   0 |    0 |       40 files changed, 455 insertions(+), 364 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |       40 files changed, 455 insertions(+), 364 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |       40 files changed, 455 insertions(+), 364 deletions(-) |
| altair             | infer-basedpyright |      4 |   3 |    0 |       40 files changed, 546 insertions(+), 433 deletions(-) |
| altair             | infer-pyrefly      |      5 |   4 |    0 |       40 files changed, 521 insertions(+), 409 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |       40 files changed, 465 insertions(+), 371 deletions(-) |
| altair             | infer-ty           |      4 |   3 |    0 |       40 files changed, 542 insertions(+), 428 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                             |
| seaborn            | fix-certain        |     39 |   0 |    0 |      46 files changed, 1007 insertions(+), 808 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |      46 files changed, 1007 insertions(+), 808 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |      46 files changed, 1007 insertions(+), 808 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |      46 files changed, 1007 insertions(+), 808 deletions(-) |
| seaborn            | infer-pyrefly      |     39 |   0 |    0 |      47 files changed, 1068 insertions(+), 835 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |       46 files changed, 943 insertions(+), 726 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |       46 files changed, 978 insertions(+), 779 deletions(-) |
| websockets         | released           |      0 |     |      |                                                             |
| websockets         | fix-certain        |      0 |   0 |    0 |       39 files changed, 339 insertions(+), 233 deletions(-) |
| websockets         | fix-likely         |      1 |   1 |    0 |       39 files changed, 398 insertions(+), 290 deletions(-) |
| websockets         | fix-unsafe         |      1 |   1 |    0 |       39 files changed, 448 insertions(+), 324 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |       40 files changed, 570 insertions(+), 442 deletions(-) |
| websockets         | infer-pyrefly      |      4 |   4 |    0 |       40 files changed, 618 insertions(+), 453 deletions(-) |
| websockets         | infer-trace        |      1 |   1 |    0 |       39 files changed, 448 insertions(+), 324 deletions(-) |
| websockets         | infer-ty           |      4 |   4 |    0 |       40 files changed, 577 insertions(+), 436 deletions(-) |
| networkx           | released           |      0 |     |      |                                                             |
| networkx           | fix-certain        |      0 |   0 |    0 |    475 files changed, 6952 insertions(+), 5789 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 |    458 files changed, 6207 insertions(+), 5280 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 |    475 files changed, 6952 insertions(+), 5789 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 |    475 files changed, 7794 insertions(+), 6475 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 |    471 files changed, 7063 insertions(+), 5913 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 |    475 files changed, 6952 insertions(+), 5789 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 |    465 files changed, 7018 insertions(+), 5909 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                             |
| nibabel            | fix-certain        |     12 |   0 |    0 |    181 files changed, 2052 insertions(+), 1368 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 |    191 files changed, 2746 insertions(+), 1980 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 |    197 files changed, 3021 insertions(+), 2204 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 |    202 files changed, 3742 insertions(+), 2802 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 |    202 files changed, 3477 insertions(+), 2510 deletions(-) |
| nibabel            | infer-trace        |     15 |   3 |    0 |    197 files changed, 3129 insertions(+), 2276 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 |    199 files changed, 3687 insertions(+), 2742 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                             |
| narwhals           | fix-certain        |     19 |   0 |    0 |      96 files changed, 1080 insertions(+), 902 deletions(-) |
| narwhals           | fix-likely         |     19 |   0 |    0 |      96 files changed, 1080 insertions(+), 902 deletions(-) |
| narwhals           | fix-unsafe         |     20 |   1 |    0 |      97 files changed, 1137 insertions(+), 942 deletions(-) |
| narwhals           | infer-basedpyright |     28 |   9 |    0 |     98 files changed, 1534 insertions(+), 1262 deletions(-) |
| narwhals           | infer-pyrefly      |     33 |  14 |    0 |    101 files changed, 1726 insertions(+), 1393 deletions(-) |
| narwhals           | infer-trace        |     20 |   1 |    0 |      97 files changed, 1137 insertions(+), 942 deletions(-) |
| narwhals           | infer-ty           |     33 |  14 |    0 |     98 files changed, 1446 insertions(+), 1199 deletions(-) |
| litestar           | released           |     86 |     |      |                                                             |
| litestar           | fix-certain        |     86 |   0 |    0 |      164 files changed, 796 insertions(+), 567 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |      164 files changed, 796 insertions(+), 567 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |      164 files changed, 796 insertions(+), 567 deletions(-) |
| litestar           | infer-basedpyright |     90 |   4 |    0 |     174 files changed, 1087 insertions(+), 808 deletions(-) |
| litestar           | infer-pyrefly      |     87 |   1 |    0 |      169 files changed, 917 insertions(+), 657 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |      164 files changed, 796 insertions(+), 567 deletions(-) |
| litestar           | infer-ty           |     91 |   5 |    0 |     175 files changed, 1081 insertions(+), 791 deletions(-) |
| optuna             | released           |     52 |     |      |                                                             |
| optuna             | fix-certain        |     52 |   0 |    0 |    144 files changed, 1778 insertions(+), 1250 deletions(-) |
| optuna             | fix-likely         |     52 |   0 |    0 |    144 files changed, 1778 insertions(+), 1250 deletions(-) |
| optuna             | fix-unsafe         |     53 |   1 |    0 |    144 files changed, 1893 insertions(+), 1333 deletions(-) |
| optuna             | infer-basedpyright |     54 |   2 |    0 |    164 files changed, 2299 insertions(+), 1665 deletions(-) |
| optuna             | infer-pyrefly      |     57 |   5 |    0 |    147 files changed, 2092 insertions(+), 1489 deletions(-) |
| optuna             | infer-trace        |     53 |   1 |    0 |    144 files changed, 1893 insertions(+), 1333 deletions(-) |
| optuna             | infer-ty           |     56 |   4 |    0 |    162 files changed, 2312 insertions(+), 1665 deletions(-) |
| mypy               | released           |      0 |     |      |                                                             |
| mypy               | fix-certain        |      0 |   0 |    0 |    160 files changed, 4972 insertions(+), 3020 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 |    166 files changed, 6176 insertions(+), 4070 deletions(-) |
| mypy               | fix-unsafe         |     14 |  14 |    0 |    167 files changed, 6553 insertions(+), 4383 deletions(-) |
| mypy               | infer-basedpyright |     20 |  20 |    0 |    170 files changed, 8594 insertions(+), 6223 deletions(-) |
| mypy               | infer-pyrefly      |     23 |  23 |    0 |    170 files changed, 9210 insertions(+), 6414 deletions(-) |
| mypy               | infer-trace        |     14 |  14 |    0 |    167 files changed, 6553 insertions(+), 4383 deletions(-) |
| mypy               | infer-ty           |     26 |  26 |    0 |    170 files changed, 8925 insertions(+), 6388 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    48.3 |       107.9 |  2.2 |    3.88 |          3 |     4.72 | False |
| standard library   | fix-certain              |   106.6 |       271.5 |  2.5 |    5.21 |          3 |     6.45 | False |
| standard library   | fix-likely               |   139.3 |       346.8 |  2.5 |    7.91 |          3 |     9.85 | False |
| standard library   | fix-unsafe               |   104.0 |       293.9 |  2.8 |    5.97 |          3 |     7.41 | False |
| standard library   | infer-basedpyright       |   974.7 |      1467.4 |  1.5 |   13.33 |          2 |    16.46 | False |
| standard library   | infer-ty                 |   165.2 |       508.7 |  3.1 |   14.93 |          4 |    18.94 | False |
| standard library   | infer-pyrefly            |   149.8 |       485.0 |  3.2 |    19.0 |          4 |    23.56 | False |
| standard library   | census                   |    27.6 |        26.5 |  1.0 |    0.46 |          3 |     4.72 | False |
| standard library   | coverage                 |     9.2 |        32.2 |  3.5 |    1.64 |          4 |     2.04 | False |
| standard library   | timing                   |    62.2 |        94.8 |  1.5 |    3.78 |         16 |     4.77 | False |
| django             | check                    |     7.0 |        17.6 |  2.5 |    0.85 |          3 |     1.06 | False |
| django             | fix-certain              |    22.1 |        47.3 |  2.1 |    1.13 |          3 |      1.4 | False |
| django             | fix-likely               |    24.3 |        57.3 |  2.4 |    1.53 |          3 |      1.9 | False |
| django             | fix-unsafe               |    19.8 |        47.5 |  2.4 |     1.3 |          3 |     1.59 | False |
| django             | infer-basedpyright       |    74.3 |       229.8 |  3.1 |    6.43 |          5 |     9.57 | False |
| django             | infer-ty                 |    61.5 |        92.9 |  1.5 |     3.6 |          3 |     3.77 | False |
| django             | infer-pyrefly            |    31.5 |        90.7 |  2.9 |    4.17 |          4 |     5.14 | False |
| django             | census                   |     3.0 |         2.9 |  1.0 |    0.09 |          3 |     1.06 | False |
| django             | coverage                 |     1.8 |         4.8 |  2.7 |    0.34 |          3 |     0.42 | False |
| django             | timing                   |    12.0 |        18.3 |  1.5 |    0.85 |         16 |     1.06 | False |
| django             | traced                   |   667.3 |       510.9 |  0.8 |    1.43 |          1 |     1.66 | False |
| django             | tests-released           |    65.1 |       482.3 |  7.4 |    5.77 |          7 |     7.65 | False |
| django             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| django             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.05 | False |
| django             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          9 |      6.3 | False |
| django             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     7.15 | False |
| django             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |         11 |     6.14 | False |
| django             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          9 |     7.93 | False |
| django             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     7.55 | False |
| django             | infer-union              |    88.1 |       358.9 |  4.1 |   12.51 |          4 |    16.06 | False |
| django             | tests-infer-union        |    58.1 |       470.5 |  8.1 |    5.71 |          7 |     7.11 | False |
| django             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.25 | False |
| sqlalchemy         | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          3 |     1.06 | False |
| sqlalchemy         | fix-certain              |    17.6 |        39.2 |  2.2 |    0.95 |          3 |     1.19 | False |
| sqlalchemy         | fix-likely               |    18.6 |        43.9 |  2.4 |    1.35 |          3 |      1.7 | False |
| sqlalchemy         | fix-unsafe               |    18.9 |        37.9 |  2.0 |    1.01 |          3 |     1.25 | False |
| sqlalchemy         | infer-basedpyright       |    55.3 |       204.5 |  3.7 |    7.77 |          5 |     9.44 | False |
| sqlalchemy         | infer-ty                 |    29.9 |        77.0 |  2.6 |    3.79 |          3 |      4.4 | False |
| sqlalchemy         | infer-pyrefly            |    22.8 |        64.4 |  2.8 |    4.04 |          3 |     4.94 | False |
| sqlalchemy         | census                   |     8.8 |        16.1 |  1.8 |    0.86 |          3 |     1.06 | False |
| sqlalchemy         | coverage                 |     1.8 |         5.0 |  2.8 |    0.39 |          3 |     0.49 | False |
| sqlalchemy         | timing                   |    10.8 |        14.8 |  1.4 |    0.85 |         16 |     1.06 | False |
| sqlalchemy         | traced                   |   140.2 |       917.2 |  6.5 |    4.63 |          8 |     6.08 | False |
| sqlalchemy         | tests-released           |    97.5 |       668.0 |  6.9 |    3.61 |          8 |     4.16 | False |
| sqlalchemy         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.07 | False |
| sqlalchemy         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.07 | False |
| sqlalchemy         | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| sqlalchemy         | infer-union              |    61.3 |       217.4 |  3.5 |   10.92 |          3 |    15.85 | False |
| sqlalchemy         | tests-infer-union        |   121.0 |      1028.4 |  8.5 |    5.75 |          8 |     7.22 | False |
| sqlalchemy         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | types-released           |     7.2 |         5.9 |  0.8 |    0.34 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-certain        |     0.6 |         0.3 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | types-fix-unsafe         |     7.6 |         6.5 |  0.9 |     0.3 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-basedpyright |     7.0 |         6.8 |  1.0 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |     7.8 |         6.7 |  0.9 |    0.32 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-pyrefly      |     6.0 |         5.8 |  1.0 |    0.31 |          1 |     0.42 | False |
| sqlalchemy         | types-infer-trace        |     5.6 |         5.0 |  0.9 |     0.3 |          1 |      0.4 | False |
| sqlalchemy         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     0.37 | False |
| pydantic           | fix-certain              |     3.6 |         9.6 |  2.7 |    0.45 |          3 |     0.54 | False |
| pydantic           | fix-likely               |     4.4 |        12.0 |  2.7 |     0.5 |          3 |     0.62 | False |
| pydantic           | fix-unsafe               |     6.8 |        13.3 |  2.0 |    0.52 |          3 |     0.57 | False |
| pydantic           | infer-basedpyright       |    32.1 |        70.4 |  2.2 |    2.59 |          3 |     3.71 | False |
| pydantic           | infer-ty                 |     6.0 |        17.3 |  2.9 |     1.6 |          3 |      1.4 | False |
| pydantic           | infer-pyrefly            |     6.8 |        25.9 |  3.8 |    2.35 |          4 |     3.15 | False |
| pydantic           | census                   |     2.0 |         3.3 |  1.6 |     0.3 |          3 |     0.37 | False |
| pydantic           | coverage                 |     0.8 |         1.5 |  1.9 |     0.2 |          2 |     0.25 | False |
| pydantic           | timing                   |     2.6 |         3.6 |  1.4 |     0.3 |         16 |     0.37 | False |
| pydantic           | traced                   |    93.3 |        63.3 |  0.7 |    0.54 |          1 |     0.56 | False |
| pydantic           | tests-released           |    60.3 |        43.6 |  0.7 |    0.31 |          1 |     0.34 | False |
| pydantic           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic           | infer-union              |    35.7 |       114.1 |  3.2 |    6.16 |          2 |     7.71 | False |
| pydantic           | tests-infer-union        |    60.7 |        39.5 |  0.7 |    0.27 |          1 |     0.42 | False |
| pydantic           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | types-released           |    25.6 |        19.8 |  0.8 |    0.53 |          2 |     0.65 | False |
| pydantic           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | types-infer-basedpyright |    15.2 |        19.4 |  1.3 |    0.54 |          2 |     0.66 | False |
| pydantic           | types-infer-ty           |    12.4 |        16.9 |  1.4 |    0.55 |          2 |     0.65 | False |
| pydantic           | types-infer-pyrefly      |    12.8 |        17.3 |  1.4 |    0.54 |          2 |     0.67 | False |
| pydantic           | types-infer-trace        |    16.8 |        19.5 |  1.2 |    0.53 |          2 |     0.65 | False |
| pydantic           | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |    32.6 |       102.3 |  3.1 |    3.29 |          4 |      4.1 | False |
| pandas             | fix-certain              |    75.7 |       249.5 |  3.3 |    4.07 |          4 |      5.1 | False |
| pandas             | fix-likely               |   124.9 |       383.4 |  3.1 |    7.31 |          4 |     9.12 | False |
| pandas             | fix-unsafe               |    77.3 |       253.5 |  3.3 |    4.33 |          3 |     5.44 | False |
| pandas             | infer-basedpyright       |  1030.1 |      1599.4 |  1.6 |   15.75 |          3 |    20.09 | False |
| pandas             | infer-ty                 |   144.9 |       545.4 |  3.8 |    13.9 |          4 |    17.25 | False |
| pandas             | infer-pyrefly            |    90.5 |       374.2 |  4.1 |   20.73 |          5 |    24.85 | False |
| pandas             | census                   |    14.6 |        14.4 |  1.0 |    0.33 |          4 |      4.1 | False |
| pandas             | coverage                 |     5.2 |        17.7 |  3.4 |    1.06 |          4 |     1.32 | False |
| pandas             | timing                   |    70.8 |       111.9 |  1.6 |    3.29 |         16 |      4.1 | False |
| pandas             | traced                   |   176.7 |      1090.2 |  6.2 |   14.07 |          8 |    18.26 | False |
| pandas             | tests-released           |   100.5 |       742.8 |  7.4 |   13.34 |          9 |    16.79 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.06 | False |
| pandas             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | infer-union              |   532.3 |      1459.6 |  2.7 |   29.88 |          3 |     34.3 | False |
| pandas             | tests-infer-union        |    80.8 |       629.1 |  7.8 |   12.95 |          5 |    16.94 | False |
| pandas             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | types-released           |    51.4 |        85.1 |  1.7 |    2.28 |          2 |     2.72 | False |
| pandas             | types-fix-certain        |     0.8 |         0.7 |  0.9 |     0.1 |          2 |     2.97 | False |
| pandas             | types-fix-likely         |    39.0 |        61.9 |  1.6 |    2.28 |          2 |      2.9 | False |
| pandas             | types-fix-unsafe         |    48.4 |        82.2 |  1.7 |     2.2 |          2 |     2.79 | False |
| pandas             | types-infer-basedpyright |    40.6 |        65.0 |  1.6 |    2.34 |          2 |     2.86 | False |
| pandas             | types-infer-ty           |    40.6 |        64.4 |  1.6 |    2.23 |          2 |     2.64 | False |
| pandas             | types-infer-pyrefly      |    37.8 |        58.7 |  1.6 |    2.28 |          2 |     2.74 | False |
| pandas             | types-infer-trace        |    56.2 |        91.7 |  1.6 |    2.25 |          2 |     2.85 | False |
| pandas             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |    10.8 |        17.1 |  1.6 |    0.83 |          3 |     1.02 | False |
| twisted            | fix-certain              |    11.2 |        33.2 |  3.0 |    0.95 |          3 |     1.19 | False |
| twisted            | fix-likely               |    15.8 |        45.6 |  2.9 |    1.42 |          3 |     1.76 | False |
| twisted            | fix-unsafe               |    12.4 |        35.2 |  2.8 |    0.97 |          3 |     1.21 | False |
| twisted            | infer-basedpyright       |    66.9 |       233.9 |  3.5 |    9.52 |          3 |    10.75 | False |
| twisted            | infer-ty                 |    22.8 |        72.2 |  3.2 |    3.61 |          4 |     3.76 | False |
| twisted            | infer-pyrefly            |    21.6 |        74.6 |  3.5 |    4.28 |          4 |     5.24 | False |
| twisted            | census                   |     3.8 |         3.6 |  0.9 |     0.1 |          3 |     1.02 | False |
| twisted            | coverage                 |     1.8 |         5.4 |  3.0 |    0.37 |          3 |     0.46 | False |
| twisted            | timing                   |     9.2 |        14.1 |  1.5 |    0.82 |         16 |     1.04 | False |
| pip                | check                    |     8.6 |        11.6 |  1.3 |    0.58 |          2 |     0.67 | False |
| pip                | fix-certain              |     9.4 |        25.4 |  2.7 |    0.71 |          3 |     0.89 | False |
| pip                | fix-likely               |    12.0 |        32.1 |  2.7 |     0.9 |          3 |     1.12 | False |
| pip                | fix-unsafe               |     8.0 |        24.4 |  3.0 |    0.72 |          3 |      0.9 | False |
| pip                | infer-basedpyright       |    45.5 |       167.6 |  3.7 |    5.32 |          5 |     6.76 | False |
| pip                | infer-ty                 |    15.8 |        49.7 |  3.1 |    2.81 |          4 |     3.34 | False |
| pip                | infer-pyrefly            |    14.4 |        52.8 |  3.7 |    3.21 |          4 |      4.0 | False |
| pip                | census                   |     2.8 |         2.6 |  0.9 |    0.09 |          2 |     0.67 | False |
| pip                | coverage                 |     1.6 |         3.8 |  2.4 |    0.33 |          3 |      0.4 | False |
| pip                | timing                   |     6.2 |         9.4 |  1.5 |    0.54 |         16 |     0.69 | False |
| structlog          | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |      0.2 | False |
| structlog          | fix-certain              |     1.4 |         2.3 |  1.6 |    0.24 |          3 |     0.32 | False |
| structlog          | fix-likely               |     1.4 |         2.4 |  1.7 |    0.26 |          2 |     0.34 | False |
| structlog          | fix-unsafe               |     1.2 |         2.2 |  1.8 |    0.26 |          2 |      0.3 | False |
| structlog          | infer-basedpyright       |     7.0 |        10.6 |  1.5 |    0.56 |          2 |     0.75 | False |
| structlog          | infer-ty                 |     2.4 |         3.4 |  1.4 |    0.39 |          2 |      0.5 | False |
| structlog          | infer-pyrefly            |     1.8 |         3.0 |  1.7 |    0.38 |          2 |     0.49 | False |
| structlog          | census                   |     2.4 |         1.2 |  0.5 |    0.16 |          2 |      0.2 | False |
| structlog          | coverage                 |     0.6 |         0.5 |  0.8 |    0.14 |          1 |     0.17 | False |
| structlog          | timing                   |     0.6 |         0.7 |  1.2 |    0.16 |         16 |      0.2 | False |
| structlog          | traced                   |     4.4 |         4.6 |  1.0 |    0.27 |          1 |      0.3 | False |
| structlog          | tests-released           |     2.4 |         1.8 |  0.8 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| structlog          | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| structlog          | infer-union              |     9.7 |        13.5 |  1.4 |     1.0 |          2 |     1.26 | False |
| structlog          | tests-infer-union        |     2.6 |         1.7 |  0.7 |    0.07 |          1 |     0.09 | False |
| structlog          | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| structlog          | types-released           |     0.6 |         0.3 |  0.5 |    0.08 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| structlog          | types-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | types-infer-basedpyright |     1.0 |         0.5 |  0.5 |    0.07 |          1 |     0.09 | False |
| structlog          | types-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| structlog          | types-infer-pyrefly      |     0.6 |         0.4 |  0.7 |    0.07 |          1 |     0.09 | False |
| structlog          | types-infer-trace        |     0.6 |         0.4 |  0.7 |    0.07 |          1 |      0.1 | False |
| structlog          | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.17 | False |
| attrs              | fix-certain              |     1.4 |         2.0 |  1.4 |    0.25 |          2 |     0.31 | False |
| attrs              | fix-likely               |     1.6 |         2.1 |  1.3 |    0.25 |          2 |     0.31 | False |
| attrs              | fix-unsafe               |     4.2 |         2.8 |  0.7 |    0.25 |          2 |     0.31 | False |
| attrs              | infer-basedpyright       |     9.2 |        13.4 |  1.5 |    0.57 |          2 |      0.7 | False |
| attrs              | infer-ty                 |     2.8 |         3.4 |  1.2 |    0.39 |          2 |     0.49 | False |
| attrs              | infer-pyrefly            |     3.2 |         6.5 |  2.0 |    0.55 |          2 |     0.67 | False |
| attrs              | census                   |     0.8 |         0.7 |  0.9 |    0.15 |          1 |     0.17 | False |
| attrs              | coverage                 |     0.6 |         0.5 |  0.8 |    0.14 |          1 |     0.17 | False |
| attrs              | timing                   |     0.6 |         0.6 |  1.0 |    0.15 |         16 |     0.19 | False |
| attrs              | traced                   |     5.6 |        23.7 |  4.2 |    0.73 |          5 |     0.91 | False |
| attrs              | tests-released           |     6.0 |        18.8 |  3.1 |    0.59 |          6 |     0.76 | False |
| attrs              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | infer-union              |     7.6 |        15.3 |  2.0 |     1.1 |          2 |     1.45 | False |
| attrs              | tests-infer-union        |     4.8 |        17.2 |  3.6 |    0.58 |          4 |     0.82 | False |
| attrs              | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.21 | False |
| click              | fix-certain              |     1.4 |         2.9 |  2.1 |    0.29 |          2 |     0.36 | False |
| click              | fix-likely               |     2.2 |         3.9 |  1.8 |     0.3 |          2 |     0.36 | False |
| click              | fix-unsafe               |     4.2 |         3.9 |  0.9 |    0.27 |          2 |     0.37 | False |
| click              | infer-basedpyright       |     9.4 |        13.6 |  1.4 |    0.69 |          2 |     0.86 | False |
| click              | infer-ty                 |     2.6 |         5.0 |  1.9 |    0.46 |          2 |     0.57 | False |
| click              | infer-pyrefly            |     3.0 |         7.9 |  2.6 |    0.58 |          3 |     0.77 | False |
| click              | census                   |     1.0 |         1.2 |  1.2 |    0.17 |          2 |     0.21 | False |
| click              | coverage                 |     0.6 |         0.8 |  1.3 |    0.15 |          2 |     0.19 | False |
| click              | timing                   |     1.0 |         1.0 |  1.0 |    0.17 |         16 |     0.21 | False |
| click              | traced                   |     7.4 |         8.7 |  1.2 |    0.29 |          1 |     0.37 | False |
| click              | tests-released           |     7.0 |         5.9 |  0.8 |    0.17 |          1 |      0.2 | False |
| click              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | infer-union              |     7.8 |        18.8 |  2.4 |    1.23 |          3 |     1.62 | False |
| click              | tests-infer-union        |     5.4 |         4.9 |  0.9 |    0.16 |          1 |     0.21 | False |
| click              | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | types-released           |     0.8 |         0.6 |  0.7 |    0.13 |          1 |     0.15 | False |
| click              | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | types-infer-basedpyright |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.15 | False |
| click              | types-infer-ty           |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.15 | False |
| click              | types-infer-pyrefly      |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.15 | False |
| click              | types-infer-trace        |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.12 | False |
| click              | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.21 | False |
| hypercorn          | fix-certain              |     1.4 |         2.6 |  1.9 |    0.25 |          2 |      0.3 | False |
| hypercorn          | fix-likely               |     1.4 |         2.9 |  2.1 |    0.26 |          3 |     0.34 | False |
| hypercorn          | fix-unsafe               |     4.2 |         3.7 |  0.9 |    0.25 |          2 |     0.34 | False |
| hypercorn          | infer-basedpyright       |     4.0 |        12.2 |  3.0 |    0.89 |          3 |     1.11 | False |
| hypercorn          | infer-ty                 |     1.8 |         4.2 |  2.3 |    0.62 |          2 |     0.72 | False |
| hypercorn          | infer-pyrefly            |     2.6 |         9.1 |  3.5 |    0.87 |          5 |     1.16 | False |
| hypercorn          | census                   |     0.8 |         1.0 |  1.2 |    0.17 |          2 |     0.21 | False |
| hypercorn          | coverage                 |     0.6 |         0.7 |  1.2 |    0.14 |          1 |     0.17 | False |
| hypercorn          | timing                   |     0.8 |         0.9 |  1.1 |    0.17 |         16 |     0.21 | False |
| hypercorn          | traced                   |    11.2 |         4.8 |  0.4 |    0.26 |          1 |     0.31 | False |
| hypercorn          | tests-released           |     7.2 |         1.4 |  0.2 |     0.1 |          1 |     0.11 | False |
| hypercorn          | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| hypercorn          | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | infer-union              |    10.8 |        21.5 |  2.0 |    1.82 |          5 |     2.51 | False |
| hypercorn          | tests-infer-union        |     8.0 |         1.4 |  0.2 |    0.09 |          1 |     0.12 | False |
| hypercorn          | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | types-released           |     1.2 |         0.9 |  0.8 |    0.13 |          1 |     0.14 | False |
| hypercorn          | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| hypercorn          | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | types-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | types-infer-basedpyright |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-ty           |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.15 | False |
| hypercorn          | types-infer-pyrefly      |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-trace        |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.04 | False |
| hypercorn          | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.22 | False |
| starlette          | fix-certain              |     1.6 |         3.0 |  1.9 |    0.28 |          3 |     0.35 | False |
| starlette          | fix-likely               |     1.6 |         3.4 |  2.1 |    0.25 |          2 |     0.36 | False |
| starlette          | fix-unsafe               |     5.2 |         4.3 |  0.8 |    0.28 |          2 |     0.34 | False |
| starlette          | infer-basedpyright       |     3.4 |         8.2 |  2.4 |    0.89 |          3 |     1.22 | False |
| starlette          | infer-ty                 |     2.4 |         5.2 |  2.2 |    0.63 |          3 |      0.8 | False |
| starlette          | infer-pyrefly            |     3.2 |        11.8 |  3.7 |    0.92 |          4 |     1.16 | False |
| starlette          | census                   |     0.8 |         1.0 |  1.2 |    0.18 |          2 |     0.22 | False |
| starlette          | coverage                 |     0.4 |         0.6 |  1.5 |    0.14 |          2 |     0.17 | False |
| starlette          | timing                   |     0.8 |         1.1 |  1.4 |    0.18 |         16 |     0.22 | False |
| starlette          | traced                   |    18.8 |        12.4 |  0.7 |    0.24 |          1 |     0.37 | False |
| starlette          | tests-released           |     8.6 |         6.3 |  0.7 |    0.23 |          1 |     0.27 | False |
| starlette          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | infer-union              |    13.4 |        32.2 |  2.4 |    2.16 |          2 |     2.67 | False |
| starlette          | tests-infer-union        |     8.4 |         6.4 |  0.8 |    0.21 |          1 |     0.29 | False |
| starlette          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | types-released           |     2.2 |         1.6 |  0.7 |    0.16 |          1 |     0.15 | False |
| starlette          | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| starlette          | types-infer-basedpyright |     1.8 |         1.3 |  0.7 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-ty           |     1.2 |         1.1 |  0.9 |    0.13 |          1 |     0.15 | False |
| starlette          | types-infer-pyrefly      |     1.6 |         1.3 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     1.6 |         1.4 |  0.9 |    0.12 |          1 |     0.17 | False |
| starlette          | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     1.4 |         1.9 |  1.4 |     0.2 |          2 |     0.25 | False |
| werkzeug           | fix-certain              |     2.2 |         5.1 |  2.3 |    0.32 |          3 |      0.4 | False |
| werkzeug           | fix-likely               |     2.6 |         5.9 |  2.3 |    0.29 |          3 |      0.4 | False |
| werkzeug           | fix-unsafe               |     2.0 |         4.8 |  2.4 |    0.33 |          3 |     0.41 | False |
| werkzeug           | infer-basedpyright       |     8.4 |        25.5 |  3.0 |    1.17 |          4 |     1.55 | False |
| werkzeug           | infer-ty                 |     3.2 |         8.2 |  2.6 |    0.72 |          3 |     0.94 | False |
| werkzeug           | infer-pyrefly            |     3.8 |        11.0 |  2.9 |    1.03 |          4 |     1.35 | False |
| werkzeug           | census                   |     1.6 |         0.6 |  0.4 |    0.04 |          2 |     0.25 | False |
| werkzeug           | coverage                 |     0.8 |         0.9 |  1.1 |    0.16 |          2 |      0.2 | False |
| werkzeug           | timing                   |     1.2 |         1.7 |  1.4 |     0.2 |         16 |     0.25 | False |
| werkzeug           | traced                   |    15.1 |        13.1 |  0.9 |    0.32 |          1 |     0.42 | False |
| werkzeug           | tests-released           |    12.7 |         7.8 |  0.6 |    0.17 |          1 |      0.2 | False |
| werkzeug           | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| werkzeug           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| werkzeug           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | infer-union              |    16.6 |        48.3 |  2.9 |    2.51 |          2 |     3.12 | False |
| werkzeug           | tests-infer-union        |     8.8 |         6.9 |  0.8 |    0.16 |          1 |     0.21 | False |
| werkzeug           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | types-released           |     1.6 |         1.0 |  0.6 |    0.12 |          1 |     0.12 | False |
| werkzeug           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | types-infer-basedpyright |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types-infer-ty           |     1.4 |         1.0 |  0.7 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-infer-pyrefly      |     1.0 |         0.8 |  0.8 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-infer-trace        |     1.2 |         0.9 |  0.8 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     1.6 |         2.3 |  1.4 |    0.27 |          1 |     0.31 | False |
| mkdocs             | fix-certain              |     2.6 |         5.3 |  2.0 |    0.34 |          2 |     0.42 | False |
| mkdocs             | fix-likely               |     3.0 |         6.4 |  2.1 |    0.35 |          3 |     0.44 | False |
| mkdocs             | fix-unsafe               |     3.0 |         6.0 |  2.0 |    0.35 |          2 |     0.41 | False |
| mkdocs             | infer-basedpyright       |    11.6 |        28.1 |  2.4 |    1.14 |          3 |      1.7 | False |
| mkdocs             | infer-ty                 |     4.2 |         9.1 |  2.2 |    0.81 |          2 |     1.06 | False |
| mkdocs             | infer-pyrefly            |     4.6 |        15.1 |  3.3 |    1.08 |          4 |     1.42 | False |
| mkdocs             | census                   |     0.8 |         0.6 |  0.7 |    0.05 |          1 |     0.31 | False |
| mkdocs             | coverage                 |     0.8 |         1.2 |  1.5 |    0.17 |          2 |     0.21 | False |
| mkdocs             | timing                   |     1.6 |         1.9 |  1.2 |    0.25 |         16 |     0.31 | False |
| mkdocs             | traced                   |    23.6 |        10.9 |  0.5 |    0.36 |          1 |     0.42 | False |
| mkdocs             | tests-released           |    14.6 |         2.8 |  0.2 |    0.08 |          1 |     0.09 | False |
| mkdocs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mkdocs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mkdocs             | infer-union              |    13.0 |        36.0 |  2.8 |    2.83 |          3 |     3.55 | False |
| mkdocs             | tests-infer-union        |    10.0 |         2.4 |  0.2 |    0.07 |          1 |      0.1 | False |
| mkdocs             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| httpx              | fix-certain              |     1.2 |         2.4 |  2.0 |    0.25 |          2 |     0.31 | False |
| httpx              | fix-likely               |     1.8 |         3.3 |  1.8 |    0.26 |          2 |     0.31 | False |
| httpx              | fix-unsafe               |     4.4 |         3.8 |  0.9 |    0.27 |          2 |     0.34 | False |
| httpx              | infer-basedpyright       |     9.2 |        14.7 |  1.6 |    0.65 |          2 |     0.86 | False |
| httpx              | infer-ty                 |     5.4 |         5.5 |  1.0 |    0.49 |          2 |      0.6 | False |
| httpx              | infer-pyrefly            |     2.2 |         6.6 |  3.0 |    0.62 |          3 |     0.81 | False |
| httpx              | census                   |     1.4 |         1.4 |  1.0 |    0.19 |          1 |     0.21 | False |
| httpx              | coverage                 |     0.6 |         0.7 |  1.2 |    0.14 |          1 |     0.17 | False |
| httpx              | timing                   |     0.8 |         0.9 |  1.1 |    0.17 |         16 |     0.21 | False |
| httpx              | traced                   |     9.0 |         8.9 |  1.0 |    0.27 |          1 |     0.36 | False |
| httpx              | tests-released           |     6.6 |         5.3 |  0.8 |    0.21 |          1 |     0.26 | False |
| httpx              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| httpx              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | infer-union              |     6.0 |        12.6 |  2.1 |    1.29 |          3 |      1.7 | False |
| httpx              | tests-infer-union        |     5.8 |         4.0 |  0.7 |     0.2 |          1 |     0.27 | False |
| httpx              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | types-released           |     8.5 |         5.9 |  0.7 |    0.26 |          1 |     0.26 | False |
| httpx              | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | types-infer-basedpyright |     8.0 |         6.5 |  0.8 |    0.19 |          1 |     0.24 | False |
| httpx              | types-infer-ty           |     5.8 |         5.4 |  0.9 |     0.2 |          1 |     0.26 | False |
| httpx              | types-infer-pyrefly      |     4.6 |         4.4 |  1.0 |     0.2 |          1 |     0.26 | False |
| httpx              | types-infer-trace        |     5.8 |         5.5 |  0.9 |    0.19 |          1 |      0.3 | False |
| httpx              | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.24 | False |
| black              | fix-certain              |     2.2 |         4.3 |  2.0 |    0.32 |          3 |     0.36 | False |
| black              | fix-likely               |     2.0 |         4.5 |  2.2 |    0.32 |          3 |      0.4 | False |
| black              | fix-unsafe               |     3.0 |         4.3 |  1.4 |    0.31 |          3 |     0.39 | False |
| black              | infer-basedpyright       |    15.6 |        21.4 |  1.4 |    0.77 |          1 |     0.95 | False |
| black              | infer-ty                 |     2.0 |         4.4 |  2.2 |     0.5 |          3 |     0.66 | False |
| black              | infer-pyrefly            |     3.6 |         9.3 |  2.6 |    0.67 |          2 |     0.84 | False |
| black              | census                   |     1.2 |         1.4 |  1.2 |    0.19 |          2 |     0.24 | False |
| black              | coverage                 |     0.8 |         0.9 |  1.1 |    0.16 |          2 |      0.2 | False |
| black              | timing                   |     1.0 |         1.2 |  1.2 |    0.19 |         16 |     0.24 | False |
| black              | traced                   |    12.2 |        66.2 |  5.4 |    0.88 |          5 |     1.09 | False |
| black              | tests-released           |     8.8 |        47.5 |  5.4 |    0.74 |          7 |     0.96 | False |
| black              | tests-fix-certain        |     6.4 |        44.1 |  6.9 |    0.75 |          8 |     0.94 | False |
| black              | tests-fix-likely         |     6.8 |        42.9 |  6.3 |    0.78 |          6 |     0.95 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| black              | tests-infer-basedpyright |    10.8 |        51.0 |  4.7 |     0.8 |          7 |     0.95 | False |
| black              | tests-infer-ty           |     7.6 |        48.6 |  6.4 |    0.77 |          8 |     0.96 | False |
| black              | tests-infer-pyrefly      |    14.4 |        46.5 |  3.2 |    0.78 |          7 |     0.96 | False |
| black              | tests-infer-trace        |     7.2 |        48.4 |  6.7 |    0.74 |          8 |     0.94 | False |
| black              | infer-union              |     9.2 |        18.4 |  2.0 |    1.38 |          2 |     1.92 | False |
| black              | tests-infer-union        |     7.8 |        47.2 |  6.1 |    0.74 |          6 |     0.95 | False |
| black              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | check                    |     1.0 |         1.4 |  1.4 |    0.21 |          2 |     0.26 | False |
| fastapi            | fix-certain              |     2.2 |         3.7 |  1.7 |    0.32 |          2 |     0.36 | False |
| fastapi            | fix-likely               |     4.0 |         5.9 |  1.5 |    0.44 |          2 |     0.46 | False |
| fastapi            | fix-unsafe               |     5.8 |         6.1 |  1.1 |    0.37 |          1 |     0.41 | False |
| fastapi            | infer-basedpyright       |    12.6 |        31.1 |  2.5 |    1.23 |          3 |     1.54 | False |
| fastapi            | infer-ty                 |     4.4 |         8.4 |  1.9 |    0.84 |          2 |     1.04 | False |
| fastapi            | infer-pyrefly            |     4.4 |        14.3 |  3.2 |    1.14 |          3 |     1.42 | False |
| fastapi            | census                   |     0.4 |         0.3 |  0.7 |    0.04 |          2 |     0.26 | False |
| fastapi            | coverage                 |     0.6 |         0.8 |  1.3 |    0.16 |          2 |      0.2 | False |
| fastapi            | timing                   |     1.2 |         1.4 |  1.2 |    0.21 |         16 |     0.26 | False |
| fastapi            | traced                   |    22.4 |       112.0 |  5.0 |    2.33 |          7 |      2.9 | False |
| fastapi            | tests-released           |    19.0 |       105.2 |  5.5 |    2.08 |          8 |     2.61 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | infer-union              |    13.6 |        35.2 |  2.6 |    2.32 |          2 |     3.24 | False |
| fastapi            | tests-infer-union        |    16.4 |       101.7 |  6.2 |    2.04 |          6 |     2.62 | False |
| fastapi            | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| cattrs             | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| cattrs             | fix-certain              |     1.6 |         2.7 |  1.7 |    0.26 |          2 |     0.32 | False |
| cattrs             | fix-likely               |     1.6 |         2.9 |  1.8 |    0.24 |          2 |      0.3 | False |
| cattrs             | fix-unsafe               |     1.6 |         2.7 |  1.7 |    0.24 |          2 |     0.32 | False |
| cattrs             | infer-basedpyright       |     8.0 |        16.9 |  2.1 |    0.93 |          3 |      1.2 | False |
| cattrs             | infer-ty                 |     2.2 |         4.4 |  2.0 |    0.62 |          2 |     0.67 | False |
| cattrs             | infer-pyrefly            |     2.8 |         7.4 |  2.6 |    0.91 |          4 |     1.15 | False |
| cattrs             | census                   |     1.2 |         1.4 |  1.2 |    0.19 |          1 |     0.21 | False |
| cattrs             | coverage                 |     0.6 |         0.6 |  1.0 |    0.14 |          1 |     0.17 | False |
| cattrs             | timing                   |     0.8 |         0.9 |  1.1 |    0.18 |         16 |     0.21 | False |
| cattrs             | traced                   |    20.4 |       134.5 |  6.6 |    1.35 |          8 |     1.71 | False |
| cattrs             | tests-released           |    18.6 |       115.5 |  6.2 |    0.98 |          8 |     1.25 | False |
| cattrs             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| cattrs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| cattrs             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| cattrs             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| cattrs             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| cattrs             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| cattrs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| cattrs             | infer-union              |    10.2 |        23.4 |  2.3 |     1.9 |          2 |     2.55 | False |
| cattrs             | tests-infer-union        |    25.2 |       141.0 |  5.6 |     1.0 |          4 |     1.26 | False |
| cattrs             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pytest             | check                    |     1.6 |         2.9 |  1.8 |    0.27 |          2 |     0.34 | False |
| pytest             | fix-certain              |     3.8 |         8.4 |  2.2 |    0.39 |          2 |      0.5 | False |
| pytest             | fix-likely               |     4.6 |        10.6 |  2.3 |    0.41 |          3 |     0.51 | False |
| pytest             | fix-unsafe               |     4.6 |         8.6 |  1.9 |    0.41 |          2 |      0.5 | False |
| pytest             | infer-basedpyright       |    15.6 |        55.3 |  3.5 |    2.15 |          4 |     2.77 | False |
| pytest             | infer-ty                 |     6.2 |        16.0 |  2.6 |    1.21 |          3 |     1.11 | False |
| pytest             | infer-pyrefly            |     6.2 |        18.8 |  3.0 |    1.75 |          4 |     1.67 | False |
| pytest             | census                   |     1.0 |         0.8 |  0.8 |    0.04 |          2 |     0.34 | False |
| pytest             | coverage                 |     0.6 |         1.2 |  2.0 |    0.19 |          2 |     0.24 | False |
| pytest             | timing                   |     2.2 |         3.0 |  1.4 |    0.27 |         16 |     0.34 | False |
| pytest             | traced                   |    51.9 |       347.5 |  6.7 |    1.68 |          7 |     2.12 | False |
| pytest             | tests-released           |    20.8 |       157.0 |  7.5 |    1.35 |          8 |     1.71 | False |
| pytest             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pytest             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pytest             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pytest             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pytest             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pytest             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pytest             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pytest             | infer-union              |    16.4 |        66.8 |  4.1 |    3.82 |          4 |     5.46 | False |
| pytest             | tests-infer-union        |    20.8 |       156.2 |  7.5 |    1.32 |          8 |     1.69 | False |
| pytest             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| botocore           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.35 | False |
| botocore           | fix-certain              |     4.4 |         9.9 |  2.2 |    0.37 |          3 |     0.46 | False |
| botocore           | fix-likely               |     4.8 |        11.9 |  2.5 |    0.45 |          3 |     0.56 | False |
| botocore           | fix-unsafe               |     3.8 |         9.4 |  2.5 |    0.39 |          3 |     0.49 | False |
| botocore           | infer-basedpyright       |    16.8 |        49.1 |  2.9 |    1.85 |          4 |     2.85 | False |
| botocore           | infer-ty                 |     5.6 |        15.0 |  2.7 |    1.19 |          3 |      1.0 | False |
| botocore           | infer-pyrefly            |     6.0 |        15.8 |  2.6 |    1.21 |          3 |      1.6 | False |
| botocore           | census                   |     2.8 |         4.8 |  1.7 |    0.28 |          2 |     0.35 | False |
| botocore           | coverage                 |     1.6 |         1.7 |  1.1 |    0.18 |          2 |     0.22 | False |
| botocore           | timing                   |     2.6 |         3.8 |  1.5 |    0.28 |         16 |     0.35 | False |
| botocore           | traced                   |    40.7 |       121.6 |  3.0 |     5.1 |          4 |     6.52 | False |
| botocore           | tests-released           |    26.8 |        85.5 |  3.2 |    4.89 |          5 |     6.16 | False |
| botocore           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | infer-union              |    18.6 |        61.8 |  3.3 |    4.18 |          4 |     5.22 | False |
| botocore           | tests-infer-union        |    25.8 |        85.3 |  3.3 |    4.82 |          4 |     6.16 | False |
| botocore           | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | check                    |     1.2 |         1.6 |  1.3 |     0.2 |          1 |     0.22 | False |
| uvicorn            | fix-certain              |     1.4 |         3.0 |  2.1 |    0.28 |          2 |     0.31 | False |
| uvicorn            | fix-likely               |     1.8 |         3.8 |  2.1 |    0.28 |          3 |     0.32 | False |
| uvicorn            | fix-unsafe               |     1.6 |         3.2 |  2.0 |    0.29 |          2 |     0.31 | False |
| uvicorn            | infer-basedpyright       |    11.8 |        15.6 |  1.3 |    0.91 |          3 |     1.32 | False |
| uvicorn            | infer-ty                 |     2.4 |         4.6 |  1.9 |    0.66 |          2 |     0.85 | False |
| uvicorn            | infer-pyrefly            |     2.8 |         8.0 |  2.9 |    0.91 |          4 |     0.95 | False |
| uvicorn            | census                   |     0.4 |         0.3 |  0.7 |    0.03 |          1 |     0.22 | False |
| uvicorn            | coverage                 |     0.6 |         0.7 |  1.2 |    0.15 |          1 |     0.19 | False |
| uvicorn            | timing                   |     0.8 |         1.1 |  1.4 |    0.18 |         16 |     0.22 | False |
| uvicorn            | traced                   |    42.0 |        26.0 |  0.6 |    0.93 |          1 |     1.21 | False |
| uvicorn            | tests-released           |    39.3 |        22.1 |  0.6 |    0.82 |          1 |     0.97 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| uvicorn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| uvicorn            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| uvicorn            | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| uvicorn            | infer-union              |     5.4 |        19.4 |  3.6 |    2.26 |          4 |     2.81 | False |
| uvicorn            | tests-infer-union        |    30.5 |        23.0 |  0.8 |     0.8 |          1 |     1.09 | False |
| uvicorn            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | types-released           |     1.8 |         1.4 |  0.8 |    0.15 |          1 |     0.15 | False |
| uvicorn            | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| uvicorn            | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| uvicorn            | types-infer-basedpyright |     1.8 |         1.3 |  0.7 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-ty           |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.15 | False |
| uvicorn            | types-infer-pyrefly      |     1.0 |         0.7 |  0.7 |    0.11 |          1 |     0.15 | False |
| uvicorn            | types-infer-trace        |     2.8 |         1.6 |  0.6 |    0.12 |          1 |     0.16 | False |
| uvicorn            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     0.6 |         0.1 |  0.2 |    0.03 |          2 |     0.31 | False |
| mcp                | fix-certain              |     2.8 |         6.6 |  2.4 |    0.32 |          3 |     0.44 | False |
| mcp                | fix-likely               |     3.4 |         8.4 |  2.5 |    0.42 |          3 |     0.52 | False |
| mcp                | fix-unsafe               |     3.6 |         7.6 |  2.1 |    0.36 |          3 |     0.45 | False |
| mcp                | infer-basedpyright       |     9.4 |        30.6 |  3.3 |    2.15 |          5 |     2.99 | False |
| mcp                | infer-ty                 |     4.0 |        10.8 |  2.7 |    1.33 |          4 |     1.01 | False |
| mcp                | infer-pyrefly            |     4.0 |        16.5 |  4.1 |    1.95 |          6 |     2.19 | False |
| mcp                | census                   |     1.6 |         2.7 |  1.7 |    0.25 |          2 |     0.31 | False |
| mcp                | coverage                 |     0.8 |         1.3 |  1.6 |    0.17 |          2 |     0.21 | False |
| mcp                | timing                   |     1.8 |         2.4 |  1.3 |    0.25 |         16 |     0.31 | False |
| mcp                | traced                   |    18.6 |        84.3 |  4.5 |    2.02 |          6 |     2.87 | False |
| mcp                | tests-released           |    15.0 |        67.0 |  4.5 |    1.82 |          7 |     2.62 | False |
| mcp                | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | infer-union              |    13.2 |        59.2 |  4.5 |    5.01 |          3 |     6.14 | False |
| mcp                | tests-infer-union        |    16.6 |        69.7 |  4.2 |    1.78 |          4 |     2.62 | False |
| mcp                | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | types-released           |    22.8 |        27.5 |  1.2 |    1.27 |          2 |     1.54 | False |
| mcp                | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | types-fix-likely         |    13.8 |        21.8 |  1.6 |    1.26 |          2 |     1.59 | False |
| mcp                | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | types-infer-basedpyright |    17.2 |        25.2 |  1.5 |    1.26 |          2 |     1.57 | False |
| mcp                | types-infer-ty           |    18.6 |        25.9 |  1.4 |    1.26 |          2 |     1.61 | False |
| mcp                | types-infer-pyrefly      |    13.0 |        18.5 |  1.4 |    1.25 |          2 |     1.57 | False |
| mcp                | types-infer-trace        |    18.2 |        24.1 |  1.3 |    1.26 |          2 |     1.59 | False |
| mcp                | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          3 |     0.52 | False |
| textual            | fix-certain              |     5.4 |        14.8 |  2.7 |    0.53 |          3 |     0.66 | False |
| textual            | fix-likely               |     6.4 |        18.5 |  2.9 |     0.6 |          3 |     0.75 | False |
| textual            | fix-unsafe               |     4.6 |        14.1 |  3.1 |    0.54 |          3 |     0.65 | False |
| textual            | infer-basedpyright       |    20.0 |        85.1 |  4.3 |    3.76 |          5 |     4.69 | False |
| textual            | infer-ty                 |     7.0 |        23.2 |  3.3 |     2.0 |          4 |     2.49 | False |
| textual            | infer-pyrefly            |     8.2 |        30.6 |  3.7 |    2.46 |          5 |     3.09 | False |
| textual            | census                   |     3.6 |         6.8 |  1.9 |    0.42 |          3 |     0.52 | False |
| textual            | coverage                 |     1.2 |         2.6 |  2.2 |    0.24 |          3 |      0.3 | False |
| textual            | timing                   |     3.8 |         5.5 |  1.4 |    0.42 |         16 |     0.54 | False |
| pdm                | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.52 | False |
| pdm                | fix-certain              |     3.8 |         9.2 |  2.4 |    0.45 |          3 |     0.55 | False |
| pdm                | fix-likely               |     4.6 |        11.7 |  2.5 |    0.53 |          3 |     0.66 | False |
| pdm                | fix-unsafe               |    11.8 |        12.0 |  1.0 |    0.49 |          3 |     0.55 | False |
| pdm                | infer-basedpyright       |    11.2 |        48.3 |  4.3 |    2.67 |          5 |     3.41 | False |
| pdm                | infer-ty                 |     5.8 |        16.4 |  2.8 |    1.55 |          4 |     1.94 | False |
| pdm                | infer-pyrefly            |     6.0 |        21.4 |  3.6 |    2.15 |          5 |     2.69 | False |
| pdm                | census                   |     2.0 |         3.6 |  1.8 |    0.42 |          2 |     0.52 | False |
| pdm                | coverage                 |     1.0 |         1.6 |  1.6 |    0.18 |          2 |     0.22 | False |
| pdm                | timing                   |     2.4 |         3.4 |  1.4 |    0.42 |         16 |     0.52 | False |
| pdm                | traced                   |    21.2 |       114.4 |  5.4 |    1.57 |          7 |     2.05 | False |
| pdm                | tests-released           |    19.0 |        95.1 |  5.0 |    1.21 |          7 |     1.64 | False |
| pdm                | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pdm                | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pdm                | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pdm                | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pdm                | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pdm                | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pdm                | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pdm                | infer-union              |    10.8 |        50.8 |  4.7 |    4.91 |          3 |     6.59 | False |
| pdm                | tests-infer-union        |    27.6 |       106.8 |  3.9 |    1.19 |          4 |     1.71 | False |
| pdm                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     0.41 | False |
| strawberry-graphql | fix-certain              |     3.4 |         8.6 |  2.5 |    0.43 |          3 |     0.52 | False |
| strawberry-graphql | fix-likely               |     4.4 |        11.7 |  2.7 |    0.56 |          3 |      0.7 | False |
| strawberry-graphql | fix-unsafe               |     4.2 |         9.6 |  2.3 |    0.53 |          3 |     0.54 | False |
| strawberry-graphql | infer-basedpyright       |    17.6 |        86.5 |  4.9 |     3.2 |          6 |     3.97 | False |
| strawberry-graphql | infer-ty                 |     5.6 |        18.6 |  3.3 |    1.55 |          4 |     1.95 | False |
| strawberry-graphql | infer-pyrefly            |     6.6 |        32.0 |  4.8 |    2.29 |          5 |     2.74 | False |
| strawberry-graphql | census                   |     1.8 |         3.7 |  2.1 |    0.33 |          3 |     0.41 | False |
| strawberry-graphql | coverage                 |     0.8 |         1.2 |  1.5 |    0.18 |          2 |     0.22 | False |
| strawberry-graphql | timing                   |     2.4 |         3.4 |  1.4 |    0.34 |         16 |     0.41 | False |
| strawberry-graphql | traced                   |    18.0 |        97.3 |  5.4 |    1.47 |          7 |     1.86 | False |
| strawberry-graphql | tests-released           |    11.6 |        74.9 |  6.5 |    1.25 |          8 |      1.6 | False |
| strawberry-graphql | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | infer-union              |    15.4 |        97.0 |  6.3 |    5.35 |          4 |     7.42 | False |
| strawberry-graphql | tests-infer-union        |    18.8 |        92.8 |  4.9 |    1.22 |          4 |     1.57 | False |
| strawberry-graphql | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | types-released           |     2.0 |         1.5 |  0.8 |    0.28 |          1 |     0.27 | False |
| strawberry-graphql | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | types-infer-basedpyright |     1.4 |         1.2 |  0.9 |    0.19 |          1 |      0.3 | False |
| strawberry-graphql | types-infer-ty           |     1.6 |         1.5 |  0.9 |    0.19 |          1 |     0.31 | False |
| strawberry-graphql | types-infer-pyrefly      |     1.8 |         1.5 |  0.8 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-trace        |     1.8 |         1.5 |  0.8 |     0.2 |          1 |     0.24 | False |
| strawberry-graphql | types                    |     0.6 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     2.4 |         6.2 |  2.6 |    0.41 |          3 |     0.51 | False |
| pygments           | fix-certain              |     5.2 |        15.2 |  2.9 |    0.58 |          3 |     0.71 | False |
| pygments           | fix-likely               |     6.0 |        17.7 |  2.9 |    0.58 |          3 |     0.74 | False |
| pygments           | fix-unsafe               |     5.8 |        15.9 |  2.7 |    0.58 |          3 |      0.7 | False |
| pygments           | infer-basedpyright       |    26.6 |        83.9 |  3.2 |    2.35 |          4 |      4.1 | False |
| pygments           | infer-ty                 |     8.6 |        23.4 |  2.7 |    1.63 |          3 |     1.85 | False |
| pygments           | infer-pyrefly            |     9.8 |        27.6 |  2.8 |    1.87 |          3 |     2.17 | False |
| pygments           | census                   |     2.0 |         1.8 |  0.9 |    0.06 |          3 |     0.51 | False |
| pygments           | coverage                 |     1.2 |         2.9 |  2.4 |    0.27 |          3 |     0.34 | False |
| pygments           | timing                   |     4.0 |         6.0 |  1.5 |    0.41 |         16 |     0.51 | False |
| pygments           | traced                   |    30.9 |        36.1 |  1.2 |    0.63 |          1 |      0.8 | False |
| pygments           | tests-released           |    14.6 |        13.8 |  0.9 |    0.28 |          1 |     0.29 | False |
| pygments           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pygments           | infer-union              |    30.2 |       108.4 |  3.6 |    6.33 |          4 |     7.74 | False |
| pygments           | tests-infer-union        |    12.4 |        11.9 |  1.0 |    0.23 |          1 |     0.36 | False |
| pygments           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | check                    |     0.8 |         0.2 |  0.2 |    0.03 |          3 |     0.37 | False |
| streamlink         | fix-certain              |     4.6 |        11.2 |  2.4 |    0.44 |          3 |     0.56 | False |
| streamlink         | fix-likely               |     4.8 |        13.7 |  2.9 |    0.48 |          3 |     0.59 | False |
| streamlink         | fix-unsafe               |     4.6 |        11.9 |  2.6 |    0.45 |          3 |     0.52 | False |
| streamlink         | infer-basedpyright       |    12.0 |        47.9 |  4.0 |    2.51 |          5 |     3.65 | False |
| streamlink         | infer-ty                 |     6.8 |        21.0 |  3.1 |    1.52 |          3 |     1.91 | False |
| streamlink         | infer-pyrefly            |    10.4 |        24.1 |  2.3 |    2.01 |          5 |     2.57 | False |
| streamlink         | census                   |     2.4 |         4.9 |  2.0 |     0.3 |          3 |     0.37 | False |
| streamlink         | coverage                 |     1.2 |         2.0 |  1.7 |    0.21 |          2 |     0.26 | False |
| streamlink         | timing                   |     3.0 |         4.3 |  1.4 |    0.31 |         16 |     0.37 | False |
| streamlink         | traced                   |    23.7 |        26.1 |  1.1 |     0.4 |          1 |     0.49 | False |
| streamlink         | tests-released           |    14.7 |        11.2 |  0.8 |    0.18 |          1 |     0.21 | False |
| streamlink         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| streamlink         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| streamlink         | tests-infer-pyrefly      |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| streamlink         | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| streamlink         | infer-union              |    22.3 |        91.9 |  4.1 |    5.91 |          3 |      7.5 | False |
| streamlink         | tests-infer-union        |    11.4 |        10.3 |  0.9 |    0.17 |          1 |     0.24 | False |
| streamlink         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | types-released           |    10.2 |         6.9 |  0.7 |     0.4 |          1 |     0.46 | False |
| streamlink         | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | types-infer-basedpyright |     6.8 |         6.1 |  0.9 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-ty           |     8.2 |         7.0 |  0.9 |    0.36 |          1 |     0.46 | False |
| streamlink         | types-infer-pyrefly      |    10.2 |         7.6 |  0.7 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-trace        |     7.8 |         6.4 |  0.8 |    0.35 |          1 |     0.45 | False |
| streamlink         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     2.6 |         0.2 |  0.1 |    0.04 |          2 |     0.55 | False |
| sphinx             | fix-certain              |     5.6 |        17.9 |  3.2 |    0.63 |          3 |     0.77 | False |
| sphinx             | fix-likely               |     8.2 |        25.8 |  3.1 |    0.82 |          4 |     1.02 | False |
| sphinx             | fix-unsafe               |     7.8 |        23.2 |  3.0 |    0.67 |          3 |      0.8 | False |
| sphinx             | infer-basedpyright       |    17.8 |        82.0 |  4.6 |    4.26 |          6 |     5.36 | False |
| sphinx             | infer-ty                 |    11.8 |        38.1 |  3.2 |    2.22 |          4 |      2.8 | False |
| sphinx             | infer-pyrefly            |     9.0 |        31.5 |  3.5 |    2.47 |          4 |     2.54 | False |
| sphinx             | census                   |     4.2 |         8.4 |  2.0 |    0.44 |          2 |     0.55 | False |
| sphinx             | coverage                 |     1.2 |         2.9 |  2.4 |    0.27 |          3 |     0.34 | False |
| sphinx             | timing                   |     5.2 |         7.7 |  1.5 |    0.44 |         16 |     0.55 | False |
| sphinx             | traced                   |    21.8 |       127.2 |  5.8 |     1.7 |          8 |     2.09 | False |
| sphinx             | tests-released           |    14.8 |       106.8 |  7.2 |    1.34 |          8 |     1.69 | False |
| sphinx             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| sphinx             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.05 | False |
| sphinx             | tests-infer-basedpyright |    14.8 |       106.5 |  7.2 |    1.32 |          8 |     1.65 | False |
| sphinx             | tests-infer-ty           |    16.8 |       118.8 |  7.1 |    1.32 |          8 |     1.64 | False |
| sphinx             | tests-infer-pyrefly      |    15.0 |       108.4 |  7.2 |    1.32 |          8 |     1.65 | False |
| sphinx             | tests-infer-trace        |    16.8 |       115.6 |  6.9 |    1.32 |          8 |     1.64 | False |
| sphinx             | infer-union              |    24.7 |       101.1 |  4.1 |    6.54 |          4 |     9.31 | False |
| sphinx             | tests-infer-union        |    16.0 |       108.2 |  6.8 |    1.31 |          5 |     1.74 | False |
| sphinx             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.64 | False |
| sphinx             | types-released           |    10.5 |         6.6 |  0.6 |    0.33 |          1 |     0.36 | False |
| sphinx             | types-fix-certain        |     6.4 |         6.1 |  1.0 |    0.26 |          1 |     0.04 | False |
| sphinx             | types-fix-likely         |     5.4 |         5.1 |  0.9 |    0.26 |          1 |     0.05 | False |
| sphinx             | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.05 | False |
| sphinx             | types-infer-basedpyright |     8.0 |         5.7 |  0.7 |    0.25 |          1 |     0.37 | False |
| sphinx             | types-infer-ty           |     6.2 |         5.6 |  0.9 |    0.28 |          1 |     0.36 | False |
| sphinx             | types-infer-pyrefly      |     5.2 |         5.0 |  1.0 |    0.25 |          1 |     0.42 | False |
| sphinx             | types-infer-trace        |     7.0 |         5.9 |  0.8 |    0.26 |          1 |     0.32 | False |
| sphinx             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     1.2 |         2.2 |  1.8 |    0.23 |          2 |     0.29 | False |
| tox                | fix-certain              |     2.4 |         6.3 |  2.6 |    0.35 |          3 |     0.44 | False |
| tox                | fix-likely               |     3.0 |         7.9 |  2.6 |    0.37 |          3 |     0.46 | False |
| tox                | fix-unsafe               |     3.6 |         7.3 |  2.0 |    0.31 |          2 |     0.42 | False |
| tox                | infer-basedpyright       |    15.4 |        41.8 |  2.7 |    2.25 |          5 |     2.75 | False |
| tox                | infer-ty                 |     4.8 |        15.2 |  3.2 |    1.26 |          4 |     1.65 | False |
| tox                | infer-pyrefly            |     4.2 |        10.9 |  2.6 |    1.38 |          3 |      1.2 | False |
| tox                | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.29 | False |
| tox                | coverage                 |     0.8 |         1.3 |  1.6 |    0.17 |          2 |     0.21 | False |
| tox                | timing                   |     1.6 |         2.3 |  1.4 |    0.23 |         16 |     0.29 | False |
| tox                | traced                   |    26.8 |       140.3 |  5.2 |    1.48 |          7 |      1.9 | False |
| tox                | tests-released           |    17.2 |        93.7 |  5.4 |    1.36 |          6 |     1.75 | False |
| tox                | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| tox                | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| tox                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| tox                | infer-union              |     9.2 |        33.6 |  3.7 |    3.93 |          3 |     5.14 | False |
| tox                | tests-infer-union        |    19.2 |        94.7 |  4.9 |    1.33 |          4 |     1.81 | False |
| tox                | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | check                    |     3.2 |         4.4 |  1.4 |    0.38 |          2 |     0.45 | False |
| pint               | fix-certain              |     6.0 |        11.2 |  1.9 |    0.42 |          2 |     0.52 | False |
| pint               | fix-likely               |     7.4 |        13.2 |  1.8 |     0.5 |          2 |      0.6 | False |
| pint               | fix-unsafe               |     5.0 |         9.2 |  1.8 |    0.42 |          2 |      0.5 | False |
| pint               | infer-basedpyright       |    43.5 |       119.1 |  2.7 |    3.32 |          3 |     4.12 | False |
| pint               | infer-ty                 |     8.4 |        20.6 |  2.5 |    1.97 |          3 |      3.3 | False |
| pint               | infer-pyrefly            |     6.8 |        26.3 |  3.9 |     1.9 |          4 |     2.29 | False |
| pint               | census                   |     1.2 |         1.1 |  0.9 |    0.05 |          2 |     0.45 | False |
| pint               | coverage                 |     1.0 |         1.6 |  1.6 |    0.19 |          2 |     0.24 | False |
| pint               | timing                   |     2.8 |         3.7 |  1.3 |    0.38 |         16 |     0.45 | False |
| pint               | traced                   |    44.5 |        42.0 |  0.9 |    0.43 |          1 |     0.51 | False |
| pint               | tests-released           |    27.1 |        25.5 |  0.9 |    0.14 |          1 |     0.16 | False |
| pint               | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pint               | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pint               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | infer-union              |    39.9 |       127.4 |  3.2 |    5.92 |          3 |     8.87 | False |
| pint               | tests-infer-union        |    28.0 |        27.4 |  1.0 |    0.13 |          1 |     0.17 | False |
| pint               | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | types-released           |     7.8 |        11.5 |  1.5 |    0.53 |          2 |     0.69 | False |
| pint               | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.66 | False |
| pint               | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.65 | False |
| pint               | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pint               | types-infer-basedpyright |     6.0 |        10.4 |  1.7 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-ty           |     7.6 |        11.9 |  1.6 |    0.53 |          2 |     0.69 | False |
| pint               | types-infer-pyrefly      |     5.8 |         9.8 |  1.7 |    0.54 |          2 |     0.71 | False |
| pint               | types-infer-trace        |     7.8 |        11.0 |  1.4 |    0.52 |          2 |     0.66 | False |
| pint               | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | check                    |     3.0 |         4.7 |  1.6 |    0.66 |          2 |     0.81 | False |
| altair             | fix-certain              |     6.8 |        12.9 |  1.9 |    0.72 |          2 |      0.9 | False |
| altair             | fix-likely               |    10.2 |        16.8 |  1.6 |    0.81 |          2 |      1.0 | False |
| altair             | fix-unsafe               |    10.5 |        14.2 |  1.4 |    0.91 |          2 |      0.9 | False |
| altair             | infer-basedpyright       |    24.2 |        58.5 |  2.4 |    2.71 |          3 |     3.37 | False |
| altair             | infer-ty                 |    14.0 |        21.8 |  1.6 |    1.49 |          2 |     1.85 | False |
| altair             | infer-pyrefly            |    12.4 |        23.7 |  1.9 |    1.91 |          2 |     2.05 | False |
| altair             | census                   |     1.4 |         0.9 |  0.6 |     0.1 |          2 |     0.81 | False |
| altair             | coverage                 |     1.2 |         1.8 |  1.5 |    0.27 |          2 |     0.34 | False |
| altair             | timing                   |     3.4 |         4.3 |  1.3 |    0.66 |         16 |     0.82 | False |
| altair             | traced                   |    35.5 |       187.2 |  5.3 |    5.77 |          8 |     6.72 | False |
| altair             | tests-released           |    25.4 |       156.6 |  6.2 |    4.67 |          8 |     5.97 | False |
| altair             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | infer-union              |    22.8 |        62.6 |  2.7 |    3.77 |          3 |     5.55 | False |
| altair             | tests-infer-union        |    29.6 |       164.1 |  5.5 |    4.71 |          5 |     7.77 | False |
| altair             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| altair             | types-released           |     9.4 |         6.4 |  0.7 |     0.5 |          1 |     0.52 | False |
| altair             | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| altair             | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| altair             | types-fix-unsafe         |     3.2 |         3.2 |  1.0 |    0.37 |          1 |     0.46 | False |
| altair             | types-infer-basedpyright |     4.6 |         4.6 |  1.0 |    0.38 |          1 |     0.49 | False |
| altair             | types-infer-ty           |     6.8 |         5.7 |  0.8 |    0.39 |          1 |     0.47 | False |
| altair             | types-infer-pyrefly      |     6.0 |         5.8 |  1.0 |    0.38 |          1 |     0.51 | False |
| altair             | types-infer-trace        |     7.0 |         6.1 |  0.9 |    0.38 |          1 |     0.52 | False |
| altair             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | check                    |     4.0 |         5.3 |  1.3 |     0.4 |          2 |      0.5 | False |
| seaborn            | fix-certain              |     5.0 |        10.6 |  2.1 |    0.45 |          3 |     0.56 | False |
| seaborn            | fix-likely               |     6.2 |        14.3 |  2.3 |    0.56 |          3 |     0.69 | False |
| seaborn            | fix-unsafe               |     8.0 |        13.1 |  1.6 |    0.53 |          2 |     0.56 | False |
| seaborn            | infer-basedpyright       |    39.9 |        93.6 |  2.3 |    2.99 |          3 |      3.7 | False |
| seaborn            | infer-ty                 |     9.0 |        22.0 |  2.4 |    1.23 |          3 |     1.51 | False |
| seaborn            | infer-pyrefly            |    11.0 |        21.8 |  2.0 |    1.62 |          3 |      2.0 | False |
| seaborn            | census                   |     2.0 |         0.7 |  0.3 |    0.05 |          2 |      0.5 | False |
| seaborn            | coverage                 |     0.8 |         1.3 |  1.6 |    0.18 |          2 |     0.22 | False |
| seaborn            | timing                   |     3.2 |         4.5 |  1.4 |     0.4 |         16 |      0.5 | False |
| seaborn            | traced                   |    65.9 |       514.5 |  7.8 |    4.99 |          8 |     4.64 | False |
| seaborn            | tests-released           |    69.9 |       466.8 |  6.7 |    4.87 |          8 |     4.32 | False |
| seaborn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| seaborn            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | infer-union              |    46.3 |        77.9 |  1.7 |    4.26 |          2 |     5.85 | False |
| seaborn            | tests-infer-union        |    63.7 |       512.3 |  8.0 |    4.86 |          8 |      4.4 | False |
| seaborn            | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| seaborn            | types-released           |     1.4 |         1.0 |  0.7 |    0.17 |          1 |     0.17 | False |
| seaborn            | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| seaborn            | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| seaborn            | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| seaborn            | types-infer-basedpyright |     0.8 |         0.7 |  0.9 |    0.15 |          1 |     0.19 | False |
| seaborn            | types-infer-ty           |     1.2 |         1.0 |  0.8 |    0.15 |          1 |     0.21 | False |
| seaborn            | types-infer-pyrefly      |     0.8 |         0.7 |  0.9 |    0.14 |          1 |     0.19 | False |
| seaborn            | types-infer-trace        |     1.0 |         0.6 |  0.6 |    0.15 |          1 |     0.21 | False |
| seaborn            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| aiohttp            | check                    |     1.4 |         2.4 |  1.7 |    0.23 |          2 |     0.29 | False |
| aiohttp            | fix-certain              |     2.8 |         6.9 |  2.5 |    0.36 |          3 |     0.45 | False |
| aiohttp            | fix-likely               |     4.0 |         9.3 |  2.3 |    0.41 |          3 |     0.51 | False |
| aiohttp            | fix-unsafe               |     3.2 |         6.8 |  2.1 |    0.36 |          3 |     0.46 | False |
| aiohttp            | infer-basedpyright       |    23.6 |        38.5 |  1.6 |    1.55 |          2 |     2.14 | False |
| aiohttp            | infer-ty                 |     7.0 |        13.4 |  1.9 |    0.99 |          2 |      1.3 | False |
| aiohttp            | infer-pyrefly            |     8.6 |        13.0 |  1.5 |    0.99 |          3 |     1.34 | False |
| aiohttp            | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.29 | False |
| aiohttp            | coverage                 |     0.6 |         1.1 |  1.8 |    0.18 |          2 |     0.22 | False |
| aiohttp            | timing                   |     1.8 |         2.6 |  1.4 |    0.24 |         16 |     0.29 | False |
| aiohttp            | traced                   |    94.1 |       731.5 |  7.8 |    2.95 |          1 |     4.46 | False |
| aiohttp            | tests-released           |    81.5 |       625.4 |  7.7 |    2.58 |          1 |     3.79 | False |
| aiohttp            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| aiohttp            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| aiohttp            | infer-union              |    20.4 |        50.7 |  2.5 |     3.1 |          1 |      3.9 | False |
| aiohttp            | tests-infer-union        |    73.3 |       639.4 |  8.7 |    2.57 |          1 |     3.86 | False |
| aiohttp            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     0.25 | False |
| websockets         | fix-certain              |     1.8 |         4.0 |  2.2 |    0.29 |          2 |     0.37 | False |
| websockets         | fix-likely               |     2.4 |         5.2 |  2.2 |     0.3 |          2 |      0.4 | False |
| websockets         | fix-unsafe               |     2.6 |         4.4 |  1.7 |    0.32 |          2 |     0.39 | False |
| websockets         | infer-basedpyright       |     7.2 |        20.6 |  2.9 |    0.97 |          4 |     1.41 | False |
| websockets         | infer-ty                 |     2.8 |         6.9 |  2.5 |     0.7 |          3 |     0.95 | False |
| websockets         | infer-pyrefly            |     3.2 |         7.3 |  2.3 |    0.72 |          3 |     0.84 | False |
| websockets         | census                   |     0.8 |         1.3 |  1.6 |     0.2 |          2 |     0.25 | False |
| websockets         | coverage                 |     0.8 |         1.0 |  1.2 |    0.16 |          2 |      0.2 | False |
| websockets         | timing                   |     1.2 |         1.4 |  1.2 |     0.2 |         16 |     0.25 | False |
| websockets         | traced                   |    35.5 |        13.2 |  0.4 |    0.33 |          1 |     0.42 | False |
| websockets         | tests-released           |    28.1 |         5.1 |  0.2 |    0.14 |          1 |     0.15 | False |
| websockets         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| websockets         | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| websockets         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| websockets         | infer-union              |    23.0 |        37.2 |  1.6 |    2.07 |          2 |     2.62 | False |
| websockets         | tests-infer-union        |    29.3 |         5.8 |  0.2 |    0.13 |          1 |      0.2 | False |
| websockets         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | types-released           |     1.0 |         0.7 |  0.7 |    0.12 |          1 |     0.14 | False |
| websockets         | types-fix-certain        |     1.4 |         0.8 |  0.6 |     0.1 |          1 |     0.04 | False |
| websockets         | types-fix-likely         |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.04 | False |
| websockets         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| websockets         | types-infer-basedpyright |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.12 | False |
| websockets         | types-infer-ty           |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.14 | False |
| websockets         | types-infer-pyrefly      |     1.0 |         0.8 |  0.8 |     0.1 |          1 |     0.12 | False |
| websockets         | types-infer-trace        |     1.0 |         0.8 |  0.8 |     0.1 |          1 |     0.14 | False |
| websockets         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | check                    |     0.6 |         0.1 |  0.2 |    0.03 |          2 |     0.25 | False |
| anyio              | fix-certain              |     2.2 |         4.0 |  1.8 |    0.31 |          2 |     0.35 | False |
| anyio              | fix-likely               |     2.8 |         5.5 |  2.0 |     0.3 |          3 |     0.39 | False |
| anyio              | fix-unsafe               |     2.6 |         4.6 |  1.8 |    0.31 |          2 |      0.4 | False |
| anyio              | infer-basedpyright       |    10.8 |        22.8 |  2.1 |    0.99 |          3 |      1.4 | False |
| anyio              | infer-ty                 |     3.8 |         6.9 |  1.8 |    0.78 |          2 |     0.82 | False |
| anyio              | infer-pyrefly            |     4.0 |        12.2 |  3.0 |    0.95 |          2 |     1.34 | False |
| anyio              | census                   |     1.2 |         1.6 |  1.3 |     0.2 |          2 |     0.25 | False |
| anyio              | coverage                 |     0.6 |         0.7 |  1.2 |    0.16 |          2 |     0.19 | False |
| anyio              | timing                   |     1.2 |         1.5 |  1.2 |     0.2 |         16 |     0.25 | False |
| anyio              | traced                   |   110.4 |        53.7 |  0.5 |    0.37 |          1 |     0.44 | False |
| anyio              | tests-released           |    90.2 |        41.3 |  0.5 |    0.26 |          1 |     0.31 | False |
| anyio              | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| anyio              | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| anyio              | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| anyio              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | tests-infer-pyrefly      |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.04 | False |
| anyio              | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| anyio              | infer-union              |    11.2 |        28.1 |  2.5 |    2.52 |          2 |     3.04 | False |
| anyio              | tests-infer-union        |   119.0 |        48.6 |  0.4 |    0.25 |          1 |     0.35 | False |
| anyio              | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| zarr               | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     0.39 | False |
| zarr               | fix-certain              |     3.2 |         8.9 |  2.8 |    0.42 |          3 |     0.47 | False |
| zarr               | fix-likely               |     5.0 |        12.5 |  2.5 |    0.56 |          3 |     0.66 | False |
| zarr               | fix-unsafe               |     4.2 |         8.7 |  2.1 |     0.5 |          3 |     0.54 | False |
| zarr               | infer-basedpyright       |    15.2 |        47.2 |  3.1 |    2.63 |          5 |     3.66 | False |
| zarr               | infer-ty                 |     4.8 |        15.1 |  3.1 |    1.62 |          3 |     1.91 | False |
| zarr               | infer-pyrefly            |     5.6 |        21.0 |  3.8 |    2.15 |          5 |     2.69 | False |
| zarr               | census                   |     2.8 |         4.4 |  1.6 |    0.31 |          3 |     0.39 | False |
| zarr               | coverage                 |     0.8 |         1.5 |  1.9 |    0.19 |          2 |     0.24 | False |
| zarr               | timing                   |     2.4 |         3.4 |  1.4 |    0.31 |         16 |     0.39 | False |
| zarr               | traced                   |   116.0 |       245.8 |  2.1 |    2.61 |          3 |     3.22 | False |
| zarr               | tests-released           |   128.0 |       232.2 |  1.8 |    2.35 |          4 |     2.82 | False |
| zarr               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| zarr               | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| zarr               | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| zarr               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| zarr               | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| zarr               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| zarr               | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| zarr               | infer-union              |    45.5 |        91.4 |  2.0 |    5.71 |          3 |     7.46 | False |
| zarr               | tests-infer-union        |   115.9 |       229.6 |  2.0 |    2.33 |          2 |     3.06 | False |
| zarr               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| joblib             | check                    |     2.6 |         3.1 |  1.2 |    0.31 |          2 |     0.39 | False |
| joblib             | fix-certain              |     3.8 |         7.2 |  1.9 |    0.36 |          2 |     0.45 | False |
| joblib             | fix-likely               |     6.2 |         9.8 |  1.6 |    0.39 |          2 |     0.49 | False |
| joblib             | fix-unsafe               |     4.6 |         7.9 |  1.7 |    0.36 |          2 |     0.45 | False |
| joblib             | infer-basedpyright       |    46.9 |        77.1 |  1.6 |    2.45 |          2 |     2.99 | False |
| joblib             | infer-ty                 |     5.6 |        12.8 |  2.3 |    1.12 |          3 |      1.5 | False |
| joblib             | infer-pyrefly            |     6.0 |        13.3 |  2.2 |    1.16 |          3 |     1.64 | False |
| joblib             | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          2 |     0.39 | False |
| joblib             | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          2 |     0.21 | False |
| joblib             | timing                   |     2.2 |         2.7 |  1.2 |    0.31 |         16 |     0.39 | False |
| joblib             | traced                   |   144.3 |       496.0 |  3.4 |    1.07 |          1 |     1.32 | False |
| joblib             | tests-released           |   168.7 |       501.3 |  3.0 |    1.07 |          1 |     1.29 | False |
| joblib             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| joblib             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| joblib             | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| joblib             | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| joblib             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| joblib             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| joblib             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| joblib             | infer-union              |    23.4 |        56.5 |  2.4 |     3.8 |          4 |     5.56 | False |
| joblib             | tests-infer-union        |   140.5 |       487.8 |  3.5 |    1.06 |          1 |     1.32 | False |
| joblib             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| networkx           | check                    |     7.6 |        18.9 |  2.5 |    0.97 |          2 |     1.16 | False |
| networkx           | fix-certain              |    12.6 |        37.5 |  3.0 |    1.18 |          3 |     1.41 | False |
| networkx           | fix-likely               |    18.6 |        52.3 |  2.8 |     1.8 |          3 |     2.15 | False |
| networkx           | fix-unsafe               |    16.5 |        39.0 |  2.4 |    1.24 |          3 |     1.45 | False |
| networkx           | infer-basedpyright       |    69.1 |       280.5 |  4.1 |    9.22 |          5 |    10.36 | False |
| networkx           | infer-ty                 |    23.8 |        75.4 |  3.2 |    3.63 |          4 |     3.79 | False |
| networkx           | infer-pyrefly            |    25.8 |        87.0 |  3.4 |    4.69 |          4 |     5.15 | False |
| networkx           | census                   |     4.8 |         4.5 |  0.9 |    0.11 |          2 |     1.16 | False |
| networkx           | coverage                 |     1.6 |         4.4 |  2.8 |    0.39 |          3 |     0.49 | False |
| networkx           | timing                   |    11.2 |        17.0 |  1.5 |    0.97 |         16 |     1.16 | False |
| networkx           | traced                   |    39.0 |       263.3 |  6.8 |    2.56 |          8 |     3.27 | False |
| networkx           | tests-released           |    26.8 |       229.6 |  8.6 |    2.33 |          7 |     2.92 | False |
| networkx           | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| networkx           | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| networkx           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| networkx           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| networkx           | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| networkx           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| networkx           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| networkx           | infer-union              |    74.5 |       295.3 |  4.0 |   12.31 |          4 |    18.79 | False |
| networkx           | tests-infer-union        |    36.8 |       253.5 |  6.9 |    2.27 |          7 |     2.95 | False |
| networkx           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| networkx           | types-released           |     3.8 |         2.9 |  0.8 |    0.37 |          1 |      0.4 | False |
| networkx           | types-fix-certain        |     0.6 |         0.4 |  0.7 |    0.04 |          1 |     0.05 | False |
| networkx           | types-fix-likely         |     3.8 |         3.0 |  0.8 |    0.28 |          1 |     0.36 | False |
| networkx           | types-fix-unsafe         |     0.6 |         0.4 |  0.7 |    0.04 |          1 |     0.05 | False |
| networkx           | types-infer-basedpyright |     4.0 |         3.6 |  0.9 |     0.3 |          1 |     0.39 | False |
| networkx           | types-infer-ty           |     2.6 |         2.5 |  1.0 |    0.29 |          1 |     0.35 | False |
| networkx           | types-infer-pyrefly      |     2.6 |         2.6 |  1.0 |    0.32 |          1 |     0.41 | False |
| networkx           | types-infer-trace        |     3.8 |         3.5 |  0.9 |    0.31 |          1 |     0.37 | False |
| networkx           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| nibabel            | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          3 |     0.71 | False |
| nibabel            | fix-certain              |     9.6 |        23.9 |  2.5 |    0.68 |          3 |     0.85 | False |
| nibabel            | fix-likely               |    14.8 |        34.3 |  2.3 |    0.93 |          3 |     1.16 | False |
| nibabel            | fix-unsafe               |     8.4 |        20.8 |  2.5 |    0.69 |          3 |     0.86 | False |
| nibabel            | infer-basedpyright       |    68.5 |       236.8 |  3.5 |    5.82 |          5 |     7.66 | False |
| nibabel            | infer-ty                 |    38.3 |       113.2 |  3.0 |    2.79 |          4 |     3.46 | False |
| nibabel            | infer-pyrefly            |    19.3 |        64.1 |  3.3 |    3.29 |          4 |      3.4 | False |
| nibabel            | census                   |     5.4 |        10.7 |  2.0 |    0.58 |          3 |     0.71 | False |
| nibabel            | coverage                 |     0.8 |         1.9 |  2.4 |    0.24 |          2 |      0.3 | False |
| nibabel            | timing                   |     6.6 |         9.6 |  1.5 |    0.58 |         16 |     0.72 | False |
| nibabel            | traced                   |    29.0 |       119.5 |  4.1 |    1.12 |          6 |     1.41 | False |
| nibabel            | tests-released           |    15.0 |        95.4 |  6.4 |    1.02 |          8 |     1.31 | False |
| nibabel            | tests-fix-certain        |    14.8 |        94.5 |  6.4 |    1.02 |          7 |     1.26 | False |
| nibabel            | tests-fix-likely         |    14.4 |        80.3 |  5.6 |    1.03 |          7 |     1.26 | False |
| nibabel            | tests-fix-unsafe         |    14.2 |        91.5 |  6.4 |    1.03 |          6 |     1.29 | False |
| nibabel            | tests-infer-basedpyright |    17.0 |        90.4 |  5.3 |    1.02 |          7 |     1.29 | False |
| nibabel            | tests-infer-ty           |    15.2 |        96.2 |  6.3 |    1.04 |          7 |     1.29 | False |
| nibabel            | tests-infer-pyrefly      |    15.0 |        94.6 |  6.3 |    1.01 |          6 |     1.29 | False |
| nibabel            | tests-infer-trace        |    15.4 |        94.5 |  6.1 |    1.02 |          8 |     1.25 | False |
| nibabel            | infer-union              |    68.9 |       295.5 |  4.3 |    9.47 |          3 |    12.51 | False |
| nibabel            | tests-infer-union        |    15.0 |        97.7 |  6.5 |    1.01 |          6 |      1.3 | False |
| nibabel            | tests                    |   105.6 |       610.8 |  5.8 |    1.07 |          5 |     1.31 | False |
| nibabel            | types-released           |     3.5 |         2.1 |  0.6 |    0.18 |          1 |     0.22 | False |
| nibabel            | types-fix-certain        |     2.0 |         1.8 |  0.9 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-fix-likely         |     2.4 |         2.3 |  1.0 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-fix-unsafe         |     1.4 |         1.2 |  0.9 |    0.13 |          1 |     0.16 | False |
| nibabel            | types-infer-basedpyright |     2.6 |         2.4 |  0.9 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-infer-ty           |     2.6 |         2.3 |  0.9 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-infer-pyrefly      |     2.8 |         2.3 |  0.8 |    0.16 |          1 |     0.22 | False |
| nibabel            | types-infer-trace        |     2.2 |         2.0 |  0.9 |    0.16 |          1 |     0.21 | False |
| nibabel            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| narwhals           | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          2 |      0.5 | False |
| narwhals           | fix-certain              |     4.0 |        11.5 |  2.9 |    0.41 |          3 |     0.56 | False |
| narwhals           | fix-likely               |     6.2 |        16.9 |  2.7 |    0.84 |          3 |     1.05 | False |
| narwhals           | fix-unsafe               |    10.0 |        17.9 |  1.8 |    0.84 |          3 |     0.71 | False |
| narwhals           | infer-basedpyright       |    22.8 |       100.3 |  4.4 |    3.53 |          5 |     4.59 | False |
| narwhals           | infer-ty                 |     7.6 |        27.2 |  3.6 |    2.71 |          4 |     2.42 | False |
| narwhals           | infer-pyrefly            |     9.4 |        28.3 |  3.0 |    3.15 |          4 |     3.85 | False |
| narwhals           | census                   |     4.0 |         6.2 |  1.6 |     0.4 |          2 |      0.5 | False |
| narwhals           | coverage                 |     1.0 |         2.1 |  2.1 |    0.21 |          3 |     0.26 | False |
| narwhals           | timing                   |     3.2 |         4.9 |  1.5 |     0.4 |         16 |      0.5 | False |
| narwhals           | traced                   |    31.8 |       180.3 |  5.7 |    4.86 |          8 |     6.14 | False |
| narwhals           | tests-released           |    21.4 |       147.8 |  6.9 |     4.5 |          7 |      5.8 | False |
| narwhals           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| narwhals           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| narwhals           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | infer-union              |    18.0 |        79.6 |  4.4 |    7.09 |          3 |    10.17 | False |
| narwhals           | tests-infer-union        |    32.3 |       173.0 |  5.4 |     4.8 |          5 |      6.0 | False |
| narwhals           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | types-released           |    28.0 |        55.6 |  2.0 |    1.58 |          2 |     1.94 | False |
| narwhals           | types-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     1.99 | False |
| narwhals           | types-fix-likely         |    23.6 |        44.4 |  1.9 |    1.59 |          2 |     1.95 | False |
| narwhals           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | types-infer-basedpyright |    23.2 |        49.3 |  2.1 |    1.59 |          3 |     2.17 | False |
| narwhals           | types-infer-ty           |    22.8 |        48.8 |  2.1 |     1.6 |          3 |     2.05 | False |
| narwhals           | types-infer-pyrefly      |    26.4 |        54.1 |  2.0 |    1.62 |          3 |     2.04 | False |
| narwhals           | types-infer-trace        |    28.3 |        49.3 |  1.7 |    1.65 |          3 |     1.97 | False |
| narwhals           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| xarray             | check                    |    18.8 |        34.3 |  1.8 |    0.97 |          2 |     1.21 | False |
| xarray             | fix-certain              |    35.1 |        77.9 |  2.2 |    1.42 |          3 |     1.77 | False |
| xarray             | fix-likely               |    45.7 |       103.0 |  2.3 |    1.99 |          3 |     2.47 | False |
| xarray             | fix-unsafe               |    40.5 |        84.4 |  2.1 |     1.6 |          2 |     1.91 | False |
| xarray             | infer-basedpyright       |   144.0 |       439.5 |  3.1 |   11.29 |          4 |    13.66 | False |
| xarray             | infer-ty                 |    55.3 |       148.0 |  2.7 |    4.66 |          4 |     5.74 | False |
| xarray             | infer-pyrefly            |    47.3 |       127.7 |  2.7 |    5.39 |          3 |     6.39 | False |
| xarray             | census                   |     5.8 |         5.5 |  0.9 |    0.15 |          2 |     1.21 | False |
| xarray             | coverage                 |     2.4 |         6.7 |  2.8 |    0.44 |          3 |     0.55 | False |
| xarray             | timing                   |    22.2 |        31.5 |  1.4 |    0.97 |         16 |     1.21 | False |
| xarray             | traced                   |    58.5 |       185.7 |  3.2 |    1.97 |          5 |     2.64 | False |
| xarray             | tests-released           |    24.6 |       134.4 |  5.5 |    1.94 |          5 |     2.47 | False |
| xarray             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| xarray             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | infer-union              |   137.4 |       439.1 |  3.2 |   13.62 |          3 |    20.04 | False |
| xarray             | tests-infer-union        |    26.0 |       110.0 |  4.2 |    1.95 |          7 |     2.46 | False |
| xarray             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| litestar           | check                    |     2.0 |         0.1 |  0.1 |    0.03 |          2 |     0.54 | False |
| litestar           | fix-certain              |     4.8 |        12.0 |  2.5 |    0.62 |          3 |     0.77 | False |
| litestar           | fix-likely               |    10.8 |        17.7 |  1.6 |    0.88 |          3 |     1.06 | False |
| litestar           | fix-unsafe               |     7.8 |        15.5 |  2.0 |    0.87 |          3 |     0.79 | False |
| litestar           | infer-basedpyright       |    21.9 |        83.1 |  3.8 |    3.72 |          4 |     4.64 | False |
| litestar           | infer-ty                 |     8.8 |        24.9 |  2.8 |    1.99 |          4 |     2.45 | False |
| litestar           | infer-pyrefly            |     9.0 |        28.2 |  3.1 |    2.68 |          4 |     3.39 | False |
| litestar           | census                   |     2.6 |         5.0 |  1.9 |    0.42 |          2 |     0.54 | False |
| litestar           | coverage                 |     1.0 |         1.9 |  1.9 |     0.2 |          2 |     0.24 | False |
| litestar           | timing                   |     3.2 |         4.6 |  1.4 |    0.42 |         16 |     0.52 | False |
| litestar           | traced                   |    32.8 |       161.2 |  4.9 |    4.16 |          8 |     5.42 | False |
| litestar           | tests-released           |    25.6 |       139.9 |  5.5 |    3.83 |          7 |     4.96 | False |
| litestar           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | tests-infer-basedpyright |    31.0 |       145.1 |  4.7 |    3.69 |          1 |     0.04 | False |
| litestar           | tests-infer-ty           |    24.8 |       147.6 |  6.0 |    3.74 |          1 |     0.04 | False |
| litestar           | tests-infer-pyrefly      |    36.5 |       147.0 |  4.0 |    3.86 |          1 |     0.04 | False |
| litestar           | tests-infer-trace        |    42.9 |       143.7 |  3.3 |    3.76 |          1 |     0.04 | False |
| litestar           | infer-union              |    19.0 |        82.7 |  4.4 |     5.9 |          4 |     8.32 | False |
| litestar           | tests-infer-union        |    32.4 |       138.4 |  4.3 |    3.87 |          5 |     4.94 | False |
| litestar           | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| litestar           | types-released           |    45.9 |        61.2 |  1.3 |    2.12 |          2 |     2.52 | False |
| litestar           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | types-infer-basedpyright |    36.5 |        58.6 |  1.6 |    1.89 |          2 |     2.36 | False |
| litestar           | types-infer-ty           |    40.5 |        63.9 |  1.6 |     1.9 |          2 |     2.35 | False |
| litestar           | types-infer-pyrefly      |    49.3 |        66.7 |  1.4 |    1.88 |          2 |     2.44 | False |
| litestar           | types-infer-trace        |    41.3 |        61.8 |  1.5 |    1.88 |          2 |     2.54 | False |
| litestar           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| stripe             | check                    |     4.2 |        13.2 |  3.1 |    0.81 |          3 |      1.0 | False |
| stripe             | fix-certain              |    10.8 |        33.6 |  3.1 |    0.83 |          4 |      1.2 | False |
| stripe             | fix-likely               |    13.6 |        43.5 |  3.2 |    1.14 |          4 |     1.42 | False |
| stripe             | fix-unsafe               |     9.4 |        32.6 |  3.5 |    0.83 |          4 |      1.2 | False |
| stripe             | infer-basedpyright       |  1170.3 |      3048.4 |  2.6 |    4.58 |          3 |     5.74 | False |
| stripe             | infer-ty                 |    17.4 |        57.0 |  3.3 |    2.51 |          4 |     3.12 | False |
| stripe             | infer-pyrefly            |    21.0 |        72.4 |  3.4 |    3.83 |          4 |     4.62 | False |
| stripe             | census                   |     1.4 |         1.3 |  0.9 |    0.06 |          3 |      1.0 | False |
| stripe             | coverage                 |     2.0 |         5.6 |  2.8 |    0.37 |          3 |     0.46 | False |
| stripe             | timing                   |    10.0 |        15.6 |  1.6 |    0.81 |         16 |     1.02 | False |
| celery             | check                    |     3.0 |         5.7 |  1.9 |    0.68 |          2 |     0.85 | False |
| celery             | fix-certain              |     5.6 |        12.7 |  2.3 |    0.83 |          3 |     1.04 | False |
| celery             | fix-likely               |     9.8 |        19.9 |  2.0 |    0.96 |          3 |     1.19 | False |
| celery             | fix-unsafe               |    18.6 |        22.9 |  1.2 |    1.32 |          2 |     1.04 | False |
| celery             | infer-basedpyright       |    24.3 |        63.7 |  2.6 |    3.31 |          4 |     5.02 | False |
| celery             | infer-ty                 |    10.0 |        26.2 |  2.6 |    1.85 |          3 |     2.39 | False |
| celery             | infer-pyrefly            |    10.0 |        29.2 |  2.9 |    2.62 |          4 |     2.75 | False |
| celery             | census                   |     3.4 |         0.7 |  0.2 |    0.04 |          2 |     0.85 | False |
| celery             | coverage                 |     1.0 |         1.7 |  1.7 |    0.19 |          2 |     0.24 | False |
| celery             | timing                   |     4.0 |         5.6 |  1.4 |    0.68 |         16 |     0.85 | False |
| celery             | traced                   |   167.1 |        84.0 |  0.5 |    3.07 |          1 |     5.05 | False |
| celery             | tests-released           |    61.9 |        62.1 |  1.0 |    3.35 |          2 |     4.72 | False |
| celery             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.05 | False |
| celery             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.05 | False |
| celery             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| celery             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.05 | False |
| celery             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| celery             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.05 | False |
| celery             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.05 | False |
| celery             | infer-union              |    28.0 |       109.7 |  3.9 |    6.97 |          5 |     8.81 | False |
| celery             | tests-infer-union        |    42.5 |        47.6 |  1.1 |    3.23 |          2 |     4.82 | False |
| celery             | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.05 | False |
| optuna             | check                    |     3.2 |         7.4 |  2.3 |     0.7 |          3 |     0.86 | False |
| optuna             | fix-certain              |     7.4 |        18.5 |  2.5 |    1.04 |          3 |     1.29 | False |
| optuna             | fix-likely               |    12.8 |        31.9 |  2.5 |    1.44 |          3 |      1.8 | False |
| optuna             | fix-unsafe               |    47.3 |        43.2 |  0.9 |    2.06 |          2 |     1.29 | False |
| optuna             | infer-basedpyright       |    23.0 |        92.9 |  4.0 |    4.91 |          5 |     6.41 | False |
| optuna             | infer-ty                 |    11.6 |        34.8 |  3.0 |     2.8 |          3 |      3.5 | False |
| optuna             | infer-pyrefly            |    12.6 |        42.4 |  3.4 |    3.71 |          4 |      4.6 | False |
| optuna             | census                   |     0.8 |         0.7 |  0.9 |    0.05 |          3 |     0.86 | False |
| optuna             | coverage                 |     0.8 |         1.5 |  1.9 |    0.19 |          2 |     0.24 | False |
| optuna             | timing                   |     5.2 |         7.7 |  1.5 |     0.7 |         16 |     0.86 | False |
| optuna             | traced                   |   149.8 |      1535.8 | 10.3 |    5.05 |          8 |     6.04 | False |
| optuna             | tests-released           |   124.2 |      1116.9 |  9.0 |    4.07 |          8 |     5.15 | False |
| optuna             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| optuna             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | infer-union              |    27.0 |       105.5 |  3.9 |    7.81 |          3 |    10.91 | False |
| optuna             | tests-infer-union        |   232.9 |      2497.7 | 10.7 |    3.97 |          8 |      5.5 | False |
| optuna             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | types-released           |    10.3 |         6.2 |  0.6 |     0.6 |          1 |     0.46 | False |
| optuna             | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.46 | False |
| optuna             | types-fix-likely         |     9.0 |         6.4 |  0.7 |    0.36 |          1 |     0.45 | False |
| optuna             | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| optuna             | types-infer-basedpyright |     6.2 |         5.6 |  0.9 |    0.36 |          1 |     0.54 | False |
| optuna             | types-infer-ty           |     6.0 |         5.5 |  0.9 |    0.37 |          1 |     0.51 | False |
| optuna             | types-infer-pyrefly      |     4.8 |         4.6 |  1.0 |    0.36 |          1 |     0.45 | False |
| optuna             | types-infer-trace        |     5.4 |         4.9 |  0.9 |    0.36 |          1 |     0.56 | False |
| optuna             | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | check                    |     0.6 |         0.4 |  0.7 |    0.07 |          3 |     1.61 | False |
| dask               | fix-certain              |    38.7 |        85.0 |  2.2 |    1.83 |          3 |     2.19 | False |
| dask               | fix-likely               |    93.1 |       132.4 |  1.4 |    2.52 |          2 |     3.01 | False |
| dask               | fix-unsafe               |    70.8 |       126.0 |  1.8 |    2.74 |          2 |     3.09 | False |
| dask               | infer-basedpyright       |   166.8 |       542.0 |  3.2 |   12.99 |          5 |    16.77 | False |
| dask               | infer-ty                 |    76.0 |       193.3 |  2.5 |    5.49 |          3 |     6.14 | False |
| dask               | infer-pyrefly            |    58.5 |       158.4 |  2.7 |    6.92 |          4 |     7.97 | False |
| dask               | census                   |    24.8 |        44.1 |  1.8 |    1.34 |          3 |     1.61 | False |
| dask               | coverage                 |     2.2 |         6.5 |  3.0 |    0.45 |          3 |     0.56 | False |
| dask               | timing                   |    29.0 |        40.9 |  1.4 |    1.34 |         16 |     1.62 | False |
| dask               | traced                   |   186.3 |      1193.0 |  6.4 |    4.68 |          8 |     5.94 | False |
| dask               | tests-released           |   126.6 |      1066.3 |  8.4 |    4.57 |          8 |     5.55 | False |
| dask               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| dask               | infer-union              |   129.4 |       483.0 |  3.7 |   16.67 |          4 |    22.76 | False |
| dask               | tests-infer-union        |   136.2 |      1112.3 |  8.2 |    4.58 |          8 |     5.87 | False |
| dask               | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mypy               | check                    |     6.4 |        12.3 |  1.9 |    0.57 |          2 |     0.67 | False |
| mypy               | fix-certain              |    11.8 |        37.8 |  3.2 |    0.99 |          4 |     1.24 | False |
| mypy               | fix-likely               |    12.2 |        38.4 |  3.1 |    1.06 |          4 |     1.32 | False |
| mypy               | fix-unsafe               |    14.0 |        39.7 |  2.8 |    0.99 |          3 |     1.24 | False |
| mypy               | infer-basedpyright       |    31.1 |       119.9 |  3.9 |    5.04 |          5 |     6.09 | False |
| mypy               | infer-ty                 |    14.6 |        49.1 |  3.4 |    2.85 |          4 |     3.35 | False |
| mypy               | infer-pyrefly            |    13.6 |        46.3 |  3.4 |    3.09 |          3 |     3.72 | False |
| mypy               | census                   |     6.2 |         4.0 |  0.6 |    0.09 |          2 |     0.67 | False |
| mypy               | coverage                 |     2.2 |         5.5 |  2.5 |    0.36 |          3 |     0.45 | False |
| mypy               | timing                   |     7.2 |        11.0 |  1.5 |    0.55 |         16 |     0.69 | False |
| mypy               | traced                   |   357.7 |      2156.3 |  6.0 |    6.39 |          8 |      8.2 | False |
| mypy               | tests-released           |   327.1 |      2033.9 |  6.2 |    5.75 |          8 |     8.25 | False |
| mypy               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | infer-union              |    28.2 |       119.4 |  4.2 |    7.49 |          5 |    11.56 | False |
| mypy               | tests-infer-union        |   337.2 |      1866.2 |  5.5 |    5.92 |          7 |     7.41 | False |
| mypy               | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mypy               | types-released           |    13.0 |        28.3 |  2.2 |    0.61 |          3 |     0.77 | False |
| mypy               | types-fix-certain        |     7.2 |        19.1 |  2.7 |    0.49 |          2 |     0.61 | False |
| mypy               | types-fix-likely         |     7.8 |        20.2 |  2.6 |    0.48 |          2 |      0.6 | False |
| mypy               | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          1 |     0.05 | False |
| mypy               | types-infer-basedpyright |     8.0 |        19.8 |  2.5 |    0.49 |          3 |     0.61 | False |
| mypy               | types-infer-ty           |    11.0 |        26.5 |  2.4 |     0.6 |          3 |     0.77 | False |
| mypy               | types-infer-pyrefly      |     7.8 |        19.5 |  2.5 |    0.47 |          3 |      0.6 | False |
| mypy               | types-infer-trace        |     9.6 |        21.7 |  2.3 |    0.61 |          2 |     0.77 | False |
| mypy               | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |

- nibabel, 0.4.0-rc.3+dev, tests: the tests differ after fix-certain: 1 new
- dask, 0.4.0-rc.3+dev, fix-certain: a second pass would still fix 3
- dask, 0.4.0-rc.3+dev, fix-unsafe: a second pass would still fix 3
- standard library, 0.4.0-rc.3+dev, infer-basedpyright: held 13.33 GB beside other steps
- standard library, 0.4.0-rc.3+dev, infer-ty: held 14.93 GB beside other steps
- standard library, 0.4.0-rc.3+dev, infer-pyrefly: held 19.0 GB beside other steps
- django, 0.4.0-rc.3+dev, infer-union: held 12.51 GB beside other steps
- sqlalchemy, 0.4.0-rc.3+dev, infer-union: held 10.92 GB beside other steps
- pandas, 0.4.0-rc.3+dev, infer-basedpyright: held 15.75 GB beside other steps
- pandas, 0.4.0-rc.3+dev, infer-ty: held 13.9 GB beside other steps
- pandas, 0.4.0-rc.3+dev, infer-pyrefly: held 20.73 GB beside other steps
- pandas, 0.4.0-rc.3+dev, traced: held 14.07 GB beside other steps
- pandas, 0.4.0-rc.3+dev, tests-released: held 13.34 GB beside other steps
- pandas, 0.4.0-rc.3+dev, infer-union: held 29.88 GB beside other steps
- pandas, 0.4.0-rc.3+dev, tests-infer-union: held 12.95 GB beside other steps
- twisted, 0.4.0-rc.3+dev, infer-basedpyright: held 9.52 GB beside other steps
- networkx, 0.4.0-rc.3+dev, infer-basedpyright: held 9.22 GB beside other steps
- networkx, 0.4.0-rc.3+dev, infer-union: held 12.31 GB beside other steps
- nibabel, 0.4.0-rc.3+dev, infer-union: held 9.47 GB beside other steps
- xarray, 0.4.0-rc.3+dev, infer-basedpyright: held 11.29 GB beside other steps
- xarray, 0.4.0-rc.3+dev, infer-union: held 13.62 GB beside other steps
- dask, 0.4.0-rc.3+dev, infer-basedpyright: held 12.99 GB beside other steps
- dask, 0.4.0-rc.3+dev, infer-union: held 16.67 GB beside other steps

## Basic corpora

The run `0.3.8-rc.1` (`python -m tests.corpus`) on original: constricter 0.3.8 (`4a20971934b8`),
Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own, started once the
CPUs it's expected to keep busy and the memory it's expected to hold are free. The run took 58
minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter    | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | -------------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14.7  | 0.3.8-rc.1+dev | 1,867 |          88,565 |        12,334 |         12,772 |         57 |         14 |         8 |        0 | 113,750 |
| django           | 5.2.18  | 0.3.8-rc.1+dev |   883 |           9,926 |         2,166 |          5,084 |          0 |          0 |         1 |        0 |  17,177 |
| sqlalchemy       | 2.1.4   | 0.3.8-rc.1+dev |   258 |           8,825 |         1,636 |          2,501 |        572 |        128 |         2 |        1 |  13,665 |
| pydantic         | 2.14.0  | 0.3.8-rc.1+dev |   105 |           2,072 |           440 |            605 |        184 |         15 |         0 |        0 |   3,316 |
| pandas           | 3.0.6   | 0.3.8-rc.1+dev | 1,420 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | 0.3.8-rc.1+dev |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.3.8-rc.1+dev |   366 |           5,902 |         1,150 |          1,872 |          0 |          0 |         0 |        0 |   8,924 |
| **Total**        |         | 0.3.8-rc.1+dev | 5,718 | 201,967 (79.9%) | 21,853 (8.6%) | 27,697 (11.0%) | 947 (0.4%) | 159 (0.1%) | 12 (0.0%) | 2 (0.0%) | 252,637 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus           | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ---------------- | -------------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library | 0.3.8-rc.1+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,322 (32.8%) |   6,421 (5.6%) | 12,352 (10.9%) |      0 |    0 |            0 |
| django           | 0.3.8-rc.1+dev |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |  2,614 (15.2%) |     631 (3.7%) |  2,702 (15.7%) |      0 |    0 |            0 |
| sqlalchemy       | 0.3.8-rc.1+dev |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |  1,880 (13.8%) |     341 (2.5%) |     838 (6.1%) |      0 |    0 |            0 |
| pydantic         | 0.3.8-rc.1+dev |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |  1,179 (35.6%) |     146 (4.4%) |    408 (12.3%) |      0 |    0 |            0 |
| pandas           | 0.3.8-rc.1+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,910 (21.7%) | 23,812 (30.6%) | 24,643 (31.6%) |      0 |    0 |            0 |
| twisted          | 0.3.8-rc.1+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,433 (13.6%) |  3,656 (20.5%) |  4,676 (26.2%) |      0 |    0 |            0 |
| pip              | 0.3.8-rc.1+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,250 (25.2%) |     424 (4.8%) |  1,133 (12.7%) |      0 |    0 |            0 |
| **Total**        | 0.3.8-rc.1+dev | 0 / 251,529 | 229,664 / 22,973 | 251,529 / 1,108 | 252,637 / 0 | 64,588 (25.6%) | 35,431 (14.0%) | 46,752 (18.5%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus           | constricter    | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | -------------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.3.8-rc.1+dev |              1.2% |         33.6% |            39.2% |                  44.4% | +32.5 pts, 32.8% of untyped | +43.2 pts, 43.7% of untyped |
| django           | 0.3.8-rc.1+dev |              0.0% |         15.2% |            18.9% |                  31.0% | +15.2 pts, 15.2% of untyped | +30.9 pts, 31.0% of untyped |
| sqlalchemy       | 0.3.8-rc.1+dev |             15.3% |         27.5% |            29.8% |                  33.0% | +12.3 pts, 14.5% of untyped | +17.8 pts, 21.0% of untyped |
| pydantic         | 0.3.8-rc.1+dev |             22.4% |         51.8% |            55.4% |                  61.9% | +29.3 pts, 37.8% of untyped | +39.5 pts, 50.9% of untyped |
| pandas           | 0.3.8-rc.1+dev |              1.6% |         23.0% |            53.1% |                  54.2% | +21.4 pts, 21.7% of untyped | +52.6 pts, 53.4% of untyped |
| twisted          | 0.3.8-rc.1+dev |              0.0% |         13.6% |            34.1% |                  39.8% | +13.6 pts, 13.6% of untyped | +39.8 pts, 39.8% of untyped |
| pip              | 0.3.8-rc.1+dev |              1.5% |         26.3% |            31.0% |                  38.8% | +24.8 pts, 25.2% of untyped | +37.3 pts, 37.9% of untyped |
| **Total**        | 0.3.8-rc.1+dev |              2.3% |         27.4% |            41.2% |                  45.6% | +25.1 pts, 25.7% of untyped | +43.2 pts, 44.3% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus           | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ---------------- | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library | certain            | 37,322 |  37,322 |        |        |      0 |    0 | 38,651 |  115,001 |    58.8 |
| standard library | likely             | 43,743 |  37,532 |  6,211 |        |      0 |    0 | 45,072 |  115,001 |    96.7 |
| standard library | unsafe             | 49,674 |  37,330 |  6,203 |  6,141 |      0 |    0 | 51,003 |  115,001 |    66.6 |
| standard library | infer-basedpyright | 58,062 |  37,341 |  6,713 | 14,008 |      0 |    9 | 59,391 |  115,001 |   716.4 |
| standard library | infer-ty           | 55,809 |  37,345 |  6,678 | 11,786 |      0 |   38 | 57,138 |  115,001 |    72.9 |
| standard library | infer-pyrefly      | 58,427 |  37,341 |  6,845 | 14,241 |      0 |   35 | 59,756 |  115,001 |   120.1 |
| django           | certain            |  2,614 |   2,614 |        |        |      0 |    0 |  2,619 |   17,181 |    12.0 |
| django           | likely             |  3,245 |   2,618 |    627 |        |      0 |    0 |  3,250 |   17,181 |    13.5 |
| django           | unsafe             |  5,316 |   2,614 |    626 |  2,076 |      0 |    0 |  5,321 |   17,181 |     9.9 |
| django           | infer-basedpyright |  5,777 |   2,613 |    644 |  2,520 |      0 |    4 |  5,782 |   17,181 |    47.9 |
| django           | infer-ty           |  5,550 |   2,615 |    635 |  2,300 |      0 |    0 |  5,555 |   17,181 |    20.8 |
| django           | infer-pyrefly      |  6,037 |   2,605 |    651 |  2,781 |      0 |   36 |  6,042 |   17,181 |    22.5 |
| django           | infer-trace        |  5,861 |   2,618 |    659 |  2,584 |      0 |    0 |  5,866 |   17,181 |     9.9 |
| sqlalchemy       | certain            |  1,880 |   1,880 |        |        |      0 |    0 |  4,215 |   15,304 |     9.3 |
| sqlalchemy       | likely             |  2,221 |   1,887 |    334 |        |      0 |    0 |  4,556 |   15,304 |    15.3 |
| sqlalchemy       | unsafe             |  2,718 |   1,880 |    334 |    504 |      0 |    0 |  5,053 |   15,304 |     9.6 |
| sqlalchemy       | infer-basedpyright |  3,540 |   1,875 |    371 |  1,294 |      0 |    0 |  5,875 |   15,304 |    59.7 |
| sqlalchemy       | infer-ty           |  3,476 |   1,875 |    360 |  1,241 |      0 |    0 |  5,811 |   15,304 |    23.3 |
| sqlalchemy       | infer-pyrefly      |  3,212 |   1,874 |    351 |    987 |      0 |    0 |  5,547 |   15,304 |    17.4 |
| sqlalchemy       | infer-trace        |  2,886 |   1,880 |    334 |    672 |      0 |    0 |  5,221 |   15,304 |    11.4 |
| pydantic         | certain            |  1,179 |   1,179 |        |        |      0 |    0 |  2,081 |    4,019 |     2.1 |
| pydantic         | likely             |  1,325 |   1,187 |    138 |        |      0 |    0 |  2,227 |    4,019 |     3.2 |
| pydantic         | unsafe             |  1,587 |   1,179 |    137 |    271 |      0 |    0 |  2,489 |    4,019 |     7.8 |
| pydantic         | infer-basedpyright |  1,816 |   1,180 |    141 |    495 |      0 |    0 |  2,718 |    4,019 |    36.7 |
| pydantic         | infer-ty           |  1,728 |   1,179 |    136 |    413 |      0 |    0 |  2,630 |    4,019 |     4.0 |
| pydantic         | infer-pyrefly      |  1,789 |   1,179 |    137 |    473 |      0 |    0 |  2,691 |    4,019 |     9.0 |
| pydantic         | infer-trace        |  1,588 |   1,179 |    137 |    272 |      0 |    0 |  2,490 |    4,019 |     4.2 |
| pandas           | certain            | 16,910 |  16,910 |        |        |      0 |    0 | 18,179 |   79,062 |    50.9 |
| pandas           | likely             | 40,722 |  17,093 | 23,629 |        |      0 |    0 | 41,991 |   79,062 |    94.1 |
| pandas           | unsafe             | 41,553 |  16,906 | 23,410 |  1,237 |      0 |    0 | 42,822 |   79,062 |    52.3 |
| pandas           | infer-basedpyright | 47,291 |  16,898 | 23,431 |  6,962 |      0 |   25 | 48,560 |   79,062 |   429.8 |
| pandas           | infer-ty           | 47,043 |  16,906 | 23,460 |  6,677 |      0 |    5 | 48,312 |   79,062 |   175.0 |
| pandas           | infer-pyrefly      | 48,300 |  16,909 | 23,473 |  7,918 |      0 |    9 | 49,569 |   79,062 |   195.4 |
| pandas           | infer-trace        | 42,948 |  16,906 | 23,371 |  2,671 |      0 |    9 | 44,217 |   79,062 |    40.8 |
| twisted          | certain            |  2,433 |   2,433 |        |        |      0 |    0 |  2,433 |   17,874 |     5.8 |
| twisted          | likely             |  6,089 |   2,556 |  3,533 |        |      0 |    0 |  6,089 |   17,874 |    10.5 |
| twisted          | unsafe             |  7,109 |   2,432 |  3,533 |  1,144 |      0 |    0 |  7,109 |   17,874 |     7.3 |
| twisted          | infer-basedpyright |  8,551 |   2,437 |  3,563 |  2,551 |      0 |    2 |  8,551 |   17,874 |    62.3 |
| twisted          | infer-ty           |  7,541 |   2,432 |  3,576 |  1,533 |      0 |    0 |  7,541 |   17,874 |    15.8 |
| twisted          | infer-pyrefly      |  7,564 |   2,432 |  3,566 |  1,566 |      0 |    0 |  7,564 |   17,874 |    17.3 |
| pip              | certain            |  2,250 |   2,250 |        |        |      0 |    0 |  2,387 |    9,064 |     6.2 |
| pip              | likely             |  2,674 |   2,263 |    411 |        |      0 |    0 |  2,811 |    9,064 |     9.8 |
| pip              | unsafe             |  3,383 |   2,250 |    411 |    722 |      0 |    0 |  3,520 |    9,064 |     5.2 |
| pip              | infer-basedpyright |  4,178 |   2,255 |    465 |  1,458 |      0 |    7 |  4,315 |    9,064 |    28.1 |
| pip              | infer-ty           |  3,714 |   2,252 |    435 |  1,027 |      0 |    2 |  3,851 |    9,064 |    13.3 |
| pip              | infer-pyrefly      |  3,933 |   2,252 |    449 |  1,232 |      0 |    0 |  4,070 |    9,064 |    14.2 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 16,729 |  16,729 |        |        |
| certain            | stdlib                 | 13,248 |  13,248 |        |        |
| certain            | call                   |  5,105 |   5,105 |        |        |
| certain            | container+literal      |  3,917 |   3,917 |        |        |
| certain            | builtin                |  2,518 |   2,518 |        |        |
| certain            | loop                   |  2,442 |   2,442 |        |        |
| certain            | container+literal+loop |  1,581 |   1,581 |        |        |
| certain            | copy+loop              |  1,544 |   1,544 |        |        |
| certain            | method                 |  1,221 |   1,221 |        |        |
| certain            | open                   |  1,101 |   1,101 |        |        |
| certain            | literal+method         |    945 |     945 |        |        |
| certain            | returned               |    856 |     856 |        |        |
| likely             | constructor            | 27,110 |     235 | 26,875 |        |
| likely             | literal                | 16,730 |  16,730 |        |        |
| likely             | stdlib                 | 13,304 |  13,304 |        |        |
| likely             | call                   |  5,560 |   5,117 |    443 |        |
| likely             | container+literal      |  3,917 |   3,917 |        |        |
| likely             | builtin                |  2,518 |   2,518 |        |        |
| likely             | loop                   |  2,442 |   2,442 |        |        |
| likely             | method                 |  2,222 |   1,243 |    979 |        |
| likely             | copy+loop              |  1,805 |   1,552 |    253 |        |
| likely             | container+literal+loop |  1,581 |   1,581 |        |        |
| likely             | open                   |  1,101 |   1,101 |        |        |
| likely             | returned               |  1,073 |   1,073 |        |        |
| unsafe             | constructor            | 27,109 |     235 | 26,874 |        |
| unsafe             | literal                | 16,732 |  16,729 |        |      3 |
| unsafe             | stdlib                 | 13,554 |  13,250 |        |    304 |
| unsafe             | call                   |  5,523 |   5,105 |    418 |        |
| unsafe             | container+literal      |  3,917 |   3,917 |        |        |
| unsafe             | literal+member         |  3,689 |         |        |  3,689 |
| unsafe             | returned               |  3,269 |     858 |        |  2,411 |
| unsafe             | builtin                |  2,518 |   2,518 |        |        |
| unsafe             | loop                   |  2,442 |   2,442 |        |        |
| unsafe             | method                 |  2,161 |   1,221 |    940 |        |
| unsafe             | copy+loop              |  1,790 |   1,544 |    246 |        |
| unsafe             | container+literal+loop |  1,581 |   1,581 |        |        |
| infer-basedpyright | constructor            | 27,063 |     234 | 26,829 |        |
| infer-basedpyright | literal                | 16,733 |  16,730 |        |      3 |
| infer-basedpyright | checker                | 15,206 |         |        | 15,206 |
| infer-basedpyright | stdlib                 | 13,608 |  13,147 |        |    461 |
| infer-basedpyright | call                   |  5,619 |   5,103 |    516 |        |
| infer-basedpyright | container+literal      |  3,918 |   3,918 |        |        |
| infer-basedpyright | literal+member         |  3,688 |         |        |  3,688 |
| infer-basedpyright | returned               |  3,555 |     844 |        |  2,711 |
| infer-basedpyright | builtin                |  2,518 |   2,518 |        |        |
| infer-basedpyright | loop                   |  2,442 |   2,442 |        |        |
| infer-basedpyright | method                 |  2,291 |   1,220 |  1,071 |        |
| infer-basedpyright | copy+loop              |  2,139 |   1,547 |    592 |        |
| infer-ty           | constructor            | 27,063 |     235 | 26,828 |        |
| infer-ty           | literal                | 16,732 |  16,729 |        |      3 |
| infer-ty           | stdlib                 | 13,622 |  13,165 |        |    457 |
| infer-ty           | checker                | 11,315 |         |        | 11,315 |
| infer-ty           | call                   |  5,597 |   5,103 |    494 |        |
| infer-ty           | container+literal      |  3,920 |   3,920 |        |        |
| infer-ty           | literal+member         |  3,689 |         |        |  3,689 |
| infer-ty           | returned               |  3,496 |     858 |        |  2,638 |
| infer-ty           | builtin                |  2,518 |   2,518 |        |        |
| infer-ty           | loop                   |  2,442 |   2,442 |        |        |
| infer-ty           | method                 |  2,263 |   1,220 |  1,043 |        |
| infer-ty           | copy+loop              |  2,038 |   1,546 |    492 |        |
| infer-pyrefly      | constructor            | 27,048 |     234 | 26,814 |        |
| infer-pyrefly      | literal                | 16,732 |  16,729 |        |      3 |
| infer-pyrefly      | checker                | 15,292 |         |        | 15,292 |
| infer-pyrefly      | stdlib                 | 13,680 |  13,210 |        |    470 |
| infer-pyrefly      | call                   |  5,595 |   5,103 |    492 |        |
| infer-pyrefly      | container+literal      |  3,918 |   3,918 |        |        |
| infer-pyrefly      | literal+member         |  3,688 |         |        |  3,688 |
| infer-pyrefly      | returned               |  3,484 |     858 |        |  2,626 |
| infer-pyrefly      | builtin                |  2,518 |   2,518 |        |        |
| infer-pyrefly      | loop                   |  2,442 |   2,442 |        |        |
| infer-pyrefly      | method                 |  2,280 |   1,220 |  1,060 |        |
| infer-pyrefly      | copy+loop              |  2,097 |   1,546 |    551 |        |
| infer-trace        | constructor            | 19,787 |       3 | 19,784 |        |
| infer-trace        | literal                |  6,887 |   6,887 |        |        |
| infer-trace        | call                   |  5,159 |   4,740 |    419 |        |
| infer-trace        | traced                 |  2,004 |         |        |  2,004 |
| infer-trace        | literal+member         |  1,949 |         |        |  1,949 |
| infer-trace        | method                 |  1,763 |     840 |    923 |        |
| infer-trace        | container+literal      |  1,560 |   1,560 |        |        |
| infer-trace        | stdlib                 |  1,170 |   1,136 |        |     34 |
| infer-trace        | builtin                |    835 |     835 |        |        |
| infer-trace        | loop                   |    587 |     587 |        |        |
| infer-trace        | returned               |    583 |     224 |        |    359 |
| infer-trace        | copy+loop              |    470 |     375 |     95 |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus           | untyped | guessed | unfixed | unparsed |
| ---------------- | ------: | ------: | ------: | -------: |
| standard library | 113,671 |  12,345 |  64,004 |        0 |
| django           |  17,176 |   2,702 |  11,860 |        0 |
| sqlalchemy       |  12,962 |     838 |  10,244 |        0 |
| pydantic         |   3,117 |     408 |   1,530 |        0 |
| pandas           |  77,793 |  24,642 |  36,241 |        0 |
| twisted          |  17,874 |   4,676 |  10,765 |        0 |
| pip              |   8,924 |   1,133 |   5,541 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus           | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ---------------- | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library |    4 |       45.81 |     19.73 |    1 |                       630.2 |     656.1 | hyperfine |
| django           |    4 |         8.5 |      3.61 |    1 |                       117.5 |     125.5 | hyperfine |
| sqlalchemy       |    4 |        7.44 |      3.45 |    1 |                        96.7 |     101.7 | hyperfine |
| pydantic         |    4 |        1.52 |      0.71 |    1 |                        22.0 |      24.1 | hyperfine |
| pandas           |    4 |       54.66 |     17.67 |    1 |                       773.6 |     790.1 | hyperfine |
| twisted          |    4 |        6.23 |       2.6 |    1 |                        90.6 |      96.9 | hyperfine |
| pip              |    4 |        4.29 |      1.72 |    1 |                        65.1 |      69.2 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus     | tier    |   told |   held | differed | resting on the trace |                                                                             tests | seconds | untraced |
| ---------- | ------- | -----: | -----: | -------: | -------------------: | --------------------------------------------------------------------------------: | ------: | -------: |
| django     |         |        |        |          |                  466 | Ran 18191 tests: FAILED (failures=5, errors=4, skipped=1313, expected failures=5) |   604.8 |     63.9 |
| django     | certain |    926 |    925 |        1 |                      |                                                                                   |         |          |
| django     | likely  |    301 |    300 |        1 |                      |                                                                                   |         |          |
| django     | guess   |    306 |    290 |       16 |                      |                                                                                   |         |          |
| sqlalchemy |         |        |        |          |                  166 |                                    2 failed, 29523 passed, 971 skipped, 1 warning |    98.5 |    126.0 |
| sqlalchemy | certain |  1,098 |  1,081 |       17 |                      |                                                                                   |         |          |
| sqlalchemy | likely  |    176 |    173 |        3 |                      |                                                                                   |         |          |
| sqlalchemy | guess   |    118 |    116 |        2 |                      |                                                                                   |         |          |
| pydantic   |         |        |        |          |                    1 |                                              6965 passed, 350 skipped, 29 xfailed |    59.8 |     52.8 |
| pydantic   | certain |    518 |    513 |        5 |                      |                                                                                   |         |          |
| pydantic   | likely  |     47 |     47 |        0 |                      |                                                                                   |         |          |
| pydantic   | guess   |     32 |     32 |        0 |                      |                                                                                   |         |          |
| pandas     |         |        |        |          |                1,418 |                             165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   122.3 |    118.9 |
| pandas     | certain | 12,851 | 12,774 |       77 |                      |                                                                                   |         |          |
| pandas     | likely  | 20,116 | 20,058 |       58 |                      |                                                                                   |         |          |
| pandas     | guess   |    838 |    790 |       48 |                      |                                                                                   |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus     | run                | same as released | summary                                                    | new failures | gone | named |
| ---------- | ------------------ | ---------------- | ---------------------------------------------------------- | -----------: | ---: | ----: |
| django     | released           |                  | 5 expected failures, 1 failures, 18,191 ran, 1,313 skipped |              |      |       |
| django     | fix-certain        | False            | 5 expected failures, 2 failures, 17,585 ran, 1,129 skipped |            1 |    1 |     0 |
| django     | fix-likely         | True             | 5 expected failures, 2 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | fix-unsafe         | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-basedpyright | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-pyrefly      | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-trace        | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-ty           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped |            0 |    0 |     0 |
| sqlalchemy | released           |                  | 29,523 passed, 973 skipped                                 |              |      |       |
| sqlalchemy | fix-certain        | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | fix-likely         | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | fix-unsafe         | True             | 29,521 passed, 975 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-basedpyright | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-pyrefly      | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-trace        | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-ty           | True             | 29,523 passed, 973 skipped                                 |            0 |    0 |     0 |
| pydantic   | released           |                  | 6,965 passed, 350 skipped, 29 xfailed                      |              |      |       |
| pydantic   | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pydantic   | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pydantic   | fix-unsafe         | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-basedpyright | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-pyrefly      | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-trace        | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-ty           | True             | 6,965 passed, 350 skipped, 29 xfailed                      |            0 |    0 |     0 |
| pandas     | released           |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |              |      |       |
| pandas     | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pandas     | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pandas     | fix-unsafe         | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-basedpyright | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-pyrefly      | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-trace        | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |
| pandas     | infer-ty           | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed    |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus     | run                | errors | new | gone |                                                      change |
| ---------- | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy | released           |      0 |     |      |                                                             |
| sqlalchemy | fix-certain        |      0 |   0 |    0 |    175 files changed, 1954 insertions(+), 1534 deletions(-) |
| sqlalchemy | fix-likely         |      0 |   0 |    0 |    185 files changed, 2299 insertions(+), 1855 deletions(-) |
| sqlalchemy | fix-unsafe         |      0 |   0 |    0 |    198 files changed, 2805 insertions(+), 2319 deletions(-) |
| sqlalchemy | infer-basedpyright |      6 |   6 |    0 |    204 files changed, 3650 insertions(+), 3112 deletions(-) |
| sqlalchemy | infer-pyrefly      |     15 |  15 |    0 |    203 files changed, 3317 insertions(+), 2669 deletions(-) |
| sqlalchemy | infer-trace        |      6 |   6 |    0 |    200 files changed, 3009 insertions(+), 2473 deletions(-) |
| sqlalchemy | infer-ty           |      4 |   4 |    0 |    205 files changed, 3594 insertions(+), 2949 deletions(-) |
| pydantic   | released           |      0 |     |      |                                                             |
| pydantic   | fix-certain        |      0 |   0 |    0 |      76 files changed, 1237 insertions(+), 889 deletions(-) |
| pydantic   | fix-likely         |      0 |   0 |    0 |     78 files changed, 1390 insertions(+), 1020 deletions(-) |
| pydantic   | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1664 insertions(+), 1263 deletions(-) |
| pydantic   | infer-basedpyright |      3 |   3 |    0 |     79 files changed, 1905 insertions(+), 1490 deletions(-) |
| pydantic   | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1931 insertions(+), 1404 deletions(-) |
| pydantic   | infer-trace        |      0 |   0 |    0 |     79 files changed, 1665 insertions(+), 1264 deletions(-) |
| pydantic   | infer-ty           |      3 |   3 |    0 |     79 files changed, 1808 insertions(+), 1397 deletions(-) |
| pandas     | released           |    259 |     |      |                                                             |
| pandas     | fix-certain        |    259 |   0 |    0 | 1067 files changed, 18205 insertions(+), 15186 deletions(-) |
| pandas     | fix-likely         |    259 |   0 |    0 | 1199 files changed, 42285 insertions(+), 38650 deletions(-) |
| pandas     | fix-unsafe         |    260 |   1 |    0 | 1202 files changed, 43158 insertions(+), 39403 deletions(-) |
| pandas     | infer-basedpyright |    312 |  53 |    0 | 1213 files changed, 49415 insertions(+), 45029 deletions(-) |
| pandas     | infer-pyrefly      |    377 | 118 |    0 | 1209 files changed, 50335 insertions(+), 45703 deletions(-) |
| pandas     | infer-trace        |    261 |   2 |    0 | 1205 files changed, 44603 insertions(+), 40766 deletions(-) |
| pandas     | infer-ty           |    308 |  49 |    0 | 1214 files changed, 48953 insertions(+), 44609 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus           | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ---------------- | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library | check                    |    48.9 |        98.1 |  2.0 |    3.84 |          3 |     4.76 | False |
| standard library | fix-certain              |   121.5 |       267.5 |  2.2 |    5.19 |          3 |     6.44 | False |
| standard library | fix-likely               |   146.8 |       335.6 |  2.3 |    7.84 |          3 |      9.8 | False |
| standard library | fix-unsafe               |   121.9 |       279.2 |  2.3 |    5.89 |          3 |     7.35 | False |
| standard library | infer-basedpyright       |   869.8 |      1406.3 |  1.6 |   12.53 |          2 |     16.1 | False |
| standard library | infer-ty                 |   119.5 |       404.7 |  3.4 |   15.27 |          4 |    19.91 | False |
| standard library | infer-pyrefly            |   177.6 |       524.6 |  3.0 |   19.05 |          4 |     23.7 | False |
| standard library | census                   |    38.7 |        34.7 |  0.9 |    0.51 |          3 |     4.76 | False |
| standard library | coverage                 |     9.2 |        30.7 |  3.3 |    1.63 |          4 |     2.04 | False |
| standard library | timing                   |   128.1 |       195.0 |  1.5 |    3.78 |         16 |     4.71 | False |
| django           | check                    |     2.4 |         0.4 |  0.2 |    0.06 |          2 |     1.06 | False |
| django           | fix-certain              |    23.4 |        52.9 |  2.3 |    1.12 |          2 |     1.39 | False |
| django           | fix-likely               |    21.2 |        54.4 |  2.6 |    1.52 |          2 |     1.88 | False |
| django           | fix-unsafe               |    17.6 |        46.0 |  2.6 |    1.27 |          2 |     1.59 | False |
| django           | infer-basedpyright       |    66.3 |       296.9 |  4.5 |     7.8 |          5 |    10.01 | False |
| django           | infer-ty                 |    31.7 |        92.6 |  2.9 |    3.47 |          2 |     4.47 | False |
| django           | infer-pyrefly            |    33.1 |       101.4 |  3.1 |    4.17 |          3 |     4.99 | False |
| django           | census                   |    12.2 |        23.8 |  2.0 |    0.87 |          2 |     1.06 | False |
| django           | coverage                 |     2.0 |         5.1 |  2.5 |    0.34 |          3 |     0.44 | False |
| django           | timing                   |    24.4 |        37.2 |  1.5 |    0.85 |         16 |     1.06 | False |
| django           | traced                   |   620.8 |       499.6 |  0.8 |    1.35 |          1 |     1.61 | False |
| django           | tests-released           |    64.5 |       473.8 |  7.3 |    6.02 |          8 |      8.5 | False |
| django           | tests-fix-certain        |   112.3 |       500.2 |  4.5 |    5.39 |          1 |     0.04 | False |
| django           | tests-fix-likely         |    77.9 |       487.1 |  6.3 |    5.32 |          1 |     0.04 | False |
| django           | tests-fix-unsafe         |    85.3 |       459.1 |  5.4 |     3.8 |          8 |      4.2 | False |
| django           | tests-infer-basedpyright |    47.8 |       446.5 |  9.3 |    5.71 |          8 |     8.87 | False |
| django           | tests-infer-ty           |    59.9 |       456.3 |  7.6 |    4.86 |         12 |     6.18 | False |
| django           | tests-infer-pyrefly      |    67.1 |       482.5 |  7.2 |    5.43 |         10 |     6.79 | False |
| django           | tests-infer-trace        |    85.9 |       481.9 |  5.6 |    4.46 |          9 |     4.95 | False |
| django           | tests                    |   582.0 |      3775.6 |  6.5 |    5.67 |          1 |     0.04 | False |
| sqlalchemy       | check                    |     7.4 |        14.7 |  2.0 |    0.85 |          2 |     1.06 | False |
| sqlalchemy       | fix-certain              |    19.0 |        40.0 |  2.1 |    0.95 |          3 |     1.21 | False |
| sqlalchemy       | fix-likely               |    29.8 |        51.0 |  1.7 |    1.35 |          3 |     1.69 | False |
| sqlalchemy       | fix-unsafe               |    20.6 |        42.0 |  2.0 |     1.0 |          2 |     1.25 | False |
| sqlalchemy       | infer-basedpyright       |    84.8 |       326.9 |  3.9 |    7.55 |          4 |     9.24 | False |
| sqlalchemy       | infer-ty                 |    36.7 |        98.9 |  2.7 |    3.73 |          3 |     4.17 | False |
| sqlalchemy       | infer-pyrefly            |    29.3 |        84.4 |  2.9 |    3.36 |          3 |      4.2 | False |
| sqlalchemy       | census                   |     7.8 |         5.6 |  0.7 |    0.09 |          2 |     1.06 | False |
| sqlalchemy       | coverage                 |     2.0 |         5.7 |  2.9 |    0.39 |          3 |     0.47 | False |
| sqlalchemy       | timing                   |    21.6 |        29.8 |  1.4 |    0.85 |         16 |     1.07 | False |
| sqlalchemy       | traced                   |   114.7 |       953.0 |  8.3 |    5.05 |         10 |     5.72 | False |
| sqlalchemy       | tests-released           |   126.3 |      1121.9 |  8.9 |    5.72 |          9 |     7.44 | False |
| sqlalchemy       | tests-fix-certain        |   104.3 |      1059.0 | 10.2 |    5.75 |          9 |     6.59 | False |
| sqlalchemy       | tests-fix-likely         |   116.5 |      1082.0 |  9.3 |    5.75 |          8 |     6.59 | False |
| sqlalchemy       | tests-fix-unsafe         |    96.5 |       977.6 | 10.1 |    5.14 |         11 |      6.0 | False |
| sqlalchemy       | tests-infer-basedpyright |    99.9 |      1041.8 | 10.4 |    5.79 |         12 |     6.57 | False |
| sqlalchemy       | tests-infer-ty           |    92.1 |      1029.1 | 11.2 |    5.75 |          8 |     7.33 | False |
| sqlalchemy       | tests-infer-pyrefly      |   160.4 |      1116.4 |  7.0 |     5.8 |          7 |      7.4 | False |
| sqlalchemy       | tests-infer-trace        |   178.2 |       808.0 |  4.5 |    3.56 |          8 |     3.75 | False |
| sqlalchemy       | tests                    |   267.3 |      1741.5 |  6.5 |    4.55 |         11 |     5.18 | False |
| sqlalchemy       | types-released           |     9.2 |         8.1 |  0.9 |    0.43 |          1 |     0.37 | False |
| sqlalchemy       | types-fix-certain        |     7.6 |         6.7 |  0.9 |    0.31 |          1 |     0.37 | False |
| sqlalchemy       | types-fix-likely         |     8.2 |         7.1 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy       | types-fix-unsafe         |     7.0 |         6.6 |  0.9 |     0.3 |          1 |     0.37 | False |
| sqlalchemy       | types-infer-basedpyright |     7.2 |         7.0 |  1.0 |    0.33 |          1 |     0.39 | False |
| sqlalchemy       | types-infer-ty           |     8.4 |         7.1 |  0.8 |     0.3 |          1 |     0.36 | False |
| sqlalchemy       | types-infer-pyrefly      |     7.0 |         6.6 |  0.9 |    0.32 |          1 |     0.37 | False |
| sqlalchemy       | types-infer-trace        |     7.2 |         6.6 |  0.9 |    0.31 |          1 |      0.4 | False |
| sqlalchemy       | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | check                    |     3.0 |         4.2 |  1.4 |     0.3 |          2 |     0.92 | False |
| pydantic         | fix-certain              |     4.8 |        10.6 |  2.2 |    0.44 |          3 |     1.19 | False |
| pydantic         | fix-likely               |     5.8 |        13.3 |  2.3 |    0.49 |          4 |     1.49 | False |
| pydantic         | fix-unsafe               |    12.4 |        14.1 |  1.1 |    0.55 |          3 |     1.21 | False |
| pydantic         | infer-basedpyright       |    54.7 |       139.7 |  2.6 |    3.08 |          4 |     3.92 | False |
| pydantic         | infer-ty                 |     7.8 |        23.5 |  3.0 |    1.67 |          3 |     2.05 | False |
| pydantic         | infer-pyrefly            |    14.0 |        46.7 |  3.3 |    2.52 |          4 |     3.06 | False |
| pydantic         | census                   |     1.0 |         0.8 |  0.8 |    0.05 |          2 |     0.92 | False |
| pydantic         | coverage                 |     1.0 |         2.0 |  2.0 |     0.2 |          3 |     0.45 | False |
| pydantic         | timing                   |     4.8 |         6.9 |  1.4 |     0.3 |         16 |     0.37 | False |
| pydantic         | traced                   |    68.3 |        66.3 |  1.0 |    0.47 |          1 |     0.56 | False |
| pydantic         | tests-released           |    53.5 |        40.8 |  0.8 |    0.36 |          1 |     0.31 | False |
| pydantic         | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic         | tests-fix-unsafe         |    47.3 |        37.5 |  0.8 |    0.28 |          1 |     0.35 | False |
| pydantic         | tests-infer-basedpyright |    44.5 |        36.7 |  0.8 |    0.28 |          1 |     0.31 | False |
| pydantic         | tests-infer-ty           |    42.1 |        36.9 |  0.9 |    0.28 |          1 |     0.35 | False |
| pydantic         | tests-infer-pyrefly      |    42.2 |        34.7 |  0.8 |    0.29 |          1 |     0.35 | False |
| pydantic         | tests-infer-trace        |    47.5 |        39.2 |  0.8 |    0.28 |          1 |     0.31 | False |
| pydantic         | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic         | types-released           |    15.6 |        19.5 |  1.2 |    0.53 |          1 |     0.65 | False |
| pydantic         | types-fix-certain        |    20.4 |        23.5 |  1.2 |    0.91 |          2 |     0.65 | False |
| pydantic         | types-fix-likely         |    16.0 |        19.6 |  1.2 |    0.53 |          1 |     0.67 | False |
| pydantic         | types-fix-unsafe         |    16.4 |        21.4 |  1.3 |    0.89 |          1 |     0.64 | False |
| pydantic         | types-infer-basedpyright |    20.8 |        23.7 |  1.1 |    0.57 |          2 |     0.69 | False |
| pydantic         | types-infer-ty           |    16.2 |        20.5 |  1.3 |    0.53 |          2 |     0.66 | False |
| pydantic         | types-infer-pyrefly      |    17.6 |        20.7 |  1.2 |    0.54 |          2 |      0.7 | False |
| pydantic         | types-infer-trace        |    14.6 |        18.8 |  1.3 |    0.53 |          2 |     0.66 | False |
| pydantic         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | check                    |    34.4 |       102.8 |  3.0 |    3.27 |          3 |     4.09 | False |
| pandas           | fix-certain              |   109.0 |       272.1 |  2.5 |    4.21 |          3 |     5.06 | False |
| pandas           | fix-likely               |   135.6 |       419.7 |  3.1 |    7.27 |          4 |     9.09 | False |
| pandas           | fix-unsafe               |    99.3 |       288.2 |  2.9 |     4.3 |          3 |     5.39 | False |
| pandas           | infer-basedpyright       |   530.2 |      1305.6 |  2.5 |   15.75 |          3 |    19.92 | False |
| pandas           | infer-ty                 |   240.1 |       758.2 |  3.2 |   13.79 |          3 |    18.29 | False |
| pandas           | infer-pyrefly            |   249.1 |       645.4 |  2.6 |   19.73 |          4 |    25.04 | False |
| pandas           | census                   |    35.8 |        19.4 |  0.5 |    0.33 |          3 |     4.09 | False |
| pandas           | coverage                 |     7.0 |        22.0 |  3.1 |    1.06 |          2 |     1.31 | False |
| pandas           | timing                   |   146.3 |       228.6 |  1.6 |    3.27 |         16 |     4.09 | False |
| pandas           | traced                   |   191.6 |      1151.9 |  6.0 |   14.03 |          6 |    19.82 | False |
| pandas           | tests-released           |   119.4 |       784.5 |  6.6 |   13.12 |          8 |    18.28 | False |
| pandas           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | tests-fix-unsafe         |   162.4 |       829.1 |  5.1 |   13.09 |          7 |    18.18 | False |
| pandas           | tests-infer-basedpyright |   123.1 |       763.1 |  6.2 |   12.99 |          8 |    17.64 | False |
| pandas           | tests-infer-ty           |   136.2 |       820.1 |  6.0 |   12.94 |          7 |    16.99 | False |
| pandas           | tests-infer-pyrefly      |   120.5 |       792.7 |  6.6 |   13.01 |          9 |    16.84 | False |
| pandas           | tests-infer-trace        |   127.8 |       700.9 |  5.5 |   10.61 |          8 |    13.63 | False |
| pandas           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas           | types-released           |    75.5 |       112.5 |  1.5 |    2.14 |          2 |     2.82 | False |
| pandas           | types-fix-certain        |    69.1 |       105.4 |  1.5 |    2.13 |          2 |     2.66 | False |
| pandas           | types-fix-likely         |    64.9 |        96.3 |  1.5 |    2.25 |          2 |      2.7 | False |
| pandas           | types-fix-unsafe         |    65.7 |       101.7 |  1.5 |    2.12 |          2 |     2.72 | False |
| pandas           | types-infer-basedpyright |    79.9 |        97.7 |  1.2 |     2.2 |          2 |     2.71 | False |
| pandas           | types-infer-ty           |    63.9 |        87.8 |  1.4 |    2.16 |          2 |      2.7 | False |
| pandas           | types-infer-pyrefly      |    77.5 |       101.7 |  1.3 |    2.03 |          2 |     2.94 | False |
| pandas           | types-infer-trace        |    82.9 |       104.0 |  1.3 |    2.05 |          2 |     2.74 | False |
| pandas           | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| twisted          | check                    |     7.0 |        14.8 |  2.1 |    0.83 |          3 |     1.02 | False |
| twisted          | fix-certain              |    14.0 |        36.5 |  2.6 |    0.94 |          4 |     1.17 | False |
| twisted          | fix-likely               |    19.0 |        49.0 |  2.6 |    1.41 |          3 |     1.76 | False |
| twisted          | fix-unsafe               |    16.4 |        38.5 |  2.3 |    0.96 |          3 |      1.2 | False |
| twisted          | infer-basedpyright       |    89.5 |       327.2 |  3.7 |    8.81 |          3 |    11.02 | False |
| twisted          | infer-ty                 |    24.0 |        82.2 |  3.4 |    3.58 |          3 |     4.02 | False |
| twisted          | infer-pyrefly            |    28.7 |        94.1 |  3.3 |    3.95 |          4 |     4.86 | False |
| twisted          | census                   |     7.0 |         5.5 |  0.8 |    0.11 |          3 |     1.02 | False |
| twisted          | coverage                 |     2.8 |         6.3 |  2.2 |    0.37 |          3 |     0.46 | False |
| twisted          | timing                   |    18.0 |        27.9 |  1.5 |    0.82 |         16 |     1.02 | False |
| pip              | check                    |     4.6 |         9.8 |  2.1 |    0.54 |          3 |     0.69 | False |
| pip              | fix-certain              |    13.2 |        29.3 |  2.2 |    0.72 |          3 |      0.9 | False |
| pip              | fix-likely               |    15.8 |        36.8 |  2.3 |    0.89 |          3 |     1.11 | False |
| pip              | fix-unsafe               |    10.6 |        27.0 |  2.5 |    0.71 |          3 |     0.89 | False |
| pip              | infer-basedpyright       |    43.7 |       196.0 |  4.5 |    5.24 |          5 |     6.71 | False |
| pip              | infer-ty                 |    20.2 |        59.8 |  3.0 |    2.84 |          3 |     3.31 | False |
| pip              | infer-pyrefly            |    21.6 |        68.3 |  3.2 |    3.23 |          4 |      3.2 | False |
| pip              | census                   |     3.6 |         3.3 |  0.9 |    0.09 |          3 |     0.69 | False |
| pip              | coverage                 |     2.0 |         4.1 |  2.0 |    0.33 |          3 |      0.4 | False |
| pip              | timing                   |    12.2 |        18.2 |  1.5 |    0.54 |         16 |     0.67 | False |

- django, 0.3.8-rc.1+dev, tests: the tests differ after fix-certain: 1 new
- standard library, 0.3.8-rc.1+dev, infer-basedpyright: held 12.53 GB beside other steps
- standard library, 0.3.8-rc.1+dev, infer-ty: held 15.27 GB beside other steps
- standard library, 0.3.8-rc.1+dev, infer-pyrefly: held 19.05 GB beside other steps
- pandas, 0.3.8-rc.1+dev, infer-basedpyright: held 15.75 GB beside other steps
- pandas, 0.3.8-rc.1+dev, infer-ty: held 13.79 GB beside other steps
- pandas, 0.3.8-rc.1+dev, infer-pyrefly: held 19.73 GB beside other steps
- pandas, 0.3.8-rc.1+dev, traced: held 14.03 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-released: held 13.12 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-fix-unsafe: held 13.09 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-basedpyright: held 12.99 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-ty: held 12.94 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-pyrefly: held 13.01 GB beside other steps
- pandas, 0.3.8-rc.1+dev, tests-infer-trace: held 10.61 GB beside other steps
- twisted, 0.3.8-rc.1+dev, infer-basedpyright: held 8.81 GB beside other steps

## constricter 0.2.2

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |       `LVA002` |       `LVA004` |   `LVA005` | `LVA006` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | -------------: | -------------: | ---------: | -------: | ------: |
| standard library | 3.14    | 0.2.2       | 1,867 |          88,987 |         12,335 |         12,852 |         57 |        0 | 114,231 |
| django           | 5.2.17  | 0.2.2       |   883 |           9,921 |          2,167 |          5,099 |          0 |        0 |  17,187 |
| sqlalchemy       | 2.0.54  | 0.2.2       |   257 |           8,505 |          1,567 |          2,569 |        551 |        7 |  13,199 |
| pydantic         | 2.13.5  | 0.2.2       |   105 |           2,023 |            438 |            714 |        190 |        0 |   3,365 |
| twisted          | 12.3.0  | 0.2.2       |   819 |          13,310 |          1,349 |          3,215 |          0 |        0 |  17,874 |
| **Total**        |         | 0.2.2       | 3,931 | 122,746 (74.0%) | 17,856 (10.8%) | 24,449 (14.7%) | 798 (0.5%) | 7 (0.0%) | 165,856 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |   `constrict` | `suffocate` |        Fixed |       Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | ------------: | ----------: | -----------: | ------------: | -----: | ---: |
| standard library | 0.2.2       | 0 / 114,174 | 101,839 / 12,392 |  114,174 / 57 | 114,231 / 0 |      crashed |       crashed |      0 |    0 |
| django           | 0.2.2       |  0 / 17,187 |   15,020 / 2,167 |    17,187 / 0 |  17,187 / 0 | 1,634 (9.5%) |    522 (3.0%) |      0 |    0 |
| sqlalchemy       | 0.2.2       |  0 / 12,641 |   11,074 / 2,125 |  12,641 / 558 |  13,199 / 0 |   369 (2.8%) |    274 (2.1%) |      0 |    0 |
| pydantic         | 0.2.2       |   0 / 3,175 |      2,737 / 628 |   3,175 / 190 |   3,365 / 0 |   264 (7.8%) |    108 (3.2%) |      0 |    0 |
| twisted          | 0.2.2       |  0 / 17,874 |   16,525 / 1,349 |    17,874 / 0 |  17,874 / 0 | 1,253 (7.0%) | 3,375 (18.9%) |      0 |    0 |
| **Total**        | 0.2.2       | 0 / 165,051 | 147,195 / 18,661 | 165,051 / 805 | 165,856 / 0 |      crashed |       crashed |      0 |    0 |

## constricter 0.2.3

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |       `LVA002` |       `LVA004` |   `LVA005` | `LVA006` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | -------------: | -------------: | ---------: | -------: | ------: |
| standard library | 3.14    | 0.2.3       | 1,867 |          88,987 |         12,335 |         12,852 |         57 |        0 | 114,231 |
| django           | 5.2.17  | 0.2.3       |   883 |           9,921 |          2,167 |          5,099 |          0 |        0 |  17,187 |
| sqlalchemy       | 2.0.54  | 0.2.3       |   257 |           8,505 |          1,567 |          2,569 |        551 |        7 |  13,199 |
| pydantic         | 2.13.5  | 0.2.3       |   105 |           2,023 |            438 |            714 |        190 |        0 |   3,365 |
| twisted          | 12.3.0  | 0.2.3       |   819 |          13,310 |          1,349 |          3,215 |          0 |        0 |  17,874 |
| **Total**        |         | 0.2.3       | 3,931 | 122,746 (74.0%) | 17,856 (10.8%) | 24,449 (14.7%) | 798 (0.5%) | 7 (0.0%) | 165,856 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |   `constrict` | `suffocate` |          Fixed |       Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | ------------: | ----------: | -------------: | ------------: | -----: | ---: |
| standard library | 0.2.3       | 0 / 114,174 | 101,839 / 12,392 |  114,174 / 57 | 114,231 / 0 | 12,350 (10.8%) | 11,225 (9.8%) |      0 |    0 |
| django           | 0.2.3       |  0 / 17,187 |   15,020 / 2,167 |    17,187 / 0 |  17,187 / 0 |  1,775 (10.3%) |    549 (3.2%) |      0 |    0 |
| sqlalchemy       | 0.2.3       |  0 / 12,641 |   11,074 / 2,125 |  12,641 / 558 |  13,199 / 0 |     748 (5.7%) |    291 (2.2%) |      0 |    0 |
| pydantic         | 0.2.3       |   0 / 3,175 |      2,737 / 628 |   3,175 / 190 |   3,365 / 0 |    355 (10.5%) |    111 (3.3%) |      0 |    0 |
| twisted          | 0.2.3       |  0 / 17,874 |   16,525 / 1,349 |    17,874 / 0 |  17,874 / 0 |   1,476 (8.3%) | 3,400 (19.0%) |      0 |    0 |
| **Total**        | 0.2.3       | 0 / 165,051 | 147,195 / 18,661 | 165,051 / 805 | 165,856 / 0 | 16,704 (10.1%) | 15,576 (9.4%) |      0 |    0 |

## constricter 0.2.4

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.2.4       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.2.4       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.2.4       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.2.4       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.2.4       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.2.4       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.2.4       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.2.4       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.2.4       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 20,970 (18.4%) | 12,273 (10.7%) |      0 |    0 |
| django           | 0.2.4       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,166 (12.6%) |     781 (4.5%) |      0 |    0 |
| sqlalchemy       | 0.2.4       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,196 (9.0%) |     416 (3.1%) |      0 |    0 |
| pydantic         | 0.2.4       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    634 (18.8%) |     142 (4.2%) |      0 |    0 |
| pandas           | 0.2.4       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 |  9,857 (12.6%) | 21,844 (28.0%) |      0 |    0 |
| twisted          | 0.2.4       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  1,964 (11.0%) |  3,566 (20.0%) |      0 |    0 |
| pip              | 0.2.4       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,234 (13.8%) |     470 (5.3%) |      0 |    0 |
| **Total**        | 0.2.4       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 38,021 (15.0%) | 39,492 (15.6%) |      0 |    0 |

## constricter 0.2.5

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.2.5       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.2.5       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.2.5       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.2.5       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.2.5       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.2.5       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.2.5       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.2.5       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.2.5       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 26,590 (23.3%) |  10,743 (9.4%) |      0 |    0 |
| django           | 0.2.5       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,306 (13.4%) |     985 (5.7%) |      0 |    0 |
| sqlalchemy       | 0.2.5       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,093 (8.2%) |     606 (4.6%) |      0 |    0 |
| pydantic         | 0.2.5       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    635 (18.8%) |     212 (6.3%) |      0 |    0 |
| pandas           | 0.2.5       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 | 10,024 (12.9%) | 22,236 (28.5%) |      0 |    0 |
| twisted          | 0.2.5       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,157 (12.1%) |  3,547 (19.8%) |      0 |    0 |
| pip              | 0.2.5       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,347 (15.1%) |     640 (7.2%) |      0 |    0 |
| **Total**        | 0.2.5       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 44,152 (17.5%) | 38,969 (15.4%) |      0 |    0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.2.5       |              1.2% |         24.2% |                  33.5% | +23.0 pts, 23.3% of untyped | +32.3 pts, 32.7% of untyped |
| django           | 0.2.5       |              0.0% |         13.4% |                  19.2% | +13.4 pts, 13.4% of untyped | +19.1 pts, 19.1% of untyped |
| sqlalchemy       | 0.2.5       |             14.5% |         21.9% |                  26.0% |   +7.4 pts, 8.6% of untyped | +11.5 pts, 13.4% of untyped |
| pydantic         | 0.2.5       |             21.4% |         37.1% |                  42.4% | +15.7 pts, 20.0% of untyped | +21.0 pts, 26.7% of untyped |
| pandas           | 0.2.5       |              1.6% |         14.3% |                  42.4% | +12.7 pts, 12.9% of untyped | +40.8 pts, 41.4% of untyped |
| twisted          | 0.2.5       |              0.0% |         12.1% |                  31.9% | +12.1 pts, 12.1% of untyped | +31.9 pts, 31.9% of untyped |
| pip              | 0.2.5       |              1.5% |         16.3% |                  23.4% | +14.8 pts, 15.1% of untyped | +21.9 pts, 22.2% of untyped |
| **Total**        | 0.2.5       |              2.2% |         19.4% |                  34.5% | +17.1 pts, 17.5% of untyped | +32.3 pts, 33.0% of untyped |

## constricter 0.2.6

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.2.6       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.2.6       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.2.6       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.2.6       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.2.6       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.2.6       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.2.6       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.2.6       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.2.6       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 28,503 (24.9%) |   9,033 (7.9%) |      0 |  911 |
| django           | 0.2.6       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,394 (13.9%) |   1,078 (6.3%) |      0 |    0 |
| sqlalchemy       | 0.2.6       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,239 (9.3%) |     450 (3.4%) |      0 |    0 |
| pydantic         | 0.2.6       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    660 (19.5%) |     207 (6.1%) |      0 |    0 |
| pandas           | 0.2.6       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 | 10,340 (13.3%) | 22,415 (28.7%) |      0 |    0 |
| twisted          | 0.2.6       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,198 (12.3%) |  3,714 (20.8%) |      0 |    0 |
| pip              | 0.2.6       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,561 (17.4%) |     675 (7.5%) |      0 |    0 |
| **Total**        | 0.2.6       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 46,895 (18.5%) | 37,572 (14.9%) |      0 |  911 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.2.6       |              1.2% |         25.8% |                  33.6% | +24.7 pts, 25.0% of untyped | +32.5 pts, 32.9% of untyped |
| django           | 0.2.6       |              0.0% |         13.9% |                  20.2% | +13.9 pts, 13.9% of untyped | +20.2 pts, 20.2% of untyped |
| sqlalchemy       | 0.2.6       |             14.5% |         22.9% |                  25.9% |   +8.4 pts, 9.8% of untyped | +11.4 pts, 13.4% of untyped |
| pydantic         | 0.2.6       |             21.4% |         37.7% |                  42.9% | +16.3 pts, 20.8% of untyped | +21.5 pts, 27.3% of untyped |
| pandas           | 0.2.6       |              1.6% |         14.7% |                  43.0% | +13.1 pts, 13.3% of untyped | +41.4 pts, 42.1% of untyped |
| twisted          | 0.2.6       |              0.0% |         12.3% |                  33.1% | +12.3 pts, 12.3% of untyped | +33.1 pts, 33.1% of untyped |
| pip              | 0.2.6       |              1.5% |         18.7% |                  26.1% | +17.2 pts, 17.4% of untyped | +24.6 pts, 25.0% of untyped |
| **Total**        | 0.2.6       |              2.2% |         20.4% |                  35.0% | +18.2 pts, 18.6% of untyped | +32.8 pts, 33.5% of untyped |

## constricter 0.2.7

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.2.7       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.2.7       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.2.7       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.2.7       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.2.7       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.2.7       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.2.7       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.2.7       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.2.7       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 28,503 (24.9%) |   9,033 (7.9%) |      0 |  911 |
| django           | 0.2.7       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,394 (13.9%) |   1,078 (6.3%) |      0 |    0 |
| sqlalchemy       | 0.2.7       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,239 (9.3%) |     450 (3.4%) |      0 |    0 |
| pydantic         | 0.2.7       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    660 (19.5%) |     207 (6.1%) |      0 |    0 |
| pandas           | 0.2.7       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 | 10,340 (13.3%) | 22,415 (28.7%) |      0 |    0 |
| twisted          | 0.2.7       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,198 (12.3%) |  3,714 (20.8%) |      0 |    0 |
| pip              | 0.2.7       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,561 (17.4%) |     675 (7.5%) |      0 |    0 |
| **Total**        | 0.2.7       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 46,895 (18.5%) | 37,572 (14.9%) |      0 |  911 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.2.7       |              1.2% |         25.8% |                  33.6% | +24.7 pts, 25.0% of untyped | +32.5 pts, 32.9% of untyped |
| django           | 0.2.7       |              0.0% |         13.9% |                  20.2% | +13.9 pts, 13.9% of untyped | +20.2 pts, 20.2% of untyped |
| sqlalchemy       | 0.2.7       |             14.5% |         22.9% |                  25.9% |   +8.4 pts, 9.8% of untyped | +11.4 pts, 13.4% of untyped |
| pydantic         | 0.2.7       |             21.4% |         37.7% |                  42.9% | +16.3 pts, 20.8% of untyped | +21.5 pts, 27.3% of untyped |
| pandas           | 0.2.7       |              1.6% |         14.7% |                  43.0% | +13.1 pts, 13.3% of untyped | +41.4 pts, 42.1% of untyped |
| twisted          | 0.2.7       |              0.0% |         12.3% |                  33.1% | +12.3 pts, 12.3% of untyped | +33.1 pts, 33.1% of untyped |
| pip              | 0.2.7       |              1.5% |         18.7% |                  26.1% | +17.2 pts, 17.4% of untyped | +24.6 pts, 25.0% of untyped |
| **Total**        | 0.2.7       |              2.2% |         20.4% |                  35.0% | +18.2 pts, 18.6% of untyped | +32.8 pts, 33.5% of untyped |

## constricter 0.2.8

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.2.8       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.2.8       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.2.8       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.2.8       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.2.8       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.2.8       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.2.8       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.2.8       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.2.8       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 29,746 (26.0%) |   9,395 (8.2%) |      0 |    0 |
| django           | 0.2.8       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,426 (14.1%) |   1,124 (6.5%) |      0 |    0 |
| sqlalchemy       | 0.2.8       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,314 (9.9%) |     467 (3.5%) |      0 |    0 |
| pydantic         | 0.2.8       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    720 (21.3%) |     236 (7.0%) |      0 |    0 |
| pandas           | 0.2.8       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 | 10,397 (13.3%) | 22,373 (28.7%) |      0 |    0 |
| twisted          | 0.2.8       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,218 (12.4%) |  3,741 (20.9%) |      0 |    0 |
| pip              | 0.2.8       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,593 (17.8%) |     737 (8.2%) |      0 |    0 |
| **Total**        | 0.2.8       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 48,414 (19.1%) | 38,073 (15.1%) |      0 |    0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.2.8       |              1.2% |         26.9% |                  35.0% | +25.8 pts, 26.0% of untyped | +33.9 pts, 34.3% of untyped |
| django           | 0.2.8       |              0.0% |         14.1% |                  20.7% | +14.1 pts, 14.1% of untyped | +20.7 pts, 20.7% of untyped |
| sqlalchemy       | 0.2.8       |             14.5% |         23.4% |                  26.6% |  +8.9 pts, 10.4% of untyped | +12.0 pts, 14.1% of untyped |
| pydantic         | 0.2.8       |             21.4% |         39.2% |                  45.1% | +17.8 pts, 22.7% of untyped | +23.7 pts, 30.1% of untyped |
| pandas           | 0.2.8       |              1.6% |         14.7% |                  43.0% | +13.1 pts, 13.4% of untyped | +41.4 pts, 42.1% of untyped |
| twisted          | 0.2.8       |              0.0% |         12.4% |                  33.3% | +12.4 pts, 12.4% of untyped | +33.3 pts, 33.3% of untyped |
| pip              | 0.2.8       |              1.5% |         19.0% |                  27.1% | +17.5 pts, 17.8% of untyped | +25.6 pts, 26.0% of untyped |
| **Total**        | 0.2.8       |              2.2% |         21.0% |                  35.8% | +18.8 pts, 19.2% of untyped | +33.6 pts, 34.3% of untyped |

## constricter 0.2.9

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.2.9       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.2.9       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.2.9       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.2.9       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.2.9       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.2.9       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.2.9       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.2.9       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.2.9       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 29,746 (26.0%) |   9,395 (8.2%) |      0 |    0 |
| django           | 0.2.9       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,426 (14.1%) |   1,124 (6.5%) |      0 |    0 |
| sqlalchemy       | 0.2.9       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,314 (9.9%) |     467 (3.5%) |      0 |    0 |
| pydantic         | 0.2.9       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    720 (21.3%) |     236 (7.0%) |      0 |    0 |
| pandas           | 0.2.9       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 | 10,628 (13.6%) | 22,392 (28.7%) |      0 |    0 |
| twisted          | 0.2.9       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,218 (12.4%) |  3,741 (20.9%) |      0 |    0 |
| pip              | 0.2.9       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,593 (17.8%) |     737 (8.2%) |      0 |    0 |
| **Total**        | 0.2.9       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 48,645 (19.2%) | 38,092 (15.1%) |      0 |    0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.2.9       |              1.2% |         26.9% |                  35.0% | +25.8 pts, 26.0% of untyped | +33.9 pts, 34.3% of untyped |
| django           | 0.2.9       |              0.0% |         14.1% |                  20.7% | +14.1 pts, 14.1% of untyped | +20.7 pts, 20.7% of untyped |
| sqlalchemy       | 0.2.9       |             14.5% |         23.4% |                  26.6% |  +8.9 pts, 10.4% of untyped | +12.0 pts, 14.1% of untyped |
| pydantic         | 0.2.9       |             21.4% |         39.2% |                  45.1% | +17.8 pts, 22.7% of untyped | +23.7 pts, 30.1% of untyped |
| pandas           | 0.2.9       |              1.6% |         15.0% |                  43.3% | +13.4 pts, 13.7% of untyped | +41.7 pts, 42.4% of untyped |
| twisted          | 0.2.9       |              0.0% |         12.4% |                  33.3% | +12.4 pts, 12.4% of untyped | +33.3 pts, 33.3% of untyped |
| pip              | 0.2.9       |              1.5% |         19.0% |                  27.1% | +17.5 pts, 17.8% of untyped | +25.6 pts, 26.0% of untyped |
| **Total**        | 0.2.9       |              2.2% |         21.1% |                  35.9% | +18.9 pts, 19.3% of untyped | +33.7 pts, 34.4% of untyped |

## constricter 0.3.1

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` | `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | -------: | -------: | ------: |
| standard library | 3.14    | 0.3.1       | 1,867 |          88,987 |        12,335 |         12,854 |         57 |         14 |        8 |        0 | 114,255 |
| django           | 5.2.17  | 0.3.1       |   883 |           9,921 |         2,167 |          5,099 |          0 |          0 |        1 |        0 |  17,188 |
| sqlalchemy       | 2.0.54  | 0.3.1       |   257 |           8,505 |         1,567 |          2,569 |        551 |        124 |        0 |        1 |  13,317 |
| pydantic         | 2.13.5  | 0.3.1       |   105 |           2,023 |           438 |            714 |        190 |         13 |        0 |        0 |   3,378 |
| pandas           | 3.0.6   | 0.3.1       | 1,421 |          73,380 |         2,778 |          1,690 |        134 |          2 |        0 |        1 |  77,985 |
| twisted          | 12.3.0  | 0.3.1       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |        0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.3.1       |   366 |           5,902 |         1,150 |          1,895 |          0 |          0 |        0 |        0 |   8,947 |
| **Total**        |         | 0.3.1       | 5,718 | 202,028 (79.9%) | 21,784 (8.6%) | 28,036 (11.1%) | 932 (0.4%) | 153 (0.1%) | 9 (0.0%) | 2 (0.0%) | 252,944 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.3.1       | 0 / 114,184 | 101,841 / 12,414 |    114,184 / 71 | 114,255 / 0 | 29,746 (26.0%) |   9,395 (8.2%) |      0 |    0 |
| django           | 0.3.1       |  0 / 17,188 |   15,020 / 2,168 |      17,188 / 0 |  17,188 / 0 |  2,426 (14.1%) |   1,124 (6.5%) |      0 |    0 |
| sqlalchemy       | 0.3.1       |  0 / 12,641 |   11,074 / 2,243 |    12,641 / 676 |  13,317 / 0 |   1,314 (9.9%) |     467 (3.5%) |      0 |    0 |
| pydantic         | 0.3.1       |   0 / 3,175 |      2,737 / 641 |     3,175 / 203 |   3,378 / 0 |    720 (21.3%) |     236 (7.0%) |      0 |    0 |
| pandas           | 0.3.1       |  0 / 77,848 |   75,070 / 2,915 |    77,848 / 137 |  77,985 / 0 | 10,628 (13.6%) | 22,392 (28.7%) |      0 |    0 |
| twisted          | 0.3.1       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,218 (12.4%) |  3,741 (20.9%) |      0 |    0 |
| pip              | 0.3.1       |   0 / 8,947 |    7,797 / 1,150 |       8,947 / 0 |   8,947 / 0 |  1,593 (17.8%) |     737 (8.2%) |      0 |    0 |
| **Total**        | 0.3.1       | 0 / 251,857 | 230,064 / 22,880 | 251,857 / 1,087 | 252,944 / 0 | 48,645 (19.2%) | 38,092 (15.1%) |      0 |    0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.3.1       |              1.2% |         26.9% |                  35.0% | +25.8 pts, 26.0% of untyped | +33.9 pts, 34.3% of untyped |
| django           | 0.3.1       |              0.0% |         14.1% |                  20.7% | +14.1 pts, 14.1% of untyped | +20.7 pts, 20.7% of untyped |
| sqlalchemy       | 0.3.1       |             14.5% |         23.4% |                  26.6% |  +8.9 pts, 10.4% of untyped | +12.0 pts, 14.1% of untyped |
| pydantic         | 0.3.1       |             21.4% |         39.2% |                  45.1% | +17.8 pts, 22.7% of untyped | +23.7 pts, 30.1% of untyped |
| pandas           | 0.3.1       |              1.6% |         15.0% |                  43.3% | +13.4 pts, 13.7% of untyped | +41.7 pts, 42.4% of untyped |
| twisted          | 0.3.1       |              0.0% |         12.4% |                  33.3% | +12.4 pts, 12.4% of untyped | +33.3 pts, 33.3% of untyped |
| pip              | 0.3.1       |              1.5% |         19.0% |                  27.1% | +17.5 pts, 17.8% of untyped | +25.6 pts, 26.0% of untyped |
| **Total**        | 0.3.1       |              2.2% |         21.1% |                  35.9% | +18.9 pts, 19.3% of untyped | +33.7 pts, 34.4% of untyped |

## constricter 0.3.6

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14    | 0.3.6       | 1,867 |          88,579 |        12,335 |         12,782 |         57 |         14 |         8 |        0 | 113,775 |
| django           | 5.2.17  | 0.3.6       |   883 |           9,921 |         2,167 |          5,081 |          0 |          0 |         1 |        0 |  17,170 |
| sqlalchemy       | 2.0.54  | 0.3.6       |   257 |           8,504 |         1,567 |          2,339 |        551 |        124 |         1 |        1 |  13,087 |
| pydantic         | 2.13.5  | 0.3.6       |   105 |           2,023 |           438 |            631 |        190 |         13 |         0 |        0 |   3,295 |
| pandas           | 3.0.6   | 0.3.6       | 1,421 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | 0.3.6       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.3.6       |   366 |           5,902 |         1,150 |          1,872 |          0 |          0 |         0 |        0 |   8,924 |
| **Total**        |         | 0.3.6       | 5,718 | 201,606 (80.0%) | 21,784 (8.6%) | 27,568 (10.9%) | 932 (0.4%) | 153 (0.1%) | 11 (0.0%) | 2 (0.0%) | 252,056 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed and
what `--unsafe-fixes` guessed on top (each also as a share of the offences at `suffocate`), files a
fix broke, and what a second pass would still fix:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Guessed | Broken | Left |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -----: | ---: |
| standard library | 0.3.6       | 0 / 113,704 | 101,361 / 12,414 |    113,704 / 71 | 113,775 / 0 | 37,395 (32.9%) | 12,336 (10.8%) |      0 |    0 |
| django           | 0.3.6       |  0 / 17,170 |   15,002 / 2,168 |      17,170 / 0 |  17,170 / 0 |  2,618 (15.2%) |  2,661 (15.5%) |      0 |    0 |
| sqlalchemy       | 0.3.6       |  0 / 12,411 |   10,843 / 2,244 |    12,411 / 676 |  13,087 / 0 |  1,829 (14.0%) |     801 (6.1%) |      0 |    0 |
| pydantic         | 0.3.6       |   0 / 3,092 |      2,654 / 641 |     3,092 / 203 |   3,295 / 0 |  1,158 (35.1%) |    410 (12.4%) |      0 |    0 |
| pandas           | 0.3.6       |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,945 (21.7%) | 24,616 (31.6%) |      0 |    0 |
| twisted          | 0.3.6       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,437 (13.6%) |  4,662 (26.1%) |      0 |    0 |
| pip              | 0.3.6       |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,253 (25.2%) |  1,133 (12.7%) |      0 |    0 |
| **Total**        | 0.3.6       | 0 / 250,969 | 229,174 / 22,882 | 250,969 / 1,087 | 252,056 / 0 | 64,635 (25.6%) | 46,619 (18.5%) |      0 |    0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, and after `--fix --unsafe-fixes`, and how
much each raised it: in percentage points, and as a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.3.6       |              1.2% |         33.7% |                  44.4% | +32.5 pts, 32.9% of untyped | +43.2 pts, 43.7% of untyped |
| django           | 0.3.6       |              0.0% |         15.3% |                  30.8% | +15.2 pts, 15.2% of untyped | +30.7 pts, 30.7% of untyped |
| sqlalchemy       | 0.3.6       |             14.8% |         27.3% |                  32.8% | +12.6 pts, 14.7% of untyped | +18.1 pts, 21.2% of untyped |
| pydantic         | 0.3.6       |             21.8% |         51.1% |                  61.5% | +29.3 pts, 37.5% of untyped | +39.6 pts, 50.7% of untyped |
| pandas           | 0.3.6       |              1.6% |         23.0% |                  54.2% | +21.4 pts, 21.8% of untyped | +52.6 pts, 53.4% of untyped |
| twisted          | 0.3.6       |              0.0% |         13.6% |                  39.7% | +13.6 pts, 13.6% of untyped | +39.7 pts, 39.7% of untyped |
| pip              | 0.3.6       |              1.5% |         26.4% |                  38.9% | +24.9 pts, 25.2% of untyped | +37.4 pts, 37.9% of untyped |
| **Total**        | 0.3.6       |              2.2% |         27.4% |                  45.6% | +25.2 pts, 25.8% of untyped | +43.3 pts, 44.3% of untyped |

## constricter 0.3.6-rc.1

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14    | 0.3.6-rc.1  | 1,867 |          88,579 |        12,335 |         12,782 |         57 |         14 |         8 |        0 | 113,775 |
| django           | 5.2.17  | 0.3.6-rc.1  |   883 |           9,921 |         2,167 |          5,081 |          0 |          0 |         1 |        0 |  17,170 |
| sqlalchemy       | 2.0.54  | 0.3.6-rc.1  |   257 |           8,504 |         1,567 |          2,339 |        551 |        124 |         1 |        1 |  13,087 |
| pydantic         | 2.13.5  | 0.3.6-rc.1  |   105 |           2,023 |           438 |            631 |        190 |         13 |         0 |        0 |   3,295 |
| pandas           | 3.0.6   | 0.3.6-rc.1  | 1,421 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | 0.3.6-rc.1  |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.3.6-rc.1  |   366 |           5,902 |         1,150 |          1,872 |          0 |          0 |         0 |        0 |   8,924 |
| **Total**        |         | 0.3.6-rc.1  | 5,718 | 201,606 (80.0%) | 21,784 (8.6%) | 27,568 (10.9%) | 932 (0.4%) | 153 (0.1%) | 11 (0.0%) | 2 (0.0%) | 252,056 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library | 0.3.6-rc.1  | 0 / 113,704 | 101,361 / 12,414 |    113,704 / 71 | 113,775 / 0 | 37,385 (32.9%) |   6,251 (5.5%) | 12,313 (10.8%) |      0 |    0 |          210 |
| django           | 0.3.6-rc.1  |  0 / 17,170 |   15,002 / 2,168 |      17,170 / 0 |  17,170 / 0 |  2,618 (15.2%) |     628 (3.7%) |  2,661 (15.5%) |      0 |    0 |            6 |
| sqlalchemy       | 0.3.6-rc.1  |  0 / 12,411 |   10,843 / 2,244 |    12,411 / 676 |  13,087 / 0 |  1,828 (14.0%) |     315 (2.4%) |     801 (6.1%) |      0 |    0 |            9 |
| pydantic         | 0.3.6-rc.1  |   0 / 3,092 |      2,654 / 641 |     3,092 / 203 |   3,295 / 0 |  1,158 (35.1%) |     139 (4.2%) |    409 (12.4%) |      0 |    0 |           11 |
| pandas           | 0.3.6-rc.1  |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,945 (21.7%) | 23,433 (30.1%) | 24,616 (31.6%) |      0 |    0 |          243 |
| twisted          | 0.3.6-rc.1  |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,437 (13.6%) |  3,534 (19.8%) |  4,655 (26.0%) |      0 |    0 |          173 |
| pip              | 0.3.6-rc.1  |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,253 (25.2%) |     414 (4.6%) |  1,133 (12.7%) |      0 |    0 |           28 |
| **Total**        | 0.3.6-rc.1  | 0 / 250,969 | 229,174 / 22,882 | 250,969 / 1,087 | 252,056 / 0 | 64,624 (25.6%) | 34,714 (13.8%) | 46,588 (18.5%) |      0 |    0 |          680 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.3.6-rc.1  |              1.2% |         33.7% |            39.1% |                  44.4% | +32.5 pts, 32.9% of untyped | +43.2 pts, 43.7% of untyped |
| django           | 0.3.6-rc.1  |              0.0% |         15.3% |            18.9% |                  30.8% | +15.2 pts, 15.2% of untyped | +30.7 pts, 30.7% of untyped |
| sqlalchemy       | 0.3.6-rc.1  |             14.8% |         27.3% |            29.5% |                  32.8% | +12.5 pts, 14.7% of untyped | +18.0 pts, 21.2% of untyped |
| pydantic         | 0.3.6-rc.1  |             21.8% |         51.1% |            54.6% |                  61.5% | +29.3 pts, 37.5% of untyped | +39.6 pts, 50.7% of untyped |
| pandas           | 0.3.6-rc.1  |              1.6% |         23.0% |            52.7% |                  54.2% | +21.4 pts, 21.8% of untyped | +52.6 pts, 53.4% of untyped |
| twisted          | 0.3.6-rc.1  |              0.0% |         13.6% |            33.4% |                  39.7% | +13.6 pts, 13.6% of untyped | +39.7 pts, 39.7% of untyped |
| pip              | 0.3.6-rc.1  |              1.5% |         26.4% |            30.9% |                  38.9% | +24.9 pts, 25.2% of untyped | +37.4 pts, 37.9% of untyped |
| **Total**        | 0.3.6-rc.1  |              2.2% |         27.4% |            40.9% |                  45.6% | +25.2 pts, 25.7% of untyped | +43.3 pts, 44.3% of untyped |

## constricter 0.4.0

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14.7  | 0.4.0       | 1,867 |          88,565 |        12,334 |         12,772 |         57 |         14 |         8 |        0 | 113,750 |
| django           | 5.2.18  | 0.4.0       |   883 |           9,926 |         2,166 |          5,084 |          0 |          0 |         1 |        0 |  17,177 |
| sqlalchemy       | 2.1.4   | 0.4.0       |   258 |           8,825 |         1,636 |          2,501 |        572 |        128 |         2 |        1 |  13,665 |
| pydantic         | 2.14.0  | 0.4.0       |   105 |           2,072 |           440 |            605 |        184 |         15 |         0 |        0 |   3,316 |
| pandas           | 3.0.6   | 0.4.0       | 1,420 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | 0.4.0       |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | 0.4.0       |   366 |           5,902 |         1,150 |          1,872 |          0 |          0 |         0 |        0 |   8,924 |
| **Total**        |         | 0.4.0       | 5,718 | 201,967 (79.9%) | 21,853 (8.6%) | 27,697 (11.0%) | 947 (0.4%) | 159 (0.1%) | 12 (0.0%) | 2 (0.0%) | 252,637 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library | 0.4.0       | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,415 (32.9%) |   6,530 (5.7%) | 12,304 (10.8%) |      0 |    0 |            0 |
| django           | 0.4.0       |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |  2,627 (15.3%) |     634 (3.7%) |  2,693 (15.7%) |      0 |    0 |            0 |
| sqlalchemy       | 0.4.0       |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |  1,881 (13.8%) |     334 (2.4%) |     818 (6.0%) |      0 |    0 |            0 |
| pydantic         | 0.4.0       |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |  1,185 (35.7%) |     146 (4.4%) |    404 (12.2%) |      0 |    0 |            0 |
| pandas           | 0.4.0       |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,910 (21.7%) | 23,550 (30.2%) | 24,299 (31.2%) |      0 |    0 |            0 |
| twisted          | 0.4.0       |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,439 (13.6%) |  3,620 (20.3%) |  4,624 (25.9%) |      0 |    0 |            0 |
| pip              | 0.4.0       |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,254 (25.3%) |     421 (4.7%) |  1,109 (12.4%) |      0 |    0 |            0 |
| **Total**        | 0.4.0       | 0 / 251,529 | 229,664 / 22,973 | 251,529 / 1,108 | 252,637 / 0 | 64,711 (25.6%) | 35,235 (13.9%) | 46,251 (18.3%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | 0.4.0       |              1.2% |         33.7% |            39.4% |                  44.4% | +32.5 pts, 32.9% of untyped | +43.2 pts, 43.7% of untyped |
| django           | 0.4.0       |              0.0% |         15.3% |            19.0% |                  31.0% | +15.3 pts, 15.3% of untyped | +31.0 pts, 31.0% of untyped |
| sqlalchemy       | 0.4.0       |             15.3% |         27.5% |            29.7% |                  32.9% | +12.3 pts, 14.5% of untyped | +17.6 pts, 20.8% of untyped |
| pydantic         | 0.4.0       |             22.4% |         51.9% |            55.6% |                  62.0% | +29.5 pts, 38.0% of untyped | +39.5 pts, 51.0% of untyped |
| pandas           | 0.4.0       |              1.6% |         23.0% |            52.8% |                  53.7% | +21.4 pts, 21.7% of untyped | +52.1 pts, 53.0% of untyped |
| twisted          | 0.4.0       |              0.0% |         13.6% |            33.9% |                  39.5% | +13.6 pts, 13.6% of untyped | +39.5 pts, 39.5% of untyped |
| pip              | 0.4.0       |              1.5% |         26.4% |            31.0% |                  38.6% | +24.9 pts, 25.2% of untyped | +37.1 pts, 37.7% of untyped |
| **Total**        | 0.4.0       |              2.3% |         27.5% |            41.1% |                  45.4% | +25.1 pts, 25.7% of untyped | +43.1 pts, 44.1% of untyped |
