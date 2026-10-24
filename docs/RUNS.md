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

The run `0.4.3-rc.2` (`python -m tests.corpus`) on super: constricter 0.4.3.dev43+g44c05d551
(`44c05d55167a`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 48 minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter    | Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ------------------ | -------- | -------------- | ----: | --------------: | ------------: | -------: | -------------: | -----------: | ---------: | --------: | -------: | ------: |
| standard library   | 3.14.7   | 0.4.3-rc.2+dev | 1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |         14 |         8 |        0 | 113,750 |
| django             | 5.2.18   | 0.4.3-rc.2+dev |   883 |           9,926 |         2,166 |        0 |          5,084 |            0 |          0 |         1 |        0 |  17,177 |
| sqlalchemy         | 2.1.4    | 0.4.3-rc.2+dev |   258 |           8,825 |         1,636 |        0 |          2,501 |          572 |        128 |         2 |        1 |  13,665 |
| pydantic           | 2.14.0   | 0.4.3-rc.2+dev |   105 |           2,072 |           440 |        0 |            605 |          184 |         15 |         0 |        0 |   3,316 |
| pandas             | 3.0.6    | 0.4.3-rc.2+dev | 1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |          2 |         1 |        1 |  77,931 |
| twisted            | 12.3.0   | 0.4.3-rc.2+dev |   819 |          13,310 |         1,349 |        0 |          3,215 |            0 |          0 |         0 |        0 |  17,874 |
| pip                | 20.3.4   | 0.4.3-rc.2+dev |   366 |           5,902 |         1,150 |        0 |          1,872 |            0 |          0 |         0 |        0 |   8,924 |
| structlog          | 26.1.0   | 0.4.3-rc.2+dev |    21 |             156 |            47 |        0 |            113 |           12 |          1 |         0 |        0 |     329 |
| attrs              | 26.1.0   | 0.4.3-rc.2+dev |    13 |             285 |            50 |        0 |             58 |            2 |          0 |         1 |        0 |     396 |
| click              | 8.5.0    | 0.4.3-rc.2+dev |    17 |             481 |            58 |        0 |             69 |           28 |          1 |         0 |        0 |     637 |
| hypercorn          | 0.18.0   | 0.4.3-rc.2+dev |    39 |             220 |            67 |        0 |             68 |            8 |          0 |         0 |        0 |     363 |
| starlette          | 1.7.0    | 0.4.3-rc.2+dev |    36 |             499 |            99 |        0 |            146 |           18 |          0 |         0 |        0 |     762 |
| werkzeug           | 3.1.9    | 0.4.3-rc.2+dev |    52 |             835 |           235 |        0 |            223 |           15 |          1 |         0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | 0.4.3-rc.2+dev |    61 |           1,674 |           198 |        0 |            460 |            8 |          0 |         0 |        0 |   2,340 |
| httpx              | 0.28.1   | 0.4.3-rc.2+dev |    23 |             395 |           112 |        0 |             62 |            1 |          0 |         0 |        0 |     570 |
| black              | 26.10.0  | 0.4.3-rc.2+dev |    25 |             996 |           232 |        0 |             45 |            5 |          4 |         0 |        0 |   1,282 |
| fastapi            | 0.142.2  | 0.4.3-rc.2+dev |    52 |             586 |           105 |        0 |             51 |           98 |          5 |         0 |        0 |     845 |
| cattrs             | 26.2.1   | 0.4.3-rc.2+dev |    36 |             420 |            70 |        0 |             30 |            9 |          1 |         0 |        0 |     530 |
| pytest             | 9.1.1    | 0.4.3-rc.2+dev |    78 |           2,363 |           470 |        0 |            170 |           33 |          9 |         0 |        0 |   3,045 |
| botocore           | 1.43.108 | 0.4.3-rc.2+dev |    76 |           2,825 |           367 |        0 |            594 |            2 |          0 |         0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | 0.4.3-rc.2+dev |    45 |             363 |            71 |        0 |             55 |           11 |          4 |         0 |        0 |     504 |
| mcp                | 2.3.0    | 0.4.3-rc.2+dev |   124 |           1,356 |           173 |        0 |            191 |          105 |          8 |         0 |        0 |   1,833 |
| textual            | 8.2.8    | 0.4.3-rc.2+dev |   247 |           4,979 |           718 |        0 |            786 |           31 |         26 |         0 |        0 |   6,540 |
| pdm                | 2.29.2   | 0.4.3-rc.2+dev |   128 |           2,114 |           417 |        0 |            187 |           37 |          2 |         0 |        0 |   2,757 |
| strawberry-graphql | 0.332.0  | 0.4.3-rc.2+dev |   244 |           1,436 |           243 |        0 |            127 |          137 |          2 |         0 |        0 |   1,945 |
| pygments           | 2.21.0   | 0.4.3-rc.2+dev |   343 |           1,124 |           539 |        0 |          6,003 |            0 |          0 |         0 |        0 |   7,666 |
| streamlink         | 8.6.1    | 0.4.3-rc.2+dev |   227 |           2,080 |           310 |        0 |            639 |           37 |         11 |         0 |        0 |   3,077 |
| sphinx             | 9.1.0    | 0.4.3-rc.2+dev |   243 |           5,505 |         1,336 |        1 |          1,131 |           73 |         29 |         5 |        3 |   8,083 |
| tox                | 4.64.9   | 0.4.3-rc.2+dev |   129 |           1,369 |           286 |        0 |            107 |           18 |          5 |         0 |        0 |   1,785 |
| **Total**          |          | 0.4.3-rc.2+dev | 7,977 | 234,028 (77.2%) | 28,056 (9.3%) | 1 (0.0%) | 39,012 (12.9%) | 1,635 (0.5%) | 268 (0.1%) | 18 (0.0%) | 5 (0.0%) | 303,023 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | -------------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | 0.4.3-rc.2+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,446 (32.9%) |   6,681 (5.9%) | 13,082 (11.5%) |      0 |    0 |            0 |
| django             | 0.4.3-rc.2+dev |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |  2,622 (15.3%) |     646 (3.8%) |  2,786 (16.2%) |      0 |    0 |            0 |
| sqlalchemy         | 0.4.3-rc.2+dev |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |  1,938 (14.2%) |     350 (2.6%) |     847 (6.2%) |      0 |    0 |            0 |
| pydantic           | 0.4.3-rc.2+dev |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |  1,191 (35.9%) |     146 (4.4%) |    405 (12.2%) |      0 |    0 |            0 |
| pandas             | 0.4.3-rc.2+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,955 (21.8%) | 23,589 (30.3%) | 24,630 (31.6%) |      0 |    0 |            0 |
| twisted            | 0.4.3-rc.2+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,435 (13.6%) |  3,625 (20.3%) |  4,697 (26.3%) |      0 |    0 |            0 |
| pip                | 0.4.3-rc.2+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,270 (25.4%) |     468 (5.2%) |  1,304 (14.6%) |      0 |    0 |            0 |
| structlog          | 0.4.3-rc.2+dev |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |     98 (29.8%) |      15 (4.6%) |      28 (8.5%) |      0 |    0 |            0 |
| attrs              | 0.4.3-rc.2+dev |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |     93 (23.5%) |       9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| click              | 0.4.3-rc.2+dev |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |    302 (47.4%) |      27 (4.2%) |      63 (9.9%) |      0 |    0 |            0 |
| hypercorn          | 0.4.3-rc.2+dev |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |    134 (36.9%) |      20 (5.5%) |     58 (16.0%) |      0 |    0 |            0 |
| starlette          | 0.4.3-rc.2+dev |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |    314 (41.2%) |      57 (7.5%) |     97 (12.7%) |      0 |    0 |            0 |
| werkzeug           | 0.4.3-rc.2+dev |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |    527 (40.3%) |      66 (5.0%) |     127 (9.7%) |      0 |    0 |            0 |
| mkdocs             | 0.4.3-rc.2+dev |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |    810 (34.6%) |    377 (16.1%) |    482 (20.6%) |      0 |    0 |            0 |
| httpx              | 0.4.3-rc.2+dev |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |    234 (41.1%) |     57 (10.0%) |     73 (12.8%) |      0 |    0 |            0 |
| black              | 0.4.3-rc.2+dev |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |    707 (55.1%) |     127 (9.9%) |    163 (12.7%) |      0 |    0 |            0 |
| fastapi            | 0.4.3-rc.2+dev |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |    257 (30.4%) |      40 (4.7%) |      65 (7.7%) |      0 |    0 |            0 |
| cattrs             | 0.4.3-rc.2+dev |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |    105 (19.8%) |      34 (6.4%) |      46 (8.7%) |      0 |    0 |            0 |
| pytest             | 0.4.3-rc.2+dev |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |  1,358 (44.6%) |     156 (5.1%) |     285 (9.4%) |      0 |    0 |            0 |
| botocore           | 0.4.3-rc.2+dev |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |    543 (14.3%) |     174 (4.6%) |    608 (16.1%) |      0 |    0 |            0 |
| uvicorn            | 0.4.3-rc.2+dev |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |    231 (45.8%) |      32 (6.3%) |      47 (9.3%) |      0 |    0 |            0 |
| mcp                | 0.4.3-rc.2+dev |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |    694 (37.9%) |     154 (8.4%) |    236 (12.9%) |      0 |    0 |            0 |
| textual            | 0.4.3-rc.2+dev |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |  2,707 (41.4%) |     482 (7.4%) |    741 (11.3%) |      0 |    0 |            0 |
| pdm                | 0.4.3-rc.2+dev |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |  1,147 (41.6%) |     201 (7.3%) |    323 (11.7%) |      0 |    0 |            0 |
| strawberry-graphql | 0.4.3-rc.2+dev |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |    611 (31.4%) |     167 (8.6%) |    218 (11.2%) |      0 |    0 |            0 |
| pygments           | 0.4.3-rc.2+dev |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |     735 (9.6%) |      79 (1.0%) |     228 (3.0%) |      0 |    0 |            0 |
| streamlink         | 0.4.3-rc.2+dev |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |    682 (22.2%) |     111 (3.6%) |     250 (8.1%) |      0 |    0 |            0 |
| sphinx             | 0.4.3-rc.2+dev |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |  3,230 (40.0%) |     521 (6.4%) |    900 (11.1%) |      0 |    0 |            0 |
| tox                | 0.4.3-rc.2+dev |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |    943 (52.8%) |      82 (4.6%) |     138 (7.7%) |      0 |    0 |            0 |
| **Total**          | 0.4.3-rc.2+dev | 0 / 301,115 | 273,040 / 29,983 | 301,114 / 1,909 | 303,023 / 0 | 81,319 (26.8%) | 38,493 (12.7%) | 52,938 (17.5%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter    | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | -------------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | 0.4.3-rc.2+dev |              1.2% |         33.7% |            39.5% |                  45.1% | +32.6 pts, 32.9% of untyped | +43.9 pts, 44.5% of untyped |
| django             | 0.4.3-rc.2+dev |              0.0% |         15.3% |            19.1% |                  31.5% | +15.3 pts, 15.3% of untyped | +31.5 pts, 31.5% of untyped |
| sqlalchemy         | 0.4.3-rc.2+dev |             15.3% |         27.9% |            30.2% |                  33.5% | +12.7 pts, 14.9% of untyped | +18.2 pts, 21.5% of untyped |
| pydantic           | 0.4.3-rc.2+dev |             22.4% |         52.1% |            55.7% |                  62.2% | +29.6 pts, 38.2% of untyped | +39.7 pts, 51.2% of untyped |
| pandas             | 0.4.3-rc.2+dev |              1.6% |         23.1% |            52.9% |                  54.2% | +21.4 pts, 21.8% of untyped | +52.6 pts, 53.5% of untyped |
| twisted            | 0.4.3-rc.2+dev |              0.0% |         13.6% |            33.9% |                  39.9% | +13.6 pts, 13.6% of untyped | +39.9 pts, 39.9% of untyped |
| pip                | 0.4.3-rc.2+dev |              1.5% |         26.6% |            31.7% |                  40.9% | +25.0 pts, 25.4% of untyped | +39.4 pts, 40.0% of untyped |
| structlog          | 0.4.3-rc.2+dev |             25.6% |         48.7% |            52.2% |                  55.3% | +23.1 pts, 31.0% of untyped | +29.6 pts, 39.9% of untyped |
| attrs              | 0.4.3-rc.2+dev |              0.8% |         24.2% |            26.5% |                  27.0% | +23.5 pts, 23.7% of untyped | +26.3 pts, 26.5% of untyped |
| click              | 0.4.3-rc.2+dev |             31.5% |         65.5% |            68.5% |                  72.6% | +34.0 pts, 49.7% of untyped | +41.1 pts, 60.0% of untyped |
| hypercorn          | 0.4.3-rc.2+dev |             32.4% |         57.9% |            61.7% |                  69.0% | +25.5 pts, 37.7% of untyped | +36.6 pts, 54.1% of untyped |
| starlette          | 0.4.3-rc.2+dev |             10.3% |         48.1% |            55.0% |                  59.8% | +37.9 pts, 42.2% of untyped | +49.6 pts, 55.2% of untyped |
| werkzeug           | 0.4.3-rc.2+dev |             14.3% |         49.2% |            53.6% |                  57.7% | +34.9 pts, 40.8% of untyped | +43.3 pts, 50.6% of untyped |
| mkdocs             | 0.4.3-rc.2+dev |              4.5% |         37.7% |            53.1% |                  57.4% | +33.2 pts, 34.7% of untyped | +52.9 pts, 55.4% of untyped |
| httpx              | 0.4.3-rc.2+dev |              6.3% |         44.8% |            54.2% |                  56.8% | +38.6 pts, 41.1% of untyped | +50.6 pts, 54.0% of untyped |
| black              | 0.4.3-rc.2+dev |             15.9% |         62.6% |            71.0% |                  73.4% | +46.7 pts, 55.5% of untyped | +57.5 pts, 68.3% of untyped |
| fastapi            | 0.4.3-rc.2+dev |             42.0% |         62.1% |            65.2% |                  67.2% | +20.1 pts, 34.6% of untyped | +25.2 pts, 43.4% of untyped |
| cattrs             | 0.4.3-rc.2+dev |              7.0% |         25.8% |            31.8% |                  34.0% | +18.8 pts, 20.2% of untyped | +27.0 pts, 29.0% of untyped |
| pytest             | 0.4.3-rc.2+dev |             12.1% |         51.9% |            56.4% |                  60.2% | +39.7 pts, 45.2% of untyped | +48.1 pts, 54.7% of untyped |
| botocore           | 0.4.3-rc.2+dev |              0.5% |         14.7% |            19.3% |                  30.7% | +14.3 pts, 14.3% of untyped | +30.2 pts, 30.4% of untyped |
| uvicorn            | 0.4.3-rc.2+dev |             23.6% |         59.7% |            64.7% |                  67.0% | +36.1 pts, 47.2% of untyped | +43.4 pts, 56.9% of untyped |
| mcp                | 0.4.3-rc.2+dev |             30.7% |         58.7% |            64.9% |                  68.2% | +28.0 pts, 40.3% of untyped | +37.5 pts, 54.1% of untyped |
| textual            | 0.4.3-rc.2+dev |             15.6% |         50.8% |            57.1% |                  60.5% | +35.3 pts, 41.8% of untyped | +44.9 pts, 53.2% of untyped |
| pdm                | 0.4.3-rc.2+dev |             11.7% |         49.0% |            55.5% |                  59.5% | +37.3 pts, 42.2% of untyped | +47.7 pts, 54.1% of untyped |
| strawberry-graphql | 0.4.3-rc.2+dev |             30.1% |         53.7% |            60.2% |                  62.2% | +23.7 pts, 33.8% of untyped | +32.1 pts, 45.9% of untyped |
| pygments           | 0.4.3-rc.2+dev |              0.0% |          9.6% |            10.6% |                  12.6% |   +9.6 pts, 9.6% of untyped | +12.6 pts, 12.6% of untyped |
| streamlink         | 0.4.3-rc.2+dev |             42.8% |         55.6% |            57.7% |                  60.4% | +12.9 pts, 22.5% of untyped | +17.6 pts, 30.8% of untyped |
| sphinx             | 0.4.3-rc.2+dev |             10.4% |         46.7% |            52.6% |                  56.8% | +36.3 pts, 40.5% of untyped | +46.4 pts, 51.8% of untyped |
| tox                | 0.4.3-rc.2+dev |             16.0% |         61.0% |            64.9% |                  67.5% | +44.9 pts, 53.5% of untyped | +51.5 pts, 61.4% of untyped |
| **Total**          | 0.4.3-rc.2+dev |              4.7% |         30.5% |            42.6% |                  47.2% | +25.7 pts, 27.0% of untyped | +42.5 pts, 44.6% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,446 |  37,446 |        |        |      0 |    0 | 38,775 |  115,001 |    52.0 |
| standard library   | likely             | 44,127 |  37,689 |  6,438 |        |      0 |    0 | 45,456 |  115,001 |    80.7 |
| standard library   | unsafe             | 50,528 |  37,453 |  6,426 |  6,649 |      0 |    0 | 51,857 |  115,001 |    70.7 |
| standard library   | infer-basedpyright | 58,565 |  37,458 |  6,912 | 14,195 |      0 |   10 | 59,894 |  115,001 |   540.7 |
| standard library   | infer-ty           | 56,300 |  37,458 |  6,863 | 11,979 |      0 |   11 | 57,629 |  115,001 |   104.2 |
| standard library   | infer-pyrefly      | 58,667 |  37,452 |  6,941 | 14,274 |      0 |   42 | 59,996 |  115,001 |    96.9 |
| django             | certain            |  2,622 |   2,622 |        |        |      0 |    0 |  2,627 |   17,181 |     6.6 |
| django             | likely             |  3,268 |   2,628 |    640 |        |      0 |    0 |  3,273 |   17,181 |    10.4 |
| django             | unsafe             |  5,408 |   2,622 |    639 |  2,147 |      0 |    0 |  5,413 |   17,181 |    13.4 |
| django             | infer-basedpyright |  5,806 |   2,616 |    652 |  2,538 |      0 |    8 |  5,811 |   17,181 |    48.1 |
| django             | infer-ty           |  5,618 |   2,623 |    648 |  2,347 |      0 |    0 |  5,623 |   17,181 |    19.5 |
| django             | infer-pyrefly      |  6,088 |   2,611 |    659 |  2,818 |      0 |    0 |  6,093 |   17,181 |    18.4 |
| django             | infer-trace        |  5,954 |   2,622 |    669 |  2,663 |      0 |    0 |  5,959 |   17,181 |     7.7 |
| sqlalchemy         | certain            |  1,938 |   1,938 |        |        |      0 |    0 |  4,273 |   15,304 |    10.5 |
| sqlalchemy         | likely             |  2,288 |   1,946 |    342 |        |      0 |    0 |  4,623 |   15,304 |    16.0 |
| sqlalchemy         | unsafe             |  2,785 |   1,938 |    342 |    505 |      0 |    0 |  5,120 |   15,304 |    14.8 |
| sqlalchemy         | infer-basedpyright |  3,549 |   1,930 |    384 |  1,235 |      0 |    0 |  5,884 |   15,304 |    62.4 |
| sqlalchemy         | infer-ty           |  3,503 |   1,930 |    370 |  1,203 |      0 |    0 |  5,838 |   15,304 |    23.8 |
| sqlalchemy         | infer-pyrefly      |  3,253 |   1,929 |    360 |    964 |      0 |    0 |  5,588 |   15,304 |    21.6 |
| sqlalchemy         | infer-trace        |  2,924 |   1,938 |    342 |    644 |      0 |    0 |  5,259 |   15,304 |    10.6 |
| pydantic           | certain            |  1,191 |   1,191 |        |        |      0 |    0 |  2,093 |    4,019 |     2.2 |
| pydantic           | likely             |  1,337 |   1,198 |    139 |        |      0 |    0 |  2,239 |    4,019 |     3.4 |
| pydantic           | unsafe             |  1,596 |   1,191 |    138 |    267 |      0 |    0 |  2,498 |    4,019 |     5.1 |
| pydantic           | infer-basedpyright |  1,819 |   1,192 |    141 |    486 |      0 |    0 |  2,721 |    4,019 |    38.0 |
| pydantic           | infer-ty           |  1,734 |   1,191 |    137 |    406 |      0 |    0 |  2,636 |    4,019 |     4.2 |
| pydantic           | infer-pyrefly      |  1,798 |   1,191 |    138 |    469 |      0 |    0 |  2,700 |    4,019 |    11.5 |
| pydantic           | infer-trace        |  1,597 |   1,191 |    138 |    268 |      0 |    0 |  2,499 |    4,019 |     5.1 |
| pandas             | certain            | 16,955 |  16,955 |        |        |      0 |    0 | 18,224 |   79,062 |    41.3 |
| pandas             | likely             | 40,544 |  17,145 | 23,399 |        |      0 |    0 | 41,813 |   79,062 |    90.6 |
| pandas             | unsafe             | 41,585 |  16,951 | 23,385 |  1,249 |      0 |    0 | 42,854 |   79,062 |    89.4 |
| pandas             | infer-basedpyright | 47,035 |  16,941 | 23,381 |  6,713 |      0 |    3 | 48,304 |   79,062 |   361.0 |
| pandas             | infer-ty           | 46,960 |  16,949 | 23,381 |  6,630 |      0 |    3 | 48,229 |   79,062 |   153.8 |
| pandas             | infer-pyrefly      | 48,159 |  16,949 | 23,387 |  7,823 |      0 |    9 | 49,428 |   79,062 |   115.1 |
| pandas             | infer-trace        | 42,872 |  16,951 | 23,249 |  2,672 |      0 |    0 | 44,141 |   79,062 |    65.8 |
| twisted            | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     4.7 |
| twisted            | likely             |  6,060 |   2,558 |  3,502 |        |      0 |    0 |  6,060 |   17,874 |    11.7 |
| twisted            | unsafe             |  7,132 |   2,434 |  3,502 |  1,196 |      0 |    0 |  7,132 |   17,874 |    11.6 |
| twisted            | infer-basedpyright |  8,541 |   2,435 |  3,532 |  2,574 |      0 |    0 |  8,541 |   17,874 |    43.8 |
| twisted            | infer-ty           |  7,538 |   2,434 |  3,526 |  1,578 |      0 |    0 |  7,538 |   17,874 |    16.3 |
| twisted            | infer-pyrefly      |  7,547 |   2,434 |  3,516 |  1,597 |      0 |    0 |  7,547 |   17,874 |    13.7 |
| pip                | certain            |  2,270 |   2,270 |        |        |      0 |    0 |  2,407 |    9,064 |     5.6 |
| pip                | likely             |  2,738 |   2,283 |    455 |        |      0 |    0 |  2,875 |    9,064 |     7.9 |
| pip                | unsafe             |  3,574 |   2,270 |    454 |    850 |      0 |    0 |  3,711 |    9,064 |     6.3 |
| pip                | infer-basedpyright |  4,292 |   2,271 |    498 |  1,523 |      0 |    3 |  4,429 |    9,064 |    30.7 |
| pip                | infer-ty           |  3,866 |   2,271 |    472 |  1,123 |      0 |    0 |  4,003 |    9,064 |     8.1 |
| pip                | infer-pyrefly      |  4,077 |   2,271 |    483 |  1,323 |      0 |    0 |  4,214 |    9,064 |    12.8 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.6 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     0.7 |
| structlog          | unsafe             |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.5 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     4.1 |
| structlog          | infer-ty           |    137 |      98 |     16 |     23 |      0 |    0 |    246 |      425 |     1.1 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     1.0 |
| structlog          | infer-trace        |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.9 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     1.0 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     1.0 |
| attrs              | unsafe             |    104 |      93 |      8 |      3 |      0 |    0 |    107 |      396 |     0.7 |
| attrs              | infer-basedpyright |    130 |      93 |      8 |     29 |      0 |    0 |    133 |      396 |     6.9 |
| attrs              | infer-ty           |    115 |      93 |      8 |     14 |      0 |    0 |    118 |      396 |     1.5 |
| attrs              | infer-pyrefly      |    120 |      93 |      8 |     19 |      0 |    0 |    123 |      396 |     2.7 |
| attrs              | infer-trace        |    107 |      93 |      9 |      5 |      0 |    0 |    110 |      396 |     0.7 |
| click              | certain            |    302 |     302 |        |        |      0 |    0 |    581 |      887 |     0.6 |
| click              | likely             |    329 |     303 |     26 |        |      0 |    0 |    608 |      887 |     1.0 |
| click              | unsafe             |    365 |     302 |     26 |     37 |      0 |    0 |    644 |      887 |     1.5 |
| click              | infer-basedpyright |    435 |     302 |     29 |    104 |      0 |    0 |    714 |      887 |     5.8 |
| click              | infer-ty           |    453 |     302 |     26 |    125 |      0 |    0 |    732 |      887 |     1.5 |
| click              | infer-pyrefly      |    442 |     302 |     31 |    109 |      0 |    0 |    721 |      887 |     1.6 |
| click              | infer-trace        |    365 |     302 |     26 |     37 |      0 |    0 |    644 |      887 |     1.1 |
| hypercorn          | certain            |    134 |     134 |        |        |      0 |    0 |    304 |      525 |     1.1 |
| hypercorn          | likely             |    154 |     134 |     20 |        |      0 |    0 |    324 |      525 |     0.7 |
| hypercorn          | unsafe             |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     1.3 |
| hypercorn          | infer-basedpyright |    214 |     134 |     21 |     59 |      0 |    0 |    384 |      525 |     6.8 |
| hypercorn          | infer-ty           |    219 |     134 |     21 |     64 |      0 |    0 |    389 |      525 |     1.0 |
| hypercorn          | infer-pyrefly      |    201 |     134 |     20 |     47 |      0 |    0 |    371 |      525 |     1.4 |
| hypercorn          | infer-trace        |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     1.4 |
| starlette          | certain            |    314 |     314 |        |        |      0 |    0 |    399 |      829 |     0.7 |
| starlette          | likely             |    371 |     314 |     57 |        |      0 |    0 |    456 |      829 |     1.0 |
| starlette          | unsafe             |    411 |     314 |     57 |     40 |      0 |    0 |    496 |      829 |     1.1 |
| starlette          | infer-basedpyright |    485 |     314 |     57 |    114 |      0 |    0 |    570 |      829 |     3.4 |
| starlette          | infer-ty           |    469 |     314 |     56 |     99 |      0 |    0 |    554 |      829 |     1.1 |
| starlette          | infer-pyrefly      |    447 |     314 |     56 |     77 |      0 |    0 |    532 |      829 |     3.1 |
| starlette          | infer-trace        |    411 |     314 |     57 |     40 |      0 |    0 |    496 |      829 |     1.5 |
| werkzeug           | certain            |    527 |     527 |        |        |      0 |    0 |    743 |    1,509 |     1.0 |
| werkzeug           | likely             |    593 |     528 |     65 |        |      0 |    0 |    809 |    1,509 |     1.1 |
| werkzeug           | unsafe             |    654 |     527 |     65 |     62 |      0 |    0 |    870 |    1,509 |     1.8 |
| werkzeug           | infer-basedpyright |    776 |     527 |     78 |    171 |      0 |    0 |    992 |    1,509 |     3.2 |
| werkzeug           | infer-ty           |    803 |     527 |     81 |    195 |      0 |    0 |  1,019 |    1,509 |     1.6 |
| werkzeug           | infer-pyrefly      |    806 |     528 |     70 |    208 |      0 |    0 |  1,022 |    1,509 |     2.4 |
| werkzeug           | infer-trace        |    654 |     527 |     65 |     62 |      0 |    0 |    870 |    1,509 |     2.5 |
| mkdocs             | certain            |    810 |     810 |        |        |      0 |    0 |    921 |    2,443 |     2.1 |
| mkdocs             | likely             |  1,187 |     840 |    347 |        |      0 |    0 |  1,298 |    2,443 |     2.4 |
| mkdocs             | unsafe             |  1,292 |     810 |    347 |    135 |      0 |    0 |  1,403 |    2,443 |     1.4 |
| mkdocs             | infer-basedpyright |  1,385 |     810 |    354 |    221 |      0 |    0 |  1,496 |    2,443 |     8.6 |
| mkdocs             | infer-ty           |  1,418 |     810 |    359 |    249 |      0 |    0 |  1,529 |    2,443 |     2.6 |
| mkdocs             | infer-pyrefly      |  1,385 |     810 |    355 |    220 |      0 |    0 |  1,496 |    2,443 |     3.2 |
| mkdocs             | infer-trace        |  1,304 |     811 |    347 |    146 |      0 |    0 |  1,415 |    2,443 |     3.7 |
| httpx              | certain            |    234 |     234 |        |        |      0 |    0 |    272 |      607 |     1.9 |
| httpx              | likely             |    291 |     243 |     48 |        |      0 |    0 |    329 |      607 |     0.7 |
| httpx              | unsafe             |    307 |     234 |     48 |     25 |      0 |    0 |    345 |      607 |     1.8 |
| httpx              | infer-basedpyright |    392 |     234 |     53 |    105 |      0 |    0 |    430 |      607 |     4.2 |
| httpx              | infer-ty           |    376 |     235 |     52 |     89 |      0 |    0 |    414 |      607 |     1.9 |
| httpx              | infer-pyrefly      |    353 |     234 |     51 |     68 |      0 |    0 |    391 |      607 |     1.9 |
| httpx              | infer-trace        |    307 |     234 |     48 |     25 |      0 |    0 |    345 |      607 |     1.8 |
| black              | certain            |    707 |     707 |        |        |      0 |    0 |    947 |    1,513 |     1.8 |
| black              | likely             |    834 |     720 |    114 |        |      0 |    0 |  1,074 |    1,513 |     0.9 |
| black              | unsafe             |    870 |     707 |    114 |     49 |      0 |    0 |  1,110 |    1,513 |     1.5 |
| black              | infer-basedpyright |    928 |     707 |    114 |    107 |      0 |    0 |  1,168 |    1,513 |     8.0 |
| black              | infer-ty           |    928 |     707 |    114 |    107 |      0 |    0 |  1,168 |    1,513 |     2.0 |
| black              | infer-pyrefly      |    914 |     707 |    112 |     95 |      0 |    0 |  1,154 |    1,513 |     1.5 |
| black              | infer-trace        |    870 |     707 |    114 |     49 |      0 |    0 |  1,110 |    1,513 |     0.7 |
| fastapi            | certain            |    257 |     257 |        |        |      0 |    0 |    794 |    1,279 |     1.3 |
| fastapi            | likely             |    297 |     263 |     34 |        |      0 |    0 |    834 |    1,279 |     3.4 |
| fastapi            | unsafe             |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     4.1 |
| fastapi            | infer-basedpyright |    348 |     257 |     33 |     58 |      0 |    0 |    885 |    1,279 |     7.6 |
| fastapi            | infer-ty           |    371 |     257 |     32 |     82 |      0 |    0 |    908 |    1,279 |     4.2 |
| fastapi            | infer-pyrefly      |    345 |     257 |     34 |     54 |      0 |    0 |    882 |    1,279 |     3.2 |
| fastapi            | infer-trace        |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     1.3 |
| cattrs             | certain            |    105 |     105 |        |        |      0 |    0 |    144 |      559 |     1.2 |
| cattrs             | likely             |    139 |     112 |     27 |        |      0 |    0 |    178 |      559 |     0.9 |
| cattrs             | unsafe             |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     1.3 |
| cattrs             | infer-basedpyright |    194 |     107 |     29 |     58 |      0 |    0 |    233 |      559 |     4.1 |
| cattrs             | infer-ty           |    195 |     105 |     27 |     63 |      0 |    0 |    234 |      559 |     1.1 |
| cattrs             | infer-pyrefly      |    182 |     105 |     28 |     49 |      0 |    0 |    221 |      559 |     1.9 |
| cattrs             | infer-trace        |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     0.7 |
| pytest             | certain            |  1,358 |   1,358 |        |        |      0 |    0 |  1,773 |    3,418 |     1.7 |
| pytest             | likely             |  1,514 |   1,362 |    152 |        |      0 |    0 |  1,929 |    3,418 |     3.2 |
| pytest             | unsafe             |  1,643 |   1,358 |    152 |    133 |      0 |    0 |  2,058 |    3,418 |     2.9 |
| pytest             | infer-basedpyright |  1,988 |   1,355 |    172 |    461 |      0 |    0 |  2,403 |    3,418 |    11.0 |
| pytest             | infer-ty           |  1,996 |   1,355 |    174 |    467 |      0 |    0 |  2,411 |    3,418 |     4.2 |
| pytest             | infer-pyrefly      |  2,059 |   1,355 |    174 |    530 |      0 |    0 |  2,474 |    3,418 |     8.0 |
| pytest             | infer-trace        |  1,660 |   1,358 |    152 |    150 |      0 |    0 |  2,075 |    3,418 |     2.9 |
| botocore           | certain            |    543 |     543 |        |        |      0 |    0 |    561 |    3,806 |     2.3 |
| botocore           | likely             |    717 |     549 |    168 |        |      0 |    0 |    735 |    3,806 |     3.4 |
| botocore           | unsafe             |  1,151 |     541 |    168 |    442 |      0 |    0 |  1,169 |    3,806 |     2.3 |
| botocore           | infer-basedpyright |  1,296 |     536 |    171 |    589 |      0 |    0 |  1,314 |    3,806 |    12.8 |
| botocore           | infer-ty           |  1,207 |     541 |    169 |    497 |      0 |    0 |  1,225 |    3,806 |     4.6 |
| botocore           | infer-pyrefly      |  1,282 |     537 |    171 |    574 |      0 |    0 |  1,300 |    3,806 |     4.2 |
| botocore           | infer-trace        |  1,496 |     541 |    194 |    761 |      0 |    0 |  1,514 |    3,806 |     4.0 |
| uvicorn            | certain            |    231 |     231 |        |        |      0 |    0 |    382 |      640 |     0.8 |
| uvicorn            | likely             |    263 |     231 |     32 |        |      0 |    0 |    414 |      640 |     1.5 |
| uvicorn            | unsafe             |    278 |     231 |     32 |     15 |      0 |    0 |    429 |      640 |     1.7 |
| uvicorn            | infer-basedpyright |    346 |     231 |     35 |     80 |      0 |    0 |    497 |      640 |     5.1 |
| uvicorn            | infer-ty           |    325 |     231 |     32 |     62 |      0 |    0 |    476 |      640 |     2.4 |
| uvicorn            | infer-pyrefly      |    303 |     231 |     35 |     37 |      0 |    0 |    454 |      640 |     2.6 |
| uvicorn            | infer-trace        |    278 |     231 |     32 |     15 |      0 |    0 |    429 |      640 |     1.6 |
| mcp                | certain            |    694 |     694 |        |        |      0 |    0 |  1,457 |    2,483 |     1.0 |
| mcp                | likely             |    848 |     700 |    148 |        |      0 |    0 |  1,611 |    2,483 |     2.2 |
| mcp                | unsafe             |    930 |     694 |    148 |     88 |      0 |    0 |  1,693 |    2,483 |     4.5 |
| mcp                | infer-basedpyright |  1,048 |     694 |    159 |    195 |      0 |    0 |  1,811 |    2,483 |    11.9 |
| mcp                | infer-ty           |  1,039 |     694 |    156 |    189 |      0 |    0 |  1,802 |    2,483 |     2.4 |
| mcp                | infer-pyrefly      |  1,016 |     694 |    152 |    170 |      0 |    0 |  1,779 |    2,483 |     3.6 |
| mcp                | infer-trace        |    930 |     694 |    148 |     88 |      0 |    0 |  1,693 |    2,483 |     2.5 |
| textual            | certain            |  2,707 |   2,707 |        |        |      0 |    0 |  3,901 |    7,677 |     2.7 |
| textual            | likely             |  3,189 |   2,731 |    458 |        |      0 |    0 |  4,383 |    7,677 |     3.7 |
| textual            | unsafe             |  3,448 |   2,707 |    457 |    284 |      0 |    0 |  4,642 |    7,677 |     2.4 |
| textual            | infer-basedpyright |  4,634 |   2,707 |    525 |  1,402 |      0 |   14 |  5,828 |    7,677 |    18.0 |
| textual            | infer-ty           |  4,726 |   2,707 |    531 |  1,488 |      0 |    0 |  5,920 |    7,677 |     9.7 |
| textual            | infer-pyrefly      |  3,850 |   2,707 |    474 |    669 |      0 |    0 |  5,044 |    7,677 |     6.7 |
| pdm                | certain            |  1,147 |   1,147 |        |        |      0 |    0 |  1,508 |    3,079 |     2.9 |
| pdm                | likely             |  1,348 |   1,160 |    188 |        |      0 |    0 |  1,709 |    3,079 |     2.8 |
| pdm                | unsafe             |  1,470 |   1,147 |    187 |    136 |      0 |    0 |  1,831 |    3,079 |     4.5 |
| pdm                | infer-basedpyright |  1,853 |   1,150 |    216 |    487 |      0 |    0 |  2,214 |    3,079 |     9.5 |
| pdm                | infer-ty           |  1,845 |   1,150 |    216 |    479 |      0 |    0 |  2,206 |    3,079 |     3.6 |
| pdm                | infer-pyrefly      |  1,629 |   1,148 |    197 |    284 |      0 |    0 |  1,990 |    3,079 |     4.6 |
| pdm                | infer-trace        |  1,470 |   1,147 |    187 |    136 |      0 |    0 |  1,831 |    3,079 |     2.6 |
| strawberry-graphql | certain            |    611 |     611 |        |        |      0 |    0 |  1,387 |    2,582 |     1.7 |
| strawberry-graphql | likely             |    778 |     613 |    165 |        |      0 |    0 |  1,554 |    2,582 |     2.1 |
| strawberry-graphql | unsafe             |    829 |     611 |    165 |     53 |      0 |    0 |  1,605 |    2,582 |     5.1 |
| strawberry-graphql | infer-basedpyright |    989 |     610 |    166 |    213 |      0 |    0 |  1,765 |    2,582 |    11.2 |
| strawberry-graphql | infer-ty           |    986 |     610 |    165 |    211 |      0 |    0 |  1,762 |    2,582 |     4.3 |
| strawberry-graphql | infer-pyrefly      |    885 |     610 |    166 |    109 |      0 |    0 |  1,661 |    2,582 |     4.0 |
| strawberry-graphql | infer-trace        |    829 |     611 |    165 |     53 |      0 |    0 |  1,605 |    2,582 |     2.3 |
| pygments           | certain            |    735 |     735 |        |        |      0 |    0 |    735 |    7,666 |     2.2 |
| pygments           | likely             |    814 |     738 |     76 |        |      0 |    0 |    814 |    7,666 |     3.4 |
| pygments           | unsafe             |    963 |     735 |     76 |    152 |      0 |    0 |    963 |    7,666 |     2.9 |
| pygments           | infer-basedpyright |  1,076 |     735 |     83 |    258 |      0 |    0 |  1,076 |    7,666 |    16.0 |
| pygments           | infer-ty           |  1,077 |     735 |     84 |    258 |      0 |    0 |  1,077 |    7,666 |     6.2 |
| pygments           | infer-pyrefly      |  1,139 |     735 |     84 |    320 |      0 |    0 |  1,139 |    7,666 |     7.5 |
| pygments           | infer-trace        |  1,073 |     730 |    100 |    243 |      0 |    0 |  1,073 |    7,666 |     5.8 |
| streamlink         | certain            |    682 |     682 |        |        |      0 |    0 |  2,944 |    5,291 |     2.2 |
| streamlink         | likely             |    793 |     685 |    108 |        |      0 |    0 |  3,055 |    5,291 |     2.6 |
| streamlink         | unsafe             |    932 |     682 |    108 |    142 |      0 |    0 |  3,194 |    5,291 |     2.6 |
| streamlink         | infer-basedpyright |  1,318 |     683 |    125 |    510 |      0 |    0 |  3,580 |    5,291 |    17.9 |
| streamlink         | infer-ty           |  1,475 |     682 |    136 |    657 |      0 |    0 |  3,737 |    5,291 |     6.2 |
| streamlink         | infer-pyrefly      |  1,121 |     682 |    120 |    319 |      0 |    0 |  3,383 |    5,291 |     5.7 |
| streamlink         | infer-trace        |    940 |     682 |    108 |    150 |      0 |    0 |  3,202 |    5,291 |     4.1 |
| sphinx             | certain            |  3,230 |   3,230 |        |        |      0 |    0 |  4,158 |    8,901 |     4.7 |
| sphinx             | likely             |  3,751 |   3,245 |    506 |        |      0 |    0 |  4,679 |    8,901 |     7.1 |
| sphinx             | unsafe             |  4,130 |   3,230 |    505 |    395 |      0 |    0 |  5,058 |    8,901 |     6.3 |
| sphinx             | infer-basedpyright |  4,936 |   3,231 |    537 |  1,168 |      0 |    0 |  5,864 |    8,901 |    15.8 |
| sphinx             | infer-ty           |  4,993 |   3,230 |    531 |  1,232 |      0 |    0 |  5,921 |    8,901 |     8.1 |
| sphinx             | infer-pyrefly      |  5,205 |   3,231 |    541 |  1,433 |      0 |    0 |  6,133 |    8,901 |     8.5 |
| sphinx             | infer-trace        |  4,130 |   3,230 |    505 |    395 |      0 |    0 |  5,058 |    8,901 |     5.9 |
| tox                | certain            |    943 |     943 |        |        |      0 |    0 |  1,279 |    2,098 |     1.0 |
| tox                | likely             |  1,025 |     944 |     81 |        |      0 |    0 |  1,361 |    2,098 |     1.6 |
| tox                | unsafe             |  1,081 |     943 |     81 |     57 |      0 |    0 |  1,417 |    2,098 |     3.7 |
| tox                | infer-basedpyright |  1,331 |     945 |     98 |    288 |      0 |    0 |  1,667 |    2,098 |    12.6 |
| tox                | infer-ty           |  1,368 |     945 |     97 |    326 |      0 |    0 |  1,704 |    2,098 |     2.9 |
| tox                | infer-pyrefly      |  1,413 |     945 |     97 |    371 |      0 |    0 |  1,749 |    2,098 |     3.5 |
| tox                | infer-trace        |  1,081 |     943 |     81 |     57 |      0 |    0 |  1,417 |    2,098 |     2.1 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 19,330 |  19,330 |        |        |
| certain            | stdlib                 | 14,519 |  14,519 |        |        |
| certain            | call                   |  6,703 |   6,703 |        |        |
| certain            | container+literal      |  4,464 |   4,464 |        |        |
| certain            | builtin                |  3,061 |   3,061 |        |        |
| certain            | loop                   |  2,757 |   2,757 |        |        |
| certain            | method                 |  2,530 |   2,530 |        |        |
| certain            | copy+loop              |  2,384 |   2,384 |        |        |
| certain            | container+literal+loop |  1,675 |   1,675 |        |        |
| certain            | open                   |  1,274 |   1,274 |        |        |
| certain            | literal+method         |  1,254 |   1,254 |        |        |
| certain            | returned               |    996 |     996 |        |        |
| likely             | constructor            | 28,676 |     245 | 28,431 |        |
| likely             | literal                | 19,333 |  19,333 |        |        |
| likely             | stdlib                 | 14,597 |  14,597 |        |        |
| likely             | call                   |  7,173 |   6,716 |    457 |        |
| likely             | container+literal      |  4,464 |   4,464 |        |        |
| likely             | method                 |  3,654 |   2,553 |  1,101 |        |
| likely             | builtin                |  3,061 |   3,061 |        |        |
| likely             | copy+loop              |  2,765 |   2,398 |    367 |        |
| likely             | loop                   |  2,760 |   2,760 |        |        |
| likely             | container+literal+loop |  1,675 |   1,675 |        |        |
| likely             | open                   |  1,274 |   1,274 |        |        |
| likely             | literal+method         |  1,254 |   1,254 |        |        |
| unsafe             | constructor            | 28,675 |     245 | 28,430 |        |
| unsafe             | literal                | 19,332 |  19,328 |        |      4 |
| unsafe             | stdlib                 | 14,896 |  14,521 |        |    375 |
| unsafe             | call                   |  7,159 |   6,703 |    456 |        |
| unsafe             | container+literal      |  4,464 |   4,464 |        |        |
| unsafe             | literal+member         |  4,152 |         |        |  4,152 |
| unsafe             | returned               |  3,783 |     998 |        |  2,785 |
| unsafe             | method                 |  3,631 |   2,530 |  1,101 |        |
| unsafe             | builtin                |  3,061 |   3,061 |        |        |
| unsafe             | loop                   |  2,757 |   2,757 |        |        |
| unsafe             | copy+loop              |  2,750 |   2,384 |    366 |        |
| unsafe             | container+literal+loop |  1,675 |   1,675 |        |        |
| infer-basedpyright | constructor            | 28,623 |     244 | 28,379 |        |
| infer-basedpyright | literal                | 19,333 |  19,329 |        |      4 |
| infer-basedpyright | checker                | 18,340 |         |        | 18,340 |
| infer-basedpyright | stdlib                 | 15,012 |  14,463 |        |    549 |
| infer-basedpyright | call                   |  7,248 |   6,698 |    550 |        |
| infer-basedpyright | container+literal      |  4,467 |   4,467 |        |        |
| infer-basedpyright | literal+member         |  4,151 |         |        |  4,151 |
| infer-basedpyright | returned               |  4,039 |     977 |        |  3,062 |
| infer-basedpyright | method                 |  3,774 |   2,527 |  1,247 |        |
| infer-basedpyright | copy+loop              |  3,197 |   2,384 |    813 |        |
| infer-basedpyright | builtin                |  3,061 |   3,061 |        |        |
| infer-basedpyright | loop                   |  2,757 |   2,757 |        |        |
| infer-ty           | constructor            | 28,620 |     245 | 28,375 |        |
| infer-ty           | literal                | 19,332 |  19,328 |        |      4 |
| infer-ty           | stdlib                 | 15,022 |  14,479 |        |    543 |
| infer-ty           | checker                | 14,947 |         |        | 14,947 |
| infer-ty           | call                   |  7,208 |   6,698 |    510 |        |
| infer-ty           | container+literal      |  4,468 |   4,468 |        |        |
| infer-ty           | literal+member         |  4,152 |         |        |  4,152 |
| infer-ty           | returned               |  4,007 |     998 |        |  3,009 |
| infer-ty           | method                 |  3,744 |   2,527 |  1,217 |        |
| infer-ty           | copy+loop              |  3,102 |   2,384 |    718 |        |
| infer-ty           | builtin                |  3,061 |   3,061 |        |        |
| infer-ty           | loop                   |  2,757 |   2,757 |        |        |
| infer-pyrefly      | constructor            | 28,611 |     244 | 28,367 |        |
| infer-pyrefly      | literal                | 19,332 |  19,328 |        |      4 |
| infer-pyrefly      | checker                | 17,689 |         |        | 17,689 |
| infer-pyrefly      | stdlib                 | 15,039 |  14,483 |        |    556 |
| infer-pyrefly      | call                   |  7,205 |   6,698 |    507 |        |
| infer-pyrefly      | container+literal      |  4,466 |   4,466 |        |        |
| infer-pyrefly      | literal+member         |  4,151 |         |        |  4,151 |
| infer-pyrefly      | returned               |  3,993 |     993 |        |  3,000 |
| infer-pyrefly      | method                 |  3,744 |   2,527 |  1,217 |        |
| infer-pyrefly      | copy+loop              |  3,129 |   2,384 |    745 |        |
| infer-pyrefly      | builtin                |  3,061 |   3,061 |        |        |
| infer-pyrefly      | loop                   |  2,757 |   2,757 |        |        |
| infer-trace        | constructor            | 21,157 |      13 | 21,144 |        |
| infer-trace        | literal                |  9,243 |   9,242 |        |      1 |
| infer-trace        | call                   |  6,676 |   6,224 |    452 |        |
| infer-trace        | method                 |  2,994 |   1,966 |  1,028 |        |
| infer-trace        | stdlib                 |  2,438 |   2,345 |        |     93 |
| infer-trace        | literal+member         |  2,410 |         |        |  2,410 |
| infer-trace        | traced                 |  2,387 |         |        |  2,387 |
| infer-trace        | container+literal      |  2,076 |   2,076 |        |        |
| infer-trace        | builtin                |  1,275 |   1,275 |        |        |
| infer-trace        | copy+loop              |  1,257 |   1,072 |    185 |        |
| infer-trace        | returned               |    859 |     316 |        |    543 |
| infer-trace        | loop                   |    841 |     841 |        |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  13,076 |  63,149 |        0 |
| django             |  17,176 |   2,786 |  11,768 |        0 |
| sqlalchemy         |  12,962 |     847 |  10,177 |        0 |
| pydantic           |   3,117 |     405 |   1,521 |        0 |
| pandas             |  77,793 |  24,358 |  36,480 |        0 |
| twisted            |  17,874 |   4,697 |  10,742 |        0 |
| pip                |   8,924 |   1,304 |   5,350 |        0 |
| structlog          |     316 |      28 |     190 |        0 |
| attrs              |     393 |      11 |     289 |        0 |
| click              |     608 |      63 |     243 |        0 |
| hypercorn          |     355 |      58 |     163 |        0 |
| starlette          |     744 |      97 |     333 |        0 |
| werkzeug           |   1,293 |     127 |     639 |        0 |
| mkdocs             |   2,332 |     482 |   1,040 |        0 |
| httpx              |     569 |      73 |     262 |        0 |
| black              |   1,273 |     163 |     403 |        0 |
| fastapi            |     742 |      65 |     420 |        0 |
| cattrs             |     520 |      37 |     380 |        0 |
| pytest             |   3,003 |     285 |   1,360 |        0 |
| botocore           |   3,786 |     608 |   2,635 |        0 |
| uvicorn            |     489 |      47 |     211 |        0 |
| mcp                |   1,720 |     236 |     790 |        0 |
| textual            |   6,483 |     741 |   3,035 |        0 |
| pdm                |   2,718 |     323 |   1,248 |        0 |
| strawberry-graphql |   1,806 |     218 |     977 |        0 |
| pygments           |   7,666 |     228 |   6,703 |        0 |
| streamlink         |   3,029 |     250 |   2,097 |        0 |
| sphinx             |   7,972 |     900 |   3,843 |        0 |
| tox                |   1,762 |     138 |     681 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library   |    4 |       40.72 |     17.38 |    1 |                       581.6 |     619.9 | hyperfine |
| django             |    4 |        8.21 |      3.43 |    1 |                       114.5 |     123.4 | hyperfine |
| sqlalchemy         |    4 |        6.83 |      3.59 |    1 |                       103.0 |     109.5 | hyperfine |
| pydantic           |    4 |        1.66 |      0.79 |    1 |                        23.4 |      25.7 | hyperfine |
| pandas             |    4 |       48.89 |      18.1 |    1 |                       728.8 |     756.3 | hyperfine |
| twisted            |    4 |         6.2 |       2.6 |    1 |                        87.0 |      95.1 | hyperfine |
| pip                |    4 |        4.19 |      1.75 |    1 |                        62.1 |      66.7 | hyperfine |
| structlog          |    4 |        0.26 |      0.26 |    1 |                         3.1 |       4.2 | hyperfine |
| attrs              |    4 |        0.21 |      0.28 |    1 |                         2.6 |       3.6 | hyperfine |
| click              |    4 |         0.4 |      0.33 |    1 |                         5.3 |       6.3 | hyperfine |
| hypercorn          |    4 |        0.34 |      0.28 |    1 |                         4.0 |       5.3 | hyperfine |
| starlette          |    4 |        0.43 |      0.33 |    1 |                         5.2 |       6.6 | hyperfine |
| werkzeug           |    4 |        0.74 |      0.41 |    1 |                         9.5 |      10.8 | hyperfine |
| mkdocs             |    4 |        0.82 |      0.54 |    1 |                        10.6 |      12.6 | hyperfine |
| httpx              |    4 |        0.36 |      0.28 |    1 |                         4.4 |       5.5 | hyperfine |
| black              |    4 |        0.53 |      0.33 |    1 |                         7.1 |       8.3 | hyperfine |
| fastapi            |    4 |        0.59 |      0.52 |    1 |                         8.5 |      10.0 | hyperfine |
| cattrs             |    4 |        0.34 |      0.33 |    1 |                         4.4 |       5.8 | hyperfine |
| pytest             |    4 |        1.43 |      0.84 |    1 |                        19.0 |      21.0 | hyperfine |
| botocore           |    4 |        1.74 |      0.81 |    1 |                        23.3 |      25.5 | hyperfine |
| uvicorn            |    4 |        0.42 |       0.3 |    1 |                         5.2 |       6.4 | hyperfine |
| mcp                |    4 |        1.08 |      0.59 |    1 |                        14.0 |      16.2 | hyperfine |
| textual            |    4 |        2.53 |      1.13 |    1 |                        35.0 |      38.5 | hyperfine |
| pdm                |    4 |        1.55 |      0.92 |    1 |                        20.9 |      24.0 | hyperfine |
| strawberry-graphql |    4 |         1.6 |      0.81 |    1 |                        21.0 |      24.3 | hyperfine |
| pygments           |    4 |         2.6 |       1.1 |    1 |                        45.6 |      48.6 | hyperfine |
| streamlink         |    4 |        1.92 |      0.89 |    1 |                        26.8 |      29.1 | hyperfine |
| sphinx             |    4 |        4.13 |      1.49 |    1 |                        60.5 |      62.9 | hyperfine |
| tox                |    4 |        1.02 |      0.48 |    1 |                        13.1 |      14.2 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                   tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | ----------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  482 | Ran 17585 tests: FAILED (failures=5, skipped=1149, expected failures=5) |    52.8 |     48.2 |
| django             | certain |    971 |    970 |        1 |                      |                                                                         |         |          |
| django             | likely  |    318 |    316 |        2 |                      |                                                                         |         |          |
| django             | guess   |    361 |    344 |       17 |                      |                                                                         |         |          |
| sqlalchemy         |         |        |        |          |                  137 |                                    29525 passed, 971 skipped, 1 warning |    93.8 |     91.7 |
| sqlalchemy         | certain |  1,063 |  1,046 |       17 |                      |                                                                         |         |          |
| sqlalchemy         | likely  |    156 |    153 |        3 |                      |                                                                         |         |          |
| sqlalchemy         | guess   |    111 |    109 |        2 |                      |                                                                         |         |          |
| pydantic           |         |        |        |          |                    1 |                         65 failed, 6900 passed, 350 skipped, 29 xfailed |    55.6 |     53.7 |
| pydantic           | certain |    522 |    517 |        5 |                      |                                                                         |         |          |
| pydantic           | likely  |     47 |     47 |        0 |                      |                                                                         |         |          |
| pydantic           | guess   |     31 |     31 |        0 |                      |                                                                         |         |          |
| pandas             |         |        |        |          |                1,420 |                   165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   135.1 |     98.5 |
| pandas             | certain | 12,874 | 12,797 |       77 |                      |                                                                         |         |          |
| pandas             | likely  | 20,038 | 19,972 |       66 |                      |                                                                         |         |          |
| pandas             | guess   |    821 |    774 |       47 |                      |                                                                         |         |          |
| structlog          |         |        |        |          |                    0 |                           24 failed, 860 passed, 37 skipped, 2 warnings |     2.7 |      2.2 |
| structlog          | certain |     63 |     63 |        0 |                      |                                                                         |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                         |         |          |
| structlog          | guess   |      6 |      6 |        0 |                      |                                                                         |         |          |
| attrs              |         |        |        |          |                    2 |                             1 failed, 1382 passed, 2 skipped, 2 xfailed |     4.1 |      4.6 |
| attrs              | certain |     72 |     72 |        0 |                      |                                                                         |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                         |         |          |
| attrs              | guess   |      1 |      1 |        0 |                      |                                                                         |         |          |
| click              |         |        |        |          |                    0 |                    1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     8.4 |      7.0 |
| click              | certain |    222 |    222 |        0 |                      |                                                                         |         |          |
| click              | likely  |     19 |     18 |        1 |                      |                                                                         |         |          |
| click              | guess   |     25 |     25 |        0 |                      |                                                                         |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                    2 failed, 194 passed |     7.2 |      7.2 |
| hypercorn          | certain |     63 |     63 |        0 |                      |                                                                         |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                         |         |          |
| hypercorn          | guess   |     10 |     10 |        0 |                      |                                                                         |         |          |
| starlette          |         |        |        |          |                    0 |                                       1271 passed, 2 skipped, 2 xfailed |    11.2 |     10.3 |
| starlette          | certain |    193 |    192 |        1 |                      |                                                                         |         |          |
| starlette          | likely  |     47 |     47 |        0 |                      |                                                                         |         |          |
| starlette          | guess   |     29 |     29 |        0 |                      |                                                                         |         |          |
| werkzeug           |         |        |        |          |                    0 |                              1 failed, 979 passed, 1 skipped, 1 warning |     9.9 |      9.1 |
| werkzeug           | certain |    354 |    350 |        4 |                      |                                                                         |         |          |
| werkzeug           | likely  |     44 |     44 |        0 |                      |                                                                         |         |          |
| werkzeug           | guess   |     33 |     33 |        0 |                      |                                                                         |         |          |
| mkdocs             |         |        |        |          |                   12 |                 Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    10.9 |     10.6 |
| mkdocs             | certain |    628 |    627 |        1 |                      |                                                                         |         |          |
| mkdocs             | likely  |    322 |    322 |        0 |                      |                                                                         |         |          |
| mkdocs             | guess   |    116 |    116 |        0 |                      |                                                                         |         |          |
| httpx              |         |        |        |          |                    0 |                                        1 failed, 1416 passed, 1 skipped |     7.8 |      7.7 |
| httpx              | certain |    181 |    181 |        0 |                      |                                                                         |         |          |
| httpx              | likely  |     41 |     41 |        0 |                      |                                                                         |         |          |
| httpx              | guess   |     16 |     16 |        0 |                      |                                                                         |         |          |
| black              |         |        |        |          |                    0 |                                519 passed, 1 skipped, 9 subtests passed |     6.6 |      6.7 |
| black              | certain |    602 |    602 |        0 |                      |                                                                         |         |          |
| black              | likely  |    101 |    101 |        0 |                      |                                                                         |         |          |
| black              | guess   |     39 |     39 |        0 |                      |                                                                         |         |          |
| fastapi            |         |        |        |          |                    0 |                                      3551 passed, 17 skipped, 4 xfailed |    15.8 |     14.7 |
| fastapi            | certain |    220 |    220 |        0 |                      |                                                                         |         |          |
| fastapi            | likely  |     30 |     30 |        0 |                      |                                                                         |         |          |
| fastapi            | guess   |     22 |     22 |        0 |                      |                                                                         |         |          |
| cattrs             |         |        |        |          |                    0 |                                                  994 passed, 15 xfailed |    20.4 |     18.0 |
| cattrs             | certain |     99 |     97 |        2 |                      |                                                                         |         |          |
| cattrs             | likely  |     23 |     23 |        0 |                      |                                                                         |         |          |
| cattrs             | guess   |     13 |     13 |        0 |                      |                                                                         |         |          |
| pytest             |         |        |        |          |                   14 |     46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    43.8 |     21.3 |
| pytest             | certain |  1,102 |  1,090 |       12 |                      |                                                                         |         |          |
| pytest             | likely  |    123 |    123 |        0 |                      |                                                                         |         |          |
| pytest             | guess   |    105 |    105 |        0 |                      |                                                                         |         |          |
| botocore           |         |        |        |          |                  297 |                                       7 failed, 4593 passed, 96 skipped |    30.0 |     29.5 |
| botocore           | certain |    326 |    325 |        1 |                      |                                                                         |         |          |
| botocore           | likely  |    138 |    138 |        0 |                      |                                                                         |         |          |
| botocore           | guess   |    102 |    101 |        1 |                      |                                                                         |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                 1350 passed, 12 skipped |    40.6 |     29.5 |
| uvicorn            | certain |    168 |    164 |        4 |                      |                                                                         |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                         |         |          |
| uvicorn            | guess   |      8 |      8 |        0 |                      |                                                                         |         |          |
| mcp                |         |        |        |          |                    0 |                             3 failed, 6092 passed, 8 skipped, 1 xfailed |    19.2 |     14.9 |
| mcp                | certain |    512 |    512 |        0 |                      |                                                                         |         |          |
| mcp                | likely  |    130 |    129 |        1 |                      |                                                                         |         |          |
| mcp                | guess   |     56 |     56 |        0 |                      |                                                                         |         |          |
| pdm                |         |        |        |          |                    0 |                                     1472 passed, 1 skipped, 60 warnings |    23.7 |     15.0 |
| pdm                | certain |    865 |    861 |        4 |                      |                                                                         |         |          |
| pdm                | likely  |    126 |    126 |        0 |                      |                                                                         |         |          |
| pdm                | guess   |     79 |     79 |        0 |                      |                                                                         |         |          |
| strawberry-graphql |         |        |        |          |                    0 | 51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    16.8 |     14.0 |
| strawberry-graphql | certain |    390 |    384 |        6 |                      |                                                                         |         |          |
| strawberry-graphql | likely  |     95 |     94 |        1 |                      |                                                                         |         |          |
| strawberry-graphql | guess   |     28 |     28 |        0 |                      |                                                                         |         |          |
| pygments           |         |        |        |          |                   87 |                                       1 failed, 5330 passed, 15 skipped |    21.8 |     14.6 |
| pygments           | certain |    289 |    289 |        0 |                      |                                                                         |         |          |
| pygments           | likely  |     58 |     58 |        0 |                      |                                                                         |         |          |
| pygments           | guess   |     59 |     59 |        0 |                      |                                                                         |         |          |
| streamlink         |         |        |        |          |                    8 |                            15 failed, 7233 passed, 36 skipped, 9 errors |    16.7 |     12.4 |
| streamlink         | certain |    274 |    273 |        1 |                      |                                                                         |         |          |
| streamlink         | likely  |     38 |     38 |        0 |                      |                                                                         |         |          |
| streamlink         | guess   |     37 |     37 |        0 |                      |                                                                         |         |          |
| sphinx             |         |        |        |          |                    0 |                         10 failed, 2392 passed, 22 skipped, 35 warnings |    22.2 |     14.7 |
| sphinx             | certain |  2,055 |  2,026 |       29 |                      |                                                                         |         |          |
| sphinx             | likely  |    411 |    411 |        0 |                      |                                                                         |         |          |
| sphinx             | guess   |    196 |    193 |        3 |                      |                                                                         |         |          |
| tox                |         |        |        |          |                    0 |                            17 failed, 8525 passed, 31 skipped, 6 errors |    30.0 |     18.2 |
| tox                | certain |    701 |    698 |        3 |                      |                                                                         |         |          |
| tox                | likely  |     62 |     62 |        0 |                      |                                                                         |         |          |
| tox                | guess   |     28 |     27 |        1 |                      |                                                                         |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                                          | same as released | summary                                                              | new failures | gone | named |
| ------------------ | -------------------------------------------- | ---------------- | -------------------------------------------------------------------- | -----------: | ---: | ----: |
| django             | released                                     |                  | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped           |              |      |       |
| django             | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| django             | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| django             | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| django             | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| django             | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| django             | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| django             | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | released                                     |                  | 29,521 passed, 975 skipped                                           |              |      |       |
| sqlalchemy         | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sqlalchemy         | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                     |              |      |       |
| pydantic           | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pydantic           | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              |              |      |       |
| pandas             | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pandas             | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 24 failed, 860 passed, 37 skipped                                    |              |      |       |
| structlog          | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| structlog          | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         |              |      |       |
| attrs              | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| attrs              | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1,991 passed, 24 skipped, 1 xfailed                                  |              |      |       |
| click              | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| click              | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 2 failed, 194 passed                                                 |              |      |       |
| hypercorn          | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| hypercorn          | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1,271 passed, 2 skipped, 2 xfailed                                   |              |      |       |
| starlette          | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| starlette          | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1 failed, 979 passed, 1 skipped                                      |              |      |       |
| werkzeug           | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| werkzeug           | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 2 errors, 2 failures, 724 ran, 4 skipped                             |              |      |       |
| mkdocs             | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mkdocs             | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1 failed, 1,416 passed, 1 skipped                                    |              |      |       |
| httpx              | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| httpx              | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| black              | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 519 passed, 1 skipped                                                |              |      |       |
| black              | fix-certain                                  | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | fix-likely                                   | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | fix-unsafe                                   | True             | as infer-trace's (implied)                                           |            0 |    0 |     1 |
| black              | infer-basedpyright                           | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-pyrefly                                | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-trace                                  | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| black              | infer-ty                                     | True             | 1 failed, 518 passed, 1 skipped                                      |            0 |    0 |     1 |
| fastapi            | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 3,551 passed, 17 skipped, 4 xfailed                                  |              |      |       |
| fastapi            | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| fastapi            | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| fastapi            | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| fastapi            | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| fastapi            | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| fastapi            | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| fastapi            | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 994 passed, 15 xfailed                                               |              |      |       |
| cattrs             | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| cattrs             | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed |              |      |       |
| pytest             | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pytest             | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 7 failed, 4,593 passed, 96 skipped                                   |              |      |       |
| botocore           | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| botocore           | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1,350 passed, 12 skipped                                             |              |      |       |
| uvicorn            | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| uvicorn            | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | released                                     |                  | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                         |              |      |       |
| mcp                | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| mcp                | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1,472 passed, 1 skipped                                              |              |      |       |
| pdm                | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pdm                | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | released                                     |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          |              |      |       |
| strawberry-graphql | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| strawberry-graphql | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 1 failed, 5,330 passed, 15 skipped                                   |              |      |       |
| pygments           | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| pygments           | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 9 error, 15 failed, 7,233 passed, 36 skipped                         |              |      |       |
| streamlink         | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| streamlink         | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| sphinx             | released                                     |                  | 10 failed, 2,392 passed, 22 skipped                                  |              |      |       |
| sphinx             | fix-certain                                  | True             | as infer-basedpyright's (implied)                                    |            0 |    0 |     0 |
| sphinx             | fix-likely                                   | True             | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    0 |     0 |
| sphinx             | fix-unsafe                                   | True             | as infer-trace's (implied)                                           |            0 |    0 |     0 |
| sphinx             | infer-basedpyright                           | True             | 10 failed, 2,392 passed, 22 skipped                                  |            0 |    0 |     0 |
| sphinx             | infer-pyrefly                                | True             | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    0 |     0 |
| sphinx             | infer-trace                                  | True             | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    0 |     0 |
| sphinx             | infer-ty                                     | True             | 9 failed, 2,393 passed, 22 skipped                                   |            0 |    0 |     0 |
| tox                | released (from 0.4.3-rc.1-10-22-2026-2332-2) |                  | 6 error, 17 failed, 8,525 passed, 31 skipped                         |              |      |       |
| tox                | fix-certain                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| tox                | fix-likely                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| tox                | fix-unsafe                                   | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| tox                | infer-basedpyright                           | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| tox                | infer-pyrefly                                | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| tox                | infer-trace                                  | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |
| tox                | infer-ty                                     | True             | as infer-union's (implied)                                           |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                      change |
| ------------------ | ------------------ | -----: | --: | ---: | ----------------------------------------------------------: |
| sqlalchemy         | released           |      0 |     |      |                                                             |
| sqlalchemy         | fix-certain        |      0 |   0 |    0 |    187 files changed, 2368 insertions(+), 1920 deletions(-) |
| sqlalchemy         | fix-likely         |      0 |   0 |    0 |    187 files changed, 2368 insertions(+), 1920 deletions(-) |
| sqlalchemy         | fix-unsafe         |      0 |   0 |    0 |    198 files changed, 2873 insertions(+), 2385 deletions(-) |
| sqlalchemy         | infer-basedpyright |      3 |   3 |    0 |    204 files changed, 3659 insertions(+), 3122 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      1 |   1 |    0 |    203 files changed, 3359 insertions(+), 2704 deletions(-) |
| sqlalchemy         | infer-trace        |      6 |   6 |    0 |    200 files changed, 3047 insertions(+), 2511 deletions(-) |
| sqlalchemy         | infer-ty           |      2 |   2 |    0 |    205 files changed, 3622 insertions(+), 2973 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1908 insertions(+), 1493 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1940 insertions(+), 1409 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1674 insertions(+), 1272 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1814 insertions(+), 1402 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    259 |   0 |    0 | 1069 files changed, 18263 insertions(+), 15204 deletions(-) |
| pandas             | fix-likely         |    259 |   0 |    0 | 1201 files changed, 42127 insertions(+), 38450 deletions(-) |
| pandas             | fix-unsafe         |    261 |   2 |    0 | 1204 files changed, 43225 insertions(+), 39381 deletions(-) |
| pandas             | infer-basedpyright |    300 |  41 |    0 | 1213 files changed, 49134 insertions(+), 44751 deletions(-) |
| pandas             | infer-pyrefly      |    314 |  55 |    0 | 1210 files changed, 50222 insertions(+), 45507 deletions(-) |
| pandas             | infer-trace        |    262 |   3 |    0 | 1207 files changed, 44553 insertions(+), 40633 deletions(-) |
| pandas             | infer-ty           |    266 |   7 |    0 | 1215 files changed, 48894 insertions(+), 44483 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 140 insertions(+), 106 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 443 insertions(+), 349 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 449 insertions(+), 350 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 461 insertions(+), 361 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 236 insertions(+), 166 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 219 insertions(+), 150 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-ty           |     12 |   0 |    0 |       25 files changed, 240 insertions(+), 164 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 523 insertions(+), 403 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 802 insertions(+), 568 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 832 insertions(+), 561 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 828 insertions(+), 575 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 399 insertions(+), 330 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       16 files changed, 356 insertions(+), 284 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 383 insertions(+), 306 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       27 files changed, 298 insertions(+), 219 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       27 files changed, 298 insertions(+), 219 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 298 insertions(+), 219 deletions(-) |
| uvicorn            | infer-basedpyright |      4 |   4 |    0 |       29 files changed, 370 insertions(+), 282 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 326 insertions(+), 235 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 298 insertions(+), 219 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |       29 files changed, 351 insertions(+), 266 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 780 insertions(+), 520 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 938 insertions(+), 666 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1031 insertions(+), 737 deletions(-) |
| mcp                | infer-basedpyright |      3 |   3 |    0 |      82 files changed, 1152 insertions(+), 851 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      82 files changed, 1117 insertions(+), 805 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1031 insertions(+), 737 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      82 files changed, 1157 insertions(+), 825 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | infer-basedpyright |     13 |   3 |    0 |     155 files changed, 1101 insertions(+), 840 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     11 |   1 |    0 |      153 files changed, 979 insertions(+), 733 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | infer-ty           |     11 |   1 |    0 |     155 files changed, 1098 insertions(+), 833 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | infer-basedpyright |      0 |   0 |    0 |    186 files changed, 1753 insertions(+), 1133 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |     173 files changed, 1494 insertions(+), 902 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | infer-ty           |     24 |  24 |    0 |    186 files changed, 2008 insertions(+), 1133 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      5 |   2 |    0 |    194 files changed, 3305 insertions(+), 2230 deletions(-) |
| sphinx             | fix-likely         |      5 |   2 |    0 |    197 files changed, 3830 insertions(+), 2653 deletions(-) |
| sphinx             | fix-unsafe         |      5 |   2 |    0 |    213 files changed, 4224 insertions(+), 2981 deletions(-) |
| sphinx             | infer-basedpyright |      9 |   6 |    0 |    216 files changed, 5068 insertions(+), 3740 deletions(-) |
| sphinx             | infer-pyrefly      |     14 |  11 |    0 |    217 files changed, 5340 insertions(+), 3790 deletions(-) |
| sphinx             | infer-trace        |      5 |   2 |    0 |    213 files changed, 4224 insertions(+), 2981 deletions(-) |
| sphinx             | infer-ty           |      7 |   4 |    0 |    215 files changed, 5116 insertions(+), 3709 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    42.3 |        95.0 |  2.2 |    3.98 |          3 |     4.95 | False |
| standard library   | fix-certain              |   101.7 |       255.5 |  2.5 |    5.34 |          3 |     6.61 | False |
| standard library   | fix-likely               |   115.7 |       306.7 |  2.7 |    8.14 |          3 |    10.14 | False |
| standard library   | fix-unsafe               |   117.7 |       303.7 |  2.6 |    7.52 |          3 |    10.04 | False |
| standard library   | infer-basedpyright       |   578.9 |      1128.4 |  1.9 |   13.49 |          3 |    11.31 | False |
| standard library   | infer-ty                 |   141.8 |       450.7 |  3.2 |   15.54 |          3 |    11.85 | False |
| standard library   | infer-pyrefly            |   147.0 |       453.8 |  3.1 |   17.44 |          3 |     12.8 | False |
| standard library   | census                   |    32.1 |        30.1 |  0.9 |    0.56 |          3 |     4.95 | False |
| standard library   | coverage                 |     6.2 |        22.1 |  3.6 |    1.69 |          4 |     2.06 | False |
| standard library   | timing                   |    58.4 |        89.6 |  1.5 |    3.91 |         16 |     4.81 | False |
| django             | check                    |     9.8 |        20.1 |  2.1 |    0.99 |          3 |     1.11 | False |
| django             | fix-certain              |    16.6 |        43.6 |  2.6 |    1.22 |          2 |     1.47 | False |
| django             | fix-likely               |    17.2 |        45.6 |  2.7 |    1.61 |          3 |     1.99 | False |
| django             | fix-unsafe               |    23.9 |        54.7 |  2.3 |    1.55 |          3 |     2.07 | False |
| django             | infer-basedpyright       |    73.0 |       305.7 |  4.2 |    7.08 |          4 |     2.06 | False |
| django             | infer-ty                 |    27.9 |        80.0 |  2.9 |    3.68 |          3 |     2.25 | False |
| django             | infer-pyrefly            |    27.0 |        79.6 |  2.9 |    3.84 |          3 |     2.45 | False |
| django             | census                   |     4.2 |         4.0 |  1.0 |     0.1 |          3 |     1.11 | False |
| django             | coverage                 |     2.8 |         5.8 |  2.1 |    0.37 |          3 |     0.44 | False |
| django             | timing                   |    11.8 |        18.1 |  1.5 |    0.91 |         16 |     1.11 | False |
| django             | traced                   |    65.1 |       488.0 |  7.5 |    6.47 |          2 |    29.27 |  True |
| django             | tests-released           |    48.5 |       424.8 |  8.8 |     5.0 |          9 |      6.0 | False |
| django             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |         10 |     6.21 | False |
| django             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |         11 |     6.07 | False |
| django             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |         10 |      6.3 | False |
| django             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |         11 |     6.19 | False |
| django             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |         10 |     5.91 | False |
| django             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          9 |     6.59 | False |
| django             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |         11 |     6.82 | False |
| django             | infer-union              |    77.8 |       293.0 |  3.8 |   11.14 |          4 |    12.37 | False |
| django             | tests-infer-union        |    48.7 |       436.5 |  9.0 |    5.26 |         13 |     5.93 | False |
| django             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.03 | False |
| sqlalchemy         | check                    |     9.8 |        15.5 |  1.6 |    0.93 |          3 |     1.12 | False |
| sqlalchemy         | fix-certain              |    25.3 |        43.7 |  1.7 |    1.04 |          2 |     1.27 | False |
| sqlalchemy         | fix-likely               |    28.1 |        54.4 |  1.9 |    1.46 |          2 |     1.81 | False |
| sqlalchemy         | fix-unsafe               |    24.9 |        51.8 |  2.1 |    1.34 |          2 |      1.8 | False |
| sqlalchemy         | infer-basedpyright       |    80.0 |       241.4 |  3.0 |     8.0 |          3 |     1.89 | False |
| sqlalchemy         | infer-ty                 |    35.1 |        82.9 |  2.4 |    3.74 |          3 |     1.85 | False |
| sqlalchemy         | infer-pyrefly            |    34.5 |        76.6 |  2.2 |    4.09 |          3 |      1.9 | False |
| sqlalchemy         | census                   |     4.0 |         3.8 |  0.9 |     0.1 |          3 |     1.12 | False |
| sqlalchemy         | coverage                 |     2.4 |         6.0 |  2.5 |    0.41 |          3 |      0.5 | False |
| sqlalchemy         | timing                   |    10.6 |        14.9 |  1.4 |    0.93 |         16 |     1.12 | False |
| sqlalchemy         | traced                   |   111.3 |       899.2 |  8.1 |    4.68 |          8 |     5.83 | False |
| sqlalchemy         | tests-released           |    92.1 |       927.1 | 10.1 |    5.23 |         10 |     6.51 | False |
| sqlalchemy         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |         13 |     6.29 | False |
| sqlalchemy         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          9 |     6.65 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |         13 |      5.9 | False |
| sqlalchemy         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     6.96 | False |
| sqlalchemy         | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |         12 |     6.51 | False |
| sqlalchemy         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |         10 |     4.55 | False |
| sqlalchemy         | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          9 |     6.93 | False |
| sqlalchemy         | infer-union              |    65.8 |       226.3 |  3.4 |   11.07 |          4 |    13.57 | False |
| sqlalchemy         | tests-infer-union        |    85.9 |       784.3 |  9.1 |     4.3 |         10 |     5.51 | False |
| sqlalchemy         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.03 | False |
| sqlalchemy         | types-released           |     6.4 |         5.6 |  0.9 |    0.33 |          1 |     0.42 | False |
| sqlalchemy         | types-fix-certain        |     0.6 |         0.3 |  0.5 |    0.03 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-likely         |     5.6 |         5.2 |  0.9 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-unsafe         |    10.4 |         7.2 |  0.7 |     0.3 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-basedpyright |     9.2 |         7.5 |  0.8 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |     9.2 |         6.9 |  0.8 |    0.32 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-pyrefly      |     9.0 |         7.1 |  0.8 |    0.31 |          1 |      0.4 | False |
| sqlalchemy         | types-infer-trace        |     8.6 |         7.1 |  0.8 |    0.34 |          1 |      0.4 | False |
| sqlalchemy         | types                    |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     0.4 |         0.1 |  0.2 |    0.04 |          3 |     0.39 | False |
| pydantic           | fix-certain              |     5.6 |        11.3 |  2.0 |     0.4 |          3 |     0.57 | False |
| pydantic           | fix-likely               |     6.0 |        12.9 |  2.1 |    0.52 |          3 |     0.65 | False |
| pydantic           | fix-unsafe               |     8.3 |        14.8 |  1.8 |    0.68 |          2 |     0.69 | False |
| pydantic           | infer-basedpyright       |    41.3 |        90.1 |  2.2 |    3.09 |          3 |     0.66 | False |
| pydantic           | infer-ty                 |     6.8 |        19.4 |  2.9 |    1.14 |          3 |     0.66 | False |
| pydantic           | infer-pyrefly            |    13.6 |        33.1 |  2.4 |    2.36 |          3 |     0.66 | False |
| pydantic           | census                   |     2.4 |         4.3 |  1.8 |    0.32 |          3 |     0.39 | False |
| pydantic           | coverage                 |     1.2 |         2.1 |  1.8 |    0.21 |          2 |     0.26 | False |
| pydantic           | timing                   |     2.6 |         3.7 |  1.4 |    0.32 |         16 |     0.39 | False |
| pydantic           | traced                   |    64.0 |        59.6 |  0.9 |    0.53 |          1 |      0.7 | False |
| pydantic           | tests-released           |    54.2 |        37.4 |  0.7 |    0.36 |          1 |     0.39 | False |
| pydantic           | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.4 | False |
| pydantic           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.44 | False |
| pydantic           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.37 | False |
| pydantic           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.4 | False |
| pydantic           | infer-union              |    27.5 |        85.5 |  3.1 |    5.07 |          4 |      6.7 | False |
| pydantic           | tests-infer-union        |    44.3 |        38.5 |  0.9 |    0.37 |          1 |      0.4 | False |
| pydantic           | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pydantic           | types-released           |    13.6 |        17.2 |  1.3 |    0.56 |          2 |     0.65 | False |
| pydantic           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pydantic           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.66 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.67 | False |
| pydantic           | types-infer-basedpyright |    13.0 |        17.4 |  1.3 |    0.56 |          2 |     0.67 | False |
| pydantic           | types-infer-ty           |    12.0 |        17.5 |  1.5 |    0.54 |          2 |     0.65 | False |
| pydantic           | types-infer-pyrefly      |    13.3 |        17.4 |  1.3 |    0.53 |          2 |     0.66 | False |
| pydantic           | types-infer-trace        |    15.8 |        19.2 |  1.2 |    0.54 |          2 |     0.66 | False |
| pydantic           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |     1.2 |         1.0 |  0.8 |    0.23 |          4 |     4.26 | False |
| pandas             | fix-certain              |    79.6 |       241.4 |  3.0 |    4.52 |          4 |     5.29 | False |
| pandas             | fix-likely               |   133.5 |       402.6 |  3.0 |    7.62 |          4 |     9.55 | False |
| pandas             | fix-unsafe               |   131.8 |       398.6 |  3.0 |    7.48 |          3 |     9.36 | False |
| pandas             | infer-basedpyright       |   404.6 |      1033.7 |  2.6 |   15.68 |          4 |     12.3 | False |
| pandas             | infer-ty                 |   191.9 |       685.6 |  3.6 |   12.44 |          4 |    12.29 | False |
| pandas             | infer-pyrefly            |   144.3 |       510.1 |  3.5 |   17.92 |          4 |    12.22 | False |
| pandas             | census                   |    49.1 |       112.0 |  2.3 |    3.45 |          4 |     4.26 | False |
| pandas             | coverage                 |     4.8 |        15.9 |  3.3 |    1.08 |          4 |     1.34 | False |
| pandas             | timing                   |    67.2 |       109.0 |  1.6 |    3.45 |         16 |     4.22 | False |
| pandas             | traced                   |   228.6 |      1071.6 |  4.7 |   10.59 |          7 |    12.77 | False |
| pandas             | tests-released           |    98.9 |       643.0 |  6.5 |    11.5 |         10 |    14.11 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    11.74 | False |
| pandas             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    11.72 | False |
| pandas             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    11.77 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    11.55 | False |
| pandas             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    11.51 | False |
| pandas             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    11.54 | False |
| pandas             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |    12.32 | False |
| pandas             | infer-union              |   629.6 |      1556.3 |  2.5 |   28.48 |          4 |    29.27 |  True |
| pandas             | tests-infer-union        |    94.7 |       554.7 |  5.9 |     9.9 |          8 |     11.8 | False |
| pandas             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.03 | False |
| pandas             | types-released           |    75.4 |       102.6 |  1.4 |    2.16 |          1 |     2.77 | False |
| pandas             | types-fix-certain        |    58.3 |        90.1 |  1.5 |    2.24 |          2 |     2.75 | False |
| pandas             | types-fix-likely         |    56.7 |        89.7 |  1.6 |     2.3 |          2 |     2.92 | False |
| pandas             | types-fix-unsafe         |    60.1 |        91.3 |  1.5 |    2.27 |          2 |     2.81 | False |
| pandas             | types-infer-basedpyright |    69.2 |        96.7 |  1.4 |    2.21 |          2 |     2.99 | False |
| pandas             | types-infer-ty           |    54.1 |        87.6 |  1.6 |    2.29 |          2 |     2.79 | False |
| pandas             | types-infer-pyrefly      |    47.8 |        77.1 |  1.6 |    2.34 |          2 |     2.81 | False |
| pandas             | types-infer-trace        |    62.3 |        93.3 |  1.5 |    2.38 |          2 |      2.8 | False |
| pandas             | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |     4.8 |        12.6 |  2.6 |    0.87 |          3 |     1.07 | False |
| twisted            | fix-certain              |    12.6 |        33.0 |  2.6 |    1.01 |          4 |     1.22 | False |
| twisted            | fix-likely               |    17.4 |        45.6 |  2.6 |    1.48 |          3 |     1.84 | False |
| twisted            | fix-unsafe               |    20.5 |        46.7 |  2.3 |    1.34 |          3 |     1.79 | False |
| twisted            | infer-basedpyright       |    53.3 |       218.3 |  4.1 |    8.91 |          2 |     2.21 | False |
| twisted            | infer-ty                 |    24.1 |        73.5 |  3.0 |    3.06 |          3 |     2.01 | False |
| twisted            | infer-pyrefly            |    22.1 |        74.8 |  3.4 |    4.34 |          3 |     2.06 | False |
| twisted            | census                   |     3.6 |         3.4 |  0.9 |    0.12 |          3 |     1.07 | False |
| twisted            | coverage                 |     1.8 |         4.7 |  2.6 |     0.4 |          3 |     0.47 | False |
| twisted            | timing                   |     9.0 |        13.9 |  1.5 |    0.87 |         16 |     1.06 | False |
| pip                | check                    |     3.8 |         9.1 |  2.4 |     0.6 |          3 |     0.74 | False |
| pip                | fix-certain              |    11.0 |        25.5 |  2.3 |    0.74 |          3 |     0.92 | False |
| pip                | fix-likely               |    11.8 |        30.5 |  2.6 |    0.96 |          2 |     1.17 | False |
| pip                | fix-unsafe               |    11.4 |        29.8 |  2.6 |     0.9 |          3 |     1.09 | False |
| pip                | infer-basedpyright       |    40.1 |       149.4 |  3.7 |    5.25 |          2 |     1.25 | False |
| pip                | infer-ty                 |    12.2 |        40.3 |  3.3 |     2.2 |          3 |     1.22 | False |
| pip                | infer-pyrefly            |    20.1 |        57.9 |  2.9 |    2.69 |          3 |     1.24 | False |
| pip                | census                   |     5.8 |         3.2 |  0.6 |     0.1 |          3 |     0.74 | False |
| pip                | coverage                 |     1.8 |         4.0 |  2.2 |    0.34 |          3 |     0.42 | False |
| pip                | timing                   |     6.2 |         9.2 |  1.5 |    0.58 |         16 |     0.71 | False |
| structlog          | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| structlog          | fix-certain              |     1.6 |         2.5 |  1.6 |    0.26 |          2 |     0.35 | False |
| structlog          | fix-likely               |     1.6 |         2.8 |  1.7 |    0.25 |          2 |     0.31 | False |
| structlog          | fix-unsafe               |     1.4 |         2.4 |  1.7 |    0.25 |          2 |     0.34 | False |
| structlog          | infer-basedpyright       |     8.6 |        10.9 |  1.3 |    0.55 |          2 |     0.27 | False |
| structlog          | infer-ty                 |     2.4 |         3.6 |  1.5 |    0.37 |          2 |     0.31 | False |
| structlog          | infer-pyrefly            |     2.2 |         3.4 |  1.5 |    0.28 |          2 |     0.31 | False |
| structlog          | census                   |     1.8 |         1.2 |  0.7 |    0.16 |          1 |      0.2 | False |
| structlog          | coverage                 |     1.0 |         0.8 |  0.8 |    0.14 |          1 |     0.17 | False |
| structlog          | timing                   |     0.8 |         0.8 |  1.0 |    0.16 |         16 |      0.2 | False |
| structlog          | traced                   |     4.8 |         5.0 |  1.0 |    0.28 |          1 |     0.31 | False |
| structlog          | tests-released           |     2.6 |         2.0 |  0.8 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | infer-union              |     7.2 |        12.5 |  1.7 |    1.01 |          2 |     0.31 | False |
| structlog          | tests-infer-union        |     2.6 |         2.0 |  0.8 |    0.08 |          1 |     0.09 | False |
| structlog          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| structlog          | types-released           |     0.8 |         0.4 |  0.5 |    0.08 |          1 |      0.1 | False |
| structlog          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-infer-basedpyright |     1.2 |         0.5 |  0.4 |    0.08 |          1 |     0.09 | False |
| structlog          | types-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | types-infer-pyrefly      |     0.8 |         0.4 |  0.5 |    0.08 |          1 |     0.09 | False |
| structlog          | types-infer-trace        |     0.6 |         0.4 |  0.7 |    0.07 |          1 |      0.1 | False |
| structlog          | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     1.4 |         1.0 |  0.7 |    0.15 |          1 |     0.19 | False |
| attrs              | fix-certain              |     3.1 |         2.6 |  0.8 |    0.27 |          2 |     0.32 | False |
| attrs              | fix-likely               |     2.2 |         2.7 |  1.2 |    0.26 |          2 |     0.32 | False |
| attrs              | fix-unsafe               |     1.6 |         2.1 |  1.3 |    0.26 |          1 |     0.32 | False |
| attrs              | infer-basedpyright       |    11.0 |        12.6 |  1.1 |    0.56 |          2 |     0.29 | False |
| attrs              | infer-ty                 |     3.4 |         3.9 |  1.1 |    0.38 |          2 |     0.32 | False |
| attrs              | infer-pyrefly            |     4.8 |         7.6 |  1.6 |    0.43 |          2 |      0.3 | False |
| attrs              | census                   |     0.6 |         0.2 |  0.3 |    0.04 |          1 |     0.19 | False |
| attrs              | coverage                 |     1.0 |         0.8 |  0.8 |    0.14 |          1 |     0.17 | False |
| attrs              | timing                   |     0.8 |         0.7 |  0.9 |    0.15 |         16 |     0.19 | False |
| attrs              | traced                   |     5.6 |        23.0 |  4.1 |    0.75 |          5 |     0.92 | False |
| attrs              | tests-released           |     5.0 |        19.7 |  3.9 |     0.6 |          4 |     0.74 | False |
| attrs              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.75 | False |
| attrs              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.74 | False |
| attrs              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     0.76 | False |
| attrs              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.72 | False |
| attrs              | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     0.74 | False |
| attrs              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     0.72 | False |
| attrs              | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.75 | False |
| attrs              | infer-union              |     8.2 |        16.5 |  2.0 |     1.1 |          2 |     1.37 | False |
| attrs              | tests-infer-union        |     4.8 |        17.0 |  3.5 |    0.59 |          6 |     0.76 | False |
| attrs              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.22 | False |
| click              | fix-certain              |     1.8 |         3.2 |  1.8 |    0.28 |          2 |     0.37 | False |
| click              | fix-likely               |     2.2 |         3.8 |  1.7 |     0.3 |          2 |     0.37 | False |
| click              | fix-unsafe               |     2.8 |         4.1 |  1.5 |     0.3 |          2 |     0.37 | False |
| click              | infer-basedpyright       |     7.0 |        11.3 |  1.6 |    0.65 |          2 |     0.31 | False |
| click              | infer-ty                 |     3.0 |         4.9 |  1.6 |    0.31 |          2 |     0.37 | False |
| click              | infer-pyrefly            |     3.0 |         7.9 |  2.6 |     0.6 |          2 |     0.39 | False |
| click              | census                   |     1.4 |         1.7 |  1.2 |    0.18 |          2 |     0.22 | False |
| click              | coverage                 |     1.4 |         1.1 |  0.8 |    0.16 |          1 |      0.2 | False |
| click              | timing                   |     1.0 |         1.1 |  1.1 |    0.18 |         16 |     0.22 | False |
| click              | traced                   |    10.4 |        10.6 |  1.0 |    0.29 |          1 |     0.39 | False |
| click              | tests-released           |     7.4 |         6.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | infer-union              |    13.2 |        23.7 |  1.8 |    1.09 |          2 |     0.36 | False |
| click              | tests-infer-union        |     5.0 |         4.7 |  0.9 |    0.17 |          1 |     0.21 | False |
| click              | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| click              | types-released           |     1.4 |         0.7 |  0.5 |    0.12 |          1 |     0.15 | False |
| click              | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-infer-basedpyright |     0.8 |         0.5 |  0.6 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-ty           |     0.8 |         0.6 |  0.7 |     0.1 |          1 |     0.12 | False |
| click              | types-infer-pyrefly      |     0.8 |         0.5 |  0.6 |    0.12 |          1 |     0.12 | False |
| click              | types-infer-trace        |     1.0 |         0.7 |  0.7 |     0.1 |          1 |     0.15 | False |
| click              | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     1.2 |         1.2 |  1.0 |    0.18 |          2 |     0.21 | False |
| hypercorn          | fix-certain              |     2.4 |         3.2 |  1.3 |    0.28 |          2 |     0.31 | False |
| hypercorn          | fix-likely               |     1.8 |         3.1 |  1.7 |    0.25 |          2 |     0.32 | False |
| hypercorn          | fix-unsafe               |     2.6 |         3.3 |  1.3 |    0.21 |          2 |     0.31 | False |
| hypercorn          | infer-basedpyright       |    11.8 |        19.0 |  1.6 |    0.94 |          2 |     0.29 | False |
| hypercorn          | infer-ty                 |     2.0 |         4.1 |  2.0 |    0.32 |          2 |     0.31 | False |
| hypercorn          | infer-pyrefly            |     3.4 |         9.9 |  2.9 |    0.74 |          2 |     0.31 | False |
| hypercorn          | census                   |     0.8 |         0.3 |  0.4 |    0.03 |          2 |     0.21 | False |
| hypercorn          | coverage                 |     1.2 |         0.8 |  0.7 |    0.14 |          1 |     0.17 | False |
| hypercorn          | timing                   |     0.8 |         0.9 |  1.1 |    0.18 |         16 |     0.22 | False |
| hypercorn          | traced                   |    10.0 |         5.3 |  0.5 |    0.29 |          1 |     0.37 | False |
| hypercorn          | tests-released           |     7.6 |         1.4 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-ty           |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | infer-union              |    10.2 |        23.9 |  2.3 |    1.89 |          2 |     0.32 | False |
| hypercorn          | tests-infer-union        |     8.4 |         1.7 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| hypercorn          | types-released           |     1.8 |         1.1 |  0.6 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| hypercorn          | types-fix-likely         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-infer-basedpyright |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-ty           |     1.2 |         0.7 |  0.6 |     0.1 |          1 |     0.12 | False |
| hypercorn          | types-infer-pyrefly      |     1.2 |         0.9 |  0.8 |    0.12 |          1 |     0.14 | False |
| hypercorn          | types-infer-trace        |     1.6 |         1.1 |  0.7 |    0.11 |          1 |     0.15 | False |
| hypercorn          | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.22 | False |
| starlette          | fix-certain              |     2.0 |         3.3 |  1.6 |    0.26 |          2 |     0.34 | False |
| starlette          | fix-likely               |     2.0 |         3.9 |  1.9 |    0.26 |          2 |     0.32 | False |
| starlette          | fix-unsafe               |     2.2 |         3.7 |  1.7 |    0.26 |          2 |     0.37 | False |
| starlette          | infer-basedpyright       |     5.0 |        11.2 |  2.2 |    0.91 |          2 |      0.3 | False |
| starlette          | infer-ty                 |     2.0 |         4.5 |  2.2 |    0.38 |          3 |     0.32 | False |
| starlette          | infer-pyrefly            |     5.7 |        13.8 |  2.4 |    0.91 |          2 |     0.32 | False |
| starlette          | census                   |     1.2 |         1.4 |  1.2 |    0.19 |          2 |     0.22 | False |
| starlette          | coverage                 |     1.2 |         1.0 |  0.8 |    0.15 |          1 |     0.19 | False |
| starlette          | timing                   |     1.0 |         1.1 |  1.1 |    0.19 |         16 |     0.22 | False |
| starlette          | traced                   |    14.0 |        11.5 |  0.8 |    0.31 |          1 |     0.35 | False |
| starlette          | tests-released           |    10.6 |         6.7 |  0.6 |    0.23 |          1 |     0.29 | False |
| starlette          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-infer-basedpyright |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.29 | False |
| starlette          | infer-union              |    11.4 |        31.7 |  2.8 |    2.13 |          2 |     0.34 | False |
| starlette          | tests-infer-union        |    10.2 |         6.3 |  0.6 |    0.23 |          1 |     0.29 | False |
| starlette          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | types-released           |     3.0 |         1.7 |  0.6 |    0.14 |          1 |     0.17 | False |
| starlette          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| starlette          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.16 | False |
| starlette          | types-infer-basedpyright |     2.4 |         1.6 |  0.7 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-ty           |     0.8 |         0.5 |  0.6 |    0.12 |          1 |     0.12 | False |
| starlette          | types-infer-pyrefly      |     2.0 |         1.6 |  0.8 |    0.13 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| starlette          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     1.0 |         1.6 |  1.6 |    0.21 |          2 |     0.26 | False |
| werkzeug           | fix-certain              |     2.8 |         5.0 |  1.8 |    0.32 |          3 |     0.41 | False |
| werkzeug           | fix-likely               |     2.2 |         5.1 |  2.3 |    0.33 |          3 |     0.42 | False |
| werkzeug           | fix-unsafe               |     3.6 |         6.1 |  1.7 |     0.3 |          2 |     0.41 | False |
| werkzeug           | infer-basedpyright       |     8.2 |        24.6 |  3.0 |    1.18 |          3 |     0.36 | False |
| werkzeug           | infer-ty                 |     3.4 |         8.4 |  2.5 |    0.74 |          3 |     0.37 | False |
| werkzeug           | infer-pyrefly            |     3.8 |        10.6 |  2.8 |    0.79 |          3 |     0.41 | False |
| werkzeug           | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          2 |     0.26 | False |
| werkzeug           | coverage                 |     1.2 |         1.4 |  1.2 |    0.17 |          2 |     0.21 | False |
| werkzeug           | timing                   |     1.4 |         1.8 |  1.3 |    0.21 |         16 |     0.26 | False |
| werkzeug           | traced                   |    14.4 |        14.5 |  1.0 |    0.34 |          1 |     0.45 | False |
| werkzeug           | tests-released           |     9.7 |         7.1 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-trace        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.21 | False |
| werkzeug           | infer-union              |    11.4 |        41.7 |  3.7 |    2.51 |          3 |     0.36 | False |
| werkzeug           | tests-infer-union        |     7.6 |         6.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | types-released           |     1.8 |         1.0 |  0.6 |    0.11 |          1 |     0.16 | False |
| werkzeug           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| werkzeug           | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-infer-basedpyright |     1.0 |         0.8 |  0.8 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-infer-ty           |     0.8 |         0.6 |  0.7 |    0.13 |          1 |     0.12 | False |
| werkzeug           | types-infer-pyrefly      |     1.0 |         0.8 |  0.8 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-infer-trace        |     1.4 |         1.0 |  0.7 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     2.0 |         2.5 |  1.2 |    0.26 |          2 |     0.32 | False |
| mkdocs             | fix-certain              |     4.4 |         6.3 |  1.4 |    0.36 |          1 |     0.44 | False |
| mkdocs             | fix-likely               |     4.0 |         7.4 |  1.9 |    0.36 |          2 |     0.47 | False |
| mkdocs             | fix-unsafe               |     3.2 |         6.5 |  2.0 |    0.37 |          3 |     0.46 | False |
| mkdocs             | infer-basedpyright       |    15.0 |        34.3 |  2.3 |    1.21 |          3 |      0.4 | False |
| mkdocs             | infer-ty                 |     4.8 |        10.4 |  2.2 |    0.75 |          3 |     0.45 | False |
| mkdocs             | infer-pyrefly            |     5.8 |        16.5 |  2.8 |     1.0 |          3 |     0.46 | False |
| mkdocs             | census                   |     1.4 |         0.8 |  0.6 |    0.05 |          2 |     0.32 | False |
| mkdocs             | coverage                 |     1.2 |         1.4 |  1.2 |    0.18 |          2 |     0.22 | False |
| mkdocs             | timing                   |     1.6 |         2.0 |  1.2 |    0.27 |         16 |     0.32 | False |
| mkdocs             | traced                   |    17.0 |        11.7 |  0.7 |    0.36 |          1 |     0.46 | False |
| mkdocs             | tests-released           |    11.1 |         2.5 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | infer-union              |    17.5 |        53.9 |  3.1 |    2.41 |          4 |     2.46 | False |
| mkdocs             | tests-infer-union        |    10.5 |         2.5 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | check                    |     1.4 |         1.3 |  0.9 |    0.18 |          2 |     0.22 | False |
| httpx              | fix-certain              |     3.4 |         3.7 |  1.1 |    0.25 |          2 |     0.32 | False |
| httpx              | fix-likely               |     2.0 |         3.4 |  1.7 |    0.27 |          2 |     0.32 | False |
| httpx              | fix-unsafe               |     3.4 |         4.0 |  1.2 |    0.29 |          1 |     0.36 | False |
| httpx              | infer-basedpyright       |     7.6 |        12.5 |  1.6 |    0.65 |          2 |     0.29 | False |
| httpx              | infer-ty                 |     3.2 |         4.7 |  1.5 |    0.36 |          2 |     0.34 | False |
| httpx              | infer-pyrefly            |     4.4 |         8.7 |  2.0 |     0.5 |          2 |     0.32 | False |
| httpx              | census                   |     0.6 |         0.3 |  0.5 |    0.03 |          2 |     0.22 | False |
| httpx              | coverage                 |     0.8 |         0.8 |  1.0 |    0.14 |          1 |     0.19 | False |
| httpx              | timing                   |     0.8 |         1.0 |  1.2 |    0.18 |         16 |     0.22 | False |
| httpx              | traced                   |    11.2 |        10.1 |  0.9 |    0.28 |          1 |     0.35 | False |
| httpx              | tests-released           |     8.1 |         5.7 |  0.7 |    0.22 |          1 |     0.26 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| httpx              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| httpx              | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.27 | False |
| httpx              | infer-union              |     9.5 |        15.5 |  1.6 |    1.27 |          2 |     0.34 | False |
| httpx              | tests-infer-union        |     6.6 |         5.1 |  0.8 |    0.22 |          1 |     0.27 | False |
| httpx              | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| httpx              | types-released           |     6.6 |         5.7 |  0.9 |    0.24 |          1 |      0.3 | False |
| httpx              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.24 | False |
| httpx              | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.24 | False |
| httpx              | types-infer-basedpyright |     7.2 |         6.1 |  0.8 |    0.24 |          1 |     0.25 | False |
| httpx              | types-infer-ty           |     6.0 |         5.6 |  0.9 |    0.19 |          1 |     0.24 | False |
| httpx              | types-infer-pyrefly      |     5.8 |         5.3 |  0.9 |     0.2 |          1 |     0.25 | False |
| httpx              | types-infer-trace        |     7.2 |         6.2 |  0.9 |    0.19 |          1 |     0.24 | False |
| httpx              | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.24 | False |
| black              | fix-certain              |     4.2 |         4.6 |  1.1 |    0.33 |          3 |      0.4 | False |
| black              | fix-likely               |     2.0 |         4.5 |  2.2 |    0.31 |          3 |     0.41 | False |
| black              | fix-unsafe               |     3.2 |         5.3 |  1.7 |    0.31 |          2 |      0.4 | False |
| black              | infer-basedpyright       |    13.2 |        21.3 |  1.6 |    0.78 |          2 |     0.31 | False |
| black              | infer-ty                 |     3.4 |         6.7 |  2.0 |    0.53 |          3 |      0.4 | False |
| black              | infer-pyrefly            |     2.8 |         8.5 |  3.0 |    0.55 |          3 |      0.4 | False |
| black              | census                   |     1.2 |         1.7 |  1.4 |     0.2 |          2 |     0.24 | False |
| black              | coverage                 |     1.2 |         1.2 |  1.0 |    0.17 |          2 |     0.21 | False |
| black              | timing                   |     1.2 |         1.3 |  1.1 |    0.19 |         16 |     0.24 | False |
| black              | traced                   |     8.0 |        48.8 |  6.1 |    0.88 |          8 |     1.11 | False |
| black              | tests-released           |     7.0 |        43.0 |  6.1 |    0.76 |          7 |     0.92 | False |
| black              | tests-fix-certain        |     5.4 |        37.3 |  6.9 |    0.77 |          8 |     0.91 | False |
| black              | tests-fix-likely         |     5.6 |        36.3 |  6.5 |    0.76 |          8 |     0.92 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.94 | False |
| black              | tests-infer-basedpyright |     5.4 |        36.1 |  6.7 |    0.72 |          8 |     0.99 | False |
| black              | tests-infer-ty           |     5.8 |        37.3 |  6.4 |    0.77 |          8 |     0.96 | False |
| black              | tests-infer-pyrefly      |     5.4 |        36.2 |  6.7 |    0.74 |          8 |     0.95 | False |
| black              | tests-infer-trace        |     5.2 |        36.0 |  6.9 |    0.76 |          8 |     0.99 | False |
| black              | infer-union              |     5.2 |        12.2 |  2.3 |    1.39 |          3 |     0.36 | False |
| black              | tests-infer-union        |     5.4 |        35.1 |  6.5 |    0.77 |          7 |     0.96 | False |
| black              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| fastapi            | check                    |     1.2 |         1.4 |  1.2 |    0.22 |          2 |     0.27 | False |
| fastapi            | fix-certain              |     2.8 |         4.3 |  1.5 |    0.33 |          2 |     0.42 | False |
| fastapi            | fix-likely               |     5.4 |         6.8 |  1.3 |    0.47 |          2 |     0.56 | False |
| fastapi            | fix-unsafe               |     5.8 |         7.1 |  1.2 |    0.47 |          2 |     0.51 | False |
| fastapi            | infer-basedpyright       |    13.8 |        31.8 |  2.3 |    1.27 |          2 |     0.39 | False |
| fastapi            | infer-ty                 |     8.0 |        10.9 |  1.4 |    0.56 |          2 |     0.44 | False |
| fastapi            | infer-pyrefly            |     6.0 |        16.0 |  2.7 |    1.12 |          2 |     0.41 | False |
| fastapi            | census                   |     0.6 |         0.4 |  0.7 |    0.05 |          2 |     0.27 | False |
| fastapi            | coverage                 |     1.2 |         1.2 |  1.0 |    0.17 |          1 |     0.21 | False |
| fastapi            | timing                   |     1.4 |         1.5 |  1.1 |    0.22 |         16 |     0.27 | False |
| fastapi            | traced                   |    18.2 |       112.8 |  6.2 |     2.4 |          8 |     2.91 | False |
| fastapi            | tests-released           |    15.0 |        94.6 |  6.3 |    2.09 |          7 |      2.6 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     2.62 | False |
| fastapi            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     2.62 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.62 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.62 | False |
| fastapi            | infer-union              |    13.8 |        35.7 |  2.6 |    2.34 |          2 |      0.4 | False |
| fastapi            | tests-infer-union        |    15.8 |        97.5 |  6.2 |    2.04 |          7 |     2.62 | False |
| fastapi            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| cattrs             | check                    |     1.6 |         1.4 |  0.9 |    0.18 |          2 |     0.22 | False |
| cattrs             | fix-certain              |     3.0 |         3.6 |  1.2 |    0.27 |          2 |     0.31 | False |
| cattrs             | fix-likely               |     2.0 |         3.2 |  1.6 |    0.25 |          2 |     0.34 | False |
| cattrs             | fix-unsafe               |     2.4 |         3.4 |  1.4 |    0.27 |          2 |     0.31 | False |
| cattrs             | infer-basedpyright       |     6.2 |        14.5 |  2.3 |    0.95 |          2 |     0.29 | False |
| cattrs             | infer-ty                 |     2.0 |         4.1 |  2.0 |    0.62 |          2 |     0.35 | False |
| cattrs             | infer-pyrefly            |     3.2 |         7.8 |  2.4 |    0.68 |          2 |      0.3 | False |
| cattrs             | census                   |     0.6 |         0.3 |  0.5 |    0.03 |          2 |     0.22 | False |
| cattrs             | coverage                 |     1.0 |         0.8 |  0.8 |    0.14 |          1 |     0.17 | False |
| cattrs             | timing                   |     1.0 |         1.0 |  1.0 |    0.18 |         16 |     0.22 | False |
| cattrs             | traced                   |    21.8 |       133.1 |  6.1 |    1.28 |          8 |     1.62 | False |
| cattrs             | tests-released           |    18.2 |       123.1 |  6.8 |    1.01 |          8 |     1.22 | False |
| cattrs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.15 | False |
| cattrs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.15 | False |
| cattrs             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.34 | False |
| cattrs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.15 | False |
| cattrs             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.22 | False |
| cattrs             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.22 | False |
| cattrs             | infer-union              |     8.6 |        22.6 |  2.6 |    1.94 |          2 |     0.32 | False |
| cattrs             | tests-infer-union        |    20.2 |       120.6 |  6.0 |    0.94 |          8 |     1.27 | False |
| cattrs             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pytest             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.35 | False |
| pytest             | fix-certain              |     3.6 |         7.8 |  2.2 |    0.38 |          3 |     0.54 | False |
| pytest             | fix-likely               |     6.0 |        11.4 |  1.9 |    0.44 |          3 |     0.55 | False |
| pytest             | fix-unsafe               |     5.6 |        10.7 |  1.9 |    0.43 |          2 |     0.55 | False |
| pytest             | infer-basedpyright       |    20.2 |        59.4 |  2.9 |    2.14 |          2 |     0.51 | False |
| pytest             | infer-ty                 |     8.4 |        16.8 |  2.0 |    1.24 |          3 |     0.52 | False |
| pytest             | infer-pyrefly            |    11.2 |        22.5 |  2.0 |     1.4 |          3 |     0.57 | False |
| pytest             | census                   |     3.0 |         4.1 |  1.4 |    0.29 |          2 |     0.35 | False |
| pytest             | coverage                 |     1.6 |         2.0 |  1.2 |     0.2 |          2 |     0.25 | False |
| pytest             | timing                   |     2.6 |         3.2 |  1.2 |    0.29 |         16 |     0.35 | False |
| pytest             | traced                   |    48.5 |       325.2 |  6.7 |    1.77 |          8 |     2.21 | False |
| pytest             | tests-released           |    21.6 |       157.1 |  7.3 |    1.38 |          8 |     1.69 | False |
| pytest             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.67 | False |
| pytest             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.69 | False |
| pytest             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.71 | False |
| pytest             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.7 | False |
| pytest             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      1.7 | False |
| pytest             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      1.7 | False |
| pytest             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.71 | False |
| pytest             | infer-union              |    17.6 |        69.2 |  3.9 |    3.87 |          4 |     4.76 | False |
| pytest             | tests-infer-union        |    22.0 |       158.5 |  7.2 |    1.39 |          8 |      1.7 | False |
| pytest             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| botocore           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          3 |     0.37 | False |
| botocore           | fix-certain              |     4.2 |         9.6 |  2.3 |     0.4 |          3 |     0.51 | False |
| botocore           | fix-likely               |     6.0 |        12.9 |  2.1 |    0.49 |          3 |     0.59 | False |
| botocore           | fix-unsafe               |     4.2 |         9.9 |  2.4 |    0.48 |          3 |      0.6 | False |
| botocore           | infer-basedpyright       |    18.4 |        50.0 |  2.7 |    2.48 |          3 |     0.66 | False |
| botocore           | infer-ty                 |     7.8 |        18.2 |  2.3 |    1.25 |          3 |      0.6 | False |
| botocore           | infer-pyrefly            |     7.4 |        17.3 |  2.3 |    1.31 |          3 |      0.6 | False |
| botocore           | census                   |     2.4 |         4.3 |  1.8 |    0.31 |          3 |     0.37 | False |
| botocore           | coverage                 |     1.8 |         1.9 |  1.1 |     0.2 |          2 |     0.25 | False |
| botocore           | timing                   |     2.8 |         3.9 |  1.4 |    0.31 |         16 |     0.37 | False |
| botocore           | traced                   |    35.9 |       114.5 |  3.2 |    5.13 |          5 |     6.37 | False |
| botocore           | tests-released           |    29.9 |        95.5 |  3.2 |    4.96 |          4 |     6.11 | False |
| botocore           | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     6.05 | False |
| botocore           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     6.05 | False |
| botocore           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     6.07 | False |
| botocore           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     6.06 | False |
| botocore           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.11 | False |
| botocore           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |      6.0 | False |
| botocore           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.12 | False |
| botocore           | infer-union              |    22.2 |        56.4 |  2.5 |    3.67 |          3 |     4.41 | False |
| botocore           | tests-infer-union        |    33.5 |        94.8 |  2.8 |    4.93 |          4 |     6.16 | False |
| botocore           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | check                    |     1.6 |         1.4 |  0.9 |    0.18 |          2 |     0.22 | False |
| uvicorn            | fix-certain              |     2.2 |         3.6 |  1.6 |    0.26 |          2 |     0.37 | False |
| uvicorn            | fix-likely               |     3.4 |         4.4 |  1.3 |    0.26 |          2 |     0.32 | False |
| uvicorn            | fix-unsafe               |     3.0 |         4.4 |  1.5 |     0.3 |          2 |     0.37 | False |
| uvicorn            | infer-basedpyright       |    10.6 |        17.5 |  1.7 |    0.92 |          2 |      0.3 | False |
| uvicorn            | infer-ty                 |     3.8 |         5.9 |  1.6 |     0.4 |          3 |     0.35 | False |
| uvicorn            | infer-pyrefly            |     4.0 |         8.8 |  2.2 |    0.96 |          3 |     0.32 | False |
| uvicorn            | census                   |     0.6 |         0.4 |  0.7 |    0.03 |          2 |     0.22 | False |
| uvicorn            | coverage                 |     1.4 |         0.9 |  0.6 |    0.15 |          1 |     0.19 | False |
| uvicorn            | timing                   |     1.0 |         1.1 |  1.1 |    0.18 |         16 |     0.22 | False |
| uvicorn            | traced                   |    43.7 |        29.0 |  0.7 |    0.94 |          1 |     1.24 | False |
| uvicorn            | tests-released           |    29.7 |        19.9 |  0.7 |    0.85 |          1 |     1.02 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.04 | False |
| uvicorn            | tests-fix-unsafe         |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     1.02 | False |
| uvicorn            | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.97 | False |
| uvicorn            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.02 | False |
| uvicorn            | infer-union              |     7.0 |        21.6 |  3.1 |    2.13 |          3 |     0.32 | False |
| uvicorn            | tests-infer-union        |    40.1 |        21.9 |  0.5 |    0.84 |          1 |     1.09 | False |
| uvicorn            | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| uvicorn            | types-released           |     2.6 |         1.7 |  0.7 |    0.13 |          1 |     0.19 | False |
| uvicorn            | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-infer-basedpyright |     1.4 |         1.2 |  0.9 |    0.12 |          1 |     0.15 | False |
| uvicorn            | types-infer-ty           |     2.4 |         1.6 |  0.7 |    0.14 |          1 |     0.14 | False |
| uvicorn            | types-infer-pyrefly      |     1.8 |         1.0 |  0.6 |    0.12 |          1 |     0.14 | False |
| uvicorn            | types-infer-trace        |     1.6 |         1.4 |  0.9 |    0.13 |          1 |     0.19 | False |
| uvicorn            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     2.4 |         3.1 |  1.3 |    0.26 |          2 |     0.32 | False |
| mcp                | fix-certain              |     2.8 |         6.3 |  2.2 |    0.33 |          3 |     0.46 | False |
| mcp                | fix-likely               |     3.8 |         9.1 |  2.4 |    0.45 |          3 |     0.55 | False |
| mcp                | fix-unsafe               |     7.8 |        10.5 |  1.3 |     0.5 |          2 |      0.6 | False |
| mcp                | infer-basedpyright       |    13.6 |        43.6 |  3.2 |    2.42 |          2 |     0.54 | False |
| mcp                | infer-ty                 |     4.0 |        10.1 |  2.5 |    1.31 |          3 |     0.54 | False |
| mcp                | infer-pyrefly            |     5.8 |        18.5 |  3.2 |    1.86 |          3 |     0.54 | False |
| mcp                | census                   |     0.6 |         0.4 |  0.7 |    0.04 |          2 |     0.32 | False |
| mcp                | coverage                 |     1.2 |         1.7 |  1.4 |    0.18 |          2 |     0.22 | False |
| mcp                | timing                   |     2.0 |         2.5 |  1.2 |    0.27 |         16 |     0.32 | False |
| mcp                | traced                   |    23.2 |        93.4 |  4.0 |    2.03 |          6 |     2.55 | False |
| mcp                | tests-released           |    15.2 |        65.5 |  4.3 |    1.87 |          6 |     2.29 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.24 | False |
| mcp                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     2.24 | False |
| mcp                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      2.3 | False |
| mcp                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     2.24 | False |
| mcp                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     2.29 | False |
| mcp                | infer-union              |    14.7 |        48.7 |  3.3 |    3.95 |          3 |     0.54 | False |
| mcp                | tests-infer-union        |    17.6 |        76.2 |  4.3 |    1.79 |          6 |     2.31 | False |
| mcp                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mcp                | types-released           |    27.3 |        28.8 |  1.1 |    1.24 |          1 |     1.46 | False |
| mcp                | types-fix-certain        |    20.3 |        27.9 |  1.4 |    1.27 |          2 |     1.59 | False |
| mcp                | types-fix-likely         |    18.7 |        26.4 |  1.4 |    1.25 |          2 |     1.57 | False |
| mcp                | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.57 | False |
| mcp                | types-infer-basedpyright |    18.4 |        26.1 |  1.4 |    1.28 |          2 |     1.55 | False |
| mcp                | types-infer-ty           |    20.9 |        26.0 |  1.2 |     1.3 |          2 |     1.61 | False |
| mcp                | types-infer-pyrefly      |    22.9 |        29.8 |  1.3 |    1.24 |          2 |      1.5 | False |
| mcp                | types-infer-trace        |    20.3 |        25.6 |  1.3 |    1.25 |          2 |     1.56 | False |
| mcp                | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     2.8 |         5.9 |  2.1 |    0.46 |          3 |     0.56 | False |
| textual            | fix-certain              |     6.6 |        15.7 |  2.4 |    0.54 |          3 |     0.69 | False |
| textual            | fix-likely               |     6.8 |        18.2 |  2.7 |    0.64 |          3 |      0.8 | False |
| textual            | fix-unsafe               |     5.6 |        16.0 |  2.9 |    0.57 |          3 |     0.75 | False |
| textual            | infer-basedpyright       |    22.3 |        80.9 |  3.6 |    3.63 |          3 |     0.79 | False |
| textual            | infer-ty                 |    13.6 |        33.0 |  2.4 |    1.65 |          1 |     0.82 | False |
| textual            | infer-pyrefly            |     9.6 |        32.0 |  3.3 |    1.99 |          2 |     0.79 | False |
| textual            | census                   |     2.0 |         1.6 |  0.8 |    0.06 |          3 |     0.56 | False |
| textual            | coverage                 |     1.2 |         2.8 |  2.3 |    0.26 |          3 |     0.32 | False |
| textual            | timing                   |     4.0 |         5.7 |  1.4 |    0.45 |         16 |     0.56 | False |
| pdm                | check                    |     2.2 |         3.8 |  1.7 |    0.44 |          2 |      0.6 | False |
| pdm                | fix-certain              |     6.2 |        11.1 |  1.8 |    0.48 |          3 |     0.59 | False |
| pdm                | fix-likely               |     5.4 |        12.5 |  2.3 |    0.56 |          3 |     0.69 | False |
| pdm                | fix-unsafe               |     7.0 |        13.1 |  1.9 |    0.68 |          2 |     0.69 | False |
| pdm                | infer-basedpyright       |    12.0 |        41.5 |  3.5 |    2.49 |          3 |     0.69 | False |
| pdm                | infer-ty                 |     6.0 |        15.9 |  2.6 |    1.54 |          3 |     0.69 | False |
| pdm                | infer-pyrefly            |     7.8 |        23.2 |  3.0 |    1.55 |          3 |     0.69 | False |
| pdm                | census                   |     1.2 |         0.6 |  0.5 |    0.04 |          2 |      0.6 | False |
| pdm                | coverage                 |     0.8 |         1.3 |  1.6 |    0.19 |          2 |     0.24 | False |
| pdm                | timing                   |     2.8 |         3.7 |  1.3 |    0.44 |         16 |     0.54 | False |
| pdm                | traced                   |    28.7 |       134.0 |  4.7 |    1.62 |          5 |     1.97 | False |
| pdm                | tests-released           |    15.2 |        84.3 |  5.5 |    1.29 |          7 |     1.51 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.61 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      1.5 | False |
| pdm                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.62 | False |
| pdm                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.61 | False |
| pdm                | infer-union              |    18.6 |        70.2 |  3.8 |    4.25 |          3 |      0.7 | False |
| pdm                | tests-infer-union        |    21.0 |       105.0 |  5.0 |    1.37 |          8 |     1.71 | False |
| pdm                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | check                    |     3.4 |         4.5 |  1.3 |    0.35 |          2 |     0.42 | False |
| strawberry-graphql | fix-certain              |     4.0 |         9.5 |  2.4 |    0.44 |          3 |     0.55 | False |
| strawberry-graphql | fix-likely               |     4.6 |        11.1 |  2.4 |    0.59 |          3 |     0.72 | False |
| strawberry-graphql | fix-unsafe               |     8.0 |        13.4 |  1.7 |    0.72 |          2 |     0.81 | False |
| strawberry-graphql | infer-basedpyright       |    19.9 |        90.9 |  4.6 |    3.21 |          3 |     0.64 | False |
| strawberry-graphql | infer-ty                 |     7.0 |        19.8 |  2.8 |    1.56 |          3 |     0.64 | False |
| strawberry-graphql | infer-pyrefly            |     8.0 |        34.4 |  4.3 |    2.21 |          3 |     0.64 | False |
| strawberry-graphql | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          2 |     0.42 | False |
| strawberry-graphql | coverage                 |     1.0 |         1.6 |  1.6 |    0.19 |          2 |     0.22 | False |
| strawberry-graphql | timing                   |     2.6 |         3.6 |  1.4 |    0.35 |         16 |     0.42 | False |
| strawberry-graphql | traced                   |    21.2 |       112.8 |  5.3 |    1.49 |          8 |     1.85 | False |
| strawberry-graphql | tests-released           |    14.2 |        83.2 |  5.9 |    1.32 |          6 |     1.57 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.56 | False |
| strawberry-graphql | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.54 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.62 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.54 | False |
| strawberry-graphql | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.55 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.54 | False |
| strawberry-graphql | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.59 | False |
| strawberry-graphql | infer-union              |    21.1 |       104.2 |  4.9 |    4.18 |          3 |     0.64 | False |
| strawberry-graphql | tests-infer-union        |    13.6 |        85.7 |  6.3 |    1.27 |          8 |     1.59 | False |
| strawberry-graphql | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | types-released           |     3.2 |         2.0 |  0.6 |    0.25 |          1 |     0.31 | False |
| strawberry-graphql | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-basedpyright |     1.6 |         1.4 |  0.9 |    0.19 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-ty           |     1.8 |         1.6 |  0.9 |    0.19 |          1 |     0.25 | False |
| strawberry-graphql | types-infer-pyrefly      |     3.2 |         2.2 |  0.7 |    0.24 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-trace        |     2.2 |         1.9 |  0.9 |    0.25 |          1 |     0.29 | False |
| strawberry-graphql | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     2.4 |         5.7 |  2.4 |    0.43 |          3 |     0.52 | False |
| pygments           | fix-certain              |     5.6 |        15.0 |  2.7 |    0.59 |          3 |     0.74 | False |
| pygments           | fix-likely               |     6.4 |        17.2 |  2.7 |     0.6 |          3 |     0.74 | False |
| pygments           | fix-unsafe               |     6.2 |        16.7 |  2.7 |    0.59 |          3 |     0.74 | False |
| pygments           | infer-basedpyright       |    32.5 |        93.0 |  2.9 |    2.41 |          3 |     0.76 | False |
| pygments           | infer-ty                 |    11.0 |        24.8 |  2.3 |    1.12 |          3 |      0.8 | False |
| pygments           | infer-pyrefly            |    12.8 |        29.9 |  2.3 |    1.71 |          3 |      0.8 | False |
| pygments           | census                   |     3.4 |         2.7 |  0.8 |    0.06 |          3 |     0.52 | False |
| pygments           | coverage                 |     2.0 |         3.3 |  1.6 |    0.29 |          2 |     0.36 | False |
| pygments           | timing                   |     4.0 |         5.8 |  1.4 |    0.43 |         16 |     0.54 | False |
| pygments           | traced                   |    32.5 |        38.5 |  1.2 |    0.69 |          1 |     0.79 | False |
| pygments           | tests-released           |    15.1 |        12.8 |  0.8 |    0.29 |          1 |     0.35 | False |
| pygments           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.36 | False |
| pygments           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.35 | False |
| pygments           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.36 | False |
| pygments           | infer-union              |    40.7 |       121.5 |  3.0 |    5.77 |          4 |     6.27 | False |
| pygments           | tests-infer-union        |    16.0 |        14.4 |  0.9 |    0.29 |          1 |     0.36 | False |
| pygments           | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| streamlink         | check                    |     1.8 |         3.8 |  2.1 |    0.32 |          3 |      0.4 | False |
| streamlink         | fix-certain              |     5.2 |        11.9 |  2.3 |    0.47 |          3 |     0.59 | False |
| streamlink         | fix-likely               |     5.2 |        13.5 |  2.6 |     0.5 |          3 |     0.62 | False |
| streamlink         | fix-unsafe               |     6.0 |        13.8 |  2.3 |     0.5 |          3 |     0.65 | False |
| streamlink         | infer-basedpyright       |    20.7 |        62.2 |  3.0 |     2.9 |          3 |      0.7 | False |
| streamlink         | infer-ty                 |     8.8 |        24.0 |  2.7 |    1.57 |          3 |     0.64 | False |
| streamlink         | infer-pyrefly            |     8.2 |        26.4 |  3.2 |    2.06 |          3 |     0.64 | False |
| streamlink         | census                   |     1.2 |         1.0 |  0.8 |    0.05 |          3 |      0.4 | False |
| streamlink         | coverage                 |     1.8 |         2.6 |  1.4 |    0.22 |          2 |     0.27 | False |
| streamlink         | timing                   |     3.0 |         4.4 |  1.5 |    0.32 |         16 |      0.4 | False |
| streamlink         | traced                   |    24.5 |        28.7 |  1.2 |    0.48 |          1 |     0.65 | False |
| streamlink         | tests-released           |    12.7 |        10.7 |  0.8 |     0.2 |          1 |     0.22 | False |
| streamlink         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.25 | False |
| streamlink         | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.25 | False |
| streamlink         | infer-union              |    18.4 |        76.8 |  4.2 |    5.31 |          5 |      6.7 | False |
| streamlink         | tests-infer-union        |    14.8 |        12.7 |  0.9 |    0.22 |          1 |     0.25 | False |
| streamlink         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| streamlink         | types-released           |     9.4 |         6.9 |  0.7 |    0.39 |          1 |      0.5 | False |
| streamlink         | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.44 | False |
| streamlink         | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.44 | False |
| streamlink         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.45 | False |
| streamlink         | types-infer-basedpyright |     8.8 |         6.8 |  0.8 |    0.38 |          1 |     0.45 | False |
| streamlink         | types-infer-ty           |     7.8 |         6.8 |  0.9 |    0.37 |          1 |     0.45 | False |
| streamlink         | types-infer-pyrefly      |     7.4 |         6.2 |  0.8 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-trace        |     9.4 |         7.1 |  0.8 |    0.36 |          1 |     0.46 | False |
| streamlink         | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     3.6 |         8.4 |  2.3 |     0.5 |          3 |     0.57 | False |
| sphinx             | fix-certain              |    10.4 |        24.7 |  2.4 |    0.63 |          4 |      0.8 | False |
| sphinx             | fix-likely               |    12.0 |        32.2 |  2.7 |    0.93 |          4 |     1.07 | False |
| sphinx             | fix-unsafe               |    11.6 |        30.0 |  2.6 |     0.9 |          3 |     1.22 | False |
| sphinx             | infer-basedpyright       |    19.1 |        78.8 |  4.1 |    3.85 |          4 |      1.1 | False |
| sphinx             | infer-ty                 |    12.8 |        40.7 |  3.2 |    2.31 |          4 |     1.06 | False |
| sphinx             | infer-pyrefly            |    12.6 |        38.4 |  3.0 |    2.54 |          4 |     1.06 | False |
| sphinx             | census                   |     2.4 |         2.1 |  0.9 |    0.07 |          3 |     0.57 | False |
| sphinx             | coverage                 |     3.0 |         4.2 |  1.4 |    0.28 |          1 |     0.35 | False |
| sphinx             | timing                   |     5.8 |         8.9 |  1.5 |     0.5 |         16 |     0.57 | False |
| sphinx             | traced                   |    31.5 |       171.6 |  5.4 |    1.68 |          7 |     2.12 | False |
| sphinx             | tests-released           |    15.0 |       107.7 |  7.2 |    1.39 |          8 |     1.69 | False |
| sphinx             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.04 |          8 |     1.65 | False |
| sphinx             | tests-fix-likely         |    12.8 |        92.7 |  7.2 |    1.33 |          8 |     1.65 | False |
| sphinx             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.04 |          8 |     1.65 | False |
| sphinx             | tests-infer-basedpyright |    12.8 |        92.4 |  7.2 |    1.33 |          8 |     1.66 | False |
| sphinx             | tests-infer-ty           |    12.4 |        87.9 |  7.1 |    1.33 |          8 |     1.65 | False |
| sphinx             | tests-infer-pyrefly      |    12.4 |        90.1 |  7.3 |    1.32 |          8 |     1.66 | False |
| sphinx             | tests-infer-trace        |    12.6 |        92.8 |  7.4 |    1.32 |          8 |     1.75 | False |
| sphinx             | infer-union              |    33.3 |       124.5 |  3.7 |    5.99 |          3 |     1.09 | False |
| sphinx             | tests-infer-union        |    17.2 |       116.2 |  6.8 |    1.32 |          6 |     1.82 | False |
| sphinx             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.66 | False |
| sphinx             | types-released           |     9.0 |         6.9 |  0.8 |    0.26 |          1 |      0.4 | False |
| sphinx             | types-fix-certain        |     8.4 |         6.7 |  0.8 |    0.27 |          1 |     0.32 | False |
| sphinx             | types-fix-likely         |     7.6 |         6.6 |  0.9 |    0.33 |          1 |     0.32 | False |
| sphinx             | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.34 | False |
| sphinx             | types-infer-basedpyright |     6.4 |         5.9 |  0.9 |    0.31 |          1 |     0.32 | False |
| sphinx             | types-infer-ty           |     7.2 |         5.9 |  0.8 |    0.26 |          1 |     0.31 | False |
| sphinx             | types-infer-pyrefly      |     9.6 |         6.7 |  0.7 |    0.26 |          1 |     0.31 | False |
| sphinx             | types-infer-trace        |     9.8 |         7.0 |  0.7 |    0.32 |          1 |     0.35 | False |
| sphinx             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      0.3 | False |
| tox                | fix-certain              |     2.4 |         5.9 |  2.5 |    0.31 |          3 |     0.46 | False |
| tox                | fix-likely               |     3.0 |         7.7 |  2.6 |    0.39 |          3 |     0.49 | False |
| tox                | fix-unsafe               |     5.4 |         8.7 |  1.6 |    0.41 |          2 |     0.51 | False |
| tox                | infer-basedpyright       |    15.0 |        41.1 |  2.7 |    2.22 |          3 |     0.49 | False |
| tox                | infer-ty                 |     5.4 |        16.0 |  3.0 |    1.29 |          3 |     0.44 | False |
| tox                | infer-pyrefly            |     5.2 |        11.6 |  2.2 |     1.0 |          3 |     0.49 | False |
| tox                | census                   |     2.8 |         3.3 |  1.2 |    0.24 |          2 |      0.3 | False |
| tox                | coverage                 |     1.2 |         1.5 |  1.2 |    0.17 |          2 |     0.21 | False |
| tox                | timing                   |     1.8 |         2.3 |  1.3 |    0.25 |         16 |      0.3 | False |
| tox                | traced                   |    33.9 |       158.5 |  4.7 |    1.52 |          5 |     1.84 | False |
| tox                | tests-released           |    18.4 |        99.2 |  5.4 |    1.35 |          7 |      1.7 | False |
| tox                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.64 | False |
| tox                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.71 | False |
| tox                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.76 | False |
| tox                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.65 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.65 | False |
| tox                | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     1.62 | False |
| tox                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.71 | False |
| tox                | infer-union              |    13.4 |        40.6 |  3.0 |    3.59 |          3 |      0.5 | False |
| tox                | tests-infer-union        |    24.3 |       122.3 |  5.0 |    1.49 |          7 |     1.72 | False |
| tox                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |

The fixes whose bindings typed after aren't those typed before and those fixed, where they differ (a
fix that didn't make its binding typed):

| corpus | fix                | typed before | fixed | typed after | short |
| ------ | ------------------ | -----------: | ----: | ----------: | ----: |
| sphinx | certain            |          929 | 3,230 |       4,158 |     1 |
| sphinx | likely             |          929 | 3,751 |       4,679 |     1 |
| sphinx | unsafe             |          929 | 4,130 |       5,058 |     1 |
| sphinx | infer-basedpyright |          929 | 4,936 |       5,864 |     1 |
| sphinx | infer-ty           |          929 | 4,993 |       5,921 |     1 |
| sphinx | infer-pyrefly      |          929 | 5,205 |       6,133 |     1 |
| sphinx | infer-trace        |          929 | 4,130 |       5,058 |     1 |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus             | released                                                             | traced                                                               | same failures |
| ------------------ | -------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------- |
| django             | 5 expected failures, 1 failures, 17,585 ran, 1,149 skipped           | 5 expected failures, 5 failures, 17,585 ran, 1,149 skipped           | False         |
| sqlalchemy         | 29,521 passed, 975 skipped                                           | 29,525 passed, 971 skipped                                           | True          |
| pydantic           | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                     | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                     | True          |
| pandas             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed              | True          |
| structlog          | 24 failed, 860 passed, 37 skipped                                    | 24 failed, 860 passed, 37 skipped                                    | True          |
| attrs              | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                         | True          |
| click              | 1,991 passed, 24 skipped, 1 xfailed                                  | 1,991 passed, 24 skipped, 1 xfailed                                  | True          |
| hypercorn          | 2 failed, 194 passed                                                 | 2 failed, 194 passed                                                 | True          |
| starlette          | 1,271 passed, 2 skipped, 2 xfailed                                   | 1,271 passed, 2 skipped, 2 xfailed                                   | True          |
| werkzeug           | 1 failed, 979 passed, 1 skipped                                      | 1 failed, 979 passed, 1 skipped                                      | True          |
| mkdocs             | 2 errors, 2 failures, 724 ran, 4 skipped                             | 2 errors, 2 failures, 724 ran, 4 skipped                             | True          |
| httpx              | 1 failed, 1,416 passed, 1 skipped                                    | 1 failed, 1,416 passed, 1 skipped                                    | True          |
| black              | 519 passed, 1 skipped                                                | 519 passed, 1 skipped                                                | True          |
| fastapi            | 3,551 passed, 17 skipped, 4 xfailed                                  | 3,551 passed, 17 skipped, 4 xfailed                                  | True          |
| cattrs             | 994 passed, 15 xfailed                                               | 994 passed, 15 xfailed                                               | True          |
| pytest             | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed | True          |
| botocore           | 7 failed, 4,593 passed, 96 skipped                                   | 7 failed, 4,593 passed, 96 skipped                                   | True          |
| uvicorn            | 1,350 passed, 12 skipped                                             | 1,350 passed, 12 skipped                                             | True          |
| mcp                | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                         | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                         | False         |
| pdm                | 1,472 passed, 1 skipped                                              | 1,472 passed, 1 skipped                                              | True          |
| strawberry-graphql | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed          | False         |
| pygments           | 1 failed, 5,330 passed, 15 skipped                                   | 1 failed, 5,330 passed, 15 skipped                                   | True          |
| streamlink         | 9 error, 15 failed, 7,233 passed, 36 skipped                         | 9 error, 15 failed, 7,233 passed, 36 skipped                         | True          |
| sphinx             | 10 failed, 2,392 passed, 22 skipped                                  | 10 failed, 2,392 passed, 22 skipped                                  | True          |
| tox                | 6 error, 17 failed, 8,525 passed, 31 skipped                         | 6 error, 17 failed, 8,525 passed, 31 skipped                         | True          |

- standard library, 0.4.3-rc.2+dev, fix-likely: held 8.14 GB beside other steps
- standard library, 0.4.3-rc.2+dev, infer-basedpyright: held 13.49 GB beside other steps
- standard library, 0.4.3-rc.2+dev, infer-ty: held 15.54 GB beside other steps
- standard library, 0.4.3-rc.2+dev, infer-pyrefly: held 17.44 GB beside other steps
- django, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- django, 0.4.3-rc.2+dev, infer-union: held 11.14 GB beside other steps
- django, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store,
  so its seconds measure less of the checker
- django, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, 0.4.3-rc.2+dev, infer-union: held 11.07 GB beside other steps
- sqlalchemy, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the
  store, so its seconds measure less of the checker
- sqlalchemy, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, 0.4.3-rc.2+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- pydantic, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- pydantic, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pandas, 0.4.3-rc.2+dev, infer-basedpyright: held 15.68 GB beside other steps
- pandas, 0.4.3-rc.2+dev, infer-ty: held 12.44 GB beside other steps
- pandas, 0.4.3-rc.2+dev, infer-pyrefly: held 17.92 GB beside other steps
- pandas, 0.4.3-rc.2+dev, traced: held 10.59 GB beside other steps
- pandas, 0.4.3-rc.2+dev, tests-released: held 11.5 GB beside other steps
- pandas, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store,
  so its seconds measure less of the checker
- pandas, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 2 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, 0.4.3-rc.2+dev, tests-infer-union: held 9.9 GB beside other steps
- twisted, 0.4.3-rc.2+dev, infer-basedpyright: held 8.91 GB beside other steps
- structlog, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from
  the store, so its seconds measure less of the checker
- structlog, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- structlog, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- attrs, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so
  its seconds measure less of the checker
- attrs, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, 0.4.3-rc.2+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- click, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- click, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its seconds
  measure less of the checker
- click, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- hypercorn, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- hypercorn, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- starlette, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from
  the store, so its seconds measure less of the checker
- starlette, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- starlette, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- werkzeug, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- werkzeug, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mkdocs, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 2 of 4 rounds came from the
  store, so its seconds measure less of the checker
- mkdocs, 0.4.3-rc.2+dev, infer-ty: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- mkdocs, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- httpx, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- httpx, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- httpx, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- black, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- fastapi, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- fastapi, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store,
  so its seconds measure less of the checker
- cattrs, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, 0.4.3-rc.2+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store,
  so its seconds measure less of the checker
- pytest, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- botocore, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store,
  so its seconds measure less of the checker
- botocore, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- botocore, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- uvicorn, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mcp, 0.4.3-rc.2+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- mcp, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- textual, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 5 rounds came from the
  store, so its seconds measure less of the checker
- pdm, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 3 of 5 rounds came from the
  store, so its seconds measure less of the checker
- pdm, 0.4.3-rc.2+dev, infer-ty: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- pdm, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- strawberry-graphql, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from
  the store, so its seconds measure less of the checker
- strawberry-graphql, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- pygments, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 4 rounds came from the
  store, so its seconds measure less of the checker
- pygments, 0.4.3-rc.2+dev, infer-ty: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pygments, 0.4.3-rc.2+dev, infer-pyrefly: pyrefly's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- streamlink, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 4 rounds came from the
  store, so its seconds measure less of the checker
- streamlink, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so
  its seconds measure less of the checker
- streamlink, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, 0.4.3-rc.2+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- sphinx, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, 0.4.3-rc.2+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- tox, 0.4.3-rc.2+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, 0.4.3-rc.2+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker

## Mega corpora

The run `0.4.3-rc.1` (`python -m tests.corpus`) on mega: constricter 0.4.3.dev36+gaadbff007
(`aadbff00772a`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own,
started once the CPUs it's expected to keep busy and the memory it's expected to hold are free. The
run took 96 minutes. Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter    |  Files |        `LVA001` |      `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |     `LVA006` |  `LVA009` | `LVA010` | `LVA011` |   Total |
| ------------------ | -------- | -------------- | -----: | --------------: | ------------: | -------: | -------------: | -----------: | -----------: | --------: | -------: | -------: | ------: |
| standard library   | 3.14.7   | 0.4.3-rc.1+dev |  1,867 |          88,565 |        12,334 |        0 |         12,772 |           57 |           14 |         8 |        0 |        0 | 113,750 |
| django             | 5.2.18   | 0.4.3-rc.1+dev |    883 |           9,926 |         2,166 |        0 |          5,084 |            0 |            0 |         1 |        0 |        0 |  17,177 |
| sqlalchemy         | 2.1.4    | 0.4.3-rc.1+dev |    258 |           8,825 |         1,636 |        0 |          2,501 |          572 |          128 |         2 |        0 |        1 |  13,665 |
| pydantic           | 2.14.0   | 0.4.3-rc.1+dev |    105 |           2,072 |           440 |        0 |            605 |          184 |           15 |         0 |        0 |        0 |   3,316 |
| pandas             | 3.0.6    | 0.4.3-rc.1+dev |  1,420 |          73,367 |         2,778 |        0 |          1,648 |          134 |            2 |         1 |        0 |        1 |  77,931 |
| twisted            | 12.3.0   | 0.4.3-rc.1+dev |    819 |          13,310 |         1,349 |        0 |          3,215 |            0 |            0 |         0 |        0 |        0 |  17,874 |
| pip                | 20.3.4   | 0.4.3-rc.1+dev |    366 |           5,902 |         1,150 |        0 |          1,872 |            0 |            0 |         0 |        0 |        0 |   8,924 |
| structlog          | 26.1.0   | 0.4.3-rc.1+dev |     21 |             156 |            47 |        0 |            113 |           12 |            1 |         0 |        0 |        0 |     329 |
| attrs              | 26.1.0   | 0.4.3-rc.1+dev |     13 |             285 |            50 |        0 |             58 |            2 |            0 |         1 |        0 |        0 |     396 |
| click              | 8.5.0    | 0.4.3-rc.1+dev |     17 |             481 |            58 |        0 |             69 |           28 |            1 |         0 |        0 |        0 |     637 |
| hypercorn          | 0.18.0   | 0.4.3-rc.1+dev |     39 |             220 |            67 |        0 |             68 |            8 |            0 |         0 |        0 |        0 |     363 |
| starlette          | 1.7.0    | 0.4.3-rc.1+dev |     36 |             499 |            99 |        0 |            146 |           18 |            0 |         0 |        0 |        0 |     762 |
| werkzeug           | 3.1.9    | 0.4.3-rc.1+dev |     52 |             835 |           235 |        0 |            223 |           15 |            1 |         0 |        0 |        0 |   1,309 |
| mkdocs             | 1.6.1    | 0.4.3-rc.1+dev |     61 |           1,674 |           198 |        0 |            460 |            8 |            0 |         0 |        0 |        0 |   2,340 |
| httpx              | 0.28.1   | 0.4.3-rc.1+dev |     23 |             395 |           112 |        0 |             62 |            1 |            0 |         0 |        0 |        0 |     570 |
| black              | 26.10.0  | 0.4.3-rc.1+dev |     25 |             996 |           232 |        0 |             45 |            5 |            4 |         0 |        0 |        0 |   1,282 |
| fastapi            | 0.142.2  | 0.4.3-rc.1+dev |     52 |             586 |           105 |        0 |             51 |           98 |            5 |         0 |        0 |        0 |     845 |
| cattrs             | 26.2.1   | 0.4.3-rc.1+dev |     36 |             420 |            70 |        0 |             30 |            9 |            1 |         0 |        0 |        0 |     530 |
| pytest             | 9.1.1    | 0.4.3-rc.1+dev |     78 |           2,363 |           470 |        0 |            170 |           33 |            9 |         0 |        0 |        0 |   3,045 |
| botocore           | 1.43.108 | 0.4.3-rc.1+dev |     76 |           2,825 |           367 |        0 |            594 |            2 |            0 |         0 |        0 |        0 |   3,788 |
| uvicorn            | 0.54.0   | 0.4.3-rc.1+dev |     45 |             363 |            71 |        0 |             55 |           11 |            4 |         0 |        0 |        0 |     504 |
| mcp                | 2.3.0    | 0.4.3-rc.1+dev |    124 |           1,356 |           173 |        0 |            191 |          105 |            8 |         0 |        0 |        0 |   1,833 |
| textual            | 8.2.8    | 0.4.3-rc.1+dev |    247 |           4,979 |           718 |        0 |            786 |           31 |           26 |         0 |        0 |        0 |   6,540 |
| pdm                | 2.29.2   | 0.4.3-rc.1+dev |    128 |           2,114 |           417 |        0 |            187 |           37 |            2 |         0 |        0 |        0 |   2,757 |
| strawberry-graphql | 0.332.0  | 0.4.3-rc.1+dev |    244 |           1,436 |           243 |        0 |            127 |          137 |            2 |         0 |        0 |        0 |   1,945 |
| pygments           | 2.21.0   | 0.4.3-rc.1+dev |    343 |           1,124 |           539 |        0 |          6,003 |            0 |            0 |         0 |        0 |        0 |   7,666 |
| streamlink         | 8.6.1    | 0.4.3-rc.1+dev |    227 |           2,080 |           310 |        0 |            639 |           37 |           11 |         0 |        0 |        0 |   3,077 |
| sphinx             | 9.1.0    | 0.4.3-rc.1+dev |    243 |           5,505 |         1,336 |        1 |          1,131 |           73 |           29 |         5 |        0 |        3 |   8,083 |
| tox                | 4.64.9   | 0.4.3-rc.1+dev |    129 |           1,369 |           286 |        0 |            107 |           18 |            5 |         0 |        0 |        0 |   1,785 |
| pint               | 0.26.1   | 0.4.3-rc.1+dev |    109 |           2,591 |           297 |        0 |            190 |           14 |            2 |         0 |        0 |        0 |   3,094 |
| altair             | 6.3.0    | 0.4.3-rc.1+dev |     55 |             814 |           130 |        0 |            756 |           60 |            8 |         0 |        0 |        0 |   1,768 |
| seaborn            | 0.13.2   | 0.4.3-rc.1+dev |     54 |           2,361 |           370 |        0 |            164 |           23 |            3 |         0 |        0 |        0 |   2,921 |
| aiohttp            | 3.14.4   | 0.4.3-rc.1+dev |     54 |           1,307 |           195 |        0 |            355 |           13 |            5 |         1 |        0 |        0 |   1,876 |
| websockets         | 17.2     | 0.4.3-rc.1+dev |     52 |             605 |            85 |        0 |            101 |            0 |            0 |         0 |        0 |        0 |     791 |
| anyio              | 4.15.1   | 0.4.3-rc.1+dev |     46 |             615 |            77 |        0 |             23 |           26 |            6 |         0 |        0 |        0 |     747 |
| zarr               | 3.4.0    | 0.4.3-rc.1+dev |     98 |           1,874 |           370 |        0 |            167 |           26 |           35 |         0 |        0 |        0 |   2,472 |
| joblib             | 1.6.0    | 0.4.3-rc.1+dev |     73 |           1,842 |           158 |        0 |            239 |            1 |            0 |         0 |        0 |        0 |   2,240 |
| networkx           | 3.7      | 0.4.3-rc.1+dev |    583 |          18,854 |         3,221 |        0 |            381 |            8 |            0 |         0 |        0 |        0 |  22,464 |
| nibabel            | 5.4.2    | 0.4.3-rc.1+dev |    229 |           6,504 |         1,032 |        0 |            932 |            5 |            1 |         0 |        0 |        0 |   8,474 |
| narwhals           | 2.26.0   | 0.4.3-rc.1+dev |    162 |           2,775 |           106 |        0 |            239 |           62 |            5 |         0 |        0 |        0 |   3,187 |
| xarray             | 2026.9.0 | 0.4.3-rc.1+dev |    199 |          18,968 |         1,599 |        0 |            777 |          255 |           20 |         0 |        0 |        0 |  21,619 |
| litestar           | 2.24.0   | 0.4.3-rc.1+dev |    374 |           1,474 |           306 |        0 |            125 |          166 |           12 |         4 |        0 |        0 |   2,087 |
| stripe             | 16.0.0   | 0.4.3-rc.1+dev |  1,460 |           1,772 |            49 |        0 |          1,536 |           16 |          854 |         0 |        0 |        0 |   4,227 |
| celery             | 5.6.3    | 0.4.3-rc.1+dev |    161 |           2,202 |           331 |        0 |          1,215 |            0 |            0 |         2 |        0 |        0 |   3,750 |
| optuna             | 5.0.0    | 0.4.3-rc.1+dev |    220 |           2,740 |           446 |        0 |            412 |           28 |            4 |         0 |        0 |        0 |   3,630 |
| dask               | 2026.8.0 | 0.4.3-rc.1+dev |    361 |          20,748 |         1,691 |        0 |          1,733 |           76 |            5 |         2 |        0 |        1 |  24,256 |
| mypy               | 2.4.0    | 0.4.3-rc.1+dev |    195 |           9,008 |         2,197 |        0 |            196 |          340 |           45 |         0 |        1 |        1 |  11,788 |
| **Total**          |          | 0.4.3-rc.1+dev | 12,462 | 331,082 (78.0%) | 40,716 (9.6%) | 1 (0.0%) | 48,553 (11.4%) | 2,754 (0.6%) | 1,273 (0.3%) | 27 (0.0%) | 1 (0.0%) | 7 (0.0%) | 424,414 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter    |   `relaxed` |         `strict` |     `constrict` | `suffocate` |           Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | -------------- | ----------: | ---------------: | --------------: | ----------: | --------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library   | 0.4.3-rc.1+dev | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 |  37,445 (32.9%) |   6,681 (5.9%) | 13,082 (11.5%) |      0 |    0 |            0 |
| django             | 0.4.3-rc.1+dev |  0 / 17,177 |   15,010 / 2,167 |      17,177 / 0 |  17,177 / 0 |   2,622 (15.3%) |     646 (3.8%) |  2,786 (16.2%) |      0 |    0 |            0 |
| sqlalchemy         | 0.4.3-rc.1+dev |  0 / 12,964 |   11,326 / 2,339 |    12,964 / 701 |  13,665 / 0 |   1,938 (14.2%) |     350 (2.6%) |     847 (6.2%) |      0 |    0 |            0 |
| pydantic           | 0.4.3-rc.1+dev |   0 / 3,117 |      2,677 / 639 |     3,117 / 199 |   3,316 / 0 |   1,191 (35.9%) |     145 (4.4%) |    404 (12.2%) |      0 |    0 |            0 |
| pandas             | 0.4.3-rc.1+dev |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 |  16,952 (21.8%) | 23,585 (30.3%) | 24,357 (31.3%) |      0 |    0 |            0 |
| twisted            | 0.4.3-rc.1+dev |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |   2,435 (13.6%) |  3,625 (20.3%) |  4,697 (26.3%) |      0 |    0 |            0 |
| pip                | 0.4.3-rc.1+dev |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |   2,270 (25.4%) |     468 (5.2%) |  1,304 (14.6%) |      0 |    0 |            0 |
| structlog          | 0.4.3-rc.1+dev |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |      98 (29.8%) |      15 (4.6%) |      28 (8.5%) |      0 |    0 |            0 |
| attrs              | 0.4.3-rc.1+dev |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |      93 (23.5%) |       9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| click              | 0.4.3-rc.1+dev |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |     302 (47.4%) |      27 (4.2%) |      63 (9.9%) |      0 |    0 |            0 |
| hypercorn          | 0.4.3-rc.1+dev |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |     134 (36.9%) |      20 (5.5%) |     58 (16.0%) |      0 |    0 |            0 |
| starlette          | 0.4.3-rc.1+dev |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |     314 (41.2%) |      57 (7.5%) |     97 (12.7%) |      0 |    0 |            0 |
| werkzeug           | 0.4.3-rc.1+dev |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |     527 (40.3%) |      66 (5.0%) |     127 (9.7%) |      0 |    0 |            0 |
| mkdocs             | 0.4.3-rc.1+dev |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |     810 (34.6%) |    377 (16.1%) |    482 (20.6%) |      0 |    0 |            0 |
| httpx              | 0.4.3-rc.1+dev |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |     234 (41.1%) |     57 (10.0%) |     73 (12.8%) |      0 |    0 |            0 |
| black              | 0.4.3-rc.1+dev |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |     707 (55.1%) |     127 (9.9%) |    163 (12.7%) |      0 |    0 |            0 |
| fastapi            | 0.4.3-rc.1+dev |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |     257 (30.4%) |      40 (4.7%) |      65 (7.7%) |      0 |    0 |            0 |
| cattrs             | 0.4.3-rc.1+dev |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |     105 (19.8%) |      34 (6.4%) |      46 (8.7%) |      0 |    0 |            0 |
| pytest             | 0.4.3-rc.1+dev |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |   1,358 (44.6%) |     156 (5.1%) |     285 (9.4%) |      0 |    0 |            0 |
| botocore           | 0.4.3-rc.1+dev |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |     543 (14.3%) |     174 (4.6%) |    608 (16.1%) |      0 |    0 |            0 |
| uvicorn            | 0.4.3-rc.1+dev |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |     231 (45.8%) |      29 (5.8%) |      44 (8.7%) |      0 |    0 |            0 |
| mcp                | 0.4.3-rc.1+dev |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |     694 (37.9%) |     154 (8.4%) |    236 (12.9%) |      0 |    0 |            0 |
| textual            | 0.4.3-rc.1+dev |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |   2,707 (41.4%) |     482 (7.4%) |    741 (11.3%) |      0 |    0 |            0 |
| pdm                | 0.4.3-rc.1+dev |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |   1,147 (41.6%) |     200 (7.3%) |    321 (11.6%) |      0 |    0 |            0 |
| strawberry-graphql | 0.4.3-rc.1+dev |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |     611 (31.4%) |     167 (8.6%) |    218 (11.2%) |      0 |    0 |            0 |
| pygments           | 0.4.3-rc.1+dev |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |      735 (9.6%) |      79 (1.0%) |     228 (3.0%) |      0 |    0 |            0 |
| streamlink         | 0.4.3-rc.1+dev |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |     682 (22.2%) |     111 (3.6%) |     250 (8.1%) |      0 |    0 |            0 |
| sphinx             | 0.4.3-rc.1+dev |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |   3,128 (38.7%) |     448 (5.5%) |    821 (10.2%) |      0 |    0 |            0 |
| tox                | 0.4.3-rc.1+dev |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |     943 (52.8%) |      82 (4.6%) |     138 (7.7%) |      0 |    0 |            0 |
| pint               | 0.4.3-rc.1+dev |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |     617 (19.9%) |     104 (3.4%) |     154 (5.0%) |      0 |    0 |            0 |
| altair             | 0.4.3-rc.1+dev |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |     378 (21.4%) |      47 (2.7%) |      60 (3.4%) |      0 |    0 |            0 |
| seaborn            | 0.4.3-rc.1+dev |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |     639 (21.9%) |     137 (4.7%) |     228 (7.8%) |      0 |    0 |            0 |
| aiohttp            | 0.4.3-rc.1+dev |   0 / 1,858 |      1,662 / 214 |      1,858 / 18 |   1,876 / 0 |     701 (37.4%) |     141 (7.5%) |    252 (13.4%) |      0 |    0 |            0 |
| websockets         | 0.4.3-rc.1+dev |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |     328 (41.5%) |      61 (7.7%) |    111 (14.0%) |      0 |    0 |            0 |
| anyio              | 0.4.3-rc.1+dev |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |     212 (28.4%) |      33 (4.4%) |      61 (8.2%) |      0 |    0 |            0 |
| zarr               | 0.4.3-rc.1+dev |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |   1,084 (43.9%) |      72 (2.9%) |     109 (4.4%) |      0 |    0 |            0 |
| joblib             | 0.4.3-rc.1+dev |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |     525 (23.4%) |     182 (8.1%) |    267 (11.9%) |      0 |    0 |            0 |
| networkx           | 0.4.3-rc.1+dev |  0 / 22,456 |   19,235 / 3,229 |      22,456 / 8 |  22,464 / 0 |   3,969 (17.7%) |   2,186 (9.7%) |  2,389 (10.6%) |      0 |    0 |            0 |
| nibabel            | 0.4.3-rc.1+dev |   0 / 8,468 |    7,436 / 1,038 |       8,468 / 6 |   8,474 / 0 |   1,849 (21.8%) |     691 (8.2%) |    957 (11.3%) |      0 |    0 |            0 |
| narwhals           | 0.4.3-rc.1+dev |   0 / 3,120 |      3,014 / 173 |      3,120 / 67 |   3,187 / 0 |     982 (30.8%) |      67 (2.1%) |     119 (3.7%) |      0 |    0 |            0 |
| xarray             | 0.4.3-rc.1+dev |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |   3,557 (16.5%) |  3,127 (14.5%) |  3,338 (15.4%) |      0 |    0 |            0 |
| litestar           | 0.4.3-rc.1+dev |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |     607 (29.1%) |     101 (4.8%) |     161 (7.7%) |      0 |    0 |            0 |
| stripe             | 0.4.3-rc.1+dev |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |     569 (13.5%) |     161 (3.8%) |    664 (15.7%) |      0 |    0 |            0 |
| celery             | 0.4.3-rc.1+dev |   0 / 3,750 |      3,417 / 333 |       3,750 / 0 |   3,750 / 0 |     508 (13.5%) |     119 (3.2%) |     360 (9.6%) |      0 |    0 |            0 |
| optuna             | 0.4.3-rc.1+dev |   0 / 3,598 |      3,152 / 478 |      3,598 / 32 |   3,630 / 0 |   1,476 (40.7%) |     199 (5.5%) |     296 (8.2%) |      0 |    0 |            0 |
| dask               | 0.4.3-rc.1+dev |  0 / 24,174 |   22,481 / 1,775 |     24,174 / 82 |  24,256 / 0 |   3,120 (12.9%) |   1,926 (7.9%) |  2,736 (11.3%) |      0 |    0 |            0 |
| mypy               | 0.4.3-rc.1+dev |  0 / 11,401 |    9,204 / 2,583 |    11,401 / 387 |  11,788 / 0 |   4,763 (40.4%) |  1,181 (10.0%) |  1,553 (13.2%) |      0 |    0 |            0 |
| **Total**          | 0.4.3-rc.1+dev | 0 / 420,379 | 379,635 / 44,778 | 420,378 / 4,036 | 424,414 / 0 | 107,097 (25.2%) | 48,946 (11.5%) | 66,395 (15.6%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter    | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | -------------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library   | 0.4.3-rc.1+dev |              1.2% |         33.7% |            39.5% |                  45.1% | +32.6 pts, 32.9% of untyped | +43.9 pts, 44.4% of untyped |
| django             | 0.4.3-rc.1+dev |              0.0% |         15.3% |            19.1% |                  31.5% | +15.3 pts, 15.3% of untyped | +31.5 pts, 31.5% of untyped |
| sqlalchemy         | 0.4.3-rc.1+dev |             15.3% |         27.9% |            30.2% |                  33.5% | +12.7 pts, 14.9% of untyped | +18.2 pts, 21.5% of untyped |
| pydantic           | 0.4.3-rc.1+dev |             22.4% |         52.1% |            55.7% |                  62.1% | +29.6 pts, 38.2% of untyped | +39.7 pts, 51.2% of untyped |
| pandas             | 0.4.3-rc.1+dev |              1.6% |         23.0% |            52.9% |                  53.9% | +21.4 pts, 21.8% of untyped | +52.2 pts, 53.1% of untyped |
| twisted            | 0.4.3-rc.1+dev |              0.0% |         13.6% |            33.9% |                  39.9% | +13.6 pts, 13.6% of untyped | +39.9 pts, 39.9% of untyped |
| pip                | 0.4.3-rc.1+dev |              1.5% |         26.6% |            31.7% |                  40.9% | +25.0 pts, 25.4% of untyped | +39.4 pts, 40.0% of untyped |
| structlog          | 0.4.3-rc.1+dev |             25.6% |         48.7% |            52.2% |                  55.3% | +23.1 pts, 31.0% of untyped | +29.6 pts, 39.9% of untyped |
| attrs              | 0.4.3-rc.1+dev |              0.8% |         24.2% |            26.5% |                  27.0% | +23.5 pts, 23.7% of untyped | +26.3 pts, 26.5% of untyped |
| click              | 0.4.3-rc.1+dev |             31.5% |         65.5% |            68.5% |                  72.6% | +34.0 pts, 49.7% of untyped | +41.1 pts, 60.0% of untyped |
| hypercorn          | 0.4.3-rc.1+dev |             32.4% |         57.9% |            61.7% |                  69.0% | +25.5 pts, 37.7% of untyped | +36.6 pts, 54.1% of untyped |
| starlette          | 0.4.3-rc.1+dev |             10.3% |         48.1% |            55.0% |                  59.8% | +37.9 pts, 42.2% of untyped | +49.6 pts, 55.2% of untyped |
| werkzeug           | 0.4.3-rc.1+dev |             14.3% |         49.2% |            53.6% |                  57.7% | +34.9 pts, 40.8% of untyped | +43.3 pts, 50.6% of untyped |
| mkdocs             | 0.4.3-rc.1+dev |              4.5% |         37.7% |            53.1% |                  57.4% | +33.2 pts, 34.7% of untyped | +52.9 pts, 55.4% of untyped |
| httpx              | 0.4.3-rc.1+dev |              6.3% |         44.8% |            54.2% |                  56.8% | +38.6 pts, 41.1% of untyped | +50.6 pts, 54.0% of untyped |
| black              | 0.4.3-rc.1+dev |             15.9% |         62.6% |            71.0% |                  73.4% | +46.7 pts, 55.5% of untyped | +57.5 pts, 68.3% of untyped |
| fastapi            | 0.4.3-rc.1+dev |             42.0% |         62.1% |            65.2% |                  67.2% | +20.1 pts, 34.6% of untyped | +25.2 pts, 43.4% of untyped |
| cattrs             | 0.4.3-rc.1+dev |              7.0% |         25.8% |            31.8% |                  34.0% | +18.8 pts, 20.2% of untyped | +27.0 pts, 29.0% of untyped |
| pytest             | 0.4.3-rc.1+dev |             12.1% |         51.9% |            56.4% |                  60.2% | +39.7 pts, 45.2% of untyped | +48.1 pts, 54.7% of untyped |
| botocore           | 0.4.3-rc.1+dev |              0.5% |         14.7% |            19.3% |                  30.7% | +14.3 pts, 14.3% of untyped | +30.2 pts, 30.4% of untyped |
| uvicorn            | 0.4.3-rc.1+dev |             23.6% |         59.7% |            64.2% |                  66.6% | +36.1 pts, 47.2% of untyped | +43.0 pts, 56.2% of untyped |
| mcp                | 0.4.3-rc.1+dev |             30.7% |         58.7% |            64.9% |                  68.2% | +28.0 pts, 40.3% of untyped | +37.5 pts, 54.1% of untyped |
| textual            | 0.4.3-rc.1+dev |             15.6% |         50.8% |            57.1% |                  60.5% | +35.3 pts, 41.8% of untyped | +44.9 pts, 53.2% of untyped |
| pdm                | 0.4.3-rc.1+dev |             11.7% |         49.0% |            55.5% |                  59.4% | +37.3 pts, 42.2% of untyped | +47.7 pts, 54.0% of untyped |
| strawberry-graphql | 0.4.3-rc.1+dev |             30.1% |         53.7% |            60.2% |                  62.2% | +23.7 pts, 33.8% of untyped | +32.1 pts, 45.9% of untyped |
| pygments           | 0.4.3-rc.1+dev |              0.0% |          9.6% |            10.6% |                  12.6% |   +9.6 pts, 9.6% of untyped | +12.6 pts, 12.6% of untyped |
| streamlink         | 0.4.3-rc.1+dev |             42.8% |         55.6% |            57.7% |                  60.4% | +12.9 pts, 22.5% of untyped | +17.6 pts, 30.8% of untyped |
| sphinx             | 0.4.3-rc.1+dev |             10.4% |         45.6% |            50.6% |                  54.8% | +35.1 pts, 39.2% of untyped | +44.4 pts, 49.5% of untyped |
| tox                | 0.4.3-rc.1+dev |             16.0% |         61.0% |            64.9% |                  67.5% | +44.9 pts, 53.5% of untyped | +51.5 pts, 61.4% of untyped |
| pint               | 0.4.3-rc.1+dev |              5.1% |         24.1% |            27.3% |                  28.9% | +19.0 pts, 20.0% of untyped | +23.8 pts, 25.0% of untyped |
| altair             | 0.4.3-rc.1+dev |             49.7% |         60.9% |            62.3% |                  62.7% | +11.2 pts, 22.2% of untyped | +12.9 pts, 25.7% of untyped |
| seaborn            | 0.4.3-rc.1+dev |              6.9% |         27.5% |            31.9% |                  34.8% | +20.5 pts, 22.1% of untyped | +27.9 pts, 29.9% of untyped |
| aiohttp            | 0.4.3-rc.1+dev |             23.7% |         52.5% |            58.3% |                  62.8% | +28.8 pts, 37.7% of untyped | +39.2 pts, 51.3% of untyped |
| websockets         | 0.4.3-rc.1+dev |             13.8% |         49.6% |            56.2% |                  61.7% | +35.7 pts, 41.5% of untyped | +47.8 pts, 55.5% of untyped |
| anyio              | 0.4.3-rc.1+dev |             27.8% |         49.2% |            52.5% |                  55.4% | +21.4 pts, 29.7% of untyped | +27.6 pts, 38.2% of untyped |
| zarr               | 0.4.3-rc.1+dev |             21.7% |         56.9% |            59.2% |                  60.4% | +35.2 pts, 45.0% of untyped | +38.7 pts, 49.5% of untyped |
| joblib             | 0.4.3-rc.1+dev |              0.0% |         23.5% |            31.6% |                  35.4% | +23.4 pts, 23.4% of untyped | +35.3 pts, 35.4% of untyped |
| networkx           | 0.4.3-rc.1+dev |              0.3% |         17.9% |            27.6% |                  28.5% | +17.6 pts, 17.7% of untyped | +28.2 pts, 28.3% of untyped |
| nibabel            | 0.4.3-rc.1+dev |              1.0% |         22.6% |            30.7% |                  33.8% | +21.6 pts, 21.8% of untyped | +32.8 pts, 33.1% of untyped |
| narwhals           | 0.4.3-rc.1+dev |             21.7% |         46.3% |            48.0% |                  49.3% | +24.6 pts, 31.5% of untyped | +27.6 pts, 35.3% of untyped |
| xarray             | 0.4.3-rc.1+dev |              4.6% |         20.5% |            34.5% |                  35.4% | +15.9 pts, 16.7% of untyped | +30.8 pts, 32.3% of untyped |
| litestar           | 0.4.3-rc.1+dev |             44.9% |         62.5% |            65.4% |                  67.1% | +17.5 pts, 31.9% of untyped | +22.2 pts, 40.3% of untyped |
| stripe             | 0.4.3-rc.1+dev |             89.5% |         91.3% |            91.8% |                  93.4% |  +1.8 pts, 16.9% of untyped |  +3.8 pts, 36.7% of untyped |
| celery             | 0.4.3-rc.1+dev |              0.4% |         13.9% |            17.1% |                  23.5% | +13.5 pts, 13.6% of untyped | +23.1 pts, 23.2% of untyped |
| optuna             | 0.4.3-rc.1+dev |              7.5% |         45.4% |            50.6% |                  53.0% | +38.0 pts, 41.0% of untyped | +45.6 pts, 49.2% of untyped |
| dask               | 0.4.3-rc.1+dev |              1.1% |         13.8% |            21.7% |                  25.0% | +12.8 pts, 12.9% of untyped | +24.0 pts, 24.2% of untyped |
| mypy               | 0.4.3-rc.1+dev |             16.8% |         51.6% |            60.2% |                  62.9% | +34.8 pts, 41.8% of untyped | +46.1 pts, 55.4% of untyped |
| **Total**          | 0.4.3-rc.1+dev |             11.4% |         33.9% |            44.3% |                  47.9% | +22.6 pts, 25.5% of untyped | +36.6 pts, 41.3% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library   | certain            | 37,445 |  37,445 |        |        |      0 |    0 | 38,774 |  115,001 |    92.7 |
| standard library   | likely             | 44,126 |  37,688 |  6,438 |        |      0 |    0 | 45,455 |  115,001 |   130.9 |
| standard library   | unsafe             | 50,527 |  37,452 |  6,426 |  6,649 |      0 |    0 | 51,856 |  115,001 |    98.6 |
| standard library   | infer-basedpyright | 58,555 |  37,455 |  6,904 | 14,196 |      0 |   10 | 59,884 |  115,001 |   788.6 |
| standard library   | infer-ty           | 56,304 |  37,457 |  6,863 | 11,984 |      0 |    9 | 57,633 |  115,001 |   149.1 |
| standard library   | infer-pyrefly      | 58,653 |  37,451 |  6,941 | 14,261 |      0 |   42 | 59,982 |  115,001 |   141.3 |
| django             | certain            |  2,622 |   2,622 |        |        |      0 |    0 |  2,627 |   17,181 |    11.4 |
| django             | likely             |  3,268 |   2,628 |    640 |        |      0 |    0 |  3,273 |   17,181 |    14.2 |
| django             | unsafe             |  5,408 |   2,622 |    639 |  2,147 |      0 |    0 |  5,413 |   17,181 |    23.8 |
| django             | infer-basedpyright |  5,806 |   2,616 |    652 |  2,538 |      0 |    8 |  5,811 |   17,181 |    43.0 |
| django             | infer-ty           |  5,618 |   2,623 |    648 |  2,347 |      0 |    0 |  5,623 |   17,181 |    21.8 |
| django             | infer-pyrefly      |  6,074 |   2,611 |    658 |  2,805 |      0 |    4 |  6,079 |   17,181 |    24.6 |
| django             | infer-trace        |  5,940 |   2,622 |    669 |  2,649 |      0 |    0 |  5,945 |   17,181 |    17.6 |
| sqlalchemy         | certain            |  1,938 |   1,938 |        |        |      0 |    0 |  4,273 |   15,304 |    11.8 |
| sqlalchemy         | likely             |  2,288 |   1,946 |    342 |        |      0 |    0 |  4,623 |   15,304 |    14.2 |
| sqlalchemy         | unsafe             |  2,785 |   1,938 |    342 |    505 |      0 |    0 |  5,120 |   15,304 |    23.1 |
| sqlalchemy         | infer-basedpyright |  3,549 |   1,930 |    384 |  1,235 |      0 |    0 |  5,884 |   15,304 |    49.2 |
| sqlalchemy         | infer-ty           |  3,503 |   1,930 |    370 |  1,203 |      0 |    0 |  5,838 |   15,304 |    24.2 |
| sqlalchemy         | infer-pyrefly      |  3,253 |   1,929 |    360 |    964 |      0 |    0 |  5,588 |   15,304 |    25.3 |
| sqlalchemy         | infer-trace        |  2,927 |   1,938 |    342 |    647 |      0 |    0 |  5,262 |   15,304 |    17.0 |
| pydantic           | certain            |  1,191 |   1,191 |        |        |      0 |    0 |  2,093 |    4,019 |     1.9 |
| pydantic           | likely             |  1,336 |   1,198 |    138 |        |      0 |    0 |  2,238 |    4,019 |     3.0 |
| pydantic           | unsafe             |  1,595 |   1,191 |    137 |    267 |      0 |    0 |  2,497 |    4,019 |     9.0 |
| pydantic           | infer-basedpyright |  1,818 |   1,192 |    140 |    486 |      0 |    0 |  2,720 |    4,019 |    31.7 |
| pydantic           | infer-ty           |  1,733 |   1,191 |    136 |    406 |      0 |    0 |  2,635 |    4,019 |     5.4 |
| pydantic           | infer-pyrefly      |  1,797 |   1,191 |    137 |    469 |      0 |    0 |  2,699 |    4,019 |     8.2 |
| pydantic           | infer-trace        |  1,596 |   1,191 |    137 |    268 |      0 |    0 |  2,498 |    4,019 |     4.1 |
| pandas             | certain            | 16,952 |  16,952 |        |        |      0 |    0 | 18,221 |   79,062 |    45.0 |
| pandas             | likely             | 40,537 |  17,142 | 23,395 |        |      0 |    0 | 41,806 |   79,062 |    81.0 |
| pandas             | unsafe             | 41,309 |  16,948 | 23,173 |  1,188 |      0 |    0 | 42,578 |   79,062 |    45.1 |
| pandas             | infer-basedpyright | 47,036 |  16,938 | 23,377 |  6,721 |      0 |    3 | 48,305 |   79,062 |   669.7 |
| pandas             | infer-ty           | 46,953 |  16,946 | 23,377 |  6,630 |      0 |    3 | 48,222 |   79,062 |   172.1 |
| pandas             | infer-pyrefly      | 48,155 |  16,946 | 23,383 |  7,826 |      0 |    9 | 49,424 |   79,062 |   115.3 |
| pandas             | infer-trace        | 42,702 |  16,948 | 23,135 |  2,619 |      0 |    9 | 43,971 |   79,062 |    55.2 |
| twisted            | certain            |  2,435 |   2,435 |        |        |      0 |    0 |  2,435 |   17,874 |     7.1 |
| twisted            | likely             |  6,060 |   2,558 |  3,502 |        |      0 |    0 |  6,060 |   17,874 |     7.9 |
| twisted            | unsafe             |  7,132 |   2,434 |  3,502 |  1,196 |      0 |    0 |  7,132 |   17,874 |     7.0 |
| twisted            | infer-basedpyright |  8,541 |   2,437 |  3,532 |  2,572 |      0 |    0 |  8,541 |   17,874 |    47.0 |
| twisted            | infer-ty           |  7,538 |   2,434 |  3,526 |  1,578 |      0 |    0 |  7,538 |   17,874 |    16.7 |
| twisted            | infer-pyrefly      |  7,547 |   2,434 |  3,516 |  1,597 |      0 |    0 |  7,547 |   17,874 |    17.1 |
| pip                | certain            |  2,270 |   2,270 |        |        |      0 |    0 |  2,407 |    9,064 |     7.1 |
| pip                | likely             |  2,738 |   2,283 |    455 |        |      0 |    0 |  2,875 |    9,064 |     6.6 |
| pip                | unsafe             |  3,574 |   2,270 |    454 |    850 |      0 |    0 |  3,711 |    9,064 |     4.6 |
| pip                | infer-basedpyright |  4,293 |   2,271 |    498 |  1,524 |      0 |    3 |  4,430 |    9,064 |    32.5 |
| pip                | infer-ty           |  3,865 |   2,271 |    472 |  1,122 |      0 |    2 |  4,002 |    9,064 |    17.7 |
| pip                | infer-pyrefly      |  4,077 |   2,271 |    483 |  1,323 |      0 |    0 |  4,214 |    9,064 |    16.0 |
| structlog          | certain            |     98 |      98 |        |        |      0 |    0 |    207 |      425 |     0.6 |
| structlog          | likely             |    113 |      98 |     15 |        |      0 |    0 |    222 |      425 |     1.7 |
| structlog          | unsafe             |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.6 |
| structlog          | infer-basedpyright |    152 |      98 |     16 |     38 |      0 |    0 |    261 |      425 |     4.4 |
| structlog          | infer-ty           |    137 |      98 |     16 |     23 |      0 |    0 |    246 |      425 |     0.9 |
| structlog          | infer-pyrefly      |    147 |      98 |     17 |     32 |      0 |    0 |    256 |      425 |     1.0 |
| structlog          | infer-trace        |    126 |      98 |     15 |     13 |      0 |    0 |    235 |      425 |     0.6 |
| attrs              | certain            |     93 |      93 |        |        |      0 |    0 |     96 |      396 |     0.8 |
| attrs              | likely             |    102 |      94 |      8 |        |      0 |    0 |    105 |      396 |     1.0 |
| attrs              | unsafe             |    104 |      93 |      8 |      3 |      0 |    0 |    107 |      396 |     0.8 |
| attrs              | infer-basedpyright |    130 |      93 |      8 |     29 |      0 |    0 |    133 |      396 |     6.1 |
| attrs              | infer-ty           |    115 |      93 |      8 |     14 |      0 |    0 |    118 |      396 |     1.7 |
| attrs              | infer-pyrefly      |    120 |      93 |      8 |     19 |      0 |    0 |    123 |      396 |     2.1 |
| attrs              | infer-trace        |    107 |      93 |      9 |      5 |      0 |    0 |    110 |      396 |     0.7 |
| click              | certain            |    302 |     302 |        |        |      0 |    0 |    581 |      887 |     1.7 |
| click              | likely             |    329 |     303 |     26 |        |      0 |    0 |    608 |      887 |     2.1 |
| click              | unsafe             |    365 |     302 |     26 |     37 |      0 |    0 |    644 |      887 |     0.9 |
| click              | infer-basedpyright |    435 |     302 |     29 |    104 |      0 |    0 |    714 |      887 |     6.7 |
| click              | infer-ty           |    453 |     302 |     26 |    125 |      0 |    0 |    732 |      887 |     1.8 |
| click              | infer-pyrefly      |    442 |     302 |     31 |    109 |      0 |    0 |    721 |      887 |     1.5 |
| click              | infer-trace        |    365 |     302 |     26 |     37 |      0 |    0 |    644 |      887 |     1.4 |
| hypercorn          | certain            |    134 |     134 |        |        |      0 |    0 |    304 |      525 |     0.6 |
| hypercorn          | likely             |    154 |     134 |     20 |        |      0 |    0 |    324 |      525 |     0.7 |
| hypercorn          | unsafe             |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     0.9 |
| hypercorn          | infer-basedpyright |    214 |     134 |     21 |     59 |      0 |    0 |    384 |      525 |     2.9 |
| hypercorn          | infer-ty           |    219 |     134 |     21 |     64 |      0 |    0 |    389 |      525 |     0.8 |
| hypercorn          | infer-pyrefly      |    201 |     134 |     20 |     47 |      0 |    0 |    371 |      525 |     1.3 |
| hypercorn          | infer-trace        |    192 |     134 |     20 |     38 |      0 |    0 |    362 |      525 |     1.0 |
| starlette          | certain            |    314 |     314 |        |        |      0 |    0 |    399 |      829 |     0.7 |
| starlette          | likely             |    371 |     314 |     57 |        |      0 |    0 |    456 |      829 |     0.8 |
| starlette          | unsafe             |    411 |     314 |     57 |     40 |      0 |    0 |    496 |      829 |     0.9 |
| starlette          | infer-basedpyright |    485 |     314 |     57 |    114 |      0 |    0 |    570 |      829 |     3.9 |
| starlette          | infer-ty           |    469 |     314 |     56 |     99 |      0 |    0 |    554 |      829 |     1.4 |
| starlette          | infer-pyrefly      |    447 |     314 |     56 |     77 |      0 |    0 |    532 |      829 |     1.5 |
| starlette          | infer-trace        |    411 |     314 |     57 |     40 |      0 |    0 |    496 |      829 |     1.1 |
| werkzeug           | certain            |    527 |     527 |        |        |      0 |    0 |    743 |    1,509 |     1.0 |
| werkzeug           | likely             |    593 |     528 |     65 |        |      0 |    0 |    809 |    1,509 |     1.3 |
| werkzeug           | unsafe             |    654 |     527 |     65 |     62 |      0 |    0 |    870 |    1,509 |     1.2 |
| werkzeug           | infer-basedpyright |    776 |     527 |     78 |    171 |      0 |    0 |    992 |    1,509 |     3.7 |
| werkzeug           | infer-ty           |    803 |     527 |     81 |    195 |      0 |    0 |  1,019 |    1,509 |     1.3 |
| werkzeug           | infer-pyrefly      |    806 |     528 |     70 |    208 |      0 |    0 |  1,022 |    1,509 |     1.7 |
| werkzeug           | infer-trace        |    654 |     527 |     65 |     62 |      0 |    0 |    870 |    1,509 |     2.1 |
| mkdocs             | certain            |    810 |     810 |        |        |      0 |    0 |    921 |    2,443 |     1.9 |
| mkdocs             | likely             |  1,187 |     840 |    347 |        |      0 |    0 |  1,298 |    2,443 |     2.0 |
| mkdocs             | unsafe             |  1,292 |     810 |    347 |    135 |      0 |    0 |  1,403 |    2,443 |     2.0 |
| mkdocs             | infer-basedpyright |  1,385 |     810 |    354 |    221 |      0 |    0 |  1,496 |    2,443 |     5.1 |
| mkdocs             | infer-ty           |  1,418 |     810 |    359 |    249 |      0 |    0 |  1,529 |    2,443 |     3.2 |
| mkdocs             | infer-pyrefly      |  1,385 |     810 |    355 |    220 |      0 |    0 |  1,496 |    2,443 |     2.5 |
| mkdocs             | infer-trace        |  1,304 |     811 |    347 |    146 |      0 |    0 |  1,415 |    2,443 |     2.0 |
| httpx              | certain            |    234 |     234 |        |        |      0 |    0 |    272 |      607 |     0.6 |
| httpx              | likely             |    291 |     243 |     48 |        |      0 |    0 |    329 |      607 |     0.9 |
| httpx              | unsafe             |    307 |     234 |     48 |     25 |      0 |    0 |    345 |      607 |     0.8 |
| httpx              | infer-basedpyright |    392 |     234 |     53 |    105 |      0 |    0 |    430 |      607 |     5.5 |
| httpx              | infer-ty           |    376 |     235 |     52 |     89 |      0 |    0 |    414 |      607 |     2.5 |
| httpx              | infer-pyrefly      |    353 |     234 |     51 |     68 |      0 |    0 |    391 |      607 |     1.6 |
| httpx              | infer-trace        |    307 |     234 |     48 |     25 |      0 |    0 |    345 |      607 |     1.7 |
| black              | certain            |    707 |     707 |        |        |      0 |    0 |    947 |    1,513 |     1.1 |
| black              | likely             |    834 |     720 |    114 |        |      0 |    0 |  1,074 |    1,513 |     0.9 |
| black              | unsafe             |    870 |     707 |    114 |     49 |      0 |    0 |  1,110 |    1,513 |     0.8 |
| black              | infer-basedpyright |    928 |     707 |    114 |    107 |      0 |    0 |  1,168 |    1,513 |     7.7 |
| black              | infer-ty           |    928 |     707 |    114 |    107 |      0 |    0 |  1,168 |    1,513 |     1.8 |
| black              | infer-pyrefly      |    914 |     707 |    112 |     95 |      0 |    0 |  1,154 |    1,513 |     2.0 |
| black              | infer-trace        |    870 |     707 |    114 |     49 |      0 |    0 |  1,110 |    1,513 |     0.9 |
| fastapi            | certain            |    257 |     257 |        |        |      0 |    0 |    794 |    1,279 |     1.4 |
| fastapi            | likely             |    297 |     263 |     34 |        |      0 |    0 |    834 |    1,279 |     3.7 |
| fastapi            | unsafe             |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     2.7 |
| fastapi            | infer-basedpyright |    348 |     257 |     33 |     58 |      0 |    0 |    885 |    1,279 |     6.5 |
| fastapi            | infer-ty           |    371 |     257 |     32 |     82 |      0 |    0 |    908 |    1,279 |     3.8 |
| fastapi            | infer-pyrefly      |    345 |     257 |     34 |     54 |      0 |    0 |    882 |    1,279 |     2.8 |
| fastapi            | infer-trace        |    322 |     257 |     34 |     31 |      0 |    0 |    859 |    1,279 |     1.0 |
| cattrs             | certain            |    105 |     105 |        |        |      0 |    0 |    144 |      559 |     2.5 |
| cattrs             | likely             |    139 |     112 |     27 |        |      0 |    0 |    178 |      559 |     1.0 |
| cattrs             | unsafe             |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     1.1 |
| cattrs             | infer-basedpyright |    194 |     107 |     29 |     58 |      0 |    0 |    233 |      559 |     5.3 |
| cattrs             | infer-ty           |    195 |     105 |     27 |     63 |      0 |    0 |    234 |      559 |     1.7 |
| cattrs             | infer-pyrefly      |    182 |     105 |     28 |     49 |      0 |    0 |    221 |      559 |     1.8 |
| cattrs             | infer-trace        |    151 |     108 |     26 |     17 |      0 |    0 |    190 |      559 |     1.6 |
| pytest             | certain            |  1,358 |   1,358 |        |        |      0 |    0 |  1,773 |    3,418 |     2.0 |
| pytest             | likely             |  1,514 |   1,362 |    152 |        |      0 |    0 |  1,929 |    3,418 |     2.8 |
| pytest             | unsafe             |  1,643 |   1,358 |    152 |    133 |      0 |    0 |  2,058 |    3,418 |     3.0 |
| pytest             | infer-basedpyright |  1,988 |   1,355 |    172 |    461 |      0 |    0 |  2,403 |    3,418 |    12.0 |
| pytest             | infer-ty           |  1,996 |   1,355 |    174 |    467 |      0 |    0 |  2,411 |    3,418 |     4.0 |
| pytest             | infer-pyrefly      |  2,059 |   1,355 |    174 |    530 |      0 |    0 |  2,474 |    3,418 |     5.0 |
| pytest             | infer-trace        |  1,660 |   1,358 |    152 |    150 |      0 |    0 |  2,075 |    3,418 |     2.7 |
| botocore           | certain            |    543 |     543 |        |        |      0 |    0 |    561 |    3,806 |     2.6 |
| botocore           | likely             |    717 |     549 |    168 |        |      0 |    0 |    735 |    3,806 |     3.5 |
| botocore           | unsafe             |  1,151 |     541 |    168 |    442 |      0 |    0 |  1,169 |    3,806 |     3.2 |
| botocore           | infer-basedpyright |  1,296 |     536 |    171 |    589 |      0 |    0 |  1,314 |    3,806 |    16.2 |
| botocore           | infer-ty           |  1,207 |     541 |    169 |    497 |      0 |    0 |  1,225 |    3,806 |     5.1 |
| botocore           | infer-pyrefly      |  1,282 |     537 |    171 |    574 |      0 |    0 |  1,300 |    3,806 |     4.4 |
| botocore           | infer-trace        |  1,498 |     541 |    194 |    763 |      0 |    0 |  1,516 |    3,806 |     4.1 |
| uvicorn            | certain            |    231 |     231 |        |        |      0 |    0 |    382 |      640 |     0.7 |
| uvicorn            | likely             |    260 |     231 |     29 |        |      0 |    0 |    411 |      640 |     2.1 |
| uvicorn            | unsafe             |    275 |     231 |     29 |     15 |      0 |    0 |    426 |      640 |     2.9 |
| uvicorn            | infer-basedpyright |    346 |     231 |     32 |     83 |      0 |    0 |    497 |      640 |     3.9 |
| uvicorn            | infer-ty           |    324 |     231 |     29 |     64 |      0 |    0 |    475 |      640 |     2.2 |
| uvicorn            | infer-pyrefly      |    300 |     231 |     32 |     37 |      0 |    0 |    451 |      640 |     1.8 |
| uvicorn            | infer-trace        |    275 |     231 |     29 |     15 |      0 |    0 |    426 |      640 |     0.8 |
| mcp                | certain            |    694 |     694 |        |        |      0 |    0 |  1,457 |    2,483 |     0.9 |
| mcp                | likely             |    848 |     700 |    148 |        |      0 |    0 |  1,611 |    2,483 |     2.0 |
| mcp                | unsafe             |    930 |     694 |    148 |     88 |      0 |    0 |  1,693 |    2,483 |     6.0 |
| mcp                | infer-basedpyright |  1,048 |     694 |    159 |    195 |      0 |    0 |  1,811 |    2,483 |     5.6 |
| mcp                | infer-ty           |  1,039 |     694 |    156 |    189 |      0 |    0 |  1,802 |    2,483 |     3.0 |
| mcp                | infer-pyrefly      |  1,016 |     694 |    152 |    170 |      0 |    0 |  1,779 |    2,483 |     2.6 |
| mcp                | infer-trace        |    930 |     694 |    148 |     88 |      0 |    0 |  1,693 |    2,483 |     2.3 |
| textual            | certain            |  2,707 |   2,707 |        |        |      0 |    0 |  3,901 |    7,677 |     3.2 |
| textual            | likely             |  3,189 |   2,731 |    458 |        |      0 |    0 |  4,383 |    7,677 |     5.1 |
| textual            | unsafe             |  3,448 |   2,707 |    457 |    284 |      0 |    0 |  4,642 |    7,677 |     2.6 |
| textual            | infer-basedpyright |  4,634 |   2,707 |    525 |  1,402 |      0 |   14 |  5,828 |    7,677 |    21.2 |
| textual            | infer-ty           |  4,726 |   2,707 |    531 |  1,488 |      0 |    0 |  5,920 |    7,677 |     7.9 |
| textual            | infer-pyrefly      |  3,850 |   2,707 |    474 |    669 |      0 |    0 |  5,044 |    7,677 |     5.7 |
| pdm                | certain            |  1,147 |   1,147 |        |        |      0 |    0 |  1,508 |    3,079 |     1.7 |
| pdm                | likely             |  1,347 |   1,160 |    187 |        |      0 |    0 |  1,708 |    3,079 |     2.7 |
| pdm                | unsafe             |  1,468 |   1,147 |    186 |    135 |      0 |    0 |  1,829 |    3,079 |     4.3 |
| pdm                | infer-basedpyright |  1,853 |   1,150 |    215 |    488 |      0 |    0 |  2,214 |    3,079 |    14.1 |
| pdm                | infer-ty           |  1,845 |   1,150 |    215 |    480 |      0 |    0 |  2,206 |    3,079 |     2.8 |
| pdm                | infer-pyrefly      |  1,627 |   1,148 |    196 |    283 |      0 |    0 |  1,988 |    3,079 |     3.9 |
| pdm                | infer-trace        |  1,468 |   1,147 |    186 |    135 |      0 |    0 |  1,829 |    3,079 |     2.8 |
| strawberry-graphql | certain            |    611 |     611 |        |        |      0 |    0 |  1,387 |    2,582 |     1.6 |
| strawberry-graphql | likely             |    778 |     613 |    165 |        |      0 |    0 |  1,554 |    2,582 |     2.8 |
| strawberry-graphql | unsafe             |    829 |     611 |    165 |     53 |      0 |    0 |  1,605 |    2,582 |     8.4 |
| strawberry-graphql | infer-basedpyright |    989 |     610 |    166 |    213 |      0 |    0 |  1,765 |    2,582 |     9.3 |
| strawberry-graphql | infer-ty           |    986 |     610 |    165 |    211 |      0 |    0 |  1,762 |    2,582 |     4.2 |
| strawberry-graphql | infer-pyrefly      |    885 |     610 |    166 |    109 |      0 |    0 |  1,661 |    2,582 |     3.5 |
| strawberry-graphql | infer-trace        |    829 |     611 |    165 |     53 |      0 |    0 |  1,605 |    2,582 |     1.7 |
| pygments           | certain            |    735 |     735 |        |        |      0 |    0 |    735 |    7,666 |     3.2 |
| pygments           | likely             |    814 |     738 |     76 |        |      0 |    0 |    814 |    7,666 |     5.8 |
| pygments           | unsafe             |    963 |     735 |     76 |    152 |      0 |    0 |    963 |    7,666 |     7.0 |
| pygments           | infer-basedpyright |  1,076 |     735 |     83 |    258 |      0 |    0 |  1,076 |    7,666 |    15.1 |
| pygments           | infer-ty           |  1,077 |     735 |     84 |    258 |      0 |    0 |  1,077 |    7,666 |     7.2 |
| pygments           | infer-pyrefly      |  1,137 |     735 |     84 |    318 |      0 |    2 |  1,137 |    7,666 |     7.1 |
| pygments           | infer-trace        |  1,073 |     730 |    100 |    243 |      0 |    0 |  1,073 |    7,666 |     4.3 |
| streamlink         | certain            |    682 |     682 |        |        |      0 |    0 |  2,944 |    5,291 |     2.1 |
| streamlink         | likely             |    793 |     685 |    108 |        |      0 |    0 |  3,055 |    5,291 |     4.2 |
| streamlink         | unsafe             |    932 |     682 |    108 |    142 |      0 |    0 |  3,194 |    5,291 |     6.2 |
| streamlink         | infer-basedpyright |  1,318 |     683 |    125 |    510 |      0 |    0 |  3,580 |    5,291 |    10.2 |
| streamlink         | infer-ty           |  1,475 |     682 |    136 |    657 |      0 |    0 |  3,737 |    5,291 |     5.6 |
| streamlink         | infer-pyrefly      |  1,121 |     682 |    120 |    319 |      0 |    0 |  3,383 |    5,291 |     3.4 |
| streamlink         | infer-trace        |    940 |     682 |    108 |    150 |      0 |    0 |  3,202 |    5,291 |     4.0 |
| sphinx             | certain            |  3,128 |   3,128 |        |        |      0 |    0 |  4,056 |    8,901 |     3.5 |
| sphinx             | likely             |  3,576 |   3,142 |    434 |        |      0 |    0 |  4,504 |    8,901 |     5.8 |
| sphinx             | unsafe             |  3,949 |   3,128 |    433 |    388 |      0 |    0 |  4,877 |    8,901 |     9.5 |
| sphinx             | infer-basedpyright |  4,726 |   3,129 |    461 |  1,136 |      0 |    0 |  5,654 |    8,901 |    26.8 |
| sphinx             | infer-ty           |  4,794 |   3,128 |    456 |  1,210 |      0 |    0 |  5,722 |    8,901 |     8.5 |
| sphinx             | infer-pyrefly      |  5,085 |   3,129 |    475 |  1,481 |      0 |    0 |  6,013 |    8,901 |     7.9 |
| sphinx             | infer-trace        |  3,949 |   3,128 |    433 |    388 |      0 |    0 |  4,877 |    8,901 |     3.5 |
| tox                | certain            |    943 |     943 |        |        |      0 |    0 |  1,279 |    2,098 |     0.9 |
| tox                | likely             |  1,025 |     944 |     81 |        |      0 |    0 |  1,361 |    2,098 |     1.5 |
| tox                | unsafe             |  1,081 |     943 |     81 |     57 |      0 |    0 |  1,417 |    2,098 |     3.7 |
| tox                | infer-basedpyright |  1,333 |     945 |     98 |    290 |      0 |    0 |  1,669 |    2,098 |     9.9 |
| tox                | infer-ty           |  1,368 |     945 |     97 |    326 |      0 |    0 |  1,704 |    2,098 |     2.7 |
| tox                | infer-pyrefly      |  1,413 |     945 |     97 |    371 |      0 |    0 |  1,749 |    2,098 |     3.4 |
| tox                | infer-trace        |  1,081 |     943 |     81 |     57 |      0 |    0 |  1,417 |    2,098 |     1.3 |
| pint               | certain            |    617 |     617 |        |        |      0 |    0 |    782 |    3,243 |     2.3 |
| pint               | likely             |    721 |     623 |     98 |        |      0 |    0 |    886 |    3,243 |     4.2 |
| pint               | unsafe             |    771 |     617 |     98 |     56 |      0 |    0 |    936 |    3,243 |     2.4 |
| pint               | infer-basedpyright |    986 |     614 |     98 |    274 |      0 |   16 |  1,151 |    3,243 |    32.5 |
| pint               | infer-ty           |    894 |     614 |     93 |    187 |      0 |   20 |  1,059 |    3,243 |     4.0 |
| pint               | infer-pyrefly      |    822 |     614 |     90 |    118 |      0 |    0 |    987 |    3,243 |     3.6 |
| pint               | infer-trace        |    776 |     617 |     98 |     61 |      0 |    0 |    941 |    3,243 |     2.3 |
| altair             | certain            |    378 |     378 |        |        |      0 |    0 |  2,060 |    3,383 |     4.5 |
| altair             | likely             |    425 |     378 |     47 |        |      0 |    0 |  2,107 |    3,383 |     6.2 |
| altair             | unsafe             |    438 |     378 |     47 |     13 |      0 |    0 |  2,120 |    3,383 |     6.6 |
| altair             | infer-basedpyright |    507 |     375 |     50 |     82 |      0 |    0 |  2,189 |    3,383 |    21.4 |
| altair             | infer-ty           |    503 |     375 |     48 |     80 |      0 |    3 |  2,185 |    3,383 |     9.3 |
| altair             | infer-pyrefly      |    496 |     375 |     48 |     73 |      0 |    0 |  2,178 |    3,383 |    10.3 |
| altair             | infer-trace        |    445 |     378 |     48 |     19 |      0 |    0 |  2,127 |    3,383 |     2.9 |
| seaborn            | certain            |    639 |     639 |        |        |      0 |    0 |    854 |    3,110 |     3.0 |
| seaborn            | likely             |    776 |     647 |    129 |        |      0 |    0 |    991 |    3,110 |     4.5 |
| seaborn            | unsafe             |    867 |     639 |    129 |     99 |      0 |    0 |  1,082 |    3,110 |     8.7 |
| seaborn            | infer-basedpyright |    980 |     639 |    132 |    209 |      0 |    4 |  1,195 |    3,110 |    23.3 |
| seaborn            | infer-ty           |    955 |     638 |    131 |    186 |      0 |    0 |  1,170 |    3,110 |     5.4 |
| seaborn            | infer-pyrefly      |  1,040 |     639 |    133 |    268 |      0 |    0 |  1,255 |    3,110 |     9.5 |
| seaborn            | infer-trace        |    906 |     639 |    131 |    136 |      0 |    0 |  1,121 |    3,110 |     3.5 |
| aiohttp            | certain            |    701 |     701 |        |        |      0 |    0 |  1,277 |    2,433 |     1.4 |
| aiohttp            | likely             |    842 |     707 |    135 |        |      0 |    0 |  1,418 |    2,433 |     6.9 |
| aiohttp            | unsafe             |    953 |     701 |    135 |    117 |      0 |    0 |  1,529 |    2,433 |     3.4 |
| aiohttp            | infer-basedpyright |  1,144 |     702 |    143 |    299 |      0 |    0 |  1,720 |    2,433 |    10.5 |
| aiohttp            | infer-ty           |  1,166 |     702 |    142 |    322 |      0 |    0 |  1,742 |    2,433 |     9.9 |
| aiohttp            | infer-pyrefly      |  1,271 |     702 |    148 |    421 |      0 |    0 |  1,847 |    2,433 |     9.4 |
| aiohttp            | infer-trace        |    953 |     701 |    135 |    117 |      0 |    0 |  1,529 |    2,433 |     1.6 |
| websockets         | certain            |    328 |     328 |        |        |      0 |    0 |    455 |      918 |     1.3 |
| websockets         | likely             |    389 |     329 |     60 |        |      0 |    0 |    516 |      918 |     1.0 |
| websockets         | unsafe             |    439 |     328 |     60 |     51 |      0 |    0 |    566 |      918 |     4.4 |
| websockets         | infer-basedpyright |    548 |     330 |     60 |    158 |      0 |    0 |    675 |      918 |     3.4 |
| websockets         | infer-ty           |    562 |     330 |     60 |    172 |      0 |    0 |    689 |      918 |     1.5 |
| websockets         | infer-pyrefly      |    583 |     330 |     60 |    193 |      0 |    0 |    710 |      918 |     1.7 |
| websockets         | infer-trace        |    439 |     328 |     60 |     51 |      0 |    0 |    566 |      918 |     1.5 |
| anyio              | certain            |    212 |     212 |        |        |      0 |    0 |    487 |      990 |     1.6 |
| anyio              | likely             |    245 |     212 |     33 |        |      0 |    0 |    520 |      990 |     1.9 |
| anyio              | unsafe             |    273 |     212 |     33 |     28 |      0 |    0 |    548 |      990 |     2.8 |
| anyio              | infer-basedpyright |    367 |     212 |     41 |    114 |      0 |    0 |    642 |      990 |     4.9 |
| anyio              | infer-ty           |    399 |     212 |     44 |    143 |      0 |    0 |    674 |      990 |     4.0 |
| anyio              | infer-pyrefly      |    378 |     212 |     40 |    126 |      0 |    0 |    653 |      990 |     1.8 |
| anyio              | infer-trace        |    273 |     212 |     33 |     28 |      0 |    0 |    548 |      990 |     1.4 |
| zarr               | certain            |  1,084 |   1,084 |        |        |      0 |    0 |  1,752 |    3,079 |     2.0 |
| zarr               | likely             |  1,156 |   1,085 |     71 |        |      0 |    0 |  1,824 |    3,079 |     2.6 |
| zarr               | unsafe             |  1,193 |   1,084 |     71 |     38 |      0 |    0 |  1,861 |    3,079 |     4.9 |
| zarr               | infer-basedpyright |  1,614 |   1,084 |     96 |    434 |      0 |    0 |  2,282 |    3,079 |    16.1 |
| zarr               | infer-ty           |  1,580 |   1,084 |     95 |    401 |      0 |    0 |  2,248 |    3,079 |     4.4 |
| zarr               | infer-pyrefly      |  1,357 |   1,084 |     79 |    194 |      0 |    0 |  2,025 |    3,079 |     6.1 |
| zarr               | infer-trace        |  1,193 |   1,084 |     71 |     38 |      0 |    0 |  1,861 |    3,079 |     3.0 |
| joblib             | certain            |    525 |     525 |        |        |      0 |    0 |    526 |    2,241 |     2.0 |
| joblib             | likely             |    707 |     526 |    181 |        |      0 |    0 |    708 |    2,241 |     2.4 |
| joblib             | unsafe             |    792 |     524 |    179 |     89 |      0 |    0 |    793 |    2,241 |     4.3 |
| joblib             | infer-basedpyright |    909 |     524 |    184 |    201 |      0 |    0 |    910 |    2,241 |    12.3 |
| joblib             | infer-ty           |    858 |     524 |    181 |    153 |      0 |    0 |    859 |    2,241 |     3.2 |
| joblib             | infer-pyrefly      |    904 |     522 |    183 |    199 |      0 |    0 |    905 |    2,241 |     9.4 |
| joblib             | infer-trace        |    803 |     524 |    181 |     98 |      0 |    0 |    804 |    2,241 |     2.0 |
| networkx           | certain            |  3,969 |   3,969 |        |        |      0 |    0 |  4,031 |   22,518 |     5.3 |
| networkx           | likely             |  6,155 |   4,018 |  2,137 |        |      0 |    0 |  6,217 |   22,518 |    12.2 |
| networkx           | unsafe             |  6,358 |   3,969 |  2,084 |    305 |      0 |    0 |  6,420 |   22,518 |     7.3 |
| networkx           | infer-basedpyright |  7,404 |   3,969 |  2,193 |  1,242 |      0 |    0 |  7,466 |   22,518 |    61.9 |
| networkx           | infer-ty           |  6,852 |   3,969 |  2,149 |    734 |      0 |    0 |  6,914 |   22,518 |    17.1 |
| networkx           | infer-pyrefly      |  6,936 |   3,971 |  2,157 |    808 |      0 |    2 |  6,998 |   22,518 |    21.2 |
| networkx           | infer-trace        |  6,797 |   3,969 |  2,113 |    715 |      0 |    0 |  6,859 |   22,518 |     6.1 |
| nibabel            | certain            |  1,849 |   1,849 |        |        |      0 |    0 |  1,931 |    8,550 |     4.3 |
| nibabel            | likely             |  2,540 |   1,875 |    665 |        |      0 |    0 |  2,622 |    8,550 |    10.0 |
| nibabel            | unsafe             |  2,806 |   1,849 |    663 |    294 |      0 |    0 |  2,888 |    8,550 |     7.0 |
| nibabel            | infer-basedpyright |  3,430 |   1,850 |    703 |    877 |      0 |    0 |  3,512 |    8,550 |    57.3 |
| nibabel            | infer-ty           |  3,392 |   1,850 |    720 |    822 |      0 |    0 |  3,474 |    8,550 |    23.6 |
| nibabel            | infer-pyrefly      |  3,232 |   1,849 |    673 |    710 |      0 |    0 |  3,314 |    8,550 |    14.3 |
| nibabel            | infer-trace        |  2,885 |   1,849 |    669 |    367 |      0 |    0 |  2,967 |    8,550 |     4.4 |
| narwhals           | certain            |    982 |     982 |        |        |      0 |    0 |  1,847 |    3,985 |     2.6 |
| narwhals           | likely             |  1,049 |     983 |     66 |        |      0 |    0 |  1,914 |    3,985 |     4.8 |
| narwhals           | unsafe             |  1,101 |     982 |     66 |     53 |      0 |    0 |  1,966 |    3,985 |     7.8 |
| narwhals           | infer-basedpyright |  1,419 |     991 |     77 |    351 |      0 |    4 |  2,284 |    3,985 |    17.6 |
| narwhals           | infer-ty           |  1,390 |     991 |     86 |    313 |      0 |    0 |  2,255 |    3,985 |     7.1 |
| narwhals           | infer-pyrefly      |  1,607 |     991 |     80 |    536 |      0 |    3 |  2,472 |    3,985 |     9.6 |
| narwhals           | infer-trace        |  1,101 |     982 |     66 |     53 |      0 |    0 |  1,966 |    3,985 |     2.1 |
| xarray             | certain            |  3,557 |   3,557 |        |        |      0 |    0 |  4,586 |   22,373 |    20.4 |
| xarray             | likely             |  6,684 |   3,601 |  3,083 |        |      0 |    0 |  7,713 |   22,373 |    27.0 |
| xarray             | unsafe             |  6,895 |   3,557 |  3,083 |    255 |      0 |    0 |  7,924 |   22,373 |    47.8 |
| xarray             | infer-basedpyright |  8,913 |   3,524 |  3,157 |  2,232 |      0 |    0 |  9,942 |   22,373 |    88.3 |
| xarray             | infer-ty           |  8,959 |   3,524 |  3,150 |  2,285 |      0 |    0 |  9,988 |   22,373 |    81.5 |
| xarray             | infer-pyrefly      |  7,352 |   3,525 |  3,098 |    729 |      0 |    0 |  8,381 |   22,373 |    41.6 |
| xarray             | infer-trace        |  6,914 |   3,557 |  3,082 |    275 |      0 |    0 |  7,943 |   22,373 |    21.1 |
| litestar           | certain            |    607 |     607 |        |        |      0 |    0 |  2,161 |    3,459 |     2.4 |
| litestar           | likely             |    708 |     608 |    100 |        |      0 |    0 |  2,262 |    3,459 |     4.3 |
| litestar           | unsafe             |    768 |     607 |    100 |     61 |      0 |    0 |  2,322 |    3,459 |    14.2 |
| litestar           | infer-basedpyright |  1,004 |     604 |    111 |    289 |      0 |    0 |  2,558 |    3,459 |    12.8 |
| litestar           | infer-ty           |  1,014 |     604 |    114 |    296 |      0 |    0 |  2,568 |    3,459 |     6.2 |
| litestar           | infer-pyrefly      |    873 |     604 |    107 |    162 |      0 |    0 |  2,427 |    3,459 |     4.5 |
| litestar           | infer-trace        |    768 |     607 |    100 |     61 |      0 |    0 |  2,322 |    3,459 |     3.0 |
| stripe             | certain            |    569 |     569 |        |        |      0 |    0 | 29,319 |   32,107 |     4.0 |
| stripe             | likely             |    730 |     569 |    161 |        |      0 |    0 | 29,480 |   32,107 |     4.9 |
| stripe             | unsafe             |  1,233 |     569 |    161 |    503 |      0 |    0 | 29,983 |   32,107 |     5.0 |
| stripe             | infer-basedpyright |  1,952 |     569 |    161 |  1,222 |      0 |    0 | 30,702 |   32,107 |   648.1 |
| stripe             | infer-ty           |  1,286 |     569 |    161 |    556 |      0 |    0 | 30,036 |   32,107 |    12.8 |
| stripe             | infer-pyrefly      |  1,273 |     569 |    161 |    543 |      0 |    0 | 30,023 |   32,107 |    10.4 |
| celery             | certain            |    508 |     508 |        |        |      0 |    0 |    524 |    3,764 |     3.8 |
| celery             | likely             |    627 |     511 |    116 |        |      0 |    0 |    643 |    3,764 |     6.0 |
| celery             | unsafe             |    868 |     508 |    116 |    244 |      0 |    0 |    884 |    3,764 |    13.2 |
| celery             | infer-basedpyright |  1,035 |     508 |    125 |    402 |      0 |    0 |  1,051 |    3,764 |    13.6 |
| celery             | infer-ty           |    938 |     508 |    117 |    313 |      0 |    0 |    954 |    3,764 |     6.9 |
| celery             | infer-pyrefly      |    977 |     508 |    117 |    352 |      0 |    0 |    993 |    3,764 |     5.7 |
| celery             | infer-trace        |    932 |     508 |    115 |    309 |      0 |    0 |    948 |    3,764 |     5.5 |
| optuna             | certain            |  1,476 |   1,476 |        |        |      0 |    0 |  1,767 |    3,889 |     5.6 |
| optuna             | likely             |  1,675 |   1,483 |    192 |        |      0 |    0 |  1,966 |    3,889 |    24.9 |
| optuna             | unsafe             |  1,772 |   1,476 |    192 |    104 |      0 |    0 |  2,063 |    3,889 |    10.6 |
| optuna             | infer-basedpyright |  2,113 |   1,476 |    211 |    426 |      0 |    0 |  2,404 |    3,889 |    25.7 |
| optuna             | infer-ty           |  2,151 |   1,476 |    229 |    446 |      0 |    5 |  2,442 |    3,889 |    13.8 |
| optuna             | infer-pyrefly      |  1,957 |   1,476 |    209 |    272 |      0 |    5 |  2,248 |    3,889 |    11.6 |
| optuna             | infer-trace        |  1,772 |   1,476 |    192 |    104 |      0 |    0 |  2,063 |    3,889 |     4.4 |
| dask               | certain            |  3,120 |   3,120 |        |        |      0 |    0 |  3,378 |   24,430 |    18.9 |
| dask               | likely             |  5,046 |   3,163 |  1,883 |        |      0 |    0 |  5,304 |   24,430 |    33.5 |
| dask               | unsafe             |  5,856 |   3,128 |  1,881 |    847 |      0 |    0 |  6,114 |   24,430 |    35.3 |
| dask               | infer-basedpyright |  6,661 |   3,128 |  1,913 |  1,620 |      0 |   34 |  6,919 |   24,430 |   119.6 |
| dask               | infer-ty           |  6,185 |   3,128 |  1,903 |  1,154 |      0 |   23 |  6,443 |   24,430 |    55.7 |
| dask               | infer-pyrefly      |  6,454 |   3,132 |  1,911 |  1,411 |      0 |    0 |  6,712 |   24,430 |    43.4 |
| dask               | infer-trace        |  5,982 |   3,125 |  1,884 |    973 |      0 |    0 |  6,240 |   24,430 |    27.7 |
| mypy               | certain            |  4,763 |   4,763 |        |        |      0 |    0 |  7,063 |   13,701 |     9.6 |
| mypy               | likely             |  5,944 |   4,790 |  1,154 |        |      0 |    0 |  8,244 |   13,701 |     8.2 |
| mypy               | unsafe             |  6,316 |   4,763 |  1,152 |    401 |      0 |    0 |  8,615 |   13,701 |     8.8 |
| mypy               | infer-basedpyright |  8,206 |   4,767 |  1,270 |  2,169 |      0 |    2 | 10,504 |   13,701 |    30.9 |
| mypy               | infer-ty           |  8,554 |   4,766 |  1,277 |  2,511 |      0 |    0 | 10,852 |   13,701 |    15.5 |
| mypy               | infer-pyrefly      |  8,799 |   4,763 |  1,284 |  2,752 |      0 |    2 | 11,097 |   13,701 |    12.0 |
| mypy               | infer-trace        |  6,316 |   4,763 |  1,152 |    401 |      0 |    0 |  8,615 |   13,701 |     9.9 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 23,995 |  23,995 |        |        |
| certain            | stdlib                 | 16,143 |  16,143 |        |        |
| certain            | call                   |  9,600 |   9,600 |        |        |
| certain            | container+literal      |  6,845 |   6,845 |        |        |
| certain            | builtin                |  4,402 |   4,402 |        |        |
| certain            | loop                   |  3,942 |   3,942 |        |        |
| certain            | copy+loop              |  3,612 |   3,612 |        |        |
| certain            | method                 |  3,576 |   3,576 |        |        |
| certain            | container+literal+loop |  2,079 |   2,079 |        |        |
| certain            | literal+method         |  1,631 |   1,631 |        |        |
| certain            | call+unpack            |  1,572 |   1,572 |        |        |
| certain            | open                   |  1,493 |   1,493 |        |        |
| likely             | constructor            | 36,177 |     257 | 35,920 |        |
| likely             | literal                | 24,003 |  24,003 |        |        |
| likely             | stdlib                 | 16,231 |  16,231 |        |        |
| likely             | call                   | 10,099 |   9,613 |    486 |        |
| likely             | container+literal      |  6,845 |   6,845 |        |        |
| likely             | method                 |  5,050 |   3,606 |  1,444 |        |
| likely             | builtin                |  4,403 |   4,403 |        |        |
| likely             | copy+loop              |  4,145 |   3,638 |    507 |        |
| likely             | loop                   |  3,946 |   3,946 |        |        |
| likely             | container+literal+loop |  2,079 |   2,079 |        |        |
| likely             | literal+method         |  1,631 |   1,631 |        |        |
| likely             | call+unpack            |  1,572 |   1,572 |        |        |
| unsafe             | constructor            | 36,176 |     257 | 35,919 |        |
| unsafe             | literal                | 23,998 |  23,993 |        |      5 |
| unsafe             | stdlib                 | 16,604 |  16,145 |        |    459 |
| unsafe             | call                   | 10,061 |   9,600 |    461 |        |
| unsafe             | container+literal      |  6,845 |   6,845 |        |        |
| unsafe             | literal+member         |  5,057 |         |        |  5,057 |
| unsafe             | method                 |  4,981 |   3,576 |  1,405 |        |
| unsafe             | builtin                |  4,404 |   4,402 |        |      2 |
| unsafe             | returned               |  4,395 |   1,221 |        |  3,174 |
| unsafe             | copy+loop              |  4,111 |   3,612 |    499 |        |
| unsafe             | loop                   |  3,942 |   3,942 |        |        |
| unsafe             | container+literal+loop |  2,079 |   2,079 |        |        |
| infer-basedpyright | constructor            | 36,110 |     256 | 35,854 |        |
| infer-basedpyright | checker                | 26,675 |         |        | 26,675 |
| infer-basedpyright | literal                | 24,000 |  23,995 |        |      5 |
| infer-basedpyright | stdlib                 | 16,714 |  16,085 |        |    629 |
| infer-basedpyright | call                   | 10,202 |   9,588 |    614 |        |
| infer-basedpyright | container+literal      |  6,848 |   6,848 |        |        |
| infer-basedpyright | method                 |  5,218 |   3,543 |  1,675 |        |
| infer-basedpyright | literal+member         |  5,056 |         |        |  5,056 |
| infer-basedpyright | copy+loop              |  4,741 |   3,611 |  1,130 |        |
| infer-basedpyright | returned               |  4,666 |   1,202 |        |  3,464 |
| infer-basedpyright | builtin                |  4,404 |   4,402 |        |      2 |
| infer-basedpyright | loop                   |  3,942 |   3,942 |        |        |
| infer-ty           | constructor            | 36,109 |     257 | 35,852 |        |
| infer-ty           | literal                | 23,999 |  23,994 |        |      5 |
| infer-ty           | checker                | 21,711 |         |        | 21,711 |
| infer-ty           | stdlib                 | 16,716 |  16,101 |        |    615 |
| infer-ty           | call                   | 10,150 |   9,589 |    561 |        |
| infer-ty           | container+literal      |  6,849 |   6,849 |        |        |
| infer-ty           | method                 |  5,181 |   3,543 |  1,638 |        |
| infer-ty           | literal+member         |  5,057 |         |        |  5,057 |
| infer-ty           | copy+loop              |  4,662 |   3,611 |  1,051 |        |
| infer-ty           | returned               |  4,637 |   1,221 |        |  3,416 |
| infer-ty           | builtin                |  4,404 |   4,402 |        |      2 |
| infer-ty           | loop                   |  3,942 |   3,942 |        |        |
| infer-pyrefly      | constructor            | 36,097 |     256 | 35,841 |        |
| infer-pyrefly      | literal                | 23,999 |  23,994 |        |      5 |
| infer-pyrefly      | checker                | 23,386 |         |        | 23,386 |
| infer-pyrefly      | stdlib                 | 16,744 |  16,105 |        |    639 |
| infer-pyrefly      | call                   | 10,128 |   9,590 |    538 |        |
| infer-pyrefly      | container+literal      |  6,852 |   6,852 |        |        |
| infer-pyrefly      | method                 |  5,137 |   3,543 |  1,594 |        |
| infer-pyrefly      | literal+member         |  5,056 |         |        |  5,056 |
| infer-pyrefly      | copy+loop              |  4,646 |   3,611 |  1,035 |        |
| infer-pyrefly      | returned               |  4,626 |   1,218 |        |  3,408 |
| infer-pyrefly      | builtin                |  4,404 |   4,402 |        |      2 |
| infer-pyrefly      | loop                   |  3,942 |   3,942 |        |        |
| infer-trace        | constructor            | 28,654 |      25 | 28,629 |        |
| infer-trace        | literal                | 13,892 |  13,890 |        |      2 |
| infer-trace        | call                   |  9,567 |   9,111 |    456 |        |
| infer-trace        | method                 |  4,364 |   2,992 |  1,372 |        |
| infer-trace        | container+literal      |  4,348 |   4,348 |        |        |
| infer-trace        | stdlib                 |  4,076 |   3,892 |        |    184 |
| infer-trace        | traced                 |  3,026 |         |        |  3,026 |
| infer-trace        | literal+member         |  2,825 |         |        |  2,825 |
| infer-trace        | copy+loop              |  2,624 |   2,297 |    327 |        |
| infer-trace        | builtin                |  2,616 |   2,614 |        |      2 |
| infer-trace        | loop                   |  2,024 |   2,024 |        |        |
| infer-trace        | call+unpack            |  1,485 |   1,485 |        |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| standard library   | 113,671 |  13,076 |  63,150 |        0 |
| django             |  17,176 |   2,786 |  11,768 |        0 |
| sqlalchemy         |  12,962 |     847 |  10,177 |        0 |
| pydantic           |   3,117 |     404 |   1,522 |        0 |
| pandas             |  77,793 |  24,353 |  36,488 |        0 |
| twisted            |  17,874 |   4,697 |  10,742 |        0 |
| pip                |   8,924 |   1,304 |   5,350 |        0 |
| structlog          |     316 |      28 |     190 |        0 |
| attrs              |     393 |      11 |     289 |        0 |
| click              |     608 |      63 |     243 |        0 |
| hypercorn          |     355 |      58 |     163 |        0 |
| starlette          |     744 |      97 |     333 |        0 |
| werkzeug           |   1,293 |     127 |     639 |        0 |
| mkdocs             |   2,332 |     482 |   1,040 |        0 |
| httpx              |     569 |      73 |     262 |        0 |
| black              |   1,273 |     163 |     403 |        0 |
| fastapi            |     742 |      65 |     420 |        0 |
| cattrs             |     520 |      37 |     380 |        0 |
| pytest             |   3,003 |     285 |   1,360 |        0 |
| botocore           |   3,786 |     608 |   2,635 |        0 |
| uvicorn            |     489 |      44 |     214 |        0 |
| mcp                |   1,720 |     236 |     790 |        0 |
| textual            |   6,483 |     741 |   3,035 |        0 |
| pdm                |   2,718 |     321 |   1,250 |        0 |
| strawberry-graphql |   1,806 |     218 |     977 |        0 |
| pygments           |   7,666 |     228 |   6,703 |        0 |
| streamlink         |   3,029 |     250 |   2,097 |        0 |
| sphinx             |   7,972 |     821 |   4,024 |        0 |
| tox                |   1,762 |     138 |     681 |        0 |
| pint               |   3,078 |     154 |   2,307 |        0 |
| altair             |   1,700 |      60 |   1,262 |        0 |
| seaborn            |   2,895 |     228 |   2,028 |        0 |
| aiohttp            |   1,857 |     252 |     904 |        0 |
| websockets         |     791 |     111 |     352 |        0 |
| anyio              |     715 |      61 |     442 |        0 |
| zarr               |   2,411 |     109 |   1,218 |        0 |
| joblib             |   2,239 |     267 |   1,447 |        0 |
| networkx           |  22,456 |   2,389 |  16,098 |        0 |
| nibabel            |   8,468 |     957 |   5,662 |        0 |
| narwhals           |   3,120 |     119 |   2,019 |        0 |
| xarray             |  21,344 |   3,338 |  14,449 |        0 |
| litestar           |   1,905 |     161 |   1,137 |        0 |
| stripe             |   3,357 |     664 |   2,124 |        0 |
| celery             |   3,748 |     360 |   2,880 |        0 |
| optuna             |   3,598 |     296 |   1,826 |        0 |
| dask               |  24,172 |   2,578 |  18,474 |        0 |
| mypy               |  11,401 |   1,552 |   5,087 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library   |    4 |        51.2 |     21.13 |    1 |                       821.5 |     857.3 | hyperfine |
| django             |    4 |       10.05 |      3.89 |    1 |                       151.2 |     161.0 | hyperfine |
| sqlalchemy         |    4 |        8.38 |      3.82 |    1 |                       123.1 |     129.1 | hyperfine |
| pydantic           |    4 |        1.77 |      0.79 |    1 |                        26.9 |      29.2 | hyperfine |
| pandas             |    4 |       57.04 |     18.56 |    1 |                       881.7 |     905.0 | hyperfine |
| twisted            |    4 |        7.34 |      2.84 |    1 |                       113.3 |     121.1 | hyperfine |
| pip                |    4 |        4.98 |      2.03 |    1 |                        80.9 |      85.9 | hyperfine |
| structlog          |    4 |        0.26 |      0.24 |    1 |                         3.4 |       4.5 | hyperfine |
| attrs              |    4 |        0.23 |      0.29 |    1 |                         3.1 |       4.2 | hyperfine |
| click              |    4 |        0.44 |      0.34 |    1 |                         6.5 |       7.5 | hyperfine |
| hypercorn          |    4 |        0.36 |      0.25 |    1 |                         4.5 |       5.8 | hyperfine |
| starlette          |    4 |        0.46 |      0.32 |    1 |                         6.0 |       7.3 | hyperfine |
| werkzeug           |    4 |        0.81 |      0.41 |    1 |                        11.5 |      12.8 | hyperfine |
| mkdocs             |    4 |        0.93 |      0.56 |    1 |                        13.6 |      15.7 | hyperfine |
| httpx              |    4 |        0.37 |      0.26 |    1 |                         5.0 |       6.2 | hyperfine |
| black              |    4 |        0.57 |      0.31 |    1 |                         8.5 |       9.7 | hyperfine |
| fastapi            |    4 |        0.63 |      0.52 |    1 |                         9.4 |      11.0 | hyperfine |
| cattrs             |    4 |        0.38 |      0.33 |    1 |                         5.3 |       6.7 | hyperfine |
| pytest             |    4 |        1.51 |      0.84 |    1 |                        22.3 |      24.3 | hyperfine |
| botocore           |    4 |        2.03 |      0.86 |    1 |                        30.4 |      32.3 | hyperfine |
| uvicorn            |    4 |        0.46 |      0.29 |    1 |                         6.2 |       7.5 | hyperfine |
| mcp                |    4 |        1.13 |      0.58 |    1 |                        15.8 |      18.0 | hyperfine |
| textual            |    4 |        2.83 |      1.18 |    1 |                        42.5 |      46.1 | hyperfine |
| pdm                |    4 |        1.59 |      0.82 |    1 |                        22.6 |      25.7 | hyperfine |
| strawberry-graphql |    4 |        1.63 |      0.74 |    1 |                        22.7 |      26.0 | hyperfine |
| pygments           |    4 |        2.88 |      1.14 |    1 |                        52.3 |      55.4 | hyperfine |
| streamlink         |    4 |         2.2 |       0.9 |    1 |                        32.6 |      35.0 | hyperfine |
| sphinx             |    4 |        4.09 |      1.38 |    1 |                        62.0 |      63.4 | hyperfine |
| tox                |    4 |        1.11 |      0.48 |    1 |                        15.2 |      16.3 | hyperfine |
| pint               |    4 |        1.71 |      1.05 |    1 |                        26.7 |      31.2 | hyperfine |
| altair             |    4 |        1.95 |      1.54 |    1 |                        33.6 |      39.4 | hyperfine |
| seaborn            |    4 |        2.08 |      1.22 |    1 |                        32.8 |      39.7 | hyperfine |
| aiohttp            |    4 |         1.3 |      0.62 |    1 |                        19.3 |      20.8 | hyperfine |
| websockets         |    4 |        0.64 |      0.34 |    1 |                         9.0 |      10.5 | hyperfine |
| anyio              |    4 |        0.67 |      0.44 |    1 |                         9.7 |      11.0 | hyperfine |
| zarr               |    4 |        1.59 |      0.71 |    1 |                        24.0 |      27.1 | hyperfine |
| joblib             |    4 |        1.28 |      0.85 |    1 |                        19.0 |      22.3 | hyperfine |
| networkx           |    4 |        8.62 |      3.32 |    1 |                       139.1 |     145.3 | hyperfine |
| nibabel            |    4 |        4.74 |      2.15 |    1 |                        70.6 |      80.7 | hyperfine |
| narwhals           |    4 |        2.36 |      1.02 |    1 |                        36.4 |      41.5 | hyperfine |
| xarray             |    4 |       16.11 |      8.13 |    1 |                       279.1 |     295.2 | hyperfine |
| litestar           |    4 |        2.21 |       1.0 |    1 |                        30.2 |      34.0 | hyperfine |
| stripe             |    4 |        7.63 |      2.64 |    1 |                       128.4 |     134.5 | hyperfine |
| celery             |    4 |        2.56 |      1.57 |    1 |                        38.0 |      44.7 | hyperfine |
| optuna             |    4 |        3.46 |      1.81 |    1 |                        53.1 |      59.2 | hyperfine |
| dask               |    4 |       20.66 |     10.03 |    1 |                       393.6 |     411.7 | hyperfine |
| mypy               |    4 |        5.97 |      1.92 |    1 |                        93.6 |      95.8 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |   told |   held | differed | resting on the trace |                                                                            tests | seconds | untraced |
| ------------------ | ------- | -----: | -----: | -------: | -------------------: | -------------------------------------------------------------------------------: | ------: | -------: |
| django             |         |        |        |          |                  467 |          Ran 17585 tests: FAILED (failures=5, skipped=1129, expected failures=5) |   590.7 |     63.6 |
| django             | certain |    921 |    920 |        1 |                      |                                                                                  |         |          |
| django             | likely  |    307 |    306 |        1 |                      |                                                                                  |         |          |
| django             | guess   |    356 |    340 |       16 |                      |                                                                                  |         |          |
| sqlalchemy         |         |        |        |          |                  140 |                                             29523 passed, 973 skipped, 1 warning |   142.4 |    124.2 |
| sqlalchemy         | certain |  1,073 |  1,054 |       19 |                      |                                                                                  |         |          |
| sqlalchemy         | likely  |    160 |    157 |        3 |                      |                                                                                  |         |          |
| sqlalchemy         | guess   |    114 |    112 |        2 |                      |                                                                                  |         |          |
| pydantic           |         |        |        |          |                    1 |                                  65 failed, 6900 passed, 350 skipped, 29 xfailed |    49.5 |     53.7 |
| pydantic           | certain |    522 |    517 |        5 |                      |                                                                                  |         |          |
| pydantic           | likely  |     47 |     47 |        0 |                      |                                                                                  |         |          |
| pydantic           | guess   |     31 |     31 |        0 |                      |                                                                                  |         |          |
| pandas             |         |        |        |          |                1,418 |                            165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   139.1 |     98.5 |
| pandas             | certain | 12,884 | 12,807 |       77 |                      |                                                                                  |         |          |
| pandas             | likely  | 19,915 | 19,849 |       66 |                      |                                                                                  |         |          |
| pandas             | guess   |    798 |    752 |       46 |                      |                                                                                  |         |          |
| structlog          |         |        |        |          |                    0 |                                    24 failed, 860 passed, 37 skipped, 2 warnings |     2.3 |      2.2 |
| structlog          | certain |     62 |     62 |        0 |                      |                                                                                  |         |          |
| structlog          | likely  |      6 |      6 |        0 |                      |                                                                                  |         |          |
| structlog          | guess   |      6 |      6 |        0 |                      |                                                                                  |         |          |
| attrs              |         |        |        |          |                    2 |                                      1 failed, 1382 passed, 2 skipped, 2 xfailed |     4.1 |      4.6 |
| attrs              | certain |     72 |     72 |        0 |                      |                                                                                  |         |          |
| attrs              | likely  |      8 |      8 |        0 |                      |                                                                                  |         |          |
| attrs              | guess   |      1 |      1 |        0 |                      |                                                                                  |         |          |
| click              |         |        |        |          |                    0 |                             1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     6.0 |      7.0 |
| click              | certain |    222 |    222 |        0 |                      |                                                                                  |         |          |
| click              | likely  |     19 |     18 |        1 |                      |                                                                                  |         |          |
| click              | guess   |     25 |     25 |        0 |                      |                                                                                  |         |          |
| hypercorn          |         |        |        |          |                    0 |                                                             2 failed, 194 passed |     7.5 |      7.2 |
| hypercorn          | certain |     63 |     63 |        0 |                      |                                                                                  |         |          |
| hypercorn          | likely  |     12 |     12 |        0 |                      |                                                                                  |         |          |
| hypercorn          | guess   |     10 |     10 |        0 |                      |                                                                                  |         |          |
| starlette          |         |        |        |          |                    0 |                                                1271 passed, 2 skipped, 2 xfailed |     9.8 |     10.3 |
| starlette          | certain |    193 |    192 |        1 |                      |                                                                                  |         |          |
| starlette          | likely  |     47 |     47 |        0 |                      |                                                                                  |         |          |
| starlette          | guess   |     29 |     29 |        0 |                      |                                                                                  |         |          |
| werkzeug           |         |        |        |          |                    0 |                                       1 failed, 979 passed, 1 skipped, 1 warning |     9.2 |      9.1 |
| werkzeug           | certain |    354 |    350 |        4 |                      |                                                                                  |         |          |
| werkzeug           | likely  |     44 |     44 |        0 |                      |                                                                                  |         |          |
| werkzeug           | guess   |     33 |     33 |        0 |                      |                                                                                  |         |          |
| mkdocs             |         |        |        |          |                   12 |                          Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    10.9 |     10.6 |
| mkdocs             | certain |    628 |    627 |        1 |                      |                                                                                  |         |          |
| mkdocs             | likely  |    322 |    322 |        0 |                      |                                                                                  |         |          |
| mkdocs             | guess   |    116 |    116 |        0 |                      |                                                                                  |         |          |
| httpx              |         |        |        |          |                    0 |                                                 1 failed, 1416 passed, 1 skipped |     8.5 |      7.7 |
| httpx              | certain |    181 |    181 |        0 |                      |                                                                                  |         |          |
| httpx              | likely  |     41 |     41 |        0 |                      |                                                                                  |         |          |
| httpx              | guess   |     16 |     16 |        0 |                      |                                                                                  |         |          |
| black              |         |        |        |          |                    0 |                                         519 passed, 1 skipped, 9 subtests passed |     8.4 |      6.7 |
| black              | certain |    597 |    597 |        0 |                      |                                                                                  |         |          |
| black              | likely  |    102 |    102 |        0 |                      |                                                                                  |         |          |
| black              | guess   |     39 |     39 |        0 |                      |                                                                                  |         |          |
| fastapi            |         |        |        |          |                    0 |                                               3551 passed, 17 skipped, 4 xfailed |    16.8 |     14.7 |
| fastapi            | certain |    215 |    215 |        0 |                      |                                                                                  |         |          |
| fastapi            | likely  |     28 |     28 |        0 |                      |                                                                                  |         |          |
| fastapi            | guess   |     22 |     22 |        0 |                      |                                                                                  |         |          |
| cattrs             |         |        |        |          |                    0 |                                                           994 passed, 15 xfailed |    25.0 |     18.0 |
| cattrs             | certain |     99 |     97 |        2 |                      |                                                                                  |         |          |
| cattrs             | likely  |     23 |     23 |        0 |                      |                                                                                  |         |          |
| cattrs             | guess   |     13 |     13 |        0 |                      |                                                                                  |         |          |
| pytest             |         |        |        |          |                   14 |              46 failed, 4059 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    40.4 |     21.3 |
| pytest             | certain |  1,086 |  1,073 |       13 |                      |                                                                                  |         |          |
| pytest             | likely  |    120 |    120 |        0 |                      |                                                                                  |         |          |
| pytest             | guess   |    100 |    100 |        0 |                      |                                                                                  |         |          |
| botocore           |         |        |        |          |                  299 |                                                7 failed, 4593 passed, 96 skipped |    29.9 |     29.5 |
| botocore           | certain |    326 |    325 |        1 |                      |                                                                                  |         |          |
| botocore           | likely  |    138 |    138 |        0 |                      |                                                                                  |         |          |
| botocore           | guess   |    102 |    101 |        1 |                      |                                                                                  |         |          |
| uvicorn            |         |        |        |          |                    0 |                                                          1350 passed, 12 skipped |    29.0 |     29.5 |
| uvicorn            | certain |    168 |    164 |        4 |                      |                                                                                  |         |          |
| uvicorn            | likely  |     27 |     27 |        0 |                      |                                                                                  |         |          |
| uvicorn            | guess   |      8 |      8 |        0 |                      |                                                                                  |         |          |
| mcp                |         |        |        |          |                    0 |                                      3 failed, 6092 passed, 8 skipped, 1 xfailed |    17.2 |     15.2 |
| mcp                | certain |    511 |    511 |        0 |                      |                                                                                  |         |          |
| mcp                | likely  |    128 |    127 |        1 |                      |                                                                                  |         |          |
| mcp                | guess   |     56 |     56 |        0 |                      |                                                                                  |         |          |
| pdm                |         |        |        |          |                    0 |                                              1472 passed, 1 skipped, 60 warnings |    25.9 |     15.0 |
| pdm                | certain |    867 |    863 |        4 |                      |                                                                                  |         |          |
| pdm                | likely  |    125 |    125 |        0 |                      |                                                                                  |         |          |
| pdm                | guess   |     77 |     77 |        0 |                      |                                                                                  |         |          |
| strawberry-graphql |         |        |        |          |                    0 |          51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    14.2 |     15.1 |
| strawberry-graphql | certain |    390 |    384 |        6 |                      |                                                                                  |         |          |
| strawberry-graphql | likely  |     95 |     94 |        1 |                      |                                                                                  |         |          |
| strawberry-graphql | guess   |     28 |     28 |        0 |                      |                                                                                  |         |          |
| pygments           |         |        |        |          |                   87 |                                                1 failed, 5330 passed, 15 skipped |    31.9 |     14.6 |
| pygments           | certain |    289 |    289 |        0 |                      |                                                                                  |         |          |
| pygments           | likely  |     58 |     58 |        0 |                      |                                                                                  |         |          |
| pygments           | guess   |     60 |     60 |        0 |                      |                                                                                  |         |          |
| streamlink         |         |        |        |          |                    8 |                         15 failed, 7233 passed, 36 skipped, 2 warnings, 9 errors |    23.7 |     12.4 |
| streamlink         | certain |    274 |    273 |        1 |                      |                                                                                  |         |          |
| streamlink         | likely  |     38 |     38 |        0 |                      |                                                                                  |         |          |
| streamlink         | guess   |     37 |     37 |        0 |                      |                                                                                  |         |          |
| sphinx             |         |        |        |          |                    0 |                                  10 failed, 2392 passed, 22 skipped, 35 warnings |    24.0 |     16.6 |
| sphinx             | certain |  1,983 |  1,957 |       26 |                      |                                                                                  |         |          |
| sphinx             | likely  |    347 |    347 |        0 |                      |                                                                                  |         |          |
| sphinx             | guess   |    193 |    191 |        2 |                      |                                                                                  |         |          |
| tox                |         |        |        |          |                    0 |                                     17 failed, 8525 passed, 31 skipped, 6 errors |    21.1 |     18.2 |
| tox                | certain |    710 |    707 |        3 |                      |                                                                                  |         |          |
| tox                | likely  |     62 |     62 |        0 |                      |                                                                                  |         |          |
| tox                | guess   |     29 |     28 |        1 |                      |                                                                                  |         |          |
| pint               |         |        |        |          |                    3 | 1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    33.3 |     28.2 |
| pint               | certain |    216 |    213 |        3 |                      |                                                                                  |         |          |
| pint               | likely  |     12 |     12 |        0 |                      |                                                                                  |         |          |
| pint               | guess   |     23 |     21 |        2 |                      |                                                                                  |         |          |
| altair             |         |        |        |          |                    6 |            28 failed, 1866 passed, 12 skipped, 7 xfailed, 3 xpassed, 89 warnings |    25.7 |     21.9 |
| altair             | certain |    199 |    198 |        1 |                      |                                                                                  |         |          |
| altair             | likely  |     33 |     33 |        0 |                      |                                                                                  |         |          |
| altair             | guess   |      6 |      5 |        1 |                      |                                                                                  |         |          |
| seaborn            |         |        |        |          |                   33 |            20 failed, 2178 passed, 11 skipped, 6 xfailed, 958 warnings, 8 errors |    66.7 |     54.4 |
| seaborn            | certain |    486 |    484 |        2 |                      |                                                                                  |         |          |
| seaborn            | likely  |    116 |    115 |        1 |                      |                                                                                  |         |          |
| seaborn            | guess   |     51 |     48 |        3 |                      |                                                                                  |         |          |
| aiohttp            |         |        |        |          |                    0 |                 3 failed, 4840 passed, 535 skipped, 2 xfailed, 4 subtests passed |    91.3 |     78.7 |
| aiohttp            | certain |    516 |    498 |       18 |                      |                                                                                  |         |          |
| aiohttp            | likely  |    107 |    106 |        1 |                      |                                                                                  |         |          |
| aiohttp            | guess   |     77 |     72 |        5 |                      |                                                                                  |         |          |
| websockets         |         |        |        |          |                    0 |                                                   Ran 2589 tests: OK (skipped=8) |    32.4 |     26.7 |
| websockets         | certain |    238 |    237 |        1 |                      |                                                                                  |         |          |
| websockets         | likely  |     52 |     52 |        0 |                      |                                                                                  |         |          |
| websockets         | guess   |     33 |     33 |        0 |                      |                                                                                  |         |          |
| anyio              |         |        |        |          |                    0 |                               3824 passed, 19 skipped, 388 deselected, 5 xfailed |   126.5 |    124.5 |
| anyio              | certain |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | likely  |      0 |      0 |        0 |                      |                                                                                  |         |          |
| anyio              | guess   |      0 |      0 |        0 |                      |                                                                                  |         |          |
| zarr               |         |        |        |          |                    0 |                                             8422 passed, 1205 skipped, 4 xfailed |    99.9 |    106.0 |
| zarr               | certain |    731 |    721 |       10 |                      |                                                                                  |         |          |
| zarr               | likely  |     46 |     46 |        0 |                      |                                                                                  |         |          |
| zarr               | guess   |     23 |     21 |        2 |                      |                                                                                  |         |          |
| joblib             |         |        |        |          |                    9 |                       10 failed, 1482 passed, 45 skipped, 4 xpassed, 85 warnings |   151.8 |    157.1 |
| joblib             | certain |    126 |    126 |        0 |                      |                                                                                  |         |          |
| joblib             | likely  |     16 |     16 |        0 |                      |                                                                                  |         |          |
| joblib             | guess   |     25 |     25 |        0 |                      |                                                                                  |         |          |
| networkx           |         |        |        |          |                  359 |                                            10083 passed, 62 skipped, 741 xfailed |    26.1 |     26.5 |
| networkx           | certain |    928 |    927 |        1 |                      |                                                                                  |         |          |
| networkx           | likely  |    176 |    175 |        1 |                      |                                                                                  |         |          |
| networkx           | guess   |    105 |    102 |        3 |                      |                                                                                  |         |          |
| nibabel            |         |        |        |          |                   71 |                      110 failed, 5166 passed, 304 skipped, 40 xfailed, 20 errors |    17.8 |     14.9 |
| nibabel            | certain |    407 |    404 |        3 |                      |                                                                                  |         |          |
| nibabel            | likely  |    126 |    126 |        0 |                      |                                                                                  |         |          |
| nibabel            | guess   |     89 |     88 |        1 |                      |                                                                                  |         |          |
| narwhals           |         |        |        |          |                    0 |                               972 failed, 11116 passed, 235 skipped, 699 xfailed |    49.5 |     31.6 |
| narwhals           | certain |    511 |    509 |        2 |                      |                                                                                  |         |          |
| narwhals           | likely  |     45 |     45 |        0 |                      |                                                                                  |         |          |
| narwhals           | guess   |     22 |     22 |        0 |                      |                                                                                  |         |          |
| xarray             |         |        |        |          |                   20 |  3 failed, 6333 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    19.0 |     17.1 |
| xarray             | certain |    825 |    819 |        6 |                      |                                                                                  |         |          |
| xarray             | likely  |    116 |    116 |        0 |                      |                                                                                  |         |          |
| xarray             | guess   |     54 |     54 |        0 |                      |                                                                                  |         |          |
| litestar           |         |        |        |          |                    0 |  6 failed, 5645 passed, 256 skipped, 13 xfailed, 30 xpassed, 3 warnings, 1 rerun |    33.5 |     22.5 |
| litestar           | certain |    461 |    460 |        1 |                      |                                                                                  |         |          |
| litestar           | likely  |     86 |     86 |        0 |                      |                                                                                  |         |          |
| litestar           | guess   |     39 |     38 |        1 |                      |                                                                                  |         |          |
| celery             |         |        |        |          |                   64 |                                     3 failed, 3521 passed, 36 skipped, 3 xfailed |   171.4 |     58.0 |
| celery             | certain |    218 |    215 |        3 |                      |                                                                                  |         |          |
| celery             | likely  |     35 |     34 |        1 |                      |                                                                                  |         |          |
| celery             | guess   |     30 |     26 |        4 |                      |                                                                                  |         |          |
| optuna             |         |        |        |          |                    0 |                     263 failed, 4203 passed, 43 skipped, 318 warnings, 16 errors |   131.2 |    225.0 |
| optuna             | certain |    622 |    622 |        0 |                      |                                                                                  |         |          |
| optuna             | likely  |    104 |    104 |        0 |                      |                                                                                  |         |          |
| optuna             | guess   |     48 |     48 |        0 |                      |                                                                                  |         |          |
| dask               |         |        |        |          |                  117 |         5 failed, 16196 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   145.9 |    166.8 |
| dask               | certain |  1,065 |  1,059 |        6 |                      |                                                                                  |         |          |
| dask               | likely  |    168 |    167 |        1 |                      |                                                                                  |         |          |
| dask               | guess   |    109 |    106 |        3 |                      |                                                                                  |         |          |
| mypy               |         |        |        |          |                    0 |                        14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   335.2 |    371.4 |
| mypy               | certain |  3,045 |  3,045 |        0 |                      |                                                                                  |         |          |
| mypy               | likely  |    695 |    695 |        0 |                      |                                                                                  |         |          |
| mypy               | guess   |    239 |    239 |        0 |                      |                                                                                  |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                | same as released | summary                                                               | new failures | gone | named |
| ------------------ | ------------------ | ---------------- | --------------------------------------------------------------------- | -----------: | ---: | ----: |
| django             | released           |                  | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            |              |      |       |
| django             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| django             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| django             | fix-unsafe         | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-basedpyright | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-pyrefly      | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-trace        | True             | 5 expected failures, 2 failures, 17,585 ran, 1,129 skipped            |            0 |    0 |     0 |
| django             | infer-ty           | True             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            |            0 |    0 |     0 |
| sqlalchemy         | released           |                  | 29,521 passed, 975 skipped                                            |              |      |       |
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
| sphinx             | released           |                  | 9 failed, 2,393 passed, 22 skipped                                    |              |      |       |
| sphinx             | fix-certain        | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| sphinx             | fix-likely         | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| sphinx             | fix-unsafe         | True             | as infer-trace's (implied)                                            |            0 |    0 |     0 |
| sphinx             | infer-basedpyright | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-pyrefly      | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-trace        | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-ty           | True             | 10 failed, 2,392 passed, 22 skipped                                   |            0 |    0 |     0 |
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
| nibabel            | released           |                  | 19 error, 109 failed, 5,168 passed, 304 skipped, 40 xfailed           |              |      |       |
| nibabel            | fix-certain        | True             | 20 error, 108 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-likely         | True             | 21 error, 107 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-unsafe         | True             | 19 error, 109 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-basedpyright | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-pyrefly      | True             | 20 error, 108 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-trace        | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-ty           | True             | 19 error, 108 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
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
| litestar           | fix-certain        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | fix-likely         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | fix-unsafe         | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | infer-basedpyright | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | infer-pyrefly      | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | infer-trace        | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
| litestar           | infer-ty           | True             | as infer-union's (implied)                                            |            0 |    0 |     0 |
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
| sqlalchemy         | fix-certain        |      0 |   0 |    0 |    198 files changed, 2873 insertions(+), 2385 deletions(-) |
| sqlalchemy         | fix-likely         |      0 |   0 |    0 |    187 files changed, 2368 insertions(+), 1920 deletions(-) |
| sqlalchemy         | fix-unsafe         |      0 |   0 |    0 |    198 files changed, 2873 insertions(+), 2385 deletions(-) |
| sqlalchemy         | infer-basedpyright |      3 |   3 |    0 |    204 files changed, 3659 insertions(+), 3122 deletions(-) |
| sqlalchemy         | infer-pyrefly      |      1 |   1 |    0 |    203 files changed, 3359 insertions(+), 2704 deletions(-) |
| sqlalchemy         | infer-trace        |      6 |   6 |    0 |    200 files changed, 3051 insertions(+), 2513 deletions(-) |
| sqlalchemy         | infer-ty           |      2 |   2 |    0 |    205 files changed, 3622 insertions(+), 2973 deletions(-) |
| pydantic           | released           |      0 |     |      |                                                             |
| pydantic           | fix-certain        |      0 |   0 |    0 |     79 files changed, 1670 insertions(+), 1271 deletions(-) |
| pydantic           | fix-likely         |      0 |   0 |    0 |     79 files changed, 1670 insertions(+), 1271 deletions(-) |
| pydantic           | fix-unsafe         |      0 |   0 |    0 |     79 files changed, 1670 insertions(+), 1271 deletions(-) |
| pydantic           | infer-basedpyright |      0 |   0 |    0 |     79 files changed, 1904 insertions(+), 1492 deletions(-) |
| pydantic           | infer-pyrefly      |      0 |   0 |    0 |     79 files changed, 1936 insertions(+), 1408 deletions(-) |
| pydantic           | infer-trace        |      0 |   0 |    0 |     79 files changed, 1670 insertions(+), 1271 deletions(-) |
| pydantic           | infer-ty           |      3 |   3 |    0 |     79 files changed, 1810 insertions(+), 1401 deletions(-) |
| pandas             | released           |    259 |     |      |                                                             |
| pandas             | fix-certain        |    259 |   0 |    0 | 1069 files changed, 18260 insertions(+), 15201 deletions(-) |
| pandas             | fix-likely         |    259 |   0 |    0 | 1201 files changed, 42120 insertions(+), 38443 deletions(-) |
| pandas             | fix-unsafe         |    261 |   2 |    0 | 1204 files changed, 42944 insertions(+), 39147 deletions(-) |
| pandas             | infer-basedpyright |    300 |  41 |    0 | 1213 files changed, 49130 insertions(+), 44752 deletions(-) |
| pandas             | infer-pyrefly      |    314 |  55 |    0 | 1210 files changed, 50218 insertions(+), 45503 deletions(-) |
| pandas             | infer-trace        |    262 |   3 |    0 | 1207 files changed, 44385 insertions(+), 40506 deletions(-) |
| pandas             | infer-ty           |    266 |   7 |    0 | 1215 files changed, 48887 insertions(+), 44476 deletions(-) |
| structlog          | released           |      8 |     |      |                                                             |
| structlog          | fix-certain        |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-pyrefly      |      8 |   0 |    0 |       16 files changed, 161 insertions(+), 118 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |       16 files changed, 167 insertions(+), 131 deletions(-) |
| click              | released           |      0 |     |      |                                                             |
| click              | fix-certain        |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |       15 files changed, 443 insertions(+), 349 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |       15 files changed, 449 insertions(+), 350 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |       15 files changed, 370 insertions(+), 285 deletions(-) |
| click              | infer-ty           |      0 |   0 |    0 |       15 files changed, 461 insertions(+), 361 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                             |
| hypercorn          | fix-certain        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |       25 files changed, 236 insertions(+), 166 deletions(-) |
| hypercorn          | infer-pyrefly      |     12 |   0 |    0 |       25 files changed, 219 insertions(+), 150 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |       25 files changed, 209 insertions(+), 145 deletions(-) |
| hypercorn          | infer-ty           |     12 |   0 |    0 |       25 files changed, 240 insertions(+), 164 deletions(-) |
| starlette          | released           |      0 |     |      |                                                             |
| starlette          | fix-certain        |      0 |   0 |    0 |       33 files changed, 432 insertions(+), 332 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |       33 files changed, 432 insertions(+), 332 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |       33 files changed, 432 insertions(+), 332 deletions(-) |
| starlette          | infer-basedpyright |      0 |   0 |    0 |       33 files changed, 523 insertions(+), 403 deletions(-) |
| starlette          | infer-pyrefly      |      0 |   0 |    0 |       33 files changed, 471 insertions(+), 361 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |       33 files changed, 432 insertions(+), 332 deletions(-) |
| starlette          | infer-ty           |      0 |   0 |    0 |       33 files changed, 504 insertions(+), 386 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                             |
| werkzeug           | fix-certain        |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |       45 files changed, 802 insertions(+), 568 deletions(-) |
| werkzeug           | infer-pyrefly      |      0 |   0 |    0 |       45 files changed, 832 insertions(+), 561 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |       43 files changed, 672 insertions(+), 463 deletions(-) |
| werkzeug           | infer-ty           |      0 |   0 |    0 |       45 files changed, 828 insertions(+), 575 deletions(-) |
| httpx              | released           |      0 |     |      |                                                             |
| httpx              | fix-certain        |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |       17 files changed, 399 insertions(+), 330 deletions(-) |
| httpx              | infer-pyrefly      |      1 |   1 |    0 |       16 files changed, 356 insertions(+), 284 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |       16 files changed, 308 insertions(+), 253 deletions(-) |
| httpx              | infer-ty           |      1 |   1 |    0 |       17 files changed, 383 insertions(+), 306 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                             |
| uvicorn            | fix-certain        |      0 |   0 |    0 |       27 files changed, 295 insertions(+), 216 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |       27 files changed, 295 insertions(+), 216 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |       27 files changed, 295 insertions(+), 216 deletions(-) |
| uvicorn            | infer-basedpyright |      7 |   7 |    0 |       29 files changed, 371 insertions(+), 282 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |       28 files changed, 323 insertions(+), 232 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |       27 files changed, 295 insertions(+), 216 deletions(-) |
| uvicorn            | infer-ty           |      2 |   2 |    0 |       29 files changed, 351 insertions(+), 265 deletions(-) |
| mcp                | released           |      0 |     |      |                                                             |
| mcp                | fix-certain        |      0 |   0 |    0 |       80 files changed, 780 insertions(+), 520 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |       80 files changed, 938 insertions(+), 666 deletions(-) |
| mcp                | fix-unsafe         |      1 |   1 |    0 |      81 files changed, 1031 insertions(+), 737 deletions(-) |
| mcp                | infer-basedpyright |      3 |   3 |    0 |      82 files changed, 1152 insertions(+), 851 deletions(-) |
| mcp                | infer-pyrefly      |      1 |   1 |    0 |      82 files changed, 1117 insertions(+), 805 deletions(-) |
| mcp                | infer-trace        |      1 |   1 |    0 |      81 files changed, 1031 insertions(+), 737 deletions(-) |
| mcp                | infer-ty           |      1 |   1 |    0 |      82 files changed, 1157 insertions(+), 825 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                             |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | infer-basedpyright |     13 |   3 |    0 |     155 files changed, 1101 insertions(+), 840 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     11 |   1 |    0 |      153 files changed, 979 insertions(+), 733 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |      151 files changed, 922 insertions(+), 684 deletions(-) |
| strawberry-graphql | infer-ty           |     11 |   1 |    0 |     155 files changed, 1098 insertions(+), 833 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                             |
| streamlink         | fix-certain        |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | infer-basedpyright |      0 |   0 |    0 |    186 files changed, 1753 insertions(+), 1133 deletions(-) |
| streamlink         | infer-pyrefly      |      0 |   0 |    0 |     173 files changed, 1494 insertions(+), 902 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |     170 files changed, 1314 insertions(+), 767 deletions(-) |
| streamlink         | infer-ty           |     24 |  24 |    0 |    186 files changed, 2008 insertions(+), 1133 deletions(-) |
| sphinx             | released           |      3 |     |      |                                                             |
| sphinx             | fix-certain        |      4 |   1 |    0 |    194 files changed, 3199 insertions(+), 2156 deletions(-) |
| sphinx             | fix-likely         |      4 |   1 |    0 |    197 files changed, 3649 insertions(+), 2507 deletions(-) |
| sphinx             | fix-unsafe         |      4 |   1 |    0 |    212 files changed, 4037 insertions(+), 2831 deletions(-) |
| sphinx             | infer-basedpyright |      8 |   5 |    0 |    215 files changed, 4842 insertions(+), 3573 deletions(-) |
| sphinx             | infer-pyrefly      |     13 |  10 |    0 |    216 files changed, 5201 insertions(+), 3699 deletions(-) |
| sphinx             | infer-trace        |      4 |   1 |    0 |    212 files changed, 4037 insertions(+), 2831 deletions(-) |
| sphinx             | infer-ty           |      6 |   3 |    0 |    215 files changed, 4905 insertions(+), 3550 deletions(-) |
| pint               | released           |    659 |     |      |                                                             |
| pint               | fix-certain        |    659 |   0 |    0 |       75 files changed, 817 insertions(+), 555 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |       75 files changed, 817 insertions(+), 555 deletions(-) |
| pint               | fix-unsafe         |    659 |   0 |    0 |       75 files changed, 817 insertions(+), 555 deletions(-) |
| pint               | infer-basedpyright |    660 |   1 |    0 |      79 files changed, 1079 insertions(+), 747 deletions(-) |
| pint               | infer-pyrefly      |    664 |   5 |    0 |       76 files changed, 866 insertions(+), 583 deletions(-) |
| pint               | infer-trace        |    659 |   0 |    0 |       75 files changed, 817 insertions(+), 555 deletions(-) |
| pint               | infer-ty           |    660 |   2 |    1 |       78 files changed, 956 insertions(+), 659 deletions(-) |
| altair             | released           |      1 |     |      |                                                             |
| altair             | fix-certain        |      1 |   0 |    0 |       40 files changed, 462 insertions(+), 366 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |       40 files changed, 462 insertions(+), 366 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |       40 files changed, 462 insertions(+), 366 deletions(-) |
| altair             | infer-basedpyright |      4 |   3 |    0 |       40 files changed, 549 insertions(+), 433 deletions(-) |
| altair             | infer-pyrefly      |      4 |   3 |    0 |       40 files changed, 526 insertions(+), 409 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |       40 files changed, 472 insertions(+), 373 deletions(-) |
| altair             | infer-ty           |      4 |   3 |    0 |       40 files changed, 548 insertions(+), 429 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                             |
| seaborn            | fix-certain        |     39 |   0 |    0 |      46 files changed, 1018 insertions(+), 809 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |      46 files changed, 1018 insertions(+), 809 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |      46 files changed, 1018 insertions(+), 809 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |      46 files changed, 1018 insertions(+), 809 deletions(-) |
| seaborn            | infer-pyrefly      |     39 |   0 |    0 |      47 files changed, 1078 insertions(+), 835 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |       46 files changed, 957 insertions(+), 730 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |       46 files changed, 989 insertions(+), 780 deletions(-) |
| websockets         | released           |      0 |     |      |                                                             |
| websockets         | fix-certain        |      0 |   0 |    0 |       39 files changed, 341 insertions(+), 235 deletions(-) |
| websockets         | fix-likely         |      1 |   1 |    0 |       39 files changed, 402 insertions(+), 294 deletions(-) |
| websockets         | fix-unsafe         |      1 |   1 |    0 |       39 files changed, 455 insertions(+), 331 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |       40 files changed, 564 insertions(+), 438 deletions(-) |
| websockets         | infer-pyrefly      |      4 |   4 |    0 |       40 files changed, 611 insertions(+), 448 deletions(-) |
| websockets         | infer-trace        |      1 |   1 |    0 |       39 files changed, 455 insertions(+), 331 deletions(-) |
| websockets         | infer-ty           |      4 |   4 |    0 |       40 files changed, 581 insertions(+), 439 deletions(-) |
| networkx           | released           |      0 |     |      |                                                             |
| networkx           | fix-certain        |      0 |   0 |    0 |    475 files changed, 6963 insertions(+), 5799 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 |    458 files changed, 6207 insertions(+), 5280 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 |    475 files changed, 6963 insertions(+), 5799 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 |    475 files changed, 7783 insertions(+), 6472 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 |    471 files changed, 7057 insertions(+), 5909 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 |    475 files changed, 6963 insertions(+), 5799 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 |    465 files changed, 7013 insertions(+), 5906 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                             |
| nibabel            | fix-certain        |     12 |   0 |    0 |    181 files changed, 2054 insertions(+), 1368 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 |    191 files changed, 2759 insertions(+), 1985 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 |    197 files changed, 3057 insertions(+), 2228 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 |    202 files changed, 3787 insertions(+), 2836 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 |    202 files changed, 3505 insertions(+), 2529 deletions(-) |
| nibabel            | infer-trace        |     15 |   3 |    0 |    197 files changed, 3161 insertions(+), 2296 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 |    199 files changed, 3718 insertions(+), 2763 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                             |
| narwhals           | fix-certain        |     23 |   4 |    0 |      96 files changed, 1019 insertions(+), 841 deletions(-) |
| narwhals           | fix-likely         |     23 |   4 |    0 |      96 files changed, 1088 insertions(+), 907 deletions(-) |
| narwhals           | fix-unsafe         |     24 |   5 |    0 |      97 files changed, 1147 insertions(+), 949 deletions(-) |
| narwhals           | infer-basedpyright |     30 |  11 |    0 |     98 files changed, 1532 insertions(+), 1261 deletions(-) |
| narwhals           | infer-pyrefly      |     36 |  17 |    0 |    101 files changed, 1728 insertions(+), 1395 deletions(-) |
| narwhals           | infer-trace        |     24 |   5 |    0 |      97 files changed, 1147 insertions(+), 949 deletions(-) |
| narwhals           | infer-ty           |     36 |  17 |    0 |     98 files changed, 1453 insertions(+), 1203 deletions(-) |
| litestar           | released           |     86 |     |      |                                                             |
| litestar           | fix-certain        |     86 |   0 |    0 |      165 files changed, 806 insertions(+), 576 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |      165 files changed, 806 insertions(+), 576 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |      165 files changed, 806 insertions(+), 576 deletions(-) |
| litestar           | infer-basedpyright |     90 |   4 |    0 |     174 files changed, 1081 insertions(+), 802 deletions(-) |
| litestar           | infer-pyrefly      |     87 |   1 |    0 |      169 files changed, 916 insertions(+), 655 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |      165 files changed, 806 insertions(+), 576 deletions(-) |
| litestar           | infer-ty           |     91 |   5 |    0 |     175 files changed, 1081 insertions(+), 791 deletions(-) |
| optuna             | released           |     52 |     |      |                                                             |
| optuna             | fix-certain        |     52 |   0 |    0 |    144 files changed, 1781 insertions(+), 1253 deletions(-) |
| optuna             | fix-likely         |     52 |   0 |    0 |    144 files changed, 1781 insertions(+), 1253 deletions(-) |
| optuna             | fix-unsafe         |     53 |   1 |    0 |    144 files changed, 1899 insertions(+), 1339 deletions(-) |
| optuna             | infer-basedpyright |     53 |   1 |    0 |    164 files changed, 2297 insertions(+), 1663 deletions(-) |
| optuna             | infer-pyrefly      |     57 |   5 |    0 |    147 files changed, 2094 insertions(+), 1491 deletions(-) |
| optuna             | infer-trace        |     53 |   1 |    0 |    144 files changed, 1899 insertions(+), 1339 deletions(-) |
| optuna             | infer-ty           |     56 |   4 |    0 |    162 files changed, 2311 insertions(+), 1664 deletions(-) |
| mypy               | released           |      0 |     |      |                                                             |
| mypy               | fix-certain        |      0 |   0 |    0 |    160 files changed, 5008 insertions(+), 3053 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 |    166 files changed, 6214 insertions(+), 4105 deletions(-) |
| mypy               | fix-unsafe         |     14 |  14 |    0 |    167 files changed, 6597 insertions(+), 4421 deletions(-) |
| mypy               | infer-basedpyright |     20 |  20 |    0 |    170 files changed, 8586 insertions(+), 6213 deletions(-) |
| mypy               | infer-pyrefly      |     20 |  20 |    0 |    170 files changed, 9196 insertions(+), 6398 deletions(-) |
| mypy               | infer-trace        |     14 |  14 |    0 |    167 files changed, 6597 insertions(+), 4421 deletions(-) |
| mypy               | infer-ty           |     26 |  26 |    0 |    170 files changed, 8937 insertions(+), 6395 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step                     | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library   | check                    |    82.1 |       116.8 |  1.4 |    3.93 |          2 |     4.81 | False |
| standard library   | fix-certain              |   152.5 |       301.5 |  2.0 |     5.3 |          3 |     6.65 | False |
| standard library   | fix-likely               |   178.0 |       374.1 |  2.1 |    8.03 |          3 |    10.04 | False |
| standard library   | fix-unsafe               |   152.8 |       315.5 |  2.1 |     6.1 |          4 |     7.65 | False |
| standard library   | infer-basedpyright       |   855.8 |      1457.9 |  1.7 |   12.51 |          2 |    16.01 | False |
| standard library   | infer-ty                 |   220.4 |       569.5 |  2.6 |   15.02 |          2 |    19.29 | False |
| standard library   | infer-pyrefly            |   202.1 |       538.7 |  2.7 |   18.08 |          3 |    23.85 | False |
| standard library   | census                   |    30.1 |        29.5 |  1.0 |    0.53 |          2 |     4.81 | False |
| standard library   | coverage                 |    11.6 |        34.0 |  2.9 |    1.65 |          4 |     2.06 | False |
| standard library   | timing                   |    72.6 |       109.9 |  1.5 |    3.89 |         16 |     4.81 | False |
| django             | check                    |     6.6 |        17.1 |  2.6 |    0.89 |          3 |     1.11 | False |
| django             | fix-certain              |    24.1 |        56.6 |  2.3 |    1.18 |          3 |     1.45 | False |
| django             | fix-likely               |    25.1 |        66.1 |  2.6 |    1.58 |          3 |     1.97 | False |
| django             | fix-unsafe               |    43.1 |        57.9 |  1.3 |    1.34 |          2 |     1.65 | False |
| django             | infer-basedpyright       |    71.8 |       306.0 |  4.3 |    7.46 |          4 |      9.0 | False |
| django             | infer-ty                 |    31.1 |        93.9 |  3.0 |    3.64 |          3 |      3.8 | False |
| django             | infer-pyrefly            |    35.1 |       102.5 |  2.9 |    4.13 |          3 |      5.2 | False |
| django             | census                   |     3.4 |         3.1 |  0.9 |    0.09 |          3 |     1.11 | False |
| django             | coverage                 |     5.6 |         5.5 |  1.0 |    0.36 |          3 |     0.44 | False |
| django             | timing                   |    14.2 |        21.3 |  1.5 |     0.9 |         16 |     1.11 | False |
| django             | traced                   |   621.5 |       515.2 |  0.8 |    1.44 |          1 |     1.74 | False |
| django             | tests-released           |    63.9 |       458.3 |  7.2 |    5.49 |          7 |     6.96 | False |
| django             | tests-fix-certain        |     0.2 |         0.2 |  1.0 |    0.04 |          8 |     6.08 | False |
| django             | tests-fix-likely         |     0.4 |         0.3 |  0.7 |    0.04 |         12 |     6.89 | False |
| django             | tests-fix-unsafe         |    59.7 |       462.3 |  7.7 |     5.4 |          6 |     6.77 | False |
| django             | tests-infer-basedpyright |    55.3 |       442.5 |  8.0 |    5.66 |          8 |     7.19 | False |
| django             | tests-infer-ty           |    55.1 |       431.6 |  7.8 |     5.4 |          8 |     6.88 | False |
| django             | tests-infer-pyrefly      |    63.1 |       420.8 |  6.7 |    4.14 |          8 |     4.84 | False |
| django             | tests-infer-trace        |    57.3 |       461.0 |  8.0 |    5.77 |          7 |     7.16 | False |
| django             | infer-union              |    88.0 |       315.7 |  3.6 |   10.16 |          5 |    11.94 | False |
| django             | tests-infer-union        |    65.1 |       470.5 |  7.2 |     5.8 |          7 |      7.1 | False |
| django             | tests                    |    66.7 |       452.7 |  6.8 |    4.76 |         10 |     5.41 | False |
| sqlalchemy         | check                    |     3.0 |         0.3 |  0.1 |    0.05 |          2 |     1.14 | False |
| sqlalchemy         | fix-certain              |    23.3 |        46.9 |  2.0 |    1.03 |          3 |     1.27 | False |
| sqlalchemy         | fix-likely               |    25.3 |        57.4 |  2.3 |    1.43 |          3 |     1.79 | False |
| sqlalchemy         | fix-unsafe               |    36.9 |        47.8 |  1.3 |    1.11 |          2 |     1.35 | False |
| sqlalchemy         | infer-basedpyright       |    65.4 |       179.9 |  2.8 |    6.35 |          4 |     9.34 | False |
| sqlalchemy         | infer-ty                 |    37.3 |        88.1 |  2.4 |    3.84 |          3 |     4.55 | False |
| sqlalchemy         | infer-pyrefly            |    35.1 |        73.6 |  2.1 |     4.1 |          3 |     4.65 | False |
| sqlalchemy         | census                   |    10.8 |        18.8 |  1.7 |     0.9 |          2 |     1.14 | False |
| sqlalchemy         | coverage                 |     3.4 |         7.3 |  2.1 |    0.41 |          3 |     0.51 | False |
| sqlalchemy         | timing                   |    12.4 |        17.1 |  1.4 |    0.91 |         16 |     1.14 | False |
| sqlalchemy         | traced                   |   166.6 |      1279.1 |  7.7 |    6.28 |          7 |     7.87 | False |
| sqlalchemy         | tests-released           |   124.5 |       981.9 |  7.9 |    5.21 |          8 |     7.13 | False |
| sqlalchemy         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |         10 |     4.49 | False |
| sqlalchemy         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     6.22 | False |
| sqlalchemy         | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     3.62 | False |
| sqlalchemy         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |         10 |     5.52 | False |
| sqlalchemy         | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.33 | False |
| sqlalchemy         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     7.05 | False |
| sqlalchemy         | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     4.95 | False |
| sqlalchemy         | infer-union              |    82.8 |       296.5 |  3.6 |   11.44 |          2 |    13.69 | False |
| sqlalchemy         | tests-infer-union        |   121.1 |      1049.3 |  8.7 |    5.82 |          8 |     7.31 | False |
| sqlalchemy         | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sqlalchemy         | types-released           |     0.6 |         0.3 |  0.5 |    0.07 |          1 |     0.41 | False |
| sqlalchemy         | types-fix-certain        |     0.6 |         0.3 |  0.5 |    0.03 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-likely         |    10.0 |         7.5 |  0.8 |    0.31 |          1 |     0.39 | False |
| sqlalchemy         | types-fix-unsafe         |     6.0 |         5.5 |  0.9 |     0.3 |          1 |     0.37 | False |
| sqlalchemy         | types-infer-basedpyright |    10.4 |         7.8 |  0.8 |    0.32 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-ty           |     7.6 |         6.6 |  0.9 |    0.32 |          1 |     0.42 | False |
| sqlalchemy         | types-infer-pyrefly      |     5.8 |         5.2 |  0.9 |    0.34 |          1 |     0.39 | False |
| sqlalchemy         | types-infer-trace        |     5.6 |         5.3 |  0.9 |    0.31 |          1 |     0.41 | False |
| sqlalchemy         | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| pydantic           | check                    |     0.6 |         0.2 |  0.3 |    0.04 |          2 |     0.39 | False |
| pydantic           | fix-certain              |     4.2 |        10.5 |  2.5 |    0.44 |          3 |     0.56 | False |
| pydantic           | fix-likely               |     5.2 |        13.5 |  2.6 |    0.51 |          3 |     0.65 | False |
| pydantic           | fix-unsafe               |    15.0 |        14.8 |  1.0 |    0.54 |          2 |     0.67 | False |
| pydantic           | infer-basedpyright       |    35.1 |        89.1 |  2.5 |    3.23 |          3 |     3.77 | False |
| pydantic           | infer-ty                 |     7.8 |        21.9 |  2.8 |    1.71 |          3 |     1.41 | False |
| pydantic           | infer-pyrefly            |    10.8 |        33.5 |  3.1 |    2.03 |          4 |      2.4 | False |
| pydantic           | census                   |     3.0 |         5.2 |  1.7 |    0.31 |          2 |     0.39 | False |
| pydantic           | coverage                 |     2.8 |         2.0 |  0.7 |    0.21 |          3 |     0.26 | False |
| pydantic           | timing                   |     2.8 |         3.9 |  1.4 |    0.32 |         16 |      0.4 | False |
| pydantic           | traced                   |    56.6 |        52.4 |  0.9 |    0.49 |          1 |     0.69 | False |
| pydantic           | tests-released           |    54.2 |        37.4 |  0.7 |    0.36 |          1 |     0.39 | False |
| pydantic           | tests-fix-certain        |     1.0 |         0.2 |  0.2 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.4 | False |
| pydantic           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.35 | False |
| pydantic           | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.37 | False |
| pydantic           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.35 | False |
| pydantic           | infer-union              |    25.1 |        84.2 |  3.4 |    5.16 |          4 |     5.89 | False |
| pydantic           | tests-infer-union        |    42.7 |        36.8 |  0.9 |    0.35 |          1 |     0.46 | False |
| pydantic           | tests                    |     0.8 |         0.2 |  0.2 |    0.03 |          1 |     0.35 | False |
| pydantic           | types-released           |    11.2 |        15.9 |  1.4 |    0.52 |          2 |     0.66 | False |
| pydantic           | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.67 | False |
| pydantic           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.69 | False |
| pydantic           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.65 | False |
| pydantic           | types-infer-basedpyright |    15.2 |        19.9 |  1.3 |    0.54 |          2 |      0.7 | False |
| pydantic           | types-infer-ty           |    12.0 |        17.1 |  1.4 |    0.53 |          2 |     0.69 | False |
| pydantic           | types-infer-pyrefly      |    13.8 |        19.0 |  1.4 |    0.53 |          2 |     0.69 | False |
| pydantic           | types-infer-trace        |    13.1 |        17.1 |  1.3 |    0.55 |          2 |     0.74 | False |
| pydantic           | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| pandas             | check                    |    29.5 |        88.4 |  3.0 |     3.4 |          4 |     4.26 | False |
| pandas             | fix-certain              |    77.0 |       231.0 |  3.0 |    4.22 |          4 |     5.27 | False |
| pandas             | fix-likely               |   132.3 |       398.6 |  3.0 |    7.56 |          4 |     9.47 | False |
| pandas             | fix-unsafe               |    95.2 |       295.4 |  3.1 |    4.47 |          3 |     5.59 | False |
| pandas             | infer-basedpyright       |   738.3 |      1915.7 |  2.6 |   19.46 |          2 |    19.14 | False |
| pandas             | infer-ty                 |   213.5 |       631.9 |  3.0 |   14.11 |          4 |    17.91 | False |
| pandas             | infer-pyrefly            |   167.4 |       559.4 |  3.3 |   18.73 |          3 |    22.15 | False |
| pandas             | census                   |    34.9 |        16.6 |  0.5 |    0.34 |          4 |     4.26 | False |
| pandas             | coverage                 |    11.0 |        24.2 |  2.2 |    1.09 |          4 |     1.34 | False |
| pandas             | timing                   |    75.8 |       119.7 |  1.6 |    3.39 |         16 |     4.22 | False |
| pandas             | traced                   |   239.1 |      1175.5 |  4.9 |   12.32 |          5 |    15.32 | False |
| pandas             | tests-released           |    98.9 |       643.0 |  6.5 |    11.5 |         10 |    14.11 | False |
| pandas             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    13.97 | False |
| pandas             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |    13.97 | False |
| pandas             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |         10 |    14.05 | False |
| pandas             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    14.12 | False |
| pandas             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |         10 |    14.07 | False |
| pandas             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    14.11 | False |
| pandas             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          9 |    14.17 | False |
| pandas             | infer-union              |   228.4 |       888.3 |  3.9 |   28.27 |          4 |    35.02 | False |
| pandas             | tests-infer-union        |   113.4 |       648.4 |  5.7 |   11.53 |          6 |    14.17 | False |
| pandas             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.03 | False |
| pandas             | types-released           |    70.0 |       106.1 |  1.5 |    2.19 |          2 |     2.49 | False |
| pandas             | types-fix-certain        |    67.9 |        91.7 |  1.4 |    2.27 |          1 |      2.7 | False |
| pandas             | types-fix-likely         |    83.2 |        77.5 |  0.9 |    2.25 |          1 |     2.91 | False |
| pandas             | types-fix-unsafe         |    62.3 |        97.1 |  1.6 |    2.24 |          2 |     2.84 | False |
| pandas             | types-infer-basedpyright |    63.9 |        99.4 |  1.6 |    2.34 |          2 |     2.87 | False |
| pandas             | types-infer-ty           |    65.9 |        93.2 |  1.4 |    2.25 |          1 |     2.65 | False |
| pandas             | types-infer-pyrefly      |    71.9 |        99.9 |  1.4 |    2.16 |          2 |     2.84 | False |
| pandas             | types-infer-trace        |    66.7 |       100.4 |  1.5 |    2.22 |          1 |      2.9 | False |
| pandas             | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| twisted            | check                    |     6.4 |        15.5 |  2.4 |    0.85 |          3 |     1.06 | False |
| twisted            | fix-certain              |    18.0 |        44.6 |  2.5 |    0.98 |          3 |     1.22 | False |
| twisted            | fix-likely               |    14.4 |        43.5 |  3.0 |    1.46 |          3 |     1.82 | False |
| twisted            | fix-unsafe               |    17.2 |        45.2 |  2.6 |    0.99 |          3 |     1.24 | False |
| twisted            | infer-basedpyright       |    58.7 |       217.5 |  3.7 |     9.5 |          4 |     11.1 | False |
| twisted            | infer-ty                 |    24.3 |        79.0 |  3.3 |     3.0 |          4 |     3.85 | False |
| twisted            | infer-pyrefly            |    30.5 |        77.7 |  2.5 |    3.74 |          4 |     5.21 | False |
| twisted            | census                   |    11.0 |         4.9 |  0.4 |     0.1 |          3 |     1.06 | False |
| twisted            | coverage                 |     2.8 |         7.0 |  2.5 |    0.38 |          4 |      0.5 | False |
| twisted            | timing                   |    10.4 |        15.9 |  1.5 |    0.86 |         16 |     1.07 | False |
| pip                | check                    |     4.6 |        10.5 |  2.3 |     0.6 |          3 |     0.75 | False |
| pip                | fix-certain              |    13.6 |        32.9 |  2.4 |    0.75 |          3 |     0.92 | False |
| pip                | fix-likely               |    10.8 |        32.2 |  3.0 |    0.93 |          3 |     1.16 | False |
| pip                | fix-unsafe               |    10.8 |        28.8 |  2.7 |    0.74 |          3 |     0.92 | False |
| pip                | infer-basedpyright       |    47.1 |       173.7 |  3.7 |     5.5 |          4 |     6.64 | False |
| pip                | infer-ty                 |    23.4 |        59.1 |  2.5 |    2.84 |          4 |     3.36 | False |
| pip                | infer-pyrefly            |    24.6 |        61.3 |  2.5 |    3.26 |          4 |     3.84 | False |
| pip                | census                   |     3.0 |         2.8 |  0.9 |     0.1 |          3 |     0.75 | False |
| pip                | coverage                 |     1.6 |         3.8 |  2.4 |    0.33 |          3 |     0.44 | False |
| pip                | timing                   |     7.2 |        10.7 |  1.5 |    0.57 |         16 |     0.71 | False |
| structlog          | check                    |     1.6 |         1.1 |  0.7 |    0.16 |          1 |      0.2 | False |
| structlog          | fix-certain              |     1.6 |         2.6 |  1.6 |    0.25 |          2 |     0.34 | False |
| structlog          | fix-likely               |     3.6 |         3.1 |  0.9 |    0.28 |          2 |      0.3 | False |
| structlog          | fix-unsafe               |     1.4 |         2.4 |  1.7 |    0.26 |          2 |     0.34 | False |
| structlog          | infer-basedpyright       |     8.2 |        11.7 |  1.4 |     0.6 |          1 |      0.7 | False |
| structlog          | infer-ty                 |     2.2 |         3.6 |  1.6 |    0.41 |          2 |     0.39 | False |
| structlog          | infer-pyrefly            |     2.4 |         3.6 |  1.5 |    0.39 |          2 |     0.49 | False |
| structlog          | census                   |     1.8 |         0.3 |  0.2 |    0.03 |          1 |      0.2 | False |
| structlog          | coverage                 |     1.8 |         0.9 |  0.5 |    0.14 |          1 |     0.17 | False |
| structlog          | timing                   |     0.8 |         0.8 |  1.0 |    0.16 |         16 |      0.2 | False |
| structlog          | traced                   |     3.8 |         4.6 |  1.2 |    0.26 |          1 |     0.35 | False |
| structlog          | tests-released           |     2.6 |         2.0 |  0.8 |    0.07 |          1 |     0.09 | False |
| structlog          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | infer-union              |     7.4 |        12.2 |  1.6 |    0.97 |          1 |     1.26 | False |
| structlog          | tests-infer-union        |     2.0 |         1.7 |  0.8 |    0.07 |          1 |     0.09 | False |
| structlog          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| structlog          | types-released           |     0.8 |         0.5 |  0.6 |    0.08 |          1 |     0.07 | False |
| structlog          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-infer-basedpyright |     0.8 |         0.4 |  0.5 |    0.07 |          1 |      0.1 | False |
| structlog          | types-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| structlog          | types-infer-pyrefly      |     0.6 |         0.4 |  0.7 |    0.08 |          1 |      0.1 | False |
| structlog          | types-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| structlog          | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| attrs              | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.19 | False |
| attrs              | fix-certain              |     2.0 |         2.5 |  1.2 |    0.26 |          2 |     0.31 | False |
| attrs              | fix-likely               |     2.2 |         2.6 |  1.2 |    0.26 |          2 |     0.32 | False |
| attrs              | fix-unsafe               |     2.0 |         2.5 |  1.2 |    0.26 |          2 |     0.32 | False |
| attrs              | infer-basedpyright       |     9.4 |        12.1 |  1.3 |    0.58 |          1 |     0.72 | False |
| attrs              | infer-ty                 |     3.0 |         3.8 |  1.3 |     0.4 |          2 |     0.34 | False |
| attrs              | infer-pyrefly            |     3.2 |         6.7 |  2.1 |    0.55 |          3 |     0.69 | False |
| attrs              | census                   |     2.0 |         1.1 |  0.6 |    0.15 |          1 |     0.19 | False |
| attrs              | coverage                 |     2.2 |         0.8 |  0.4 |    0.14 |          1 |     0.17 | False |
| attrs              | timing                   |     0.8 |         0.7 |  0.9 |    0.15 |         16 |     0.19 | False |
| attrs              | traced                   |     5.4 |        23.4 |  4.3 |    0.74 |          6 |     0.91 | False |
| attrs              | tests-released           |     5.0 |        19.7 |  3.9 |     0.6 |          4 |     0.74 | False |
| attrs              | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.75 | False |
| attrs              | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     0.74 | False |
| attrs              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.75 | False |
| attrs              | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     0.72 | False |
| attrs              | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     0.74 | False |
| attrs              | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.72 | False |
| attrs              | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.76 | False |
| attrs              | infer-union              |     6.0 |        14.1 |  2.4 |    1.09 |          3 |     1.37 | False |
| attrs              | tests-infer-union        |     3.6 |        17.1 |  4.8 |     0.6 |          6 |     0.75 | False |
| attrs              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     0.75 | False |
| click              | check                    |     0.8 |         1.0 |  1.2 |    0.18 |          2 |     0.22 | False |
| click              | fix-certain              |     4.4 |         4.4 |  1.0 |     0.3 |          2 |     0.37 | False |
| click              | fix-likely               |     4.2 |         5.3 |  1.3 |    0.27 |          2 |     0.37 | False |
| click              | fix-unsafe               |     2.2 |         3.8 |  1.7 |     0.3 |          2 |     0.37 | False |
| click              | infer-basedpyright       |     9.8 |        12.8 |  1.3 |    0.68 |          1 |     0.86 | False |
| click              | infer-ty                 |     3.4 |         5.7 |  1.7 |    0.47 |          1 |     0.41 | False |
| click              | infer-pyrefly            |     3.0 |         7.7 |  2.6 |     0.6 |          3 |     0.74 | False |
| click              | census                   |     1.2 |         0.4 |  0.3 |    0.04 |          2 |     0.22 | False |
| click              | coverage                 |     1.2 |         1.0 |  0.8 |    0.16 |          1 |      0.2 | False |
| click              | timing                   |     1.0 |         1.1 |  1.1 |    0.18 |         16 |     0.22 | False |
| click              | traced                   |     9.0 |        10.1 |  1.1 |    0.29 |          1 |     0.39 | False |
| click              | tests-released           |     7.4 |         6.2 |  0.8 |    0.17 |          1 |     0.21 | False |
| click              | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| click              | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| click              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.21 | False |
| click              | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| click              | infer-union              |    12.2 |        20.7 |  1.7 |    1.22 |          3 |     1.22 | False |
| click              | tests-infer-union        |     4.8 |         4.7 |  1.0 |    0.17 |          1 |     0.21 | False |
| click              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| click              | types-released           |     1.0 |         0.6 |  0.6 |    0.12 |          1 |     0.09 | False |
| click              | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| click              | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.06 | False |
| click              | types-infer-basedpyright |     2.0 |         0.7 |  0.3 |     0.1 |          1 |     0.15 | False |
| click              | types-infer-ty           |     1.4 |         0.7 |  0.5 |     0.1 |          1 |     0.14 | False |
| click              | types-infer-pyrefly      |     0.8 |         0.5 |  0.6 |    0.12 |          1 |     0.15 | False |
| click              | types-infer-trace        |     0.8 |         0.6 |  0.7 |    0.12 |          1 |     0.14 | False |
| click              | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| hypercorn          | check                    |     2.8 |         0.2 |  0.1 |    0.03 |          1 |     0.22 | False |
| hypercorn          | fix-certain              |     1.8 |         3.0 |  1.7 |    0.25 |          2 |     0.35 | False |
| hypercorn          | fix-likely               |     1.8 |         3.3 |  1.8 |    0.25 |          2 |     0.35 | False |
| hypercorn          | fix-unsafe               |     2.0 |         3.4 |  1.7 |    0.25 |          2 |     0.31 | False |
| hypercorn          | infer-basedpyright       |     5.8 |        16.3 |  2.8 |    0.89 |          2 |     0.94 | False |
| hypercorn          | infer-ty                 |     2.0 |         4.5 |  2.2 |    0.62 |          3 |     0.74 | False |
| hypercorn          | infer-pyrefly            |     3.0 |        10.2 |  3.4 |    0.64 |          4 |     1.06 | False |
| hypercorn          | census                   |     3.0 |         1.8 |  0.6 |     0.2 |          1 |     0.22 | False |
| hypercorn          | coverage                 |     2.0 |         0.9 |  0.5 |    0.14 |          1 |     0.17 | False |
| hypercorn          | timing                   |     0.8 |         0.9 |  1.1 |    0.18 |         16 |     0.22 | False |
| hypercorn          | traced                   |     9.8 |         5.0 |  0.5 |    0.27 |          1 |     0.32 | False |
| hypercorn          | tests-released           |     7.6 |         1.4 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| hypercorn          | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.11 | False |
| hypercorn          | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.11 | False |
| hypercorn          | infer-union              |     6.6 |        21.7 |  3.3 |    1.91 |          4 |     2.02 | False |
| hypercorn          | tests-infer-union        |     7.2 |         1.3 |  0.2 |     0.1 |          1 |     0.12 | False |
| hypercorn          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.11 | False |
| hypercorn          | types-released           |     1.2 |         0.9 |  0.8 |    0.12 |          1 |     0.09 | False |
| hypercorn          | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| hypercorn          | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.14 | False |
| hypercorn          | types-infer-basedpyright |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.15 | False |
| hypercorn          | types-infer-ty           |     1.0 |         0.8 |  0.8 |    0.12 |          1 |     0.14 | False |
| hypercorn          | types-infer-pyrefly      |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.14 | False |
| hypercorn          | types-infer-trace        |     1.6 |         1.0 |  0.6 |    0.14 |          1 |     0.15 | False |
| hypercorn          | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | check                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.22 | False |
| starlette          | fix-certain              |     1.8 |         3.5 |  1.9 |    0.27 |          2 |     0.37 | False |
| starlette          | fix-likely               |     1.8 |         3.9 |  2.2 |    0.29 |          2 |     0.34 | False |
| starlette          | fix-unsafe               |     2.0 |         3.6 |  1.8 |    0.26 |          2 |     0.32 | False |
| starlette          | infer-basedpyright       |     5.0 |        13.1 |  2.6 |    1.06 |          3 |     1.11 | False |
| starlette          | infer-ty                 |     2.6 |         5.5 |  2.1 |    0.65 |          3 |      0.8 | False |
| starlette          | infer-pyrefly            |     3.0 |        11.9 |  4.0 |    0.93 |          5 |     1.15 | False |
| starlette          | census                   |     3.8 |         2.3 |  0.6 |    0.21 |          2 |     0.22 | False |
| starlette          | coverage                 |     2.2 |         1.1 |  0.5 |    0.15 |          1 |     0.19 | False |
| starlette          | timing                   |     1.0 |         1.2 |  1.2 |    0.18 |         16 |     0.22 | False |
| starlette          | traced                   |    12.2 |        10.9 |  0.9 |    0.28 |          1 |     0.35 | False |
| starlette          | tests-released           |    10.6 |         6.7 |  0.6 |    0.23 |          1 |     0.29 | False |
| starlette          | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| starlette          | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.29 | False |
| starlette          | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.27 | False |
| starlette          | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.27 | False |
| starlette          | infer-union              |     6.2 |        23.8 |  3.8 |     2.0 |          4 |     2.26 | False |
| starlette          | tests-infer-union        |    13.8 |         7.6 |  0.6 |    0.23 |          1 |     0.29 | False |
| starlette          | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| starlette          | types-released           |     1.8 |         1.5 |  0.8 |    0.14 |          1 |     0.09 | False |
| starlette          | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.15 | False |
| starlette          | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.16 | False |
| starlette          | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| starlette          | types-infer-basedpyright |     1.2 |         1.0 |  0.8 |    0.14 |          1 |     0.17 | False |
| starlette          | types-infer-ty           |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.12 | False |
| starlette          | types-infer-pyrefly      |     1.2 |         1.0 |  0.8 |    0.14 |          1 |     0.16 | False |
| starlette          | types-infer-trace        |     2.4 |         1.7 |  0.7 |    0.14 |          1 |     0.17 | False |
| starlette          | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| werkzeug           | check                    |     1.2 |         1.9 |  1.6 |    0.21 |          2 |     0.26 | False |
| werkzeug           | fix-certain              |     2.4 |         5.6 |  2.3 |    0.34 |          2 |     0.42 | False |
| werkzeug           | fix-likely               |     2.8 |         6.6 |  2.4 |    0.34 |          2 |      0.4 | False |
| werkzeug           | fix-unsafe               |     2.8 |         6.0 |  2.1 |    0.33 |          2 |     0.41 | False |
| werkzeug           | infer-basedpyright       |     7.2 |        23.7 |  3.3 |    1.17 |          3 |     1.49 | False |
| werkzeug           | infer-ty                 |     2.6 |         7.6 |  2.9 |    0.74 |          3 |     0.92 | False |
| werkzeug           | infer-pyrefly            |     2.8 |         9.2 |  3.3 |    1.05 |          3 |     1.31 | False |
| werkzeug           | census                   |     0.6 |         0.5 |  0.8 |    0.04 |          2 |     0.26 | False |
| werkzeug           | coverage                 |     2.0 |         1.5 |  0.8 |    0.17 |          1 |     0.21 | False |
| werkzeug           | timing                   |     1.4 |         1.9 |  1.4 |    0.21 |         16 |     0.26 | False |
| werkzeug           | traced                   |    12.8 |        14.4 |  1.1 |    0.32 |          1 |     0.42 | False |
| werkzeug           | tests-released           |     9.7 |         7.1 |  0.7 |    0.17 |          1 |     0.21 | False |
| werkzeug           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.21 | False |
| werkzeug           | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | infer-union              |    16.4 |        48.0 |  2.9 |    2.55 |          4 |     2.82 | False |
| werkzeug           | tests-infer-union        |    10.0 |         7.1 |  0.7 |    0.16 |          1 |     0.21 | False |
| werkzeug           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.2 | False |
| werkzeug           | types-released           |     1.2 |         1.0 |  0.8 |    0.11 |          1 |     0.07 | False |
| werkzeug           | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.12 | False |
| werkzeug           | types-infer-basedpyright |     1.0 |         0.7 |  0.7 |    0.11 |          1 |     0.12 | False |
| werkzeug           | types-infer-ty           |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.14 | False |
| werkzeug           | types-infer-pyrefly      |     0.8 |         0.7 |  0.9 |     0.1 |          1 |     0.12 | False |
| werkzeug           | types-infer-trace        |     1.4 |         1.0 |  0.7 |    0.11 |          1 |     0.14 | False |
| werkzeug           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mkdocs             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.32 | False |
| mkdocs             | fix-certain              |     5.2 |         6.7 |  1.3 |    0.36 |          3 |     0.45 | False |
| mkdocs             | fix-likely               |     4.4 |         8.2 |  1.9 |    0.36 |          2 |     0.46 | False |
| mkdocs             | fix-unsafe               |     4.0 |         7.3 |  1.8 |    0.37 |          2 |     0.44 | False |
| mkdocs             | infer-basedpyright       |     9.4 |        24.8 |  2.6 |    1.17 |          3 |     1.46 | False |
| mkdocs             | infer-ty                 |     5.8 |        11.7 |  2.0 |    0.87 |          2 |     1.04 | False |
| mkdocs             | infer-pyrefly            |     5.2 |        15.9 |  3.1 |    0.86 |          4 |     1.06 | False |
| mkdocs             | census                   |     2.0 |         2.9 |  1.4 |    0.26 |          2 |     0.32 | False |
| mkdocs             | coverage                 |     0.8 |         1.4 |  1.7 |    0.18 |          2 |     0.22 | False |
| mkdocs             | timing                   |     1.8 |         2.2 |  1.2 |    0.26 |         16 |     0.32 | False |
| mkdocs             | traced                   |    14.8 |        10.5 |  0.7 |    0.37 |          1 |     0.46 | False |
| mkdocs             | tests-released           |    11.1 |         2.5 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests-fix-certain        |     0.6 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.09 | False |
| mkdocs             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.1 | False |
| mkdocs             | infer-union              |    17.5 |        54.7 |  3.1 |    2.77 |          3 |     2.89 | False |
| mkdocs             | tests-infer-union        |    10.0 |         2.3 |  0.2 |    0.08 |          1 |      0.1 | False |
| mkdocs             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| httpx              | check                    |     1.0 |         1.2 |  1.2 |    0.18 |          2 |     0.22 | False |
| httpx              | fix-certain              |     1.8 |         3.2 |  1.8 |     0.3 |          2 |     0.35 | False |
| httpx              | fix-likely               |     1.8 |         3.7 |  2.1 |    0.28 |          2 |     0.36 | False |
| httpx              | fix-unsafe               |     2.0 |         3.2 |  1.6 |    0.26 |          2 |     0.32 | False |
| httpx              | infer-basedpyright       |     9.4 |        16.1 |  1.7 |    0.66 |          2 |     0.86 | False |
| httpx              | infer-ty                 |     4.0 |         5.4 |  1.4 |    0.52 |          1 |     0.51 | False |
| httpx              | infer-pyrefly            |     3.0 |         7.9 |  2.6 |    0.64 |          3 |     0.61 | False |
| httpx              | census                   |     0.4 |         0.3 |  0.7 |    0.03 |          2 |     0.22 | False |
| httpx              | coverage                 |     2.2 |         1.0 |  0.5 |    0.15 |          1 |     0.17 | False |
| httpx              | timing                   |     0.8 |         1.0 |  1.2 |    0.18 |         16 |     0.22 | False |
| httpx              | traced                   |    11.8 |        10.1 |  0.9 |     0.3 |          1 |     0.39 | False |
| httpx              | tests-released           |     8.1 |         5.7 |  0.7 |    0.22 |          1 |     0.26 | False |
| httpx              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.25 | False |
| httpx              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.27 | False |
| httpx              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| httpx              | infer-union              |     5.2 |        11.9 |  2.3 |    1.33 |          3 |      1.3 | False |
| httpx              | tests-infer-union        |     8.2 |         6.2 |  0.8 |    0.22 |          1 |     0.29 | False |
| httpx              | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.26 | False |
| httpx              | types-released           |     6.8 |         5.8 |  0.9 |    0.24 |          1 |     0.09 | False |
| httpx              | types-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.25 | False |
| httpx              | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.24 | False |
| httpx              | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.24 | False |
| httpx              | types-infer-basedpyright |     4.8 |         4.6 |  1.0 |    0.19 |          1 |      0.3 | False |
| httpx              | types-infer-ty           |    13.8 |         6.7 |  0.5 |    0.19 |          1 |      0.3 | False |
| httpx              | types-infer-pyrefly      |     7.4 |         6.1 |  0.8 |     0.2 |          1 |      0.3 | False |
| httpx              | types-infer-trace        |     8.6 |         6.4 |  0.7 |    0.24 |          1 |     0.29 | False |
| httpx              | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| black              | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.24 | False |
| black              | fix-certain              |     2.4 |         4.6 |  1.9 |    0.29 |          2 |     0.41 | False |
| black              | fix-likely               |     2.0 |         4.9 |  2.5 |    0.32 |          3 |     0.41 | False |
| black              | fix-unsafe               |     1.8 |         4.5 |  2.5 |    0.32 |          3 |      0.4 | False |
| black              | infer-basedpyright       |    15.7 |        23.2 |  1.5 |    0.77 |          2 |     0.96 | False |
| black              | infer-ty                 |     3.2 |         6.7 |  2.1 |    0.53 |          2 |     0.64 | False |
| black              | infer-pyrefly            |     3.6 |         9.8 |  2.7 |    0.68 |          3 |     0.69 | False |
| black              | census                   |     2.6 |         2.1 |  0.8 |    0.19 |          2 |     0.24 | False |
| black              | coverage                 |     1.4 |         1.2 |  0.9 |    0.17 |          1 |     0.21 | False |
| black              | timing                   |     1.2 |         1.4 |  1.2 |    0.19 |         16 |     0.24 | False |
| black              | traced                   |    10.2 |        60.4 |  5.9 |    0.89 |          8 |      1.1 | False |
| black              | tests-released           |     7.0 |        43.0 |  6.1 |    0.76 |          7 |     0.92 | False |
| black              | tests-fix-certain        |     8.6 |        46.0 |  5.3 |    0.76 |          4 |     0.95 | False |
| black              | tests-fix-likely         |     4.8 |        33.7 |  7.0 |    0.74 |          3 |     0.95 | False |
| black              | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     0.95 | False |
| black              | tests-infer-basedpyright |     8.8 |        49.9 |  5.7 |    0.77 |          6 |     0.99 | False |
| black              | tests-infer-ty           |     7.6 |        46.9 |  6.2 |    0.77 |          4 |     0.94 | False |
| black              | tests-infer-pyrefly      |     7.0 |        44.4 |  6.3 |    0.77 |          8 |     0.94 | False |
| black              | tests-infer-trace        |     7.2 |        47.7 |  6.6 |    0.75 |          6 |     0.94 | False |
| black              | infer-union              |     6.0 |        14.9 |  2.5 |    1.39 |          3 |     1.74 | False |
| black              | tests-infer-union        |     9.0 |        49.8 |  5.5 |    0.78 |          3 |     0.95 | False |
| black              | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     0.96 | False |
| fastapi            | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.27 | False |
| fastapi            | fix-certain              |     3.4 |         4.8 |  1.4 |    0.34 |          2 |     0.37 | False |
| fastapi            | fix-likely               |     7.0 |         7.4 |  1.1 |    0.45 |          1 |     0.56 | False |
| fastapi            | fix-unsafe               |     4.4 |         5.4 |  1.2 |    0.37 |          1 |     0.39 | False |
| fastapi            | infer-basedpyright       |    11.6 |        27.7 |  2.4 |    1.25 |          3 |     1.59 | False |
| fastapi            | infer-ty                 |     7.2 |        11.0 |  1.5 |    0.85 |          2 |     0.71 | False |
| fastapi            | infer-pyrefly            |     5.0 |        15.0 |  3.0 |    1.16 |          3 |     1.45 | False |
| fastapi            | census                   |     1.8 |         2.0 |  1.1 |    0.22 |          2 |     0.27 | False |
| fastapi            | coverage                 |     0.8 |         1.1 |  1.4 |    0.17 |          2 |     0.21 | False |
| fastapi            | timing                   |     1.4 |         1.5 |  1.1 |    0.22 |         16 |     0.27 | False |
| fastapi            | traced                   |    18.8 |       113.2 |  6.0 |    2.33 |          8 |     2.92 | False |
| fastapi            | tests-released           |    15.0 |        94.6 |  6.3 |    2.09 |          7 |      2.6 | False |
| fastapi            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      2.6 | False |
| fastapi            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      2.6 | False |
| fastapi            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.56 | False |
| fastapi            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.55 | False |
| fastapi            | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.56 | False |
| fastapi            | infer-union              |    13.8 |        34.4 |  2.5 |    2.33 |          3 |     2.36 | False |
| fastapi            | tests-infer-union        |    14.8 |        92.2 |  6.2 |    2.01 |          4 |     2.65 | False |
| fastapi            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| cattrs             | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.22 | False |
| cattrs             | fix-certain              |     5.2 |         3.8 |  0.7 |    0.27 |          2 |     0.27 | False |
| cattrs             | fix-likely               |     2.2 |         3.7 |  1.7 |     0.2 |          2 |     0.32 | False |
| cattrs             | fix-unsafe               |     2.2 |         3.5 |  1.6 |    0.25 |          2 |     0.34 | False |
| cattrs             | infer-basedpyright       |     8.2 |        17.3 |  2.1 |    0.95 |          3 |     1.22 | False |
| cattrs             | infer-ty                 |     3.0 |         5.1 |  1.7 |    0.62 |          2 |     0.42 | False |
| cattrs             | infer-pyrefly            |     2.6 |         7.1 |  2.7 |    0.93 |          3 |     0.85 | False |
| cattrs             | census                   |     1.4 |         1.6 |  1.1 |    0.18 |          2 |     0.22 | False |
| cattrs             | coverage                 |     1.6 |         0.9 |  0.6 |    0.14 |          1 |     0.17 | False |
| cattrs             | timing                   |     1.0 |         1.0 |  1.0 |    0.18 |         16 |     0.22 | False |
| cattrs             | traced                   |    28.0 |       157.6 |  5.6 |    1.23 |          6 |     1.64 | False |
| cattrs             | tests-released           |    18.2 |       123.1 |  6.8 |    1.01 |          8 |     1.22 | False |
| cattrs             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.17 | False |
| cattrs             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.17 | False |
| cattrs             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.25 | False |
| cattrs             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.15 | False |
| cattrs             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.26 | False |
| cattrs             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.22 | False |
| cattrs             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.24 | False |
| cattrs             | infer-union              |    10.4 |        24.0 |  2.3 |    1.91 |          2 |      2.4 | False |
| cattrs             | tests-infer-union        |    20.6 |       121.9 |  5.9 |    0.97 |          7 |     1.17 | False |
| cattrs             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pytest             | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          2 |     0.35 | False |
| pytest             | fix-certain              |     4.4 |         9.4 |  2.1 |    0.42 |          3 |     0.54 | False |
| pytest             | fix-likely               |     5.6 |        11.7 |  2.1 |    0.43 |          3 |     0.54 | False |
| pytest             | fix-unsafe               |     6.2 |        11.5 |  1.9 |    0.44 |          3 |     0.52 | False |
| pytest             | infer-basedpyright       |    21.3 |        61.8 |  2.9 |    2.14 |          4 |     2.72 | False |
| pytest             | infer-ty                 |     7.4 |        17.8 |  2.4 |    1.23 |          3 |     1.32 | False |
| pytest             | infer-pyrefly            |     7.4 |        21.3 |  2.9 |    1.37 |          3 |     2.16 | False |
| pytest             | census                   |     4.6 |         4.9 |  1.1 |    0.28 |          2 |     0.35 | False |
| pytest             | coverage                 |     1.2 |         2.0 |  1.7 |     0.2 |          2 |     0.25 | False |
| pytest             | timing                   |     2.6 |         3.4 |  1.3 |    0.28 |         16 |     0.35 | False |
| pytest             | traced                   |    44.9 |       308.9 |  6.9 |    1.79 |          7 |     2.17 | False |
| pytest             | tests-released           |    21.6 |       157.1 |  7.3 |    1.38 |          8 |     1.69 | False |
| pytest             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          7 |     1.67 | False |
| pytest             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     1.67 | False |
| pytest             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |      1.7 | False |
| pytest             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |      1.7 | False |
| pytest             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      1.7 | False |
| pytest             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      1.7 | False |
| pytest             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.64 | False |
| pytest             | infer-union              |    26.9 |        69.6 |  2.6 |    3.83 |          4 |     4.79 | False |
| pytest             | tests-infer-union        |    22.2 |       161.2 |  7.3 |    1.39 |          8 |     1.71 | False |
| pytest             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.67 | False |
| botocore           | check                    |     3.6 |         4.8 |  1.3 |     0.3 |          3 |     0.37 | False |
| botocore           | fix-certain              |     5.2 |        11.5 |  2.2 |    0.42 |          3 |     0.51 | False |
| botocore           | fix-likely               |     5.8 |        13.5 |  2.3 |    0.47 |          3 |     0.59 | False |
| botocore           | fix-unsafe               |     5.8 |        12.5 |  2.2 |    0.41 |          3 |     0.51 | False |
| botocore           | infer-basedpyright       |    23.1 |        59.0 |  2.6 |    2.48 |          3 |     2.99 | False |
| botocore           | infer-ty                 |     8.6 |        20.6 |  2.4 |    1.24 |          3 |     1.54 | False |
| botocore           | infer-pyrefly            |     7.6 |        18.6 |  2.4 |    1.33 |          3 |     1.51 | False |
| botocore           | census                   |     1.6 |         1.1 |  0.7 |    0.05 |          3 |     0.37 | False |
| botocore           | coverage                 |     2.4 |         2.0 |  0.8 |     0.2 |          2 |     0.25 | False |
| botocore           | timing                   |     3.2 |         4.4 |  1.4 |     0.3 |         16 |     0.37 | False |
| botocore           | traced                   |    36.5 |       120.1 |  3.3 |    5.13 |          4 |      6.4 | False |
| botocore           | tests-released           |    29.9 |        95.5 |  3.2 |    4.96 |          4 |     6.11 | False |
| botocore           | tests-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          4 |     6.05 | False |
| botocore           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          5 |     6.05 | False |
| botocore           | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     5.97 | False |
| botocore           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     6.06 | False |
| botocore           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          4 |     6.11 | False |
| botocore           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          5 |      6.0 | False |
| botocore           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          3 |      6.0 | False |
| botocore           | infer-union              |    35.7 |        58.0 |  1.6 |    3.63 |          3 |     4.59 | False |
| botocore           | tests-infer-union        |    29.3 |        87.9 |  3.0 |    4.82 |          3 |     6.12 | False |
| botocore           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     6.02 | False |
| uvicorn            | check                    |     1.0 |         1.4 |  1.4 |    0.18 |          2 |     0.22 | False |
| uvicorn            | fix-certain              |     1.8 |         3.6 |  2.0 |    0.28 |          2 |     0.37 | False |
| uvicorn            | fix-likely               |     4.4 |         5.0 |  1.1 |    0.22 |          2 |     0.32 | False |
| uvicorn            | fix-unsafe               |     5.4 |         4.4 |  0.8 |    0.26 |          2 |     0.37 | False |
| uvicorn            | infer-basedpyright       |     7.8 |        16.6 |  2.1 |    0.92 |          3 |     1.29 | False |
| uvicorn            | infer-ty                 |     3.8 |         5.7 |  1.5 |    0.66 |          3 |     0.51 | False |
| uvicorn            | infer-pyrefly            |     3.0 |         8.6 |  2.9 |    0.96 |          3 |     1.07 | False |
| uvicorn            | census                   |     0.6 |         0.4 |  0.7 |    0.03 |          2 |     0.22 | False |
| uvicorn            | coverage                 |     1.2 |         0.9 |  0.8 |    0.15 |          1 |     0.19 | False |
| uvicorn            | timing                   |     1.0 |         1.2 |  1.2 |    0.18 |         16 |     0.22 | False |
| uvicorn            | traced                   |    31.0 |        26.4 |  0.9 |    0.91 |          1 |      1.2 | False |
| uvicorn            | tests-released           |    29.7 |        19.9 |  0.7 |    0.85 |          1 |     1.02 | False |
| uvicorn            | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.99 | False |
| uvicorn            | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.99 | False |
| uvicorn            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.02 | False |
| uvicorn            | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.97 | False |
| uvicorn            | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     1.01 | False |
| uvicorn            | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.99 | False |
| uvicorn            | infer-union              |     8.0 |        22.6 |  2.8 |    2.25 |          3 |     2.44 | False |
| uvicorn            | tests-infer-union        |    39.7 |        21.5 |  0.5 |    0.85 |          1 |     1.02 | False |
| uvicorn            | tests                    |     1.2 |         0.2 |  0.2 |    0.03 |          1 |     0.04 | False |
| uvicorn            | types-released           |     2.0 |         1.6 |  0.8 |    0.13 |          1 |     0.09 | False |
| uvicorn            | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.15 | False |
| uvicorn            | types-infer-basedpyright |     1.0 |         0.9 |  0.9 |    0.11 |          1 |     0.17 | False |
| uvicorn            | types-infer-ty           |     3.4 |         1.7 |  0.5 |    0.13 |          1 |     0.19 | False |
| uvicorn            | types-infer-pyrefly      |     2.4 |         1.7 |  0.7 |    0.13 |          1 |     0.17 | False |
| uvicorn            | types-infer-trace        |     2.0 |         1.5 |  0.8 |    0.12 |          1 |     0.16 | False |
| uvicorn            | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| mcp                | check                    |     2.8 |         3.2 |  1.1 |    0.26 |          2 |     0.32 | False |
| mcp                | fix-certain              |     2.4 |         5.7 |  2.4 |    0.38 |          3 |     0.47 | False |
| mcp                | fix-likely               |     3.6 |         8.9 |  2.5 |    0.43 |          3 |     0.54 | False |
| mcp                | fix-unsafe               |    10.2 |         9.4 |  0.9 |    0.38 |          2 |     0.46 | False |
| mcp                | infer-basedpyright       |     6.8 |        27.1 |  4.0 |    2.22 |          5 |     3.07 | False |
| mcp                | infer-ty                 |     5.8 |        13.6 |  2.3 |    0.97 |          3 |     1.04 | False |
| mcp                | infer-pyrefly            |     3.8 |        15.9 |  4.2 |    1.97 |          5 |     2.47 | False |
| mcp                | census                   |     1.0 |         0.7 |  0.7 |    0.04 |          2 |     0.32 | False |
| mcp                | coverage                 |     0.8 |         1.4 |  1.7 |    0.18 |          2 |     0.22 | False |
| mcp                | timing                   |     2.0 |         2.6 |  1.3 |    0.26 |         16 |     0.32 | False |
| mcp                | traced                   |    21.2 |        92.1 |  4.3 |    2.04 |          6 |     2.55 | False |
| mcp                | tests-released           |    15.6 |        69.9 |  4.5 |    1.83 |          6 |     2.27 | False |
| mcp                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.24 | False |
| mcp                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.22 | False |
| mcp                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.52 | False |
| mcp                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          3 |     2.24 | False |
| mcp                | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     2.24 | False |
| mcp                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     2.24 | False |
| mcp                | infer-union              |    12.4 |        54.1 |  4.4 |    4.98 |          5 |      5.3 | False |
| mcp                | tests-infer-union        |    23.1 |        68.3 |  3.0 |    1.81 |          5 |     2.32 | False |
| mcp                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     2.24 | False |
| mcp                | types-released           |    19.3 |        26.2 |  1.4 |    1.28 |          2 |     1.59 | False |
| mcp                | types-fix-certain        |    22.4 |        24.6 |  1.1 |    1.22 |          2 |     1.56 | False |
| mcp                | types-fix-likely         |    25.4 |        27.3 |  1.1 |     1.2 |          1 |     1.51 | False |
| mcp                | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     1.54 | False |
| mcp                | types-infer-basedpyright |    23.0 |        25.5 |  1.1 |    1.19 |          2 |      1.6 | False |
| mcp                | types-infer-ty           |    19.6 |        26.7 |  1.4 |    1.25 |          2 |     1.57 | False |
| mcp                | types-infer-pyrefly      |    26.1 |        27.1 |  1.0 |    1.24 |          2 |     1.59 | False |
| mcp                | types-infer-trace        |    24.2 |        24.5 |  1.0 |    1.24 |          2 |     1.59 | False |
| mcp                | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| textual            | check                    |     3.0 |         6.9 |  2.3 |    0.45 |          2 |     0.56 | False |
| textual            | fix-certain              |     6.8 |        17.8 |  2.6 |    0.55 |          3 |     0.69 | False |
| textual            | fix-likely               |     9.2 |        24.2 |  2.6 |    0.63 |          3 |     0.79 | False |
| textual            | fix-unsafe               |     6.0 |        16.7 |  2.8 |    0.56 |          4 |      0.7 | False |
| textual            | infer-basedpyright       |    25.3 |        88.9 |  3.5 |    3.62 |          3 |     4.54 | False |
| textual            | infer-ty                 |    11.8 |        34.7 |  2.9 |    2.06 |          2 |     2.51 | False |
| textual            | infer-pyrefly            |    10.8 |        31.8 |  2.9 |    2.47 |          4 |     2.52 | False |
| textual            | census                   |     1.4 |         1.2 |  0.9 |    0.06 |          2 |     0.56 | False |
| textual            | coverage                 |     3.0 |         2.8 |  0.9 |    0.25 |          3 |     0.32 | False |
| textual            | timing                   |     4.2 |         6.2 |  1.5 |    0.45 |         16 |     0.56 | False |
| pdm                | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.54 | False |
| pdm                | fix-certain              |     3.6 |         9.3 |  2.6 |    0.46 |          3 |     0.57 | False |
| pdm                | fix-likely               |     4.8 |        13.0 |  2.7 |    0.55 |          3 |     0.67 | False |
| pdm                | fix-unsafe               |     7.0 |        12.3 |  1.8 |    0.51 |          2 |     0.64 | False |
| pdm                | infer-basedpyright       |    17.2 |        56.4 |  3.3 |    2.64 |          2 |     3.32 | False |
| pdm                | infer-ty                 |     4.4 |        13.9 |  3.2 |    1.57 |          3 |     1.97 | False |
| pdm                | infer-pyrefly            |     5.6 |        20.4 |  3.6 |    2.18 |          3 |     2.07 | False |
| pdm                | census                   |     2.6 |         4.5 |  1.7 |    0.43 |          2 |     0.54 | False |
| pdm                | coverage                 |     1.6 |         2.3 |  1.4 |    0.19 |          2 |     0.24 | False |
| pdm                | timing                   |     2.6 |         3.7 |  1.4 |    0.43 |         16 |     0.54 | False |
| pdm                | traced                   |    31.1 |       131.7 |  4.2 |    1.65 |          3 |     1.97 | False |
| pdm                | tests-released           |    15.2 |        84.3 |  5.5 |    1.29 |          7 |     1.51 | False |
| pdm                | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.72 | False |
| pdm                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     1.72 | False |
| pdm                | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.49 | False |
| pdm                | infer-union              |    10.0 |        47.8 |  4.8 |    4.18 |          5 |     6.19 | False |
| pdm                | tests-infer-union        |    18.2 |        96.8 |  5.3 |    1.19 |          7 |     1.72 | False |
| pdm                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| strawberry-graphql | check                    |     0.8 |         0.1 |  0.1 |    0.03 |          3 |     0.42 | False |
| strawberry-graphql | fix-certain              |     3.6 |         9.2 |  2.6 |    0.44 |          3 |     0.55 | False |
| strawberry-graphql | fix-likely               |     5.0 |        13.3 |  2.7 |    0.58 |          3 |     0.72 | False |
| strawberry-graphql | fix-unsafe               |    13.6 |        14.1 |  1.0 |    0.55 |          2 |     0.67 | False |
| strawberry-graphql | infer-basedpyright       |    15.9 |        79.6 |  5.0 |     3.2 |          5 |     3.91 | False |
| strawberry-graphql | infer-ty                 |     7.8 |        21.4 |  2.7 |    1.57 |          4 |     1.95 | False |
| strawberry-graphql | infer-pyrefly            |     7.0 |        33.2 |  4.7 |     1.9 |          5 |     2.71 | False |
| strawberry-graphql | census                   |     1.6 |         3.2 |  2.0 |    0.34 |          3 |     0.42 | False |
| strawberry-graphql | coverage                 |     1.0 |         1.7 |  1.7 |    0.19 |          2 |     0.22 | False |
| strawberry-graphql | timing                   |     2.6 |         3.7 |  1.4 |    0.35 |         16 |     0.42 | False |
| strawberry-graphql | traced                   |    17.9 |        97.9 |  5.5 |    1.49 |          8 |     1.86 | False |
| strawberry-graphql | tests-released           |    15.4 |        71.1 |  4.6 |    1.26 |          8 |     1.56 | False |
| strawberry-graphql | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.56 | False |
| strawberry-graphql | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.54 | False |
| strawberry-graphql | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     1.52 | False |
| strawberry-graphql | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.54 | False |
| strawberry-graphql | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.55 | False |
| strawberry-graphql | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.54 | False |
| strawberry-graphql | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.54 | False |
| strawberry-graphql | infer-union              |    13.2 |        87.7 |  6.6 |    5.33 |          8 |     6.64 | False |
| strawberry-graphql | tests-infer-union        |    12.4 |        78.8 |  6.4 |    1.25 |          8 |     1.62 | False |
| strawberry-graphql | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.55 | False |
| strawberry-graphql | types-released           |     2.4 |         1.8 |  0.8 |    0.23 |          1 |     0.14 | False |
| strawberry-graphql | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.25 | False |
| strawberry-graphql | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-basedpyright |     2.0 |         1.4 |  0.7 |    0.19 |          1 |     0.29 | False |
| strawberry-graphql | types-infer-ty           |     2.8 |         2.0 |  0.7 |    0.24 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-pyrefly      |     1.6 |         1.2 |  0.7 |    0.24 |          1 |     0.24 | False |
| strawberry-graphql | types-infer-trace        |     1.4 |         1.1 |  0.8 |    0.25 |          1 |      0.3 | False |
| strawberry-graphql | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| pygments           | check                    |     3.2 |         6.6 |  2.1 |    0.43 |          3 |     0.54 | False |
| pygments           | fix-certain              |     8.2 |        18.3 |  2.2 |    0.61 |          3 |     0.74 | False |
| pygments           | fix-likely               |    10.6 |        22.0 |  2.1 |     0.6 |          3 |     0.74 | False |
| pygments           | fix-unsafe               |    15.8 |        19.4 |  1.2 |     0.6 |          2 |     0.74 | False |
| pygments           | infer-basedpyright       |    29.1 |        88.3 |  3.0 |    2.37 |          4 |     2.94 | False |
| pygments           | infer-ty                 |    13.8 |        28.1 |  2.0 |    1.65 |          3 |      1.5 | False |
| pygments           | infer-pyrefly            |    11.4 |        30.2 |  2.6 |     2.1 |          3 |     2.04 | False |
| pygments           | census                   |     4.0 |         2.6 |  0.7 |    0.06 |          3 |     0.54 | False |
| pygments           | coverage                 |     3.4 |         2.6 |  0.8 |    0.29 |          3 |     0.36 | False |
| pygments           | timing                   |     4.2 |         6.2 |  1.5 |    0.43 |         16 |     0.54 | False |
| pygments           | traced                   |    41.5 |        38.7 |  0.9 |    0.62 |          1 |     0.84 | False |
| pygments           | tests-released           |    15.1 |        12.8 |  0.8 |    0.29 |          1 |     0.35 | False |
| pygments           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      0.3 | False |
| pygments           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.35 | False |
| pygments           | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.3 | False |
| pygments           | infer-union              |    44.3 |       123.7 |  2.8 |    6.46 |          4 |      6.9 | False |
| pygments           | tests-infer-union        |    18.4 |        15.0 |  0.8 |    0.29 |          1 |     0.36 | False |
| pygments           | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      0.3 | False |
| streamlink         | check                    |     2.8 |         5.3 |  1.9 |    0.32 |          2 |      0.4 | False |
| streamlink         | fix-certain              |     4.8 |        12.5 |  2.6 |    0.46 |          3 |     0.57 | False |
| streamlink         | fix-likely               |     7.6 |        17.7 |  2.3 |    0.49 |          3 |     0.61 | False |
| streamlink         | fix-unsafe               |    13.7 |        11.2 |  0.8 |     0.5 |          3 |      0.6 | False |
| streamlink         | infer-basedpyright       |    12.2 |        42.5 |  3.5 |    2.51 |          4 |     3.72 | False |
| streamlink         | infer-ty                 |     8.6 |        24.5 |  2.8 |    1.53 |          4 |     1.95 | False |
| streamlink         | infer-pyrefly            |     5.4 |        21.6 |  4.0 |    1.68 |          4 |     2.61 | False |
| streamlink         | census                   |     3.4 |         1.3 |  0.4 |    0.05 |          2 |      0.4 | False |
| streamlink         | coverage                 |     1.0 |         1.9 |  1.9 |    0.22 |          2 |     0.27 | False |
| streamlink         | timing                   |     3.4 |         4.8 |  1.4 |    0.32 |         16 |      0.4 | False |
| streamlink         | traced                   |    32.1 |        23.7 |  0.7 |    0.41 |          1 |     0.54 | False |
| streamlink         | tests-released           |    12.7 |        10.7 |  0.8 |     0.2 |          1 |     0.22 | False |
| streamlink         | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.25 | False |
| streamlink         | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.22 | False |
| streamlink         | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.22 | False |
| streamlink         | infer-union              |    20.9 |        91.2 |  4.4 |    5.46 |          5 |      5.4 | False |
| streamlink         | tests-infer-union        |    14.9 |        12.2 |  0.8 |     0.2 |          1 |     0.25 | False |
| streamlink         | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.22 | False |
| streamlink         | types-released           |     7.2 |         5.6 |  0.8 |    0.35 |          1 |     0.49 | False |
| streamlink         | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.44 | False |
| streamlink         | types-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.44 | False |
| streamlink         | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.51 | False |
| streamlink         | types-infer-basedpyright |     4.8 |         4.5 |  0.9 |    0.37 |          1 |     0.46 | False |
| streamlink         | types-infer-ty           |     8.2 |         7.0 |  0.9 |    0.36 |          1 |     0.45 | False |
| streamlink         | types-infer-pyrefly      |     6.4 |         5.3 |  0.8 |    0.39 |          1 |     0.49 | False |
| streamlink         | types-infer-trace        |     9.4 |         7.2 |  0.8 |    0.39 |          1 |      0.5 | False |
| streamlink         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| sphinx             | check                    |     3.2 |         8.1 |  2.5 |    0.46 |          3 |     0.57 | False |
| sphinx             | fix-certain              |     7.8 |        23.8 |  3.1 |    0.65 |          3 |     0.79 | False |
| sphinx             | fix-likely               |     9.8 |        29.8 |  3.0 |    0.84 |          4 |     1.06 | False |
| sphinx             | fix-unsafe               |    18.2 |        28.8 |  1.6 |    0.69 |          2 |     0.85 | False |
| sphinx             | infer-basedpyright       |    31.1 |       106.3 |  3.4 |    4.35 |          4 |      5.3 | False |
| sphinx             | infer-ty                 |    12.3 |        40.0 |  3.3 |    1.65 |          4 |     2.77 | False |
| sphinx             | infer-pyrefly            |    12.0 |        37.5 |  3.1 |    2.01 |          4 |     2.56 | False |
| sphinx             | census                   |     2.0 |         1.8 |  0.9 |    0.07 |          3 |     0.57 | False |
| sphinx             | coverage                 |     3.4 |         3.6 |  1.1 |    0.28 |          3 |     0.35 | False |
| sphinx             | timing                   |     5.8 |         8.6 |  1.5 |    0.46 |         16 |     0.57 | False |
| sphinx             | traced                   |    30.2 |       156.6 |  5.2 |    1.68 |          8 |     2.12 | False |
| sphinx             | tests-released           |    17.0 |       118.2 |  7.0 |    1.35 |          8 |     1.67 | False |
| sphinx             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     1.66 | False |
| sphinx             | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     1.65 | False |
| sphinx             | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     1.64 | False |
| sphinx             | tests-infer-basedpyright |    14.0 |        97.9 |  7.0 |    1.33 |          8 |     1.66 | False |
| sphinx             | tests-infer-ty           |    15.6 |       103.5 |  6.6 |    1.33 |          8 |     1.65 | False |
| sphinx             | tests-infer-pyrefly      |    16.0 |       105.2 |  6.6 |    1.32 |          7 |     1.65 | False |
| sphinx             | tests-infer-trace        |    14.6 |       101.7 |  7.0 |    1.32 |          6 |     1.65 | False |
| sphinx             | infer-union              |    24.5 |        98.7 |  4.0 |    6.18 |          4 |     8.14 | False |
| sphinx             | tests-infer-union        |    13.4 |        96.9 |  7.2 |    1.32 |          6 |     1.69 | False |
| sphinx             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |      1.8 | False |
| sphinx             | types-released           |     0.8 |         0.4 |  0.5 |    0.08 |          1 |     0.32 | False |
| sphinx             | types-fix-certain        |     5.6 |         5.4 |  1.0 |    0.26 |          1 |     0.32 | False |
| sphinx             | types-fix-likely         |     9.0 |         6.9 |  0.8 |    0.26 |          1 |     0.32 | False |
| sphinx             | types-fix-unsafe         |     0.4 |         0.3 |  0.7 |    0.04 |          1 |     0.32 | False |
| sphinx             | types-infer-basedpyright |     8.4 |         6.3 |  0.8 |    0.29 |          1 |     0.31 | False |
| sphinx             | types-infer-ty           |     8.6 |         6.9 |  0.8 |    0.34 |          1 |     0.42 | False |
| sphinx             | types-infer-pyrefly      |     5.8 |         5.4 |  0.9 |    0.25 |          1 |     0.36 | False |
| sphinx             | types-infer-trace        |     6.0 |         5.4 |  0.9 |    0.32 |          1 |      0.4 | False |
| sphinx             | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| tox                | check                    |     0.8 |         0.2 |  0.2 |    0.03 |          2 |      0.3 | False |
| tox                | fix-certain              |     2.6 |         6.5 |  2.5 |    0.35 |          3 |     0.42 | False |
| tox                | fix-likely               |     3.2 |         8.0 |  2.5 |    0.38 |          3 |     0.47 | False |
| tox                | fix-unsafe               |     7.8 |         7.9 |  1.0 |    0.34 |          2 |     0.46 | False |
| tox                | infer-basedpyright       |    11.6 |        41.9 |  3.6 |    2.25 |          4 |      2.8 | False |
| tox                | infer-ty                 |     5.2 |        16.1 |  3.1 |    1.28 |          2 |     1.59 | False |
| tox                | infer-pyrefly            |     5.2 |        13.2 |  2.5 |    1.41 |          3 |     1.75 | False |
| tox                | census                   |     4.4 |         3.6 |  0.8 |    0.25 |          2 |      0.3 | False |
| tox                | coverage                 |     1.4 |         1.5 |  1.1 |    0.17 |          2 |     0.21 | False |
| tox                | timing                   |     1.8 |         2.5 |  1.4 |    0.24 |         16 |      0.3 | False |
| tox                | traced                   |    23.5 |       120.6 |  5.1 |    1.52 |          7 |     1.89 | False |
| tox                | tests-released           |    18.4 |        99.2 |  5.4 |    1.35 |          7 |      1.7 | False |
| tox                | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     1.64 | False |
| tox                | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.66 | False |
| tox                | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          7 |     1.64 | False |
| tox                | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     1.65 | False |
| tox                | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.65 | False |
| tox                | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     1.62 | False |
| tox                | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          5 |      1.7 | False |
| tox                | infer-union              |     7.8 |        34.8 |  4.5 |    3.94 |          4 |     4.11 | False |
| tox                | tests-infer-union        |    20.2 |       110.4 |  5.5 |    1.36 |          6 |     1.76 | False |
| tox                | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     1.66 | False |
| pint               | check                    |     3.0 |         4.8 |  1.6 |    0.39 |          2 |     0.49 | False |
| pint               | fix-certain              |     5.4 |        11.1 |  2.1 |    0.43 |          2 |     0.54 | False |
| pint               | fix-likely               |     7.4 |        14.6 |  2.0 |    0.52 |          2 |     0.65 | False |
| pint               | fix-unsafe               |     6.0 |        11.3 |  1.9 |    0.44 |          3 |     0.55 | False |
| pint               | infer-basedpyright       |    55.1 |        92.4 |  1.7 |    2.46 |          3 |     4.09 | False |
| pint               | infer-ty                 |    10.8 |        23.7 |  2.2 |    2.03 |          3 |     1.76 | False |
| pint               | infer-pyrefly            |     6.6 |        26.6 |  4.0 |     1.4 |          4 |     2.27 | False |
| pint               | census                   |     1.4 |         1.1 |  0.8 |    0.05 |          2 |     0.49 | False |
| pint               | coverage                 |     1.0 |         1.6 |  1.6 |     0.2 |          2 |     0.25 | False |
| pint               | timing                   |     3.0 |         4.0 |  1.3 |    0.39 |         16 |     0.49 | False |
| pint               | traced                   |    38.5 |        43.9 |  1.1 |    0.45 |          1 |     0.56 | False |
| pint               | tests-released           |    28.6 |        25.7 |  0.9 |    0.15 |          1 |     0.17 | False |
| pint               | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.17 | False |
| pint               | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.17 | False |
| pint               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.17 | False |
| pint               | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.16 | False |
| pint               | infer-union              |    28.5 |       128.7 |  4.5 |    7.05 |          4 |     6.46 | False |
| pint               | tests-infer-union        |    35.7 |        30.5 |  0.9 |    0.15 |          1 |     0.19 | False |
| pint               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| pint               | types-released           |     6.8 |        10.2 |  1.5 |    0.54 |          2 |     0.67 | False |
| pint               | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.66 | False |
| pint               | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.65 | False |
| pint               | types-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     0.67 | False |
| pint               | types-infer-basedpyright |     5.4 |         9.1 |  1.7 |    0.54 |          2 |     0.67 | False |
| pint               | types-infer-ty           |     6.8 |         9.9 |  1.5 |    0.53 |          2 |     0.67 | False |
| pint               | types-infer-pyrefly      |     4.4 |         7.1 |  1.6 |    0.54 |          2 |     0.69 | False |
| pint               | types-infer-trace        |     6.2 |        10.0 |  1.6 |    0.55 |          1 |     0.72 | False |
| pint               | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| altair             | check                    |     3.4 |         4.9 |  1.4 |    0.68 |          2 |     0.85 | False |
| altair             | fix-certain              |     8.8 |        14.2 |  1.6 |    0.75 |          2 |     0.92 | False |
| altair             | fix-likely               |    10.2 |        16.6 |  1.6 |    0.83 |          2 |     1.04 | False |
| altair             | fix-unsafe               |    12.4 |        17.2 |  1.4 |    0.93 |          2 |     0.92 | False |
| altair             | infer-basedpyright       |    36.3 |        71.1 |  2.0 |    2.81 |          2 |     3.47 | False |
| altair             | infer-ty                 |    15.4 |        24.7 |  1.6 |    1.52 |          2 |     2.32 | False |
| altair             | infer-pyrefly            |    16.3 |        27.4 |  1.7 |    1.92 |          2 |     2.42 | False |
| altair             | census                   |     2.2 |         1.0 |  0.5 |     0.1 |          2 |     0.85 | False |
| altair             | coverage                 |     2.4 |         2.5 |  1.0 |    0.27 |          2 |     0.34 | False |
| altair             | timing                   |     3.8 |         4.7 |  1.2 |    0.69 |         16 |     0.86 | False |
| altair             | traced                   |    33.5 |       166.4 |  5.0 |    6.31 |          4 |     7.82 | False |
| altair             | tests-released           |    22.2 |       148.0 |  6.7 |    4.25 |          8 |     5.84 | False |
| altair             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.82 | False |
| altair             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.82 | False |
| altair             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.69 | False |
| altair             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     6.16 | False |
| altair             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     5.61 | False |
| altair             | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          6 |      5.9 | False |
| altair             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.81 | False |
| altair             | infer-union              |    45.9 |        72.9 |  1.6 |    3.77 |          3 |     4.09 | False |
| altair             | tests-infer-union        |    23.0 |       152.1 |  6.6 |    4.92 |          7 |      7.7 | False |
| altair             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.46 | False |
| altair             | types-released           |     0.6 |         0.4 |  0.7 |    0.09 |          1 |     0.54 | False |
| altair             | types-fix-certain        |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.47 | False |
| altair             | types-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.47 | False |
| altair             | types-fix-unsafe         |     7.4 |         4.3 |  0.6 |    0.37 |          1 |     0.46 | False |
| altair             | types-infer-basedpyright |     7.0 |         6.5 |  0.9 |    0.38 |          1 |     0.47 | False |
| altair             | types-infer-ty           |     8.9 |         7.0 |  0.8 |    0.42 |          1 |     0.52 | False |
| altair             | types-infer-pyrefly      |     5.4 |         5.2 |  1.0 |    0.38 |          1 |      0.5 | False |
| altair             | types-infer-trace        |     8.6 |         6.1 |  0.7 |     0.4 |          1 |     0.54 | False |
| altair             | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| seaborn            | check                    |     3.8 |         6.1 |  1.6 |    0.42 |          2 |     0.52 | False |
| seaborn            | fix-certain              |     6.0 |        11.7 |  1.9 |    0.47 |          1 |     0.59 | False |
| seaborn            | fix-likely               |     7.4 |        17.0 |  2.3 |    0.58 |          3 |     0.72 | False |
| seaborn            | fix-unsafe               |    13.8 |        14.7 |  1.1 |    0.57 |          2 |     0.59 | False |
| seaborn            | infer-basedpyright       |    39.3 |        96.1 |  2.4 |    3.07 |          2 |     3.67 | False |
| seaborn            | infer-ty                 |     9.6 |        23.9 |  2.5 |    1.25 |          3 |     1.56 | False |
| seaborn            | infer-pyrefly            |    14.6 |        26.2 |  1.8 |    1.68 |          2 |     2.05 | False |
| seaborn            | census                   |     1.2 |         0.9 |  0.8 |    0.05 |          2 |     0.52 | False |
| seaborn            | coverage                 |     0.8 |         1.4 |  1.7 |    0.19 |          2 |     0.24 | False |
| seaborn            | timing                   |     3.6 |         4.8 |  1.3 |    0.42 |         16 |     0.52 | False |
| seaborn            | traced                   |    72.4 |       597.3 |  8.2 |    4.97 |          6 |      6.3 | False |
| seaborn            | tests-released           |    54.8 |       531.9 |  9.7 |    4.78 |          8 |     6.09 | False |
| seaborn            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.09 | False |
| seaborn            | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.97 | False |
| seaborn            | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.99 | False |
| seaborn            | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          7 |      6.0 | False |
| seaborn            | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.92 | False |
| seaborn            | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      5.9 | False |
| seaborn            | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     6.02 | False |
| seaborn            | infer-union              |    60.6 |        67.4 |  1.1 |    4.31 |          3 |     5.32 | False |
| seaborn            | tests-infer-union        |    61.7 |       558.8 |  9.1 |     4.7 |          8 |     6.07 | False |
| seaborn            | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     6.05 | False |
| seaborn            | types-released           |     1.6 |         1.2 |  0.7 |    0.17 |          1 |     0.09 | False |
| seaborn            | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.17 | False |
| seaborn            | types-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| seaborn            | types-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.19 | False |
| seaborn            | types-infer-basedpyright |     1.0 |         0.7 |  0.7 |    0.14 |          1 |     0.21 | False |
| seaborn            | types-infer-ty           |     2.0 |         1.2 |  0.6 |    0.17 |          1 |      0.2 | False |
| seaborn            | types-infer-pyrefly      |     1.6 |         1.2 |  0.7 |    0.16 |          1 |     0.21 | False |
| seaborn            | types-infer-trace        |     1.0 |         0.7 |  0.7 |    0.16 |          1 |     0.24 | False |
| seaborn            | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| aiohttp            | check                    |     0.8 |         0.2 |  0.2 |    0.03 |          2 |      0.3 | False |
| aiohttp            | fix-certain              |     3.6 |         7.9 |  2.2 |    0.36 |          3 |     0.47 | False |
| aiohttp            | fix-likely               |    11.8 |        13.0 |  1.1 |    0.42 |          2 |     0.54 | False |
| aiohttp            | fix-unsafe               |     5.8 |         9.1 |  1.6 |    0.38 |          2 |     0.45 | False |
| aiohttp            | infer-basedpyright       |    12.8 |        31.0 |  2.4 |    1.49 |          2 |     2.16 | False |
| aiohttp            | infer-ty                 |    15.1 |        17.0 |  1.1 |    0.99 |          2 |     0.89 | False |
| aiohttp            | infer-pyrefly            |    14.2 |        15.2 |  1.1 |     1.0 |          2 |     1.24 | False |
| aiohttp            | census                   |     5.6 |         4.1 |  0.7 |    0.24 |          2 |      0.3 | False |
| aiohttp            | coverage                 |     0.8 |         1.6 |  2.0 |    0.18 |          2 |     0.22 | False |
| aiohttp            | timing                   |     2.2 |         2.9 |  1.3 |    0.24 |         16 |      0.3 | False |
| aiohttp            | traced                   |    94.4 |       746.9 |  7.9 |    2.95 |          1 |      3.7 | False |
| aiohttp            | tests-released           |    79.0 |       601.9 |  7.6 |    2.59 |          1 |     3.22 | False |
| aiohttp            | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |      3.2 | False |
| aiohttp            | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     3.24 | False |
| aiohttp            | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.24 | False |
| aiohttp            | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     3.22 | False |
| aiohttp            | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.21 | False |
| aiohttp            | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      3.2 | False |
| aiohttp            | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     3.19 | False |
| aiohttp            | infer-union              |    20.9 |        49.8 |  2.4 |    3.11 |          3 |     3.01 | False |
| aiohttp            | tests-infer-union        |    85.6 |       658.7 |  7.7 |    2.55 |          1 |     3.21 | False |
| aiohttp            | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      3.2 | False |
| websockets         | check                    |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     0.26 | False |
| websockets         | fix-certain              |     3.4 |         5.2 |  1.5 |    0.33 |          3 |      0.4 | False |
| websockets         | fix-likely               |     2.2 |         5.0 |  2.3 |    0.31 |          3 |     0.36 | False |
| websockets         | fix-unsafe               |     7.8 |         6.0 |  0.8 |    0.32 |          2 |      0.4 | False |
| websockets         | infer-basedpyright       |     7.2 |        21.4 |  3.0 |    0.98 |          3 |     1.24 | False |
| websockets         | infer-ty                 |     3.4 |         7.8 |  2.3 |    0.71 |          3 |     0.81 | False |
| websockets         | infer-pyrefly            |     3.8 |         8.1 |  2.1 |    0.74 |          3 |     0.65 | False |
| websockets         | census                   |     1.2 |         1.8 |  1.5 |     0.2 |          2 |     0.26 | False |
| websockets         | coverage                 |     2.2 |         1.3 |  0.6 |    0.16 |          1 |      0.2 | False |
| websockets         | timing                   |     1.2 |         1.6 |  1.3 |    0.21 |         16 |     0.26 | False |
| websockets         | traced                   |    35.3 |        12.1 |  0.3 |    0.33 |          1 |     0.42 | False |
| websockets         | tests-released           |    26.9 |         5.0 |  0.2 |    0.16 |          1 |     0.17 | False |
| websockets         | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.17 | False |
| websockets         | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.15 | False |
| websockets         | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          1 |      0.2 | False |
| websockets         | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.19 | False |
| websockets         | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.16 | False |
| websockets         | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.16 | False |
| websockets         | infer-union              |    11.8 |        33.7 |  2.9 |    2.03 |          3 |     2.21 | False |
| websockets         | tests-infer-union        |    29.1 |         5.9 |  0.2 |    0.16 |          1 |     0.19 | False |
| websockets         | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| websockets         | types-released           |     1.2 |         0.8 |  0.7 |    0.12 |          1 |     0.07 | False |
| websockets         | types-fix-certain        |     0.8 |         0.6 |  0.7 |    0.11 |          1 |     0.14 | False |
| websockets         | types-fix-likely         |     1.2 |         0.9 |  0.8 |    0.11 |          1 |     0.15 | False |
| websockets         | types-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.12 | False |
| websockets         | types-infer-basedpyright |     1.0 |         0.8 |  0.8 |    0.11 |          1 |     0.15 | False |
| websockets         | types-infer-ty           |     1.6 |         1.0 |  0.6 |     0.1 |          1 |     0.14 | False |
| websockets         | types-infer-pyrefly      |     3.0 |         1.1 |  0.4 |    0.12 |          1 |     0.12 | False |
| websockets         | types-infer-trace        |     1.2 |         0.8 |  0.7 |    0.11 |          1 |     0.14 | False |
| websockets         | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| anyio              | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          2 |     0.26 | False |
| anyio              | fix-certain              |     3.8 |         5.8 |  1.5 |    0.29 |          2 |      0.4 | False |
| anyio              | fix-likely               |     4.4 |         6.2 |  1.4 |    0.33 |          1 |     0.41 | False |
| anyio              | fix-unsafe               |     5.8 |         5.6 |  1.0 |    0.33 |          2 |     0.37 | False |
| anyio              | infer-basedpyright       |     9.4 |        21.0 |  2.2 |    0.98 |          3 |     1.22 | False |
| anyio              | infer-ty                 |     5.6 |         8.4 |  1.5 |    0.79 |          2 |     0.66 | False |
| anyio              | infer-pyrefly            |     4.6 |        12.4 |  2.7 |    0.97 |          4 |     0.99 | False |
| anyio              | census                   |     1.4 |         1.9 |  1.4 |    0.21 |          2 |     0.26 | False |
| anyio              | coverage                 |     1.2 |         1.2 |  1.0 |    0.16 |          2 |      0.2 | False |
| anyio              | timing                   |     1.4 |         1.6 |  1.1 |    0.21 |         16 |     0.26 | False |
| anyio              | traced                   |   130.1 |        56.1 |  0.4 |    0.34 |          1 |     0.46 | False |
| anyio              | tests-released           |   125.3 |        48.2 |  0.4 |    0.27 |          1 |     0.32 | False |
| anyio              | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.31 | False |
| anyio              | tests-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.31 | False |
| anyio              | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.36 | False |
| anyio              | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.31 | False |
| anyio              | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.32 | False |
| anyio              | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.31 | False |
| anyio              | infer-union              |    11.7 |        30.2 |  2.6 |    2.56 |          3 |     2.82 | False |
| anyio              | tests-infer-union        |    97.1 |        47.6 |  0.5 |    0.27 |          1 |     0.34 | False |
| anyio              | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| zarr               | check                    |     0.6 |         0.2 |  0.3 |    0.04 |          2 |      0.4 | False |
| zarr               | fix-certain              |     4.6 |        10.6 |  2.3 |    0.41 |          3 |     0.55 | False |
| zarr               | fix-likely               |     5.0 |        13.1 |  2.6 |    0.58 |          3 |     0.72 | False |
| zarr               | fix-unsafe               |     8.2 |        11.8 |  1.4 |     0.5 |          2 |     0.62 | False |
| zarr               | infer-basedpyright       |    19.5 |        55.4 |  2.8 |    2.62 |          4 |     3.27 | False |
| zarr               | infer-ty                 |     6.8 |        19.1 |  2.8 |    1.58 |          3 |     2.02 | False |
| zarr               | infer-pyrefly            |     9.2 |        26.0 |  2.8 |    2.17 |          4 |     2.55 | False |
| zarr               | census                   |     2.6 |         4.7 |  1.8 |    0.32 |          2 |      0.4 | False |
| zarr               | coverage                 |     2.2 |         2.1 |  1.0 |     0.2 |          2 |     0.25 | False |
| zarr               | timing                   |     2.6 |         3.6 |  1.4 |    0.32 |         16 |      0.4 | False |
| zarr               | traced                   |   105.6 |       252.3 |  2.4 |    2.63 |          3 |      3.0 | False |
| zarr               | tests-released           |   106.4 |       235.8 |  2.2 |    2.27 |          3 |     2.94 | False |
| zarr               | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          3 |     2.94 | False |
| zarr               | tests-fix-likely         |     0.6 |         0.1 |  0.2 |    0.03 |          3 |     2.94 | False |
| zarr               | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     2.91 | False |
| zarr               | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          4 |      3.0 | False |
| zarr               | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          3 |     2.94 | False |
| zarr               | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          3 |     2.87 | False |
| zarr               | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          3 |     2.97 | False |
| zarr               | infer-union              |    24.5 |        87.4 |  3.6 |    5.96 |          3 |     6.24 | False |
| zarr               | tests-infer-union        |    98.2 |       221.1 |  2.3 |    2.36 |          2 |     2.97 | False |
| zarr               | tests                    |     0.6 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| joblib             | check                    |     1.6 |         0.2 |  0.1 |    0.03 |          2 |      0.4 | False |
| joblib             | fix-certain              |     4.0 |         8.0 |  2.0 |    0.38 |          1 |     0.47 | False |
| joblib             | fix-likely               |     5.4 |         9.6 |  1.8 |     0.4 |          2 |     0.54 | False |
| joblib             | fix-unsafe               |     9.7 |         9.6 |  1.0 |    0.38 |          3 |     0.47 | False |
| joblib             | infer-basedpyright       |    21.5 |        53.0 |  2.5 |     1.9 |          3 |     2.45 | False |
| joblib             | infer-ty                 |     6.2 |        13.9 |  2.2 |    1.11 |          3 |      1.4 | False |
| joblib             | infer-pyrefly            |    16.1 |        12.4 |  0.8 |    1.17 |          3 |     1.46 | False |
| joblib             | census                   |     3.8 |         4.3 |  1.1 |    0.32 |          2 |      0.4 | False |
| joblib             | coverage                 |     1.0 |         1.3 |  1.3 |    0.18 |          2 |     0.22 | False |
| joblib             | timing                   |     2.4 |         3.1 |  1.3 |    0.32 |         16 |      0.4 | False |
| joblib             | traced                   |   156.1 |       504.7 |  3.2 |     1.1 |          1 |     1.34 | False |
| joblib             | tests-released           |   157.6 |       496.1 |  3.1 |    1.08 |          1 |     1.35 | False |
| joblib             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-fix-likely         |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     1.37 | False |
| joblib             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.31 | False |
| joblib             | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          1 |      1.3 | False |
| joblib             | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     1.31 | False |
| joblib             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     1.32 | False |
| joblib             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     1.35 | False |
| joblib             | infer-union              |    24.3 |        69.9 |  2.9 |    4.38 |          3 |     4.95 | False |
| joblib             | tests-infer-union        |   166.8 |       428.7 |  2.6 |    1.07 |          1 |     1.37 | False |
| joblib             | tests                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| networkx           | check                    |     2.4 |         0.4 |  0.2 |    0.07 |          3 |     1.25 | False |
| networkx           | fix-certain              |    12.4 |        40.1 |  3.2 |    1.21 |          3 |      1.5 | False |
| networkx           | fix-likely               |    21.7 |        62.5 |  2.9 |    1.84 |          3 |      2.3 | False |
| networkx           | fix-unsafe               |    15.4 |        43.0 |  2.8 |    1.27 |          3 |     1.59 | False |
| networkx           | infer-basedpyright       |    76.3 |       300.8 |  3.9 |     9.3 |          4 |    10.91 | False |
| networkx           | infer-ty                 |    25.9 |        85.0 |  3.3 |    3.01 |          4 |     4.45 | False |
| networkx           | infer-pyrefly            |    33.5 |       101.8 |  3.0 |    4.72 |          4 |     5.75 | False |
| networkx           | census                   |    10.4 |        21.6 |  2.1 |     1.0 |          3 |     1.25 | False |
| networkx           | coverage                 |     2.8 |         6.3 |  2.2 |     0.4 |          3 |     0.51 | False |
| networkx           | timing                   |    12.2 |        18.5 |  1.5 |    1.01 |         16 |     1.26 | False |
| networkx           | traced                   |    39.9 |       269.3 |  6.7 |    2.55 |          8 |     3.19 | False |
| networkx           | tests-released           |    26.8 |       236.0 |  8.8 |    2.35 |          8 |     2.91 | False |
| networkx           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.96 | False |
| networkx           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.89 | False |
| networkx           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.65 | False |
| networkx           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      2.9 | False |
| networkx           | tests-infer-ty           |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     2.94 | False |
| networkx           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |      2.9 | False |
| networkx           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.87 | False |
| networkx           | infer-union              |    82.4 |       310.0 |  3.8 |   11.57 |          4 |    13.74 | False |
| networkx           | tests-infer-union        |    25.9 |       222.1 |  8.6 |    2.35 |          8 |     2.96 | False |
| networkx           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| networkx           | types-released           |     4.2 |         3.1 |  0.7 |    0.33 |          1 |      0.1 | False |
| networkx           | types-fix-certain        |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.39 | False |
| networkx           | types-fix-likely         |     4.6 |         3.4 |  0.7 |    0.28 |          1 |     0.35 | False |
| networkx           | types-fix-unsafe         |     0.6 |         0.3 |  0.5 |    0.04 |          1 |     0.39 | False |
| networkx           | types-infer-basedpyright |     5.6 |         3.5 |  0.6 |    0.33 |          1 |     0.37 | False |
| networkx           | types-infer-ty           |     2.6 |         2.3 |  0.9 |    0.33 |          1 |     0.37 | False |
| networkx           | types-infer-pyrefly      |     2.8 |         2.6 |  0.9 |    0.34 |          1 |     0.42 | False |
| networkx           | types-infer-trace        |     3.0 |         2.8 |  0.9 |    0.31 |          1 |     0.41 | False |
| networkx           | types                    |     0.6 |         0.2 |  0.3 |    0.03 |          1 |     0.04 | False |
| nibabel            | check                    |     3.8 |         9.2 |  2.4 |     0.6 |          3 |     0.75 | False |
| nibabel            | fix-certain              |     9.4 |        24.1 |  2.6 |     0.7 |          3 |     0.87 | False |
| nibabel            | fix-likely               |    15.4 |        35.8 |  2.3 |    0.96 |          3 |      1.2 | False |
| nibabel            | fix-unsafe               |    13.4 |        27.8 |  2.1 |    0.72 |          3 |      0.9 | False |
| nibabel            | infer-basedpyright       |    71.2 |       260.2 |  3.7 |    5.86 |          3 |     6.85 | False |
| nibabel            | infer-ty                 |    29.7 |       101.9 |  3.4 |    2.77 |          4 |     2.69 | False |
| nibabel            | infer-pyrefly            |    22.1 |        70.1 |  3.2 |    3.34 |          3 |     3.54 | False |
| nibabel            | census                   |     2.0 |         1.8 |  0.9 |    0.06 |          3 |     0.75 | False |
| nibabel            | coverage                 |     1.0 |         2.2 |  2.2 |    0.25 |          3 |     0.32 | False |
| nibabel            | timing                   |     7.2 |        10.4 |  1.4 |     0.6 |         16 |     0.75 | False |
| nibabel            | traced                   |    26.7 |       112.2 |  4.2 |    1.14 |          6 |     1.42 | False |
| nibabel            | tests-released           |    15.2 |        90.2 |  5.9 |    1.04 |          7 |     1.31 | False |
| nibabel            | tests-fix-certain        |    18.2 |        88.3 |  4.9 |    1.02 |          8 |     1.26 | False |
| nibabel            | tests-fix-likely         |    19.8 |        86.1 |  4.3 |    1.02 |          8 |     1.29 | False |
| nibabel            | tests-fix-unsafe         |    13.1 |        91.8 |  7.0 |    1.02 |          8 |     1.26 | False |
| nibabel            | tests-infer-basedpyright |    17.6 |        86.6 |  4.9 |    1.03 |          8 |      1.3 | False |
| nibabel            | tests-infer-ty           |    12.9 |        89.1 |  6.9 |    1.03 |          8 |     1.26 | False |
| nibabel            | tests-infer-pyrefly      |    14.4 |        89.0 |  6.2 |    1.04 |          8 |     1.26 | False |
| nibabel            | tests-infer-trace        |    13.8 |        86.1 |  6.2 |    1.02 |          8 |      1.3 | False |
| nibabel            | infer-union              |    63.0 |       278.4 |  4.4 |    8.56 |          5 |    10.45 | False |
| nibabel            | tests-infer-union        |    14.2 |        87.0 |  6.1 |    1.05 |          8 |     1.29 | False |
| nibabel            | tests                    |   108.1 |       611.5 |  5.7 |    1.06 |          5 |     1.35 | False |
| nibabel            | types-released           |     0.6 |         0.3 |  0.5 |    0.06 |          1 |     0.22 | False |
| nibabel            | types-fix-certain        |     2.4 |         2.1 |  0.9 |    0.16 |          1 |      0.2 | False |
| nibabel            | types-fix-likely         |     2.6 |         1.9 |  0.7 |    0.15 |          1 |     0.19 | False |
| nibabel            | types-fix-unsafe         |     2.4 |         1.5 |  0.6 |    0.13 |          1 |     0.16 | False |
| nibabel            | types-infer-basedpyright |     3.0 |         2.3 |  0.8 |    0.16 |          1 |     0.21 | False |
| nibabel            | types-infer-ty           |     2.0 |         1.8 |  0.9 |    0.16 |          1 |     0.22 | False |
| nibabel            | types-infer-pyrefly      |     3.2 |         2.5 |  0.8 |    0.18 |          1 |     0.22 | False |
| nibabel            | types-infer-trace        |     3.6 |         2.4 |  0.7 |    0.16 |          1 |     0.24 | False |
| nibabel            | types                    |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.04 | False |
| narwhals           | check                    |     0.4 |         0.2 |  0.5 |    0.04 |          3 |     0.51 | False |
| narwhals           | fix-certain              |     6.0 |        14.7 |  2.4 |    0.42 |          2 |     0.52 | False |
| narwhals           | fix-likely               |     7.8 |        20.4 |  2.6 |    0.86 |          3 |     1.07 | False |
| narwhals           | fix-unsafe               |    11.4 |        20.1 |  1.8 |    0.85 |          2 |     1.07 | False |
| narwhals           | infer-basedpyright       |    28.7 |       106.7 |  3.7 |    3.57 |          5 |     4.44 | False |
| narwhals           | infer-ty                 |     9.8 |        32.5 |  3.3 |    2.64 |          4 |     2.92 | False |
| narwhals           | infer-pyrefly            |    14.1 |        35.8 |  2.5 |     3.2 |          4 |     3.55 | False |
| narwhals           | census                   |     3.2 |         6.1 |  1.9 |    0.41 |          3 |     0.51 | False |
| narwhals           | coverage                 |     0.8 |         1.7 |  2.1 |    0.21 |          2 |     0.26 | False |
| narwhals           | timing                   |     3.6 |         5.4 |  1.5 |    0.41 |         16 |     0.51 | False |
| narwhals           | traced                   |    53.7 |       208.0 |  3.9 |    4.65 |          6 |     6.07 | False |
| narwhals           | tests-released           |    32.0 |       169.9 |  5.3 |    4.55 |          8 |     5.62 | False |
| narwhals           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          5 |      5.7 | False |
| narwhals           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     5.55 | False |
| narwhals           | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          7 |      5.7 | False |
| narwhals           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     5.71 | False |
| narwhals           | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     5.84 | False |
| narwhals           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          5 |     5.85 | False |
| narwhals           | tests-infer-trace        |     0.4 |         0.2 |  0.5 |    0.03 |          4 |      5.8 | False |
| narwhals           | infer-union              |    15.8 |        74.4 |  4.7 |    7.11 |          5 |     8.95 | False |
| narwhals           | tests-infer-union        |    32.3 |       168.6 |  5.2 |    4.43 |          5 |     6.05 | False |
| narwhals           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          4 |     5.71 | False |
| narwhals           | types-released           |    24.9 |        48.0 |  1.9 |    1.59 |          2 |     1.94 | False |
| narwhals           | types-fix-certain        |    30.5 |        51.2 |  1.7 |    1.56 |          2 |     1.97 | False |
| narwhals           | types-fix-likely         |    31.7 |        52.2 |  1.6 |    1.58 |          2 |     1.72 | False |
| narwhals           | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          3 |     1.95 | False |
| narwhals           | types-infer-basedpyright |    21.2 |        45.1 |  2.1 |    1.59 |          3 |      2.0 | False |
| narwhals           | types-infer-ty           |    17.2 |        37.4 |  2.2 |    1.59 |          3 |     1.95 | False |
| narwhals           | types-infer-pyrefly      |    17.8 |        39.4 |  2.2 |     1.6 |          3 |     2.09 | False |
| narwhals           | types-infer-trace        |    43.5 |        56.0 |  1.3 |    1.55 |          3 |     2.06 | False |
| narwhals           | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| xarray             | check                    |     2.2 |         0.4 |  0.2 |    0.07 |          2 |     1.26 | False |
| xarray             | fix-certain              |    40.3 |        82.4 |  2.0 |    1.46 |          2 |     1.84 | False |
| xarray             | fix-likely               |    44.7 |       105.3 |  2.4 |    2.04 |          3 |     2.55 | False |
| xarray             | fix-unsafe               |    81.0 |        99.0 |  1.2 |    1.62 |          2 |     2.02 | False |
| xarray             | infer-basedpyright       |   115.4 |       304.8 |  2.6 |    8.04 |          3 |    12.56 | False |
| xarray             | infer-ty                 |   100.2 |       193.4 |  1.9 |    4.88 |          3 |     5.26 | False |
| xarray             | infer-pyrefly            |    61.5 |       143.8 |  2.3 |    4.78 |          3 |     6.42 | False |
| xarray             | census                   |    18.8 |        35.4 |  1.9 |     1.0 |          2 |     1.26 | False |
| xarray             | coverage                 |     4.4 |         8.2 |  1.9 |    0.46 |          3 |     0.57 | False |
| xarray             | timing                   |    24.4 |        34.4 |  1.4 |    1.01 |         16 |     1.26 | False |
| xarray             | traced                   |    56.1 |       192.9 |  3.4 |    1.99 |          4 |     2.49 | False |
| xarray             | tests-released           |    17.6 |       111.9 |  6.4 |     2.0 |          8 |     2.46 | False |
| xarray             | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.45 | False |
| xarray             | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.45 | False |
| xarray             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |     2.47 | False |
| xarray             | tests-infer-basedpyright |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.45 | False |
| xarray             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.45 | False |
| xarray             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     2.46 | False |
| xarray             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     2.46 | False |
| xarray             | infer-union              |   146.0 |       492.9 |  3.4 |   17.27 |          2 |    16.86 | False |
| xarray             | tests-infer-union        |    19.6 |       108.6 |  5.5 |    1.96 |          8 |     2.47 | False |
| xarray             | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| litestar           | check                    |     0.6 |         0.2 |  0.3 |    0.03 |          3 |     0.54 | False |
| litestar           | fix-certain              |     5.0 |        13.2 |  2.6 |    0.63 |          3 |      0.8 | False |
| litestar           | fix-likely               |     7.0 |        17.0 |  2.4 |    0.91 |          2 |     1.14 | False |
| litestar           | fix-unsafe               |    21.4 |        20.2 |  0.9 |    0.88 |          2 |     1.11 | False |
| litestar           | infer-basedpyright       |    16.1 |        64.2 |  4.0 |    3.16 |          5 |     4.64 | False |
| litestar           | infer-ty                 |     9.6 |        25.4 |  2.6 |     2.0 |          2 |     2.51 | False |
| litestar           | infer-pyrefly            |     6.8 |        24.9 |  3.7 |    2.59 |          4 |      3.4 | False |
| litestar           | census                   |     6.6 |         4.7 |  0.7 |    0.43 |          3 |     0.54 | False |
| litestar           | coverage                 |     1.0 |         2.2 |  2.2 |     0.2 |          2 |     0.25 | False |
| litestar           | timing                   |     3.4 |         5.0 |  1.5 |    0.43 |         16 |     0.55 | False |
| litestar           | traced                   |    38.9 |       185.4 |  4.8 |    4.27 |          4 |     5.31 | False |
| litestar           | tests-released           |    22.8 |       125.6 |  5.5 |    3.86 |          7 |     4.84 | False |
| litestar           | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.84 | False |
| litestar           | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.84 | False |
| litestar           | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     4.74 | False |
| litestar           | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          6 |     4.97 | False |
| litestar           | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          4 |     4.69 | False |
| litestar           | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          7 |     4.64 | False |
| litestar           | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          6 |     4.71 | False |
| litestar           | infer-union              |    26.3 |       107.8 |  4.1 |    5.94 |          5 |     6.36 | False |
| litestar           | tests-infer-union        |    23.5 |       122.2 |  5.2 |    3.85 |          7 |     4.81 | False |
| litestar           | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          5 |     4.74 | False |
| litestar           | types-released           |    79.1 |        63.1 |  0.8 |    2.04 |          2 |     2.55 | False |
| litestar           | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     2.35 | False |
| litestar           | types-fix-likely         |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     2.36 | False |
| litestar           | types-fix-unsafe         |     0.6 |         0.2 |  0.3 |    0.03 |          2 |     2.36 | False |
| litestar           | types-infer-basedpyright |    41.9 |        65.8 |  1.6 |    1.89 |          2 |     2.34 | False |
| litestar           | types-infer-ty           |    38.9 |        64.8 |  1.7 |    1.91 |          2 |     2.51 | False |
| litestar           | types-infer-pyrefly      |    48.7 |        67.9 |  1.4 |    1.96 |          2 |     2.56 | False |
| litestar           | types-infer-trace        |    45.5 |        67.0 |  1.5 |     1.9 |          2 |     2.37 | False |
| litestar           | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| stripe             | check                    |     4.6 |        13.7 |  3.0 |    0.83 |          4 |     1.05 | False |
| stripe             | fix-certain              |     9.6 |        32.2 |  3.4 |    1.06 |          4 |      1.3 | False |
| stripe             | fix-likely               |    10.2 |        33.7 |  3.3 |    1.18 |          4 |     1.49 | False |
| stripe             | fix-unsafe               |    12.2 |        38.2 |  3.1 |    1.05 |          3 |      1.3 | False |
| stripe             | infer-basedpyright       |  1068.3 |      2823.1 |  2.6 |    4.78 |          3 |     5.86 | False |
| stripe             | infer-ty                 |    20.1 |        55.1 |  2.7 |    2.56 |          4 |     3.09 | False |
| stripe             | infer-pyrefly            |    16.0 |        57.8 |  3.6 |    3.83 |          4 |     4.16 | False |
| stripe             | census                   |     2.2 |         1.9 |  0.9 |    0.06 |          4 |     1.05 | False |
| stripe             | coverage                 |     4.8 |         8.2 |  1.7 |    0.37 |          4 |     0.46 | False |
| stripe             | timing                   |    10.6 |        16.3 |  1.5 |    0.84 |         16 |     1.05 | False |
| celery             | check                    |     3.0 |         0.2 |  0.1 |    0.04 |          2 |     0.87 | False |
| celery             | fix-certain              |     7.8 |        16.4 |  2.1 |    0.86 |          3 |     1.07 | False |
| celery             | fix-likely               |     9.8 |        21.1 |  2.2 |    0.99 |          2 |     1.22 | False |
| celery             | fix-unsafe               |    18.5 |        21.0 |  1.1 |    1.27 |          2 |     1.07 | False |
| celery             | infer-basedpyright       |    21.9 |        58.0 |  2.6 |    3.34 |          4 |     5.06 | False |
| celery             | infer-ty                 |    11.4 |        28.7 |  2.5 |    1.95 |          3 |     1.95 | False |
| celery             | infer-pyrefly            |    10.2 |        38.4 |  3.8 |    2.67 |          4 |     2.59 | False |
| celery             | census                   |     4.6 |         7.0 |  1.5 |     0.7 |          2 |     0.87 | False |
| celery             | coverage                 |     1.2 |         1.9 |  1.6 |    0.21 |          2 |     0.26 | False |
| celery             | timing                   |     4.4 |         6.2 |  1.4 |     0.7 |         16 |     0.89 | False |
| celery             | traced                   |   181.6 |        86.6 |  0.5 |    3.06 |          1 |     3.85 | False |
| celery             | tests-released           |    58.5 |        60.1 |  1.0 |     2.9 |          2 |     3.14 | False |
| celery             | tests-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      3.6 | False |
| celery             | tests-fix-likely         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      3.6 | False |
| celery             | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     3.72 | False |
| celery             | tests-infer-basedpyright |     0.4 |         0.2 |  0.5 |    0.03 |          2 |     3.77 | False |
| celery             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          2 |     3.61 | False |
| celery             | tests-infer-pyrefly      |     0.4 |         0.2 |  0.5 |    0.03 |          2 |      3.6 | False |
| celery             | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          2 |      3.6 | False |
| celery             | infer-union              |    23.9 |        90.5 |  3.8 |    6.64 |          4 |     7.22 | False |
| celery             | tests-infer-union        |    57.8 |        57.3 |  1.0 |    2.92 |          2 |     4.14 | False |
| celery             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          2 |     3.61 | False |
| optuna             | check                    |     7.2 |         8.9 |  1.2 |    0.71 |          3 |      0.9 | False |
| optuna             | fix-certain              |    10.4 |        22.3 |  2.1 |    1.05 |          3 |     1.31 | False |
| optuna             | fix-likely               |    29.2 |        43.2 |  1.5 |    2.56 |          2 |     1.85 | False |
| optuna             | fix-unsafe               |    18.9 |        24.1 |  1.3 |    1.04 |          3 |     1.31 | False |
| optuna             | infer-basedpyright       |    30.3 |       105.0 |  3.5 |    5.05 |          3 |     6.26 | False |
| optuna             | infer-ty                 |    23.3 |        39.0 |  1.7 |    2.84 |          3 |     3.55 | False |
| optuna             | infer-pyrefly            |    17.6 |        48.3 |  2.7 |     3.7 |          4 |     4.54 | False |
| optuna             | census                   |     1.6 |         1.0 |  0.6 |    0.05 |          3 |      0.9 | False |
| optuna             | coverage                 |     2.2 |         2.3 |  1.0 |    0.19 |          2 |     0.25 | False |
| optuna             | timing                   |     5.4 |         8.1 |  1.5 |    0.72 |         16 |      0.9 | False |
| optuna             | traced                   |   138.7 |      1162.2 |  8.4 |    4.66 |          8 |     6.07 | False |
| optuna             | tests-released           |   225.4 |      2321.4 | 10.3 |    4.41 |          8 |     5.09 | False |
| optuna             | tests-fix-certain        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.27 | False |
| optuna             | tests-fix-likely         |     0.6 |         0.1 |  0.2 |    0.03 |          8 |     4.91 | False |
| optuna             | tests-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.24 | False |
| optuna             | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     4.96 | False |
| optuna             | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.05 | False |
| optuna             | tests-infer-pyrefly      |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.19 | False |
| optuna             | tests-infer-trace        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.49 | False |
| optuna             | infer-union              |    29.7 |       107.0 |  3.6 |    7.14 |          5 |     9.61 | False |
| optuna             | tests-infer-union        |   146.4 |      1749.5 | 12.0 |    4.01 |          8 |     5.04 | False |
| optuna             | tests                    |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     4.86 | False |
| optuna             | types-released           |     1.8 |         0.8 |  0.4 |    0.15 |          1 |     0.57 | False |
| optuna             | types-fix-certain        |     0.4 |         0.2 |  0.5 |    0.03 |          1 |     0.46 | False |
| optuna             | types-fix-likely         |     5.8 |         5.2 |  0.9 |    0.36 |          1 |     0.45 | False |
| optuna             | types-fix-unsafe         |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.46 | False |
| optuna             | types-infer-basedpyright |     6.6 |         5.3 |  0.8 |    0.36 |          1 |     0.45 | False |
| optuna             | types-infer-ty           |    15.3 |         5.7 |  0.4 |    0.47 |          1 |     0.57 | False |
| optuna             | types-infer-pyrefly      |     7.8 |         5.8 |  0.7 |    0.36 |          1 |     0.45 | False |
| optuna             | types-infer-trace        |     4.4 |         3.7 |  0.8 |    0.41 |          1 |     0.57 | False |
| optuna             | types                    |     0.4 |         0.1 |  0.2 |    0.03 |          1 |     0.04 | False |
| dask               | check                    |    18.4 |         0.4 |  0.0 |    0.07 |          2 |     1.74 | False |
| dask               | fix-certain              |    40.5 |        90.7 |  2.2 |    1.88 |          3 |     2.35 | False |
| dask               | fix-likely               |    55.5 |       132.1 |  2.4 |    2.58 |          2 |     3.22 | False |
| dask               | fix-unsafe               |    61.1 |       121.6 |  2.0 |     2.8 |          2 |      3.5 | False |
| dask               | infer-basedpyright       |   158.7 |       542.2 |  3.4 |    13.4 |          4 |    16.76 | False |
| dask               | infer-ty                 |    79.0 |       200.2 |  2.5 |    5.23 |          3 |     5.82 | False |
| dask               | infer-pyrefly            |    67.0 |       180.0 |  2.7 |    6.89 |          3 |     7.92 | False |
| dask               | census                   |    23.5 |        48.2 |  2.1 |    1.39 |          2 |     1.74 | False |
| dask               | coverage                 |     3.2 |         7.5 |  2.3 |    0.47 |          3 |     0.59 | False |
| dask               | timing                   |    31.0 |        44.0 |  1.4 |    1.39 |         16 |     1.74 | False |
| dask               | traced                   |   190.4 |      1221.9 |  6.4 |    4.93 |          8 |     6.14 | False |
| dask               | tests-released           |   167.2 |      1209.2 |  7.2 |    4.37 |          8 |     5.66 | False |
| dask               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.66 | False |
| dask               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.74 | False |
| dask               | tests-fix-unsafe         |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.55 | False |
| dask               | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.62 | False |
| dask               | tests-infer-ty           |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.47 | False |
| dask               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          8 |     5.55 | False |
| dask               | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     5.24 | False |
| dask               | infer-union              |   143.2 |       489.1 |  3.4 |   17.84 |          4 |    20.62 | False |
| dask               | tests-infer-union        |   162.0 |      1239.6 |  7.7 |    4.31 |          6 |     5.79 | False |
| dask               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | check                    |     2.6 |         0.2 |  0.1 |    0.05 |          3 |     0.71 | False |
| mypy               | fix-certain              |    15.0 |        44.4 |  3.0 |    1.03 |          4 |     1.29 | False |
| mypy               | fix-likely               |    13.6 |        44.3 |  3.3 |    1.09 |          4 |     1.37 | False |
| mypy               | fix-unsafe               |    14.8 |        40.4 |  2.7 |    1.05 |          3 |     1.29 | False |
| mypy               | infer-basedpyright       |    38.3 |       137.4 |  3.6 |    4.88 |          4 |     6.56 | False |
| mypy               | infer-ty                 |    21.7 |        67.0 |  3.1 |    2.77 |          4 |     2.94 | False |
| mypy               | infer-pyrefly            |    19.7 |        60.1 |  3.1 |    3.12 |          4 |      3.9 | False |
| mypy               | census                   |     4.8 |        10.5 |  2.2 |    0.57 |          3 |     0.71 | False |
| mypy               | coverage                 |     5.2 |         5.0 |  1.0 |    0.37 |          3 |     0.46 | False |
| mypy               | timing                   |     8.2 |        12.6 |  1.5 |    0.57 |         16 |     0.71 | False |
| mypy               | traced                   |   350.8 |      2365.0 |  6.7 |     6.5 |          8 |     8.31 | False |
| mypy               | tests-released           |   371.7 |      2257.0 |  6.1 |    6.15 |          8 |     7.19 | False |
| mypy               | tests-fix-certain        |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      7.5 | False |
| mypy               | tests-fix-likely         |     0.2 |         0.1 |  0.5 |    0.03 |          8 |      7.5 | False |
| mypy               | tests-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.03 |          8 |      7.5 | False |
| mypy               | tests-infer-basedpyright |     0.4 |         0.1 |  0.2 |    0.03 |          8 |     7.49 | False |
| mypy               | tests-infer-ty           |     0.4 |         0.1 |  0.2 |    0.03 |          7 |     7.26 | False |
| mypy               | tests-infer-pyrefly      |     0.2 |         0.1 |  0.5 |    0.03 |          7 |     7.72 | False |
| mypy               | tests-infer-trace        |     0.4 |         0.1 |  0.2 |    0.03 |          7 |      7.5 | False |
| mypy               | infer-union              |    34.7 |       135.2 |  3.9 |    7.66 |          4 |     9.49 | False |
| mypy               | tests-infer-union        |   351.8 |      2150.8 |  6.1 |    6.16 |          8 |     7.79 | False |
| mypy               | tests                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |
| mypy               | types-released           |    11.0 |        28.9 |  2.6 |    0.62 |          3 |     0.77 | False |
| mypy               | types-fix-certain        |    11.2 |        27.5 |  2.5 |    0.63 |          3 |     0.61 | False |
| mypy               | types-fix-likely         |     8.6 |        19.4 |  2.3 |    0.47 |          3 |     0.61 | False |
| mypy               | types-fix-unsafe         |     0.4 |         0.2 |  0.5 |    0.04 |          3 |     0.59 | False |
| mypy               | types-infer-basedpyright |    10.2 |        22.1 |  2.2 |     0.5 |          3 |      0.6 | False |
| mypy               | types-infer-ty           |    11.8 |        28.7 |  2.4 |    0.61 |          3 |     0.77 | False |
| mypy               | types-infer-pyrefly      |     9.0 |        21.7 |  2.4 |    0.49 |          3 |     0.61 | False |
| mypy               | types-infer-trace        |    12.0 |        28.2 |  2.4 |    0.63 |          3 |      0.8 | False |
| mypy               | types                    |     0.2 |         0.1 |  0.5 |    0.03 |          1 |     0.04 | False |

The likely fixes the unsafe fixes leave out or write otherwise, where there are any (the fixes
interact, so unsafe isn't likely with more):

| corpus   | likely | absent from unsafe | annotated otherwise |
| -------- | -----: | -----------------: | ------------------: |
| pandas   | 40,537 |                216 |                   0 |
| networkx |  6,155 |                 52 |                   0 |

The fixes whose bindings typed after aren't those typed before and those fixed, where they differ (a
fix that didn't make its binding typed):

| corpus | fix                | typed before | fixed | typed after | short |
| ------ | ------------------ | -----------: | ----: | ----------: | ----: |
| sphinx | certain            |          929 | 3,128 |       4,056 |     1 |
| sphinx | likely             |          929 | 3,576 |       4,504 |     1 |
| sphinx | unsafe             |          929 | 3,949 |       4,877 |     1 |
| sphinx | infer-basedpyright |          929 | 4,726 |       5,654 |     1 |
| sphinx | infer-ty           |          929 | 4,794 |       5,722 |     1 |
| sphinx | infer-pyrefly      |          929 | 5,085 |       6,013 |     1 |
| sphinx | infer-trace        |          929 | 3,949 |       4,877 |     1 |
| mypy   | unsafe             |        2,300 | 6,316 |       8,615 |     1 |
| mypy   | infer-basedpyright |        2,300 | 8,206 |      10,504 |     2 |
| mypy   | infer-ty           |        2,300 | 8,554 |      10,852 |     2 |
| mypy   | infer-pyrefly      |        2,300 | 8,799 |      11,097 |     2 |
| mypy   | infer-trace        |        2,300 | 6,316 |       8,615 |     1 |

Each suite's traced tests beside its released tests, a sample of its flakiness:

| corpus             | released                                                              | traced                                                                | same failures |
| ------------------ | --------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------- |
| django             | 5 expected failures, 1 failures, 17,585 ran, 1,129 skipped            | 5 expected failures, 5 failures, 17,585 ran, 1,129 skipped            | False         |
| sqlalchemy         | 29,521 passed, 975 skipped                                            | 29,523 passed, 973 skipped                                            | True          |
| pydantic           | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      | 65 failed, 6,900 passed, 350 skipped, 29 xfailed                      | True          |
| pandas             | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               | 165,411 passed, 24,659 skipped, 753 xfailed, 84 xpassed               | True          |
| structlog          | 24 failed, 860 passed, 37 skipped                                     | 24 failed, 860 passed, 37 skipped                                     | True          |
| attrs              | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          | True          |
| click              | 1,991 passed, 24 skipped, 1 xfailed                                   | 1,991 passed, 24 skipped, 1 xfailed                                   | True          |
| hypercorn          | 2 failed, 194 passed                                                  | 2 failed, 194 passed                                                  | True          |
| starlette          | 1,271 passed, 2 skipped, 2 xfailed                                    | 1,271 passed, 2 skipped, 2 xfailed                                    | True          |
| werkzeug           | 1 failed, 979 passed, 1 skipped                                       | 1 failed, 979 passed, 1 skipped                                       | True          |
| mkdocs             | 2 errors, 2 failures, 724 ran, 4 skipped                              | 2 errors, 2 failures, 724 ran, 4 skipped                              | True          |
| httpx              | 1 failed, 1,416 passed, 1 skipped                                     | 1 failed, 1,416 passed, 1 skipped                                     | True          |
| black              | 519 passed, 1 skipped                                                 | 519 passed, 1 skipped                                                 | True          |
| fastapi            | 3,551 passed, 17 skipped, 4 xfailed                                   | 3,551 passed, 17 skipped, 4 xfailed                                   | True          |
| cattrs             | 994 passed, 15 xfailed                                                | 994 passed, 15 xfailed                                                | True          |
| pytest             | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  | 1 error, 46 failed, 4,059 passed, 110 skipped, 14 xfailed, 1 xpassed  | True          |
| botocore           | 7 failed, 4,593 passed, 96 skipped                                    | 7 failed, 4,593 passed, 96 skipped                                    | True          |
| uvicorn            | 1,350 passed, 12 skipped                                              | 1,350 passed, 12 skipped                                              | True          |
| mcp                | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          | 3 failed, 6,092 passed, 8 skipped, 1 xfailed                          | False         |
| pdm                | 1,472 passed, 1 skipped                                               | 1,472 passed, 1 skipped                                               | True          |
| strawberry-graphql | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           | False         |
| pygments           | 1 failed, 5,330 passed, 15 skipped                                    | 1 failed, 5,330 passed, 15 skipped                                    | True          |
| streamlink         | 9 error, 15 failed, 7,233 passed, 36 skipped                          | 9 error, 15 failed, 7,233 passed, 36 skipped                          | True          |
| sphinx             | 9 failed, 2,393 passed, 22 skipped                                    | 10 failed, 2,392 passed, 22 skipped                                   | False         |
| tox                | 6 error, 17 failed, 8,525 passed, 31 skipped                          | 6 error, 17 failed, 8,525 passed, 31 skipped                          | True          |
| pint               | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       | True          |
| altair             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             | 28 failed, 1,866 passed, 12 skipped, 7 xfailed, 3 xpassed             | True          |
| seaborn            | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               | False         |
| aiohttp            | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        | 3 failed, 4,840 passed, 535 skipped, 2 xfailed                        | True          |
| websockets         | 2,589 ran, 8 skipped                                                  | 2,589 ran, 8 skipped                                                  | True          |
| anyio              | 3,824 passed, 19 skipped, 5 xfailed                                   | 3,824 passed, 19 skipped, 5 xfailed                                   | True          |
| zarr               | 8,422 passed, 1,205 skipped, 4 xfailed                                | 8,422 passed, 1,205 skipped, 4 xfailed                                | True          |
| joblib             | 8 failed, 1,484 passed, 45 skipped, 4 xpassed                         | 10 failed, 1,482 passed, 45 skipped, 4 xpassed                        | False         |
| networkx           | 10,083 passed, 62 skipped, 741 xfailed                                | 10,083 passed, 62 skipped, 741 xfailed                                | True          |
| nibabel            | 19 error, 109 failed, 5,168 passed, 304 skipped, 40 xfailed           | 20 error, 110 failed, 5,166 passed, 304 skipped, 40 xfailed           | False         |
| narwhals           | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | 972 failed, 11,116 passed, 235 skipped, 699 xfailed                   | True          |
| xarray             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed | 3 error, 3 failed, 6,333 passed, 9,626 skipped, 11 xfailed, 4 xpassed | False         |
| litestar           | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           | 6 failed, 5,645 passed, 256 skipped, 13 xfailed, 30 xpassed           | False         |
| celery             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         | True          |
| optuna             | 16 error, 263 failed, 4,203 passed, 43 skipped                        | 16 error, 263 failed, 4,203 passed, 43 skipped                        | False         |
| dask               | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | 5 failed, 16,196 passed, 1,089 skipped, 513 xfailed, 2 xpassed        | False         |
| mypy               | 14,464 passed, 366 skipped, 12 xfailed                                | 14,464 passed, 366 skipped, 12 xfailed                                | True          |

- standard library, 0.4.3-rc.1+dev, fix-likely: held 8.03 GB beside other steps
- standard library, 0.4.3-rc.1+dev, infer-basedpyright: held 12.51 GB beside other steps
- standard library, 0.4.3-rc.1+dev, infer-ty: held 15.02 GB beside other steps
- standard library, 0.4.3-rc.1+dev, infer-pyrefly: held 18.08 GB beside other steps
- django, 0.4.3-rc.1+dev, infer-union: held 10.16 GB beside other steps
- django, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store,
  so its seconds measure less of the checker
- django, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- django, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- sqlalchemy, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 2 of 5 rounds came from
  the store, so its seconds measure less of the checker
- sqlalchemy, 0.4.3-rc.1+dev, infer-union: held 11.44 GB beside other steps
- sqlalchemy, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- sqlalchemy, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pydantic, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- pydantic, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- pydantic, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- pandas, 0.4.3-rc.1+dev, infer-basedpyright: held 19.46 GB beside other steps
- pandas, 0.4.3-rc.1+dev, infer-ty: held 14.11 GB beside other steps
- pandas, 0.4.3-rc.1+dev, infer-pyrefly: held 18.73 GB beside other steps
- pandas, 0.4.3-rc.1+dev, traced: held 12.32 GB beside other steps
- pandas, 0.4.3-rc.1+dev, tests-released: held 11.5 GB beside other steps
- pandas, 0.4.3-rc.1+dev, infer-union: held 28.27 GB beside other steps
- pandas, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store,
  so its seconds measure less of the checker
- pandas, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- pandas, 0.4.3-rc.1+dev, tests-infer-union: held 11.53 GB beside other steps
- twisted, 0.4.3-rc.1+dev, infer-basedpyright: held 9.5 GB beside other steps
- structlog, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- structlog, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- structlog, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- attrs, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store, so
  its seconds measure less of the checker
- attrs, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- attrs, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- click, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- click, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- click, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- hypercorn, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- hypercorn, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- hypercorn, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- starlette, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- starlette, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- starlette, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- werkzeug, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- werkzeug, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mkdocs, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 2 of 4 rounds came from the
  store, so its seconds measure less of the checker
- mkdocs, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 2 of 4 rounds came from the store, so
  its seconds measure less of the checker
- mkdocs, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- httpx, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- httpx, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- httpx, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- black, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- black, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- fastapi, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- fastapi, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- fastapi, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store,
  so its seconds measure less of the checker
- cattrs, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- cattrs, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 2 of 4 rounds came from the store,
  so its seconds measure less of the checker
- pytest, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- pytest, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 4 rounds came from the store, so its
  seconds measure less of the checker
- botocore, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store,
  so its seconds measure less of the checker
- botocore, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- botocore, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- uvicorn, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- uvicorn, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mcp, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- mcp, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mcp, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- textual, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 5 rounds came from the
  store, so its seconds measure less of the checker
- textual, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- pdm, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 3 of 5 rounds came from the store, so
  its seconds measure less of the checker
- pdm, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 3 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pdm, 0.4.3-rc.1+dev, infer-union: ty's hints for 3 of 5 rounds came from the store, so its seconds
  measure less of the checker
- strawberry-graphql, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 2 rounds came from
  the store, so its seconds measure less of the checker
- strawberry-graphql, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- strawberry-graphql, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- pygments, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 4 rounds came from the
  store, so its seconds measure less of the checker
- pygments, 0.4.3-rc.1+dev, infer-ty: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- pygments, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so
  its seconds measure less of the checker
- streamlink, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from
  the store, so its seconds measure less of the checker
- streamlink, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- streamlink, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- sphinx, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- sphinx, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- sphinx, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- tox, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- tox, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- pint, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 2 of 4 rounds came from the
  store, so its seconds measure less of the checker
- pint, 0.4.3-rc.1+dev, infer-ty: ty's hints for 2 of 4 rounds came from the store, so its seconds
  measure less of the checker
- pint, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- altair, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 3 of 4 rounds came from the store,
  so its seconds measure less of the checker
- altair, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- altair, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 4 rounds came from the store, so its
  seconds measure less of the checker
- seaborn, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 2 of 5 rounds came from the store,
  so its seconds measure less of the checker
- seaborn, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- seaborn, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- aiohttp, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- aiohttp, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- websockets, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from
  the store, so its seconds measure less of the checker
- websockets, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store, so its
  seconds measure less of the checker
- websockets, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store,
  so its seconds measure less of the checker
- anyio, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 2 rounds came from the
  store, so its seconds measure less of the checker
- anyio, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- anyio, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 2 rounds came from the store, so
  its seconds measure less of the checker
- zarr, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- zarr, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 3 rounds came from the store, so its seconds
  measure less of the checker
- zarr, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- joblib, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 4 rounds came from the
  store, so its seconds measure less of the checker
- joblib, 0.4.3-rc.1+dev, infer-ty: ty's hints for 1 of 4 rounds came from the store, so its seconds
  measure less of the checker
- joblib, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 4 rounds came from the store, so
  its seconds measure less of the checker
- networkx, 0.4.3-rc.1+dev, infer-basedpyright: held 9.3 GB beside other steps
- networkx, 0.4.3-rc.1+dev, infer-union: held 11.57 GB beside other steps
- networkx, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 6 rounds came from the store,
  so its seconds measure less of the checker
- networkx, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 6 rounds came from the store, so
  its seconds measure less of the checker
- networkx, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 6 rounds came from the store, so its
  seconds measure less of the checker
- nibabel, 0.4.3-rc.1+dev, infer-union: held 8.56 GB beside other steps
- nibabel, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store,
  so its seconds measure less of the checker
- nibabel, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- nibabel, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- narwhals, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- narwhals, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- narwhals, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- xarray, 0.4.3-rc.1+dev, infer-basedpyright: held 8.04 GB beside other steps
- xarray, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 5 rounds came from the
  store, so its seconds measure less of the checker
- xarray, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 2 of 5 rounds came from the store, so
  its seconds measure less of the checker
- xarray, 0.4.3-rc.1+dev, infer-union: held 17.27 GB beside other steps
- xarray, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- litestar, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 1 of 3 rounds came from the
  store, so its seconds measure less of the checker
- litestar, 0.4.3-rc.1+dev, infer-pyrefly: pyrefly's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- litestar, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- celery, 0.4.3-rc.1+dev, infer-basedpyright: basedpyright's hints for 2 of 5 rounds came from the
  store, so its seconds measure less of the checker
- celery, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- celery, 0.4.3-rc.1+dev, infer-union: ty's hints for 2 of 5 rounds came from the store, so its
  seconds measure less of the checker
- optuna, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store,
  so its seconds measure less of the checker
- optuna, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- optuna, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- dask, 0.4.3-rc.1+dev, infer-basedpyright: held 13.4 GB beside other steps
- dask, 0.4.3-rc.1+dev, infer-union: held 17.84 GB beside other steps
- dask, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 5 rounds came from the store, so
  its seconds measure less of the checker
- dask, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- dask, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 5 rounds came from the store, so its
  seconds measure less of the checker
- mypy, 0.4.3-rc.1+dev, infer-union: basedpyright's hints for 1 of 3 rounds came from the store, so
  its seconds measure less of the checker
- mypy, 0.4.3-rc.1+dev, infer-union: pyrefly's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker
- mypy, 0.4.3-rc.1+dev, infer-union: ty's hints for 1 of 3 rounds came from the store, so its
  seconds measure less of the checker

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

## constricter 0.4.0

0.4.1 and 0.4.2 changed the build alone, not `constricter/`: their checks and fixes are 0.4.0's.

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
