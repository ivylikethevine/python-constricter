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

The run `0.3.7-rc.1` (`python -m tests.corpus`) on mega: constricter 0.3.7 (`f6872d429e40`), Python
3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own, started once the CPUs
it's expected to keep busy and the memory it's expected to hold are free. The run took 155 minutes.
Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter    |  Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |     `LVA006` |  `LVA009` | `LVA010` | `LVA011` |   Total |
| ------------------ | -------- | -------------- | -----: | --------------: | ------------: | -------: | -------------: | -----------: | -----------: | --------: | -------: | -------: | ------: |
| standard library   | 3.14.7   | 0.3.7-rc.1+dev |  1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |           14 |         8 |        0 |        0 | 113,750 |
| django             | 5.2.17   | 0.3.7-rc.1+dev |    883 |           9,921 |         2,167 |        0 |          5,081 |            0 |            0 |         1 |        0 |        0 |  17,170 |
| sqlalchemy         | 2.0.54   | 0.3.7-rc.1+dev |    257 |           8,504 |         1,567 |        0 |          2,339 |          551 |          124 |         1 |        0 |        1 |  13,087 |
| pydantic           | 2.13.5   | 0.3.7-rc.1+dev |    105 |           2,023 |           438 |        0 |            631 |          190 |           13 |         0 |        0 |        0 |   3,295 |
| pandas             | 3.0.6    | 0.3.7-rc.1+dev |  1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |            2 |         1 |        0 |        1 |  77,931 |
| twisted            | 12.3.0   | 0.3.7-rc.1+dev |    819 |          13,310 |         1,349 |        0 |          3,215 |            0 |            0 |         0 |        0 |        0 |  17,874 |
| pip                | 20.3.4   | 0.3.7-rc.1+dev |    366 |           5,902 |         1,150 |        0 |          1,872 |            0 |            0 |         0 |        0 |        0 |   8,924 |
| structlog          | 26.1.0   | 0.3.7-rc.1+dev |     21 |             156 |            47 |        0 |            113 |           12 |            1 |         0 |        0 |        0 |     329 |
| attrs              | 26.1.0   | 0.3.7-rc.1+dev |     13 |             285 |            50 |        0 |             58 |            2 |            0 |         1 |        0 |        0 |     396 |
| click              | 8.5.0    | 0.3.7-rc.1+dev |     17 |             481 |            58 |        0 |             69 |           28 |            1 |         0 |        0 |        0 |     637 |
| hypercorn          | 0.18.0   | 0.3.7-rc.1+dev |     39 |             220 |            67 |        0 |             68 |            8 |            0 |         0 |        0 |        0 |     363 |
| starlette          | 1.7.0    | 0.3.7-rc.1+dev |     36 |             499 |            99 |        0 |            146 |           18 |            0 |         0 |        0 |        0 |     762 |
| werkzeug           | 3.1.9    | 0.3.7-rc.1+dev |     52 |             835 |           235 |        0 |            223 |           15 |            1 |         0 |        0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | 0.3.7-rc.1+dev |     61 |           1,674 |           198 |        0 |            460 |            8 |            0 |         0 |        0 |        0 |   2,340 |
| httpx              | 0.28.1   | 0.3.7-rc.1+dev |     23 |             395 |           112 |        0 |             62 |            1 |            0 |         0 |        0 |        0 |     570 |
| black              | 26.10.0  | 0.3.7-rc.1+dev |     25 |             996 |           232 |        0 |             45 |            5 |            4 |         0 |        0 |        0 |   1,282 |
| fastapi            | 0.142.2  | 0.3.7-rc.1+dev |     52 |             586 |           105 |        0 |             51 |           98 |            5 |         0 |        0 |        0 |     845 |
| cattrs             | 26.2.1   | 0.3.7-rc.1+dev |     36 |             420 |            70 |        0 |             30 |            9 |            1 |         0 |        0 |        0 |     530 |
| pytest             | 9.1.1    | 0.3.7-rc.1+dev |     78 |           2,363 |           470 |        0 |            170 |           33 |            9 |         0 |        0 |        0 |   3,045 |
| botocore           | 1.43.108 | 0.3.7-rc.1+dev |     76 |           2,825 |           367 |        0 |            594 |            2 |            0 |         0 |        0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | 0.3.7-rc.1+dev |     45 |             363 |            71 |        0 |             55 |           11 |            4 |         0 |        0 |        0 |     504 |
| mcp                | 2.3.0    | 0.3.7-rc.1+dev |    124 |           1,356 |           173 |        0 |            191 |          105 |            8 |         0 |        0 |        0 |   1,833 |
| textual            | 8.2.8    | 0.3.7-rc.1+dev |    247 |           4,979 |           718 |        0 |            786 |           31 |           26 |         0 |        0 |        0 |   6,540 |
| pdm                | 2.29.2   | 0.3.7-rc.1+dev |    128 |           2,114 |           417 |        0 |            187 |           37 |            2 |         0 |        0 |        0 |   2,757 |
| strawberry-graphql | 0.332.0  | 0.3.7-rc.1+dev |    244 |           1,436 |           243 |        0 |            127 |          137 |            2 |         0 |        0 |        0 |   1,945 |
| pygments           | 2.21.0   | 0.3.7-rc.1+dev |    343 |           1,124 |           539 |        0 |          6,003 |            0 |            0 |         0 |        0 |        0 |   7,666 |
| streamlink         | 8.6.1    | 0.3.7-rc.1+dev |    227 |           2,080 |           310 |        0 |            639 |           37 |           11 |         0 |        0 |        0 |   3,077 |
| sphinx             | 9.1.0    | 0.3.7-rc.1+dev |    243 |           5,505 |         1,336 |        1 |          1,131 |           73 |           29 |         5 |        0 |        3 |   8,083 |
| tox                | 4.64.9   | 0.3.7-rc.1+dev |    129 |           1,369 |           286 |        0 |            107 |           18 |            5 |         0 |        0 |        0 |   1,785 |
| pint               | 0.26.1   | 0.3.7-rc.1+dev |    109 |           2,591 |           297 |        0 |            190 |           14 |            2 |         0 |        0 |        0 |   3,094 |
| altair             | 6.3.0    | 0.3.7-rc.1+dev |     55 |             814 |           130 |        0 |            756 |           60 |            8 |         0 |        0 |        0 |   1,768 |
| seaborn            | 0.13.2   | 0.3.7-rc.1+dev |     54 |           2,361 |           370 |        0 |            164 |           23 |            3 |         0 |        0 |        0 |   2,921 |
| aiohttp            | 3.14.4   | 0.3.7-rc.1+dev |     54 |           1,307 |           195 |        0 |            355 |           13 |            5 |         1 |        0 |        0 |   1,876 |
| websockets         | 17.2     | 0.3.7-rc.1+dev |     52 |             605 |            85 |        0 |            101 |            0 |            0 |         0 |        0 |        0 |     791 |
| anyio              | 4.15.1   | 0.3.7-rc.1+dev |     46 |             615 |            77 |        0 |             23 |           26 |            6 |         0 |        0 |        0 |     747 |
| zarr               | 3.4.0    | 0.3.7-rc.1+dev |     98 |           1,874 |           370 |        0 |            167 |           26 |           35 |         0 |        0 |        0 |   2,472 |
| joblib             | 1.6.0    | 0.3.7-rc.1+dev |     73 |           1,842 |           158 |        0 |            239 |            1 |            0 |         0 |        0 |        0 |   2,240 |
| networkx           | 3.7      | 0.3.7-rc.1+dev |    583 |          18,854 |         3,221 |        0 |            381 |            8 |            0 |         0 |        0 |        0 |  22,464 |
| nibabel            | 5.4.2    | 0.3.7-rc.1+dev |    229 |           6,504 |         1,032 |        0 |            932 |            5 |            1 |         0 |        0 |        0 |   8,474 |
| narwhals           | 2.26.0   | 0.3.7-rc.1+dev |    162 |           2,775 |           106 |        0 |            239 |           62 |            5 |         0 |        0 |        0 |   3,187 |
| xarray             | 2026.9.0 | 0.3.7-rc.1+dev |    199 |          18,968 |         1,599 |        0 |            777 |          255 |           20 |         0 |        0 |        0 |  21,619 |
| litestar           | 2.24.0   | 0.3.7-rc.1+dev |    374 |           1,474 |           306 |        0 |            125 |          166 |           12 |         4 |        0 |        0 |   2,087 |
| stripe             | 16.0.0   | 0.3.7-rc.1+dev |  1,460 |           1,772 |            49 |        0 |          1,536 |           16 |          854 |         0 |        0 |        0 |   4,227 |
| celery             | 5.6.3    | 0.3.7-rc.1+dev |    161 |           2,202 |           331 |        0 |          1,215 |            0 |            0 |         2 |        0 |        0 |   3,750 |
| optuna             | 5.0.0    | 0.3.7-rc.1+dev |    220 |           2,740 |           446 |        0 |            412 |           28 |            4 |         0 |        0 |        0 |   3,630 |
| dask               | 2026.8.0 | 0.3.7-rc.1+dev |    361 |          20,748 |         1,691 |        0 |          1,733 |           76 |            5 |         2 |        0 |        1 |  24,256 |
| mypy               | 2.4.0    | 0.3.7-rc.1+dev |    195 |           9,008 |         2,197 |        0 |            196 |          340 |           45 |         0 |        1 |        1 |  11,788 |
| **Total**          |          | 0.3.7-rc.1+dev | 12,461 | 330,707 (78.0%) | 40,646 (9.6%) | 1 (0.0%) | 48,414 (11.4%) | 2,739 (0.6%) | 1,267 (0.3%) | 26 (0.0%) | 1 (0.0%) | 7 (0.0%) | 423,808 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |           Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | -------------- | ----------: | ---------------: | --------------: | ----------: | --------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | 0.3.7-rc.1+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 |  37,329 (32.8%) |   6,433 (5.7%) | 12,373 (10.9%) |      0 |    0 |            0 |
| django             | 0.3.7-rc.1+dev |  0 / 17,170 |   15,002 / 2,168 |      17,170 / 0 |  17,170 / 0 |   2,618 (15.2%) |     630 (3.7%) |  2,701 (15.7%) |      0 |    0 |            0 |
| sqlalchemy         | 0.3.7-rc.1+dev |  0 / 12,411 |   10,843 / 2,244 |    12,411 / 676 |  13,087 / 0 |   1,668 (12.7%) |     320 (2.4%) |     962 (7.4%) |      0 |    0 |            0 |
| pydantic           | 0.3.7-rc.1+dev |   0 / 3,092 |      2,654 / 641 |     3,092 / 203 |   3,295 / 0 |   1,083 (32.9%) |     148 (4.5%) |    409 (12.4%) |      0 |    0 |            0 |
| pandas             | 0.3.7-rc.1+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 |  16,950 (21.8%) | 23,811 (30.6%) | 24,638 (31.6%) |      0 |    0 |            0 |
| twisted            | 0.3.7-rc.1+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |   2,437 (13.6%) |  3,657 (20.5%) |  4,678 (26.2%) |      0 |    0 |            0 |
| pip                | 0.3.7-rc.1+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |   2,253 (25.2%) |     425 (4.8%) |  1,136 (12.7%) |      0 |    0 |            0 |
| structlog          | 0.3.7-rc.1+dev |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |      98 (29.8%) |      15 (4.6%) |      27 (8.2%) |      0 |    0 |            0 |
| attrs              | 0.3.7-rc.1+dev |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |      94 (23.7%) |       9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| click              | 0.3.7-rc.1+dev |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |     285 (44.7%) |      28 (4.4%) |     67 (10.5%) |      0 |    0 |            0 |
| hypercorn          | 0.3.7-rc.1+dev |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |     135 (37.2%) |      20 (5.5%) |     57 (15.7%) |      0 |    0 |            0 |
| starlette          | 0.3.7-rc.1+dev |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |     311 (40.8%) |      56 (7.3%) |     97 (12.7%) |      0 |    0 |            0 |
| werkzeug           | 0.3.7-rc.1+dev |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |     530 (40.5%) |      65 (5.0%) |     128 (9.8%) |      0 |    0 |            0 |
| mkdocs             | 0.3.7-rc.1+dev |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |     811 (34.7%) |    379 (16.2%) |    472 (20.2%) |      0 |    0 |            0 |
| httpx              | 0.3.7-rc.1+dev |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |     235 (41.2%) |     57 (10.0%) |     73 (12.8%) |      0 |    0 |            0 |
| black              | 0.3.7-rc.1+dev |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |     712 (55.5%) |     124 (9.7%) |    163 (12.7%) |      0 |    0 |            0 |
| fastapi            | 0.3.7-rc.1+dev |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |     257 (30.4%) |      40 (4.7%) |      67 (7.9%) |      0 |    0 |            0 |
| cattrs             | 0.3.7-rc.1+dev |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |     106 (20.0%) |      35 (6.6%) |      46 (8.7%) |      0 |    0 |            0 |
| pytest             | 0.3.7-rc.1+dev |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |   1,344 (44.1%) |     160 (5.3%) |     285 (9.4%) |      0 |    0 |            0 |
| botocore           | 0.3.7-rc.1+dev |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |     547 (14.4%) |     166 (4.4%) |    591 (15.6%) |      0 |    0 |            0 |
| uvicorn            | 0.3.7-rc.1+dev |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |     231 (45.8%) |      29 (5.8%) |      43 (8.5%) |      0 |    0 |            0 |
| mcp                | 0.3.7-rc.1+dev |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |     691 (37.7%) |     156 (8.5%) |    235 (12.8%) |      0 |    0 |            0 |
| textual            | 0.3.7-rc.1+dev |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |   2,567 (39.3%) |     478 (7.3%) |    731 (11.2%) |      0 |    0 |            0 |
| pdm                | 0.3.7-rc.1+dev |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |   1,152 (41.8%) |     198 (7.2%) |    313 (11.4%) |      0 |    0 |            0 |
| strawberry-graphql | 0.3.7-rc.1+dev |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |     595 (30.6%) |     165 (8.5%) |    213 (11.0%) |      0 |    0 |            0 |
| pygments           | 0.3.7-rc.1+dev |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |      736 (9.6%) |      80 (1.0%) |     224 (2.9%) |      0 |    0 |            0 |
| streamlink         | 0.3.7-rc.1+dev |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |     674 (21.9%) |     108 (3.5%) |     232 (7.5%) |      0 |    0 |            0 |
| sphinx             | 0.3.7-rc.1+dev |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |   3,136 (38.8%) |     439 (5.4%) |    816 (10.1%) |      0 |    0 |            0 |
| tox                | 0.3.7-rc.1+dev |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |     942 (52.8%) |      79 (4.4%) |     134 (7.5%) |      0 |    0 |            0 |
| pint               | 0.3.7-rc.1+dev |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |     576 (18.6%) |     107 (3.5%) |     160 (5.2%) |      0 |    0 |            0 |
| altair             | 0.3.7-rc.1+dev |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |     373 (21.1%) |      47 (2.7%) |      62 (3.5%) |      0 |    0 |            0 |
| seaborn            | 0.3.7-rc.1+dev |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |     639 (21.9%) |     137 (4.7%) |     229 (7.8%) |      0 |    0 |            0 |
| aiohttp            | 0.3.7-rc.1+dev |   0 / 1,858 |      1,662 / 214 |      1,858 / 18 |   1,876 / 0 |     678 (36.1%) |     141 (7.5%) |    258 (13.8%) |      0 |    0 |            0 |
| websockets         | 0.3.7-rc.1+dev |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |     326 (41.2%) |      59 (7.5%) |    106 (13.4%) |      0 |    0 |            0 |
| anyio              | 0.3.7-rc.1+dev |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |     207 (27.7%) |      32 (4.3%) |      59 (7.9%) |      0 |    0 |            0 |
| zarr               | 0.3.7-rc.1+dev |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |   1,069 (43.2%) |      73 (3.0%) |     113 (4.6%) |      0 |    0 |            0 |
| joblib             | 0.3.7-rc.1+dev |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |     525 (23.4%) |     177 (7.9%) |    246 (11.0%) |      0 |    0 |            0 |
| networkx           | 0.3.7-rc.1+dev |  0 / 22,456 |   19,235 / 3,229 |      22,456 / 8 |  22,464 / 0 |   3,939 (17.5%) |   2,160 (9.6%) |  2,466 (11.0%) |      0 |    0 |            0 |
| nibabel            | 0.3.7-rc.1+dev |   0 / 8,468 |    7,436 / 1,038 |       8,468 / 6 |   8,474 / 0 |   1,850 (21.8%) |     681 (8.0%) |    939 (11.1%) |      0 |    0 |            0 |
| narwhals           | 0.3.7-rc.1+dev |   0 / 3,120 |      3,014 / 173 |      3,120 / 67 |   3,187 / 0 |     973 (30.5%) |      68 (2.1%) |     123 (3.9%) |      0 |    0 |            0 |
| xarray             | 0.3.7-rc.1+dev |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |   3,544 (16.4%) |  3,144 (14.5%) |  3,353 (15.5%) |      0 |    0 |            0 |
| litestar           | 0.3.7-rc.1+dev |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |     595 (28.5%) |     103 (4.9%) |     165 (7.9%) |      0 |    0 |            0 |
| stripe             | 0.3.7-rc.1+dev |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |     565 (13.4%) |     161 (3.8%) |    663 (15.7%) |      0 |    0 |            0 |
| celery             | 0.3.7-rc.1+dev |   0 / 3,750 |      3,417 / 333 |       3,750 / 0 |   3,750 / 0 |     503 (13.4%) |     120 (3.2%) |     367 (9.8%) |      0 |    0 |            0 |
| optuna             | 0.3.7-rc.1+dev |   0 / 3,598 |      3,152 / 478 |      3,598 / 32 |   3,630 / 0 |   1,473 (40.6%) |     201 (5.5%) |     306 (8.4%) |      0 |    0 |            0 |
| dask               | 0.3.7-rc.1+dev |  0 / 24,174 |   22,481 / 1,775 |     24,174 / 82 |  24,256 / 0 |   3,117 (12.9%) |   1,985 (8.2%) |  2,678 (11.0%) |      0 |    0 |            0 |
| mypy               | 0.3.7-rc.1+dev |  0 / 11,401 |    9,204 / 2,583 |    11,401 / 387 |  11,788 / 0 |   4,738 (40.2%) |  1,175 (10.0%) |  1,562 (13.3%) |      0 |    0 |            0 |
| **Total**          | 0.3.7-rc.1+dev | 0 / 419,794 | 379,121 / 44,686 | 419,793 / 4,015 | 423,808 / 0 | 106,217 (25.1%) | 48,881 (11.5%) | 65,777 (15.5%) |      0 |    0 |            0 |

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
| pint               | 0.3.7-rc.1+dev |              5.1% |         22.8% |            26.1% |                  27.8% | +17.8 pts, 18.7% of untyped | +22.7 pts, 23.9% of untyped |
| altair             | 0.3.7-rc.1+dev |             49.7% |         60.7% |            62.1% |                  62.6% | +11.0 pts, 21.9% of untyped | +12.9 pts, 25.6% of untyped |
| seaborn            | 0.3.7-rc.1+dev |              6.9% |         27.5% |            31.9% |                  34.8% | +20.5 pts, 22.1% of untyped | +27.9 pts, 30.0% of untyped |
| aiohttp            | 0.3.7-rc.1+dev |             23.7% |         51.5% |            57.3% |                  62.1% | +27.9 pts, 36.5% of untyped | +38.5 pts, 50.4% of untyped |
| websockets         | 0.3.7-rc.1+dev |             13.8% |         49.3% |            55.8% |                  60.9% | +35.5 pts, 41.2% of untyped | +47.1 pts, 54.6% of untyped |
| anyio              | 0.3.7-rc.1+dev |             27.8% |         48.7% |            51.9% |                  54.6% | +20.9 pts, 29.0% of untyped | +26.9 pts, 37.2% of untyped |
| zarr               | 0.3.7-rc.1+dev |             21.7% |         56.4% |            58.8% |                  60.1% | +34.7 pts, 44.3% of untyped | +38.4 pts, 49.0% of untyped |
| joblib             | 0.3.7-rc.1+dev |              0.0% |         23.5% |            31.4% |                  34.4% | +23.4 pts, 23.4% of untyped | +34.4 pts, 34.4% of untyped |
| networkx           | 0.3.7-rc.1+dev |              0.3% |         17.8% |            27.4% |                  28.7% | +17.5 pts, 17.5% of untyped | +28.4 pts, 28.5% of untyped |
| nibabel            | 0.3.7-rc.1+dev |              1.0% |         22.6% |            30.6% |                  33.6% | +21.6 pts, 21.8% of untyped | +32.6 pts, 32.9% of untyped |
| narwhals           | 0.3.7-rc.1+dev |             21.7% |         46.1% |            47.8% |                  49.2% | +24.4 pts, 31.2% of untyped | +27.5 pts, 35.1% of untyped |
| xarray             | 0.3.7-rc.1+dev |              4.6% |         20.4% |            34.5% |                  35.4% | +15.8 pts, 16.6% of untyped | +30.8 pts, 32.3% of untyped |
| litestar           | 0.3.7-rc.1+dev |             44.9% |         62.1% |            65.1% |                  66.9% | +17.2 pts, 31.2% of untyped | +22.0 pts, 39.9% of untyped |
| stripe             | 0.3.7-rc.1+dev |             89.5% |         91.3% |            91.8% |                  93.4% |  +1.8 pts, 16.8% of untyped |  +3.8 pts, 36.6% of untyped |
| celery             | 0.3.7-rc.1+dev |              0.4% |         13.8% |            17.0% |                  23.5% | +13.4 pts, 13.4% of untyped | +23.1 pts, 23.2% of untyped |
| optuna             | 0.3.7-rc.1+dev |              7.5% |         45.4% |            50.5% |                  53.2% | +37.9 pts, 40.9% of untyped | +45.7 pts, 49.4% of untyped |
| dask               | 0.3.7-rc.1+dev |              1.1% |         13.8% |            21.9% |                  24.8% | +12.8 pts, 12.9% of untyped | +23.7 pts, 24.0% of untyped |
| mypy               | 0.3.7-rc.1+dev |             16.8% |         51.4% |            59.9% |                  62.8% | +34.6 pts, 41.6% of untyped | +46.0 pts, 55.2% of untyped |
| **Total**          | 0.3.7-rc.1+dev |             11.3% |         33.8% |            44.1% |                  47.7% | +22.4 pts, 25.3% of untyped | +36.3 pts, 41.0% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,329 |  37,329 |        |        |      0 |    0 | 38,658 |  115,001 |    38.7 |
| standard library   | likely             | 43,762 |  37,543 |  6,219 |        |      0 |    0 | 45,091 |  115,001 |    72.8 |
| standard library   | unsafe             | 49,702 |  37,337 |  6,211 |  6,154 |      0 |    0 | 51,031 |  115,001 |    75.8 |
| standard library   | infer-basedpyright | 58,068 |  37,345 |  6,715 | 14,008 |      0 |    9 | 59,397 |  115,001 |   938.6 |
| standard library   | infer-ty           | 55,832 |  37,346 |  6,681 | 11,805 |      0 |   39 | 57,161 |  115,001 |   127.1 |
| standard library   | infer-pyrefly      | 58,455 |  37,345 |  6,849 | 14,261 |      0 |   37 | 59,784 |  115,001 |   141.6 |
| django             | certain            |  2,618 |   2,618 |        |        |      0 |    0 |  2,620 |   17,171 |    19.8 |
| django             | likely             |  3,248 |   2,621 |    627 |        |      0 |    0 |  3,250 |   17,171 |    24.4 |
| django             | unsafe             |  5,319 |   2,618 |    626 |  2,075 |      0 |    0 |  5,321 |   17,171 |    10.5 |
| django             | infer-basedpyright |  5,776 |   2,617 |    642 |  2,517 |      0 |    6 |  5,778 |   17,171 |    48.2 |
| django             | infer-ty           |  5,561 |   2,619 |    637 |  2,305 |      0 |    4 |  5,563 |   17,171 |    64.8 |
| django             | infer-pyrefly      |  6,034 |   2,609 |    648 |  2,777 |      0 |   36 |  6,036 |   17,171 |    17.7 |
| django             | infer-trace        |  5,859 |   2,622 |    660 |  2,577 |      0 |    0 |  5,861 |   17,171 |    14.2 |
| sqlalchemy         | certain            |  1,668 |   1,668 |        |        |      0 |    0 |  3,817 |   14,568 |     7.2 |
| sqlalchemy         | likely             |  1,988 |   1,675 |    313 |        |      0 |    0 |  4,137 |   14,568 |    19.7 |
| sqlalchemy         | unsafe             |  2,630 |   1,668 |    312 |    650 |      0 |    0 |  4,779 |   14,568 |    13.8 |
| sqlalchemy         | infer-basedpyright |  3,509 |   1,669 |    356 |  1,484 |      0 |    0 |  5,658 |   14,568 |    46.4 |
| sqlalchemy         | infer-ty           |  3,446 |   1,669 |    342 |  1,435 |      0 |    4 |  5,595 |   14,568 |    20.8 |
| sqlalchemy         | infer-pyrefly      |  3,110 |   1,668 |    332 |  1,110 |      0 |    0 |  5,259 |   14,568 |    20.7 |
| sqlalchemy         | infer-trace        |  2,809 |   1,668 |    312 |    829 |      0 |    0 |  4,958 |   14,568 |     6.3 |
| pydantic           | certain            |  1,083 |   1,083 |        |        |      0 |    0 |  1,947 |    3,956 |     1.8 |
| pydantic           | likely             |  1,231 |   1,091 |    140 |        |      0 |    0 |  2,095 |    3,956 |     5.3 |
| pydantic           | unsafe             |  1,492 |   1,083 |    139 |    270 |      0 |    0 |  2,356 |    3,956 |     2.0 |
| pydantic           | infer-basedpyright |  1,788 |   1,084 |    143 |    561 |      0 |    0 |  2,652 |    3,956 |    23.3 |
| pydantic           | infer-ty           |  1,669 |   1,084 |    140 |    445 |      0 |    0 |  2,533 |    3,956 |     6.8 |
| pydantic           | infer-pyrefly      |  1,687 |   1,083 |    141 |    463 |      0 |    0 |  2,551 |    3,956 |     4.1 |
| pydantic           | infer-trace        |  1,493 |   1,083 |    139 |    271 |      0 |    0 |  2,357 |    3,956 |     2.4 |
| pandas             | certain            | 16,950 |  16,950 |        |        |      0 |    0 | 18,219 |   79,062 |    39.5 |
| pandas             | likely             | 40,761 |  17,133 | 23,628 |        |      0 |    0 | 42,030 |   79,062 |   132.9 |
| pandas             | unsafe             | 41,588 |  16,946 | 23,409 |  1,233 |      0 |    0 | 42,857 |   79,062 |    63.7 |
| pandas             | infer-basedpyright | 47,315 |  16,938 | 23,430 |  6,947 |      0 |   21 | 48,584 |   79,062 |   412.2 |
| pandas             | infer-ty           | 46,441 |  16,946 | 23,466 |  6,029 |      0 |    2 | 47,710 |   79,062 |   149.2 |
| pandas             | infer-pyrefly      | 48,328 |  16,949 | 23,472 |  7,907 |      0 |    9 | 49,597 |   79,062 |   109.4 |
| pandas             | infer-trace        | 42,994 |  16,946 | 23,370 |  2,678 |      0 |    9 | 44,263 |   79,062 |    42.2 |
| twisted            | certain            |  2,437 |   2,437 |        |        |      0 |    0 |  2,437 |   17,874 |     4.0 |
| twisted            | likely             |  6,094 |   2,561 |  3,533 |        |      0 |    0 |  6,094 |   17,874 |     9.5 |
| twisted            | unsafe             |  7,115 |   2,436 |  3,533 |  1,146 |      0 |    0 |  7,115 |   17,874 |     6.3 |
| twisted            | infer-basedpyright |  8,551 |   2,441 |  3,563 |  2,547 |      0 |   10 |  8,551 |   17,874 |    48.7 |
| twisted            | infer-ty           |  7,547 |   2,436 |  3,576 |  1,535 |      0 |    0 |  7,547 |   17,874 |    32.4 |
| twisted            | infer-pyrefly      |  7,570 |   2,436 |  3,566 |  1,568 |      0 |    0 |  7,570 |   17,874 |    16.5 |
| pip                | certain            |  2,253 |   2,253 |        |        |      0 |    0 |  2,390 |    9,064 |     4.2 |
| pip                | likely             |  2,678 |   2,266 |    412 |        |      0 |    0 |  2,815 |    9,064 |     5.8 |
| pip                | unsafe             |  3,389 |   2,253 |    412 |    724 |      0 |    0 |  3,526 |    9,064 |     3.5 |
| pip                | infer-basedpyright |  4,185 |   2,258 |    466 |  1,461 |      0 |    6 |  4,322 |    9,064 |    31.3 |
| pip                | infer-ty           |  3,719 |   2,255 |    436 |  1,028 |      0 |    4 |  3,856 |    9,064 |    17.7 |
| pip                | infer-pyrefly      |  3,939 |   2,255 |    450 |  1,234 |      0 |    0 |  4,076 |    9,064 |     8.3 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.6 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.5 |
| structlog          | unsafe             |    125 |      98 |     15 |     12 |      0 |    0 |    234 |      425 |     1.4 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     3.1 |
| structlog          | infer-ty           |    136 |      98 |     16 |     22 |      0 |    0 |    245 |      425 |     1.7 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     1.1 |
| structlog          | infer-trace        |    125 |      98 |     15 |     12 |      0 |    0 |    234 |      425 |     1.0 |
| attrs              | certain            |     94 |      94 |        |        |      0 |    0 |     97 |      396 |     1.0 |
| attrs              | likely             |    103 |      95 |      8 |        |      0 |    0 |    106 |      396 |     1.1 |
| attrs              | unsafe             |    105 |      94 |      8 |      3 |      0 |    0 |    108 |      396 |     2.5 |
| attrs              | infer-basedpyright |    132 |      94 |      8 |     30 |      0 |    0 |    135 |      396 |     4.8 |
| attrs              | infer-ty           |    116 |      94 |      8 |     14 |      0 |    0 |    119 |      396 |     1.9 |
| attrs              | infer-pyrefly      |    121 |      94 |      8 |     19 |      0 |    0 |    124 |      396 |     1.9 |
| attrs              | infer-trace        |    108 |      94 |      9 |      5 |      0 |    0 |    111 |      396 |     1.0 |
| click              | certain            |    285 |     285 |        |        |      0 |    0 |    564 |      887 |     0.6 |
| click              | likely             |    313 |     286 |     27 |        |      0 |    0 |    592 |      887 |     0.8 |
| click              | unsafe             |    352 |     285 |     27 |     40 |      0 |    0 |    631 |      887 |     1.0 |
| click              | infer-basedpyright |    434 |     286 |     30 |    118 |      0 |    0 |    713 |      887 |     9.6 |
| click              | infer-ty           |    449 |     286 |     25 |    138 |      0 |    0 |    728 |      887 |     2.9 |
| click              | infer-pyrefly      |    439 |     285 |     32 |    122 |      0 |    0 |    718 |      887 |     2.0 |
| click              | infer-trace        |    352 |     285 |     27 |     40 |      0 |    0 |    631 |      887 |     1.2 |
| hypercorn          | certain            |    135 |     135 |        |        |      0 |    0 |    305 |      525 |     0.6 |
| hypercorn          | likely             |    155 |     135 |     20 |        |      0 |    0 |    325 |      525 |     0.7 |
| hypercorn          | unsafe             |    192 |     135 |     20 |     37 |      0 |    0 |    362 |      525 |     0.7 |
| hypercorn          | infer-basedpyright |    214 |     135 |     21 |     58 |      0 |    0 |    384 |      525 |     3.3 |
| hypercorn          | infer-ty           |    229 |     135 |     21 |     73 |      0 |    0 |    399 |      525 |     2.7 |
| hypercorn          | infer-pyrefly      |    201 |     135 |     20 |     46 |      0 |    0 |    371 |      525 |     1.5 |
| hypercorn          | infer-trace        |    192 |     135 |     20 |     37 |      0 |    0 |    362 |      525 |     0.8 |
| starlette          | certain            |    311 |     311 |        |        |      0 |    0 |    396 |      829 |     0.6 |
| starlette          | likely             |    367 |     311 |     56 |        |      0 |    0 |    452 |      829 |     0.8 |
| starlette          | unsafe             |    408 |     311 |     56 |     41 |      0 |    0 |    493 |      829 |     0.8 |
| starlette          | infer-basedpyright |    487 |     311 |     56 |    120 |      0 |    0 |    572 |      829 |     3.3 |
| starlette          | infer-ty           |    491 |     311 |     55 |    125 |      0 |    0 |    576 |      829 |     1.4 |
| starlette          | infer-pyrefly      |    445 |     311 |     55 |     79 |      0 |    0 |    530 |      829 |     1.6 |
| starlette          | infer-trace        |    408 |     311 |     56 |     41 |      0 |    0 |    493 |      829 |     1.0 |
| werkzeug           | certain            |    530 |     530 |        |        |      0 |    0 |    746 |    1,509 |     1.1 |
| werkzeug           | likely             |    595 |     531 |     64 |        |      0 |    0 |    811 |    1,509 |     1.4 |
| werkzeug           | unsafe             |    658 |     530 |     64 |     64 |      0 |    0 |    874 |    1,509 |     0.9 |
| werkzeug           | infer-basedpyright |    780 |     530 |     76 |    174 |      0 |    0 |    996 |    1,509 |     4.3 |
| werkzeug           | infer-ty           |    802 |     530 |     79 |    193 |      0 |    0 |  1,018 |    1,509 |     2.6 |
| werkzeug           | infer-pyrefly      |    811 |     530 |     69 |    212 |      0 |    0 |  1,027 |    1,509 |     2.4 |
| werkzeug           | infer-trace        |    658 |     530 |     64 |     64 |      0 |    0 |    874 |    1,509 |     1.6 |
| mkdocs             | certain            |    811 |     811 |        |        |      0 |    0 |    922 |    2,443 |     1.6 |
| mkdocs             | likely             |  1,190 |     841 |    349 |        |      0 |    0 |  1,301 |    2,443 |     1.7 |
| mkdocs             | unsafe             |  1,283 |     811 |    349 |    123 |      0 |    0 |  1,394 |    2,443 |     1.3 |
| mkdocs             | infer-basedpyright |  1,386 |     811 |    356 |    219 |      0 |    0 |  1,497 |    2,443 |     9.7 |
| mkdocs             | infer-ty           |  1,422 |     811 |    361 |    250 |      0 |    0 |  1,533 |    2,443 |     8.8 |
| mkdocs             | infer-pyrefly      |  1,458 |     811 |    357 |    290 |      0 |    0 |  1,569 |    2,443 |     3.2 |
| mkdocs             | infer-trace        |  1,295 |     812 |    348 |    135 |      0 |    0 |  1,406 |    2,443 |     2.0 |
| httpx              | certain            |    235 |     235 |        |        |      0 |    0 |    273 |      607 |     0.5 |
| httpx              | likely             |    292 |     244 |     48 |        |      0 |    0 |    330 |      607 |     1.1 |
| httpx              | unsafe             |    308 |     235 |     48 |     25 |      0 |    0 |    346 |      607 |     0.8 |
| httpx              | infer-basedpyright |    409 |     235 |     53 |    121 |      0 |    0 |    447 |      607 |     6.0 |
| httpx              | infer-ty           |    381 |     235 |     52 |     94 |      0 |    0 |    419 |      607 |     2.6 |
| httpx              | infer-pyrefly      |    354 |     235 |     51 |     68 |      0 |    0 |    392 |      607 |     2.0 |
| httpx              | infer-trace        |    308 |     235 |     48 |     25 |      0 |    0 |    346 |      607 |     0.9 |
| black              | certain            |    712 |     712 |        |        |      0 |    0 |    952 |    1,513 |     0.7 |
| black              | likely             |    836 |     725 |    111 |        |      0 |    0 |  1,076 |    1,513 |     0.9 |
| black              | unsafe             |    875 |     712 |    111 |     52 |      0 |    0 |  1,115 |    1,513 |     0.7 |
| black              | infer-basedpyright |    946 |     712 |    110 |    124 |      0 |    0 |  1,186 |    1,513 |     7.4 |
| black              | infer-ty           |  1,068 |     712 |    115 |    241 |      0 |    0 |  1,308 |    1,513 |     3.3 |
| black              | infer-pyrefly      |    917 |     712 |    110 |     95 |      0 |    0 |  1,157 |    1,513 |     1.5 |
| black              | infer-trace        |    875 |     712 |    111 |     52 |      0 |    0 |  1,115 |    1,513 |     1.3 |
| fastapi            | certain            |    257 |     257 |        |        |      0 |    0 |    794 |    1,279 |     1.5 |
| fastapi            | likely             |    297 |     263 |     34 |        |      0 |    0 |    834 |    1,279 |     2.4 |
| fastapi            | unsafe             |    324 |     257 |     34 |     33 |      0 |    0 |    861 |    1,279 |     1.5 |
| fastapi            | infer-basedpyright |    350 |     257 |     33 |     60 |      0 |    0 |    887 |    1,279 |     6.3 |
| fastapi            | infer-ty           |    372 |     257 |     32 |     83 |      0 |    0 |    909 |    1,279 |     4.0 |
| fastapi            | infer-pyrefly      |    346 |     257 |     34 |     55 |      0 |    0 |    883 |    1,279 |     2.9 |
| fastapi            | infer-trace        |    324 |     257 |     34 |     33 |      0 |    0 |    861 |    1,279 |     1.3 |
| cattrs             | certain            |    106 |     106 |        |        |      0 |    0 |    145 |      559 |     0.6 |
| cattrs             | likely             |    141 |     113 |     28 |        |      0 |    0 |    180 |      559 |     1.1 |
| cattrs             | unsafe             |    152 |     109 |     27 |     16 |      0 |    0 |    191 |      559 |     1.0 |
| cattrs             | infer-basedpyright |    196 |     108 |     30 |     58 |      0 |    0 |    235 |      559 |     4.7 |
| cattrs             | infer-ty           |    190 |     106 |     28 |     56 |      0 |    0 |    229 |      559 |     3.5 |
| cattrs             | infer-pyrefly      |    183 |     106 |     29 |     48 |      0 |    0 |    222 |      559 |     1.8 |
| cattrs             | infer-trace        |    152 |     109 |     27 |     16 |      0 |    0 |    191 |      559 |     0.9 |
| pytest             | certain            |  1,344 |   1,344 |        |        |      0 |    0 |  1,759 |    3,418 |     1.8 |
| pytest             | likely             |  1,504 |   1,348 |    156 |        |      0 |    0 |  1,919 |    3,418 |     2.9 |
| pytest             | unsafe             |  1,629 |   1,344 |    156 |    129 |      0 |    0 |  2,044 |    3,418 |     1.8 |
| pytest             | infer-basedpyright |  1,982 |   1,343 |    174 |    465 |      0 |    0 |  2,397 |    3,418 |    12.9 |
| pytest             | infer-ty           |  1,988 |   1,343 |    176 |    469 |      0 |    0 |  2,403 |    3,418 |     5.4 |
| pytest             | infer-pyrefly      |  2,056 |   1,343 |    177 |    536 |      0 |    0 |  2,471 |    3,418 |     6.5 |
| pytest             | infer-trace        |  1,647 |   1,344 |    156 |    147 |      0 |    0 |  2,062 |    3,418 |     1.7 |
| botocore           | certain            |    547 |     547 |        |        |      0 |    0 |    565 |    3,806 |     5.5 |
| botocore           | likely             |    713 |     553 |    160 |        |      0 |    0 |    731 |    3,806 |     3.0 |
| botocore           | unsafe             |  1,138 |     545 |    160 |    433 |      0 |    0 |  1,156 |    3,806 |     6.6 |
| botocore           | infer-basedpyright |  1,293 |     540 |    163 |    590 |      0 |    0 |  1,311 |    3,806 |    11.2 |
| botocore           | infer-ty           |  1,200 |     545 |    161 |    494 |      0 |    3 |  1,218 |    3,806 |     5.8 |
| botocore           | infer-pyrefly      |  1,280 |     540 |    166 |    574 |      0 |    0 |  1,298 |    3,806 |     3.5 |
| botocore           | infer-trace        |  1,483 |     545 |    188 |    750 |      0 |    0 |  1,501 |    3,806 |     2.1 |
| uvicorn            | certain            |    231 |     231 |        |        |      0 |    0 |    382 |      640 |     0.8 |
| uvicorn            | likely             |    260 |     231 |     29 |        |      0 |    0 |    411 |      640 |     0.8 |
| uvicorn            | unsafe             |    274 |     231 |     29 |     14 |      0 |    0 |    425 |      640 |     1.0 |
| uvicorn            | infer-basedpyright |    347 |     231 |     32 |     84 |      0 |    0 |    498 |      640 |     6.2 |
| uvicorn            | infer-ty           |    354 |     232 |     29 |     93 |      0 |    0 |    505 |      640 |     2.0 |
| uvicorn            | infer-pyrefly      |    302 |     231 |     34 |     37 |      0 |    0 |    453 |      640 |     2.4 |
| uvicorn            | infer-trace        |    274 |     231 |     29 |     14 |      0 |    0 |    425 |      640 |     1.1 |
| mcp                | certain            |    691 |     691 |        |        |      0 |    0 |  1,454 |    2,483 |     1.4 |
| mcp                | likely             |    847 |     697 |    150 |        |      0 |    0 |  1,610 |    2,483 |     1.7 |
| mcp                | unsafe             |    926 |     691 |    150 |     85 |      0 |    0 |  1,689 |    2,483 |     3.7 |
| mcp                | infer-basedpyright |  1,057 |     691 |    162 |    204 |      0 |    0 |  1,820 |    2,483 |     7.2 |
| mcp                | infer-ty           |  1,160 |     692 |    158 |    310 |      0 |    0 |  1,923 |    2,483 |     7.4 |
| mcp                | infer-pyrefly      |  1,015 |     691 |    155 |    169 |      0 |    0 |  1,778 |    2,483 |     3.2 |
| mcp                | infer-trace        |    926 |     691 |    150 |     85 |      0 |    0 |  1,689 |    2,483 |     1.2 |
| textual            | certain            |  2,567 |   2,567 |        |        |      0 |    0 |  3,761 |    7,677 |     2.8 |
| textual            | likely             |  3,045 |   2,596 |    449 |        |      0 |    0 |  4,239 |    7,677 |     4.1 |
| textual            | unsafe             |  3,298 |   2,567 |    448 |    283 |      0 |    0 |  4,492 |    7,677 |     2.1 |
| textual            | infer-basedpyright |  4,557 |   2,568 |    522 |  1,467 |      0 |   20 |  5,751 |    7,677 |    33.3 |
| textual            | infer-ty           |  4,641 |   2,568 |    529 |  1,544 |      0 |    0 |  5,835 |    7,677 |    11.3 |
| textual            | infer-pyrefly      |  3,763 |   2,568 |    470 |    725 |      0 |    0 |  4,957 |    7,677 |     5.4 |
| pdm                | certain            |  1,152 |   1,152 |        |        |      0 |    0 |  1,513 |    3,079 |     1.7 |
| pdm                | likely             |  1,350 |   1,165 |    185 |        |      0 |    0 |  1,711 |    3,079 |     3.2 |
| pdm                | unsafe             |  1,465 |   1,152 |    184 |    129 |      0 |    0 |  1,826 |    3,079 |     2.5 |
| pdm                | infer-basedpyright |  1,857 |   1,156 |    213 |    488 |      0 |    0 |  2,218 |    3,079 |     8.7 |
| pdm                | infer-ty           |  1,960 |   1,158 |    211 |    591 |      0 |    0 |  2,321 |    3,079 |     5.1 |
| pdm                | infer-pyrefly      |  1,640 |   1,153 |    194 |    293 |      0 |    0 |  2,001 |    3,079 |     4.0 |
| pdm                | infer-trace        |  1,465 |   1,152 |    184 |    129 |      0 |    0 |  1,826 |    3,079 |     1.9 |
| strawberry-graphql | certain            |    595 |     595 |        |        |      0 |    0 |  1,371 |    2,582 |     2.3 |
| strawberry-graphql | likely             |    760 |     597 |    163 |        |      0 |    0 |  1,536 |    2,582 |     2.8 |
| strawberry-graphql | unsafe             |    808 |     595 |    163 |     50 |      0 |    0 |  1,584 |    2,582 |     1.8 |
| strawberry-graphql | infer-basedpyright |    983 |     594 |    163 |    226 |      0 |    0 |  1,759 |    2,582 |     7.2 |
| strawberry-graphql | infer-ty           |  1,022 |     595 |    163 |    264 |      0 |    0 |  1,798 |    2,582 |     6.4 |
| strawberry-graphql | infer-pyrefly      |    872 |     594 |    164 |    114 |      0 |    0 |  1,648 |    2,582 |     4.1 |
| strawberry-graphql | infer-trace        |    808 |     595 |    163 |     50 |      0 |    0 |  1,584 |    2,582 |     1.2 |
| pygments           | certain            |    736 |     736 |        |        |      0 |    0 |    736 |    7,666 |     5.2 |
| pygments           | likely             |    816 |     739 |     77 |        |      0 |    0 |    816 |    7,666 |     2.7 |
| pygments           | unsafe             |    960 |     736 |     77 |    147 |      0 |    0 |    960 |    7,666 |     5.0 |
| pygments           | infer-basedpyright |  1,074 |     736 |     84 |    254 |      0 |    0 |  1,074 |    7,666 |    21.1 |
| pygments           | infer-ty           |  1,078 |     736 |     85 |    257 |      0 |    0 |  1,078 |    7,666 |     9.4 |
| pygments           | infer-pyrefly      |  1,139 |     736 |     85 |    318 |      0 |    2 |  1,139 |    7,666 |     6.2 |
| pygments           | infer-trace        |  1,072 |     731 |    101 |    240 |      0 |    0 |  1,072 |    7,666 |     3.5 |
| streamlink         | certain            |    674 |     674 |        |        |      0 |    0 |  2,936 |    5,291 |     2.8 |
| streamlink         | likely             |    782 |     677 |    105 |        |      0 |    0 |  3,044 |    5,291 |     2.2 |
| streamlink         | unsafe             |    906 |     674 |    105 |    127 |      0 |    0 |  3,168 |    5,291 |     2.2 |
| streamlink         | infer-basedpyright |  1,317 |     674 |    127 |    516 |      0 |    0 |  3,579 |    5,291 |     7.6 |
| streamlink         | infer-ty           |  1,469 |     674 |    138 |    657 |      0 |    0 |  3,731 |    5,291 |     9.6 |
| streamlink         | infer-pyrefly      |  1,097 |     674 |    118 |    305 |      0 |    0 |  3,359 |    5,291 |     4.5 |
| streamlink         | infer-trace        |    914 |     674 |    105 |    135 |      0 |    0 |  3,176 |    5,291 |     3.4 |
| sphinx             | certain            |  3,136 |   3,136 |        |        |      0 |    0 |  4,064 |    8,901 |     3.0 |
| sphinx             | likely             |  3,575 |   3,146 |    429 |        |      0 |    0 |  4,503 |    8,901 |     4.8 |
| sphinx             | unsafe             |  3,952 |   3,136 |    426 |    390 |      0 |    0 |  4,880 |    8,901 |     3.6 |
| sphinx             | infer-basedpyright |  4,735 |   3,141 |    455 |  1,139 |      0 |    0 |  5,663 |    8,901 |    20.0 |
| sphinx             | infer-ty           |  4,881 |   3,140 |    457 |  1,284 |      0 |    2 |  5,809 |    8,901 |    14.6 |
| sphinx             | infer-pyrefly      |  5,096 |   3,141 |    471 |  1,484 |      0 |    2 |  6,024 |    8,901 |     7.6 |
| sphinx             | infer-trace        |  3,952 |   3,136 |    426 |    390 |      0 |    0 |  4,880 |    8,901 |     3.3 |
| tox                | certain            |    942 |     942 |        |        |      0 |    0 |  1,278 |    2,098 |     1.6 |
| tox                | likely             |  1,021 |     943 |     78 |        |      0 |    0 |  1,357 |    2,098 |     2.5 |
| tox                | unsafe             |  1,076 |     942 |     78 |     56 |      0 |    0 |  1,412 |    2,098 |     1.8 |
| tox                | infer-basedpyright |  1,338 |     944 |     95 |    299 |      0 |    3 |  1,674 |    2,098 |     7.5 |
| tox                | infer-ty           |  1,375 |     944 |     95 |    336 |      0 |    0 |  1,711 |    2,098 |     4.5 |
| tox                | infer-pyrefly      |  1,425 |     944 |     95 |    386 |      0 |    0 |  1,761 |    2,098 |     3.3 |
| tox                | infer-trace        |  1,076 |     942 |     78 |     56 |      0 |    0 |  1,412 |    2,098 |     1.0 |
| pint               | certain            |    576 |     576 |        |        |      0 |    0 |    741 |    3,243 |     2.4 |
| pint               | likely             |    683 |     582 |    101 |        |      0 |    0 |    848 |    3,243 |     3.9 |
| pint               | unsafe             |    736 |     576 |    101 |     59 |      0 |    0 |    901 |    3,243 |     1.7 |
| pint               | infer-basedpyright |  1,018 |     574 |    105 |    339 |      0 |   12 |  1,183 |    3,243 |    33.7 |
| pint               | infer-ty           |    915 |     574 |     98 |    243 |      0 |    0 |  1,080 |    3,243 |    11.1 |
| pint               | infer-pyrefly      |    820 |     572 |     95 |    153 |      0 |    0 |    985 |    3,243 |     4.3 |
| pint               | infer-trace        |    748 |     576 |    101 |     71 |      0 |    0 |    913 |    3,243 |     3.0 |
| altair             | certain            |    373 |     373 |        |        |      0 |    0 |  2,055 |    3,383 |     3.2 |
| altair             | likely             |    420 |     373 |     47 |        |      0 |    0 |  2,102 |    3,383 |     4.3 |
| altair             | unsafe             |    435 |     373 |     47 |     15 |      0 |    0 |  2,117 |    3,383 |     4.5 |
| altair             | infer-basedpyright |    506 |     370 |     51 |     85 |      0 |    0 |  2,188 |    3,383 |    17.2 |
| altair             | infer-ty           |    501 |     370 |     48 |     83 |      0 |    3 |  2,183 |    3,383 |     8.9 |
| altair             | infer-pyrefly      |    495 |     370 |     48 |     77 |      0 |    0 |  2,177 |    3,383 |     6.7 |
| altair             | infer-trace        |    442 |     373 |     48 |     21 |      0 |    0 |  2,124 |    3,383 |     3.0 |
| seaborn            | certain            |    639 |     639 |        |        |      0 |    0 |    854 |    3,110 |     2.4 |
| seaborn            | likely             |    776 |     647 |    129 |        |      0 |    0 |    991 |    3,110 |     2.8 |
| seaborn            | unsafe             |    868 |     639 |    129 |    100 |      0 |    0 |  1,083 |    3,110 |     5.3 |
| seaborn            | infer-basedpyright |  1,012 |     639 |    132 |    241 |      0 |    4 |  1,227 |    3,110 |    30.2 |
| seaborn            | infer-ty           |    953 |     638 |    131 |    184 |      0 |    0 |  1,168 |    3,110 |     9.4 |
| seaborn            | infer-pyrefly      |  1,041 |     639 |    133 |    269 |      0 |    0 |  1,256 |    3,110 |    10.7 |
| seaborn            | infer-trace        |    908 |     639 |    131 |    138 |      0 |    0 |  1,123 |    3,110 |     2.1 |
| aiohttp            | certain            |    678 |     678 |        |        |      0 |    0 |  1,254 |    2,433 |     1.3 |
| aiohttp            | likely             |    819 |     684 |    135 |        |      0 |    0 |  1,395 |    2,433 |     2.2 |
| aiohttp            | unsafe             |    936 |     678 |    135 |    123 |      0 |    0 |  1,512 |    2,433 |     3.4 |
| aiohttp            | infer-basedpyright |  1,136 |     681 |    143 |    312 |      0 |    0 |  1,712 |    2,433 |    18.6 |
| aiohttp            | infer-ty           |  1,240 |     681 |    147 |    412 |      0 |    0 |  1,816 |    2,433 |     6.3 |
| aiohttp            | infer-pyrefly      |  1,268 |     681 |    148 |    439 |      0 |    0 |  1,844 |    2,433 |     4.3 |
| aiohttp            | infer-trace        |    937 |     678 |    135 |    124 |      0 |    0 |  1,513 |    2,433 |     1.5 |
| websockets         | certain            |    326 |     326 |        |        |      0 |    0 |    453 |      918 |     0.7 |
| websockets         | likely             |    385 |     327 |     58 |        |      0 |    0 |    512 |      918 |     1.0 |
| websockets         | unsafe             |    432 |     326 |     58 |     48 |      0 |    0 |    559 |      918 |     3.4 |
| websockets         | infer-basedpyright |    552 |     328 |     58 |    166 |      0 |    0 |    679 |      918 |     5.5 |
| websockets         | infer-ty           |    572 |     328 |     58 |    186 |      0 |    0 |    699 |      918 |     4.1 |
| websockets         | infer-pyrefly      |    589 |     328 |     58 |    203 |      0 |    0 |    716 |      918 |     2.1 |
| websockets         | infer-trace        |    432 |     326 |     58 |     48 |      0 |    0 |    559 |      918 |     2.1 |
| anyio              | certain            |    207 |     207 |        |        |      0 |    0 |    482 |      990 |     1.1 |
| anyio              | likely             |    239 |     207 |     32 |        |      0 |    0 |    514 |      990 |     1.2 |
| anyio              | unsafe             |    266 |     207 |     32 |     27 |      0 |    0 |    541 |      990 |     1.4 |
| anyio              | infer-basedpyright |    372 |     207 |     40 |    125 |      0 |    0 |    647 |      990 |     9.0 |
| anyio              | infer-ty           |    415 |     207 |     49 |    159 |      0 |    0 |    690 |      990 |     4.0 |
| anyio              | infer-pyrefly      |    372 |     207 |     39 |    126 |      0 |    0 |    647 |      990 |     2.4 |
| anyio              | infer-trace        |    266 |     207 |     32 |     27 |      0 |    0 |    541 |      990 |     1.8 |
| zarr               | certain            |  1,069 |   1,069 |        |        |      0 |    0 |  1,737 |    3,079 |     1.6 |
| zarr               | likely             |  1,142 |   1,070 |     72 |        |      0 |    0 |  1,810 |    3,079 |     4.2 |
| zarr               | unsafe             |  1,182 |   1,069 |     72 |     41 |      0 |    0 |  1,850 |    3,079 |     4.2 |
| zarr               | infer-basedpyright |  1,646 |   1,069 |     99 |    478 |      0 |    2 |  2,314 |    3,079 |    19.6 |
| zarr               | infer-ty           |  1,604 |   1,069 |     98 |    437 |      0 |    0 |  2,272 |    3,079 |    11.2 |
| zarr               | infer-pyrefly      |  1,348 |   1,069 |     80 |    199 |      0 |    0 |  2,016 |    3,079 |     4.5 |
| zarr               | infer-trace        |  1,182 |   1,069 |     72 |     41 |      0 |    0 |  1,850 |    3,079 |     1.8 |
| joblib             | certain            |    525 |     525 |        |        |      0 |    0 |    526 |    2,241 |     2.0 |
| joblib             | likely             |    702 |     526 |    176 |        |      0 |    0 |    703 |    2,241 |     2.1 |
| joblib             | unsafe             |    771 |     525 |    176 |     70 |      0 |    0 |    772 |    2,241 |     5.0 |
| joblib             | infer-basedpyright |    899 |     525 |    184 |    190 |      0 |    0 |    900 |    2,241 |    17.6 |
| joblib             | infer-ty           |    842 |     525 |    182 |    135 |      0 |    0 |    843 |    2,241 |    10.1 |
| joblib             | infer-pyrefly      |    892 |     523 |    184 |    185 |      0 |    0 |    893 |    2,241 |     4.3 |
| joblib             | infer-trace        |    832 |     525 |    177 |    130 |      0 |    0 |    833 |    2,241 |     2.6 |
| networkx           | certain            |  3,939 |   3,939 |        |        |      0 |    0 |  4,001 |   22,518 |     5.0 |
| networkx           | likely             |  6,099 |   3,988 |  2,111 |        |      0 |    0 |  6,161 |   22,518 |    10.4 |
| networkx           | unsafe             |  6,405 |   3,939 |  2,097 |    369 |      0 |    0 |  6,467 |   22,518 |     6.9 |
| networkx           | infer-basedpyright |  7,413 |   3,941 |  2,166 |  1,306 |      0 |    9 |  7,475 |   22,518 |    76.9 |
| networkx           | infer-ty           |  6,860 |   3,939 |  2,122 |    799 |      0 |    0 |  6,922 |   22,518 |    29.6 |
| networkx           | infer-pyrefly      |  6,936 |   3,943 |  2,130 |    863 |      0 |    2 |  6,998 |   22,518 |    22.7 |
| networkx           | infer-trace        |  6,921 |   3,939 |  2,135 |    847 |      0 |    3 |  6,983 |   22,518 |    10.6 |
| nibabel            | certain            |  1,850 |   1,850 |        |        |      0 |    0 |  1,932 |    8,550 |     3.3 |
| nibabel            | likely             |  2,531 |   1,874 |    657 |        |      0 |    0 |  2,613 |    8,550 |    20.2 |
| nibabel            | unsafe             |  2,789 |   1,850 |    657 |    282 |      0 |    0 |  2,871 |    8,550 |    11.1 |
| nibabel            | infer-basedpyright |  3,405 |   1,851 |    696 |    858 |      0 |    5 |  3,487 |    8,550 |    59.9 |
| nibabel            | infer-ty           |  3,373 |   1,851 |    715 |    807 |      0 |    6 |  3,455 |    8,550 |    53.4 |
| nibabel            | infer-pyrefly      |  3,222 |   1,850 |    667 |    705 |      0 |    0 |  3,304 |    8,550 |    10.4 |
| nibabel            | infer-trace        |  2,879 |   1,850 |    662 |    367 |      0 |    0 |  2,961 |    8,550 |     4.3 |
| narwhals           | certain            |    973 |     973 |        |        |      0 |    0 |  1,838 |    3,985 |     1.7 |
| narwhals           | likely             |  1,041 |     974 |     67 |        |      0 |    0 |  1,906 |    3,985 |     3.4 |
| narwhals           | unsafe             |  1,096 |     973 |     67 |     56 |      0 |    0 |  1,961 |    3,985 |     5.2 |
| narwhals           | infer-basedpyright |  1,422 |     982 |     80 |    360 |      0 |    4 |  2,287 |    3,985 |    15.0 |
| narwhals           | infer-ty           |  1,559 |     982 |     89 |    488 |      0 |    0 |  2,424 |    3,985 |    19.2 |
| narwhals           | infer-pyrefly      |  1,607 |     982 |     81 |    544 |      0 |    3 |  2,472 |    3,985 |     9.5 |
| narwhals           | infer-trace        |  1,096 |     973 |     67 |     56 |      0 |    0 |  1,961 |    3,985 |     2.5 |
| xarray             | certain            |  3,544 |   3,544 |        |        |      0 |    0 |  4,573 |   22,373 |    19.4 |
| xarray             | likely             |  6,688 |   3,586 |  3,102 |        |      0 |    0 |  7,717 |   22,373 |    45.4 |
| xarray             | unsafe             |  6,897 |   3,544 |  3,102 |    251 |      0 |    0 |  7,926 |   22,373 |    22.4 |
| xarray             | infer-basedpyright |  8,932 |   3,511 |  3,153 |  2,268 |      0 |    0 |  9,961 |   22,373 |    90.9 |
| xarray             | infer-ty           |  8,942 |   3,511 |  3,153 |  2,278 |      0 |    4 |  9,971 |   22,373 |    53.0 |
| xarray             | infer-pyrefly      |  7,361 |   3,511 |  3,115 |    735 |      0 |    0 |  8,390 |   22,373 |    31.2 |
| xarray             | infer-trace        |  6,932 |   3,544 |  3,101 |    287 |      0 |    0 |  7,961 |   22,373 |    15.4 |
| litestar           | certain            |    595 |     595 |        |        |      0 |    0 |  2,149 |    3,459 |     2.5 |
| litestar           | likely             |    698 |     596 |    102 |        |      0 |    0 |  2,252 |    3,459 |     4.3 |
| litestar           | unsafe             |    760 |     595 |    102 |     63 |      0 |    0 |  2,314 |    3,459 |     3.7 |
| litestar           | infer-basedpyright |  1,031 |     592 |    113 |    326 |      0 |    0 |  2,585 |    3,459 |    15.3 |
| litestar           | infer-ty           |  1,039 |     592 |    116 |    331 |      0 |    0 |  2,593 |    3,459 |    13.0 |
| litestar           | infer-pyrefly      |    876 |     592 |    109 |    175 |      0 |    0 |  2,430 |    3,459 |    10.3 |
| litestar           | infer-trace        |    760 |     595 |    102 |     63 |      0 |    0 |  2,314 |    3,459 |     2.0 |
| stripe             | certain            |    565 |     565 |        |        |      0 |    0 | 29,315 |   32,107 |     5.6 |
| stripe             | likely             |    726 |     565 |    161 |        |      0 |    0 | 29,476 |   32,107 |     7.5 |
| stripe             | unsafe             |  1,228 |     565 |    161 |    502 |      0 |    0 | 29,978 |   32,107 |     5.6 |
| stripe             | infer-basedpyright |  1,949 |     565 |    161 |  1,223 |      0 |    0 | 30,699 |   32,107 |   820.8 |
| stripe             | infer-ty           |  1,282 |     565 |    161 |    556 |      0 |    0 | 30,032 |   32,107 |    25.1 |
| stripe             | infer-pyrefly      |  1,279 |     565 |    161 |    553 |      0 |    0 | 30,029 |   32,107 |    13.9 |
| celery             | certain            |    503 |     503 |        |        |      0 |    0 |    519 |    3,764 |     3.8 |
| celery             | likely             |    623 |     506 |    117 |        |      0 |    0 |    639 |    3,764 |     6.1 |
| celery             | unsafe             |    870 |     503 |    117 |    250 |      0 |    0 |    886 |    3,764 |     4.5 |
| celery             | infer-basedpyright |  1,027 |     503 |    126 |    398 |      0 |   16 |  1,043 |    3,764 |    25.1 |
| celery             | infer-ty           |    945 |     503 |    118 |    324 |      0 |    0 |    961 |    3,764 |     7.8 |
| celery             | infer-pyrefly      |    978 |     503 |    119 |    356 |      0 |    0 |    994 |    3,764 |     6.6 |
| celery             | infer-trace        |    934 |     503 |    116 |    315 |      0 |    0 |    950 |    3,764 |     3.4 |
| optuna             | certain            |  1,473 |   1,473 |        |        |      0 |    0 |  1,764 |    3,889 |     4.9 |
| optuna             | likely             |  1,674 |   1,479 |    195 |        |      0 |    0 |  1,965 |    3,889 |     8.2 |
| optuna             | unsafe             |  1,779 |   1,473 |    195 |    111 |      0 |    0 |  2,070 |    3,889 |     4.1 |
| optuna             | infer-basedpyright |  2,136 |   1,473 |    216 |    447 |      0 |    5 |  2,427 |    3,889 |    21.6 |
| optuna             | infer-ty           |  2,185 |   1,473 |    234 |    478 |      0 |    5 |  2,476 |    3,889 |    17.7 |
| optuna             | infer-pyrefly      |  1,973 |   1,473 |    213 |    287 |      0 |    5 |  2,264 |    3,889 |    10.9 |
| optuna             | infer-trace        |  1,779 |   1,473 |    195 |    111 |      0 |    0 |  2,070 |    3,889 |     2.9 |
| dask               | certain            |  3,117 |   3,117 |        |        |      0 |    0 |  3,375 |   24,430 |    18.4 |
| dask               | likely             |  5,102 |   3,184 |  1,918 |        |      0 |    0 |  5,360 |   24,430 |    28.4 |
| dask               | unsafe             |  5,795 |   3,152 |  1,916 |    727 |      0 |    0 |  6,053 |   24,430 |    29.7 |
| dask               | infer-basedpyright |  6,771 |   3,151 |  1,963 |  1,657 |      0 |   29 |  7,029 |   24,430 |    88.8 |
| dask               | infer-ty           |  6,215 |   3,152 |  1,949 |  1,114 |      0 |   17 |  6,473 |   24,430 |    59.7 |
| dask               | infer-pyrefly      |  6,483 |   3,153 |  1,959 |  1,371 |      0 |    0 |  6,741 |   24,430 |    32.5 |
| dask               | infer-trace        |  6,137 |   3,152 |  1,916 |  1,069 |      0 |    0 |  6,395 |   24,430 |    17.1 |
| mypy               | certain            |  4,738 |   4,738 |        |        |      0 |    0 |  7,038 |   13,701 |     7.7 |
| mypy               | likely             |  5,913 |   4,760 |  1,153 |        |      0 |    0 |  8,213 |   13,701 |     6.8 |
| mypy               | unsafe             |  6,300 |   4,738 |  1,151 |    411 |      0 |    0 |  8,599 |   13,701 |    11.2 |
| mypy               | infer-basedpyright |  8,231 |   4,743 |  1,265 |  2,223 |      0 |    0 | 10,530 |   13,701 |    28.7 |
| mypy               | infer-ty           |  8,554 |   4,742 |  1,276 |  2,536 |      0 |    0 | 10,853 |   13,701 |    19.3 |
| mypy               | infer-pyrefly      |  8,806 |   4,738 |  1,284 |  2,784 |      0 |    0 | 11,105 |   13,701 |    10.1 |
| mypy               | infer-trace        |  6,300 |   4,738 |  1,151 |    411 |      0 |    0 |  8,599 |   13,701 |     8.0 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 23,973 |  23,973 |        |        |
| certain            | stdlib                 | 16,158 |  16,158 |        |        |
| certain            | call                   |  9,553 |   9,553 |        |        |
| certain            | container+literal      |  6,956 |   6,956 |        |        |
| certain            | builtin                |  4,396 |   4,396 |        |        |
| certain            | loop                   |  3,933 |   3,933 |        |        |
| certain            | copy+loop              |  3,593 |   3,593 |        |        |
| certain            | method                 |  3,444 |   3,444 |        |        |
| certain            | container+literal+loop |  2,079 |   2,079 |        |        |
| certain            | literal+method         |  1,629 |   1,629 |        |        |
| certain            | call+unpack            |  1,553 |   1,553 |        |        |
| certain            | open                   |  1,493 |   1,493 |        |        |
| likely             | constructor            | 36,157 |     256 | 35,901 |        |
| likely             | literal                | 23,981 |  23,981 |        |        |
| likely             | stdlib                 | 16,222 |  16,222 |        |        |
| likely             | call                   | 10,051 |   9,566 |    485 |        |
| likely             | container+literal      |  6,956 |   6,956 |        |        |
| likely             | method                 |  4,862 |   3,475 |  1,387 |        |
| likely             | builtin                |  4,397 |   4,397 |        |        |
| likely             | copy+loop              |  4,081 |   3,619 |    462 |        |
| likely             | loop                   |  3,933 |   3,933 |        |        |
| likely             | container+literal+loop |  2,079 |   2,079 |        |        |
| likely             | literal+method         |  1,629 |   1,629 |        |        |
| likely             | call+unpack            |  1,553 |   1,553 |        |        |
| unsafe             | constructor            | 36,154 |     256 | 35,898 |        |
| unsafe             | literal                | 23,976 |  23,971 |        |      5 |
| unsafe             | stdlib                 | 16,615 |  16,160 |        |    455 |
| unsafe             | call                   | 10,013 |   9,553 |    460 |        |
| unsafe             | container+literal      |  6,956 |   6,956 |        |        |
| unsafe             | literal+member         |  5,048 |         |        |  5,048 |
| unsafe             | method                 |  4,792 |   3,444 |  1,348 |        |
| unsafe             | builtin                |  4,398 |   4,396 |        |      2 |
| unsafe             | copy+loop              |  4,047 |   3,593 |    454 |        |
| unsafe             | returned               |  4,024 |   1,168 |        |  2,856 |
| unsafe             | loop                   |  3,933 |   3,933 |        |        |
| unsafe             | container+literal+loop |  2,079 |   2,079 |        |        |
| infer-basedpyright | constructor            | 36,088 |     255 | 35,833 |        |
| infer-basedpyright | checker                | 27,982 |         |        | 27,982 |
| infer-basedpyright | literal                | 23,981 |  23,976 |        |      5 |
| infer-basedpyright | stdlib                 | 16,671 |  16,045 |        |    626 |
| infer-basedpyright | call                   | 10,156 |   9,541 |    615 |        |
| infer-basedpyright | container+literal      |  6,956 |   6,956 |        |        |
| infer-basedpyright | literal+member         |  5,047 |         |        |  5,047 |
| infer-basedpyright | method                 |  5,024 |   3,414 |  1,610 |        |
| infer-basedpyright | copy+loop              |  4,702 |   3,596 |  1,106 |        |
| infer-basedpyright | returned               |  4,427 |   1,149 |        |  3,278 |
| infer-basedpyright | builtin                |  4,398 |   4,396 |        |      2 |
| infer-basedpyright | loop                   |  3,933 |   3,933 |        |        |
| infer-ty           | constructor            | 36,091 |     256 | 35,835 |        |
| infer-ty           | literal                | 23,980 |  23,975 |        |      5 |
| infer-ty           | checker                | 22,742 |         |        | 22,742 |
| infer-ty           | stdlib                 | 16,674 |  16,066 |        |    608 |
| infer-ty           | call                   | 10,100 |   9,542 |    558 |        |
| infer-ty           | container+literal      |  6,956 |   6,956 |        |        |
| infer-ty           | literal+member         |  5,048 |         |        |  5,048 |
| infer-ty           | method                 |  5,001 |   3,415 |  1,586 |        |
| infer-ty           | copy+loop              |  4,625 |   3,595 |  1,030 |        |
| infer-ty           | builtin                |  4,398 |   4,396 |        |      2 |
| infer-ty           | returned               |  4,359 |   1,169 |        |  3,190 |
| infer-ty           | loop                   |  3,933 |   3,933 |        |        |
| infer-pyrefly      | constructor            | 36,073 |     255 | 35,818 |        |
| infer-pyrefly      | checker                | 24,481 |         |        | 24,481 |
| infer-pyrefly      | literal                | 23,981 |  23,976 |        |      5 |
| infer-pyrefly      | stdlib                 | 16,747 |  16,115 |        |    632 |
| infer-pyrefly      | call                   | 10,084 |   9,543 |    541 |        |
| infer-pyrefly      | container+literal      |  6,956 |   6,956 |        |        |
| infer-pyrefly      | literal+member         |  5,047 |         |        |  5,047 |
| infer-pyrefly      | method                 |  4,954 |   3,414 |  1,540 |        |
| infer-pyrefly      | copy+loop              |  4,605 |   3,595 |  1,010 |        |
| infer-pyrefly      | builtin                |  4,398 |   4,396 |        |      2 |
| infer-pyrefly      | returned               |  4,357 |   1,166 |        |  3,191 |
| infer-pyrefly      | loop                   |  3,933 |   3,933 |        |        |
| infer-trace        | constructor            | 28,631 |      24 | 28,607 |        |
| infer-trace        | literal                | 13,872 |  13,870 |        |      2 |
| infer-trace        | call                   |  9,521 |   9,066 |    455 |        |
| infer-trace        | container+literal      |  4,427 |   4,427 |        |        |
| infer-trace        | method                 |  4,231 |   2,887 |  1,344 |        |
| infer-trace        | stdlib                 |  4,073 |   3,883 |        |    190 |
| infer-trace        | traced                 |  3,450 |         |        |  3,450 |
| infer-trace        | literal+member         |  2,816 |         |        |  2,816 |
| infer-trace        | builtin                |  2,608 |   2,606 |        |      2 |
| infer-trace        | copy+loop              |  2,597 |   2,289 |    308 |        |
| infer-trace        | loop                   |  2,015 |   2,015 |        |        |
| infer-trace        | call+unpack            |  1,466 |   1,466 |        |        |

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
| pint               |   3,078 |     160 |   2,342 |        0 |
| altair             |   1,700 |      62 |   1,265 |        0 |
| seaborn            |   2,895 |     229 |   2,027 |        0 |
| aiohttp            |   1,857 |     258 |     921 |        0 |
| websockets         |     791 |     102 |     363 |        0 |
| anyio              |     715 |      59 |     449 |        0 |
| zarr               |   2,411 |     113 |   1,229 |        0 |
| joblib             |   2,239 |     246 |   1,468 |        0 |
| networkx           |  22,456 |   2,466 |  16,051 |        0 |
| nibabel            |   8,468 |     939 |   5,679 |        0 |
| narwhals           |   3,120 |     123 |   2,024 |        0 |
| xarray             |  21,344 |   3,353 |  14,447 |        0 |
| litestar           |   1,905 |     165 |   1,145 |        0 |
| stripe             |   3,357 |     663 |   2,129 |        0 |
| celery             |   3,748 |     367 |   2,878 |        0 |
| optuna             |   3,598 |     306 |   1,819 |        0 |
| dask               |  24,172 |   2,520 |  18,535 |        0 |
| mypy               |  11,401 |   1,561 |   5,103 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library   |    4 |       40.19 |     17.02 |    1 |                       620.7 |     646.0 | hyperfine |
| django             |    4 |        7.91 |      3.31 |    1 |                       116.8 |     124.7 | hyperfine |
| sqlalchemy         |    4 |        6.57 |      2.89 |    1 |                        92.2 |      96.8 | hyperfine |
| pydantic           |    4 |        1.44 |      0.68 |    1 |                        21.3 |      23.6 | hyperfine |
| pandas             |    4 |       50.48 |     16.45 |    1 |                       766.5 |     785.2 | hyperfine |
| twisted            |    4 |        6.07 |      2.43 |    1 |                        90.4 |      96.4 | hyperfine |
| pip                |    4 |        4.01 |      1.68 |    1 |                        64.7 |      69.0 | hyperfine |
| structlog          |    4 |        0.23 |      0.23 |    1 |                         2.8 |       3.9 | hyperfine |
| attrs              |    4 |         0.2 |      0.26 |    1 |                         2.6 |       3.6 | hyperfine |
| click              |    4 |        0.36 |       0.3 |    1 |                         5.0 |       6.0 | hyperfine |
| hypercorn          |    4 |        0.29 |      0.24 |    1 |                         3.7 |       4.9 | hyperfine |
| starlette          |    4 |        0.38 |      0.29 |    1 |                         4.8 |       6.1 | hyperfine |
| werkzeug           |    4 |        0.66 |      0.36 |    1 |                         8.9 |      10.2 | hyperfine |
| mkdocs             |    4 |        0.75 |      0.48 |    1 |                        10.4 |      12.3 | hyperfine |
| httpx              |    4 |        0.31 |      0.25 |    1 |                         4.1 |       5.2 | hyperfine |
| black              |    4 |        0.46 |      0.28 |    1 |                         6.5 |       7.7 | hyperfine |
| fastapi            |    4 |        0.53 |      0.46 |    1 |                         7.8 |       9.2 | hyperfine |
| cattrs             |    4 |        0.32 |       0.3 |    1 |                         4.3 |       5.5 | hyperfine |
| pytest             |    4 |        1.23 |      0.72 |    1 |                        17.6 |      19.5 | hyperfine |
| botocore           |    4 |        1.61 |      0.75 |    1 |                        23.8 |      25.5 | hyperfine |
| uvicorn            |    4 |        0.38 |      0.28 |    1 |                         4.9 |       6.1 | hyperfine |
| mcp                |    4 |        0.95 |      0.51 |    1 |                        12.9 |      14.9 | hyperfine |
| textual            |    4 |        2.39 |      1.02 |    1 |                        33.5 |      36.7 | hyperfine |
| pdm                |    4 |        1.34 |      0.74 |    1 |                        18.4 |      21.3 | hyperfine |
| strawberry-graphql |    4 |         1.4 |      0.68 |    1 |                        19.2 |      22.5 | hyperfine |
| pygments           |    4 |        2.57 |      1.04 |    1 |                        46.8 |      49.6 | hyperfine |
| streamlink         |    4 |        1.83 |      0.78 |    1 |                        26.2 |      28.3 | hyperfine |
| sphinx             |    4 |        3.35 |      1.21 |    1 |                        49.6 |      51.2 | hyperfine |
| tox                |    4 |        0.94 |      0.43 |    1 |                        12.5 |      13.5 | hyperfine |
| pint               |    4 |        1.38 |      0.88 |    1 |                        20.7 |      24.5 | hyperfine |
| altair             |    4 |        1.65 |      1.38 |    1 |                        28.3 |      33.9 | hyperfine |
| seaborn            |    4 |        1.81 |       1.1 |    1 |                        28.3 |      34.8 | hyperfine |
| aiohttp            |    4 |        1.06 |      0.54 |    1 |                        15.2 |      16.6 | hyperfine |
| websockets         |    4 |        0.53 |      0.32 |    1 |                         7.1 |       8.6 | hyperfine |
| anyio              |    4 |        0.57 |       0.4 |    1 |                         7.9 |       9.1 | hyperfine |
| zarr               |    4 |        1.37 |      0.65 |    1 |                        20.1 |      23.1 | hyperfine |
| joblib             |    4 |        1.05 |      0.76 |    1 |                        15.1 |      18.2 | hyperfine |
| networkx           |    4 |        6.77 |      2.65 |    1 |                       104.1 |     108.0 | hyperfine |
| nibabel            |    4 |        4.12 |      1.95 |    1 |                        60.0 |      69.6 | hyperfine |
| narwhals           |    4 |        1.98 |      0.91 |    1 |                        29.8 |      34.8 | hyperfine |
| xarray             |    4 |       13.99 |      7.16 |    1 |                       240.5 |     254.7 | hyperfine |
| litestar           |    4 |        1.86 |      0.92 |    1 |                        25.5 |      29.1 | hyperfine |
| stripe             |    4 |        6.94 |      2.43 |    1 |                       117.0 |     122.6 | hyperfine |
| celery             |    4 |         2.1 |      1.42 |    1 |                        31.1 |      37.2 | hyperfine |
| optuna             |    4 |        3.08 |       1.7 |    1 |                        47.8 |      53.5 | hyperfine |
| dask               |    4 |       15.08 |      7.32 |    1 |                       277.0 |     291.4 | hyperfine |
| mypy               |    4 |        4.82 |      1.65 |    1 |                        73.4 |      75.6 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                            tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | -------------------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  460 |          Ran 17578 tests: FAILED (failures=5, skipped=1129, expected failures=5) |   626.1 |     68.6 |
| django             | certain |    927 |    925 |        2 |                      |                                                                                  |         |          |
| django             | likely  |    297 |    296 |        1 |                      |                                                                                  |         |          |
| django             | guess   |    300 |    284 |       16 |                      |                                                                                  |         |          |
| sqlalchemy         |         |        |        |          |                  176 |                                              1 failed, 26644 passed, 983 skipped |    90.1 |     92.5 |
| sqlalchemy         | certain |  1,052 |  1,033 |       19 |                      |                                                                                  |         |          |
| sqlalchemy         | likely  |    170 |    168 |        2 |                      |                                                                                  |         |          |
| sqlalchemy         | guess   |    124 |    122 |        2 |                      |                                                                                  |         |          |
| pydantic           |         |        |        |          |                    1 |                                             6439 passed, 329 skipped, 27 xfailed |    76.9 |     22.5 |
| pydantic           | certain |    484 |    479 |        5 |                      |                                                                                  |         |          |
| pydantic           | likely  |     53 |     53 |        0 |                      |                                                                                  |         |          |
| pydantic           | guess   |     32 |     32 |        0 |                      |                                                                                  |         |          |
| pandas             |         |        |        |          |                1,429 |                            165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   116.2 |     84.0 |
| pandas             | certain | 12,872 | 12,797 |       75 |                      |                                                                                  |         |          |
| pandas             | likely  | 20,110 | 20,052 |       58 |                      |                                                                                  |         |          |
| pandas             | guess   |    831 |    783 |       48 |                      |                                                                                  |         |          |
| structlog          |         |        |        |          |                    0 |                                     1 failed, 883 passed, 37 skipped, 2 warnings |     4.6 |      1.9 |
| structlog          | certain |     64 |     64 |        0 |                      |                                                                                  |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | guess   |      5 |      5 |        0 |                      |                                                                                  |         |          |
| attrs              |         |        |        |          |                    2 |                                      1 failed, 1382 passed, 2 skipped, 2 xfailed |     7.5 |      4.7 |
| attrs              | certain |     73 |     73 |        0 |                      |                                                                                  |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                                  |         |          |
| attrs              | guess   |      1 |      1 |        0 |                      |                                                                                  |         |          |
| click              |         |        |        |          |                    0 |                             1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     8.6 |      5.9 |
| click              | certain |    208 |    208 |        0 |                      |                                                                                  |         |          |
| click              | likely  |     20 |     19 |        1 |                      |                                                                                  |         |          |
| click              | guess   |     28 |     28 |        0 |                      |                                                                                  |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                             2 failed, 194 passed |     9.0 |      8.5 |
| hypercorn          | certain |     64 |     64 |        0 |                      |                                                                                  |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                                  |         |          |
| hypercorn          | guess   |      9 |      9 |        0 |                      |                                                                                  |         |          |
| starlette          |         |        |        |          |                    0 |                                                1271 passed, 2 skipped, 2 xfailed |    14.9 |     14.4 |
| starlette          | certain |    190 |    190 |        0 |                      |                                                                                  |         |          |
| starlette          | likely  |     46 |     46 |        0 |                      |                                                                                  |         |          |
| starlette          | guess   |     30 |     30 |        0 |                      |                                                                                  |         |          |
| werkzeug           |         |        |        |          |                    0 |                                                 980 passed, 1 skipped, 1 warning |     9.8 |     11.2 |
| werkzeug           | certain |    356 |    351 |        5 |                      |                                                                                  |         |          |
| werkzeug           | likely  |     44 |     44 |        0 |                      |                                                                                  |         |          |
| werkzeug           | guess   |     34 |     34 |        0 |                      |                                                                                  |         |          |
| mkdocs             |         |        |        |          |                   12 |                          Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    10.8 |     11.0 |
| mkdocs             | certain |    629 |    628 |        1 |                      |                                                                                  |         |          |
| mkdocs             | likely  |    324 |    324 |        0 |                      |                                                                                  |         |          |
| mkdocs             | guess   |    107 |    107 |        0 |                      |                                                                                  |         |          |
| httpx              |         |        |        |          |                    0 |                                                 1 failed, 1416 passed, 1 skipped |     9.6 |      8.4 |
| httpx              | certain |    182 |    182 |        0 |                      |                                                                                  |         |          |
| httpx              | likely  |     41 |     41 |        0 |                      |                                                                                  |         |          |
| httpx              | guess   |     16 |     16 |        0 |                      |                                                                                  |         |          |
| black              |         |        |        |          |                    0 |                                         519 passed, 1 skipped, 9 subtests passed |     8.7 |      5.0 |
| black              | certain |    609 |    608 |        1 |                      |                                                                                  |         |          |
| black              | likely  |     99 |     99 |        0 |                      |                                                                                  |         |          |
| black              | guess   |     40 |     40 |        0 |                      |                                                                                  |         |          |
| fastapi            |         |        |        |          |                    0 |                                               3551 passed, 17 skipped, 4 xfailed |    18.6 |     22.1 |
| fastapi            | certain |    216 |    216 |        0 |                      |                                                                                  |         |          |
| fastapi            | likely  |     28 |     28 |        0 |                      |                                                                                  |         |          |
| fastapi            | guess   |     24 |     24 |        0 |                      |                                                                                  |         |          |
| cattrs             |         |        |        |          |                    0 |                                                           994 passed, 15 xfailed |    23.4 |     29.5 |
| cattrs             | certain |    103 |    101 |        2 |                      |                                                                                  |         |          |
| cattrs             | likely  |     24 |     24 |        0 |                      |                                                                                  |         |          |
| cattrs             | guess   |     12 |     12 |        0 |                      |                                                                                  |         |          |
| pytest             |         |        |        |          |                   15 |                         4105 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    58.5 |     23.9 |
| pytest             | certain |  1,080 |  1,068 |       12 |                      |                                                                                  |         |          |
| pytest             | likely  |    126 |    126 |        0 |                      |                                                                                  |         |          |
| pytest             | guess   |     98 |     98 |        0 |                      |                                                                                  |         |          |
| botocore           |         |        |        |          |                  298 |                                                7 failed, 4593 passed, 96 skipped |    26.5 |     31.3 |
| botocore           | certain |    331 |    330 |        1 |                      |                                                                                  |         |          |
| botocore           | likely  |    130 |    130 |        0 |                      |                                                                                  |         |          |
| botocore           | guess   |     93 |     92 |        1 |                      |                                                                                  |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                          1350 passed, 12 skipped |    31.0 |     30.0 |
| uvicorn            | certain |    169 |    165 |        4 |                      |                                                                                  |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                                  |         |          |
| uvicorn            | guess   |      7 |      7 |        0 |                      |                                                                                  |         |          |
| mcp                |         |        |        |          |                    0 |                                                6095 passed, 8 skipped, 1 xfailed |    19.8 |     16.7 |
| mcp                | certain |    501 |    501 |        0 |                      |                                                                                  |         |          |
| mcp                | likely  |    128 |    127 |        1 |                      |                                                                                  |         |          |
| mcp                | guess   |     54 |     54 |        0 |                      |                                                                                  |         |          |
| pdm                |         |        |        |          |                    0 |                                              1472 passed, 1 skipped, 60 warnings |    17.3 |     23.2 |
| pdm                | certain |    888 |    880 |        8 |                      |                                                                                  |         |          |
| pdm                | likely  |    133 |    133 |        0 |                      |                                                                                  |         |          |
| pdm                | guess   |     76 |     76 |        0 |                      |                                                                                  |         |          |
| strawberry-graphql |         |        |        |          |                    0 |          51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    16.5 |     16.3 |
| strawberry-graphql | certain |    377 |    371 |        6 |                      |                                                                                  |         |          |
| strawberry-graphql | likely  |     93 |     91 |        2 |                      |                                                                                  |         |          |
| strawberry-graphql | guess   |     27 |     27 |        0 |                      |                                                                                  |         |          |
| pygments           |         |        |        |          |                   88 |                                                1 failed, 5330 passed, 15 skipped |    21.5 |     21.0 |
| pygments           | certain |    291 |    291 |        0 |                      |                                                                                  |         |          |
| pygments           | likely  |     59 |     59 |        0 |                      |                                                                                  |         |          |
| pygments           | guess   |     59 |     59 |        0 |                      |                                                                                  |         |          |
| streamlink         |         |        |        |          |                    8 |                                                          7248 passed, 36 skipped |    21.2 |     17.0 |
| streamlink         | certain |    267 |    266 |        1 |                      |                                                                                  |         |          |
| streamlink         | likely  |     38 |     38 |        0 |                      |                                                                                  |         |          |
| streamlink         | guess   |     36 |     36 |        0 |                      |                                                                                  |         |          |
| sphinx             |         |        |        |          |                    0 |                                   9 failed, 2393 passed, 22 skipped, 35 warnings |    16.3 |     19.2 |
| sphinx             | certain |  2,022 |  1,995 |       27 |                      |                                                                                  |         |          |
| sphinx             | likely  |    342 |    341 |        1 |                      |                                                                                  |         |          |
| sphinx             | guess   |    192 |    190 |        2 |                      |                                                                                  |         |          |
| tox                |         |        |        |          |                    0 |                                                1 failed, 8547 passed, 31 skipped |    24.4 |     32.6 |
| tox                | certain |    729 |    726 |        3 |                      |                                                                                  |         |          |
| tox                | likely  |     59 |     59 |        0 |                      |                                                                                  |         |          |
| tox                | guess   |     29 |     28 |        1 |                      |                                                                                  |         |          |
| pint               |         |        |        |          |                   10 | 1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    38.3 |     31.8 |
| pint               | certain |    334 |    326 |        8 |                      |                                                                                  |         |          |
| pint               | likely  |     63 |     63 |        0 |                      |                                                                                  |         |          |
| pint               | guess   |     37 |     34 |        3 |                      |                                                                                  |         |          |
| altair             |         |        |        |          |                    6 |            28 failed, 1866 passed, 12 skipped, 7 xfailed, 3 xpassed, 92 warnings |    26.4 |     25.5 |
| altair             | certain |    198 |    197 |        1 |                      |                                                                                  |         |          |
| altair             | likely  |     33 |     33 |        0 |                      |                                                                                  |         |          |
| altair             | guess   |      7 |      6 |        1 |                      |                                                                                  |         |          |
| seaborn            |         |        |        |          |                   34 |            20 failed, 2178 passed, 11 skipped, 6 xfailed, 958 warnings, 8 errors |    65.5 |     58.9 |
| seaborn            | certain |    484 |    482 |        2 |                      |                                                                                  |         |          |
| seaborn            | likely  |    115 |    114 |        1 |                      |                                                                                  |         |          |
| seaborn            | guess   |     53 |     50 |        3 |                      |                                                                                  |         |          |
| aiohttp            |         |        |        |          |                    1 |                           4843 passed, 535 skipped, 2 xfailed, 4 subtests passed |   108.9 |     92.2 |
| aiohttp            | certain |    508 |    493 |       15 |                      |                                                                                  |         |          |
| aiohttp            | likely  |    117 |    116 |        1 |                      |                                                                                  |         |          |
| aiohttp            | guess   |     83 |     80 |        3 |                      |                                                                                  |         |          |
| websockets         |         |        |        |          |                    0 |                                                   Ran 2589 tests: OK (skipped=8) |    32.6 |     30.1 |
| websockets         | certain |    236 |    235 |        1 |                      |                                                                                  |         |          |
| websockets         | likely  |     50 |     50 |        0 |                      |                                                                                  |         |          |
| websockets         | guess   |     30 |     30 |        0 |                      |                                                                                  |         |          |
| anyio              |         |        |        |          |                    0 |                               3824 passed, 19 skipped, 388 deselected, 5 xfailed |   117.3 |    110.2 |
| anyio              | certain |    152 |    151 |        1 |                      |                                                                                  |         |          |
| anyio              | likely  |     24 |     24 |        0 |                      |                                                                                  |         |          |
| anyio              | guess   |     22 |     21 |        1 |                      |                                                                                  |         |          |
| zarr               |         |        |        |          |                    0 |                                             8422 passed, 1205 skipped, 4 xfailed |    80.1 |     74.4 |
| zarr               | certain |    723 |    711 |       12 |                      |                                                                                  |         |          |
| zarr               | likely  |     47 |     47 |        0 |                      |                                                                                  |         |          |
| zarr               | guess   |     24 |     23 |        1 |                      |                                                                                  |         |          |
| joblib             |         |        |        |          |                   59 |                        7 failed, 1485 passed, 45 skipped, 4 xpassed, 83 warnings |   157.8 |    163.3 |
| joblib             | certain |    357 |    357 |        0 |                      |                                                                                  |         |          |
| joblib             | likely  |    130 |    130 |        0 |                      |                                                                                  |         |          |
| joblib             | guess   |     38 |     38 |        0 |                      |                                                                                  |         |          |
| networkx           |         |        |        |          |                  424 |                                            10083 passed, 62 skipped, 741 xfailed |    52.1 |     30.5 |
| networkx           | certain |  3,649 |  3,648 |        1 |                      |                                                                                  |         |          |
| networkx           | likely  |  2,009 |  2,005 |        4 |                      |                                                                                  |         |          |
| networkx           | guess   |    310 |    307 |        3 |                      |                                                                                  |         |          |
| nibabel            |         |        |        |          |                   81 |                      108 failed, 5168 passed, 304 skipped, 40 xfailed, 20 errors |    16.8 |     15.1 |
| nibabel            | certain |  1,238 |  1,235 |        3 |                      |                                                                                  |         |          |
| nibabel            | likely  |    546 |    545 |        1 |                      |                                                                                  |         |          |
| nibabel            | guess   |    152 |    152 |        0 |                      |                                                                                  |         |          |
| narwhals           |         |        |        |          |                    0 |                               972 failed, 11116 passed, 235 skipped, 699 xfailed |    37.3 |     28.0 |
| narwhals           | certain |    512 |    511 |        1 |                      |                                                                                  |         |          |
| narwhals           | likely  |     46 |     46 |        0 |                      |                                                                                  |         |          |
| narwhals           | guess   |     25 |     25 |        0 |                      |                                                                                  |         |          |
| xarray             |         |        |        |          |                   36 |  2 failed, 6334 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    18.5 |     20.7 |
| xarray             | certain |  1,759 |  1,751 |        8 |                      |                                                                                  |         |          |
| xarray             | likely  |  1,751 |  1,751 |        0 |                      |                                                                                  |         |          |
| xarray             | guess   |    111 |    111 |        0 |                      |                                                                                  |         |          |
| litestar           |         |        |        |          |                    0 |           6 failed, 5645 passed, 256 skipped, 13 xfailed, 30 xpassed, 4 warnings |    29.9 |     28.2 |
| litestar           | certain |    447 |    446 |        1 |                      |                                                                                  |         |          |
| litestar           | likely  |     88 |     88 |        0 |                      |                                                                                  |         |          |
| litestar           | guess   |     41 |     40 |        1 |                      |                                                                                  |         |          |
| celery             |         |        |        |          |                   64 |                                     3 failed, 3521 passed, 36 skipped, 3 xfailed |   192.8 |     41.9 |
| celery             | certain |    218 |    214 |        4 |                      |                                                                                  |         |          |
| celery             | likely  |     35 |     35 |        0 |                      |                                                                                  |         |          |
| celery             | guess   |     32 |     29 |        3 |                      |                                                                                  |         |          |
| optuna             |         |        |        |          |                    0 |                     263 failed, 4203 passed, 43 skipped, 326 warnings, 16 errors |   161.1 |    287.5 |
| optuna             | certain |    841 |    840 |        1 |                      |                                                                                  |         |          |
| optuna             | likely  |    121 |    121 |        0 |                      |                                                                                  |         |          |
| optuna             | guess   |     47 |     47 |        0 |                      |                                                                                  |         |          |
| dask               |         |        |        |          |                  339 |         1 failed, 16200 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   140.6 |    190.8 |
| dask               | certain |  2,354 |  2,347 |        7 |                      |                                                                                  |         |          |
| dask               | likely  |  1,519 |  1,518 |        1 |                      |                                                                                  |         |          |
| dask               | guess   |    215 |    208 |        7 |                      |                                                                                  |         |          |
| mypy               |         |        |        |          |                    0 |                        14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   299.3 |    357.6 |
| mypy               | certain |  3,675 |  3,675 |        0 |                      |                                                                                  |         |          |
| mypy               | likely  |    899 |    899 |        0 |                      |                                                                                  |         |          |
| mypy               | guess   |    289 |    289 |        0 |                      |                                                                                  |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                | same as released | summary                                                               | new failures | gone | named |
| ------------------ | ------------------ | ---------------- | --------------------------------------------------------------------- | -----------: | ---: | ----: |
| django             | released           |                  | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped            |              |      |       |
| django             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| django             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| django             | fix-unsafe         | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-basedpyright | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-pyrefly      | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-trace        | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-ty           | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped            |            0 |    0 |     0 |
| sqlalchemy         | released           |                  | 26,643 passed, 985 skipped                                            |              |      |       |
| sqlalchemy         | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| sqlalchemy         | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| sqlalchemy         | fix-unsafe         | True             | 26,643 passed, 985 skipped                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-basedpyright | True             | 26,643 passed, 985 skipped                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-pyrefly      | True             | 26,645 passed, 983 skipped                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-trace        | True             | 26,645 passed, 983 skipped                                            |            0 |    0 |     0 |
| sqlalchemy         | infer-ty           | True             | 26,645 passed, 983 skipped                                            |            0 |    0 |     0 |
| pydantic           | released           |                  | 6,439 passed, 329 skipped, 27 xfailed                                 |              |      |       |
| pydantic           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pydantic           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pydantic           | fix-unsafe         | True             | 6,439 passed, 329 skipped, 27 xfailed                                 |            0 |    0 |     0 |
| pydantic           | infer-basedpyright | True             | 6,439 passed, 329 skipped, 27 xfailed                                 |            0 |    0 |     0 |
| pydantic           | infer-pyrefly      | True             | 6,439 passed, 329 skipped, 27 xfailed                                 |            0 |    0 |     0 |
| pydantic           | infer-trace        | True             | 6,439 passed, 329 skipped, 27 xfailed                                 |            0 |    0 |     0 |
| pydantic           | infer-ty           | True             | 6,439 passed, 329 skipped, 27 xfailed                                 |            0 |    0 |     0 |
| pandas             | released           |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |              |      |       |
| pandas             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pandas             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pandas             | fix-unsafe         | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |            0 |    0 |     0 |
| pandas             | infer-basedpyright | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |            0 |    0 |     0 |
| pandas             | infer-pyrefly      | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |            0 |    0 |     0 |
| pandas             | infer-trace        | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |            0 |    0 |     0 |
| pandas             | infer-ty           | True             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               |            0 |    0 |     0 |
| structlog          | released           |                  | 884 passed, 37 skipped                                                |              |      |       |
| structlog          | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| structlog          | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| structlog          | fix-unsafe         | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-basedpyright | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-pyrefly      | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-trace        | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-ty           | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| attrs              | released           |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |              |      |       |
| attrs              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| attrs              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| attrs              | fix-unsafe         | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-basedpyright | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-pyrefly      | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-trace        | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-ty           | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| click              | released           |                  | 1,991 passed, 24 skipped, 1 xfailed                                   |              |      |       |
| click              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| click              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| click              | fix-unsafe         | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-basedpyright | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-pyrefly      | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-trace        | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-ty           | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| hypercorn          | released           |                  | 2 failed, 194 passed                                                  |              |      |       |
| hypercorn          | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| hypercorn          | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| hypercorn          | fix-unsafe         | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-basedpyright | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-pyrefly      | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-trace        | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-ty           | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| starlette          | released           |                  | 1,271 passed, 2 skipped, 2 xfailed                                    |              |      |       |
| starlette          | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| starlette          | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| starlette          | fix-unsafe         | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-basedpyright | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-pyrefly      | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-trace        | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-ty           | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| werkzeug           | released           |                  | 980 passed, 1 skipped                                                 |              |      |       |
| werkzeug           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| werkzeug           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| werkzeug           | fix-unsafe         | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-basedpyright | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-pyrefly      | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-trace        | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-ty           | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| mkdocs             | released           |                  | 2 errors, 2 failures, 724 ran, 4 skipped                              |              |      |       |
| mkdocs             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mkdocs             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mkdocs             | fix-unsafe         | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-basedpyright | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-pyrefly      | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-trace        | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-ty           | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| httpx              | released           |                  | 1 failed, 1,416 passed, 1 skipped                                     |              |      |       |
| httpx              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| httpx              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| httpx              | fix-unsafe         | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-basedpyright | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-pyrefly      | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-trace        | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-ty           | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| black              | released           |                  | 519 passed, 1 skipped                                                 |              |      |       |
| black              | fix-certain        | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | fix-likely         | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | fix-unsafe         | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-basedpyright | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-pyrefly      | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-trace        | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-ty           | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| fastapi            | released           |                  | 3,551 passed, 17 skipped, 4 xfailed                                   |              |      |       |
| fastapi            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| fastapi            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| fastapi            | fix-unsafe         | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-basedpyright | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-pyrefly      | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-trace        | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-ty           | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| cattrs             | released           |                  | 994 passed, 15 xfailed                                                |              |      |       |
| cattrs             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| cattrs             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| cattrs             | fix-unsafe         | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-basedpyright | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-pyrefly      | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-trace        | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-ty           | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| pytest             | released           |                  | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |              |      |       |
| pytest             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pytest             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pytest             | fix-unsafe         | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-basedpyright | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-pyrefly      | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-trace        | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-ty           | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| botocore           | released           |                  | 7 failed, 4,593 passed, 96 skipped                                    |              |      |       |
| botocore           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| botocore           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| botocore           | fix-unsafe         | True             | 7 failed, 4,593 passed, 96 skipped                                    |            0 |    0 |     0 |
| botocore           | infer-basedpyright | True             | 7 failed, 4,593 passed, 96 skipped                                    |            0 |    0 |     0 |
| botocore           | infer-pyrefly      | True             | 7 failed, 4,593 passed, 96 skipped                                    |            0 |    0 |     0 |
| botocore           | infer-trace        | True             | 7 failed, 4,593 passed, 96 skipped                                    |            0 |    0 |     0 |
| botocore           | infer-ty           | True             | 7 failed, 4,593 passed, 96 skipped                                    |            0 |    0 |     0 |
| uvicorn            | released           |                  | 1,350 passed, 12 skipped                                              |              |      |       |
| uvicorn            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| uvicorn            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| uvicorn            | fix-unsafe         | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-basedpyright | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-pyrefly      | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-trace        | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-ty           | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| mcp                | released           |                  | 6,095 passed, 8 skipped, 1 xfailed                                    |              |      |       |
| mcp                | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mcp                | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mcp                | fix-unsafe         | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-basedpyright | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-pyrefly      | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-trace        | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-ty           | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| pdm                | released           |                  | 1,472 passed, 1 skipped                                               |              |      |       |
| pdm                | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pdm                | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pdm                | fix-unsafe         | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-basedpyright | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-pyrefly      | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-trace        | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-ty           | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| strawberry-graphql | released           |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |              |      |       |
| strawberry-graphql | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| strawberry-graphql | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| strawberry-graphql | fix-unsafe         | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-basedpyright | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-pyrefly      | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-trace        | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-ty           | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| pygments           | released           |                  | 1 failed, 5,330 passed, 15 skipped                                    |              |      |       |
| pygments           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pygments           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pygments           | fix-unsafe         | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-basedpyright | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-pyrefly      | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-trace        | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-ty           | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| streamlink         | released           |                  | 7,248 passed, 36 skipped                                              |              |      |       |
| streamlink         | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| streamlink         | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| streamlink         | fix-unsafe         | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-basedpyright | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-pyrefly      | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-trace        | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-ty           | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| sphinx             | released           |                  | 10 failed, 2,392 passed, 22 skipped                                   |              |      |       |
| sphinx             | fix-certain        | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | fix-likely         | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | fix-unsafe         | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-basedpyright | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-pyrefly      | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-trace        | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-ty           | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| tox                | released           |                  | 1 failed, 8,547 passed, 31 skipped                                    |              |      |       |
| tox                | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| tox                | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| tox                | fix-unsafe         | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-basedpyright | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-pyrefly      | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-trace        | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-ty           | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| pint               | released           |                  | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |              |      |       |
| pint               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pint               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pint               | fix-unsafe         | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-basedpyright | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-pyrefly      | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-trace        | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-ty           | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| altair             | released           |                  | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |              |      |       |
| altair             | fix-certain        | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | fix-likely         | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | fix-unsafe         | True             | 28 failed, 1,866 passed, 12 skipped, 7 xfailed, 3 xpassed             |            0 |    0 |     0 |
| altair             | infer-basedpyright | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | infer-pyrefly      | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | infer-trace        | True             | 28 failed, 1,866 passed, 12 skipped, 7 xfailed, 3 xpassed             |            0 |    0 |     0 |
| altair             | infer-ty           | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| seaborn            | released           |                  | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |              |      |       |
| seaborn            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| seaborn            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| seaborn            | fix-unsafe         | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-basedpyright | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-pyrefly      | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-trace        | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-ty           | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| aiohttp            | released           |                  | 4,843 passed, 535 skipped, 2 xfailed                                  |              |      |       |
| aiohttp            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| aiohttp            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| aiohttp            | fix-unsafe         | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-basedpyright | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-pyrefly      | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-trace        | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-ty           | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| websockets         | released           |                  | 2,589 ran, 8 skipped                                                  |              |      |       |
| websockets         | fix-certain        | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | fix-likely         | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | fix-unsafe         | True             | 1 failures, 2,589 ran, 8 skipped                                      |            0 |    0 |     0 |
| websockets         | infer-basedpyright | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-pyrefly      | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-trace        | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-ty           | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| anyio              | released           |                  | 3,824 passed, 19 skipped, 5 xfailed                                   |              |      |       |
| anyio              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| anyio              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| anyio              | fix-unsafe         | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-basedpyright | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-pyrefly      | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-trace        | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-ty           | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| zarr               | released           |                  | 8,422 passed, 1,205 skipped, 4 xfailed                                |              |      |       |
| zarr               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| zarr               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| zarr               | fix-unsafe         | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-basedpyright | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-pyrefly      | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-trace        | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-ty           | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| joblib             | released           |                  | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |              |      |       |
| joblib             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| joblib             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| joblib             | fix-unsafe         | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-basedpyright | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-pyrefly      | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-trace        | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-ty           | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| networkx           | released           |                  | 10,083 passed, 62 skipped, 741 xfailed                                |              |      |       |
| networkx           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| networkx           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| networkx           | fix-unsafe         | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-basedpyright | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-pyrefly      | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-trace        | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-ty           | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| nibabel            | released           |                  | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |              |      |       |
| nibabel            | fix-certain        | True             | 18 error, 109 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-likely         | True             | 19 error, 107 failed, 5,170 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-unsafe         | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-basedpyright | True             | 21 error, 108 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-pyrefly      | True             | 18 error, 109 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-trace        | True             | 20 error, 107 failed, 5,170 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-ty           | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| narwhals           | released           |                  | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |              |      |       |
| narwhals           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| narwhals           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| narwhals           | fix-unsafe         | True             | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |            0 |    0 |     0 |
| narwhals           | infer-basedpyright | True             | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |            0 |    0 |     0 |
| narwhals           | infer-pyrefly      | True             | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |            0 |    0 |     0 |
| narwhals           | infer-trace        | True             | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |            0 |    0 |     0 |
| narwhals           | infer-ty           | True             | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   |            0 |    0 |     0 |
| xarray             | released           |                  | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |              |      |       |
| xarray             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| xarray             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| xarray             | fix-unsafe         | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-basedpyright | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-pyrefly      | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-trace        | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-ty           | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| litestar           | released           |                  | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |              |      |       |
| litestar           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| litestar           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| litestar           | fix-unsafe         | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-basedpyright | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-pyrefly      | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-trace        | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-ty           | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| celery             | released           |                  | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |              |      |       |
| celery             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| celery             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| celery             | fix-unsafe         | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-basedpyright | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-pyrefly      | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-trace        | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-ty           | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| optuna             | released           |                  | 16 error, 263 failed, 4,203 passed, 43 skipped                        |              |      |       |
| optuna             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| optuna             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| optuna             | fix-unsafe         | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-basedpyright | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-pyrefly      | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-trace        | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-ty           | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| dask               | released           |                  | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |              |      |       |
| dask               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| dask               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| dask               | fix-unsafe         | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-basedpyright | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-pyrefly      | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-trace        | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-ty           | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| mypy               | released           |                  | 14,464 passed, 366 skipped, 12 xfailed                                |              |      |       |
| mypy               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mypy               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mypy               | fix-unsafe         | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-basedpyright | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-pyrefly      | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-trace        | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-ty           | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                      change |
| ------------------ | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy         | released           |      9 |     |      |                                                             |
| sqlalchemy         | fix-certain        |      9 |   0 |    0 |    164 files changed, 1729 insertions(+), 1327 deletions(-) |
| sqlalchemy         | fix-likely         |      9 |   0 |    0 |    175 files changed, 2054 insertions(+), 1632 deletions(-) |
| sqlalchemy         | fix-unsafe         |      9 |   0 |    0 |    194 files changed, 2726 insertions(+), 2244 deletions(-) |
| sqlalchemy         | infer-basedpyright |     16 |   7 |    0 |    199 files changed, 3641 insertions(+), 3088 deletions(-) |
| sqlalchemy         | infer-pyrefly      |     28 |  19 |    0 |    196 files changed, 3230 insertions(+), 2574 deletions(-) |
| sqlalchemy         | infer-trace        |     15 |   6 |    0 |    196 files changed, 2955 insertions(+), 2408 deletions(-) |
| sqlalchemy         | infer-ty           |     12 |   3 |    0 |    198 files changed, 3589 insertions(+), 2914 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |      73 files changed, 1119 insertions(+), 804 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |      75 files changed, 1274 insertions(+), 933 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     77 files changed, 1547 insertions(+), 1175 deletions(-) |
| pydantic           | infer-basedpyright |      3 |   3 |    0 |     80 files changed, 1878 insertions(+), 1469 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     77 files changed, 1799 insertions(+), 1309 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     77 files changed, 1548 insertions(+), 1176 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     77 files changed, 1737 insertions(+), 1341 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    259 |   0 |    0 | 1067 files changed, 18245 insertions(+), 15225 deletions(-) |
| pandas             | fix-likely         |    259 |   0 |    0 | 1199 files changed, 42324 insertions(+), 38688 deletions(-) |
| pandas             | fix-unsafe         |    260 |   1 |    0 | 1202 files changed, 43193 insertions(+), 39437 deletions(-) |
| pandas             | infer-basedpyright |    297 |  38 |    0 | 1213 files changed, 49442 insertions(+), 45052 deletions(-) |
| pandas             | infer-pyrefly      |    377 | 118 |    0 | 1209 files changed, 50363 insertions(+), 45730 deletions(-) |
| pandas             | infer-trace        |    262 |   3 |    0 | 1205 files changed, 44650 insertions(+), 40810 deletions(-) |
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
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 446 insertions(+), 347 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 357 insertions(+), 272 deletions(-) |
| click              | infer-ty           |      5 |   5 |    0 |       15 files changed, 460 insertions(+), 358 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |        24 files changed, 149 insertions(+), 96 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 169 insertions(+), 109 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 146 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 236 insertions(+), 167 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 219 insertions(+), 151 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 146 deletions(-) |
| hypercorn          | infer-ty           |     14 |   2 |    0 |       25 files changed, 250 insertions(+), 174 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       29 files changed, 329 insertions(+), 248 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 386 insertions(+), 296 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-basedpyright |     12 |  12 |    0 |       33 files changed, 525 insertions(+), 408 deletions(-) |
| starlette          | infer-pyrefly      |     12 |  12 |    0 |       33 files changed, 469 insertions(+), 361 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-ty           |     12 |  12 |    0 |       33 files changed, 526 insertions(+), 407 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 542 insertions(+), 368 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 610 insertions(+), 416 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 676 insertions(+), 466 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 806 insertions(+), 572 deletions(-) |
| werkzeug           | infer-pyrefly      |      3 |   3 |    0 |       45 files changed, 837 insertions(+), 566 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 676 insertions(+), 466 deletions(-) |
| werkzeug           | infer-ty           |      1 |   1 |    0 |       45 files changed, 828 insertions(+), 575 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 235 insertions(+), 195 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 293 insertions(+), 238 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 309 insertions(+), 254 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       18 files changed, 417 insertions(+), 347 deletions(-) |
| httpx              | infer-pyrefly      |      2 |   2 |    0 |       16 files changed, 357 insertions(+), 285 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 309 insertions(+), 254 deletions(-) |
| httpx              | infer-ty           |      5 |   5 |    0 |       17 files changed, 388 insertions(+), 311 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       26 files changed, 239 insertions(+), 182 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       26 files changed, 275 insertions(+), 207 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-basedpyright |      7 |   7 |    0 |       29 files changed, 372 insertions(+), 283 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 325 insertions(+), 233 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 380 insertions(+), 293 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 774 insertions(+), 519 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 933 insertions(+), 667 deletions(-) |
| mcp                | fix-unsafe         |      2 |   2 |    0 |      81 files changed, 1023 insertions(+), 735 deletions(-) |
| mcp                | infer-basedpyright |      4 |   4 |    0 |      82 files changed, 1158 insertions(+), 862 deletions(-) |
| mcp                | infer-pyrefly      |      2 |   2 |    0 |      82 files changed, 1113 insertions(+), 807 deletions(-) |
| mcp                | infer-trace        |      2 |   2 |    0 |      81 files changed, 1023 insertions(+), 735 deletions(-) |
| mcp                | infer-ty           |      4 |   4 |    0 |      84 files changed, 1306 insertions(+), 938 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |      129 files changed, 667 insertions(+), 471 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |      147 files changed, 840 insertions(+), 625 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |      151 files changed, 897 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-basedpyright |     16 |   6 |    0 |     154 files changed, 1095 insertions(+), 838 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     14 |   4 |    0 |      152 files changed, 963 insertions(+), 725 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |      151 files changed, 897 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-ty           |     18 |   8 |    0 |     155 files changed, 1146 insertions(+), 872 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |     164 files changed, 1034 insertions(+), 532 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |     166 files changed, 1144 insertions(+), 625 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |     168 files changed, 1279 insertions(+), 739 deletions(-) |
| streamlink         | infer-basedpyright |      1 |   1 |    0 |    185 files changed, 1752 insertions(+), 1132 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |     172 files changed, 1470 insertions(+), 884 deletions(-) |
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
| pint               | released           |    659 |     |      |                                                             |
| pint               | fix-certain        |    659 |   0 |    0 |       69 files changed, 590 insertions(+), 388 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |       73 files changed, 717 insertions(+), 482 deletions(-) |
| pint               | fix-unsafe         |    665 |  10 |    4 |       76 files changed, 773 insertions(+), 524 deletions(-) |
| pint               | infer-basedpyright |    666 |  11 |    4 |      79 files changed, 1122 insertions(+), 773 deletions(-) |
| pint               | infer-pyrefly      |    670 |  15 |    4 |       77 files changed, 863 insertions(+), 584 deletions(-) |
| pint               | infer-trace        |    665 |  10 |    4 |       77 files changed, 792 insertions(+), 534 deletions(-) |
| pint               | infer-ty           |    667 |  13 |    5 |       79 files changed, 988 insertions(+), 680 deletions(-) |
| altair             | released           |      1 |     |      |                                                             |
| altair             | fix-certain        |      1 |   0 |    0 |       38 files changed, 392 insertions(+), 308 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |       38 files changed, 440 insertions(+), 354 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |       40 files changed, 457 insertions(+), 364 deletions(-) |
| altair             | infer-basedpyright |      4 |   3 |    0 |       40 files changed, 546 insertions(+), 433 deletions(-) |
| altair             | infer-pyrefly      |      6 |   5 |    0 |       40 files changed, 523 insertions(+), 410 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |       40 files changed, 467 insertions(+), 371 deletions(-) |
| altair             | infer-ty           |      9 |   8 |    0 |       40 files changed, 544 insertions(+), 429 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                             |
| seaborn            | fix-certain        |     39 |   0 |    0 |       42 files changed, 660 insertions(+), 492 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |       46 files changed, 800 insertions(+), 614 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |       46 files changed, 895 insertions(+), 699 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |      46 files changed, 1050 insertions(+), 842 deletions(-) |
| seaborn            | infer-pyrefly      |     41 |   2 |    0 |      47 files changed, 1070 insertions(+), 840 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |       46 files changed, 953 insertions(+), 733 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |       46 files changed, 982 insertions(+), 778 deletions(-) |
| websockets         | released           |      0 |     |      |                                                             |
| websockets         | fix-certain        |      0 |   0 |    0 |       39 files changed, 339 insertions(+), 233 deletions(-) |
| websockets         | fix-likely         |      0 |   0 |    0 |       39 files changed, 398 insertions(+), 290 deletions(-) |
| websockets         | fix-unsafe         |      0 |   0 |    0 |       39 files changed, 448 insertions(+), 324 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |       40 files changed, 571 insertions(+), 443 deletions(-) |
| websockets         | infer-pyrefly      |      5 |   5 |    0 |       40 files changed, 620 insertions(+), 455 deletions(-) |
| websockets         | infer-trace        |      0 |   0 |    0 |       39 files changed, 448 insertions(+), 324 deletions(-) |
| websockets         | infer-ty           |      5 |   5 |    0 |       40 files changed, 600 insertions(+), 450 deletions(-) |
| networkx           | released           |      0 |     |      |                                                             |
| networkx           | fix-certain        |      0 |   0 |    0 |    408 files changed, 3969 insertions(+), 3165 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 |    458 files changed, 6137 insertions(+), 5268 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 |    461 files changed, 6449 insertions(+), 5533 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 |    475 files changed, 7784 insertions(+), 6511 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 |    472 files changed, 7045 insertions(+), 5952 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 |    477 files changed, 7128 insertions(+), 5893 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 |    466 files changed, 7021 insertions(+), 5947 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                             |
| nibabel            | fix-certain        |     12 |   0 |    0 |    181 files changed, 2053 insertions(+), 1369 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 |    191 files changed, 2748 insertions(+), 1982 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 |    197 files changed, 3044 insertions(+), 2218 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 |    202 files changed, 3765 insertions(+), 2818 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 |    203 files changed, 3498 insertions(+), 2529 deletions(-) |
| nibabel            | infer-trace        |     15 |   3 |    0 |    197 files changed, 3162 insertions(+), 2296 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 |    199 files changed, 3703 insertions(+), 2751 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                             |
| narwhals           | fix-certain        |     19 |   0 |    0 |      96 files changed, 1010 insertions(+), 836 deletions(-) |
| narwhals           | fix-likely         |     19 |   0 |    0 |      96 files changed, 1080 insertions(+), 903 deletions(-) |
| narwhals           | fix-unsafe         |     20 |   1 |    0 |      97 files changed, 1142 insertions(+), 947 deletions(-) |
| narwhals           | infer-basedpyright |     28 |   9 |    0 |     98 files changed, 1537 insertions(+), 1266 deletions(-) |
| narwhals           | infer-pyrefly      |     32 |  13 |    0 |    101 files changed, 1729 insertions(+), 1396 deletions(-) |
| narwhals           | infer-trace        |     20 |   1 |    0 |      97 files changed, 1142 insertions(+), 947 deletions(-) |
| narwhals           | infer-ty           |     61 |  42 |    0 |    100 files changed, 1677 insertions(+), 1371 deletions(-) |
| litestar           | released           |     86 |     |      |                                                             |
| litestar           | fix-certain        |     86 |   0 |    0 |      142 files changed, 620 insertions(+), 439 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |      152 files changed, 725 insertions(+), 521 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |      165 files changed, 797 insertions(+), 567 deletions(-) |
| litestar           | infer-basedpyright |    301 | 215 |    0 |     183 files changed, 1123 insertions(+), 828 deletions(-) |
| litestar           | infer-pyrefly      |     87 |   1 |    0 |      170 files changed, 918 insertions(+), 658 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |      165 files changed, 797 insertions(+), 567 deletions(-) |
| litestar           | infer-ty           |     99 |  13 |    0 |     176 files changed, 1117 insertions(+), 816 deletions(-) |
| optuna             | released           |     52 |     |      |                                                             |
| optuna             | fix-certain        |     52 |   0 |    0 |    141 files changed, 1576 insertions(+), 1070 deletions(-) |
| optuna             | fix-likely         |     52 |   0 |    0 |    144 files changed, 1780 insertions(+), 1249 deletions(-) |
| optuna             | fix-unsafe         |     53 |   1 |    0 |    144 files changed, 1907 insertions(+), 1337 deletions(-) |
| optuna             | infer-basedpyright |     59 |   7 |    0 |    165 files changed, 2324 insertions(+), 1677 deletions(-) |
| optuna             | infer-pyrefly      |     62 |  10 |    0 |    147 files changed, 2111 insertions(+), 1499 deletions(-) |
| optuna             | infer-trace        |     53 |   1 |    0 |    144 files changed, 1907 insertions(+), 1337 deletions(-) |
| optuna             | infer-ty           |     68 |  16 |    0 |    162 files changed, 2347 insertions(+), 1691 deletions(-) |
| mypy               | released           |      0 |     |      |                                                             |
| mypy               | fix-certain        |      0 |   0 |    0 |    160 files changed, 4983 insertions(+), 3030 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 |    166 files changed, 6183 insertions(+), 4080 deletions(-) |
| mypy               | fix-unsafe         |     17 |  17 |    0 |    167 files changed, 6580 insertions(+), 4399 deletions(-) |
| mypy               | infer-basedpyright |     21 |  21 |    0 |    170 files changed, 8613 insertions(+), 6233 deletions(-) |
| mypy               | infer-pyrefly      |     24 |  24 |    0 |    170 files changed, 9205 insertions(+), 6435 deletions(-) |
| mypy               | infer-trace        |     17 |  17 |    0 |    167 files changed, 6580 insertions(+), 4399 deletions(-) |
| mypy               | infer-ty           |     29 |  29 |    0 |    170 files changed, 8935 insertions(+), 6411 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    33.3 |        83.0 |  2.5 |    3.78 |          8 |    18.56 | False |
| standard library   | fix-certain              |    89.2 |       230.1 |  2.6 |    5.18 |          3 |     6.44 | False |
| standard library   | fix-likely               |   118.3 |       319.5 |  2.7 |    7.83 |          3 |     9.72 | False |
| standard library   | fix-unsafe               |   127.2 |       250.4 |  2.0 |    5.89 |          3 |     7.34 | False |
| standard library   | infer-basedpyright       |  1262.1 |      1708.2 |  1.4 |   13.09 |          2 |    16.27 | False |
| standard library   | infer-ty                 |   205.5 |       619.7 |  3.0 |   15.55 |          3 |    20.26 | False |
| standard library   | infer-pyrefly            |   196.1 |       541.6 |  2.8 |   17.45 |          4 |    23.74 | False |
| standard library   | census                   |    16.6 |        16.5 |  1.0 |    0.51 |          8 |    18.56 | False |
| standard library   | coverage                 |     9.6 |        31.1 |  3.2 |    1.66 |          4 |     2.09 | False |
| standard library   | timing                   |   114.9 |       175.1 |  1.5 |    3.78 |         16 |      4.7 | False |
| django             | check                    |     0.4 |         0.3 |  0.7 |    0.07 |          6 |     4.01 | False |
| django             | fix-certain              |    39.7 |        49.9 |  1.3 |    1.12 |          2 |     1.37 | False |
| django             | fix-likely               |    41.3 |        58.4 |  1.4 |     1.5 |          2 |     1.85 | False |
| django             | fix-unsafe               |    19.9 |        46.4 |  2.3 |    1.25 |          3 |     1.52 | False |
| django             | infer-basedpyright       |    69.6 |       286.0 |  4.1 |    7.25 |          4 |     9.56 | False |
| django             | infer-ty                 |    88.8 |       153.3 |  1.7 |    3.61 |          3 |     4.66 | False |
| django             | infer-pyrefly            |    29.3 |        90.2 |  3.1 |    3.64 |          4 |     5.21 | False |
| django             | census                   |     9.4 |        19.1 |  2.0 |    0.85 |          6 |     4.01 | False |
| django             | coverage                 |     1.8 |         4.6 |  2.6 |    0.34 |          3 |     0.42 | False |
| django             | timing                   |    22.8 |        34.7 |  1.5 |    0.86 |         16 |     1.05 | False |
| django             | traced                   |   649.0 |       505.0 |  0.8 |    1.29 |          1 |     1.69 | False |
| django             | tests-released           |    68.9 |       390.9 |  5.7 |     3.4 |          8 |     4.08 | False |
| django             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |         16 |     6.55 | False |
| django             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |         16 |     6.75 | False |
| django             | tests-fix-unsafe         |    55.9 |       408.2 |  7.3 |    4.17 |         11 |     5.12 | False |
| django             | tests-infer-basedpyright |    41.5 |       410.5 |  9.9 |    5.79 |         16 |     7.25 | False |
| django             | tests-infer-ty           |    40.9 |       401.2 |  9.8 |    5.36 |         16 |     6.65 | False |
| django             | tests-infer-pyrefly      |    84.8 |       447.4 |  5.3 |    3.49 |          8 |     3.74 | False |
| django             | tests-infer-trace        |    41.7 |       415.0 | 10.0 |    5.72 |         16 |     7.44 | False |
| django             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |         15 |     6.68 | False |
| sqlalchemy         | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          6 |     4.04 | False |
| sqlalchemy         | fix-certain              |    14.8 |        35.0 |  2.4 |    0.97 |          3 |     1.19 | False |
| sqlalchemy         | fix-likely               |    28.0 |        47.5 |  1.7 |    1.35 |          2 |     1.65 | False |
| sqlalchemy         | fix-unsafe               |    24.9 |        39.4 |  1.6 |     1.0 |          2 |     1.22 | False |
| sqlalchemy         | infer-basedpyright       |    69.9 |       264.8 |  3.8 |    7.08 |          5 |     8.79 | False |
| sqlalchemy         | infer-ty                 |    31.0 |       100.0 |  3.2 |    3.86 |          3 |     4.87 | False |
| sqlalchemy         | infer-pyrefly            |    31.2 |        79.7 |  2.6 |    3.54 |          4 |     5.02 | False |
| sqlalchemy         | census                   |     9.4 |        15.9 |  1.7 |    0.85 |          6 |     4.04 | False |
| sqlalchemy         | coverage                 |     1.8 |         5.0 |  2.8 |    0.37 |          3 |     0.46 | False |
| sqlalchemy         | timing                   |    19.2 |        26.9 |  1.4 |    0.85 |         16 |     1.04 | False |
| sqlalchemy         | traced                   |   100.7 |      1051.7 | 10.4 |    6.41 |         16 |      8.2 | False |
| sqlalchemy         | tests-released           |    92.8 |       612.7 |  6.6 |    3.35 |          9 |     4.22 | False |
| sqlalchemy         | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     0.02 | False |
| sqlalchemy         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     0.02 | False |
| sqlalchemy         | tests-fix-unsafe         |    90.7 |       583.7 |  6.4 |    3.03 |          8 |     3.63 | False |
| sqlalchemy         | tests-infer-basedpyright |    94.7 |       591.6 |  6.2 |    3.04 |          8 |     3.57 | False |
| sqlalchemy         | tests-infer-ty           |    76.1 |       825.4 | 10.8 |    5.23 |         16 |     7.05 | False |
| sqlalchemy         | tests-infer-pyrefly      |    82.5 |       831.6 | 10.1 |    5.24 |         16 |     6.85 | False |
| sqlalchemy         | tests-infer-trace        |    74.1 |       825.3 | 11.1 |    5.25 |         16 |     6.85 | False |
| sqlalchemy         | tests                    |   273.1 |      3032.6 | 11.1 |    4.99 |         15 |     6.48 | False |
| sqlalchemy         | types-released           |     4.8 |         4.6 |  1.0 |     0.3 |          1 |      0.4 | False |
| sqlalchemy         | types-fix-certain        |     5.8 |         5.4 |  0.9 |    0.29 |          1 |     0.36 | False |
| sqlalchemy         | types-fix-likely         |     6.6 |         6.1 |  0.9 |     0.3 |          1 |     0.37 | False |
| sqlalchemy         | types-fix-unsafe         |     5.8 |         5.1 |  0.9 |    0.31 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-basedpyright |     7.4 |         6.9 |  0.9 |    0.29 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-ty           |     5.0 |         4.7 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-pyrefly      |     5.6 |         5.4 |  1.0 |    0.31 |          1 |     0.36 | False |
| sqlalchemy         | types-infer-trace        |     5.8 |         5.4 |  0.9 |    0.32 |          1 |     0.37 | False |
| sqlalchemy         | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     2.02 | False |
| pydantic           | fix-certain              |     4.0 |         9.6 |  2.4 |    0.43 |          3 |     0.51 | False |
| pydantic           | fix-likely               |    10.4 |        13.1 |  1.3 |    0.49 |          2 |      0.6 | False |
| pydantic           | fix-unsafe               |     6.2 |        10.3 |  1.7 |    0.44 |          3 |     0.54 | False |
| pydantic           | infer-basedpyright       |    35.8 |       109.0 |  3.0 |    3.13 |          4 |     3.92 | False |
| pydantic           | infer-ty                 |    11.4 |        31.8 |  2.8 |    1.68 |          3 |     2.09 | False |
| pydantic           | infer-pyrefly            |     7.0 |        32.5 |  4.6 |    1.89 |          5 |     3.07 | False |
| pydantic           | census                   |     2.0 |         3.3 |  1.6 |     0.3 |          5 |     2.02 | False |
| pydantic           | coverage                 |     1.0 |         1.8 |  1.8 |     0.2 |          2 |     0.25 | False |
| pydantic           | timing                   |     4.4 |         6.5 |  1.5 |     0.3 |         16 |     0.35 | False |
| pydantic           | traced                   |    81.7 |        49.0 |  0.6 |    0.45 |          1 |      0.6 | False |
| pydantic           | tests-released           |    22.9 |        22.1 |  1.0 |    0.25 |          1 |     0.35 | False |
| pydantic           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic           | tests-fix-unsafe         |    69.3 |        32.3 |  0.5 |    0.25 |          1 |     0.31 | False |
| pydantic           | tests-infer-basedpyright |    36.8 |        27.7 |  0.8 |    0.25 |          1 |     0.35 | False |
| pydantic           | tests-infer-ty           |    35.7 |        31.1 |  0.9 |    0.25 |          1 |     0.31 | False |
| pydantic           | tests-infer-pyrefly      |    31.1 |        27.2 |  0.9 |    0.28 |          1 |     0.31 | False |
| pydantic           | tests-infer-trace        |    38.2 |        28.9 |  0.8 |    0.25 |          1 |     0.31 | False |
| pydantic           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | types-released           |    11.7 |        14.3 |  1.2 |    0.53 |          2 |     0.65 | False |
| pydantic           | types-fix-certain        |     9.6 |        14.4 |  1.5 |    0.54 |          2 |     0.65 | False |
| pydantic           | types-fix-likely         |    11.6 |        14.9 |  1.3 |    0.53 |          2 |     0.65 | False |
| pydantic           | types-fix-unsafe         |    13.0 |        16.3 |  1.3 |    0.52 |          2 |     0.64 | False |
| pydantic           | types-infer-basedpyright |    13.9 |        16.3 |  1.2 |    0.53 |          2 |     0.67 | False |
| pydantic           | types-infer-ty           |    13.7 |        14.8 |  1.1 |    0.54 |          2 |     0.66 | False |
| pydantic           | types-infer-pyrefly      |     9.6 |        14.0 |  1.5 |    0.53 |          2 |     0.67 | False |
| pydantic           | types-infer-trace        |    13.4 |        16.8 |  1.3 |    0.53 |          2 |     0.65 | False |
| pydantic           | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |     1.0 |         0.8 |  0.8 |    0.19 |          8 |    15.55 | False |
| pandas             | fix-certain              |    81.9 |       238.5 |  2.9 |    4.05 |          3 |     5.04 | False |
| pandas             | fix-likely               |   179.7 |       413.0 |  2.3 |    7.26 |          3 |     9.05 | False |
| pandas             | fix-unsafe               |   129.6 |       265.0 |  2.0 |     4.3 |          4 |     5.36 | False |
| pandas             | infer-basedpyright       |   525.4 |      1311.0 |  2.5 |   15.95 |          3 |    19.71 | False |
| pandas             | infer-ty                 |   223.9 |       851.3 |  3.8 |   14.75 |          4 |    18.26 | False |
| pandas             | infer-pyrefly            |   160.1 |       609.3 |  3.8 |   17.53 |          4 |    25.67 | False |
| pandas             | census                   |    34.6 |        81.3 |  2.3 |    3.27 |          8 |    15.55 | False |
| pandas             | coverage                 |    13.4 |        23.1 |  1.7 |    1.06 |          4 |     1.32 | False |
| pandas             | timing                   |   134.1 |       212.1 |  1.6 |    3.27 |         16 |     4.07 | False |
| pandas             | traced                   |   183.8 |       880.0 |  4.8 |    9.76 |          8 |     11.1 | False |
| pandas             | tests-released           |    84.5 |       485.8 |  5.7 |     9.0 |          8 |    10.86 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |         12 |     0.04 | False |
| pandas             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |         12 |     0.04 | False |
| pandas             | tests-fix-unsafe         |    79.6 |       600.6 |  7.5 |    12.2 |         12 |    15.37 | False |
| pandas             | tests-infer-basedpyright |    80.2 |       600.1 |  7.5 |    12.2 |         12 |    15.24 | False |
| pandas             | tests-infer-ty           |   142.6 |       533.4 |  3.7 |    9.01 |          8 |    10.12 | False |
| pandas             | tests-infer-pyrefly      |    80.1 |       605.2 |  7.6 |   12.22 |         12 |    16.23 | False |
| pandas             | tests-infer-trace        |    81.1 |       598.5 |  7.4 |   12.58 |         12 |    15.31 | False |
| pandas             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |         12 |     0.04 | False |
| pandas             | types-released           |    86.1 |       104.4 |  1.2 |     2.2 |          2 |      2.9 | False |
| pandas             | types-fix-certain        |    66.4 |        99.9 |  1.5 |    2.19 |          2 |     2.92 | False |
| pandas             | types-fix-likely         |   105.3 |       107.0 |  1.0 |    2.21 |          2 |     2.85 | False |
| pandas             | types-fix-unsafe         |    67.9 |        96.1 |  1.4 |    2.16 |          2 |     2.67 | False |
| pandas             | types-infer-basedpyright |    66.4 |        98.5 |  1.5 |    2.27 |          2 |     2.74 | False |
| pandas             | types-infer-ty           |    52.3 |        79.5 |  1.5 |    2.24 |          2 |      2.8 | False |
| pandas             | types-infer-pyrefly      |    53.9 |        82.4 |  1.5 |    2.23 |          2 |      2.7 | False |
| pandas             | types-infer-trace        |    43.5 |        73.3 |  1.7 |    2.19 |          2 |     2.74 | False |
| pandas             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |     0.4 |         0.2 |  0.5 |    0.06 |          6 |     3.69 | False |
| twisted            | fix-certain              |    13.4 |        31.9 |  2.4 |    0.94 |          3 |     1.16 | False |
| twisted            | fix-likely               |    17.6 |        48.0 |  2.7 |    1.41 |          3 |     1.74 | False |
| twisted            | fix-unsafe               |    14.2 |        37.5 |  2.6 |    0.96 |          3 |     1.17 | False |
| twisted            | infer-basedpyright       |    66.9 |       285.8 |  4.3 |    9.46 |          5 |    11.97 | False |
| twisted            | infer-ty                 |    53.9 |       132.2 |  2.5 |    3.79 |          3 |     4.74 | False |
| twisted            | infer-pyrefly            |    28.9 |        91.1 |  3.2 |    3.63 |          4 |     5.24 | False |
| twisted            | census                   |     8.6 |        16.9 |  2.0 |    0.82 |          6 |     3.69 | False |
| twisted            | coverage                 |     2.4 |         5.3 |  2.2 |    0.37 |          3 |     0.46 | False |
| twisted            | timing                   |    17.2 |        26.6 |  1.5 |    0.82 |         16 |      1.0 | False |
| pip                | check                    |     6.4 |         9.6 |  1.5 |    0.54 |          5 |     2.31 | False |
| pip                | fix-certain              |     8.2 |        22.8 |  2.8 |    0.71 |          3 |     0.89 | False |
| pip                | fix-likely               |    10.0 |        27.7 |  2.8 |     0.9 |          3 |     1.09 | False |
| pip                | fix-unsafe               |     7.6 |        21.7 |  2.9 |    0.71 |          3 |     0.86 | False |
| pip                | infer-basedpyright       |    48.3 |       199.6 |  4.1 |    5.36 |          5 |      6.8 | False |
| pip                | infer-ty                 |    30.9 |        78.8 |  2.6 |    2.74 |          3 |     3.69 | False |
| pip                | infer-pyrefly            |    14.8 |        57.4 |  3.9 |    3.14 |          4 |      4.0 | False |
| pip                | census                   |     4.3 |         2.6 |  0.6 |     0.1 |          5 |     2.31 | False |
| pip                | coverage                 |     1.4 |         3.4 |  2.4 |    0.33 |          3 |      0.4 | False |
| pip                | timing                   |    11.6 |        17.6 |  1.5 |    0.54 |         16 |     0.66 | False |
| structlog          | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     0.57 | False |
| structlog          | fix-certain              |     1.6 |         2.3 |  1.4 |    0.24 |          2 |     0.31 | False |
| structlog          | fix-likely               |     1.2 |         2.4 |  2.0 |    0.24 |          2 |      0.3 | False |
| structlog          | fix-unsafe               |     3.2 |         2.5 |  0.8 |    0.27 |          2 |     0.31 | False |
| structlog          | infer-basedpyright       |     6.4 |        10.6 |  1.7 |     0.6 |          2 |     0.77 | False |
| structlog          | infer-ty                 |     3.6 |         4.7 |  1.3 |    0.39 |          2 |     0.49 | False |
| structlog          | infer-pyrefly            |     2.4 |         3.7 |  1.5 |    0.39 |          2 |     0.49 | False |
| structlog          | census                   |     1.0 |         1.0 |  1.0 |    0.16 |          3 |     0.57 | False |
| structlog          | coverage                 |     0.8 |         0.7 |  0.9 |    0.14 |          1 |     0.17 | False |
| structlog          | timing                   |     1.2 |         1.3 |  1.1 |    0.16 |         16 |     0.17 | False |
| structlog          | traced                   |     6.7 |         5.3 |  0.8 |    0.26 |          1 |     0.34 | False |
| structlog          | tests-released           |     2.2 |         2.0 |  0.9 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-unsafe         |     3.0 |         1.8 |  0.6 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-infer-basedpyright |     2.0 |         1.7 |  0.8 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-infer-ty           |     2.6 |         1.9 |  0.7 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-infer-pyrefly      |     1.8 |         1.7 |  0.9 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-infer-trace        |     3.7 |         1.8 |  0.5 |    0.07 |          1 |     0.09 | False |
| structlog          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | types-released           |     0.6 |         0.4 |  0.7 |    0.08 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.6 |         0.4 |  0.7 |    0.07 |          1 |      0.1 | False |
| structlog          | types-fix-likely         |     1.0 |         0.5 |  0.5 |    0.07 |          1 |      0.1 | False |
| structlog          | types-fix-unsafe         |     0.6 |         0.4 |  0.7 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-basedpyright |     0.8 |         0.5 |  0.6 |    0.07 |          1 |      0.1 | False |
| structlog          | types-infer-ty           |     0.6 |         0.4 |  0.7 |    0.07 |          1 |      0.1 | False |
| structlog          | types-infer-pyrefly      |     1.0 |         0.5 |  0.5 |    0.07 |          1 |      0.1 | False |
| structlog          | types-infer-trace        |     0.6 |         0.3 |  0.5 |    0.05 |          1 |      0.1 | False |
| structlog          | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |      0.1 | False |
| attrs              | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          3 |     0.55 | False |
| attrs              | fix-certain              |     2.0 |         2.5 |  1.2 |    0.25 |          2 |      0.3 | False |
| attrs              | fix-likely               |     2.2 |         2.7 |  1.2 |    0.25 |          2 |      0.3 | False |
| attrs              | fix-unsafe               |     5.0 |         2.7 |  0.5 |    0.25 |          2 |      0.3 | False |
| attrs              | infer-basedpyright       |     8.6 |        12.3 |  1.4 |    0.58 |          2 |     0.71 | False |
| attrs              | infer-ty                 |     3.6 |         4.1 |  1.1 |    0.39 |          2 |     0.49 | False |
| attrs              | infer-pyrefly            |     3.4 |         6.8 |  2.0 |    0.54 |          2 |     0.47 | False |
| attrs              | census                   |     1.2 |         0.9 |  0.8 |    0.15 |          3 |     0.55 | False |
| attrs              | coverage                 |     0.6 |         0.6 |  1.0 |    0.14 |          1 |     0.16 | False |
| attrs              | timing                   |     1.2 |         1.2 |  1.0 |    0.15 |         16 |     0.16 | False |
| attrs              | traced                   |     9.6 |        39.2 |  4.1 |    1.57 |          8 |     0.91 | False |
| attrs              | tests-released           |     5.0 |        24.6 |  4.9 |     1.6 |          8 |     0.75 | False |
| attrs              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.75 | False |
| attrs              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.75 | False |
| attrs              | tests-fix-unsafe         |     3.6 |        17.6 |  4.9 |     0.6 |          8 |     0.75 | False |
| attrs              | tests-infer-basedpyright |     2.4 |        12.6 |  5.2 |    0.59 |          8 |     0.75 | False |
| attrs              | tests-infer-ty           |     3.0 |        13.6 |  4.5 |     0.6 |          8 |     0.75 | False |
| attrs              | tests-infer-pyrefly      |     4.6 |        19.7 |  4.3 |    0.61 |          8 |     0.75 | False |
| attrs              | tests-infer-trace        |     3.6 |        17.5 |  4.9 |    0.61 |          8 |     0.75 | False |
| attrs              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.75 | False |
| click              | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     0.66 | False |
| click              | fix-certain              |     1.8 |         2.9 |  1.6 |     0.3 |          2 |     0.36 | False |
| click              | fix-likely               |     1.8 |         3.4 |  1.9 |    0.29 |          2 |     0.35 | False |
| click              | fix-unsafe               |     2.4 |         3.3 |  1.4 |    0.29 |          2 |     0.35 | False |
| click              | infer-basedpyright       |    14.9 |        19.8 |  1.3 |    0.68 |          2 |     0.86 | False |
| click              | infer-ty                 |     5.4 |         7.3 |  1.4 |    0.47 |          2 |     0.57 | False |
| click              | infer-pyrefly            |     3.6 |         8.5 |  2.4 |    0.61 |          2 |     0.59 | False |
| click              | census                   |     2.4 |         1.5 |  0.6 |    0.17 |          4 |     0.66 | False |
| click              | coverage                 |     0.6 |         0.8 |  1.3 |    0.15 |          2 |     0.19 | False |
| click              | timing                   |     1.6 |         1.9 |  1.2 |    0.17 |         16 |      0.2 | False |
| click              | traced                   |    11.5 |        10.9 |  0.9 |    0.29 |          1 |     0.36 | False |
| click              | tests-released           |     6.4 |         5.8 |  0.9 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     6.3 |         5.0 |  0.8 |    0.17 |          1 |     0.21 | False |
| click              | tests-infer-basedpyright |     7.0 |         5.6 |  0.8 |    0.16 |          1 |     0.21 | False |
| click              | tests-infer-ty           |     8.2 |         7.1 |  0.9 |    0.16 |          1 |     0.21 | False |
| click              | tests-infer-pyrefly      |     6.8 |         6.3 |  0.9 |    0.16 |          1 |     0.21 | False |
| click              | tests-infer-trace        |     5.2 |         4.7 |  0.9 |    0.16 |          1 |     0.21 | False |
| click              | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | types-released           |     1.4 |         0.7 |  0.5 |    0.12 |          1 |     0.16 | False |
| click              | types-fix-certain        |     1.2 |         0.8 |  0.7 |     0.1 |          1 |     0.16 | False |
| click              | types-fix-likely         |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.16 | False |
| click              | types-fix-unsafe         |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.16 | False |
| click              | types-infer-basedpyright |     0.8 |         0.6 |  0.7 |    0.09 |          1 |     0.16 | False |
| click              | types-infer-ty           |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.16 | False |
| click              | types-infer-pyrefly      |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.16 | False |
| click              | types-infer-trace        |     0.6 |         0.3 |  0.5 |    0.05 |          1 |     0.16 | False |
| click              | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.16 | False |
| hypercorn          | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     0.65 | False |
| hypercorn          | fix-certain              |     1.8 |         2.8 |  1.6 |    0.24 |          2 |     0.31 | False |
| hypercorn          | fix-likely               |     1.8 |         3.0 |  1.7 |    0.27 |          2 |     0.32 | False |
| hypercorn          | fix-unsafe               |     2.0 |         2.8 |  1.4 |    0.24 |          2 |     0.32 | False |
| hypercorn          | infer-basedpyright       |     8.2 |        16.1 |  2.0 |    0.88 |          3 |     1.12 | False |
| hypercorn          | infer-ty                 |     4.4 |         6.7 |  1.5 |    0.63 |          2 |      0.8 | False |
| hypercorn          | infer-pyrefly            |     3.0 |        10.5 |  3.5 |    0.65 |          3 |     0.81 | False |
| hypercorn          | census                   |     2.2 |         1.3 |  0.6 |    0.17 |          4 |     0.65 | False |
| hypercorn          | coverage                 |     0.8 |         0.8 |  1.0 |    0.14 |          1 |     0.17 | False |
| hypercorn          | timing                   |     1.4 |         1.6 |  1.1 |    0.17 |         16 |      0.2 | False |
| hypercorn          | traced                   |    11.0 |         5.8 |  0.5 |    0.28 |          1 |     0.32 | False |
| hypercorn          | tests-released           |     8.8 |         2.6 |  0.3 |     0.1 |          1 |     0.11 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-fix-unsafe         |     8.1 |         1.5 |  0.2 |     0.1 |          1 |     0.11 | False |
| hypercorn          | tests-infer-basedpyright |     9.4 |         1.7 |  0.2 |     0.1 |          1 |     0.11 | False |
| hypercorn          | tests-infer-ty           |     7.5 |         1.5 |  0.2 |    0.09 |          1 |     0.11 | False |
| hypercorn          | tests-infer-pyrefly      |     7.0 |         1.2 |  0.2 |    0.09 |          1 |     0.11 | False |
| hypercorn          | tests-infer-trace        |     7.4 |         1.3 |  0.2 |    0.09 |          1 |     0.11 | False |
| hypercorn          | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | types-released           |     1.4 |         1.0 |  0.7 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types-fix-certain        |     0.8 |         0.5 |  0.6 |    0.09 |          1 |     0.15 | False |
| hypercorn          | types-fix-likely         |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.15 | False |
| hypercorn          | types-fix-unsafe         |     0.4 |         0.3 |  0.7 |    0.06 |          1 |     0.15 | False |
| hypercorn          | types-infer-basedpyright |     2.0 |         1.0 |  0.5 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types-infer-ty           |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.15 | False |
| hypercorn          | types-infer-pyrefly      |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.15 | False |
| hypercorn          | types-infer-trace        |     1.4 |         1.0 |  0.7 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.15 | False |
| starlette          | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          4 |      0.7 | False |
| starlette          | fix-certain              |     1.6 |         3.0 |  1.9 |    0.27 |          2 |     0.34 | False |
| starlette          | fix-likely               |     1.8 |         3.6 |  2.0 |    0.29 |          2 |     0.35 | False |
| starlette          | fix-unsafe               |     2.0 |         3.2 |  1.6 |    0.27 |          2 |      0.3 | False |
| starlette          | infer-basedpyright       |     5.8 |        16.4 |  2.8 |    1.03 |          3 |     1.34 | False |
| starlette          | infer-ty                 |     2.8 |         5.2 |  1.9 |    0.38 |          3 |     0.82 | False |
| starlette          | infer-pyrefly            |     3.6 |        11.8 |  3.3 |    0.91 |          2 |     0.84 | False |
| starlette          | census                   |     2.6 |         1.6 |  0.6 |    0.18 |          4 |      0.7 | False |
| starlette          | coverage                 |     1.0 |         0.9 |  0.9 |    0.14 |          2 |     0.17 | False |
| starlette          | timing                   |     1.6 |         2.0 |  1.2 |    0.18 |         16 |     0.21 | False |
| starlette          | traced                   |    17.5 |        13.3 |  0.8 |    0.27 |          1 |     0.36 | False |
| starlette          | tests-released           |    14.6 |         8.1 |  0.6 |    0.23 |          1 |     0.27 | False |
| starlette          | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-fix-unsafe         |    10.7 |         6.4 |  0.6 |    0.22 |          1 |     0.27 | False |
| starlette          | tests-infer-basedpyright |     7.2 |         4.7 |  0.7 |    0.23 |          1 |     0.27 | False |
| starlette          | tests-infer-ty           |     8.6 |         5.2 |  0.6 |    0.21 |          1 |     0.27 | False |
| starlette          | tests-infer-pyrefly      |    10.4 |         6.6 |  0.6 |    0.22 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     9.1 |         5.8 |  0.6 |    0.21 |          1 |     0.27 | False |
| starlette          | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | types-released           |     2.0 |         1.5 |  0.8 |    0.14 |          1 |     0.17 | False |
| starlette          | types-fix-certain        |     1.2 |         0.7 |  0.6 |    0.11 |          1 |     0.17 | False |
| starlette          | types-fix-likely         |     2.4 |         1.7 |  0.7 |    0.13 |          1 |     0.17 | False |
| starlette          | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.07 |          1 |     0.17 | False |
| starlette          | types-infer-basedpyright |     1.6 |         1.3 |  0.8 |    0.14 |          1 |     0.17 | False |
| starlette          | types-infer-ty           |     1.0 |         0.7 |  0.7 |    0.12 |          1 |     0.17 | False |
| starlette          | types-infer-pyrefly      |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.17 | False |
| starlette          | types-infer-trace        |     2.0 |         1.4 |  0.7 |    0.14 |          1 |     0.17 | False |
| starlette          | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.17 | False |
| werkzeug           | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.86 | False |
| werkzeug           | fix-certain              |     2.6 |         5.5 |  2.1 |    0.31 |          2 |     0.39 | False |
| werkzeug           | fix-likely               |     2.8 |         6.3 |  2.2 |    0.31 |          2 |     0.39 | False |
| werkzeug           | fix-unsafe               |     2.4 |         5.2 |  2.2 |    0.31 |          3 |     0.39 | False |
| werkzeug           | infer-basedpyright       |     7.6 |        25.3 |  3.3 |    1.21 |          4 |      1.5 | False |
| werkzeug           | infer-ty                 |     5.2 |        11.3 |  2.2 |    0.48 |          3 |     0.94 | False |
| werkzeug           | infer-pyrefly            |     4.4 |        14.4 |  3.3 |    0.84 |          3 |      1.0 | False |
| werkzeug           | census                   |     1.0 |         1.8 |  1.8 |     0.2 |          5 |     0.86 | False |
| werkzeug           | coverage                 |     0.8 |         1.2 |  1.5 |    0.16 |          2 |      0.2 | False |
| werkzeug           | timing                   |     2.4 |         3.1 |  1.3 |     0.2 |         16 |     0.22 | False |
| werkzeug           | traced                   |    13.0 |        14.6 |  1.1 |    0.34 |          1 |     0.37 | False |
| werkzeug           | tests-released           |    11.6 |         8.4 |  0.7 |    0.17 |          1 |      0.2 | False |
| werkzeug           | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-fix-unsafe         |     7.6 |         6.3 |  0.8 |    0.16 |          1 |      0.2 | False |
| werkzeug           | tests-infer-basedpyright |     8.8 |         6.7 |  0.8 |    0.17 |          1 |      0.2 | False |
| werkzeug           | tests-infer-ty           |     7.2 |         5.7 |  0.8 |    0.17 |          1 |      0.2 | False |
| werkzeug           | tests-infer-pyrefly      |     9.0 |         7.5 |  0.8 |    0.16 |          1 |      0.2 | False |
| werkzeug           | tests-infer-trace        |     8.8 |         6.4 |  0.7 |    0.16 |          1 |      0.2 | False |
| werkzeug           | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | types-released           |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-fix-certain        |     1.2 |         1.0 |  0.8 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types-fix-likely         |     1.4 |         0.9 |  0.6 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types-fix-unsafe         |     1.4 |         1.1 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-basedpyright |     1.2 |         1.0 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-ty           |     1.4 |         1.1 |  0.8 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types-infer-pyrefly      |     1.4 |         1.1 |  0.8 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types-infer-trace        |     0.6 |         0.3 |  0.5 |    0.06 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.14 | False |
| mkdocs             | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.04 | False |
| mkdocs             | fix-certain              |     3.8 |         6.3 |  1.7 |    0.35 |          2 |     0.41 | False |
| mkdocs             | fix-likely               |     3.6 |         7.1 |  2.0 |    0.34 |          2 |     0.39 | False |
| mkdocs             | fix-unsafe               |     3.0 |         5.2 |  1.7 |    0.33 |          2 |     0.41 | False |
| mkdocs             | infer-basedpyright       |    15.4 |        36.7 |  2.4 |    1.38 |          3 |     1.72 | False |
| mkdocs             | infer-ty                 |    15.6 |        16.2 |  1.0 |    0.66 |          3 |      1.1 | False |
| mkdocs             | infer-pyrefly            |     5.4 |        15.2 |  2.8 |    0.87 |          3 |     1.11 | False |
| mkdocs             | census                   |     1.4 |         2.0 |  1.4 |    0.24 |          5 |     1.04 | False |
| mkdocs             | coverage                 |     0.8 |         1.3 |  1.6 |    0.17 |          2 |     0.21 | False |
| mkdocs             | timing                   |     2.8 |         3.6 |  1.3 |    0.25 |         16 |     0.29 | False |
| mkdocs             | traced                   |    14.3 |         8.3 |  0.6 |    0.34 |          1 |     0.44 | False |
| mkdocs             | tests-released           |    11.4 |         3.0 |  0.3 |    0.08 |          1 |     0.09 | False |
| mkdocs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-fix-unsafe         |    10.9 |         2.4 |  0.2 |    0.07 |          1 |     0.09 | False |
| mkdocs             | tests-infer-basedpyright |    10.6 |         2.6 |  0.2 |    0.08 |          1 |     0.09 | False |
| mkdocs             | tests-infer-ty           |    15.0 |         3.1 |  0.2 |    0.07 |          1 |     0.09 | False |
| mkdocs             | tests-infer-pyrefly      |     9.6 |         1.9 |  0.2 |    0.08 |          1 |     0.09 | False |
| mkdocs             | tests-infer-trace        |    10.6 |         2.4 |  0.2 |    0.07 |          1 |     0.09 | False |
| mkdocs             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| httpx              | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     0.77 | False |
| httpx              | fix-certain              |     1.6 |         2.7 |  1.7 |    0.25 |          2 |     0.34 | False |
| httpx              | fix-likely               |     2.0 |         3.5 |  1.8 |    0.27 |          2 |     0.34 | False |
| httpx              | fix-unsafe               |     2.0 |         2.8 |  1.4 |    0.25 |          2 |     0.34 | False |
| httpx              | infer-basedpyright       |    10.0 |        14.9 |  1.5 |    0.65 |          2 |     0.82 | False |
| httpx              | infer-ty                 |     4.6 |         6.4 |  1.4 |    0.42 |          2 |     0.61 | False |
| httpx              | infer-pyrefly            |     3.8 |         8.3 |  2.2 |    0.63 |          2 |     0.64 | False |
| httpx              | census                   |     1.0 |         1.1 |  1.1 |    0.17 |          3 |     0.77 | False |
| httpx              | coverage                 |     0.6 |         0.5 |  0.8 |    0.14 |          1 |     0.17 | False |
| httpx              | timing                   |     1.4 |         1.7 |  1.2 |    0.17 |         16 |      0.2 | False |
| httpx              | traced                   |    11.5 |        10.3 |  0.9 |    0.27 |          1 |     0.34 | False |
| httpx              | tests-released           |     8.8 |         6.3 |  0.7 |    0.23 |          1 |     0.25 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-fix-unsafe         |     6.4 |         4.8 |  0.7 |    0.21 |          1 |     0.25 | False |
| httpx              | tests-infer-basedpyright |     7.2 |         5.4 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | tests-infer-ty           |     6.6 |         5.3 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | tests-infer-pyrefly      |     7.0 |         5.4 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | tests-infer-trace        |     5.8 |         4.4 |  0.8 |     0.2 |          1 |     0.25 | False |
| httpx              | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-released           |     6.6 |         5.6 |  0.8 |    0.24 |          1 |      0.3 | False |
| httpx              | types-fix-certain        |     5.2 |         4.8 |  0.9 |     0.2 |          1 |      0.3 | False |
| httpx              | types-fix-likely         |     5.4 |         4.9 |  0.9 |     0.2 |          1 |      0.3 | False |
| httpx              | types-fix-unsafe         |     5.2 |         4.7 |  0.9 |    0.23 |          1 |      0.3 | False |
| httpx              | types-infer-basedpyright |     6.4 |         5.9 |  0.9 |    0.21 |          1 |      0.3 | False |
| httpx              | types-infer-ty           |     7.0 |         5.7 |  0.8 |    0.19 |          1 |      0.3 | False |
| httpx              | types-infer-pyrefly      |     7.6 |         6.7 |  0.9 |    0.19 |          1 |      0.3 | False |
| httpx              | types-infer-trace        |     0.4 |         0.3 |  0.7 |    0.06 |          1 |      0.3 | False |
| httpx              | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.3 | False |
| black              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     0.74 | False |
| black              | fix-certain              |     2.0 |         4.1 |  2.0 |    0.31 |          2 |     0.37 | False |
| black              | fix-likely               |     2.0 |         4.6 |  2.3 |    0.31 |          2 |     0.39 | False |
| black              | fix-unsafe               |     1.8 |         3.8 |  2.1 |    0.31 |          2 |     0.37 | False |
| black              | infer-basedpyright       |    13.0 |        21.5 |  1.7 |    0.76 |          2 |     0.96 | False |
| black              | infer-ty                 |     5.8 |         8.9 |  1.5 |    0.54 |          2 |     0.67 | False |
| black              | infer-pyrefly            |     3.6 |         9.5 |  2.6 |    0.68 |          2 |     0.69 | False |
| black              | census                   |     1.2 |         1.6 |  1.3 |    0.19 |          4 |     0.74 | False |
| black              | coverage                 |     0.6 |         0.9 |  1.5 |    0.16 |          1 |      0.2 | False |
| black              | timing                   |     1.8 |         2.3 |  1.3 |    0.19 |         16 |     0.21 | False |
| black              | traced                   |    11.2 |        58.3 |  5.2 |    0.88 |          8 |      1.1 | False |
| black              | tests-released           |     5.2 |        35.7 |  6.9 |    0.79 |          8 |      1.0 | False |
| black              | tests-fix-certain        |     9.8 |        51.6 |  5.3 |    0.74 |          8 |      1.0 | False |
| black              | tests-fix-likely         |     6.4 |        40.6 |  6.3 |    0.78 |          8 |      1.0 | False |
| black              | tests-fix-unsafe         |     7.0 |        44.9 |  6.4 |    0.79 |          8 |      1.0 | False |
| black              | tests-infer-basedpyright |     7.4 |        48.1 |  6.5 |    0.77 |          8 |      1.0 | False |
| black              | tests-infer-ty           |     5.6 |        37.8 |  6.8 |    0.73 |          8 |      1.0 | False |
| black              | tests-infer-pyrefly      |     7.6 |        49.0 |  6.4 |    0.78 |          8 |      1.0 | False |
| black              | tests-infer-trace        |     7.4 |        49.1 |  6.6 |    0.78 |          8 |      1.0 | False |
| black              | tests                    |    40.6 |       283.7 |  7.0 |    0.78 |          8 |      1.0 | False |
| fastapi            | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     0.86 | False |
| fastapi            | fix-certain              |     3.2 |         4.9 |  1.5 |    0.33 |          2 |      0.4 | False |
| fastapi            | fix-likely               |     3.8 |         5.9 |  1.6 |    0.37 |          2 |      0.5 | False |
| fastapi            | fix-unsafe               |     4.0 |         4.3 |  1.1 |    0.29 |          2 |      0.4 | False |
| fastapi            | infer-basedpyright       |    12.6 |        30.2 |  2.4 |    1.22 |          3 |      1.5 | False |
| fastapi            | infer-ty                 |     7.6 |        11.3 |  1.5 |    0.81 |          2 |     1.02 | False |
| fastapi            | infer-pyrefly            |     5.6 |        14.4 |  2.6 |    0.94 |          2 |     1.09 | False |
| fastapi            | census                   |     3.6 |         2.1 |  0.6 |    0.21 |          4 |     0.86 | False |
| fastapi            | coverage                 |     0.6 |         0.8 |  1.3 |    0.16 |          2 |      0.2 | False |
| fastapi            | timing                   |     2.2 |         2.6 |  1.2 |    0.21 |         16 |     0.25 | False |
| fastapi            | traced                   |    21.0 |       134.4 |  6.4 |    2.44 |          8 |     2.91 | False |
| fastapi            | tests-released           |    23.0 |       132.5 |  5.8 |    2.19 |          8 |     2.57 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.57 | False |
| fastapi            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.57 | False |
| fastapi            | tests-fix-unsafe         |    15.8 |       101.4 |  6.4 |    2.09 |          8 |     2.57 | False |
| fastapi            | tests-infer-basedpyright |    11.8 |        81.1 |  6.9 |    2.06 |          8 |     2.57 | False |
| fastapi            | tests-infer-ty           |    14.6 |        98.6 |  6.8 |    2.04 |          8 |     2.57 | False |
| fastapi            | tests-infer-pyrefly      |    11.2 |        79.0 |  7.1 |    2.05 |          8 |     2.57 | False |
| fastapi            | tests-infer-trace        |    11.2 |        80.9 |  7.2 |     2.0 |          8 |     2.57 | False |
| fastapi            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.57 | False |
| cattrs             | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          4 |      0.7 | False |
| cattrs             | fix-certain              |     1.4 |         2.4 |  1.7 |    0.26 |          1 |     0.32 | False |
| cattrs             | fix-likely               |     2.2 |         3.5 |  1.6 |    0.26 |          2 |     0.31 | False |
| cattrs             | fix-unsafe               |     2.0 |         3.0 |  1.5 |    0.26 |          1 |     0.31 | False |
| cattrs             | infer-basedpyright       |     7.8 |        19.3 |  2.5 |    0.96 |          3 |     1.19 | False |
| cattrs             | infer-ty                 |     6.4 |         7.9 |  1.2 |    0.62 |          2 |     0.76 | False |
| cattrs             | infer-pyrefly            |     3.4 |        10.8 |  3.2 |     0.9 |          2 |     0.77 | False |
| cattrs             | census                   |     1.0 |         1.0 |  1.0 |    0.17 |          4 |      0.7 | False |
| cattrs             | coverage                 |     0.6 |         0.7 |  1.2 |    0.14 |          2 |     0.17 | False |
| cattrs             | timing                   |     1.6 |         1.8 |  1.1 |    0.17 |         16 |      0.2 | False |
| cattrs             | traced                   |    25.2 |       160.4 |  6.4 |     1.4 |          8 |     1.72 | False |
| cattrs             | tests-released           |    29.9 |       127.4 |  4.3 |    1.02 |          8 |     1.27 | False |
| cattrs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.27 | False |
| cattrs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.27 | False |
| cattrs             | tests-fix-unsafe         |    14.4 |       101.5 |  7.0 |    0.98 |          8 |     1.27 | False |
| cattrs             | tests-infer-basedpyright |    19.2 |       106.7 |  5.6 |    0.92 |          8 |     1.27 | False |
| cattrs             | tests-infer-ty           |    21.0 |       138.9 |  6.6 |    0.99 |          8 |     1.27 | False |
| cattrs             | tests-infer-pyrefly      |    16.8 |       120.7 |  7.2 |    1.01 |          8 |     1.27 | False |
| cattrs             | tests-infer-trace        |    18.2 |       123.6 |  6.8 |    0.98 |          8 |     1.27 | False |
| cattrs             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.27 | False |
| pytest             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          5 |     1.11 | False |
| pytest             | fix-certain              |     4.0 |         8.1 |  2.0 |     0.4 |          2 |      0.5 | False |
| pytest             | fix-likely               |     5.4 |        10.6 |  2.0 |    0.41 |          2 |     0.49 | False |
| pytest             | fix-unsafe               |     3.8 |         8.6 |  2.3 |    0.36 |          2 |      0.5 | False |
| pytest             | infer-basedpyright       |    20.7 |        60.5 |  2.9 |     2.2 |          3 |     2.76 | False |
| pytest             | infer-ty                 |     9.2 |        21.3 |  2.3 |    1.25 |          3 |     1.56 | False |
| pytest             | infer-pyrefly            |    10.8 |        27.8 |  2.6 |    1.75 |          2 |     1.62 | False |
| pytest             | census                   |     6.2 |         4.4 |  0.7 |    0.26 |          5 |     1.11 | False |
| pytest             | coverage                 |     1.2 |         1.8 |  1.5 |    0.19 |          2 |     0.24 | False |
| pytest             | timing                   |     4.2 |         5.6 |  1.3 |    0.27 |         16 |     0.31 | False |
| pytest             | traced                   |    61.5 |       356.3 |  5.8 |     1.8 |          8 |     2.12 | False |
| pytest             | tests-released           |    24.2 |       182.1 |  7.5 |     1.4 |          8 |     2.05 | False |
| pytest             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.05 | False |
| pytest             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.05 | False |
| pytest             | tests-fix-unsafe         |    19.4 |       144.4 |  7.4 |    1.35 |          8 |     2.05 | False |
| pytest             | tests-infer-basedpyright |    20.2 |       146.3 |  7.2 |    1.35 |          8 |     2.05 | False |
| pytest             | tests-infer-ty           |    21.4 |       161.8 |  7.6 |    1.37 |          8 |     2.05 | False |
| pytest             | tests-infer-pyrefly      |    27.7 |       176.9 |  6.4 |    1.32 |          8 |     2.05 | False |
| pytest             | tests-infer-trace        |    18.0 |       136.7 |  7.6 |    1.34 |          8 |     2.05 | False |
| pytest             | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     2.05 | False |
| botocore           | check                    |     0.2 |         0.1 |  0.5 |    0.04 |          6 |     1.14 | False |
| botocore           | fix-certain              |    10.8 |        11.1 |  1.0 |    0.38 |          2 |     0.45 | False |
| botocore           | fix-likely               |     5.6 |        12.7 |  2.3 |    0.45 |          2 |     0.54 | False |
| botocore           | fix-unsafe               |    11.8 |        11.8 |  1.0 |    0.39 |          2 |     0.46 | False |
| botocore           | infer-basedpyright       |    17.4 |        61.2 |  3.5 |    2.38 |          4 |     2.86 | False |
| botocore           | infer-ty                 |     9.8 |        22.9 |  2.3 |    1.21 |          3 |     1.54 | False |
| botocore           | infer-pyrefly            |     6.0 |        15.1 |  2.5 |    0.99 |          3 |     1.61 | False |
| botocore           | census                   |     2.6 |         4.4 |  1.7 |    0.28 |          6 |     1.14 | False |
| botocore           | coverage                 |     0.8 |         1.3 |  1.6 |    0.18 |          2 |     0.22 | False |
| botocore           | timing                   |     5.0 |         7.3 |  1.5 |    0.28 |         16 |     0.32 | False |
| botocore           | traced                   |    30.0 |        92.7 |  3.1 |     5.1 |          8 |     6.45 | False |
| botocore           | tests-released           |    32.3 |        78.2 |  2.4 |    4.84 |          8 |     6.15 | False |
| botocore           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.15 | False |
| botocore           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.15 | False |
| botocore           | tests-fix-unsafe         |    27.2 |        85.4 |  3.1 |    4.78 |          8 |     6.15 | False |
| botocore           | tests-infer-basedpyright |    25.8 |        83.9 |  3.3 |    4.83 |          8 |     6.15 | False |
| botocore           | tests-infer-ty           |    24.6 |        83.4 |  3.4 |    4.82 |          8 |     6.15 | False |
| botocore           | tests-infer-pyrefly      |    26.1 |        81.7 |  3.1 |    4.78 |          8 |     6.15 | False |
| botocore           | tests-infer-trace        |    24.6 |        83.9 |  3.4 |     4.8 |          8 |     6.15 | False |
| botocore           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.15 | False |
| uvicorn            | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     0.69 | False |
| uvicorn            | fix-certain              |     2.2 |         3.6 |  1.6 |    0.26 |          2 |     0.34 | False |
| uvicorn            | fix-likely               |     1.8 |         3.5 |  1.9 |    0.25 |          2 |     0.34 | False |
| uvicorn            | fix-unsafe               |     2.4 |         3.5 |  1.5 |    0.25 |          2 |     0.34 | False |
| uvicorn            | infer-basedpyright       |    10.0 |        23.2 |  2.3 |    1.04 |          2 |      1.3 | False |
| uvicorn            | infer-ty                 |     4.0 |         7.5 |  1.9 |    0.39 |          2 |     0.82 | False |
| uvicorn            | infer-pyrefly            |     4.6 |        13.8 |  3.0 |    0.98 |          2 |     0.85 | False |
| uvicorn            | census                   |     2.4 |         1.5 |  0.6 |    0.18 |          4 |     0.69 | False |
| uvicorn            | coverage                 |     0.6 |         0.7 |  1.2 |    0.14 |          1 |     0.17 | False |
| uvicorn            | timing                   |     1.6 |         2.0 |  1.2 |    0.18 |         16 |      0.2 | False |
| uvicorn            | traced                   |    33.9 |        32.2 |  0.9 |    0.93 |          1 |     1.21 | False |
| uvicorn            | tests-released           |    30.5 |        24.0 |  0.8 |    0.84 |          1 |     1.09 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.09 | False |
| uvicorn            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.09 | False |
| uvicorn            | tests-fix-unsafe         |    39.8 |        21.0 |  0.5 |    0.88 |          1 |     1.09 | False |
| uvicorn            | tests-infer-basedpyright |    38.7 |        20.6 |  0.5 |    0.78 |          1 |     1.09 | False |
| uvicorn            | tests-infer-ty           |    39.6 |        21.8 |  0.6 |    0.81 |          1 |     1.09 | False |
| uvicorn            | tests-infer-pyrefly      |    28.9 |        21.9 |  0.8 |    0.79 |          1 |     1.09 | False |
| uvicorn            | tests-infer-trace        |    40.0 |        20.7 |  0.5 |    0.86 |          1 |     1.09 | False |
| uvicorn            | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.09 | False |
| uvicorn            | types-released           |     2.4 |         1.5 |  0.6 |    0.13 |          1 |     0.17 | False |
| uvicorn            | types-fix-certain        |     2.4 |         1.8 |  0.8 |    0.13 |          1 |     0.17 | False |
| uvicorn            | types-fix-likely         |     1.6 |         1.4 |  0.9 |    0.12 |          1 |     0.17 | False |
| uvicorn            | types-fix-unsafe         |     1.8 |         1.3 |  0.7 |    0.13 |          1 |     0.17 | False |
| uvicorn            | types-infer-basedpyright |     2.0 |         1.6 |  0.8 |    0.12 |          1 |     0.17 | False |
| uvicorn            | types-infer-ty           |     1.2 |         1.0 |  0.8 |    0.12 |          1 |     0.17 | False |
| uvicorn            | types-infer-pyrefly      |     2.4 |         1.5 |  0.6 |    0.12 |          1 |     0.17 | False |
| uvicorn            | types-infer-trace        |     0.6 |         0.3 |  0.5 |    0.07 |          1 |     0.17 | False |
| uvicorn            | types                    |     0.6 |         0.1 |  0.2 |    0.03 |          1 |     0.17 | False |
| mcp                | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.05 | False |
| mcp                | fix-certain              |     3.4 |         7.4 |  2.2 |    0.36 |          2 |     0.45 | False |
| mcp                | fix-likely               |     3.4 |         8.3 |  2.4 |    0.42 |          2 |     0.56 | False |
| mcp                | fix-unsafe               |     8.4 |         7.7 |  0.9 |    0.38 |          3 |     0.42 | False |
| mcp                | infer-basedpyright       |    12.2 |        57.5 |  4.7 |    2.38 |          5 |     3.01 | False |
| mcp                | infer-ty                 |    11.9 |        24.5 |  2.1 |    0.96 |          3 |     1.88 | False |
| mcp                | infer-pyrefly            |     5.8 |        26.4 |  4.6 |    1.48 |          3 |     1.65 | False |
| mcp                | census                   |     1.6 |         2.5 |  1.6 |    0.25 |          6 |     1.05 | False |
| mcp                | coverage                 |     0.8 |         1.2 |  1.5 |    0.17 |          1 |     0.21 | False |
| mcp                | timing                   |     3.2 |         4.4 |  1.4 |    0.25 |         16 |      0.3 | False |
| mcp                | traced                   |    22.2 |       117.7 |  5.3 |    2.38 |          8 |     2.89 | False |
| mcp                | tests-released           |    17.0 |        93.0 |  5.5 |    2.11 |          8 |     2.54 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.54 | False |
| mcp                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.54 | False |
| mcp                | tests-fix-unsafe         |    14.6 |        75.2 |  5.2 |    2.01 |          8 |     2.54 | False |
| mcp                | tests-infer-basedpyright |    13.8 |        72.3 |  5.2 |    2.01 |          8 |     2.54 | False |
| mcp                | tests-infer-ty           |    14.4 |        65.0 |  4.5 |    2.02 |          8 |     2.54 | False |
| mcp                | tests-infer-pyrefly      |    13.6 |        71.9 |  5.3 |    2.02 |          8 |     2.54 | False |
| mcp                | tests-infer-trace        |    13.6 |        71.6 |  5.3 |    2.02 |          8 |     2.54 | False |
| mcp                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.54 | False |
| mcp                | types-released           |    20.9 |        25.8 |  1.2 |    1.25 |          2 |     1.61 | False |
| mcp                | types-fix-certain        |    18.2 |        25.3 |  1.4 |    1.25 |          2 |     1.61 | False |
| mcp                | types-fix-likely         |    21.1 |        28.5 |  1.4 |    1.24 |          2 |     1.61 | False |
| mcp                | types-fix-unsafe         |    17.9 |        23.7 |  1.3 |    1.29 |          2 |     1.61 | False |
| mcp                | types-infer-basedpyright |    18.7 |        25.1 |  1.3 |    1.27 |          2 |     1.61 | False |
| mcp                | types-infer-ty           |    13.2 |        21.6 |  1.6 |    1.25 |          2 |     1.61 | False |
| mcp                | types-infer-pyrefly      |    39.3 |        31.1 |  0.8 |    1.22 |          2 |     1.61 | False |
| mcp                | types-infer-trace        |    11.4 |        16.8 |  1.5 |    1.26 |          2 |     1.61 | False |
| mcp                | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     1.61 | False |
| textual            | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          7 |     1.66 | False |
| textual            | fix-certain              |     6.4 |        14.8 |  2.3 |    0.55 |          2 |     0.65 | False |
| textual            | fix-likely               |     7.6 |        19.7 |  2.6 |     0.6 |          3 |     0.72 | False |
| textual            | fix-unsafe               |     5.0 |        14.1 |  2.8 |    0.53 |          3 |     0.65 | False |
| textual            | infer-basedpyright       |    52.3 |       134.4 |  2.6 |    3.68 |          5 |      4.7 | False |
| textual            | infer-ty                 |    20.4 |        53.7 |  2.6 |    2.04 |          3 |     2.59 | False |
| textual            | infer-pyrefly            |     9.1 |        38.3 |  4.2 |    2.25 |          4 |     2.96 | False |
| textual            | census                   |     2.8 |         5.4 |  1.9 |    0.42 |          7 |     1.66 | False |
| textual            | coverage                 |     1.4 |         2.9 |  2.1 |    0.24 |          2 |      0.3 | False |
| textual            | timing                   |     7.0 |        10.4 |  1.5 |    0.43 |         16 |     0.51 | False |
| pdm                | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     1.92 | False |
| pdm                | fix-certain              |     3.6 |         8.2 |  2.3 |    0.44 |          3 |     0.51 | False |
| pdm                | fix-likely               |     5.6 |        12.1 |  2.2 |    0.53 |          3 |     0.59 | False |
| pdm                | fix-unsafe               |     5.0 |         9.4 |  1.9 |    0.44 |          2 |     0.55 | False |
| pdm                | infer-basedpyright       |    15.4 |        71.5 |  4.6 |     2.7 |          5 |     3.37 | False |
| pdm                | infer-ty                 |     8.9 |        23.6 |  2.7 |    1.06 |          4 |      2.0 | False |
| pdm                | infer-pyrefly            |     7.7 |        29.9 |  3.9 |    1.62 |          3 |     2.17 | False |
| pdm                | census                   |     4.8 |         4.4 |  0.9 |    0.42 |          4 |     1.92 | False |
| pdm                | coverage                 |     1.2 |         1.7 |  1.4 |    0.18 |          2 |     0.22 | False |
| pdm                | timing                   |     4.4 |         6.3 |  1.4 |    0.42 |         16 |     0.49 | False |
| pdm                | traced                   |    21.4 |       114.1 |  5.3 |    1.52 |          8 |     1.91 | False |
| pdm                | tests-released           |    23.4 |       123.1 |  5.3 |    1.22 |          8 |     3.16 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.16 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.16 | False |
| pdm                | tests-fix-unsafe         |    19.6 |       108.2 |  5.5 |    1.19 |          8 |     3.16 | False |
| pdm                | tests-infer-basedpyright |    19.8 |       110.4 |  5.6 |    1.19 |          8 |     3.16 | False |
| pdm                | tests-infer-ty           |    13.8 |        84.4 |  6.1 |    1.19 |          8 |     3.16 | False |
| pdm                | tests-infer-pyrefly      |    14.6 |        93.1 |  6.4 |    1.19 |          8 |     3.16 | False |
| pdm                | tests-infer-trace        |    19.4 |       108.2 |  5.6 |    1.19 |          8 |     3.16 | False |
| pdm                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.16 | False |
| strawberry-graphql | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      2.0 | False |
| strawberry-graphql | fix-certain              |     4.6 |        10.0 |  2.2 |    0.42 |          2 |     0.51 | False |
| strawberry-graphql | fix-likely               |     4.8 |        11.8 |  2.5 |    0.56 |          2 |     0.67 | False |
| strawberry-graphql | fix-unsafe               |     4.2 |         9.8 |  2.3 |    0.42 |          3 |     0.52 | False |
| strawberry-graphql | infer-basedpyright       |    14.2 |        75.8 |  5.3 |    3.08 |          5 |     3.76 | False |
| strawberry-graphql | infer-ty                 |    13.5 |        29.7 |  2.2 |    1.63 |          3 |     2.06 | False |
| strawberry-graphql | infer-pyrefly            |     8.2 |        33.6 |  4.1 |    1.72 |          3 |      2.2 | False |
| strawberry-graphql | census                   |     2.2 |         3.8 |  1.7 |    0.33 |          6 |      2.0 | False |
| strawberry-graphql | coverage                 |     1.0 |         1.6 |  1.6 |    0.18 |          2 |     0.22 | False |
| strawberry-graphql | timing                   |     4.4 |         6.5 |  1.5 |    0.33 |         16 |      0.4 | False |
| strawberry-graphql | traced                   |    19.6 |       113.4 |  5.8 |     1.5 |          8 |     1.84 | False |
| strawberry-graphql | tests-released           |    16.6 |       106.1 |  6.4 |    1.29 |          8 |     1.59 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.59 | False |
| strawberry-graphql | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.59 | False |
| strawberry-graphql | tests-fix-unsafe         |    13.0 |        72.1 |  5.5 |    1.22 |          8 |     1.59 | False |
| strawberry-graphql | tests-infer-basedpyright |    14.0 |        81.6 |  5.8 |    1.22 |          8 |     1.59 | False |
| strawberry-graphql | tests-infer-ty           |    24.7 |        80.3 |  3.3 |    1.21 |          8 |     1.59 | False |
| strawberry-graphql | tests-infer-pyrefly      |    17.4 |        80.0 |  4.6 |     1.2 |          8 |     1.59 | False |
| strawberry-graphql | tests-infer-trace        |     9.4 |        57.9 |  6.2 |    1.23 |          8 |     1.59 | False |
| strawberry-graphql | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.59 | False |
| strawberry-graphql | types-released           |     3.0 |         2.0 |  0.7 |    0.23 |          1 |     0.31 | False |
| strawberry-graphql | types-fix-certain        |     3.6 |         2.1 |  0.6 |    0.23 |          1 |     0.31 | False |
| strawberry-graphql | types-fix-likely         |     2.2 |         1.9 |  0.9 |    0.19 |          1 |     0.31 | False |
| strawberry-graphql | types-fix-unsafe         |     2.4 |         2.0 |  0.8 |     0.2 |          1 |     0.31 | False |
| strawberry-graphql | types-infer-basedpyright |     1.2 |         1.1 |  0.9 |    0.19 |          1 |     0.31 | False |
| strawberry-graphql | types-infer-ty           |     2.6 |         1.9 |  0.7 |    0.24 |          1 |     0.31 | False |
| strawberry-graphql | types-infer-pyrefly      |     1.6 |         1.4 |  0.9 |    0.19 |          1 |     0.31 | False |
| strawberry-graphql | types-infer-trace        |     2.2 |         1.4 |  0.6 |    0.22 |          1 |     0.31 | False |
| strawberry-graphql | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.31 | False |
| pygments           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          6 |     1.84 | False |
| pygments           | fix-certain              |    12.6 |        16.9 |  1.3 |    0.58 |          3 |     0.71 | False |
| pygments           | fix-likely               |     6.8 |        16.8 |  2.5 |    0.57 |          3 |     0.72 | False |
| pygments           | fix-unsafe               |    13.8 |        17.2 |  1.2 |    0.58 |          3 |     0.71 | False |
| pygments           | infer-basedpyright       |    36.9 |       117.0 |  3.2 |    3.33 |          4 |      4.1 | False |
| pygments           | infer-ty                 |    19.4 |        41.6 |  2.1 |    1.75 |          3 |     2.16 | False |
| pygments           | infer-pyrefly            |    10.4 |        31.2 |  3.0 |    1.66 |          3 |     2.54 | False |
| pygments           | census                   |     4.0 |         6.9 |  1.7 |    0.41 |          6 |     1.84 | False |
| pygments           | coverage                 |     1.2 |         2.7 |  2.3 |    0.27 |          3 |     0.34 | False |
| pygments           | timing                   |     7.4 |        11.2 |  1.5 |    0.41 |         16 |     0.49 | False |
| pygments           | traced                   |    30.4 |        37.0 |  1.2 |    0.59 |          1 |     0.75 | False |
| pygments           | tests-released           |    21.7 |        15.5 |  0.7 |    0.23 |          1 |     0.29 | False |
| pygments           | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| pygments           | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| pygments           | tests-fix-unsafe         |    34.5 |        15.3 |  0.4 |    0.23 |          1 |     0.29 | False |
| pygments           | tests-infer-basedpyright |    13.4 |        12.9 |  1.0 |    0.24 |          1 |     0.29 | False |
| pygments           | tests-infer-ty           |    12.6 |        11.8 |  0.9 |    0.23 |          1 |     0.29 | False |
| pygments           | tests-infer-pyrefly      |    14.8 |        13.5 |  0.9 |    0.23 |          1 |     0.29 | False |
| pygments           | tests-infer-trace        |    23.6 |        14.8 |  0.6 |    0.23 |          1 |     0.29 | False |
| pygments           | tests                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| streamlink         | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.32 | False |
| streamlink         | fix-certain              |     5.8 |        11.5 |  2.0 |    0.45 |          3 |     0.55 | False |
| streamlink         | fix-likely               |     4.2 |        11.8 |  2.8 |    0.47 |          3 |     0.59 | False |
| streamlink         | fix-unsafe               |     5.4 |        12.0 |  2.2 |     0.4 |          3 |     0.56 | False |
| streamlink         | infer-basedpyright       |    12.6 |        64.4 |  5.1 |    2.92 |          5 |     3.71 | False |
| streamlink         | infer-ty                 |    15.7 |        33.9 |  2.2 |    1.52 |          3 |      1.9 | False |
| streamlink         | infer-pyrefly            |     7.8 |        32.9 |  4.2 |    1.54 |          3 |     2.09 | False |
| streamlink         | census                   |     5.4 |         5.5 |  1.0 |     0.3 |          7 |     1.32 | False |
| streamlink         | coverage                 |     1.0 |         2.0 |  2.0 |    0.21 |          2 |     0.26 | False |
| streamlink         | timing                   |     5.4 |         8.1 |  1.5 |     0.3 |         16 |     0.36 | False |
| streamlink         | traced                   |    27.5 |        30.9 |  1.1 |    0.42 |          1 |     0.49 | False |
| streamlink         | tests-released           |    17.4 |        13.4 |  0.8 |    0.19 |          1 |     0.21 | False |
| streamlink         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| streamlink         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| streamlink         | tests-fix-unsafe         |    16.0 |        12.2 |  0.8 |    0.18 |          1 |     0.21 | False |
| streamlink         | tests-infer-basedpyright |    13.2 |        11.3 |  0.9 |    0.18 |          1 |     0.21 | False |
| streamlink         | tests-infer-ty           |    11.2 |        10.5 |  0.9 |    0.18 |          1 |     0.21 | False |
| streamlink         | tests-infer-pyrefly      |    11.4 |        10.6 |  0.9 |    0.18 |          1 |     0.21 | False |
| streamlink         | tests-infer-trace        |    13.2 |        11.2 |  0.8 |    0.16 |          1 |     0.21 | False |
| streamlink         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| streamlink         | types-released           |    12.5 |         7.3 |  0.6 |    0.37 |          1 |     0.47 | False |
| streamlink         | types-fix-certain        |     4.8 |         4.7 |  1.0 |    0.35 |          1 |     0.47 | False |
| streamlink         | types-fix-likely         |     5.6 |         5.5 |  1.0 |    0.35 |          1 |     0.47 | False |
| streamlink         | types-fix-unsafe         |     6.8 |         6.2 |  0.9 |    0.36 |          1 |     0.47 | False |
| streamlink         | types-infer-basedpyright |     7.2 |         6.1 |  0.8 |    0.37 |          1 |     0.47 | False |
| streamlink         | types-infer-ty           |     7.0 |         6.6 |  0.9 |    0.37 |          1 |     0.47 | False |
| streamlink         | types-infer-pyrefly      |     5.4 |         4.9 |  0.9 |    0.36 |          1 |     0.47 | False |
| streamlink         | types-infer-trace        |     6.6 |         6.0 |  0.9 |    0.35 |          1 |     0.47 | False |
| streamlink         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.47 | False |
| sphinx             | check                    |     0.4 |         0.2 |  0.5 |    0.05 |          7 |     2.36 | False |
| sphinx             | fix-certain              |     7.2 |        20.4 |  2.8 |    0.62 |          3 |     0.82 | False |
| sphinx             | fix-likely               |     8.8 |        26.2 |  3.0 |    0.82 |          3 |     1.07 | False |
| sphinx             | fix-unsafe               |     7.6 |        22.3 |  2.9 |    0.63 |          3 |      0.8 | False |
| sphinx             | infer-basedpyright       |    31.1 |       133.3 |  4.3 |    4.33 |          5 |     5.44 | False |
| sphinx             | infer-ty                 |    23.2 |        68.6 |  3.0 |    2.31 |          4 |     2.79 | False |
| sphinx             | infer-pyrefly            |    12.0 |        39.7 |  3.3 |    2.48 |          4 |      3.0 | False |
| sphinx             | census                   |     3.7 |         6.9 |  1.9 |    0.44 |          7 |     2.36 | False |
| sphinx             | coverage                 |     1.6 |         3.8 |  2.4 |    0.27 |          2 |     0.34 | False |
| sphinx             | timing                   |     9.4 |        14.4 |  1.5 |    0.44 |         16 |     0.57 | False |
| sphinx             | traced                   |    22.0 |       134.5 |  6.1 |    1.69 |          8 |     2.09 | False |
| sphinx             | tests-released           |    19.6 |       138.9 |  7.1 |    1.36 |          8 |     2.07 | False |
| sphinx             | tests-fix-certain        |    15.8 |       114.1 |  7.2 |    1.32 |          8 |     2.07 | False |
| sphinx             | tests-fix-likely         |    16.0 |       115.0 |  7.2 |    1.31 |          8 |     2.07 | False |
| sphinx             | tests-fix-unsafe         |    12.0 |        88.5 |  7.4 |    1.31 |          8 |     2.07 | False |
| sphinx             | tests-infer-basedpyright |    13.2 |        96.4 |  7.3 |    1.32 |          8 |     2.07 | False |
| sphinx             | tests-infer-ty           |    15.4 |       113.2 |  7.4 |    1.31 |          8 |     2.07 | False |
| sphinx             | tests-infer-pyrefly      |    15.4 |       113.1 |  7.3 |    1.31 |          8 |     2.07 | False |
| sphinx             | tests-infer-trace        |    16.0 |       116.9 |  7.3 |    1.32 |          8 |     2.07 | False |
| sphinx             | tests                    |   128.2 |       942.7 |  7.4 |    1.65 |          8 |     2.07 | False |
| sphinx             | types-released           |     9.1 |         6.5 |  0.7 |    0.32 |          1 |     0.41 | False |
| sphinx             | types-fix-certain        |     5.4 |         4.9 |  0.9 |    0.25 |          1 |     0.41 | False |
| sphinx             | types-fix-likely         |     7.0 |         5.8 |  0.8 |    0.26 |          1 |     0.41 | False |
| sphinx             | types-fix-unsafe         |     8.8 |         6.9 |  0.8 |    0.32 |          1 |     0.41 | False |
| sphinx             | types-infer-basedpyright |    13.8 |         7.6 |  0.6 |    0.29 |          1 |     0.41 | False |
| sphinx             | types-infer-ty           |     4.6 |         4.2 |  0.9 |     0.3 |          1 |     0.41 | False |
| sphinx             | types-infer-pyrefly      |     8.4 |         6.2 |  0.7 |    0.24 |          1 |     0.41 | False |
| sphinx             | types-infer-trace        |     5.8 |         4.5 |  0.8 |    0.28 |          1 |     0.41 | False |
| sphinx             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.41 | False |
| tox                | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.24 | False |
| tox                | fix-certain              |     4.0 |         7.1 |  1.8 |     0.3 |          2 |     0.42 | False |
| tox                | fix-likely               |     4.6 |         9.3 |  2.0 |    0.37 |          2 |     0.47 | False |
| tox                | fix-unsafe               |     3.6 |         6.4 |  1.8 |     0.3 |          2 |     0.42 | False |
| tox                | infer-basedpyright       |    11.2 |        52.4 |  4.7 |    2.23 |          5 |     2.75 | False |
| tox                | infer-ty                 |     8.2 |        19.6 |  2.4 |    1.32 |          2 |     1.64 | False |
| tox                | infer-pyrefly            |     6.2 |        13.8 |  2.2 |    0.95 |          3 |     1.72 | False |
| tox                | census                   |     1.4 |         2.1 |  1.5 |    0.23 |          5 |     1.24 | False |
| tox                | coverage                 |     0.8 |         1.3 |  1.6 |    0.17 |          1 |      0.2 | False |
| tox                | timing                   |     3.0 |         4.3 |  1.4 |    0.23 |         16 |     0.27 | False |
| tox                | traced                   |    26.6 |       149.7 |  5.6 |    1.61 |          8 |      2.0 | False |
| tox                | tests-released           |    32.8 |       114.8 |  3.5 |    1.35 |          8 |      1.8 | False |
| tox                | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      1.8 | False |
| tox                | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      1.8 | False |
| tox                | tests-fix-unsafe         |    22.2 |       121.5 |  5.5 |    1.29 |          8 |      1.8 | False |
| tox                | tests-infer-basedpyright |    17.2 |        96.7 |  5.6 |    1.35 |          8 |      1.8 | False |
| tox                | tests-infer-ty           |    16.4 |        91.2 |  5.6 |    1.28 |          8 |      1.8 | False |
| tox                | tests-infer-pyrefly      |    16.8 |       100.9 |  6.0 |     1.3 |          8 |      1.8 | False |
| tox                | tests-infer-trace        |    19.0 |       108.8 |  5.7 |    1.29 |          8 |      1.8 | False |
| tox                | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      1.8 | False |
| pint               | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.47 | False |
| pint               | fix-certain              |     6.0 |         9.3 |  1.6 |    0.41 |          2 |     0.47 | False |
| pint               | fix-likely               |     6.6 |        12.6 |  1.9 |    0.48 |          2 |     0.64 | False |
| pint               | fix-unsafe               |     3.6 |         8.3 |  2.3 |     0.4 |          2 |     0.49 | False |
| pint               | infer-basedpyright       |    50.9 |       123.1 |  2.4 |    3.38 |          2 |     4.25 | False |
| pint               | infer-ty                 |    18.4 |        50.3 |  2.7 |    2.56 |          3 |     3.66 | False |
| pint               | infer-pyrefly            |     7.6 |        28.8 |  3.8 |    1.57 |          3 |     2.27 | False |
| pint               | census                   |     2.2 |         3.4 |  1.5 |    0.36 |          6 |     1.47 | False |
| pint               | coverage                 |     1.0 |         1.4 |  1.4 |    0.19 |          2 |     0.24 | False |
| pint               | timing                   |     4.8 |         6.5 |  1.4 |    0.36 |         16 |     0.42 | False |
| pint               | traced                   |    44.3 |        44.7 |  1.0 |    0.41 |          1 |     0.51 | False |
| pint               | tests-released           |    32.1 |        28.9 |  0.9 |    0.15 |          1 |     0.17 | False |
| pint               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | tests-fix-unsafe         |    30.5 |        28.1 |  0.9 |    0.15 |          1 |     0.17 | False |
| pint               | tests-infer-basedpyright |    36.3 |        30.4 |  0.8 |    0.15 |          1 |     0.17 | False |
| pint               | tests-infer-ty           |    28.1 |        27.9 |  1.0 |    0.15 |          1 |     0.17 | False |
| pint               | tests-infer-pyrefly      |    30.7 |        28.6 |  0.9 |    0.15 |          1 |     0.17 | False |
| pint               | tests-infer-trace        |    40.8 |        30.8 |  0.8 |    0.13 |          1 |     0.17 | False |
| pint               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | types-released           |     6.4 |        10.4 |  1.6 |    0.53 |          2 |      0.7 | False |
| pint               | types-fix-certain        |     6.0 |         9.9 |  1.7 |    0.54 |          2 |      0.7 | False |
| pint               | types-fix-likely         |     6.0 |         9.5 |  1.6 |    0.54 |          2 |      0.7 | False |
| pint               | types-fix-unsafe         |     6.8 |        10.0 |  1.5 |    0.53 |          2 |      0.7 | False |
| pint               | types-infer-basedpyright |     7.2 |        10.2 |  1.4 |    0.54 |          2 |      0.7 | False |
| pint               | types-infer-ty           |     6.0 |        10.0 |  1.7 |    0.53 |          2 |      0.7 | False |
| pint               | types-infer-pyrefly      |     7.8 |        10.0 |  1.3 |    0.54 |          2 |      0.7 | False |
| pint               | types-infer-trace        |     6.0 |         9.6 |  1.6 |    0.54 |          2 |      0.7 | False |
| pint               | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |      0.7 | False |
| altair             | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.55 | False |
| altair             | fix-certain              |     7.4 |        12.7 |  1.7 |    0.72 |          2 |     0.86 | False |
| altair             | fix-likely               |     8.6 |        14.3 |  1.7 |     0.8 |          2 |     1.01 | False |
| altair             | fix-unsafe               |     9.5 |        12.6 |  1.3 |    0.72 |          2 |     0.86 | False |
| altair             | infer-basedpyright       |    28.6 |        60.7 |  2.1 |    2.75 |          3 |     3.44 | False |
| altair             | infer-ty                 |    14.7 |        22.4 |  1.5 |    1.48 |          2 |     1.85 | False |
| altair             | infer-pyrefly            |    10.6 |        24.2 |  2.3 |    1.89 |          1 |      2.5 | False |
| altair             | census                   |     2.6 |         3.8 |  1.5 |    0.66 |          5 |     2.55 | False |
| altair             | coverage                 |     1.2 |         2.0 |  1.7 |    0.27 |          1 |     0.34 | False |
| altair             | timing                   |     6.4 |         8.1 |  1.3 |    0.65 |         16 |     0.77 | False |
| altair             | traced                   |    32.2 |       186.3 |  5.8 |    5.89 |          8 |     6.59 | False |
| altair             | tests-released           |    25.8 |       168.6 |  6.5 |    5.04 |          8 |     6.01 | False |
| altair             | tests-fix-certain        |    24.6 |       154.7 |  6.3 |    4.75 |          8 |     6.01 | False |
| altair             | tests-fix-likely         |    23.5 |       153.6 |  6.5 |    4.97 |          8 |     6.01 | False |
| altair             | tests-fix-unsafe         |    23.4 |       151.7 |  6.5 |    4.72 |          8 |     6.01 | False |
| altair             | tests-infer-basedpyright |    23.4 |       151.4 |  6.5 |    4.81 |          8 |     6.01 | False |
| altair             | tests-infer-ty           |    23.9 |       152.9 |  6.4 |    4.93 |          8 |     6.01 | False |
| altair             | tests-infer-pyrefly      |    24.2 |       153.3 |  6.3 |    4.86 |          8 |     6.01 | False |
| altair             | tests-infer-trace        |    23.4 |       149.8 |  6.4 |    4.78 |          8 |     6.01 | False |
| altair             | tests                    |    66.7 |       453.1 |  6.8 |     4.9 |          8 |     6.01 | False |
| altair             | types-released           |     8.8 |         6.5 |  0.7 |    0.42 |          1 |     0.56 | False |
| altair             | types-fix-certain        |     6.2 |         5.7 |  0.9 |    0.38 |          1 |     0.56 | False |
| altair             | types-fix-likely         |     7.0 |         6.2 |  0.9 |    0.41 |          1 |     0.56 | False |
| altair             | types-fix-unsafe         |     5.2 |         4.8 |  0.9 |    0.38 |          1 |     0.56 | False |
| altair             | types-infer-basedpyright |     9.1 |         6.4 |  0.7 |    0.38 |          1 |     0.56 | False |
| altair             | types-infer-ty           |     7.6 |         5.8 |  0.8 |    0.44 |          1 |     0.56 | False |
| altair             | types-infer-pyrefly      |     8.2 |         6.3 |  0.8 |    0.38 |          1 |     0.56 | False |
| altair             | types-infer-trace        |     5.6 |         4.7 |  0.8 |    0.42 |          1 |     0.56 | False |
| altair             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.56 | False |
| seaborn            | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     1.71 | False |
| seaborn            | fix-certain              |     7.8 |        11.2 |  1.4 |    0.45 |          2 |     0.59 | False |
| seaborn            | fix-likely               |     5.2 |        12.0 |  2.3 |    0.55 |          3 |     0.67 | False |
| seaborn            | fix-unsafe               |     9.9 |        12.4 |  1.3 |    0.45 |          2 |      0.6 | False |
| seaborn            | infer-basedpyright       |    46.0 |        98.5 |  2.1 |    3.04 |          2 |     3.69 | False |
| seaborn            | infer-ty                 |    17.5 |        31.5 |  1.8 |    1.25 |          2 |      1.6 | False |
| seaborn            | infer-pyrefly            |    16.5 |        25.5 |  1.5 |    1.57 |          2 |     2.02 | False |
| seaborn            | census                   |     3.2 |         4.4 |  1.4 |     0.4 |          5 |     1.71 | False |
| seaborn            | coverage                 |     0.8 |         1.3 |  1.6 |    0.18 |          2 |     0.22 | False |
| seaborn            | timing                   |     6.2 |         8.5 |  1.4 |     0.4 |         16 |     0.49 | False |
| seaborn            | traced                   |    69.1 |       571.0 |  8.3 |    5.15 |          8 |     6.47 | False |
| seaborn            | tests-released           |    59.2 |       571.7 |  9.7 |    4.83 |          8 |     6.05 | False |
| seaborn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.05 | False |
| seaborn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.05 | False |
| seaborn            | tests-fix-unsafe         |    60.4 |       543.2 |  9.0 |    4.81 |          8 |     6.05 | False |
| seaborn            | tests-infer-basedpyright |    54.5 |       534.7 |  9.8 |    4.72 |          8 |     6.05 | False |
| seaborn            | tests-infer-ty           |    54.4 |       545.3 | 10.0 |    4.83 |          8 |     6.05 | False |
| seaborn            | tests-infer-pyrefly      |    59.1 |       550.0 |  9.3 |    4.83 |          8 |     6.05 | False |
| seaborn            | tests-infer-trace        |    64.9 |       564.1 |  8.7 |    4.88 |          8 |     6.05 | False |
| seaborn            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.05 | False |
| seaborn            | types-released           |     1.6 |         1.0 |  0.6 |    0.16 |          1 |     0.21 | False |
| seaborn            | types-fix-certain        |     4.2 |         1.4 |  0.3 |    0.16 |          1 |     0.21 | False |
| seaborn            | types-fix-likely         |     1.2 |         0.9 |  0.8 |    0.15 |          1 |     0.21 | False |
| seaborn            | types-fix-unsafe         |     1.4 |         1.0 |  0.7 |    0.15 |          1 |     0.21 | False |
| seaborn            | types-infer-basedpyright |     1.2 |         0.9 |  0.8 |    0.15 |          1 |     0.21 | False |
| seaborn            | types-infer-ty           |     2.2 |         1.3 |  0.6 |    0.16 |          1 |     0.21 | False |
| seaborn            | types-infer-pyrefly      |     1.4 |         0.9 |  0.6 |    0.14 |          1 |     0.21 | False |
| seaborn            | types-infer-trace        |     0.8 |         0.6 |  0.7 |    0.17 |          1 |     0.21 | False |
| seaborn            | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| aiohttp            | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     0.97 | False |
| aiohttp            | fix-certain              |     3.6 |         7.5 |  2.1 |    0.37 |          2 |     0.45 | False |
| aiohttp            | fix-likely               |     3.8 |         9.1 |  2.4 |     0.4 |          2 |     0.57 | False |
| aiohttp            | fix-unsafe               |     7.2 |         7.9 |  1.1 |    0.37 |          2 |     0.45 | False |
| aiohttp            | infer-basedpyright       |    26.1 |        56.5 |  2.2 |    1.84 |          2 |      2.3 | False |
| aiohttp            | infer-ty                 |    10.4 |        21.6 |  2.1 |    0.82 |          3 |     1.32 | False |
| aiohttp            | infer-pyrefly            |     7.4 |        14.5 |  2.0 |    0.84 |          3 |     1.32 | False |
| aiohttp            | census                   |     1.2 |         2.2 |  1.8 |    0.23 |          6 |     0.97 | False |
| aiohttp            | coverage                 |     0.8 |         1.3 |  1.6 |    0.18 |          2 |     0.22 | False |
| aiohttp            | timing                   |     3.4 |         4.8 |  1.4 |    0.24 |         16 |     0.27 | False |
| aiohttp            | traced                   |   111.7 |       916.0 |  8.2 |    3.62 |          1 |     4.45 | False |
| aiohttp            | tests-released           |    92.6 |       738.0 |  8.0 |    3.18 |          1 |     3.97 | False |
| aiohttp            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     3.97 | False |
| aiohttp            | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     3.97 | False |
| aiohttp            | tests-fix-unsafe         |    92.6 |       636.8 |  6.9 |     3.0 |          1 |     3.97 | False |
| aiohttp            | tests-infer-basedpyright |   102.6 |       637.6 |  6.2 |    3.02 |          1 |     3.97 | False |
| aiohttp            | tests-infer-ty           |   100.5 |       635.7 |  6.3 |    3.05 |          1 |     3.97 | False |
| aiohttp            | tests-infer-pyrefly      |    89.4 |       655.2 |  7.3 |    3.05 |          1 |     3.97 | False |
| aiohttp            | tests-infer-trace        |    91.4 |       637.3 |  7.0 |    3.06 |          1 |     3.97 | False |
| aiohttp            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     3.97 | False |
| websockets         | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     0.81 | False |
| websockets         | fix-certain              |     2.0 |         4.0 |  2.0 |     0.3 |          2 |     0.37 | False |
| websockets         | fix-likely               |     2.2 |         4.9 |  2.2 |     0.3 |          2 |     0.39 | False |
| websockets         | fix-unsafe               |     6.4 |         5.5 |  0.9 |    0.31 |          2 |     0.37 | False |
| websockets         | infer-basedpyright       |     9.4 |        26.3 |  2.8 |    1.15 |          3 |     1.42 | False |
| websockets         | infer-ty                 |     7.6 |        11.9 |  1.6 |    0.66 |          2 |     0.97 | False |
| websockets         | infer-pyrefly            |     4.2 |         8.5 |  2.0 |    0.79 |          2 |     1.01 | False |
| websockets         | census                   |     1.2 |         1.8 |  1.5 |     0.2 |          4 |     0.81 | False |
| websockets         | coverage                 |     0.8 |         0.9 |  1.1 |    0.15 |          1 |     0.19 | False |
| websockets         | timing                   |     2.0 |         2.6 |  1.3 |     0.2 |         16 |     0.22 | False |
| websockets         | traced                   |    36.7 |        14.0 |  0.4 |     0.3 |          1 |     0.41 | False |
| websockets         | tests-released           |    30.5 |         6.5 |  0.2 |    0.16 |          1 |     0.16 | False |
| websockets         | tests-fix-certain        |    27.9 |         5.6 |  0.2 |    0.13 |          1 |     0.16 | False |
| websockets         | tests-fix-likely         |    28.5 |         5.8 |  0.2 |    0.14 |          1 |     0.16 | False |
| websockets         | tests-fix-unsafe         |    33.4 |         6.0 |  0.2 |    0.13 |          1 |     0.16 | False |
| websockets         | tests-infer-basedpyright |    28.3 |         5.5 |  0.2 |    0.14 |          1 |     0.16 | False |
| websockets         | tests-infer-ty           |    30.9 |         5.8 |  0.2 |    0.12 |          1 |     0.16 | False |
| websockets         | tests-infer-pyrefly      |    26.5 |         5.4 |  0.2 |    0.13 |          1 |     0.16 | False |
| websockets         | tests-infer-trace        |    27.5 |         5.6 |  0.2 |    0.12 |          1 |     0.16 | False |
| websockets         | tests                    |   200.2 |        11.7 |  0.1 |    0.12 |          1 |     0.16 | False |
| websockets         | types-released           |     2.2 |         0.9 |  0.4 |    0.11 |          1 |     0.15 | False |
| websockets         | types-fix-certain        |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.15 | False |
| websockets         | types-fix-likely         |     1.4 |         0.9 |  0.6 |     0.1 |          1 |     0.15 | False |
| websockets         | types-fix-unsafe         |     1.0 |         0.6 |  0.6 |     0.1 |          1 |     0.15 | False |
| websockets         | types-infer-basedpyright |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.15 | False |
| websockets         | types-infer-ty           |     1.0 |         0.7 |  0.7 |    0.11 |          1 |     0.15 | False |
| websockets         | types-infer-pyrefly      |     1.0 |         0.8 |  0.8 |     0.1 |          1 |     0.15 | False |
| websockets         | types-infer-trace        |     1.2 |         0.8 |  0.7 |    0.11 |          1 |     0.15 | False |
| websockets         | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| anyio              | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     0.81 | False |
| anyio              | fix-certain              |     3.0 |         4.6 |  1.5 |    0.27 |          2 |     0.39 | False |
| anyio              | fix-likely               |     2.6 |         5.0 |  1.9 |    0.28 |          2 |     0.39 | False |
| anyio              | fix-unsafe               |     2.8 |         4.6 |  1.6 |    0.28 |          2 |     0.37 | False |
| anyio              | infer-basedpyright       |    15.3 |        29.4 |  1.9 |    1.16 |          2 |     1.41 | False |
| anyio              | infer-ty                 |     6.8 |        11.3 |  1.7 |    0.83 |          2 |     1.05 | False |
| anyio              | infer-pyrefly            |     4.8 |        13.5 |  2.8 |    0.97 |          2 |     1.04 | False |
| anyio              | census                   |     2.4 |         2.0 |  0.8 |     0.2 |          4 |     0.81 | False |
| anyio              | coverage                 |     0.8 |         0.9 |  1.1 |    0.15 |          1 |     0.19 | False |
| anyio              | timing                   |     2.2 |         2.8 |  1.3 |     0.2 |         16 |     0.24 | False |
| anyio              | traced                   |   121.7 |        63.3 |  0.5 |    0.31 |          1 |     0.44 | False |
| anyio              | tests-released           |   110.9 |        49.5 |  0.4 |     0.3 |          1 |      0.4 | False |
| anyio              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.4 | False |
| anyio              | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.4 | False |
| anyio              | tests-fix-unsafe         |   105.2 |        50.2 |  0.5 |    0.27 |          1 |      0.4 | False |
| anyio              | tests-infer-basedpyright |   127.5 |        51.5 |  0.4 |    0.27 |          1 |      0.4 | False |
| anyio              | tests-infer-ty           |   126.7 |        51.1 |  0.4 |    0.27 |          1 |      0.4 | False |
| anyio              | tests-infer-pyrefly      |   103.3 |        47.9 |  0.5 |    0.28 |          1 |      0.4 | False |
| anyio              | tests-infer-trace        |   107.5 |        46.9 |  0.4 |    0.27 |          1 |      0.4 | False |
| anyio              | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.4 | False |
| zarr               | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.32 | False |
| zarr               | fix-certain              |     3.8 |         8.8 |  2.3 |    0.38 |          3 |     0.46 | False |
| zarr               | fix-likely               |     6.4 |        13.0 |  2.0 |    0.53 |          2 |     0.75 | False |
| zarr               | fix-unsafe               |     9.2 |        10.2 |  1.1 |     0.4 |          2 |     0.52 | False |
| zarr               | infer-basedpyright       |    28.1 |        89.6 |  3.2 |    2.98 |          5 |     3.56 | False |
| zarr               | infer-ty                 |    19.1 |        36.3 |  1.9 |    1.81 |          3 |     2.25 | False |
| zarr               | infer-pyrefly            |     7.2 |        30.5 |  4.2 |    1.71 |          3 |     2.26 | False |
| zarr               | census                   |     4.0 |         4.2 |  1.1 |    0.31 |          5 |     1.32 | False |
| zarr               | coverage                 |     1.2 |         1.6 |  1.3 |    0.19 |          1 |     0.24 | False |
| zarr               | timing                   |     4.2 |         6.3 |  1.5 |    0.31 |         16 |     0.37 | False |
| zarr               | traced                   |    83.7 |       242.6 |  2.9 |     2.6 |          8 |     3.29 | False |
| zarr               | tests-released           |    74.7 |       210.6 |  2.8 |    2.46 |          8 |     3.21 | False |
| zarr               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.21 | False |
| zarr               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.21 | False |
| zarr               | tests-fix-unsafe         |    48.8 |       159.3 |  3.3 |    2.36 |          8 |     3.21 | False |
| zarr               | tests-infer-basedpyright |    43.2 |       143.0 |  3.3 |    2.31 |          8 |     3.21 | False |
| zarr               | tests-infer-ty           |    43.2 |       143.6 |  3.3 |     2.3 |          8 |     3.21 | False |
| zarr               | tests-infer-pyrefly      |    65.9 |       188.7 |  2.9 |    2.37 |          8 |     3.21 | False |
| zarr               | tests-infer-trace        |    65.9 |       184.7 |  2.8 |    2.32 |          8 |     3.21 | False |
| zarr               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     3.21 | False |
| joblib             | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     1.26 | False |
| joblib             | fix-certain              |     4.4 |         7.5 |  1.7 |    0.36 |          2 |     0.42 | False |
| joblib             | fix-likely               |     4.8 |         8.5 |  1.8 |    0.39 |          2 |     0.51 | False |
| joblib             | fix-unsafe               |    10.8 |         8.7 |  0.8 |    0.36 |          2 |     0.42 | False |
| joblib             | infer-basedpyright       |    27.5 |        67.5 |  2.5 |    2.44 |          3 |     3.09 | False |
| joblib             | infer-ty                 |    16.2 |        26.1 |  1.6 |    1.35 |          2 |     1.74 | False |
| joblib             | infer-pyrefly            |     7.2 |        15.1 |  2.1 |    1.29 |          2 |     1.65 | False |
| joblib             | census                   |     4.0 |         3.7 |  0.9 |     0.3 |          4 |     1.26 | False |
| joblib             | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          1 |     0.21 | False |
| joblib             | timing                   |     3.8 |         5.1 |  1.3 |    0.31 |         16 |     0.36 | False |
| joblib             | traced                   |   163.1 |       521.4 |  3.2 |    1.08 |          1 |     1.34 | False |
| joblib             | tests-released           |   163.8 |       498.9 |  3.0 |    1.06 |          1 |     1.36 | False |
| joblib             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     1.36 | False |
| joblib             | tests-fix-unsafe         |   183.7 |       496.8 |  2.7 |    1.09 |          1 |     1.36 | False |
| joblib             | tests-infer-basedpyright |   148.2 |       491.2 |  3.3 |    1.05 |          1 |     1.36 | False |
| joblib             | tests-infer-ty           |   156.2 |       494.1 |  3.2 |    1.07 |          1 |     1.36 | False |
| joblib             | tests-infer-pyrefly      |   143.4 |       518.3 |  3.6 |    1.06 |          1 |     1.36 | False |
| joblib             | tests-infer-trace        |   157.9 |       496.0 |  3.1 |    1.06 |          1 |     1.36 | False |
| joblib             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     1.36 | False |
| networkx           | check                    |     5.4 |        13.1 |  2.4 |    0.93 |          7 |     4.41 | False |
| networkx           | fix-certain              |    14.2 |        36.5 |  2.6 |    1.13 |          3 |     1.39 | False |
| networkx           | fix-likely               |    17.0 |        48.9 |  2.9 |    1.72 |          3 |     2.12 | False |
| networkx           | fix-unsafe               |    14.8 |        41.3 |  2.8 |    1.15 |          3 |     1.41 | False |
| networkx           | infer-basedpyright       |   105.0 |       388.8 |  3.7 |    8.84 |          4 |    11.47 | False |
| networkx           | infer-ty                 |    49.8 |       122.3 |  2.5 |    3.53 |          2 |      4.6 | False |
| networkx           | infer-pyrefly            |    34.8 |        98.7 |  2.8 |    4.55 |          4 |     6.67 | False |
| networkx           | census                   |     4.2 |         3.9 |  0.9 |    0.11 |          7 |     4.41 | False |
| networkx           | coverage                 |     2.0 |         5.1 |  2.5 |    0.39 |          3 |     0.49 | False |
| networkx           | timing                   |    19.2 |        29.3 |  1.5 |    0.93 |         16 |     1.15 | False |
| networkx           | traced                   |    67.7 |       354.8 |  5.2 |    2.66 |          8 |     3.24 | False |
| networkx           | tests-released           |    30.8 |       259.1 |  8.4 |    2.38 |          8 |     2.92 | False |
| networkx           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.92 | False |
| networkx           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.92 | False |
| networkx           | tests-fix-unsafe         |    29.0 |       257.6 |  8.9 |    2.31 |          8 |     2.92 | False |
| networkx           | tests-infer-basedpyright |    27.1 |       248.9 |  9.2 |    2.28 |          8 |     2.92 | False |
| networkx           | tests-infer-ty           |    30.4 |       261.2 |  8.6 |    2.29 |          8 |     2.92 | False |
| networkx           | tests-infer-pyrefly      |    22.2 |       218.6 |  9.8 |    2.29 |          8 |     2.92 | False |
| networkx           | tests-infer-trace        |    29.0 |       256.9 |  8.9 |    2.33 |          8 |     2.92 | False |
| networkx           | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.92 | False |
| networkx           | types-released           |     5.8 |         3.4 |  0.6 |    0.33 |          1 |     0.44 | False |
| networkx           | types-fix-certain        |     3.4 |         3.0 |  0.9 |    0.32 |          1 |     0.44 | False |
| networkx           | types-fix-likely         |     3.8 |         3.3 |  0.9 |     0.3 |          1 |     0.44 | False |
| networkx           | types-fix-unsafe         |     3.8 |         3.4 |  0.9 |     0.3 |          1 |     0.44 | False |
| networkx           | types-infer-basedpyright |     6.6 |         3.6 |  0.5 |    0.31 |          1 |     0.44 | False |
| networkx           | types-infer-ty           |     3.2 |         2.9 |  0.9 |    0.31 |          1 |     0.44 | False |
| networkx           | types-infer-pyrefly      |     2.4 |         2.3 |  1.0 |    0.28 |          1 |     0.44 | False |
| networkx           | types-infer-trace        |     2.0 |         1.8 |  0.9 |    0.34 |          1 |     0.44 | False |
| networkx           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.44 | False |
| nibabel            | check                    |     0.4 |         0.1 |  0.2 |    0.05 |          7 |     2.45 | False |
| nibabel            | fix-certain              |     8.2 |        19.7 |  2.4 |    0.67 |          3 |     0.82 | False |
| nibabel            | fix-likely               |    31.5 |        34.4 |  1.1 |    0.92 |          2 |     1.17 | False |
| nibabel            | fix-unsafe               |    21.8 |        25.2 |  1.2 |    0.68 |          2 |     0.84 | False |
| nibabel            | infer-basedpyright       |    80.7 |       304.7 |  3.8 |    6.57 |          4 |     7.86 | False |
| nibabel            | infer-ty                 |    78.2 |       264.7 |  3.4 |    3.01 |          4 |     3.84 | False |
| nibabel            | infer-pyrefly            |    17.7 |        64.6 |  3.6 |    2.97 |          3 |     3.77 | False |
| nibabel            | census                   |    12.2 |        12.2 |  1.0 |    0.57 |          7 |     2.45 | False |
| nibabel            | coverage                 |     1.8 |         2.6 |  1.4 |    0.24 |          2 |     0.29 | False |
| nibabel            | timing                   |    12.4 |        18.2 |  1.5 |    0.57 |         16 |     0.71 | False |
| nibabel            | traced                   |    24.7 |       129.1 |  5.2 |    1.17 |          8 |     1.46 | False |
| nibabel            | tests-released           |    15.2 |        92.2 |  6.1 |    1.02 |          8 |      1.3 | False |
| nibabel            | tests-fix-certain        |    15.0 |        93.1 |  6.2 |    1.02 |          8 |      1.3 | False |
| nibabel            | tests-fix-likely         |    15.2 |        94.3 |  6.2 |    1.01 |          8 |      1.3 | False |
| nibabel            | tests-fix-unsafe         |    15.1 |        93.3 |  6.2 |    1.02 |          8 |      1.3 | False |
| nibabel            | tests-infer-basedpyright |    14.8 |        91.0 |  6.1 |    1.04 |          8 |      1.3 | False |
| nibabel            | tests-infer-ty           |    14.6 |        91.6 |  6.3 |    1.02 |          8 |      1.3 | False |
| nibabel            | tests-infer-pyrefly      |    14.4 |        91.6 |  6.4 |    1.02 |          8 |      1.3 | False |
| nibabel            | tests-infer-trace        |    14.8 |        91.6 |  6.2 |    1.01 |          8 |      1.3 | False |
| nibabel            | tests                    |   108.7 |       734.2 |  6.8 |    1.05 |          8 |      1.3 | False |
| nibabel            | types-released           |     3.0 |         2.1 |  0.7 |    0.18 |          1 |     0.22 | False |
| nibabel            | types-fix-certain        |     3.0 |         2.4 |  0.8 |    0.16 |          1 |     0.22 | False |
| nibabel            | types-fix-likely         |     1.4 |         1.3 |  0.9 |    0.15 |          1 |     0.22 | False |
| nibabel            | types-fix-unsafe         |     2.8 |         2.1 |  0.8 |    0.17 |          1 |     0.22 | False |
| nibabel            | types-infer-basedpyright |     2.4 |         2.1 |  0.9 |    0.15 |          1 |     0.22 | False |
| nibabel            | types-infer-ty           |     2.6 |         2.2 |  0.8 |    0.16 |          1 |     0.22 | False |
| nibabel            | types-infer-pyrefly      |     2.4 |         2.0 |  0.8 |    0.17 |          1 |     0.22 | False |
| nibabel            | types-infer-trace        |     1.6 |         1.4 |  0.9 |    0.17 |          1 |     0.22 | False |
| nibabel            | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| narwhals           | check                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.75 | False |
| narwhals           | fix-certain              |     4.2 |        11.2 |  2.7 |     0.4 |          3 |     0.62 | False |
| narwhals           | fix-likely               |     5.8 |        15.0 |  2.6 |    0.83 |          3 |     1.09 | False |
| narwhals           | fix-unsafe               |    11.8 |        13.7 |  1.2 |    0.57 |          3 |     0.75 | False |
| narwhals           | infer-basedpyright       |    24.5 |       105.2 |  4.3 |    3.54 |          4 |     4.45 | False |
| narwhals           | infer-ty                 |    28.9 |        83.3 |  2.9 |    2.79 |          2 |     4.39 | False |
| narwhals           | infer-pyrefly            |    14.9 |        38.7 |  2.6 |     2.7 |          2 |     3.96 | False |
| narwhals           | census                   |     2.6 |         5.0 |  1.9 |    0.39 |          6 |     1.75 | False |
| narwhals           | coverage                 |     1.0 |         2.0 |  2.0 |    0.21 |          2 |     0.26 | False |
| narwhals           | timing                   |     6.0 |         9.1 |  1.5 |     0.4 |         16 |     0.47 | False |
| narwhals           | traced                   |    42.3 |       235.5 |  5.6 |    4.98 |          8 |     6.57 | False |
| narwhals           | tests-released           |    28.2 |       187.2 |  6.6 |    4.61 |          8 |     6.04 | False |
| narwhals           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.04 | False |
| narwhals           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.04 | False |
| narwhals           | tests-fix-unsafe         |    25.2 |       166.9 |  6.6 |    4.54 |          8 |     6.04 | False |
| narwhals           | tests-infer-basedpyright |    25.8 |       171.1 |  6.6 |    4.52 |          8 |     6.04 | False |
| narwhals           | tests-infer-ty           |    24.0 |       167.4 |  7.0 |    4.55 |          8 |     6.04 | False |
| narwhals           | tests-infer-pyrefly      |    23.6 |       162.6 |  6.9 |    4.63 |          8 |     6.04 | False |
| narwhals           | tests-infer-trace        |    26.8 |       162.6 |  6.1 |    4.51 |          8 |     6.04 | False |
| narwhals           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.04 | False |
| narwhals           | types-released           |    24.1 |        47.3 |  2.0 |    1.62 |          2 |     2.05 | False |
| narwhals           | types-fix-certain        |    23.7 |        44.5 |  1.9 |    1.61 |          2 |     2.05 | False |
| narwhals           | types-fix-likely         |    19.4 |        43.6 |  2.2 |    1.51 |          2 |     2.05 | False |
| narwhals           | types-fix-unsafe         |    27.3 |        53.7 |  2.0 |    1.65 |          2 |     2.05 | False |
| narwhals           | types-infer-basedpyright |    25.5 |        53.6 |  2.1 |    1.62 |          2 |     2.05 | False |
| narwhals           | types-infer-ty           |    27.7 |        53.1 |  1.9 |    1.58 |          2 |     2.05 | False |
| narwhals           | types-infer-pyrefly      |    22.9 |        49.3 |  2.2 |    1.67 |          2 |     2.05 | False |
| narwhals           | types-infer-trace        |    20.0 |        36.3 |  1.8 |    1.62 |          2 |     2.05 | False |
| narwhals           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     2.05 | False |
| xarray             | check                    |     0.4 |         0.3 |  0.7 |    0.08 |          6 |     4.45 | False |
| xarray             | fix-certain              |    42.0 |        73.4 |  1.7 |    1.42 |          2 |     1.71 | False |
| xarray             | fix-likely               |    73.7 |       102.0 |  1.4 |    1.97 |          2 |     2.41 | False |
| xarray             | fix-unsafe               |    42.4 |        80.7 |  1.9 |    1.53 |          2 |     1.86 | False |
| xarray             | infer-basedpyright       |   120.0 |       451.0 |  3.8 |   10.83 |          3 |     13.6 | False |
| xarray             | infer-ty                 |    84.5 |       256.6 |  3.0 |    5.27 |          3 |      6.7 | False |
| xarray             | infer-pyrefly            |    52.4 |       142.0 |  2.7 |    5.44 |          3 |     7.25 | False |
| xarray             | census                   |    13.4 |        26.0 |  1.9 |    0.98 |          6 |     4.45 | False |
| xarray             | coverage                 |     2.2 |         6.3 |  2.9 |    0.46 |          3 |     0.55 | False |
| xarray             | timing                   |    42.4 |        60.0 |  1.4 |    0.98 |         16 |     1.17 | False |
| xarray             | traced                   |    44.0 |       181.1 |  4.1 |    2.18 |          8 |     2.77 | False |
| xarray             | tests-released           |    21.0 |       116.8 |  5.6 |    1.98 |          8 |     2.49 | False |
| xarray             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| xarray             | tests-fix-unsafe         |    12.6 |        93.6 |  7.4 |    1.95 |          8 |     2.49 | False |
| xarray             | tests-infer-basedpyright |    17.0 |       113.9 |  6.7 |    1.96 |          8 |     2.49 | False |
| xarray             | tests-infer-ty           |    16.4 |       112.6 |  6.9 |    1.96 |          8 |     2.49 | False |
| xarray             | tests-infer-pyrefly      |    15.2 |       106.4 |  7.0 |    1.95 |          8 |     2.49 | False |
| xarray             | tests-infer-trace        |    21.1 |       123.8 |  5.9 |    1.95 |          8 |     2.49 | False |
| xarray             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.49 | False |
| litestar           | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     2.11 | False |
| litestar           | fix-certain              |     5.2 |        11.7 |  2.2 |    0.61 |          2 |     0.75 | False |
| litestar           | fix-likely               |     8.6 |        17.3 |  2.0 |    0.84 |          2 |     1.11 | False |
| litestar           | fix-unsafe               |     7.6 |        13.6 |  1.8 |    0.61 |          2 |     0.76 | False |
| litestar           | infer-basedpyright       |    26.5 |       113.7 |  4.3 |    3.68 |          4 |      4.5 | False |
| litestar           | infer-ty                 |    22.9 |        50.4 |  2.2 |    2.18 |          3 |     2.62 | False |
| litestar           | infer-pyrefly            |    17.7 |        40.3 |  2.3 |    2.61 |          2 |     3.24 | False |
| litestar           | census                   |     1.8 |         3.4 |  1.9 |    0.41 |          5 |     2.11 | False |
| litestar           | coverage                 |     1.2 |         2.0 |  1.7 |    0.19 |          1 |     0.24 | False |
| litestar           | timing                   |     5.8 |         8.7 |  1.5 |    0.41 |         16 |     0.51 | False |
| litestar           | traced                   |    33.8 |       181.2 |  5.4 |    4.47 |          8 |     5.26 | False |
| litestar           | tests-released           |    28.5 |       167.2 |  5.9 |    4.08 |          8 |     5.11 | False |
| litestar           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.11 | False |
| litestar           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.11 | False |
| litestar           | tests-fix-unsafe         |    22.2 |       128.0 |  5.8 |     3.8 |          8 |     5.11 | False |
| litestar           | tests-infer-basedpyright |    24.2 |       137.5 |  5.7 |     3.8 |          8 |     5.11 | False |
| litestar           | tests-infer-ty           |    25.4 |       132.5 |  5.2 |    3.77 |          8 |     5.11 | False |
| litestar           | tests-infer-pyrefly      |    26.6 |       139.3 |  5.2 |    3.86 |          8 |     5.11 | False |
| litestar           | tests-infer-trace        |    23.8 |       133.9 |  5.6 |    3.79 |          8 |     5.11 | False |
| litestar           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.11 | False |
| litestar           | types-released           |    49.1 |        64.5 |  1.3 |    2.01 |          2 |     2.57 | False |
| litestar           | types-fix-certain        |    47.6 |        65.9 |  1.4 |    1.85 |          2 |     2.57 | False |
| litestar           | types-fix-likely         |    44.7 |        64.7 |  1.4 |    2.04 |          2 |     2.57 | False |
| litestar           | types-fix-unsafe         |    40.1 |        61.6 |  1.5 |    1.88 |          2 |     2.57 | False |
| litestar           | types-infer-basedpyright |    40.1 |        62.2 |  1.6 |     1.9 |          2 |     2.57 | False |
| litestar           | types-infer-ty           |    43.3 |        68.1 |  1.6 |    1.89 |          2 |     2.57 | False |
| litestar           | types-infer-pyrefly      |    41.1 |        62.2 |  1.5 |    1.88 |          2 |     2.57 | False |
| litestar           | types-infer-trace        |    37.6 |        59.8 |  1.6 |    2.04 |          2 |     2.57 | False |
| litestar           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     2.57 | False |
| stripe             | check                    |     0.2 |         0.1 |  0.5 |    0.04 |          8 |     3.75 | False |
| stripe             | fix-certain              |    12.8 |        40.2 |  3.1 |    0.96 |          3 |     1.24 | False |
| stripe             | fix-likely               |    15.2 |        44.0 |  2.9 |    1.14 |          3 |      1.4 | False |
| stripe             | fix-unsafe               |    11.8 |        35.9 |  3.0 |    0.83 |          4 |     1.25 | False |
| stripe             | infer-basedpyright       |  1358.6 |      3234.0 |  2.4 |     4.6 |          3 |     5.82 | False |
| stripe             | infer-ty                 |    48.5 |        96.6 |  2.0 |    2.55 |          4 |     3.32 | False |
| stripe             | infer-pyrefly            |    28.1 |        91.6 |  3.3 |    3.43 |          4 |     4.64 | False |
| stripe             | census                   |     5.2 |        12.3 |  2.4 |    0.81 |          8 |     3.75 | False |
| stripe             | coverage                 |     2.0 |         5.8 |  2.9 |    0.37 |          3 |     0.46 | False |
| stripe             | timing                   |    19.2 |        29.9 |  1.6 |    0.82 |         16 |     0.97 | False |
| celery             | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     2.52 | False |
| celery             | fix-certain              |     8.2 |        14.6 |  1.8 |    0.82 |          2 |     0.96 | False |
| celery             | fix-likely               |    10.2 |        19.8 |  1.9 |    0.94 |          2 |     1.11 | False |
| celery             | fix-unsafe               |     8.8 |        14.7 |  1.7 |    0.82 |          2 |      1.3 | False |
| celery             | infer-basedpyright       |    35.7 |       106.5 |  3.0 |    3.72 |          5 |     4.96 | False |
| celery             | infer-ty                 |    14.0 |        34.1 |  2.4 |    1.93 |          3 |      2.4 | False |
| celery             | infer-pyrefly            |    11.5 |        37.2 |  3.2 |    2.56 |          2 |     2.69 | False |
| celery             | census                   |     4.2 |         6.4 |  1.5 |    0.67 |          5 |     2.52 | False |
| celery             | coverage                 |     0.8 |         1.2 |  1.5 |    0.19 |          2 |     0.24 | False |
| celery             | timing                   |     7.4 |        10.6 |  1.4 |    0.67 |         16 |     0.79 | False |
| celery             | traced                   |   199.0 |        91.9 |  0.5 |    3.12 |          4 |     5.13 | False |
| celery             | tests-released           |    42.3 |        49.0 |  1.2 |    3.28 |          4 |     5.43 | False |
| celery             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     5.43 | False |
| celery             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     5.43 | False |
| celery             | tests-fix-unsafe         |    40.4 |        43.7 |  1.1 |    3.16 |          4 |     5.43 | False |
| celery             | tests-infer-basedpyright |    39.9 |        42.9 |  1.1 |     3.2 |          4 |     5.43 | False |
| celery             | tests-infer-ty           |    42.6 |        44.5 |  1.0 |    3.22 |          4 |     5.43 | False |
| celery             | tests-infer-pyrefly      |    42.2 |        41.6 |  1.0 |    3.19 |          4 |     5.43 | False |
| celery             | tests-infer-trace        |    41.6 |        45.9 |  1.1 |    3.23 |          4 |     5.43 | False |
| celery             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     5.43 | False |
| optuna             | check                    |     0.4 |         0.1 |  0.2 |    0.04 |          6 |     3.32 | False |
| optuna             | fix-certain              |     9.4 |        20.3 |  2.2 |    1.01 |          2 |     1.29 | False |
| optuna             | fix-likely               |    12.2 |        30.4 |  2.5 |    1.43 |          2 |      1.8 | False |
| optuna             | fix-unsafe               |     7.8 |        19.3 |  2.5 |    1.01 |          2 |     1.35 | False |
| optuna             | infer-basedpyright       |    34.1 |       133.7 |  3.9 |    4.95 |          4 |     6.26 | False |
| optuna             | infer-ty                 |    27.9 |        72.6 |  2.6 |    3.07 |          3 |     3.87 | False |
| optuna             | infer-pyrefly            |    15.9 |        53.1 |  3.3 |    3.32 |          3 |     4.36 | False |
| optuna             | census                   |     3.6 |         7.2 |  2.0 |    0.69 |          6 |     3.32 | False |
| optuna             | coverage                 |     1.4 |         1.9 |  1.4 |    0.19 |          2 |     0.22 | False |
| optuna             | timing                   |     9.8 |        14.8 |  1.5 |    0.69 |         16 |     0.87 | False |
| optuna             | traced                   |   166.1 |      1804.9 | 10.9 |    5.11 |          8 |     6.02 | False |
| optuna             | tests-released           |   287.9 |      3005.5 | 10.4 |    4.23 |          8 |     5.34 | False |
| optuna             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.34 | False |
| optuna             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.34 | False |
| optuna             | tests-fix-unsafe         |   126.8 |      1208.0 |  9.5 |    3.86 |          8 |     5.34 | False |
| optuna             | tests-infer-basedpyright |   125.0 |      1165.6 |  9.3 |    3.84 |          8 |     5.34 | False |
| optuna             | tests-infer-ty           |   156.5 |      1488.4 |  9.5 |    3.98 |          8 |     5.34 | False |
| optuna             | tests-infer-pyrefly      |   319.3 |      3354.5 | 10.5 |    4.01 |          8 |     5.34 | False |
| optuna             | tests-infer-trace        |   130.0 |      1247.8 |  9.6 |    3.84 |          8 |     5.34 | False |
| optuna             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.34 | False |
| optuna             | types-released           |     8.4 |         6.3 |  0.8 |    0.46 |          1 |     0.61 | False |
| optuna             | types-fix-certain        |     7.6 |         6.0 |  0.8 |    0.43 |          1 |     0.61 | False |
| optuna             | types-fix-likely         |     6.0 |         5.0 |  0.8 |    0.44 |          1 |     0.61 | False |
| optuna             | types-fix-unsafe         |     5.0 |         4.7 |  0.9 |    0.37 |          1 |     0.61 | False |
| optuna             | types-infer-basedpyright |     6.6 |         5.7 |  0.9 |    0.45 |          1 |     0.61 | False |
| optuna             | types-infer-ty           |     5.6 |         4.6 |  0.8 |    0.36 |          1 |     0.61 | False |
| optuna             | types-infer-pyrefly      |     6.0 |         4.9 |  0.8 |    0.36 |          1 |     0.61 | False |
| optuna             | types-infer-trace        |     6.0 |         5.1 |  0.8 |    0.45 |          1 |     0.61 | False |
| optuna             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.61 | False |
| dask               | check                    |     0.6 |         0.4 |  0.7 |    0.08 |          6 |      5.6 | False |
| dask               | fix-certain              |    35.3 |        76.3 |  2.2 |    1.73 |          2 |      2.2 | False |
| dask               | fix-likely               |    48.6 |       102.3 |  2.1 |    2.39 |          2 |     2.96 | False |
| dask               | fix-unsafe               |    50.0 |       102.2 |  2.0 |    2.44 |          2 |     3.01 | False |
| dask               | infer-basedpyright       |   114.6 |       501.9 |  4.4 |   13.28 |          4 |    16.05 | False |
| dask               | infer-ty                 |    86.9 |       284.0 |  3.3 |    5.79 |          3 |     7.72 | False |
| dask               | infer-pyrefly            |    46.9 |       145.8 |  3.1 |    6.75 |          3 |     8.64 | False |
| dask               | census                   |    17.1 |        31.6 |  1.8 |    1.28 |          6 |      5.6 | False |
| dask               | coverage                 |     2.4 |         6.4 |  2.7 |    0.45 |          3 |     0.56 | False |
| dask               | timing                   |    45.2 |        65.6 |  1.5 |    1.27 |         16 |     1.56 | False |
| dask               | traced                   |   166.9 |      1170.5 |  7.0 |    4.71 |          8 |     5.96 | False |
| dask               | tests-released           |   191.1 |      1096.0 |  5.7 |    4.59 |          8 |     5.72 | False |
| dask               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.72 | False |
| dask               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.72 | False |
| dask               | tests-fix-unsafe         |   119.5 |       990.7 |  8.3 |    4.43 |          8 |     5.72 | False |
| dask               | tests-infer-basedpyright |   127.7 |      1070.5 |  8.4 |    4.48 |          8 |     5.72 | False |
| dask               | tests-infer-ty           |   124.9 |      1013.4 |  8.1 |    4.61 |          8 |     5.72 | False |
| dask               | tests-infer-pyrefly      |   118.5 |      1004.9 |  8.5 |    4.52 |          8 |     5.72 | False |
| dask               | tests-infer-trace        |   116.8 |       996.0 |  8.5 |    4.28 |          8 |     5.72 | False |
| dask               | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.72 | False |
| mypy               | check                    |     4.0 |        10.6 |  2.6 |    0.55 |          7 |     2.69 | False |
| mypy               | fix-certain              |    13.8 |        40.0 |  2.9 |    0.99 |          3 |     1.21 | False |
| mypy               | fix-likely               |    11.2 |        34.9 |  3.1 |    1.05 |          3 |      1.3 | False |
| mypy               | fix-unsafe               |    19.0 |        38.3 |  2.0 |    0.99 |          3 |     1.22 | False |
| mypy               | infer-basedpyright       |    41.3 |       160.5 |  3.9 |    5.01 |          4 |      6.2 | False |
| mypy               | infer-ty                 |    30.9 |        84.9 |  2.7 |     2.9 |          3 |     3.66 | False |
| mypy               | infer-pyrefly            |    19.1 |        56.8 |  3.0 |    2.96 |          3 |     3.89 | False |
| mypy               | census                   |     2.2 |         2.0 |  0.9 |    0.09 |          7 |     2.69 | False |
| mypy               | coverage                 |     1.8 |         4.6 |  2.6 |    0.36 |          3 |     0.45 | False |
| mypy               | timing                   |    13.2 |        20.7 |  1.6 |    0.54 |         16 |     0.66 | False |
| mypy               | traced                   |   311.8 |      2223.7 |  7.1 |    6.32 |          8 |     8.05 | False |
| mypy               | tests-released           |   358.0 |      1935.2 |  5.4 |    6.06 |          8 |      7.7 | False |
| mypy               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      7.7 | False |
| mypy               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      7.7 | False |
| mypy               | tests-fix-unsafe         |   301.5 |      2091.4 |  6.9 |    6.06 |          8 |      7.7 | False |
| mypy               | tests-infer-basedpyright |   305.8 |      1978.6 |  6.5 |    5.49 |          8 |      7.7 | False |
| mypy               | tests-infer-ty           |   393.7 |      1884.0 |  4.8 |    5.64 |          8 |      7.7 | False |
| mypy               | tests-infer-pyrefly      |   371.7 |      1909.1 |  5.1 |    6.36 |          8 |      7.7 | False |
| mypy               | tests-infer-trace        |   322.1 |      2166.0 |  6.7 |    6.16 |          8 |      7.7 | False |
| mypy               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      7.7 | False |
| mypy               | types-released           |    11.6 |        27.1 |  2.3 |    0.62 |          3 |     0.84 | False |
| mypy               | types-fix-certain        |     9.8 |        23.7 |  2.4 |    0.61 |          3 |     0.84 | False |
| mypy               | types-fix-likely         |     6.0 |        15.1 |  2.5 |    0.47 |          3 |     0.84 | False |
| mypy               | types-fix-unsafe         |     9.4 |        22.7 |  2.4 |    0.61 |          3 |     0.84 | False |
| mypy               | types-infer-basedpyright |    10.2 |        25.7 |  2.5 |    0.61 |          3 |     0.84 | False |
| mypy               | types-infer-ty           |    10.2 |        26.0 |  2.5 |    0.61 |          3 |     0.84 | False |
| mypy               | types-infer-pyrefly      |     7.2 |        17.2 |  2.4 |    0.47 |          3 |     0.84 | False |
| mypy               | types-infer-trace        |     9.0 |        23.4 |  2.6 |     0.6 |          3 |     0.84 | False |
| mypy               | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          3 |     0.84 | False |

- standard library, 0.3.7-rc.1+dev, infer-basedpyright: held 13.09 GB beside other steps
- standard library, 0.3.7-rc.1+dev, infer-ty: held 15.55 GB beside other steps
- standard library, 0.3.7-rc.1+dev, infer-pyrefly: held 17.45 GB beside other steps
- pandas, 0.3.7-rc.1+dev, infer-basedpyright: held 15.95 GB beside other steps
- pandas, 0.3.7-rc.1+dev, infer-ty: held 14.75 GB beside other steps
- pandas, 0.3.7-rc.1+dev, infer-pyrefly: held 17.53 GB beside other steps
- pandas, 0.3.7-rc.1+dev, traced: held 9.76 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests-released: held 9.0 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests-fix-unsafe: held 12.2 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests-infer-basedpyright: held 12.2 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests-infer-ty: held 9.01 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests-infer-pyrefly: held 12.22 GB beside other steps
- pandas, 0.3.7-rc.1+dev, tests-infer-trace: held 12.58 GB beside other steps
- twisted, 0.3.7-rc.1+dev, infer-basedpyright: held 9.46 GB beside other steps
- networkx, 0.3.7-rc.1+dev, infer-basedpyright: held 8.84 GB beside other steps
- xarray, 0.3.7-rc.1+dev, infer-basedpyright: held 10.83 GB beside other steps
- dask, 0.3.7-rc.1+dev, infer-basedpyright: held 13.28 GB beside other steps

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
