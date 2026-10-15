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

The run `super` (`python -m tests.corpus`) on seven: constricter 0.3.6 (`773ed2b6b4da`), Python
3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own, started once the CPUs
it's expected to keep busy and the memory it's expected to hold are free. The run took 48 minutes.
Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus           | Version | constricter | Files |        `LVA001` |      `LVA002` |       `LVA004` |   `LVA005` |   `LVA006` |  `LVA009` | `LVA011` |   Total |
| ---------------- | ------- | ----------- | ----: | --------------: | ------------: | -------------: | ---------: | ---------: | --------: | -------: | ------: |
| standard library | 3.14.7  | super+dev   | 1,867 |          88,565 |        12,334 |         12,772 |         57 |         14 |         8 |        0 | 113,750 |
| django           | 5.2.17  | super+dev   |   883 |           9,921 |         2,167 |          5,081 |          0 |          0 |         1 |        0 |  17,170 |
| sqlalchemy       | 2.0.54  | super+dev   |   257 |           8,504 |         1,567 |          2,339 |        551 |        124 |         1 |        1 |  13,087 |
| pydantic         | 2.13.5  | super+dev   |   105 |           2,023 |           438 |            631 |        190 |         13 |         0 |        0 |   3,295 |
| pandas           | 3.0.6   | super+dev   | 1,420 |          73,367 |         2,778 |          1,648 |        134 |          2 |         1 |        1 |  77,931 |
| twisted          | 12.3.0  | super+dev   |   819 |          13,310 |         1,349 |          3,215 |          0 |          0 |         0 |        0 |  17,874 |
| pip              | 20.3.4  | super+dev   |   366 |           5,902 |         1,150 |          1,872 |          0 |          0 |         0 |        0 |   8,924 |
| **Total**        |         | super+dev   | 5,717 | 201,592 (80.0%) | 21,783 (8.6%) | 27,558 (10.9%) | 932 (0.4%) | 153 (0.1%) | 11 (0.0%) | 2 (0.0%) | 252,031 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus           | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |         Likely |        Guessed | Broken | Left | Left, likely |
| ---------------- | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | -------------: | -------------: | -----: | ---: | -----------: |
| standard library | super+dev   | 0 / 113,679 | 101,337 / 12,413 |    113,679 / 71 | 113,750 / 0 | 37,330 (32.8%) |   6,430 (5.7%) | 12,337 (10.8%) |      0 |    0 |            0 |
| django           | super+dev   |  0 / 17,170 |   15,002 / 2,168 |      17,170 / 0 |  17,170 / 0 |  2,618 (15.2%) |     629 (3.7%) |  2,659 (15.5%) |      0 |    0 |            0 |
| sqlalchemy       | super+dev   |  0 / 12,411 |   10,843 / 2,244 |    12,411 / 676 |  13,087 / 0 |  1,667 (12.7%) |     320 (2.4%) |     962 (7.4%) |      0 |    0 |            0 |
| pydantic         | super+dev   |   0 / 3,092 |      2,654 / 641 |     3,092 / 203 |   3,295 / 0 |  1,081 (32.8%) |     148 (4.5%) |    409 (12.4%) |      0 |    0 |            0 |
| pandas           | super+dev   |  0 / 77,794 |   75,015 / 2,916 |    77,794 / 137 |  77,931 / 0 | 16,945 (21.7%) | 23,794 (30.5%) | 24,616 (31.6%) |      0 |    0 |            0 |
| twisted          | super+dev   |  0 / 17,874 |   16,525 / 1,349 |      17,874 / 0 |  17,874 / 0 |  2,437 (13.6%) |  3,657 (20.5%) |  4,657 (26.1%) |      0 |    0 |            0 |
| pip              | super+dev   |   0 / 8,924 |    7,774 / 1,150 |       8,924 / 0 |   8,924 / 0 |  2,253 (25.2%) |     425 (4.8%) |  1,133 (12.7%) |      0 |    0 |            0 |
| **Total**        | super+dev   | 0 / 250,944 | 229,150 / 22,881 | 250,944 / 1,087 | 252,031 / 0 | 64,331 (25.5%) | 35,403 (14.0%) | 46,773 (18.6%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus           | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ---------------- | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| standard library | super+dev   |              1.2% |         33.6% |            39.2% |                  44.3% | +32.5 pts, 32.8% of untyped | +43.2 pts, 43.7% of untyped |
| django           | super+dev   |              0.0% |         15.3% |            18.9% |                  30.7% | +15.2 pts, 15.2% of untyped | +30.7 pts, 30.7% of untyped |
| sqlalchemy       | super+dev   |             14.8% |         26.2% |            28.4% |                  32.8% | +11.4 pts, 13.4% of untyped | +18.0 pts, 21.2% of untyped |
| pydantic         | super+dev   |             21.8% |         49.2% |            52.9% |                  59.5% | +27.3 pts, 35.0% of untyped | +37.7 pts, 48.2% of untyped |
| pandas           | super+dev   |              1.6% |         23.0% |            53.1% |                  54.2% | +21.4 pts, 21.8% of untyped | +52.6 pts, 53.4% of untyped |
| twisted          | super+dev   |              0.0% |         13.6% |            34.1% |                  39.7% | +13.6 pts, 13.6% of untyped | +39.7 pts, 39.7% of untyped |
| pip              | super+dev   |              1.5% |         26.4% |            31.1% |                  38.9% | +24.9 pts, 25.2% of untyped | +37.4 pts, 37.9% of untyped |
| **Total**        | super+dev   |              2.2% |         27.3% |            41.1% |                  45.5% | +25.1 pts, 25.6% of untyped | +43.3 pts, 44.3% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus           | fix                |  fixed | certain | likely |  guess | broken | left |  typed | bindings | seconds |
| ---------------- | ------------------ | -----: | ------: | -----: | -----: | -----: | ---: | -----: | -------: | ------: |
| standard library | certain            | 37,330 |  37,330 |        |        |      0 |    0 | 38,659 |  115,001 |    55.9 |
| standard library | likely             | 43,760 |  37,544 |  6,216 |        |      0 |    0 | 45,089 |  115,001 |    72.8 |
| standard library | unsafe             | 49,667 |  37,338 |  6,208 |  6,121 |      0 |    0 | 50,996 |  115,001 |    53.9 |
| standard library | infer-basedpyright | 58,032 |  37,346 |  6,712 | 13,974 |      0 |    9 | 59,361 |  115,001 |   418.3 |
| standard library | infer-ty           | 55,800 |  37,347 |  6,681 | 11,772 |      0 |   41 | 57,129 |  115,001 |   126.3 |
| standard library | infer-pyrefly      | 57,662 |  37,345 |  6,797 | 13,520 |      0 |   42 | 58,991 |  115,001 |   108.5 |
| django           | certain            |  2,618 |   2,618 |        |        |      0 |    0 |  2,620 |   17,171 |    11.7 |
| django           | likely             |  3,247 |   2,621 |    626 |        |      0 |    0 |  3,249 |   17,171 |    19.1 |
| django           | unsafe             |  5,277 |   2,618 |    625 |  2,034 |      0 |    0 |  5,279 |   17,171 |    10.2 |
| django           | infer-basedpyright |  5,735 |   2,617 |    641 |  2,477 |      0 |    2 |  5,737 |   17,171 |    38.4 |
| django           | infer-ty           |  5,529 |   2,619 |    635 |  2,275 |      0 |    5 |  5,531 |   17,171 |    31.0 |
| django           | infer-pyrefly      |  6,005 |   2,609 |    648 |  2,748 |      0 |   36 |  6,007 |   17,171 |    20.6 |
| django           | infer-trace        |  5,817 |   2,622 |    659 |  2,536 |      0 |    0 |  5,819 |   17,171 |     8.2 |
| sqlalchemy       | certain            |  1,667 |   1,667 |        |        |      0 |    0 |  3,816 |   14,568 |     9.0 |
| sqlalchemy       | likely             |  1,987 |   1,674 |    313 |        |      0 |    0 |  4,136 |   14,568 |    14.6 |
| sqlalchemy       | unsafe             |  2,629 |   1,667 |    312 |    650 |      0 |    0 |  4,778 |   14,568 |    12.4 |
| sqlalchemy       | infer-basedpyright |  3,509 |   1,668 |    356 |  1,485 |      0 |    0 |  5,658 |   14,568 |    43.9 |
| sqlalchemy       | infer-ty           |  3,446 |   1,668 |    342 |  1,436 |      0 |    4 |  5,595 |   14,568 |    23.8 |
| sqlalchemy       | infer-pyrefly      |  3,741 |   1,667 |    354 |  1,720 |      0 |    2 |  5,890 |   14,568 |    27.5 |
| sqlalchemy       | infer-trace        |  2,809 |   1,667 |    312 |    830 |      0 |    0 |  4,958 |   14,568 |    12.4 |
| pydantic         | certain            |  1,081 |   1,081 |        |        |      0 |    0 |  1,945 |    3,956 |     1.7 |
| pydantic         | likely             |  1,229 |   1,089 |    140 |        |      0 |    0 |  2,093 |    3,956 |     2.8 |
| pydantic         | unsafe             |  1,490 |   1,081 |    139 |    270 |      0 |    0 |  2,354 |    3,956 |     2.1 |
| pydantic         | infer-basedpyright |  1,786 |   1,082 |    143 |    561 |      0 |    0 |  2,650 |    3,956 |    24.3 |
| pydantic         | infer-ty           |  1,667 |   1,082 |    140 |    445 |      0 |    0 |  2,531 |    3,956 |     6.7 |
| pydantic         | infer-pyrefly      |  1,736 |   1,082 |    142 |    512 |      0 |    0 |  2,600 |    3,956 |     6.8 |
| pydantic         | infer-trace        |  1,491 |   1,081 |    139 |    271 |      0 |    0 |  2,355 |    3,956 |     2.6 |
| pandas           | certain            | 16,945 |  16,945 |        |        |      0 |    0 | 18,214 |   79,062 |    46.6 |
| pandas           | likely             | 40,739 |  17,128 | 23,611 |        |      0 |    0 | 42,008 |   79,062 |    73.2 |
| pandas           | unsafe             | 41,561 |  16,941 | 23,393 |  1,227 |      0 |    0 | 42,830 |   79,062 |    47.6 |
| pandas           | infer-basedpyright | 47,277 |  16,933 | 23,428 |  6,916 |      0 |   14 | 48,546 |   79,062 |   374.2 |
| pandas           | infer-ty           | 46,407 |  16,941 | 23,465 |  6,001 |      0 |    0 | 47,676 |   79,062 |   127.6 |
| pandas           | infer-pyrefly      | 47,011 |  16,944 | 23,471 |  6,596 |      0 |    2 | 48,280 |   79,062 |    91.6 |
| pandas           | infer-trace        | 42,964 |  16,941 | 23,354 |  2,669 |      0 |    9 | 44,233 |   79,062 |    40.7 |
| twisted          | certain            |  2,437 |   2,437 |        |        |      0 |    0 |  2,437 |   17,874 |     7.4 |
| twisted          | likely             |  6,094 |   2,561 |  3,533 |        |      0 |    0 |  6,094 |   17,874 |    11.2 |
| twisted          | unsafe             |  7,094 |   2,436 |  3,533 |  1,125 |      0 |    0 |  7,094 |   17,874 |     5.9 |
| twisted          | infer-basedpyright |  8,530 |   2,441 |  3,563 |  2,526 |      0 |   10 |  8,530 |   17,874 |    43.0 |
| twisted          | infer-ty           |  7,530 |   2,436 |  3,576 |  1,518 |      0 |    0 |  7,530 |   17,874 |    19.5 |
| twisted          | infer-pyrefly      |  7,497 |   2,436 |  3,566 |  1,495 |      0 |    0 |  7,497 |   17,874 |    12.7 |
| pip              | certain            |  2,253 |   2,253 |        |        |      0 |    0 |  2,390 |    9,064 |     6.8 |
| pip              | likely             |  2,678 |   2,266 |    412 |        |      0 |    0 |  2,815 |    9,064 |    10.9 |
| pip              | unsafe             |  3,386 |   2,253 |    412 |    721 |      0 |    0 |  3,523 |    9,064 |     6.7 |
| pip              | infer-basedpyright |  4,180 |   2,258 |    466 |  1,456 |      0 |    7 |  4,317 |    9,064 |    41.0 |
| pip              | infer-ty           |  3,714 |   2,255 |    436 |  1,023 |      0 |    8 |  3,851 |    9,064 |    14.9 |
| pip              | infer-pyrefly      |  3,882 |   2,255 |    446 |  1,181 |      0 |    0 |  4,019 |    9,064 |     8.6 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms             |  fixed | certain | likely |  guess |
| ------------------ | ---------------------- | -----: | ------: | -----: | -----: |
| certain            | literal                | 16,713 |  16,713 |        |        |
| certain            | stdlib                 | 13,235 |  13,235 |        |        |
| certain            | call                   |  5,104 |   5,104 |        |        |
| certain            | container+literal      |  3,976 |   3,976 |        |        |
| certain            | builtin                |  2,510 |   2,510 |        |        |
| certain            | loop                   |  2,433 |   2,433 |        |        |
| certain            | container+literal+loop |  1,581 |   1,581 |        |        |
| certain            | copy+loop              |  1,541 |   1,541 |        |        |
| certain            | method                 |  1,205 |   1,205 |        |        |
| certain            | open                   |  1,101 |   1,101 |        |        |
| certain            | literal+method         |    944 |     944 |        |        |
| certain            | returned               |    860 |     860 |        |        |
| likely             | constructor            | 27,092 |     234 | 26,858 |        |
| likely             | literal                | 16,714 |  16,714 |        |        |
| likely             | stdlib                 | 13,291 |  13,291 |        |        |
| likely             | call                   |  5,559 |   5,116 |    443 |        |
| likely             | container+literal      |  3,976 |   3,976 |        |        |
| likely             | builtin                |  2,510 |   2,510 |        |        |
| likely             | loop                   |  2,433 |   2,433 |        |        |
| likely             | method                 |  2,205 |   1,227 |    978 |        |
| likely             | copy+loop              |  1,802 |   1,549 |    253 |        |
| likely             | container+literal+loop |  1,581 |   1,581 |        |        |
| likely             | open                   |  1,101 |   1,101 |        |        |
| likely             | returned               |  1,078 |   1,078 |        |        |
| unsafe             | constructor            | 27,091 |     234 | 26,857 |        |
| unsafe             | literal                | 16,716 |  16,713 |        |      3 |
| unsafe             | stdlib                 | 13,545 |  13,237 |        |    308 |
| unsafe             | call                   |  5,522 |   5,104 |    418 |        |
| unsafe             | container+literal      |  3,976 |   3,976 |        |        |
| unsafe             | literal+member         |  3,680 |         |        |  3,680 |
| unsafe             | returned               |  3,276 |     862 |        |  2,414 |
| unsafe             | builtin                |  2,510 |   2,510 |        |        |
| unsafe             | loop                   |  2,433 |   2,433 |        |        |
| unsafe             | method                 |  2,144 |   1,205 |    939 |        |
| unsafe             | copy+loop              |  1,787 |   1,541 |    246 |        |
| unsafe             | container+literal+loop |  1,581 |   1,581 |        |        |
| infer-basedpyright | constructor            | 27,045 |     233 | 26,812 |        |
| infer-basedpyright | literal                | 16,717 |  16,714 |        |      3 |
| infer-basedpyright | checker                | 15,300 |         |        | 15,300 |
| infer-basedpyright | stdlib                 | 13,601 |  13,135 |        |    466 |
| infer-basedpyright | call                   |  5,619 |   5,102 |    517 |        |
| infer-basedpyright | container+literal      |  3,976 |   3,976 |        |        |
| infer-basedpyright | literal+member         |  3,679 |         |        |  3,679 |
| infer-basedpyright | returned               |  3,559 |     848 |        |  2,711 |
| infer-basedpyright | builtin                |  2,510 |   2,510 |        |        |
| infer-basedpyright | loop                   |  2,433 |   2,433 |        |        |
| infer-basedpyright | method                 |  2,272 |   1,205 |  1,067 |        |
| infer-basedpyright | copy+loop              |  2,135 |   1,544 |    591 |        |
| infer-ty           | constructor            | 27,049 |     234 | 26,815 |        |
| infer-ty           | literal                | 16,716 |  16,713 |        |      3 |
| infer-ty           | stdlib                 | 13,613 |  13,153 |        |    460 |
| infer-ty           | checker                | 10,802 |         |        | 10,802 |
| infer-ty           | call                   |  5,594 |   5,102 |    492 |        |
| infer-ty           | container+literal      |  3,976 |   3,976 |        |        |
| infer-ty           | literal+member         |  3,680 |         |        |  3,680 |
| infer-ty           | returned               |  3,504 |     863 |        |  2,641 |
| infer-ty           | builtin                |  2,510 |   2,510 |        |        |
| infer-ty           | loop                   |  2,433 |   2,433 |        |        |
| infer-ty           | method                 |  2,246 |   1,205 |  1,041 |        |
| infer-ty           | copy+loop              |  2,034 |   1,543 |    491 |        |
| infer-pyrefly      | constructor            | 27,040 |     233 | 26,807 |        |
| infer-pyrefly      | literal                | 16,716 |  16,713 |        |      3 |
| infer-pyrefly      | checker                | 13,939 |         |        | 13,939 |
| infer-pyrefly      | stdlib                 | 13,672 |  13,200 |        |    472 |
| infer-pyrefly      | call                   |  5,592 |   5,102 |    490 |        |
| infer-pyrefly      | container+literal      |  3,976 |   3,976 |        |        |
| infer-pyrefly      | literal+member         |  3,679 |         |        |  3,679 |
| infer-pyrefly      | returned               |  3,456 |     863 |        |  2,593 |
| infer-pyrefly      | builtin                |  2,510 |   2,510 |        |        |
| infer-pyrefly      | loop                   |  2,433 |   2,433 |        |        |
| infer-pyrefly      | method                 |  2,273 |   1,205 |  1,068 |        |
| infer-pyrefly      | copy+loop              |  2,067 |   1,543 |    524 |        |
| infer-trace        | constructor            | 19,769 |       2 | 19,767 |        |
| infer-trace        | literal                |  6,870 |   6,870 |        |        |
| infer-trace        | call                   |  5,158 |   4,739 |    419 |        |
| infer-trace        | traced                 |  2,016 |         |        |  2,016 |
| infer-trace        | literal+member         |  1,940 |         |        |  1,940 |
| infer-trace        | method                 |  1,746 |     824 |    922 |        |
| infer-trace        | container+literal      |  1,591 |   1,591 |        |        |
| infer-trace        | stdlib                 |  1,160 |   1,122 |        |     38 |
| infer-trace        | builtin                |    827 |     827 |        |        |
| infer-trace        | returned               |    586 |     225 |        |    361 |
| infer-trace        | loop                   |    578 |     578 |        |        |
| infer-trace        | copy+loop              |    468 |     373 |     95 |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus           | untyped | guessed | unfixed | unparsed |
| ---------------- | ------: | ------: | ------: | -------: |
| standard library | 113,671 |  12,330 |  64,011 |        0 |
| django           |  17,169 |   2,659 |  11,892 |        0 |
| sqlalchemy       |  12,410 |     962 |   9,781 |        0 |
| pydantic         |   3,092 |     409 |   1,602 |        0 |
| pandas           |  77,793 |  24,615 |  36,233 |        0 |
| twisted          |  17,874 |   4,657 |  10,780 |        0 |
| pip              |   8,924 |   1,133 |   5,538 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus           | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ---------------- | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| standard library |    4 |       51.84 |     23.04 |    1 |                       899.0 |     936.4 | hyperfine |
| django           |    4 |        9.46 |      3.96 |    1 |                       158.9 |     168.4 | hyperfine |
| sqlalchemy       |    4 |        6.49 |      3.34 |    1 |                       108.3 |     115.4 | hyperfine |
| pydantic         |    4 |        1.48 |      0.68 |    1 |                        21.7 |      24.0 | hyperfine |
| pandas           |    4 |       56.32 |     20.01 |    1 |                       961.2 |     987.4 | hyperfine |
| twisted          |    4 |         6.7 |      2.72 |    1 |                       106.8 |     113.8 | hyperfine |
| pip              |    4 |        4.19 |      1.76 |    1 |                        67.9 |      72.0 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus     | tier    |   told |   held | differed | resting on the trace |                                                                   tests | seconds | untraced |
| ---------- | ------- | -----: | -----: | -------: | -------------------: | ----------------------------------------------------------------------: | ------: | -------: |
| django     |         |        |        |          |                  460 | Ran 17578 tests: FAILED (failures=5, skipped=1129, expected failures=5) |   373.9 |     69.1 |
| django     | certain |    927 |    925 |        2 |                      |                                                                         |         |          |
| django     | likely  |    296 |    295 |        1 |                      |                                                                         |         |          |
| django     | guess   |    291 |    269 |       22 |                      |                                                                         |         |          |
| sqlalchemy |         |        |        |          |                  177 |                                     1 failed, 26642 passed, 985 skipped |   106.8 |    105.1 |
| sqlalchemy | certain |  1,030 |  1,010 |       20 |                      |                                                                         |         |          |
| sqlalchemy | likely  |    167 |    163 |        4 |                      |                                                                         |         |          |
| sqlalchemy | guess   |    123 |    121 |        2 |                      |                                                                         |         |          |
| pydantic   |         |        |        |          |                    1 |                                    6439 passed, 329 skipped, 27 xfailed |    36.1 |     28.9 |
| pydantic   | certain |    482 |    477 |        5 |                      |                                                                         |         |          |
| pydantic   | likely  |     53 |     53 |        0 |                      |                                                                         |         |          |
| pydantic   | guess   |     32 |     32 |        0 |                      |                                                                         |         |          |
| pandas     |         |        |        |          |                1,426 |                   165411 passed, 24659 skipped, 753 xfailed, 84 xpassed |   204.7 |    103.1 |
| pandas     | certain | 12,876 | 12,801 |       75 |                      |                                                                         |         |          |
| pandas     | likely  | 20,096 | 20,032 |       64 |                      |                                                                         |         |          |
| pandas     | guess   |    827 |    780 |       47 |                      |                                                                         |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus     | run                | same as released | summary                                                    | new failures | gone | named |
| ---------- | ------------------ | ---------------- | ---------------------------------------------------------- | -----------: | ---: | ----: |
| django     | released           |                  | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |              |      |       |
| django     | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| django     | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| django     | fix-unsafe         | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-basedpyright | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-pyrefly      | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-trace        | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |            0 |    0 |     0 |
| django     | infer-ty           | True             | 5 expected failures, 1 failures, 17,578 ran, 1,129 skipped |            0 |    0 |     0 |
| sqlalchemy | released           |                  | 26,643 passed, 985 skipped                                 |              |      |       |
| sqlalchemy | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| sqlalchemy | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| sqlalchemy | fix-unsafe         | True             | 26,643 passed, 985 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-basedpyright | True             | 26,643 passed, 985 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-pyrefly      | True             | 26,643 passed, 985 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-trace        | True             | 26,643 passed, 985 skipped                                 |            0 |    0 |     0 |
| sqlalchemy | infer-ty           | True             | 26,643 passed, 985 skipped                                 |            0 |    0 |     0 |
| pydantic   | released           |                  | 6,439 passed, 329 skipped, 27 xfailed                      |              |      |       |
| pydantic   | fix-certain        | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pydantic   | fix-likely         | True             | as fix-unsafe's (implied)                                  |            0 |    0 |     0 |
| pydantic   | fix-unsafe         | True             | 6,439 passed, 329 skipped, 27 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-basedpyright | True             | 6,439 passed, 329 skipped, 27 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-pyrefly      | True             | 6,439 passed, 329 skipped, 27 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-trace        | True             | 6,439 passed, 329 skipped, 27 xfailed                      |            0 |    0 |     0 |
| pydantic   | infer-ty           | True             | 6,439 passed, 329 skipped, 27 xfailed                      |            0 |    0 |     0 |
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
| sqlalchemy | released           |      9 |     |      |                                                             |
| sqlalchemy | fix-certain        |      9 |   0 |    0 |    164 files changed, 1728 insertions(+), 1326 deletions(-) |
| sqlalchemy | fix-likely         |      9 |   0 |    0 |    175 files changed, 2053 insertions(+), 1631 deletions(-) |
| sqlalchemy | fix-unsafe         |      9 |   0 |    0 |    194 files changed, 2725 insertions(+), 2243 deletions(-) |
| sqlalchemy | infer-basedpyright |     16 |   7 |    0 |    199 files changed, 3641 insertions(+), 3088 deletions(-) |
| sqlalchemy | infer-pyrefly      |     58 |  49 |    0 |    201 files changed, 3931 insertions(+), 3123 deletions(-) |
| sqlalchemy | infer-trace        |     15 |   6 |    0 |    196 files changed, 2955 insertions(+), 2408 deletions(-) |
| sqlalchemy | infer-ty           |     12 |   3 |    0 |    198 files changed, 3589 insertions(+), 2914 deletions(-) |
| pydantic   | released           |      0 |     |      |                                                             |
| pydantic   | fix-certain        |      0 |   0 |    0 |      73 files changed, 1116 insertions(+), 803 deletions(-) |
| pydantic   | fix-likely         |      0 |   0 |    0 |      75 files changed, 1271 insertions(+), 932 deletions(-) |
| pydantic   | fix-unsafe         |      0 |   0 |    0 |     77 files changed, 1544 insertions(+), 1174 deletions(-) |
| pydantic   | infer-basedpyright |      3 |   3 |    0 |     80 files changed, 1875 insertions(+), 1468 deletions(-) |
| pydantic   | infer-pyrefly      |      0 |   0 |    0 |     77 files changed, 1858 insertions(+), 1346 deletions(-) |
| pydantic   | infer-trace        |      0 |   0 |    0 |     77 files changed, 1545 insertions(+), 1175 deletions(-) |
| pydantic   | infer-ty           |      3 |   3 |    0 |     77 files changed, 1734 insertions(+), 1340 deletions(-) |
| pandas     | released           |    259 |     |      |                                                             |
| pandas     | fix-certain        |    259 |   0 |    0 | 1067 files changed, 18233 insertions(+), 15224 deletions(-) |
| pandas     | fix-likely         |    259 |   0 |    0 | 1198 files changed, 42295 insertions(+), 38670 deletions(-) |
| pandas     | fix-unsafe         |    260 |   1 |    0 | 1201 files changed, 43159 insertions(+), 39415 deletions(-) |
| pandas     | infer-basedpyright |    297 |  38 |    0 | 1212 files changed, 49400 insertions(+), 45019 deletions(-) |
| pandas     | infer-pyrefly      |    384 | 125 |    0 | 1211 files changed, 48905 insertions(+), 44450 deletions(-) |
| pandas     | infer-trace        |    261 |   2 |    0 | 1205 files changed, 44610 insertions(+), 40785 deletions(-) |
| pandas     | infer-ty           |    341 |  82 |    0 | 1211 files changed, 48277 insertions(+), 44017 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus           | step               | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ---------------- | ------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| standard library | check              |    45.3 |       104.0 |  2.3 |    3.61 |          3 |     4.51 | False |
| standard library | fix-certain        |   112.4 |       281.2 |  2.5 |    4.54 |          3 |      5.7 | False |
| standard library | fix-likely         |   115.9 |       323.9 |  2.8 |    7.04 |          3 |      7.8 | False |
| standard library | fix-unsafe         |    96.8 |       245.6 |  2.5 |    5.24 |          3 |     6.54 | False |
| standard library | infer-basedpyright |   537.9 |      1011.8 |  1.9 |   12.32 |          2 |    14.46 | False |
| standard library | infer-ty           |   182.7 |       587.6 |  3.2 |   14.23 |          4 |    15.76 | False |
| standard library | infer-pyrefly      |   164.5 |       526.1 |  3.2 |   15.63 |          4 |    19.04 | False |
| standard library | census             |    31.3 |        30.1 |  1.0 |    0.43 |          3 |     4.51 | False |
| standard library | coverage           |    10.9 |        30.6 |  2.8 |    1.65 |          3 |     1.89 | False |
| standard library | timing             |   149.9 |       216.3 |  1.4 |    3.61 |         16 |     4.51 | False |
| django           | check              |     8.4 |        17.9 |  2.1 |    0.78 |          3 |     1.09 | False |
| django           | fix-certain        |    22.9 |        45.6 |  2.0 |    1.03 |          3 |     1.32 | False |
| django           | fix-likely         |    29.1 |        55.3 |  1.9 |    1.44 |          3 |     1.46 | False |
| django           | fix-unsafe         |    19.4 |        43.8 |  2.3 |    1.07 |          3 |     1.45 | False |
| django           | infer-basedpyright |    55.3 |       245.6 |  4.4 |    7.41 |          5 |     8.59 | False |
| django           | infer-ty           |    47.3 |       133.4 |  2.8 |    3.27 |          3 |     4.19 | False |
| django           | infer-pyrefly      |    34.3 |        92.8 |  2.7 |    3.44 |          3 |      4.8 | False |
| django           | census             |     3.6 |         3.5 |  1.0 |     0.1 |          3 |     1.09 | False |
| django           | coverage           |     2.0 |         0.4 |  0.2 |    0.07 |          3 |     0.52 | False |
| django           | timing             |    27.2 |        30.8 |  1.1 |    0.73 |         16 |     0.97 | False |
| django           | traced             |   387.3 |       335.5 |  0.9 |    1.19 |          1 |     1.45 | False |
| django           | tests              |   420.8 |      2371.3 |  5.6 |     4.6 |          6 |     5.85 | False |
| sqlalchemy       | check              |     0.4 |         0.3 |  0.7 |    0.07 |          2 |     0.95 | False |
| sqlalchemy       | fix-certain        |    18.2 |        34.3 |  1.9 |    0.98 |          3 |     1.36 | False |
| sqlalchemy       | fix-likely         |    23.3 |        41.3 |  1.8 |    1.29 |          3 |     1.35 | False |
| sqlalchemy       | fix-unsafe         |    22.1 |        38.9 |  1.8 |    1.11 |          2 |      1.2 | False |
| sqlalchemy       | infer-basedpyright |    64.8 |       270.6 |  4.2 |     7.3 |          4 |     8.05 | False |
| sqlalchemy       | infer-ty           |    40.1 |       115.0 |  2.9 |    3.22 |          3 |      4.5 | False |
| sqlalchemy       | infer-pyrefly      |    40.9 |        73.9 |  1.8 |    3.94 |          2 |     4.22 | False |
| sqlalchemy       | census             |    14.7 |        16.3 |  1.1 |    0.74 |          2 |     0.95 | False |
| sqlalchemy       | coverage           |     2.4 |         0.3 |  0.1 |     0.1 |          1 |     0.41 | False |
| sqlalchemy       | timing             |    20.0 |        24.2 |  1.2 |    0.89 |         16 |     0.95 | False |
| sqlalchemy       | traced             |   126.9 |       646.5 |  5.1 |    3.89 |          6 |     4.91 | False |
| sqlalchemy       | tests              |   567.6 |      3109.3 |  5.5 |    3.28 |          6 |     4.12 | False |
| sqlalchemy       | types              |    42.1 |        40.8 |  1.0 |    0.33 |          1 |     0.82 | False |
| pydantic         | check              |     1.2 |         0.2 |  0.2 |    0.07 |          1 |     0.29 | False |
| pydantic         | fix-certain        |     4.2 |         4.0 |  1.0 |    0.65 |          2 |      0.6 | False |
| pydantic         | fix-likely         |     5.2 |         2.7 |  0.5 |     0.4 |          2 |     0.85 | False |
| pydantic         | fix-unsafe         |     4.6 |         4.3 |  0.9 |     0.4 |          2 |      0.6 | False |
| pydantic         | infer-basedpyright |    41.7 |       107.7 |  2.6 |    3.34 |          4 |     4.14 | False |
| pydantic         | infer-ty           |    11.0 |        25.5 |  2.3 |    1.62 |          3 |     2.37 | False |
| pydantic         | infer-pyrefly      |    10.6 |        19.3 |  1.8 |    2.01 |          2 |     2.35 | False |
| pydantic         | census             |     5.2 |         3.2 |  0.6 |     0.5 |          1 |     0.29 | False |
| pydantic         | coverage           |     0.8 |         0.2 |  0.2 |    0.07 |          3 |      0.4 | False |
| pydantic         | timing             |     4.6 |         3.4 |  0.7 |    0.14 |         16 |      0.2 | False |
| pydantic         | traced             |    40.7 |        35.0 |  0.9 |    0.44 |          1 |     0.52 | False |
| pydantic         | tests              |   149.0 |       142.6 |  1.0 |    0.28 |          1 |     0.35 | False |
| pydantic         | types              |    68.5 |       108.9 |  1.6 |    0.62 |          2 |     0.76 | False |
| pandas           | check              |     1.0 |         0.9 |  0.9 |    0.21 |          3 |     4.97 | False |
| pandas           | fix-certain        |    90.6 |       266.6 |  2.9 |    4.72 |          3 |     5.64 | False |
| pandas           | fix-likely         |   104.7 |       329.2 |  3.1 |    8.08 |          4 |     8.96 | False |
| pandas           | fix-unsafe         |    97.6 |       280.7 |  2.9 |     5.0 |          3 |     6.05 | False |
| pandas           | infer-basedpyright |   450.2 |      1155.8 |  2.6 |   17.28 |          3 |    18.15 | False |
| pandas           | infer-ty           |   173.7 |       720.1 |  4.1 |    15.3 |          4 |    14.95 | False |
| pandas           | infer-pyrefly      |   127.3 |       482.5 |  3.8 |   17.19 |          4 |    19.97 | False |
| pandas           | census             |    63.6 |       140.1 |  2.2 |    4.11 |          3 |     4.97 | False |
| pandas           | coverage           |     8.0 |        22.0 |  2.8 |    1.15 |          4 |     1.41 | False |
| pandas           | timing             |   152.9 |       235.3 |  1.5 |    3.97 |         16 |     4.97 | False |
| pandas           | traced             |   274.6 |      1185.5 |  4.3 |   10.01 |          5 |     12.6 | False |
| pandas           | tests              |   593.6 |      3383.7 |  5.7 |    9.39 |          6 |    11.79 | False |
| pandas           | types              |   372.9 |       602.2 |  1.6 |    2.31 |          2 |     6.12 | False |
| twisted          | check              |     8.0 |        13.6 |  1.7 |     0.8 |          3 |      1.1 | False |
| twisted          | fix-certain        |    15.8 |        31.4 |  2.0 |    1.05 |          3 |     1.06 | False |
| twisted          | fix-likely         |    19.2 |        41.2 |  2.1 |    1.24 |          3 |     1.47 | False |
| twisted          | fix-unsafe         |    15.2 |        29.6 |  1.9 |    0.93 |          3 |      1.4 | False |
| twisted          | infer-basedpyright |    57.5 |       245.9 |  4.3 |    8.78 |          5 |     9.17 | False |
| twisted          | infer-ty           |    33.3 |       106.0 |  3.2 |    3.16 |          3 |      3.9 | False |
| twisted          | infer-pyrefly      |    21.1 |        73.8 |  3.5 |    4.06 |          4 |     4.77 | False |
| twisted          | census             |     4.2 |         4.2 |  1.0 |    0.11 |          3 |      1.1 | False |
| twisted          | coverage           |     2.0 |         0.8 |  0.4 |    0.27 |          3 |     0.61 | False |
| twisted          | timing             |    19.2 |        22.2 |  1.2 |     0.8 |         16 |      1.1 | False |
| pip              | check              |     5.8 |         8.4 |  1.4 |    0.58 |          2 |     0.69 | False |
| pip              | fix-certain        |    13.4 |        17.8 |  1.3 |    0.65 |          3 |     0.96 | False |
| pip              | fix-likely         |    15.8 |        29.3 |  1.9 |    0.87 |          2 |     0.96 | False |
| pip              | fix-unsafe         |    13.1 |        17.9 |  1.4 |    0.68 |          2 |     1.01 | False |
| pip              | infer-basedpyright |    60.6 |       198.5 |  3.3 |     5.4 |          4 |      6.5 | False |
| pip              | infer-ty           |    21.7 |        69.4 |  3.2 |    2.45 |          3 |     3.01 | False |
| pip              | infer-pyrefly      |    13.2 |        47.7 |  3.6 |    3.13 |          4 |     3.92 | False |
| pip              | census             |     3.6 |         3.1 |  0.9 |     0.1 |          2 |     0.69 | False |
| pip              | coverage           |     1.6 |         0.2 |  0.1 |    0.07 |          1 |      5.0 | False |
| pip              | timing             |    12.2 |        12.8 |  1.0 |    0.55 |         16 |     0.69 | False |

- standard library, super+dev, infer-basedpyright: held 12.32 GB beside other steps
- standard library, super+dev, infer-ty: held 14.23 GB beside other steps
- standard library, super+dev, infer-pyrefly: held 15.63 GB beside other steps
- pandas, super+dev, fix-likely: held 8.08 GB beside other steps
- pandas, super+dev, infer-basedpyright: held 17.28 GB beside other steps
- pandas, super+dev, infer-ty: held 15.3 GB beside other steps
- pandas, super+dev, infer-pyrefly: held 17.19 GB beside other steps
- pandas, super+dev, traced: held 10.01 GB beside other steps
- pandas, super+dev, tests: held 9.39 GB beside other steps
- twisted, super+dev, infer-basedpyright: held 8.78 GB beside other steps

## Mega corpora

The run `mega` (`python -m tests.corpus`) on mega: constricter 0.3.6 (`773ed2b6b4da`), Python
3.14.7, on 16CPU/60GB (Linux): `--jobs=4`, each step a process of its own, started once the CPUs
it's expected to keep busy and the memory it's expected to hold are free. The run took 119 minutes.
Timings don't compare across machines.

Offences per code at `suffocate`, with `all-scopes` (Python 3.14.7); the total row gives each code's
share of them:

| Corpus             | Version  | constricter | Files |        `LVA001` |       `LVA002` | `LVA003` |       `LVA004` |     `LVA005` |     `LVA006` |  `LVA009` | `LVA010` | `LVA011` |   Total |
| ------------------ | -------- | ----------- | ----: | --------------: | -------------: | -------: | -------------: | -----------: | -----------: | --------: | -------: | -------: | ------: |
| black              | 26.10.0  | mega+dev    |    25 |             996 |            232 |        0 |             45 |            5 |            4 |         0 |        0 |        0 |   1,282 |
| pdm                | 2.29.2   | mega+dev    |   128 |           2,114 |            417 |        0 |            187 |           37 |            2 |         0 |        0 |        0 |   2,757 |
| tox                | 4.64.9   | mega+dev    |   129 |           1,369 |            286 |        0 |            107 |           18 |            5 |         0 |        0 |        0 |   1,785 |
| sphinx             | 9.1.0    | mega+dev    |   243 |           5,505 |          1,336 |        1 |          1,131 |           73 |           29 |         5 |        0 |        3 |   8,083 |
| mkdocs             | 1.6.1    | mega+dev    |    61 |           1,674 |            198 |        0 |            460 |            8 |            0 |         0 |        0 |        0 |   2,340 |
| streamlink         | 8.6.1    | mega+dev    |   227 |           2,080 |            310 |        0 |            639 |           37 |           11 |         0 |        0 |        0 |   3,077 |
| mypy               | 2.4.0    | mega+dev    |   195 |           9,008 |          2,197 |        0 |            196 |          340 |           45 |         0 |        1 |        1 |  11,788 |
| httpx              | 0.28.1   | mega+dev    |    23 |             395 |            112 |        0 |             62 |            1 |            0 |         0 |        0 |        0 |     570 |
| starlette          | 1.7.0    | mega+dev    |    36 |             499 |             99 |        0 |            146 |           18 |            0 |         0 |        0 |        0 |     762 |
| uvicorn            | 0.54.0   | mega+dev    |    45 |             363 |             71 |        0 |             55 |           11 |            4 |         0 |        0 |        0 |     504 |
| anyio              | 4.15.1   | mega+dev    |    46 |             615 |             77 |        0 |             23 |           26 |            6 |         0 |        0 |        0 |     747 |
| websockets         | 17.2     | mega+dev    |    52 |             605 |             85 |        0 |            101 |            0 |            0 |         0 |        0 |        0 |     791 |
| hypercorn          | 0.18.0   | mega+dev    |    39 |             220 |             67 |        0 |             68 |            8 |            0 |         0 |        0 |        0 |     363 |
| aiohttp            | 3.14.4   | mega+dev    |    54 |           1,307 |            195 |        0 |            355 |           13 |            5 |         1 |        0 |        0 |   1,876 |
| fastapi            | 0.142.2  | mega+dev    |    52 |             586 |            105 |        0 |             51 |           98 |            5 |         0 |        0 |        0 |     845 |
| textual            | 8.2.8    | mega+dev    |   247 |           4,979 |            718 |        0 |            786 |           31 |           26 |         0 |        0 |        0 |   6,540 |
| mcp                | 2.3.0    | mega+dev    |   124 |           1,356 |            173 |        0 |            191 |          105 |            8 |         0 |        0 |        0 |   1,833 |
| pytest             | 9.1.1    | mega+dev    |    78 |           2,363 |            470 |        0 |            170 |           33 |            9 |         0 |        0 |        0 |   3,045 |
| attrs              | 26.1.0   | mega+dev    |    13 |             285 |             50 |        0 |             58 |            2 |            0 |         1 |        0 |        0 |     396 |
| werkzeug           | 3.1.9    | mega+dev    |    52 |             835 |            235 |        0 |            223 |           15 |            1 |         0 |        0 |        0 |   1,309 |
| cattrs             | 26.2.1   | mega+dev    |    36 |             420 |             70 |        0 |             30 |            9 |            1 |         0 |        0 |        0 |     530 |
| structlog          | 26.1.0   | mega+dev    |    21 |             156 |             47 |        0 |            113 |           12 |            1 |         0 |        0 |        0 |     329 |
| xarray             | 2026.9.0 | mega+dev    |   199 |          18,968 |          1,599 |        0 |            777 |          255 |           20 |         0 |        0 |        0 |  21,619 |
| networkx           | 3.7      | mega+dev    |   583 |          18,854 |          3,221 |        0 |            381 |            8 |            0 |         0 |        0 |        0 |  22,464 |
| pint               | 0.26.1   | mega+dev    |   109 |           2,591 |            297 |        0 |            190 |           14 |            2 |         0 |        0 |        0 |   3,094 |
| dask               | 2026.8.0 | mega+dev    |   361 |          20,748 |          1,691 |        0 |          1,733 |           76 |            5 |         2 |        0 |        1 |  24,256 |
| zarr               | 3.4.0    | mega+dev    |    98 |           1,874 |            370 |        0 |            167 |           26 |           35 |         0 |        0 |        0 |   2,472 |
| nibabel            | 5.4.2    | mega+dev    |   229 |           6,504 |          1,032 |        0 |            932 |            5 |            1 |         0 |        0 |        0 |   8,474 |
| seaborn            | 0.13.2   | mega+dev    |    54 |           2,361 |            370 |        0 |            164 |           23 |            3 |         0 |        0 |        0 |   2,921 |
| optuna             | 5.0.0    | mega+dev    |   220 |           2,740 |            446 |        0 |            412 |           28 |            4 |         0 |        0 |        0 |   3,630 |
| altair             | 6.3.0    | mega+dev    |    55 |             814 |            130 |        0 |            756 |           60 |            8 |         0 |        0 |        0 |   1,768 |
| stripe             | 16.0.0   | mega+dev    | 1,460 |           1,772 |             49 |        0 |          1,536 |           16 |          854 |         0 |        0 |        0 |   4,227 |
| strawberry-graphql | 0.332.0  | mega+dev    |   244 |           1,436 |            243 |        0 |            127 |          137 |            2 |         0 |        0 |        0 |   1,945 |
| litestar           | 2.24.0   | mega+dev    |   374 |           1,474 |            306 |        0 |            125 |          166 |           12 |         4 |        0 |        0 |   2,087 |
| narwhals           | 2.26.0   | mega+dev    |   162 |           2,775 |            106 |        0 |            239 |           62 |            5 |         0 |        0 |        0 |   3,187 |
| click              | 8.5.0    | mega+dev    |    17 |             481 |             58 |        0 |             69 |           28 |            1 |         0 |        0 |        0 |     637 |
| pygments           | 2.21.0   | mega+dev    |   343 |           1,124 |            539 |        0 |          6,003 |            0 |            0 |         0 |        0 |        0 |   7,666 |
| celery             | 5.6.3    | mega+dev    |   161 |           2,202 |            331 |        0 |          1,215 |            0 |            0 |         2 |        0 |        0 |   3,750 |
| botocore           | 1.43.108 | mega+dev    |    76 |           2,825 |            367 |        0 |            594 |            2 |            0 |         0 |        0 |        0 |   3,788 |
| joblib             | 1.6.0    | mega+dev    |    73 |           1,842 |            158 |        0 |            239 |            1 |            0 |         0 |        0 |        0 |   2,240 |
| **Total**          |          | mega+dev    | 6,744 | 129,115 (75.2%) | 18,863 (11.0%) | 1 (0.0%) | 20,856 (12.1%) | 1,807 (1.1%) | 1,114 (0.6%) | 15 (0.0%) | 1 (0.0%) | 5 (0.0%) | 171,777 |

Errors / warnings at each level, by the version's own rules and defaults; what `--fix` fixed, what
`--likely` guessed on top and what `--unsafe-fixes` did (each also as a share of the offences at
`suffocate`; the likely guesses are among the guessed), files a fix broke, and what a second pass
would still fix, with every guess and with the likely ones:

| Corpus             | constricter |   `relaxed` |         `strict` |     `constrict` | `suffocate` |          Fixed |        Likely |        Guessed | Broken | Left | Left, likely |
| ------------------ | ----------- | ----------: | ---------------: | --------------: | ----------: | -------------: | ------------: | -------------: | -----: | ---: | -----------: |
| black              | mega+dev    |   0 / 1,273 |      1,041 / 241 |       1,273 / 9 |   1,282 / 0 |    712 (55.5%) |    124 (9.7%) |    163 (12.7%) |      0 |    0 |            0 |
| pdm                | mega+dev    |   0 / 2,718 |      2,301 / 456 |      2,718 / 39 |   2,757 / 0 |  1,152 (41.8%) |    198 (7.2%) |    311 (11.3%) |      0 |    0 |            0 |
| tox                | mega+dev    |   0 / 1,762 |      1,476 / 309 |      1,762 / 23 |   1,785 / 0 |    942 (52.8%) |     79 (4.4%) |     134 (7.5%) |      0 |    0 |            0 |
| sphinx             | mega+dev    |   0 / 7,978 |    6,636 / 1,447 |     7,977 / 106 |   8,083 / 0 |  3,136 (38.8%) |    439 (5.4%) |    816 (10.1%) |      0 |    0 |            0 |
| mkdocs             | mega+dev    |   0 / 2,332 |      2,134 / 206 |       2,332 / 8 |   2,340 / 0 |    811 (34.7%) |   379 (16.2%) |    472 (20.2%) |      0 |    0 |            0 |
| streamlink         | mega+dev    |   0 / 3,029 |      2,719 / 358 |      3,029 / 48 |   3,077 / 0 |    674 (21.9%) |    108 (3.5%) |     232 (7.5%) |      0 |    0 |            0 |
| mypy               | mega+dev    |  0 / 11,401 |    9,204 / 2,583 |    11,401 / 387 |  11,788 / 0 |  4,738 (40.2%) | 1,175 (10.0%) |  1,562 (13.3%) |      0 |    0 |            0 |
| httpx              | mega+dev    |     0 / 569 |        457 / 113 |         569 / 1 |     570 / 0 |    235 (41.2%) |    57 (10.0%) |     73 (12.8%) |      0 |    0 |            0 |
| starlette          | mega+dev    |     0 / 744 |        645 / 117 |        744 / 18 |     762 / 0 |    311 (40.8%) |     56 (7.3%) |     97 (12.7%) |      0 |    0 |            0 |
| uvicorn            | mega+dev    |     0 / 489 |         418 / 86 |        489 / 15 |     504 / 0 |    231 (45.8%) |     29 (5.8%) |      43 (8.5%) |      0 |    0 |            0 |
| anyio              | mega+dev    |     0 / 715 |        638 / 109 |        715 / 32 |     747 / 0 |    205 (27.4%) |     32 (4.3%) |      59 (7.9%) |      0 |    0 |            0 |
| websockets         | mega+dev    |     0 / 791 |         706 / 85 |         791 / 0 |     791 / 0 |    326 (41.2%) |     59 (7.5%) |    106 (13.4%) |      0 |    0 |            0 |
| hypercorn          | mega+dev    |     0 / 355 |         288 / 75 |         355 / 8 |     363 / 0 |    135 (37.2%) |     20 (5.5%) |     57 (15.7%) |      0 |    0 |            0 |
| aiohttp            | mega+dev    |   0 / 1,858 |      1,662 / 214 |      1,858 / 18 |   1,876 / 0 |    678 (36.1%) |    141 (7.5%) |    255 (13.6%) |      0 |    0 |            0 |
| fastapi            | mega+dev    |     0 / 742 |        637 / 208 |       742 / 103 |     845 / 0 |    257 (30.4%) |     40 (4.7%) |      67 (7.9%) |      0 |    0 |            0 |
| textual            | mega+dev    |   0 / 6,483 |      5,765 / 775 |      6,483 / 57 |   6,540 / 0 |  2,567 (39.3%) |    478 (7.3%) |    727 (11.1%) |      0 |    0 |            0 |
| mcp                | mega+dev    |   0 / 1,720 |      1,547 / 286 |     1,720 / 113 |   1,833 / 0 |    691 (37.7%) |    156 (8.5%) |    235 (12.8%) |      0 |    0 |            0 |
| pytest             | mega+dev    |   0 / 3,003 |      2,533 / 512 |      3,003 / 42 |   3,045 / 0 |  1,344 (44.1%) |    160 (5.3%) |     285 (9.4%) |      0 |    0 |            0 |
| attrs              | mega+dev    |     0 / 394 |         343 / 53 |         394 / 2 |     396 / 0 |     94 (23.7%) |      9 (2.3%) |      11 (2.8%) |      0 |    0 |            0 |
| werkzeug           | mega+dev    |   0 / 1,293 |      1,058 / 251 |      1,293 / 16 |   1,309 / 0 |    530 (40.5%) |     64 (4.9%) |     126 (9.6%) |      0 |    0 |            0 |
| cattrs             | mega+dev    |     0 / 520 |         450 / 80 |        520 / 10 |     530 / 0 |    106 (20.0%) |     35 (6.6%) |      46 (8.7%) |      0 |    0 |            0 |
| structlog          | mega+dev    |     0 / 316 |         269 / 60 |        316 / 13 |     329 / 0 |     98 (29.8%) |     15 (4.6%) |      26 (7.9%) |      0 |    0 |            0 |
| xarray             | mega+dev    |  0 / 21,344 |   19,745 / 1,874 |    21,344 / 275 |  21,619 / 0 |  3,544 (16.4%) | 3,137 (14.5%) |  3,346 (15.5%) |      0 |    0 |            0 |
| networkx           | mega+dev    |  0 / 22,456 |   19,235 / 3,229 |      22,456 / 8 |  22,464 / 0 |  3,939 (17.5%) |  2,160 (9.6%) |  2,466 (11.0%) |      0 |    0 |            0 |
| pint               | mega+dev    |   0 / 3,078 |      2,781 / 313 |      3,078 / 16 |   3,094 / 0 |    561 (18.1%) |    107 (3.5%) |     160 (5.2%) |      0 |    0 |            0 |
| dask               | mega+dev    |  0 / 24,174 |   22,481 / 1,775 |     24,174 / 82 |  24,256 / 0 |  3,112 (12.8%) |  1,985 (8.2%) |  2,677 (11.0%) |      0 |    0 |            0 |
| zarr               | mega+dev    |   0 / 2,411 |      2,041 / 431 |      2,411 / 61 |   2,472 / 0 |  1,069 (43.2%) |     73 (3.0%) |     113 (4.6%) |      0 |    0 |            0 |
| nibabel            | mega+dev    |   0 / 8,468 |    7,436 / 1,038 |       8,468 / 6 |   8,474 / 0 |  1,850 (21.8%) |    681 (8.0%) |    933 (11.0%) |      0 |    0 |            0 |
| seaborn            | mega+dev    |   0 / 2,895 |      2,525 / 396 |      2,895 / 26 |   2,921 / 0 |    639 (21.9%) |    137 (4.7%) |     229 (7.8%) |      0 |    0 |            0 |
| optuna             | mega+dev    |   0 / 3,598 |      3,152 / 478 |      3,598 / 32 |   3,630 / 0 |  1,473 (40.6%) |    201 (5.5%) |     306 (8.4%) |      0 |    0 |            0 |
| altair             | mega+dev    |   0 / 1,700 |      1,570 / 198 |      1,700 / 68 |   1,768 / 0 |    373 (21.1%) |     47 (2.7%) |      62 (3.5%) |      0 |    0 |            0 |
| stripe             | mega+dev    |   0 / 3,357 |      3,308 / 919 |     3,357 / 870 |   4,227 / 0 |    565 (13.4%) |    161 (3.8%) |    663 (15.7%) |      0 |    0 |            0 |
| strawberry-graphql | mega+dev    |   0 / 1,806 |      1,563 / 382 |     1,806 / 139 |   1,945 / 0 |    595 (30.6%) |    165 (8.5%) |    213 (11.0%) |      0 |    0 |            0 |
| litestar           | mega+dev    |   0 / 1,909 |      1,599 / 488 |     1,909 / 178 |   2,087 / 0 |    595 (28.5%) |    103 (4.9%) |     165 (7.9%) |      0 |    0 |            0 |
| narwhals           | mega+dev    |   0 / 3,120 |      3,014 / 173 |      3,120 / 67 |   3,187 / 0 |    973 (30.5%) |     68 (2.1%) |     123 (3.9%) |      0 |    0 |            0 |
| click              | mega+dev    |     0 / 608 |         550 / 87 |        608 / 29 |     637 / 0 |    285 (44.7%) |     28 (4.4%) |     67 (10.5%) |      0 |    0 |            0 |
| pygments           | mega+dev    |   0 / 7,666 |      7,127 / 539 |       7,666 / 0 |   7,666 / 0 |     736 (9.6%) |     80 (1.0%) |     224 (2.9%) |      0 |    0 |            0 |
| celery             | mega+dev    |   0 / 3,750 |      3,417 / 333 |       3,750 / 0 |   3,750 / 0 |    503 (13.4%) |    119 (3.2%) |     355 (9.5%) |      0 |    0 |            0 |
| botocore           | mega+dev    |   0 / 3,786 |      3,419 / 369 |       3,786 / 2 |   3,788 / 0 |    547 (14.4%) |    166 (4.4%) |    585 (15.4%) |      0 |    0 |            0 |
| joblib             | mega+dev    |   0 / 2,239 |      2,081 / 159 |       2,239 / 1 |   2,240 / 0 |    525 (23.4%) |    177 (7.9%) |    245 (10.9%) |      0 |    0 |            0 |
| **Total**          | mega+dev    | 0 / 168,850 | 149,971 / 21,805 | 168,849 / 2,928 | 171,777 / 0 | 41,857 (24.4%) | 13,448 (7.8%) | 18,835 (11.0%) |      0 |    0 |            0 |

Annotation coverage (`--coverage` with `all-scopes`, counted by this checkout for every version):
the share of bindings typed as released, after `--fix`, after `--fix --likely` and after
`--fix --unsafe-fixes`, and how much the first and the last raised it: in percentage points, and as
a share of the bindings that were untyped:

| Corpus             | constricter | Typed as released | After `--fix` | After `--likely` | After `--unsafe-fixes` |           Raised by `--fix` |         Raised with guesses |
| ------------------ | ----------- | ----------------: | ------------: | ---------------: | ---------------------: | --------------------------: | --------------------------: |
| black              | mega+dev    |             15.9% |         62.9% |            71.1% |                  73.7% | +47.1 pts, 55.9% of untyped | +57.8 pts, 68.7% of untyped |
| pdm                | mega+dev    |             11.7% |         49.1% |            55.6% |                  59.2% | +37.4 pts, 42.4% of untyped | +47.5 pts, 53.8% of untyped |
| tox                | mega+dev    |             16.0% |         60.9% |            64.7% |                  67.3% | +44.9 pts, 53.5% of untyped | +51.3 pts, 61.1% of untyped |
| sphinx             | mega+dev    |             10.4% |         45.7% |            50.6% |                  54.8% | +35.2 pts, 39.3% of untyped | +44.4 pts, 49.6% of untyped |
| mkdocs             | mega+dev    |              4.5% |         37.7% |            53.3% |                  57.1% | +33.2 pts, 34.8% of untyped | +52.5 pts, 55.0% of untyped |
| streamlink         | mega+dev    |             42.8% |         55.5% |            57.5% |                  59.9% | +12.7 pts, 22.3% of untyped | +17.1 pts, 29.9% of untyped |
| mypy               | mega+dev    |             16.8% |         51.4% |            59.9% |                  62.8% | +34.6 pts, 41.6% of untyped | +46.0 pts, 55.2% of untyped |
| httpx              | mega+dev    |              6.3% |         45.0% |            54.4% |                  57.0% | +38.7 pts, 41.3% of untyped | +50.7 pts, 54.1% of untyped |
| starlette          | mega+dev    |             10.3% |         47.8% |            54.5% |                  59.5% | +37.5 pts, 41.8% of untyped | +49.2 pts, 54.8% of untyped |
| uvicorn            | mega+dev    |             23.6% |         59.7% |            64.2% |                  66.4% | +36.1 pts, 47.2% of untyped | +42.8 pts, 56.0% of untyped |
| anyio              | mega+dev    |             27.8% |         48.5% |            51.7% |                  54.4% | +20.7 pts, 28.7% of untyped | +26.7 pts, 36.9% of untyped |
| websockets         | mega+dev    |             13.8% |         49.3% |            55.8% |                  60.9% | +35.5 pts, 41.2% of untyped | +47.1 pts, 54.6% of untyped |
| hypercorn          | mega+dev    |             32.4% |         58.1% |            61.9% |                  69.0% | +25.7 pts, 38.0% of untyped | +36.6 pts, 54.1% of untyped |
| aiohttp            | mega+dev    |             23.7% |         51.5% |            57.3% |                  62.0% | +27.9 pts, 36.5% of untyped | +38.3 pts, 50.2% of untyped |
| fastapi            | mega+dev    |             42.0% |         62.1% |            65.2% |                  67.3% | +20.1 pts, 34.6% of untyped | +25.3 pts, 43.7% of untyped |
| textual            | mega+dev    |             15.6% |         49.0% |            55.2% |                  58.5% | +33.4 pts, 39.6% of untyped | +42.9 pts, 50.8% of untyped |
| mcp                | mega+dev    |             30.7% |         58.6% |            64.8% |                  68.0% | +27.8 pts, 40.2% of untyped | +37.3 pts, 53.8% of untyped |
| pytest             | mega+dev    |             12.1% |         51.5% |            56.1% |                  59.8% | +39.3 pts, 44.8% of untyped | +47.7 pts, 54.2% of untyped |
| attrs              | mega+dev    |              0.8% |         24.5% |            26.8% |                  27.3% | +23.7 pts, 23.9% of untyped | +26.5 pts, 26.7% of untyped |
| werkzeug           | mega+dev    |             14.3% |         49.4% |            53.7% |                  57.8% | +35.1 pts, 41.0% of untyped | +43.5 pts, 50.7% of untyped |
| cattrs             | mega+dev    |              7.0% |         25.9% |            32.2% |                  34.2% | +19.0 pts, 20.4% of untyped | +27.2 pts, 29.2% of untyped |
| structlog          | mega+dev    |             25.6% |         48.7% |            52.2% |                  54.8% | +23.1 pts, 31.0% of untyped | +29.2 pts, 39.2% of untyped |
| xarray             | mega+dev    |              4.6% |         20.4% |            34.5% |                  35.4% | +15.8 pts, 16.6% of untyped | +30.8 pts, 32.3% of untyped |
| networkx           | mega+dev    |              0.3% |         17.8% |            27.4% |                  28.7% | +17.5 pts, 17.5% of untyped | +28.4 pts, 28.5% of untyped |
| pint               | mega+dev    |              5.1% |         22.4% |            25.7% |                  27.3% | +17.3 pts, 18.2% of untyped | +22.2 pts, 23.4% of untyped |
| dask               | mega+dev    |              1.1% |         13.8% |            21.9% |                  24.8% | +12.7 pts, 12.9% of untyped | +23.7 pts, 23.9% of untyped |
| zarr               | mega+dev    |             21.7% |         56.4% |            58.8% |                  60.1% | +34.7 pts, 44.3% of untyped | +38.4 pts, 49.0% of untyped |
| nibabel            | mega+dev    |              1.0% |         22.6% |            30.6% |                  33.5% | +21.6 pts, 21.8% of untyped | +32.5 pts, 32.9% of untyped |
| seaborn            | mega+dev    |              6.9% |         27.5% |            31.9% |                  34.8% | +20.5 pts, 22.1% of untyped | +27.9 pts, 30.0% of untyped |
| optuna             | mega+dev    |              7.5% |         45.4% |            50.5% |                  53.2% | +37.9 pts, 40.9% of untyped | +45.7 pts, 49.4% of untyped |
| altair             | mega+dev    |             49.7% |         60.7% |            62.1% |                  62.6% | +11.0 pts, 21.9% of untyped | +12.9 pts, 25.6% of untyped |
| stripe             | mega+dev    |             89.5% |         91.3% |            91.8% |                  93.4% |  +1.8 pts, 16.8% of untyped |  +3.8 pts, 36.6% of untyped |
| strawberry-graphql | mega+dev    |             30.1% |         53.1% |            59.5% |                  61.3% | +23.0 pts, 32.9% of untyped | +31.3 pts, 44.7% of untyped |
| litestar           | mega+dev    |             44.9% |         62.1% |            65.1% |                  66.9% | +17.2 pts, 31.2% of untyped | +22.0 pts, 39.9% of untyped |
| narwhals           | mega+dev    |             21.7% |         46.1% |            47.8% |                  49.2% | +24.4 pts, 31.2% of untyped | +27.5 pts, 35.1% of untyped |
| click              | mega+dev    |             31.5% |         63.6% |            66.7% |                  71.1% | +32.1 pts, 46.9% of untyped | +39.7 pts, 57.9% of untyped |
| pygments           | mega+dev    |              0.0% |          9.6% |            10.6% |                  12.5% |   +9.6 pts, 9.6% of untyped | +12.5 pts, 12.5% of untyped |
| celery             | mega+dev    |              0.4% |         13.8% |            17.0% |                  23.2% | +13.4 pts, 13.4% of untyped | +22.8 pts, 22.9% of untyped |
| botocore           | mega+dev    |              0.5% |         14.8% |            19.2% |                  30.2% | +14.4 pts, 14.4% of untyped | +29.7 pts, 29.9% of untyped |
| joblib             | mega+dev    |              0.0% |         23.5% |            31.4% |                  34.4% | +23.4 pts, 23.4% of untyped | +34.4 pts, 34.4% of untyped |
| **Total**          | mega+dev    |             22.1% |         41.4% |            47.6% |                  50.1% | +19.3 pts, 24.8% of untyped | +28.0 pts, 35.9% of untyped |

Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:

| corpus             | fix                | fixed | certain | likely | guess | broken | left |  typed | bindings | seconds |
| ------------------ | ------------------ | ----: | ------: | -----: | ----: | -----: | ---: | -----: | -------: | ------: |
| black              | certain            |   712 |     712 |        |       |      0 |    0 |    952 |    1,513 |     0.8 |
| black              | likely             |   836 |     725 |    111 |       |      0 |    0 |  1,076 |    1,513 |     1.1 |
| black              | unsafe             |   875 |     712 |    111 |    52 |      0 |    0 |  1,115 |    1,513 |     1.0 |
| black              | infer-basedpyright |   946 |     712 |    110 |   124 |      0 |    0 |  1,186 |    1,513 |     4.5 |
| black              | infer-ty           | 1,068 |     712 |    115 |   241 |      0 |    0 |  1,308 |    1,513 |     4.2 |
| black              | infer-pyrefly      | 1,068 |     712 |    114 |   242 |      0 |    0 |  1,308 |    1,513 |     2.3 |
| black              | infer-trace        |   875 |     712 |    111 |    52 |      0 |    0 |  1,115 |    1,513 |     1.1 |
| pdm                | certain            | 1,152 |   1,152 |        |       |      0 |    0 |  1,513 |    3,079 |     3.3 |
| pdm                | likely             | 1,350 |   1,165 |    185 |       |      0 |    0 |  1,711 |    3,079 |     5.2 |
| pdm                | unsafe             | 1,463 |   1,152 |    184 |   127 |      0 |    0 |  1,824 |    3,079 |     3.3 |
| pdm                | infer-basedpyright | 1,855 |   1,156 |    213 |   486 |      0 |    0 |  2,216 |    3,079 |     8.8 |
| pdm                | infer-ty           | 1,958 |   1,158 |    211 |   589 |      0 |    0 |  2,319 |    3,079 |     2.7 |
| pdm                | infer-pyrefly      | 2,013 |   1,158 |    217 |   638 |      0 |    0 |  2,374 |    3,079 |     5.1 |
| pdm                | infer-trace        | 1,463 |   1,152 |    184 |   127 |      0 |    0 |  1,824 |    3,079 |     1.4 |
| tox                | certain            |   942 |     942 |        |       |      0 |    0 |  1,278 |    2,098 |     1.2 |
| tox                | likely             | 1,021 |     943 |     78 |       |      0 |    0 |  1,357 |    2,098 |     2.9 |
| tox                | unsafe             | 1,076 |     942 |     78 |    56 |      0 |    0 |  1,412 |    2,098 |     2.2 |
| tox                | infer-basedpyright | 1,340 |     944 |     95 |   301 |      0 |    0 |  1,676 |    2,098 |     8.5 |
| tox                | infer-ty           | 1,375 |     944 |     95 |   336 |      0 |    0 |  1,711 |    2,098 |     5.0 |
| tox                | infer-pyrefly      | 1,425 |     944 |     95 |   386 |      0 |    0 |  1,761 |    2,098 |     3.3 |
| tox                | infer-trace        | 1,076 |     942 |     78 |    56 |      0 |    0 |  1,412 |    2,098 |     3.5 |
| sphinx             | certain            | 3,136 |   3,136 |        |       |      0 |    0 |  4,064 |    8,901 |     3.5 |
| sphinx             | likely             | 3,575 |   3,146 |    429 |       |      0 |    0 |  4,503 |    8,901 |     4.5 |
| sphinx             | unsafe             | 3,952 |   3,136 |    426 |   390 |      0 |    0 |  4,880 |    8,901 |     3.8 |
| sphinx             | infer-basedpyright | 4,735 |   3,141 |    455 | 1,139 |      0 |    0 |  5,663 |    8,901 |    14.0 |
| sphinx             | infer-ty           | 4,881 |   3,140 |    457 | 1,284 |      0 |    2 |  5,809 |    8,901 |     9.8 |
| sphinx             | infer-pyrefly      | 5,096 |   3,141 |    471 | 1,484 |      0 |    2 |  6,024 |    8,901 |     6.0 |
| sphinx             | infer-trace        | 3,952 |   3,136 |    426 |   390 |      0 |    0 |  4,880 |    8,901 |     3.5 |
| mkdocs             | certain            |   811 |     811 |        |       |      0 |    0 |    922 |    2,443 |     1.2 |
| mkdocs             | likely             | 1,190 |     841 |    349 |       |      0 |    0 |  1,301 |    2,443 |     1.6 |
| mkdocs             | unsafe             | 1,283 |     811 |    349 |   123 |      0 |    0 |  1,394 |    2,443 |     1.3 |
| mkdocs             | infer-basedpyright | 1,386 |     811 |    356 |   219 |      0 |    0 |  1,497 |    2,443 |     9.4 |
| mkdocs             | infer-ty           | 1,422 |     811 |    361 |   250 |      0 |    0 |  1,533 |    2,443 |     3.4 |
| mkdocs             | infer-pyrefly      | 1,554 |     811 |    364 |   379 |      0 |    0 |  1,665 |    2,443 |     3.1 |
| mkdocs             | infer-trace        | 1,295 |     812 |    348 |   135 |      0 |    0 |  1,406 |    2,443 |     1.6 |
| streamlink         | certain            |   674 |     674 |        |       |      0 |    0 |  2,936 |    5,291 |     1.7 |
| streamlink         | likely             |   782 |     677 |    105 |       |      0 |    0 |  3,044 |    5,291 |     7.2 |
| streamlink         | unsafe             |   906 |     674 |    105 |   127 |      0 |    0 |  3,168 |    5,291 |     1.5 |
| streamlink         | infer-basedpyright | 1,317 |     674 |    127 |   516 |      0 |    0 |  3,579 |    5,291 |    17.6 |
| streamlink         | infer-ty           | 1,469 |     674 |    138 |   657 |      0 |    0 |  3,731 |    5,291 |     5.3 |
| streamlink         | infer-pyrefly      | 1,567 |     674 |    153 |   740 |      0 |    0 |  3,829 |    5,291 |     4.3 |
| streamlink         | infer-trace        |   914 |     674 |    105 |   135 |      0 |    0 |  3,176 |    5,291 |     2.8 |
| mypy               | certain            | 4,738 |   4,738 |        |       |      0 |    0 |  7,038 |   13,701 |    12.7 |
| mypy               | likely             | 5,913 |   4,760 |  1,153 |       |      0 |    0 |  8,213 |   13,701 |    10.5 |
| mypy               | unsafe             | 6,300 |   4,738 |  1,151 |   411 |      0 |    0 |  8,599 |   13,701 |    12.8 |
| mypy               | infer-basedpyright | 8,231 |   4,743 |  1,265 | 2,223 |      0 |    0 | 10,530 |   13,701 |    47.7 |
| mypy               | infer-ty           | 8,554 |   4,742 |  1,276 | 2,536 |      0 |    0 | 10,853 |   13,701 |    23.9 |
| mypy               | infer-pyrefly      | 8,806 |   4,738 |  1,284 | 2,784 |      0 |    0 | 11,105 |   13,701 |    17.7 |
| mypy               | infer-trace        | 6,300 |   4,738 |  1,151 |   411 |      0 |    0 |  8,599 |   13,701 |     6.7 |
| httpx              | certain            |   235 |     235 |        |       |      0 |    0 |    273 |      607 |     0.6 |
| httpx              | likely             |   292 |     244 |     48 |       |      0 |    0 |    330 |      607 |     1.1 |
| httpx              | unsafe             |   308 |     235 |     48 |    25 |      0 |    0 |    346 |      607 |     0.8 |
| httpx              | infer-basedpyright |   409 |     235 |     53 |   121 |      0 |    0 |    447 |      607 |     6.4 |
| httpx              | infer-ty           |   381 |     235 |     52 |    94 |      0 |    0 |    419 |      607 |     2.1 |
| httpx              | infer-pyrefly      |   391 |     235 |     53 |   103 |      0 |    0 |    429 |      607 |     1.5 |
| httpx              | infer-trace        |   308 |     235 |     48 |    25 |      0 |    0 |    346 |      607 |     0.8 |
| starlette          | certain            |   311 |     311 |        |       |      0 |    0 |    396 |      829 |     0.5 |
| starlette          | likely             |   367 |     311 |     56 |       |      0 |    0 |    452 |      829 |     1.1 |
| starlette          | unsafe             |   408 |     311 |     56 |    41 |      0 |    0 |    493 |      829 |     0.8 |
| starlette          | infer-basedpyright |   487 |     311 |     56 |   120 |      0 |    0 |    572 |      829 |     4.4 |
| starlette          | infer-ty           |   491 |     311 |     55 |   125 |      0 |    0 |    576 |      829 |     2.2 |
| starlette          | infer-pyrefly      |   492 |     311 |     56 |   125 |      0 |    0 |    577 |      829 |     1.7 |
| starlette          | infer-trace        |   408 |     311 |     56 |    41 |      0 |    0 |    493 |      829 |     0.9 |
| uvicorn            | certain            |   231 |     231 |        |       |      0 |    0 |    382 |      640 |     1.3 |
| uvicorn            | likely             |   260 |     231 |     29 |       |      0 |    0 |    411 |      640 |     2.3 |
| uvicorn            | unsafe             |   274 |     231 |     29 |    14 |      0 |    0 |    425 |      640 |     1.2 |
| uvicorn            | infer-basedpyright |   347 |     231 |     32 |    84 |      0 |    0 |    498 |      640 |     5.2 |
| uvicorn            | infer-ty           |   354 |     232 |     29 |    93 |      0 |    0 |    505 |      640 |     1.9 |
| uvicorn            | infer-pyrefly      |   381 |     232 |     34 |   115 |      0 |    0 |    532 |      640 |     3.4 |
| uvicorn            | infer-trace        |   274 |     231 |     29 |    14 |      0 |    0 |    425 |      640 |     1.7 |
| anyio              | certain            |   205 |     205 |        |       |      0 |    0 |    480 |      990 |     2.1 |
| anyio              | likely             |   237 |     205 |     32 |       |      0 |    0 |    512 |      990 |     2.6 |
| anyio              | unsafe             |   264 |     205 |     32 |    27 |      0 |    0 |    539 |      990 |     1.4 |
| anyio              | infer-basedpyright |   371 |     205 |     40 |   126 |      0 |    0 |    646 |      990 |    17.4 |
| anyio              | infer-ty           |   414 |     205 |     49 |   160 |      0 |    0 |    689 |      990 |     6.4 |
| anyio              | infer-pyrefly      |   443 |     205 |     49 |   189 |      0 |    0 |    718 |      990 |     4.1 |
| anyio              | infer-trace        |   264 |     205 |     32 |    27 |      0 |    0 |    539 |      990 |     2.9 |
| websockets         | certain            |   326 |     326 |        |       |      0 |    0 |    453 |      918 |     1.8 |
| websockets         | likely             |   385 |     327 |     58 |       |      0 |    0 |    512 |      918 |     2.3 |
| websockets         | unsafe             |   432 |     326 |     58 |    48 |      0 |    0 |    559 |      918 |     2.1 |
| websockets         | infer-basedpyright |   552 |     328 |     58 |   166 |      0 |    0 |    679 |      918 |    10.4 |
| websockets         | infer-ty           |   572 |     328 |     58 |   186 |      0 |    0 |    699 |      918 |     7.1 |
| websockets         | infer-pyrefly      |   589 |     328 |     58 |   203 |      0 |    0 |    716 |      918 |     4.3 |
| websockets         | infer-trace        |   432 |     326 |     58 |    48 |      0 |    0 |    559 |      918 |     0.8 |
| hypercorn          | certain            |   135 |     135 |        |       |      0 |    0 |    305 |      525 |     0.4 |
| hypercorn          | likely             |   155 |     135 |     20 |       |      0 |    0 |    325 |      525 |     0.5 |
| hypercorn          | unsafe             |   192 |     135 |     20 |    37 |      0 |    0 |    362 |      525 |     0.4 |
| hypercorn          | infer-basedpyright |   214 |     135 |     21 |    58 |      0 |    0 |    384 |      525 |     3.0 |
| hypercorn          | infer-ty           |   229 |     135 |     21 |    73 |      0 |    0 |    399 |      525 |     1.0 |
| hypercorn          | infer-pyrefly      |   244 |     135 |     26 |    83 |      0 |    0 |    414 |      525 |     1.0 |
| hypercorn          | infer-trace        |   192 |     135 |     20 |    37 |      0 |    0 |    362 |      525 |     0.5 |
| aiohttp            | certain            |   678 |     678 |        |       |      0 |    0 |  1,254 |    2,433 |     2.2 |
| aiohttp            | likely             |   819 |     684 |    135 |       |      0 |    0 |  1,395 |    2,433 |     4.0 |
| aiohttp            | unsafe             |   933 |     678 |    135 |   120 |      0 |    0 |  1,509 |    2,433 |     2.4 |
| aiohttp            | infer-basedpyright | 1,133 |     681 |    143 |   309 |      0 |    0 |  1,709 |    2,433 |    13.0 |
| aiohttp            | infer-ty           | 1,238 |     681 |    147 |   410 |      0 |    0 |  1,814 |    2,433 |     7.6 |
| aiohttp            | infer-pyrefly      | 1,266 |     681 |    148 |   437 |      0 |    0 |  1,842 |    2,433 |     3.8 |
| aiohttp            | infer-trace        |   934 |     678 |    135 |   121 |      0 |    0 |  1,510 |    2,433 |     1.2 |
| fastapi            | certain            |   257 |     257 |        |       |      0 |    0 |    794 |    1,279 |     1.5 |
| fastapi            | likely             |   297 |     263 |     34 |       |      0 |    0 |    834 |    1,279 |     3.4 |
| fastapi            | unsafe             |   324 |     257 |     34 |    33 |      0 |    0 |    861 |    1,279 |     1.6 |
| fastapi            | infer-basedpyright |   350 |     257 |     33 |    60 |      0 |    0 |    887 |    1,279 |     7.9 |
| fastapi            | infer-ty           |   372 |     257 |     32 |    83 |      0 |    0 |    909 |    1,279 |     3.4 |
| fastapi            | infer-pyrefly      |   390 |     257 |     35 |    98 |      0 |    0 |    927 |    1,279 |     3.1 |
| fastapi            | infer-trace        |   324 |     257 |     34 |    33 |      0 |    0 |    861 |    1,279 |     1.2 |
| textual            | certain            | 2,567 |   2,567 |        |       |      0 |    0 |  3,761 |    7,677 |     2.5 |
| textual            | likely             | 3,045 |   2,596 |    449 |       |      0 |    0 |  4,239 |    7,677 |     4.4 |
| textual            | unsafe             | 3,294 |   2,567 |    448 |   279 |      0 |    0 |  4,488 |    7,677 |     2.4 |
| textual            | infer-basedpyright | 4,550 |   2,568 |    522 | 1,460 |      0 |   20 |  5,744 |    7,677 |    18.1 |
| textual            | infer-ty           | 4,637 |   2,568 |    529 | 1,540 |      0 |    0 |  5,831 |    7,677 |     9.2 |
| textual            | infer-pyrefly      | 3,758 |   2,568 |    470 |   720 |      0 |    0 |  4,952 |    7,677 |     6.2 |
| mcp                | certain            |   691 |     691 |        |       |      0 |    0 |  1,454 |    2,483 |     3.0 |
| mcp                | likely             |   847 |     697 |    150 |       |      0 |    0 |  1,610 |    2,483 |     1.9 |
| mcp                | unsafe             |   926 |     691 |    150 |    85 |      0 |    0 |  1,689 |    2,483 |     2.4 |
| mcp                | infer-basedpyright | 1,057 |     691 |    162 |   204 |      0 |    0 |  1,820 |    2,483 |     8.5 |
| mcp                | infer-ty           | 1,160 |     692 |    158 |   310 |      0 |    0 |  1,923 |    2,483 |     4.5 |
| mcp                | infer-pyrefly      | 1,207 |     692 |    155 |   360 |      0 |    0 |  1,970 |    2,483 |     3.6 |
| mcp                | infer-trace        |   926 |     691 |    150 |    85 |      0 |    0 |  1,689 |    2,483 |     1.9 |
| pytest             | certain            | 1,344 |   1,344 |        |       |      0 |    0 |  1,759 |    3,418 |     4.0 |
| pytest             | likely             | 1,504 |   1,348 |    156 |       |      0 |    0 |  1,919 |    3,418 |     5.8 |
| pytest             | unsafe             | 1,629 |   1,344 |    156 |   129 |      0 |    0 |  2,044 |    3,418 |     4.6 |
| pytest             | infer-basedpyright | 1,982 |   1,343 |    174 |   465 |      0 |    0 |  2,397 |    3,418 |    14.4 |
| pytest             | infer-ty           | 1,988 |   1,343 |    176 |   469 |      0 |    0 |  2,403 |    3,418 |    10.7 |
| pytest             | infer-pyrefly      | 2,057 |   1,343 |    180 |   534 |      0 |    0 |  2,472 |    3,418 |     8.0 |
| pytest             | infer-trace        | 1,647 |   1,344 |    156 |   147 |      0 |    0 |  2,062 |    3,418 |     3.1 |
| attrs              | certain            |    94 |      94 |        |       |      0 |    0 |     97 |      396 |     0.6 |
| attrs              | likely             |   103 |      95 |      8 |       |      0 |    0 |    106 |      396 |     0.8 |
| attrs              | unsafe             |   105 |      94 |      8 |     3 |      0 |    0 |    108 |      396 |     0.7 |
| attrs              | infer-basedpyright |   132 |      94 |      8 |    30 |      0 |    0 |    135 |      396 |     3.9 |
| attrs              | infer-ty           |   116 |      94 |      8 |    14 |      0 |    0 |    119 |      396 |     1.4 |
| attrs              | infer-pyrefly      |   119 |      94 |      8 |    17 |      0 |    0 |    122 |      396 |     1.4 |
| attrs              | infer-trace        |   108 |      94 |      9 |     5 |      0 |    0 |    111 |      396 |     0.9 |
| werkzeug           | certain            |   530 |     530 |        |       |      0 |    0 |    746 |    1,509 |     0.9 |
| werkzeug           | likely             |   594 |     531 |     63 |       |      0 |    0 |    810 |    1,509 |     2.1 |
| werkzeug           | unsafe             |   656 |     530 |     63 |    63 |      0 |    0 |    872 |    1,509 |     0.9 |
| werkzeug           | infer-basedpyright |   778 |     530 |     75 |   173 |      0 |    0 |    994 |    1,509 |     6.1 |
| werkzeug           | infer-ty           |   800 |     530 |     78 |   192 |      0 |    0 |  1,016 |    1,509 |     3.1 |
| werkzeug           | infer-pyrefly      |   870 |     530 |     77 |   263 |      0 |    0 |  1,086 |    1,509 |     2.5 |
| werkzeug           | infer-trace        |   656 |     530 |     63 |    63 |      0 |    0 |    872 |    1,509 |     1.4 |
| cattrs             | certain            |   106 |     106 |        |       |      0 |    0 |    145 |      559 |     1.2 |
| cattrs             | likely             |   141 |     113 |     28 |       |      0 |    0 |    180 |      559 |     1.9 |
| cattrs             | unsafe             |   152 |     109 |     27 |    16 |      0 |    0 |    191 |      559 |     2.0 |
| cattrs             | infer-basedpyright |   196 |     108 |     30 |    58 |      0 |    0 |    235 |      559 |    11.5 |
| cattrs             | infer-ty           |   190 |     106 |     28 |    56 |      0 |    0 |    229 |      559 |     2.4 |
| cattrs             | infer-pyrefly      |   177 |     108 |     29 |    40 |      0 |    0 |    216 |      559 |     5.0 |
| cattrs             | infer-trace        |   152 |     109 |     27 |    16 |      0 |    0 |    191 |      559 |     0.6 |
| structlog          | certain            |    98 |      98 |        |       |      0 |    0 |    207 |      425 |     0.5 |
| structlog          | likely             |   113 |      98 |     15 |       |      0 |    0 |    222 |      425 |     1.0 |
| structlog          | unsafe             |   124 |      98 |     15 |    11 |      0 |    0 |    233 |      425 |     0.5 |
| structlog          | infer-basedpyright |   151 |      98 |     16 |    37 |      0 |    0 |    260 |      425 |     3.6 |
| structlog          | infer-ty           |   135 |      98 |     16 |    21 |      0 |    0 |    244 |      425 |     1.0 |
| structlog          | infer-pyrefly      |   146 |      98 |     17 |    31 |      0 |    0 |    255 |      425 |     0.9 |
| structlog          | infer-trace        |   124 |      98 |     15 |    11 |      0 |    0 |    233 |      425 |     0.6 |
| xarray             | certain            | 3,544 |   3,544 |        |       |      0 |    0 |  4,573 |   22,373 |    20.0 |
| xarray             | likely             | 6,681 |   3,586 |  3,095 |       |      0 |    0 |  7,710 |   22,373 |    21.2 |
| xarray             | unsafe             | 6,890 |   3,544 |  3,095 |   251 |      0 |    0 |  7,919 |   22,373 |    19.8 |
| xarray             | infer-basedpyright | 8,912 |   3,511 |  3,150 | 2,251 |      0 |    0 |  9,941 |   22,373 |    82.5 |
| xarray             | infer-ty           | 8,921 |   3,511 |  3,149 | 2,261 |      0 |    4 |  9,950 |   22,373 |    71.2 |
| xarray             | infer-pyrefly      | 9,072 |   3,511 |  3,163 | 2,398 |      0 |    0 | 10,101 |   22,373 |    48.3 |
| xarray             | infer-trace        | 6,924 |   3,544 |  3,094 |   286 |      0 |    0 |  7,953 |   22,373 |    20.6 |
| networkx           | certain            | 3,939 |   3,939 |        |       |      0 |    0 |  4,001 |   22,518 |     6.3 |
| networkx           | likely             | 6,099 |   3,988 |  2,111 |       |      0 |    0 |  6,161 |   22,518 |    10.9 |
| networkx           | unsafe             | 6,405 |   3,939 |  2,097 |   369 |      0 |    0 |  6,467 |   22,518 |     6.7 |
| networkx           | infer-basedpyright | 7,415 |   3,941 |  2,166 | 1,308 |      0 |    6 |  7,477 |   22,518 |    66.5 |
| networkx           | infer-ty           | 6,860 |   3,939 |  2,122 |   799 |      0 |    0 |  6,922 |   22,518 |    26.2 |
| networkx           | infer-pyrefly      | 7,017 |   3,943 |  2,136 |   938 |      0 |    9 |  7,079 |   22,518 |    27.0 |
| networkx           | infer-trace        | 6,931 |   3,939 |  2,135 |   857 |      0 |    3 |  6,993 |   22,518 |    11.0 |
| pint               | certain            |   561 |     561 |        |       |      0 |    0 |    726 |    3,243 |     4.9 |
| pint               | likely             |   668 |     567 |    101 |       |      0 |    0 |    833 |    3,243 |     5.7 |
| pint               | unsafe             |   721 |     561 |    101 |    59 |      0 |    0 |    886 |    3,243 |     4.3 |
| pint               | infer-basedpyright | 1,018 |     559 |    105 |   354 |      0 |   12 |  1,183 |    3,243 |    31.1 |
| pint               | infer-ty           |   905 |     559 |     98 |   248 |      0 |    0 |  1,070 |    3,243 |    20.7 |
| pint               | infer-pyrefly      | 1,033 |     559 |    106 |   368 |      0 |    3 |  1,198 |    3,243 |    10.5 |
| pint               | infer-trace        |   758 |     561 |    101 |    96 |      0 |    0 |    923 |    3,243 |     2.5 |
| dask               | certain            | 3,112 |   3,112 |        |       |      0 |    0 |  3,370 |   24,430 |    21.9 |
| dask               | likely             | 5,097 |   3,179 |  1,918 |       |      0 |    0 |  5,355 |   24,430 |    51.2 |
| dask               | unsafe             | 5,789 |   3,147 |  1,916 |   726 |      0 |    0 |  6,047 |   24,430 |    55.0 |
| dask               | infer-basedpyright | 6,759 |   3,146 |  1,963 | 1,650 |      0 |   36 |  7,017 |   24,430 |   154.6 |
| dask               | infer-ty           | 6,208 |   3,147 |  1,949 | 1,112 |      0 |   17 |  6,466 |   24,430 |   101.9 |
| dask               | infer-pyrefly      | 6,833 |   3,147 |  1,961 | 1,725 |      0 |   56 |  7,091 |   24,430 |    51.0 |
| dask               | infer-trace        | 6,130 |   3,147 |  1,916 | 1,067 |      0 |    0 |  6,388 |   24,430 |    38.6 |
| zarr               | certain            | 1,069 |   1,069 |        |       |      0 |    0 |  1,737 |    3,079 |     2.9 |
| zarr               | likely             | 1,142 |   1,070 |     72 |       |      0 |    0 |  1,810 |    3,079 |     4.5 |
| zarr               | unsafe             | 1,182 |   1,069 |     72 |    41 |      0 |    0 |  1,850 |    3,079 |     4.6 |
| zarr               | infer-basedpyright | 1,646 |   1,069 |     99 |   478 |      0 |    2 |  2,314 |    3,079 |    26.3 |
| zarr               | infer-ty           | 1,604 |   1,069 |     98 |   437 |      0 |    0 |  2,272 |    3,079 |    10.4 |
| zarr               | infer-pyrefly      | 1,649 |   1,069 |    101 |   479 |      0 |    0 |  2,317 |    3,079 |     5.2 |
| zarr               | infer-trace        | 1,182 |   1,069 |     72 |    41 |      0 |    0 |  1,850 |    3,079 |     1.4 |
| nibabel            | certain            | 1,850 |   1,850 |        |       |      0 |    0 |  1,932 |    8,550 |     3.5 |
| nibabel            | likely             | 2,531 |   1,874 |    657 |       |      0 |    0 |  2,613 |    8,550 |     7.7 |
| nibabel            | unsafe             | 2,783 |   1,850 |    657 |   276 |      0 |    0 |  2,865 |    8,550 |     5.1 |
| nibabel            | infer-basedpyright | 3,395 |   1,851 |    696 |   848 |      0 |    5 |  3,477 |    8,550 |    49.6 |
| nibabel            | infer-ty           | 3,369 |   1,851 |    715 |   803 |      0 |    8 |  3,451 |    8,550 |    38.4 |
| nibabel            | infer-pyrefly      | 3,758 |   1,851 |    726 | 1,181 |      0 |    8 |  3,840 |    8,550 |     8.8 |
| nibabel            | infer-trace        | 2,875 |   1,850 |    662 |   363 |      0 |    0 |  2,957 |    8,550 |     6.3 |
| seaborn            | certain            |   639 |     639 |        |       |      0 |    0 |    854 |    3,110 |     1.8 |
| seaborn            | likely             |   776 |     647 |    129 |       |      0 |    0 |    991 |    3,110 |     4.1 |
| seaborn            | unsafe             |   868 |     639 |    129 |   100 |      0 |    0 |  1,083 |    3,110 |     2.9 |
| seaborn            | infer-basedpyright | 1,012 |     639 |    132 |   241 |      0 |    4 |  1,227 |    3,110 |    29.4 |
| seaborn            | infer-ty           |   953 |     638 |    131 |   184 |      0 |    0 |  1,168 |    3,110 |     6.6 |
| seaborn            | infer-pyrefly      | 1,041 |     639 |    133 |   269 |      0 |    0 |  1,256 |    3,110 |     4.9 |
| seaborn            | infer-trace        |   906 |     639 |    131 |   136 |      0 |    0 |  1,121 |    3,110 |     2.8 |
| optuna             | certain            | 1,473 |   1,473 |        |       |      0 |    0 |  1,764 |    3,889 |     5.1 |
| optuna             | likely             | 1,674 |   1,479 |    195 |       |      0 |    0 |  1,965 |    3,889 |    27.3 |
| optuna             | unsafe             | 1,779 |   1,473 |    195 |   111 |      0 |    0 |  2,070 |    3,889 |     5.4 |
| optuna             | infer-basedpyright | 2,136 |   1,473 |    216 |   447 |      0 |    5 |  2,427 |    3,889 |    46.0 |
| optuna             | infer-ty           | 2,185 |   1,473 |    234 |   478 |      0 |    5 |  2,476 |    3,889 |    17.4 |
| optuna             | infer-pyrefly      | 2,226 |   1,473 |    227 |   526 |      0 |    5 |  2,517 |    3,889 |    23.7 |
| optuna             | infer-trace        | 1,779 |   1,473 |    195 |   111 |      0 |    0 |  2,070 |    3,889 |     4.0 |
| altair             | certain            |   373 |     373 |        |       |      0 |    0 |  2,055 |    3,383 |     6.2 |
| altair             | likely             |   420 |     373 |     47 |       |      0 |    0 |  2,102 |    3,383 |     9.8 |
| altair             | unsafe             |   435 |     373 |     47 |    15 |      0 |    0 |  2,117 |    3,383 |     7.2 |
| altair             | infer-basedpyright |   506 |     370 |     51 |    85 |      0 |    0 |  2,188 |    3,383 |    16.3 |
| altair             | infer-ty           |   501 |     370 |     48 |    83 |      0 |    3 |  2,183 |    3,383 |    12.2 |
| altair             | infer-pyrefly      |   543 |     370 |     49 |   124 |      0 |    3 |  2,225 |    3,383 |    11.8 |
| altair             | infer-trace        |   442 |     373 |     48 |    21 |      0 |    0 |  2,124 |    3,383 |     3.2 |
| stripe             | certain            |   565 |     565 |        |       |      0 |    0 | 29,315 |   32,107 |     4.2 |
| stripe             | likely             |   726 |     565 |    161 |       |      0 |    0 | 29,476 |   32,107 |     7.1 |
| stripe             | unsafe             | 1,228 |     565 |    161 |   502 |      0 |    0 | 29,978 |   32,107 |     4.5 |
| stripe             | infer-basedpyright | 1,949 |     565 |    161 | 1,223 |      0 |    0 | 30,699 |   32,107 |   421.5 |
| stripe             | infer-ty           | 1,282 |     565 |    161 |   556 |      0 |    0 | 30,032 |   32,107 |    13.5 |
| stripe             | infer-pyrefly      | 1,277 |     565 |    161 |   551 |      0 |    0 | 30,027 |   32,107 |    14.1 |
| strawberry-graphql | certain            |   595 |     595 |        |       |      0 |    0 |  1,371 |    2,582 |     1.7 |
| strawberry-graphql | likely             |   760 |     597 |    163 |       |      0 |    0 |  1,536 |    2,582 |     6.6 |
| strawberry-graphql | unsafe             |   808 |     595 |    163 |    50 |      0 |    0 |  1,584 |    2,582 |     4.5 |
| strawberry-graphql | infer-basedpyright |   983 |     594 |    163 |   226 |      0 |    0 |  1,759 |    2,582 |     9.9 |
| strawberry-graphql | infer-ty           | 1,022 |     595 |    163 |   264 |      0 |    0 |  1,798 |    2,582 |     4.0 |
| strawberry-graphql | infer-pyrefly      | 1,018 |     595 |    165 |   258 |      0 |    0 |  1,794 |    2,582 |     3.1 |
| strawberry-graphql | infer-trace        |   808 |     595 |    163 |    50 |      0 |    0 |  1,584 |    2,582 |     1.3 |
| litestar           | certain            |   595 |     595 |        |       |      0 |    0 |  2,149 |    3,459 |     2.7 |
| litestar           | likely             |   698 |     596 |    102 |       |      0 |    0 |  2,252 |    3,459 |    12.0 |
| litestar           | unsafe             |   760 |     595 |    102 |    63 |      0 |    0 |  2,314 |    3,459 |     1.8 |
| litestar           | infer-basedpyright | 1,031 |     592 |    113 |   326 |      0 |    0 |  2,585 |    3,459 |    18.8 |
| litestar           | infer-ty           | 1,039 |     592 |    116 |   331 |      0 |    0 |  2,593 |    3,459 |    12.1 |
| litestar           | infer-pyrefly      | 1,102 |     592 |    119 |   391 |      0 |    0 |  2,656 |    3,459 |     6.4 |
| litestar           | infer-trace        |   760 |     595 |    102 |    63 |      0 |    0 |  2,314 |    3,459 |     3.0 |
| narwhals           | certain            |   973 |     973 |        |       |      0 |    0 |  1,838 |    3,985 |     1.9 |
| narwhals           | likely             | 1,041 |     974 |     67 |       |      0 |    0 |  1,906 |    3,985 |    15.0 |
| narwhals           | unsafe             | 1,096 |     973 |     67 |    56 |      0 |    0 |  1,961 |    3,985 |    11.0 |
| narwhals           | infer-basedpyright | 1,425 |     982 |     80 |   363 |      0 |    0 |  2,290 |    3,985 |    30.2 |
| narwhals           | infer-ty           | 1,556 |     982 |     89 |   485 |      0 |    0 |  2,421 |    3,985 |    15.2 |
| narwhals           | infer-pyrefly      | 1,602 |     982 |     81 |   539 |      0 |    3 |  2,467 |    3,985 |     9.3 |
| narwhals           | infer-trace        | 1,096 |     973 |     67 |    56 |      0 |    0 |  1,961 |    3,985 |     1.8 |
| click              | certain            |   285 |     285 |        |       |      0 |    0 |    564 |      887 |     0.5 |
| click              | likely             |   313 |     286 |     27 |       |      0 |    0 |    592 |      887 |     0.8 |
| click              | unsafe             |   352 |     285 |     27 |    40 |      0 |    0 |    631 |      887 |     0.8 |
| click              | infer-basedpyright |   434 |     286 |     30 |   118 |      0 |    0 |    713 |      887 |     5.9 |
| click              | infer-ty           |   449 |     286 |     25 |   138 |      0 |    0 |    728 |      887 |     1.8 |
| click              | infer-pyrefly      |   453 |     285 |     31 |   137 |      0 |    0 |    732 |      887 |     1.4 |
| click              | infer-trace        |   352 |     285 |     27 |    40 |      0 |    0 |    631 |      887 |     0.9 |
| pygments           | certain            |   736 |     736 |        |       |      0 |    0 |    736 |    7,666 |     2.1 |
| pygments           | likely             |   816 |     739 |     77 |       |      0 |    0 |    816 |    7,666 |     3.0 |
| pygments           | unsafe             |   960 |     736 |     77 |   147 |      0 |    0 |    960 |    7,666 |     5.1 |
| pygments           | infer-basedpyright | 1,074 |     736 |     84 |   254 |      0 |    0 |  1,074 |    7,666 |    21.0 |
| pygments           | infer-ty           | 1,078 |     736 |     85 |   257 |      0 |    0 |  1,078 |    7,666 |     5.8 |
| pygments           | infer-pyrefly      | 1,139 |     736 |     85 |   318 |      0 |    2 |  1,139 |    7,666 |     5.3 |
| pygments           | infer-trace        | 1,069 |     731 |     99 |   239 |      0 |    0 |  1,069 |    7,666 |     2.5 |
| celery             | certain            |   503 |     503 |        |       |      0 |    0 |    519 |    3,764 |     8.7 |
| celery             | likely             |   622 |     506 |    116 |       |      0 |    0 |    638 |    3,764 |     9.3 |
| celery             | unsafe             |   858 |     503 |    116 |   239 |      0 |    0 |    874 |    3,764 |     9.5 |
| celery             | infer-basedpyright | 1,018 |     503 |    125 |   390 |      0 |   13 |  1,034 |    3,764 |    30.5 |
| celery             | infer-ty           |   937 |     503 |    117 |   317 |      0 |    0 |    953 |    3,764 |     9.0 |
| celery             | infer-pyrefly      | 1,067 |     503 |    119 |   445 |      0 |    0 |  1,083 |    3,764 |     7.0 |
| celery             | infer-trace        |   922 |     503 |    115 |   304 |      0 |    0 |    938 |    3,764 |     2.4 |
| botocore           | certain            |   547 |     547 |        |       |      0 |    0 |    565 |    3,806 |     4.4 |
| botocore           | likely             |   713 |     553 |    160 |       |      0 |    0 |    731 |    3,806 |     8.2 |
| botocore           | unsafe             | 1,132 |     545 |    160 |   427 |      0 |    0 |  1,150 |    3,806 |     2.5 |
| botocore           | infer-basedpyright | 1,287 |     540 |    163 |   584 |      0 |    0 |  1,305 |    3,806 |    12.5 |
| botocore           | infer-ty           | 1,194 |     545 |    161 |   488 |      0 |    3 |  1,212 |    3,806 |     3.2 |
| botocore           | infer-pyrefly      | 1,274 |     540 |    166 |   568 |      0 |    0 |  1,292 |    3,806 |     3.3 |
| botocore           | infer-trace        | 1,480 |     545 |    189 |   746 |      0 |    0 |  1,498 |    3,806 |     5.0 |
| joblib             | certain            |   525 |     525 |        |       |      0 |    0 |    526 |    2,241 |     3.3 |
| joblib             | likely             |   702 |     526 |    176 |       |      0 |    0 |    703 |    2,241 |     3.4 |
| joblib             | unsafe             |   770 |     525 |    176 |    69 |      0 |    0 |    771 |    2,241 |     2.5 |
| joblib             | infer-basedpyright |   898 |     525 |    184 |   189 |      0 |    0 |    899 |    2,241 |     7.1 |
| joblib             | infer-ty           |   841 |     525 |    182 |   134 |      0 |    0 |    842 |    2,241 |     9.2 |
| joblib             | infer-pyrefly      |   891 |     523 |    184 |   184 |      0 |    0 |    892 |    2,241 |     3.7 |
| joblib             | infer-trace        |   831 |     525 |    177 |   129 |      0 |    0 |    832 |    2,241 |     1.5 |

Each fix's 12 sets of mechanisms that made the most fixes, the corpora together, by tier (a guess is
likely by its whole set: every set is in `tables/mechanisms.csv`):

| fix                | mechanisms        |  fixed | certain | likely |  guess |
| ------------------ | ----------------- | -----: | ------: | -----: | -----: |
| certain            | literal           |  7,260 |   7,260 |        |        |
| certain            | call              |  4,428 |   4,428 |        |        |
| certain            | container+literal |  2,980 |   2,980 |        |        |
| certain            | stdlib            |  2,924 |   2,924 |        |        |
| certain            | method            |  2,235 |   2,235 |        |        |
| certain            | copy+loop         |  2,052 |   2,052 |        |        |
| certain            | builtin           |  1,886 |   1,886 |        |        |
| certain            | loop              |  1,500 |   1,500 |        |        |
| certain            | call+unpack       |  1,215 |   1,215 |        |        |
| certain            | attribute+loop    |  1,031 |   1,031 |        |        |
| certain            | literal+method    |    685 |     685 |        |        |
| certain            | method+unpack     |    674 |     674 |        |        |
| likely             | constructor       |  9,048 |      22 |  9,026 |        |
| likely             | literal           |  7,267 |   7,267 |        |        |
| likely             | call              |  4,471 |   4,429 |     42 |        |
| likely             | container+literal |  2,980 |   2,980 |        |        |
| likely             | stdlib            |  2,932 |   2,932 |        |        |
| likely             | method            |  2,653 |   2,244 |    409 |        |
| likely             | copy+loop         |  2,279 |   2,070 |    209 |        |
| likely             | builtin           |  1,887 |   1,887 |        |        |
| likely             | loop              |  1,500 |   1,500 |        |        |
| likely             | call+unpack       |  1,215 |   1,215 |        |        |
| likely             | attribute+loop    |  1,070 |   1,036 |     34 |        |
| likely             | copy+unpack       |    815 |     664 |    151 |        |
| unsafe             | constructor       |  9,046 |      22 |  9,024 |        |
| unsafe             | literal           |  7,260 |   7,258 |        |      2 |
| unsafe             | call              |  4,470 |   4,428 |     42 |        |
| unsafe             | stdlib            |  3,071 |   2,924 |        |    147 |
| unsafe             | container+literal |  2,980 |   2,980 |        |        |
| unsafe             | method            |  2,644 |   2,235 |    409 |        |
| unsafe             | copy+loop         |  2,260 |   2,052 |    208 |        |
| unsafe             | builtin           |  1,888 |   1,886 |        |      2 |
| unsafe             | loop              |  1,500 |   1,500 |        |        |
| unsafe             | literal+member    |  1,368 |         |        |  1,368 |
| unsafe             | call+unpack       |  1,215 |   1,215 |        |        |
| unsafe             | attribute+loop    |  1,065 |   1,031 |     34 |        |
| infer-basedpyright | checker           | 12,696 |         |        | 12,696 |
| infer-basedpyright | constructor       |  9,026 |      22 |  9,004 |        |
| infer-basedpyright | literal           |  7,264 |   7,262 |        |      2 |
| infer-basedpyright | call              |  4,516 |   4,418 |     98 |        |
| infer-basedpyright | stdlib            |  3,071 |   2,911 |        |    160 |
| infer-basedpyright | container+literal |  2,980 |   2,980 |        |        |
| infer-basedpyright | method            |  2,748 |   2,205 |    543 |        |
| infer-basedpyright | copy+loop         |  2,567 |   2,052 |    515 |        |
| infer-basedpyright | builtin           |  1,888 |   1,886 |        |      2 |
| infer-basedpyright | loop              |  1,500 |   1,500 |        |        |
| infer-basedpyright | literal+member    |  1,368 |         |        |  1,368 |
| infer-basedpyright | call+unpack       |  1,217 |   1,215 |        |      2 |
| infer-ty           | checker           | 11,966 |         |        | 11,966 |
| infer-ty           | constructor       |  9,025 |      22 |  9,003 |        |
| infer-ty           | literal           |  7,264 |   7,262 |        |      2 |
| infer-ty           | call              |  4,485 |   4,419 |     66 |        |
| infer-ty           | stdlib            |  3,062 |   2,914 |        |    148 |
| infer-ty           | container+literal |  2,980 |   2,980 |        |        |
| infer-ty           | method            |  2,751 |   2,206 |    545 |        |
| infer-ty           | copy+loop         |  2,591 |   2,052 |    539 |        |
| infer-ty           | builtin           |  1,888 |   1,886 |        |      2 |
| infer-ty           | loop              |  1,500 |   1,500 |        |        |
| infer-ty           | literal+member    |  1,368 |         |        |  1,368 |
| infer-ty           | call+unpack       |  1,215 |   1,215 |        |        |
| infer-pyrefly      | checker           | 14,208 |         |        | 14,208 |
| infer-pyrefly      | constructor       |  9,025 |      22 |  9,003 |        |
| infer-pyrefly      | literal           |  7,265 |   7,263 |        |      2 |
| infer-pyrefly      | call              |  4,494 |   4,419 |     75 |        |
| infer-pyrefly      | stdlib            |  3,074 |   2,913 |        |    161 |
| infer-pyrefly      | container+literal |  2,980 |   2,980 |        |        |
| infer-pyrefly      | method            |  2,757 |   2,206 |    551 |        |
| infer-pyrefly      | copy+loop         |  2,627 |   2,052 |    575 |        |
| infer-pyrefly      | builtin           |  1,888 |   1,886 |        |      2 |
| infer-pyrefly      | loop              |  1,500 |   1,500 |        |        |
| infer-pyrefly      | literal+member    |  1,368 |         |        |  1,368 |
| infer-pyrefly      | call+unpack       |  1,215 |   1,215 |        |        |
| infer-trace        | constructor       |  8,845 |      22 |  8,823 |        |
| infer-trace        | literal           |  7,002 |   7,000 |        |      2 |
| infer-trace        | call              |  4,342 |   4,306 |     36 |        |
| infer-trace        | stdlib            |  2,914 |   2,761 |        |    153 |
| infer-trace        | container+literal |  2,836 |   2,836 |        |        |
| infer-trace        | method            |  2,482 |   2,059 |    423 |        |
| infer-trace        | copy+loop         |  2,129 |   1,916 |    213 |        |
| infer-trace        | builtin           |  1,781 |   1,779 |        |      2 |
| infer-trace        | traced            |  1,463 |         |        |  1,463 |
| infer-trace        | loop              |  1,437 |   1,437 |        |        |
| infer-trace        | call+unpack       |  1,184 |   1,184 |        |        |
| infer-trace        | attribute+loop    |    983 |     949 |     34 |        |

The untyped bindings: with only a guess, with no fix, and in files that don't parse:

| corpus             | untyped | guessed | unfixed | unparsed |
| ------------------ | ------: | ------: | ------: | -------: |
| black              |   1,273 |     163 |     398 |        0 |
| pdm                |   2,718 |     311 |   1,255 |        0 |
| tox                |   1,762 |     134 |     686 |        0 |
| sphinx             |   7,972 |     816 |   4,021 |        0 |
| mkdocs             |   2,332 |     472 |   1,049 |        0 |
| streamlink         |   3,029 |     232 |   2,123 |        0 |
| mypy               |  11,401 |   1,561 |   5,103 |        0 |
| httpx              |     569 |      73 |     261 |        0 |
| starlette          |     744 |      97 |     336 |        0 |
| uvicorn            |     489 |      43 |     215 |        0 |
| anyio              |     715 |      59 |     451 |        0 |
| websockets         |     791 |     102 |     363 |        0 |
| hypercorn          |     355 |      57 |     163 |        0 |
| aiohttp            |   1,857 |     255 |     924 |        0 |
| fastapi            |     742 |      67 |     418 |        0 |
| textual            |   6,483 |     727 |   3,189 |        0 |
| mcp                |   1,720 |     235 |     794 |        0 |
| pytest             |   3,003 |     285 |   1,374 |        0 |
| attrs              |     393 |      11 |     288 |        0 |
| werkzeug           |   1,293 |     126 |     637 |        0 |
| cattrs             |     520 |      38 |     378 |        0 |
| structlog          |     316 |      26 |     192 |        0 |
| xarray             |  21,344 |   3,346 |  14,454 |        0 |
| networkx           |  22,456 |   2,466 |  16,051 |        0 |
| pint               |   3,078 |     160 |   2,357 |        0 |
| dask               |  24,172 |   2,519 |  18,541 |        0 |
| zarr               |   2,411 |     113 |   1,229 |        0 |
| nibabel            |   8,468 |     933 |   5,685 |        0 |
| seaborn            |   2,895 |     229 |   2,027 |        0 |
| optuna             |   3,598 |     306 |   1,819 |        0 |
| altair             |   1,700 |      62 |   1,265 |        0 |
| stripe             |   3,357 |     663 |   2,129 |        0 |
| strawberry-graphql |   1,806 |     213 |     998 |        0 |
| litestar           |   1,905 |     165 |   1,145 |        0 |
| narwhals           |   3,120 |     123 |   2,024 |        0 |
| click              |     608 |      67 |     256 |        0 |
| pygments           |   7,666 |     224 |   6,706 |        0 |
| celery             |   3,748 |     355 |   2,890 |        0 |
| botocore           |   3,786 |     585 |   2,654 |        0 |
| joblib             |   2,239 |     245 |   1,469 |        0 |

A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and the
billions of instructions they took, where `hyperfine` counted them:

| corpus             | jobs | one process | with jobs | runs | G instructions, one process | with jobs |  timed by |
| ------------------ | ---: | ----------: | --------: | ---: | --------------------------: | --------: | --------: |
| black              |    4 |        0.47 |      0.28 |    1 |                         6.5 |       7.7 | hyperfine |
| pdm                |    4 |        1.33 |      0.74 |    1 |                        18.6 |      21.5 | hyperfine |
| tox                |    4 |        0.94 |      0.43 |    1 |                        12.5 |      13.5 | hyperfine |
| sphinx             |    4 |        3.46 |      1.26 |    1 |                        53.1 |      54.7 | hyperfine |
| mkdocs             |    4 |        0.76 |      0.48 |    1 |                        10.7 |      12.6 | hyperfine |
| streamlink         |    4 |        1.88 |       0.8 |    1 |                        27.7 |      30.0 | hyperfine |
| mypy               |    4 |        5.07 |      1.75 |    1 |                        79.8 |      82.2 | hyperfine |
| httpx              |    4 |        0.31 |      0.25 |    1 |                         4.1 |       5.2 | hyperfine |
| starlette          |    4 |        0.37 |      0.29 |    1 |                         4.8 |       6.1 | hyperfine |
| uvicorn            |    4 |        0.38 |      0.27 |    1 |                         5.0 |       6.2 | hyperfine |
| anyio              |    4 |        0.57 |      0.39 |    1 |                         8.0 |       9.2 | hyperfine |
| websockets         |    4 |        0.55 |      0.31 |    1 |                         7.2 |       8.7 | hyperfine |
| hypercorn          |    4 |        0.29 |      0.23 |    1 |                         3.8 |       5.0 | hyperfine |
| aiohttp            |    4 |        1.07 |      0.54 |    1 |                        15.3 |      16.7 | hyperfine |
| fastapi            |    4 |        0.53 |      0.47 |    1 |                         7.8 |       9.3 | hyperfine |
| textual            |    4 |        2.35 |      1.07 |    1 |                        34.7 |      38.0 | hyperfine |
| mcp                |    4 |        0.95 |      0.51 |    1 |                        13.3 |      15.3 | hyperfine |
| pytest             |    4 |        1.29 |      0.75 |    1 |                        18.7 |      20.5 | hyperfine |
| attrs              |    4 |         0.2 |      0.26 |    1 |                         2.6 |       3.6 | hyperfine |
| werkzeug           |    4 |        0.67 |      0.36 |    1 |                         8.8 |      10.1 | hyperfine |
| cattrs             |    4 |        0.31 |       0.3 |    1 |                         4.2 |       5.5 | hyperfine |
| structlog          |    4 |        0.23 |      0.22 |    1 |                         2.8 |       3.9 | hyperfine |
| xarray             |    4 |       14.97 |      7.72 |    1 |                       266.0 |     281.5 | hyperfine |
| networkx           |    4 |        7.89 |      3.14 |    1 |                       132.5 |     137.2 | hyperfine |
| pint               |    4 |        1.36 |      0.89 |    1 |                        20.7 |      24.5 | hyperfine |
| dask               |    4 |       19.19 |      9.35 |    1 |                       393.0 |     415.0 | hyperfine |
| zarr               |    4 |        1.39 |      0.66 |    1 |                        20.9 |      23.9 | hyperfine |
| nibabel            |    4 |         3.9 |      2.04 |    1 |                        63.7 |      73.9 | hyperfine |
| seaborn            |    4 |        1.87 |      1.21 |    1 |                        32.6 |      39.4 | hyperfine |
| optuna             |    4 |        3.15 |      1.75 |    1 |                        50.0 |      55.7 | hyperfine |
| altair             |    4 |        1.65 |      1.39 |    1 |                        28.4 |      34.0 | hyperfine |
| stripe             |    4 |        7.12 |      2.73 |    1 |                       123.9 |     130.3 | hyperfine |
| strawberry-graphql |    4 |        1.42 |      0.67 |    1 |                        19.4 |      22.7 | hyperfine |
| litestar           |    4 |        1.87 |      0.91 |    1 |                        25.4 |      29.0 | hyperfine |
| narwhals           |    4 |        2.02 |      0.93 |    1 |                        30.8 |      35.8 | hyperfine |
| click              |    4 |        0.36 |       0.3 |    1 |                         5.0 |       6.0 | hyperfine |
| pygments           |    4 |         2.5 |      1.02 |    1 |                        45.1 |      47.8 | hyperfine |
| celery             |    4 |        2.15 |       1.4 |    1 |                        31.7 |      37.7 | hyperfine |
| botocore           |    4 |        1.81 |      0.85 |    1 |                        29.2 |      31.0 | hyperfine |
| joblib             |    4 |        1.04 |      0.75 |    1 |                        15.2 |      18.3 | hyperfine |

The fixes a traced test could tell of, those whose every value fit, and those one didn't; and the
traced tests' seconds, beside the released tests' untraced:

| corpus             | tier    |  told |  held | differed | resting on the trace |                                                                            tests | seconds | untraced |
| ------------------ | ------- | ----: | ----: | -------: | -------------------: | -------------------------------------------------------------------------------: | ------: | -------: |
| black              |         |       |       |          |                    0 |                                         519 passed, 1 skipped, 9 subtests passed |     8.4 |      9.1 |
| black              | certain |   604 |   603 |        1 |                      |                                                                                  |         |          |
| black              | likely  |   100 |   100 |        0 |                      |                                                                                  |         |          |
| black              | guess   |    40 |    40 |        0 |                      |                                                                                  |         |          |
| pdm                |         |       |       |          |                    0 |                                              1472 passed, 1 skipped, 60 warnings |    13.9 |     12.0 |
| pdm                | certain |   887 |   876 |       11 |                      |                                                                                  |         |          |
| pdm                | likely  |   133 |   133 |        0 |                      |                                                                                  |         |          |
| pdm                | guess   |    75 |    74 |        1 |                      |                                                                                  |         |          |
| tox                |         |       |       |          |                    0 |                                                1 failed, 8547 passed, 31 skipped |    51.2 |     38.3 |
| tox                | certain |   718 |   714 |        4 |                      |                                                                                  |         |          |
| tox                | likely  |    56 |    56 |        0 |                      |                                                                                  |         |          |
| tox                | guess   |    29 |    29 |        0 |                      |                                                                                  |         |          |
| sphinx             |         |       |       |          |                    0 |                                  10 failed, 2392 passed, 22 skipped, 35 warnings |    20.6 |     12.2 |
| sphinx             | certain | 2,010 | 1,984 |       26 |                      |                                                                                  |         |          |
| sphinx             | likely  |   340 |   339 |        1 |                      |                                                                                  |         |          |
| sphinx             | guess   |   192 |   190 |        2 |                      |                                                                                  |         |          |
| mkdocs             |         |       |       |          |                   12 |                          Ran 724 tests: FAILED (failures=2, errors=2, skipped=4) |    10.1 |      9.3 |
| mkdocs             | certain |   629 |   628 |        1 |                      |                                                                                  |         |          |
| mkdocs             | likely  |   324 |   324 |        0 |                      |                                                                                  |         |          |
| mkdocs             | guess   |   107 |   107 |        0 |                      |                                                                                  |         |          |
| streamlink         |         |       |       |          |                    8 |                                                          7248 passed, 36 skipped |    14.0 |     12.6 |
| streamlink         | certain |   267 |   266 |        1 |                      |                                                                                  |         |          |
| streamlink         | likely  |    38 |    38 |        0 |                      |                                                                                  |         |          |
| streamlink         | guess   |    36 |    36 |        0 |                      |                                                                                  |         |          |
| mypy               |         |       |       |          |                    0 |                        14464 passed, 366 skipped, 12 xfailed, 46 subtests passed |   304.0 |    415.8 |
| mypy               | certain | 3,692 | 3,692 |        0 |                      |                                                                                  |         |          |
| mypy               | likely  |   899 |   899 |        0 |                      |                                                                                  |         |          |
| mypy               | guess   |   290 |   290 |        0 |                      |                                                                                  |         |          |
| httpx              |         |       |       |          |                    0 |                                                 1 failed, 1416 passed, 1 skipped |     6.5 |      4.8 |
| httpx              | certain |   182 |   182 |        0 |                      |                                                                                  |         |          |
| httpx              | likely  |    41 |    41 |        0 |                      |                                                                                  |         |          |
| httpx              | guess   |    16 |    16 |        0 |                      |                                                                                  |         |          |
| starlette          |         |       |       |          |                    0 |                                                1271 passed, 2 skipped, 2 xfailed |     9.7 |      6.2 |
| starlette          | certain |   190 |   190 |        0 |                      |                                                                                  |         |          |
| starlette          | likely  |    46 |    46 |        0 |                      |                                                                                  |         |          |
| starlette          | guess   |    30 |    30 |        0 |                      |                                                                                  |         |          |
| uvicorn            |         |       |       |          |                    0 |                                                          1350 passed, 12 skipped |    29.1 |     27.2 |
| uvicorn            | certain |   169 |   165 |        4 |                      |                                                                                  |         |          |
| uvicorn            | likely  |    27 |    27 |        0 |                      |                                                                                  |         |          |
| uvicorn            | guess   |     7 |     7 |        0 |                      |                                                                                  |         |          |
| anyio              |         |       |       |          |                    0 |                               3824 passed, 19 skipped, 388 deselected, 5 xfailed |   120.3 |    112.2 |
| anyio              | certain |   150 |   149 |        1 |                      |                                                                                  |         |          |
| anyio              | likely  |    24 |    24 |        0 |                      |                                                                                  |         |          |
| anyio              | guess   |    22 |    21 |        1 |                      |                                                                                  |         |          |
| websockets         |         |       |       |          |                    0 |                                                   Ran 2589 tests: OK (skipped=8) |    94.4 |     93.7 |
| websockets         | certain |   236 |   234 |        2 |                      |                                                                                  |         |          |
| websockets         | likely  |    50 |    50 |        0 |                      |                                                                                  |         |          |
| websockets         | guess   |    30 |    30 |        0 |                      |                                                                                  |         |          |
| hypercorn          |         |       |       |          |                    0 |                                                             2 failed, 194 passed |     6.8 |      6.3 |
| hypercorn          | certain |    64 |    64 |        0 |                      |                                                                                  |         |          |
| hypercorn          | likely  |    12 |    12 |        0 |                      |                                                                                  |         |          |
| hypercorn          | guess   |     9 |     9 |        0 |                      |                                                                                  |         |          |
| aiohttp            |         |       |       |          |                    1 |                           4843 passed, 535 skipped, 2 xfailed, 4 subtests passed |    96.5 |     72.5 |
| aiohttp            | certain |   509 |   488 |       21 |                      |                                                                                  |         |          |
| aiohttp            | likely  |   117 |   115 |        2 |                      |                                                                                  |         |          |
| aiohttp            | guess   |    82 |    77 |        5 |                      |                                                                                  |         |          |
| fastapi            |         |       |       |          |                    0 |                                               3551 passed, 17 skipped, 4 xfailed |    18.5 |     18.6 |
| fastapi            | certain |   221 |   221 |        0 |                      |                                                                                  |         |          |
| fastapi            | likely  |    28 |    28 |        0 |                      |                                                                                  |         |          |
| fastapi            | guess   |    24 |    24 |        0 |                      |                                                                                  |         |          |
| mcp                |         |       |       |          |                    0 |                                                6095 passed, 8 skipped, 1 xfailed |    16.3 |     11.5 |
| mcp                | certain |   505 |   504 |        1 |                      |                                                                                  |         |          |
| mcp                | likely  |   129 |   128 |        1 |                      |                                                                                  |         |          |
| mcp                | guess   |    53 |    53 |        0 |                      |                                                                                  |         |          |
| pytest             |         |       |       |          |                   15 |                         4105 passed, 110 skipped, 14 xfailed, 1 xpassed, 1 error |    49.8 |     25.3 |
| pytest             | certain | 1,087 | 1,074 |       13 |                      |                                                                                  |         |          |
| pytest             | likely  |   129 |   128 |        1 |                      |                                                                                  |         |          |
| pytest             | guess   |   104 |   104 |        0 |                      |                                                                                  |         |          |
| attrs              |         |       |       |          |                    2 |                                      1 failed, 1382 passed, 2 skipped, 2 xfailed |     4.5 |      3.1 |
| attrs              | certain |    73 |    73 |        0 |                      |                                                                                  |         |          |
| attrs              | likely  |     8 |     8 |        0 |                      |                                                                                  |         |          |
| attrs              | guess   |     1 |     1 |        0 |                      |                                                                                  |         |          |
| werkzeug           |         |       |       |          |                    0 |                                                 980 passed, 1 skipped, 1 warning |     9.0 |      7.0 |
| werkzeug           | certain |   356 |   351 |        5 |                      |                                                                                  |         |          |
| werkzeug           | likely  |    43 |    43 |        0 |                      |                                                                                  |         |          |
| werkzeug           | guess   |    34 |    34 |        0 |                      |                                                                                  |         |          |
| cattrs             |         |       |       |          |                    0 |                                                           994 passed, 15 xfailed |    19.9 |     19.9 |
| cattrs             | certain |   100 |    98 |        2 |                      |                                                                                  |         |          |
| cattrs             | likely  |    24 |    24 |        0 |                      |                                                                                  |         |          |
| cattrs             | guess   |    12 |    12 |        0 |                      |                                                                                  |         |          |
| structlog          |         |       |       |          |                    0 |                                     1 failed, 883 passed, 37 skipped, 2 warnings |     3.0 |      1.0 |
| structlog          | certain |    62 |    62 |        0 |                      |                                                                                  |         |          |
| structlog          | likely  |     6 |     6 |        0 |                      |                                                                                  |         |          |
| structlog          | guess   |     5 |     5 |        0 |                      |                                                                                  |         |          |
| xarray             |         |       |       |          |                   35 |  2 failed, 6334 passed, 9626 skipped, 11 xfailed, 4 xpassed, 1 warning, 3 errors |    25.3 |     14.1 |
| xarray             | certain | 1,757 | 1,749 |        8 |                      |                                                                                  |         |          |
| xarray             | likely  | 1,745 | 1,742 |        3 |                      |                                                                                  |         |          |
| xarray             | guess   |   111 |   111 |        0 |                      |                                                                                  |         |          |
| networkx           |         |       |       |          |                  433 |                                            10083 passed, 62 skipped, 741 xfailed |    32.3 |     19.6 |
| networkx           | certain | 3,649 | 3,648 |        1 |                      |                                                                                  |         |          |
| networkx           | likely  | 2,010 | 1,994 |       16 |                      |                                                                                  |         |          |
| networkx           | guess   |   310 |   306 |        4 |                      |                                                                                  |         |          |
| pint               |         |       |       |          |                   35 | 1 failed, 2289 passed, 590 skipped, 11 xfailed, 14 warnings, 298 subtests passed |    36.7 |     28.3 |
| pint               | certain |   319 |   311 |        8 |                      |                                                                                  |         |          |
| pint               | likely  |    63 |    63 |        0 |                      |                                                                                  |         |          |
| pint               | guess   |    37 |    34 |        3 |                      |                                                                                  |         |          |
| dask               |         |       |       |          |                  338 |         1 failed, 16200 passed, 1089 skipped, 513 xfailed, 2 xpassed, 6 warnings |   204.7 |    153.3 |
| dask               | certain | 2,354 | 2,347 |        7 |                      |                                                                                  |         |          |
| dask               | likely  | 1,518 | 1,516 |        2 |                      |                                                                                  |         |          |
| dask               | guess   |   214 |   207 |        7 |                      |                                                                                  |         |          |
| zarr               |         |       |       |          |                    0 |                                             8422 passed, 1205 skipped, 4 xfailed |   103.0 |    108.2 |
| zarr               | certain |   726 |   714 |       12 |                      |                                                                                  |         |          |
| zarr               | likely  |    47 |    47 |        0 |                      |                                                                                  |         |          |
| zarr               | guess   |    24 |    23 |        1 |                      |                                                                                  |         |          |
| nibabel            |         |       |       |          |                   83 |                      111 failed, 5166 passed, 304 skipped, 40 xfailed, 19 errors |    19.7 |     14.5 |
| nibabel            | certain | 1,238 | 1,235 |        3 |                      |                                                                                  |         |          |
| nibabel            | likely  |   546 |   544 |        2 |                      |                                                                                  |         |          |
| nibabel            | guess   |   150 |   150 |        0 |                      |                                                                                  |         |          |
| seaborn            |         |       |       |          |                   31 |            20 failed, 2178 passed, 11 skipped, 6 xfailed, 958 warnings, 8 errors |    64.5 |     55.3 |
| seaborn            | certain |   485 |   483 |        2 |                      |                                                                                  |         |          |
| seaborn            | likely  |   115 |   113 |        2 |                      |                                                                                  |         |          |
| seaborn            | guess   |    53 |    50 |        3 |                      |                                                                                  |         |          |
| optuna             |         |       |       |          |                    0 |                     263 failed, 4203 passed, 43 skipped, 326 warnings, 16 errors |   445.6 |    237.0 |
| optuna             | certain |   837 |   836 |        1 |                      |                                                                                  |         |          |
| optuna             | likely  |   121 |   121 |        0 |                      |                                                                                  |         |          |
| optuna             | guess   |    47 |    47 |        0 |                      |                                                                                  |         |          |
| altair             |         |       |       |          |                    6 |            28 failed, 1866 passed, 12 skipped, 6 xfailed, 4 xpassed, 93 warnings |    42.8 |     22.4 |
| altair             | certain |   199 |   198 |        1 |                      |                                                                                  |         |          |
| altair             | likely  |    33 |    33 |        0 |                      |                                                                                  |         |          |
| altair             | guess   |     7 |     6 |        1 |                      |                                                                                  |         |          |
| strawberry-graphql |         |       |       |          |                    0 |          51 failed, 2521 passed, 3293 skipped, 7 xfailed, 35 warnings, 25 errors |    22.2 |     14.6 |
| strawberry-graphql | certain |   376 |   368 |        8 |                      |                                                                                  |         |          |
| strawberry-graphql | likely  |    93 |    91 |        2 |                      |                                                                                  |         |          |
| strawberry-graphql | guess   |    27 |    27 |        0 |                      |                                                                                  |         |          |
| litestar           |         |       |       |          |                    0 |           5 failed, 5646 passed, 256 skipped, 13 xfailed, 30 xpassed, 2 warnings |    39.1 |     29.8 |
| litestar           | certain |   450 |   449 |        1 |                      |                                                                                  |         |          |
| litestar           | likely  |    87 |    87 |        0 |                      |                                                                                  |         |          |
| litestar           | guess   |    42 |    41 |        1 |                      |                                                                                  |         |          |
| narwhals           |         |       |       |          |                    0 |                                           12078 passed, 235 skipped, 709 xfailed |    16.2 |     34.3 |
| narwhals           | certain |   558 |   556 |        2 |                      |                                                                                  |         |          |
| narwhals           | likely  |    46 |    46 |        0 |                      |                                                                                  |         |          |
| narwhals           | guess   |    29 |    29 |        0 |                      |                                                                                  |         |          |
| click              |         |       |       |          |                    0 |                             1991 passed, 24 skipped, 31000 deselected, 1 xfailed |     4.4 |      4.5 |
| click              | certain |   208 |   207 |        1 |                      |                                                                                  |         |          |
| click              | likely  |    20 |    19 |        1 |                      |                                                                                  |         |          |
| click              | guess   |    28 |    27 |        1 |                      |                                                                                  |         |          |
| pygments           |         |       |       |          |                   87 |                                                1 failed, 5330 passed, 15 skipped |    14.1 |     14.5 |
| pygments           | certain |   291 |   291 |        0 |                      |                                                                                  |         |          |
| pygments           | likely  |    59 |    59 |        0 |                      |                                                                                  |         |          |
| pygments           | guess   |    56 |    56 |        0 |                      |                                                                                  |         |          |
| celery             |         |       |       |          |                   64 |                                     3 failed, 3521 passed, 36 skipped, 3 xfailed |   129.0 |    150.1 |
| celery             | certain |   219 |   214 |        5 |                      |                                                                                  |         |          |
| celery             | likely  |    35 |    35 |        0 |                      |                                                                                  |         |          |
| celery             | guess   |    30 |    27 |        3 |                      |                                                                                  |         |          |
| botocore           |         |       |       |          |                  300 |                                                          4600 passed, 96 skipped |    29.9 |     32.6 |
| botocore           | certain |   328 |   327 |        1 |                      |                                                                                  |         |          |
| botocore           | likely  |   130 |   130 |        0 |                      |                                                                                  |         |          |
| botocore           | guess   |    93 |    92 |        1 |                      |                                                                                  |         |          |
| joblib             |         |       |       |          |                   59 |                        7 failed, 1485 passed, 45 skipped, 4 xpassed, 85 warnings |   158.9 |    161.2 |
| joblib             | certain |   357 |   357 |        0 |                      |                                                                                  |         |          |
| joblib             | likely  |   130 |   129 |        1 |                      |                                                                                  |         |          |
| joblib             | guess   |    38 |    38 |        0 |                      |                                                                                  |         |          |

Each package's own tests, as released and after each fix: the failures every fixed run has and no
released run, those gone, and the differences in tests its catalog entry names:

| corpus             | run                | same as released | summary                                                               | new failures | gone | named |
| ------------------ | ------------------ | ---------------- | --------------------------------------------------------------------- | -----------: | ---: | ----: |
| black              | released           |                  | 519 passed, 1 skipped                                                 |              |      |       |
| black              | fix-certain        | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | fix-likely         | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | fix-unsafe         | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-basedpyright | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-pyrefly      | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-trace        | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| black              | infer-ty           | True             | 1 failed, 518 passed, 1 skipped                                       |            0 |    0 |     1 |
| pdm                | released           |                  | 1,472 passed, 1 skipped                                               |              |      |       |
| pdm                | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pdm                | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pdm                | fix-unsafe         | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-basedpyright | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-pyrefly      | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-trace        | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| pdm                | infer-ty           | True             | 1,472 passed, 1 skipped                                               |            0 |    0 |     0 |
| tox                | released           |                  | 1 failed, 8,547 passed, 31 skipped                                    |              |      |       |
| tox                | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| tox                | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| tox                | fix-unsafe         | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-basedpyright | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-pyrefly      | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-trace        | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| tox                | infer-ty           | True             | 1 failed, 8,547 passed, 31 skipped                                    |            0 |    0 |     0 |
| sphinx             | released           |                  | 9 failed, 2,393 passed, 22 skipped                                    |              |      |       |
| sphinx             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| sphinx             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| sphinx             | fix-unsafe         | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-basedpyright | True             | 10 failed, 2,392 passed, 22 skipped                                   |            0 |    0 |     0 |
| sphinx             | infer-pyrefly      | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-trace        | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| sphinx             | infer-ty           | True             | 9 failed, 2,393 passed, 22 skipped                                    |            0 |    0 |     0 |
| mkdocs             | released           |                  | 2 errors, 2 failures, 724 ran, 4 skipped                              |              |      |       |
| mkdocs             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mkdocs             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mkdocs             | fix-unsafe         | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-basedpyright | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-pyrefly      | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-trace        | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| mkdocs             | infer-ty           | True             | 2 errors, 2 failures, 724 ran, 4 skipped                              |            0 |    0 |     0 |
| streamlink         | released           |                  | 7,248 passed, 36 skipped                                              |              |      |       |
| streamlink         | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| streamlink         | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| streamlink         | fix-unsafe         | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-basedpyright | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-pyrefly      | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-trace        | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| streamlink         | infer-ty           | True             | 7,248 passed, 36 skipped                                              |            0 |    0 |     0 |
| mypy               | released           |                  | 14,464 passed, 366 skipped, 12 xfailed                                |              |      |       |
| mypy               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mypy               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mypy               | fix-unsafe         | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-basedpyright | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-pyrefly      | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-trace        | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| mypy               | infer-ty           | True             | 14,464 passed, 366 skipped, 12 xfailed                                |            0 |    0 |     0 |
| httpx              | released           |                  | 1 failed, 1,416 passed, 1 skipped                                     |              |      |       |
| httpx              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| httpx              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| httpx              | fix-unsafe         | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-basedpyright | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-pyrefly      | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-trace        | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| httpx              | infer-ty           | True             | 1 failed, 1,416 passed, 1 skipped                                     |            0 |    0 |     0 |
| starlette          | released           |                  | 1,271 passed, 2 skipped, 2 xfailed                                    |              |      |       |
| starlette          | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| starlette          | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| starlette          | fix-unsafe         | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-basedpyright | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-pyrefly      | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-trace        | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| starlette          | infer-ty           | True             | 1,271 passed, 2 skipped, 2 xfailed                                    |            0 |    0 |     0 |
| uvicorn            | released           |                  | 1,350 passed, 12 skipped                                              |              |      |       |
| uvicorn            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| uvicorn            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| uvicorn            | fix-unsafe         | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-basedpyright | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-pyrefly      | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-trace        | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| uvicorn            | infer-ty           | True             | 1,350 passed, 12 skipped                                              |            0 |    0 |     0 |
| anyio              | released           |                  | 3,824 passed, 19 skipped, 5 xfailed                                   |              |      |       |
| anyio              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| anyio              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| anyio              | fix-unsafe         | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-basedpyright | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-pyrefly      | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-trace        | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| anyio              | infer-ty           | True             | 3,824 passed, 19 skipped, 5 xfailed                                   |            0 |    0 |     0 |
| websockets         | released           |                  | 2,589 ran, 8 skipped                                                  |              |      |       |
| websockets         | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| websockets         | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| websockets         | fix-unsafe         | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-basedpyright | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-pyrefly      | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-trace        | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| websockets         | infer-ty           | True             | 2,589 ran, 8 skipped                                                  |            0 |    0 |     0 |
| hypercorn          | released           |                  | 2 failed, 194 passed                                                  |              |      |       |
| hypercorn          | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| hypercorn          | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| hypercorn          | fix-unsafe         | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-basedpyright | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-pyrefly      | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-trace        | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| hypercorn          | infer-ty           | True             | 2 failed, 194 passed                                                  |            0 |    0 |     0 |
| aiohttp            | released           |                  | 4,843 passed, 535 skipped, 2 xfailed                                  |              |      |       |
| aiohttp            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| aiohttp            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| aiohttp            | fix-unsafe         | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-basedpyright | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-pyrefly      | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-trace        | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| aiohttp            | infer-ty           | True             | 4,843 passed, 535 skipped, 2 xfailed                                  |            0 |    0 |     0 |
| fastapi            | released           |                  | 3,551 passed, 17 skipped, 4 xfailed                                   |              |      |       |
| fastapi            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| fastapi            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| fastapi            | fix-unsafe         | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-basedpyright | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-pyrefly      | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-trace        | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| fastapi            | infer-ty           | True             | 3,551 passed, 17 skipped, 4 xfailed                                   |            0 |    0 |     0 |
| mcp                | released           |                  | 6,095 passed, 8 skipped, 1 xfailed                                    |              |      |       |
| mcp                | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mcp                | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| mcp                | fix-unsafe         | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-basedpyright | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-pyrefly      | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-trace        | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| mcp                | infer-ty           | True             | 6,095 passed, 8 skipped, 1 xfailed                                    |            0 |    0 |     0 |
| pytest             | released           |                  | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |              |      |       |
| pytest             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pytest             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pytest             | fix-unsafe         | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-basedpyright | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-pyrefly      | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-trace        | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| pytest             | infer-ty           | True             | 1 error, 4,105 passed, 110 skipped, 14 xfailed, 1 xpassed             |            0 |    0 |     0 |
| attrs              | released           |                  | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |              |      |       |
| attrs              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| attrs              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| attrs              | fix-unsafe         | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-basedpyright | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-pyrefly      | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-trace        | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| attrs              | infer-ty           | True             | 1 failed, 1,382 passed, 2 skipped, 2 xfailed                          |            0 |    0 |     0 |
| werkzeug           | released           |                  | 980 passed, 1 skipped                                                 |              |      |       |
| werkzeug           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| werkzeug           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| werkzeug           | fix-unsafe         | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-basedpyright | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-pyrefly      | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-trace        | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| werkzeug           | infer-ty           | True             | 980 passed, 1 skipped                                                 |            0 |    0 |     0 |
| cattrs             | released           |                  | 994 passed, 15 xfailed                                                |              |      |       |
| cattrs             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| cattrs             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| cattrs             | fix-unsafe         | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-basedpyright | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-pyrefly      | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-trace        | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| cattrs             | infer-ty           | True             | 994 passed, 15 xfailed                                                |            0 |    0 |     0 |
| structlog          | released           |                  | 884 passed, 37 skipped                                                |              |      |       |
| structlog          | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| structlog          | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| structlog          | fix-unsafe         | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-basedpyright | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-pyrefly      | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-trace        | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| structlog          | infer-ty           | True             | 884 passed, 37 skipped                                                |            0 |    0 |     0 |
| xarray             | released           |                  | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |              |      |       |
| xarray             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| xarray             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| xarray             | fix-unsafe         | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-basedpyright | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-pyrefly      | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-trace        | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| xarray             | infer-ty           | True             | 3 error, 2 failed, 6,334 passed, 9,626 skipped, 11 xfailed, 4 xpassed |            0 |    0 |     0 |
| networkx           | released           |                  | 10,083 passed, 62 skipped, 741 xfailed                                |              |      |       |
| networkx           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| networkx           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| networkx           | fix-unsafe         | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-basedpyright | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-pyrefly      | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-trace        | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| networkx           | infer-ty           | True             | 10,083 passed, 62 skipped, 741 xfailed                                |            0 |    0 |     0 |
| pint               | released           |                  | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |              |      |       |
| pint               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pint               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pint               | fix-unsafe         | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-basedpyright | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-pyrefly      | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-trace        | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| pint               | infer-ty           | True             | 1 failed, 2,289 passed, 590 skipped, 11 xfailed                       |            0 |    0 |     0 |
| dask               | released           |                  | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |              |      |       |
| dask               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| dask               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| dask               | fix-unsafe         | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-basedpyright | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-pyrefly      | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-trace        | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| dask               | infer-ty           | True             | 1 failed, 16,200 passed, 1,089 skipped, 513 xfailed, 2 xpassed        |            0 |    0 |     0 |
| zarr               | released           |                  | 8,422 passed, 1,205 skipped, 4 xfailed                                |              |      |       |
| zarr               | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| zarr               | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| zarr               | fix-unsafe         | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-basedpyright | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-pyrefly      | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-trace        | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| zarr               | infer-ty           | True             | 8,422 passed, 1,205 skipped, 4 xfailed                                |            0 |    0 |     0 |
| nibabel            | released           |                  | 20 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |              |      |       |
| nibabel            | fix-certain        | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-likely         | True             | 19 error, 107 failed, 5,170 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | fix-unsafe         | True             | 20 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-basedpyright | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-pyrefly      | True             | 19 error, 108 failed, 5,168 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-trace        | True             | 18 error, 110 failed, 5,167 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| nibabel            | infer-ty           | True             | 19 error, 107 failed, 5,169 passed, 304 skipped, 40 xfailed           |            0 |    0 |     0 |
| seaborn            | released           |                  | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |              |      |       |
| seaborn            | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| seaborn            | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| seaborn            | fix-unsafe         | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-basedpyright | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-pyrefly      | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-trace        | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| seaborn            | infer-ty           | True             | 8 error, 20 failed, 2,178 passed, 11 skipped, 6 xfailed               |            0 |    0 |     0 |
| optuna             | released           |                  | 16 error, 263 failed, 4,203 passed, 43 skipped                        |              |      |       |
| optuna             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| optuna             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| optuna             | fix-unsafe         | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-basedpyright | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-pyrefly      | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-trace        | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| optuna             | infer-ty           | True             | 16 error, 263 failed, 4,203 passed, 43 skipped                        |            0 |    0 |     0 |
| altair             | released           |                  | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |              |      |       |
| altair             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| altair             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| altair             | fix-unsafe         | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | infer-basedpyright | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | infer-pyrefly      | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | infer-trace        | True             | 28 failed, 1,866 passed, 12 skipped, 6 xfailed, 4 xpassed             |            0 |    0 |     0 |
| altair             | infer-ty           | True             | 28 failed, 1,866 passed, 12 skipped, 7 xfailed, 3 xpassed             |            0 |    0 |     0 |
| strawberry-graphql | released           |                  | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |              |      |       |
| strawberry-graphql | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| strawberry-graphql | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| strawberry-graphql | fix-unsafe         | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-basedpyright | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-pyrefly      | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-trace        | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| strawberry-graphql | infer-ty           | True             | 25 error, 51 failed, 2,521 passed, 3,293 skipped, 7 xfailed           |            0 |    0 |     0 |
| litestar           | released           |                  | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |              |      |       |
| litestar           | fix-certain        | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | fix-likely         | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | fix-unsafe         | True             | 6 failed, 5,645 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-basedpyright | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-pyrefly      | True             | 6 failed, 5,645 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-trace        | True             | 5 failed, 5,646 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| litestar           | infer-ty           | True             | 6 failed, 5,645 passed, 256 skipped, 13 xfailed, 30 xpassed           |            0 |    0 |     0 |
| narwhals           | released           |                  | 12,078 passed, 235 skipped, 709 xfailed                               |              |      |       |
| narwhals           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| narwhals           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| narwhals           | fix-unsafe         | True             | 12,078 passed, 235 skipped, 709 xfailed                               |            0 |    0 |     0 |
| narwhals           | infer-basedpyright | True             | 12,078 passed, 235 skipped, 709 xfailed                               |            0 |    0 |     0 |
| narwhals           | infer-pyrefly      | True             | 12,078 passed, 235 skipped, 709 xfailed                               |            0 |    0 |     0 |
| narwhals           | infer-trace        | True             | 12,078 passed, 235 skipped, 709 xfailed                               |            0 |    0 |     0 |
| narwhals           | infer-ty           | True             | 12,078 passed, 235 skipped, 709 xfailed                               |            0 |    0 |     0 |
| click              | released           |                  | 1,991 passed, 24 skipped, 1 xfailed                                   |              |      |       |
| click              | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| click              | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| click              | fix-unsafe         | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-basedpyright | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-pyrefly      | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-trace        | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| click              | infer-ty           | True             | 1,991 passed, 24 skipped, 1 xfailed                                   |            0 |    0 |     0 |
| pygments           | released           |                  | 1 failed, 5,330 passed, 15 skipped                                    |              |      |       |
| pygments           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pygments           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| pygments           | fix-unsafe         | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-basedpyright | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-pyrefly      | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-trace        | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| pygments           | infer-ty           | True             | 1 failed, 5,330 passed, 15 skipped                                    |            0 |    0 |     0 |
| celery             | released           |                  | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |              |      |       |
| celery             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| celery             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| celery             | fix-unsafe         | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-basedpyright | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-pyrefly      | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-trace        | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| celery             | infer-ty           | True             | 3 failed, 3,521 passed, 36 skipped, 3 xfailed                         |            0 |    0 |     0 |
| botocore           | released           |                  | 4,600 passed, 96 skipped                                              |              |      |       |
| botocore           | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| botocore           | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| botocore           | fix-unsafe         | True             | 4,600 passed, 96 skipped                                              |            0 |    0 |     0 |
| botocore           | infer-basedpyright | True             | 4,600 passed, 96 skipped                                              |            0 |    0 |     0 |
| botocore           | infer-pyrefly      | True             | 4,600 passed, 96 skipped                                              |            0 |    0 |     0 |
| botocore           | infer-trace        | True             | 4,600 passed, 96 skipped                                              |            0 |    0 |     0 |
| botocore           | infer-ty           | True             | 4,600 passed, 96 skipped                                              |            0 |    0 |     0 |
| joblib             | released           |                  | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |              |      |       |
| joblib             | fix-certain        | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| joblib             | fix-likely         | True             | as fix-unsafe's (implied)                                             |            0 |    0 |     0 |
| joblib             | fix-unsafe         | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-basedpyright | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-pyrefly      | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-trace        | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |
| joblib             | infer-ty           | True             | 7 failed, 1,485 passed, 45 skipped, 4 xpassed                         |            0 |    0 |     0 |

Each package's own type checks: its errors as released, then those new and gone:

| corpus             | run                | errors | new | gone |                                                   change |
| ------------------ | ------------------ | -----: | --: | ---: | -------------------------------------------------------: |
| sphinx             | released           |      3 |     |      |                                                          |
| sphinx             | fix-certain        |      3 |   0 |    0 | 194 files changed, 3207 insertions(+), 2162 deletions(-) |
| sphinx             | fix-likely         |      3 |   0 |    0 | 196 files changed, 3648 insertions(+), 2511 deletions(-) |
| sphinx             | fix-unsafe         |      3 |   0 |    0 | 212 files changed, 4040 insertions(+), 2829 deletions(-) |
| sphinx             | infer-basedpyright |      7 |   4 |    0 | 215 files changed, 4851 insertions(+), 3580 deletions(-) |
| sphinx             | infer-pyrefly      |     12 |   9 |    0 | 216 files changed, 5212 insertions(+), 3714 deletions(-) |
| sphinx             | infer-trace        |      3 |   0 |    0 | 212 files changed, 4040 insertions(+), 2829 deletions(-) |
| sphinx             | infer-ty           |     12 |   9 |    0 | 216 files changed, 4993 insertions(+), 3622 deletions(-) |
| streamlink         | released           |      0 |     |      |                                                          |
| streamlink         | fix-certain        |      0 |   0 |    0 |  164 files changed, 1034 insertions(+), 532 deletions(-) |
| streamlink         | fix-likely         |      0 |   0 |    0 |  166 files changed, 1144 insertions(+), 625 deletions(-) |
| streamlink         | fix-unsafe         |      0 |   0 |    0 |  168 files changed, 1279 insertions(+), 739 deletions(-) |
| streamlink         | infer-basedpyright |      1 |   1 |    0 | 185 files changed, 1752 insertions(+), 1132 deletions(-) |
| streamlink         | infer-pyrefly      |     41 |  41 |    0 | 186 files changed, 2110 insertions(+), 1170 deletions(-) |
| streamlink         | infer-trace        |      0 |   0 |    0 |  168 files changed, 1288 insertions(+), 745 deletions(-) |
| streamlink         | infer-ty           |     22 |  22 |    0 | 185 files changed, 2002 insertions(+), 1130 deletions(-) |
| mypy               | released           |      0 |     |      |                                                          |
| mypy               | fix-certain        |      0 |   0 |    0 | 160 files changed, 4983 insertions(+), 3030 deletions(-) |
| mypy               | fix-likely         |     14 |  14 |    0 | 166 files changed, 6183 insertions(+), 4080 deletions(-) |
| mypy               | fix-unsafe         |     17 |  17 |    0 | 167 files changed, 6580 insertions(+), 4399 deletions(-) |
| mypy               | infer-basedpyright |     21 |  21 |    0 | 170 files changed, 8613 insertions(+), 6233 deletions(-) |
| mypy               | infer-pyrefly      |     24 |  24 |    0 | 170 files changed, 9205 insertions(+), 6435 deletions(-) |
| mypy               | infer-trace        |     17 |  17 |    0 | 167 files changed, 6580 insertions(+), 4399 deletions(-) |
| mypy               | infer-ty           |     29 |  29 |    0 | 170 files changed, 8935 insertions(+), 6411 deletions(-) |
| httpx              | released           |      0 |     |      |                                                          |
| httpx              | fix-certain        |      0 |   0 |    0 |    16 files changed, 235 insertions(+), 195 deletions(-) |
| httpx              | fix-likely         |      0 |   0 |    0 |    16 files changed, 293 insertions(+), 238 deletions(-) |
| httpx              | fix-unsafe         |      0 |   0 |    0 |    16 files changed, 309 insertions(+), 254 deletions(-) |
| httpx              | infer-basedpyright |      1 |   1 |    0 |    18 files changed, 417 insertions(+), 347 deletions(-) |
| httpx              | infer-pyrefly      |      2 |   2 |    0 |    17 files changed, 398 insertions(+), 311 deletions(-) |
| httpx              | infer-trace        |      0 |   0 |    0 |    16 files changed, 309 insertions(+), 254 deletions(-) |
| httpx              | infer-ty           |      5 |   5 |    0 |    17 files changed, 388 insertions(+), 311 deletions(-) |
| starlette          | released           |      0 |     |      |                                                          |
| starlette          | fix-certain        |      0 |   0 |    0 |    29 files changed, 329 insertions(+), 248 deletions(-) |
| starlette          | fix-likely         |      0 |   0 |    0 |    33 files changed, 386 insertions(+), 296 deletions(-) |
| starlette          | fix-unsafe         |      0 |   0 |    0 |    33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-basedpyright |     12 |  12 |    0 |    33 files changed, 525 insertions(+), 408 deletions(-) |
| starlette          | infer-pyrefly      |     12 |  12 |    0 |    34 files changed, 518 insertions(+), 400 deletions(-) |
| starlette          | infer-trace        |      0 |   0 |    0 |    33 files changed, 429 insertions(+), 332 deletions(-) |
| starlette          | infer-ty           |     12 |  12 |    0 |    33 files changed, 526 insertions(+), 407 deletions(-) |
| uvicorn            | released           |      0 |     |      |                                                          |
| uvicorn            | fix-certain        |      0 |   0 |    0 |    26 files changed, 239 insertions(+), 182 deletions(-) |
| uvicorn            | fix-likely         |      0 |   0 |    0 |    26 files changed, 275 insertions(+), 207 deletions(-) |
| uvicorn            | fix-unsafe         |      0 |   0 |    0 |    27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-basedpyright |      7 |   7 |    0 |    29 files changed, 372 insertions(+), 283 deletions(-) |
| uvicorn            | infer-pyrefly      |      0 |   0 |    0 |    29 files changed, 407 insertions(+), 306 deletions(-) |
| uvicorn            | infer-trace        |      0 |   0 |    0 |    27 files changed, 294 insertions(+), 215 deletions(-) |
| uvicorn            | infer-ty           |      0 |   0 |    0 |    29 files changed, 380 insertions(+), 293 deletions(-) |
| websockets         | released           |      0 |     |      |                                                          |
| websockets         | fix-certain        |      0 |   0 |    0 |    39 files changed, 339 insertions(+), 233 deletions(-) |
| websockets         | fix-likely         |      0 |   0 |    0 |    39 files changed, 398 insertions(+), 290 deletions(-) |
| websockets         | fix-unsafe         |      0 |   0 |    0 |    39 files changed, 448 insertions(+), 324 deletions(-) |
| websockets         | infer-basedpyright |      4 |   4 |    0 |    40 files changed, 571 insertions(+), 443 deletions(-) |
| websockets         | infer-pyrefly      |      5 |   5 |    0 |    40 files changed, 620 insertions(+), 455 deletions(-) |
| websockets         | infer-trace        |      0 |   0 |    0 |    39 files changed, 448 insertions(+), 324 deletions(-) |
| websockets         | infer-ty           |      5 |   5 |    0 |    40 files changed, 600 insertions(+), 450 deletions(-) |
| hypercorn          | released           |     12 |     |      |                                                          |
| hypercorn          | fix-certain        |     12 |   0 |    0 |     24 files changed, 149 insertions(+), 96 deletions(-) |
| hypercorn          | fix-likely         |     12 |   0 |    0 |    25 files changed, 169 insertions(+), 109 deletions(-) |
| hypercorn          | fix-unsafe         |     12 |   0 |    0 |    25 files changed, 209 insertions(+), 146 deletions(-) |
| hypercorn          | infer-basedpyright |     12 |   0 |    0 |    25 files changed, 236 insertions(+), 167 deletions(-) |
| hypercorn          | infer-pyrefly      |     14 |   2 |    0 |    26 files changed, 265 insertions(+), 172 deletions(-) |
| hypercorn          | infer-trace        |     12 |   0 |    0 |    25 files changed, 209 insertions(+), 146 deletions(-) |
| hypercorn          | infer-ty           |     14 |   2 |    0 |    25 files changed, 250 insertions(+), 174 deletions(-) |
| mcp                | released           |      0 |     |      |                                                          |
| mcp                | fix-certain        |      0 |   0 |    0 |    80 files changed, 774 insertions(+), 519 deletions(-) |
| mcp                | fix-likely         |      0 |   0 |    0 |    80 files changed, 933 insertions(+), 667 deletions(-) |
| mcp                | fix-unsafe         |      2 |   2 |    0 |   81 files changed, 1023 insertions(+), 735 deletions(-) |
| mcp                | infer-basedpyright |      4 |   4 |    0 |   82 files changed, 1158 insertions(+), 862 deletions(-) |
| mcp                | infer-pyrefly      |     10 |  10 |    0 |   85 files changed, 1347 insertions(+), 968 deletions(-) |
| mcp                | infer-trace        |      2 |   2 |    0 |   81 files changed, 1023 insertions(+), 735 deletions(-) |
| mcp                | infer-ty           |      4 |   4 |    0 |   84 files changed, 1306 insertions(+), 938 deletions(-) |
| werkzeug           | released           |      0 |     |      |                                                          |
| werkzeug           | fix-certain        |      0 |   0 |    0 |    43 files changed, 542 insertions(+), 368 deletions(-) |
| werkzeug           | fix-likely         |      0 |   0 |    0 |    43 files changed, 608 insertions(+), 415 deletions(-) |
| werkzeug           | fix-unsafe         |      0 |   0 |    0 |    43 files changed, 673 insertions(+), 464 deletions(-) |
| werkzeug           | infer-basedpyright |      0 |   0 |    0 |    45 files changed, 803 insertions(+), 570 deletions(-) |
| werkzeug           | infer-pyrefly      |      3 |   3 |    0 |    45 files changed, 895 insertions(+), 594 deletions(-) |
| werkzeug           | infer-trace        |      0 |   0 |    0 |    43 files changed, 673 insertions(+), 464 deletions(-) |
| werkzeug           | infer-ty           |      1 |   1 |    0 |    45 files changed, 825 insertions(+), 573 deletions(-) |
| structlog          | released           |      8 |     |      |                                                          |
| structlog          | fix-certain        |      8 |   0 |    0 |     14 files changed, 109 insertions(+), 80 deletions(-) |
| structlog          | fix-likely         |      8 |   0 |    0 |     15 files changed, 124 insertions(+), 94 deletions(-) |
| structlog          | fix-unsafe         |      8 |   0 |    0 |    16 files changed, 138 insertions(+), 104 deletions(-) |
| structlog          | infer-basedpyright |      8 |   0 |    0 |    16 files changed, 166 insertions(+), 130 deletions(-) |
| structlog          | infer-pyrefly      |      9 |   1 |    0 |    16 files changed, 160 insertions(+), 117 deletions(-) |
| structlog          | infer-trace        |      8 |   0 |    0 |    16 files changed, 138 insertions(+), 104 deletions(-) |
| structlog          | infer-ty           |      8 |   0 |    0 |    16 files changed, 149 insertions(+), 114 deletions(-) |
| networkx           | released           |      0 |     |      |                                                          |
| networkx           | fix-certain        |      0 |   0 |    0 | 408 files changed, 3969 insertions(+), 3165 deletions(-) |
| networkx           | fix-likely         |      0 |   0 |    0 | 458 files changed, 6137 insertions(+), 5268 deletions(-) |
| networkx           | fix-unsafe         |      0 |   0 |    0 | 461 files changed, 6449 insertions(+), 5533 deletions(-) |
| networkx           | infer-basedpyright |      0 |   0 |    0 | 475 files changed, 7786 insertions(+), 6513 deletions(-) |
| networkx           | infer-pyrefly      |      0 |   0 |    0 | 472 files changed, 7166 insertions(+), 6039 deletions(-) |
| networkx           | infer-trace        |      0 |   0 |    0 | 476 files changed, 7141 insertions(+), 5902 deletions(-) |
| networkx           | infer-ty           |      0 |   0 |    0 | 466 files changed, 7021 insertions(+), 5947 deletions(-) |
| pint               | released           |    659 |     |      |                                                          |
| pint               | fix-certain        |    659 |   0 |    0 |    69 files changed, 572 insertions(+), 373 deletions(-) |
| pint               | fix-likely         |    659 |   0 |    0 |    73 files changed, 699 insertions(+), 467 deletions(-) |
| pint               | fix-unsafe         |    665 |  10 |    4 |    76 files changed, 755 insertions(+), 509 deletions(-) |
| pint               | infer-basedpyright |    666 |  11 |    4 |   79 files changed, 1122 insertions(+), 773 deletions(-) |
| pint               | infer-pyrefly      |    666 |  11 |    4 |   80 files changed, 1118 insertions(+), 739 deletions(-) |
| pint               | infer-trace        |    668 |  13 |    4 |    77 files changed, 811 insertions(+), 543 deletions(-) |
| pint               | infer-ty           |    667 |  13 |    5 |    79 files changed, 975 insertions(+), 670 deletions(-) |
| nibabel            | released           |     12 |     |      |                                                          |
| nibabel            | fix-certain        |     12 |   0 |    0 | 181 files changed, 2053 insertions(+), 1369 deletions(-) |
| nibabel            | fix-likely         |     13 |   1 |    0 | 191 files changed, 2748 insertions(+), 1982 deletions(-) |
| nibabel            | fix-unsafe         |     13 |   1 |    0 | 197 files changed, 3035 insertions(+), 2212 deletions(-) |
| nibabel            | infer-basedpyright |     15 |   3 |    0 | 202 files changed, 3752 insertions(+), 2808 deletions(-) |
| nibabel            | infer-pyrefly      |     16 |   4 |    0 | 203 files changed, 4106 insertions(+), 3027 deletions(-) |
| nibabel            | infer-trace        |     15 |   3 |    0 | 197 files changed, 3155 insertions(+), 2292 deletions(-) |
| nibabel            | infer-ty           |     14 |   2 |    0 | 199 files changed, 3699 insertions(+), 2747 deletions(-) |
| seaborn            | released           |     39 |     |      |                                                          |
| seaborn            | fix-certain        |     39 |   0 |    0 |    42 files changed, 660 insertions(+), 492 deletions(-) |
| seaborn            | fix-likely         |     39 |   0 |    0 |    46 files changed, 800 insertions(+), 614 deletions(-) |
| seaborn            | fix-unsafe         |     39 |   0 |    0 |    46 files changed, 895 insertions(+), 699 deletions(-) |
| seaborn            | infer-basedpyright |     39 |   0 |    0 |   46 files changed, 1050 insertions(+), 842 deletions(-) |
| seaborn            | infer-pyrefly      |     41 |   2 |    0 |   47 files changed, 1070 insertions(+), 840 deletions(-) |
| seaborn            | infer-trace        |     39 |   0 |    0 |    46 files changed, 951 insertions(+), 731 deletions(-) |
| seaborn            | infer-ty           |     39 |   0 |    0 |    46 files changed, 982 insertions(+), 778 deletions(-) |
| optuna             | released           |     52 |     |      |                                                          |
| optuna             | fix-certain        |     52 |   0 |    0 | 141 files changed, 1576 insertions(+), 1070 deletions(-) |
| optuna             | fix-likely         |     52 |   0 |    0 | 144 files changed, 1780 insertions(+), 1249 deletions(-) |
| optuna             | fix-unsafe         |     53 |   1 |    0 | 144 files changed, 1907 insertions(+), 1337 deletions(-) |
| optuna             | infer-basedpyright |     59 |   7 |    0 | 165 files changed, 2324 insertions(+), 1677 deletions(-) |
| optuna             | infer-pyrefly      |     62 |  10 |    0 | 164 files changed, 2405 insertions(+), 1718 deletions(-) |
| optuna             | infer-trace        |     53 |   1 |    0 | 144 files changed, 1907 insertions(+), 1337 deletions(-) |
| optuna             | infer-ty           |     68 |  16 |    0 | 162 files changed, 2347 insertions(+), 1691 deletions(-) |
| altair             | released           |      1 |     |      |                                                          |
| altair             | fix-certain        |      1 |   0 |    0 |    38 files changed, 392 insertions(+), 308 deletions(-) |
| altair             | fix-likely         |      1 |   0 |    0 |    38 files changed, 440 insertions(+), 354 deletions(-) |
| altair             | fix-unsafe         |      1 |   0 |    0 |    40 files changed, 457 insertions(+), 364 deletions(-) |
| altair             | infer-basedpyright |      4 |   3 |    0 |    40 files changed, 546 insertions(+), 433 deletions(-) |
| altair             | infer-pyrefly      |      7 |   6 |    0 |    40 files changed, 586 insertions(+), 451 deletions(-) |
| altair             | infer-trace        |      2 |   1 |    0 |    40 files changed, 467 insertions(+), 371 deletions(-) |
| altair             | infer-ty           |      9 |   8 |    0 |    40 files changed, 544 insertions(+), 429 deletions(-) |
| strawberry-graphql | released           |     10 |     |      |                                                          |
| strawberry-graphql | fix-certain        |     10 |   0 |    0 |   129 files changed, 667 insertions(+), 471 deletions(-) |
| strawberry-graphql | fix-likely         |     10 |   0 |    0 |   147 files changed, 840 insertions(+), 625 deletions(-) |
| strawberry-graphql | fix-unsafe         |     10 |   0 |    0 |   151 files changed, 897 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-basedpyright |     16 |   6 |    0 |  154 files changed, 1095 insertions(+), 838 deletions(-) |
| strawberry-graphql | infer-pyrefly      |     17 |   7 |    0 |  154 files changed, 1142 insertions(+), 862 deletions(-) |
| strawberry-graphql | infer-trace        |     10 |   0 |    0 |   151 files changed, 897 insertions(+), 668 deletions(-) |
| strawberry-graphql | infer-ty           |     18 |   8 |    0 |  155 files changed, 1146 insertions(+), 872 deletions(-) |
| litestar           | released           |     86 |     |      |                                                          |
| litestar           | fix-certain        |     86 |   0 |    0 |   142 files changed, 620 insertions(+), 439 deletions(-) |
| litestar           | fix-likely         |     86 |   0 |    0 |   152 files changed, 725 insertions(+), 521 deletions(-) |
| litestar           | fix-unsafe         |     86 |   0 |    0 |   165 files changed, 797 insertions(+), 567 deletions(-) |
| litestar           | infer-basedpyright |    301 | 215 |    0 |  183 files changed, 1123 insertions(+), 828 deletions(-) |
| litestar           | infer-pyrefly      |     93 |   7 |    0 |  175 files changed, 1194 insertions(+), 841 deletions(-) |
| litestar           | infer-trace        |     86 |   0 |    0 |   165 files changed, 797 insertions(+), 567 deletions(-) |
| litestar           | infer-ty           |     99 |  13 |    0 |  176 files changed, 1117 insertions(+), 816 deletions(-) |
| narwhals           | released           |     19 |     |      |                                                          |
| narwhals           | fix-certain        |     19 |   0 |    0 |   96 files changed, 1010 insertions(+), 836 deletions(-) |
| narwhals           | fix-likely         |     19 |   0 |    0 |   96 files changed, 1080 insertions(+), 903 deletions(-) |
| narwhals           | fix-unsafe         |     20 |   1 |    0 |   97 files changed, 1142 insertions(+), 947 deletions(-) |
| narwhals           | infer-basedpyright |     32 |  13 |    0 |  98 files changed, 1540 insertions(+), 1268 deletions(-) |
| narwhals           | infer-pyrefly      |     31 |  12 |    0 | 101 files changed, 1723 insertions(+), 1392 deletions(-) |
| narwhals           | infer-trace        |     20 |   1 |    0 |   97 files changed, 1142 insertions(+), 947 deletions(-) |
| narwhals           | infer-ty           |     61 |  42 |    0 | 100 files changed, 1674 insertions(+), 1368 deletions(-) |
| click              | released           |      0 |     |      |                                                          |
| click              | fix-certain        |      0 |   0 |    0 |    15 files changed, 290 insertions(+), 213 deletions(-) |
| click              | fix-likely         |      0 |   0 |    0 |    15 files changed, 318 insertions(+), 241 deletions(-) |
| click              | fix-unsafe         |      0 |   0 |    0 |    15 files changed, 357 insertions(+), 272 deletions(-) |
| click              | infer-basedpyright |      0 |   0 |    0 |    15 files changed, 442 insertions(+), 347 deletions(-) |
| click              | infer-pyrefly      |      0 |   0 |    0 |    15 files changed, 461 insertions(+), 360 deletions(-) |
| click              | infer-trace        |      0 |   0 |    0 |    15 files changed, 357 insertions(+), 272 deletions(-) |
| click              | infer-ty           |      5 |   5 |    0 |    15 files changed, 460 insertions(+), 358 deletions(-) |

Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most memory
it held at once, and what it was given (`sizing`):

| corpus             | step               | seconds | CPU seconds | CPUs | GB held | CPUs given | GB given | alone |
| ------------------ | ------------------ | ------: | ----------: | ---: | ------: | ---------: | -------: | ----: |
| black              | check              |     1.0 |         0.5 |  0.5 |    0.07 |          3 |     1.06 | False |
| black              | fix-certain        |     1.8 |         0.8 |  0.4 |    0.06 |          1 |      0.4 | False |
| black              | fix-likely         |     2.6 |         1.3 |  0.5 |    0.31 |          1 |     0.39 | False |
| black              | fix-unsafe         |     2.4 |         0.8 |  0.3 |    0.06 |          1 |     0.37 | False |
| black              | infer-basedpyright |     7.8 |        12.8 |  1.6 |    0.87 |          1 |     1.14 | False |
| black              | infer-ty           |     6.2 |         5.2 |  0.8 |    0.67 |          1 |     0.82 | False |
| black              | infer-pyrefly      |     4.6 |         4.8 |  1.0 |    0.68 |          1 |     0.77 | False |
| black              | census             |     0.8 |         0.6 |  0.7 |    0.06 |          3 |     1.06 | False |
| black              | coverage           |     0.6 |         0.3 |  0.5 |    0.06 |          1 |     0.09 | False |
| black              | timing             |     1.8 |         1.2 |  0.7 |    0.07 |         16 |     0.37 | False |
| black              | traced             |    10.4 |        54.1 |  5.2 |    1.23 |          7 |     1.57 | False |
| black              | tests              |   109.6 |       670.5 |  6.1 |     1.2 |          6 |     1.54 | False |
| pdm                | check              |     3.0 |         3.4 |  1.1 |    0.53 |          5 |     1.77 | False |
| pdm                | fix-certain        |     6.6 |         2.7 |  0.4 |    0.48 |          1 |      0.5 | False |
| pdm                | fix-likely         |     8.4 |         5.1 |  0.6 |    0.53 |          1 |      0.5 | False |
| pdm                | fix-unsafe         |     6.2 |         5.2 |  0.8 |    0.55 |          1 |     0.44 | False |
| pdm                | infer-basedpyright |    15.0 |        63.1 |  4.2 |    2.91 |          4 |     3.59 | False |
| pdm                | infer-ty           |     5.0 |        10.3 |  2.1 |    1.43 |          2 |     2.12 | False |
| pdm                | infer-pyrefly      |     8.0 |        13.2 |  1.6 |     1.9 |          2 |      2.3 | False |
| pdm                | census             |     0.6 |         0.4 |  0.7 |    0.06 |          5 |     1.77 | False |
| pdm                | coverage           |     1.4 |         0.4 |  0.3 |    0.06 |          1 |     0.04 | False |
| pdm                | timing             |     4.4 |         3.3 |  0.7 |    0.14 |         16 |     0.49 | False |
| pdm                | traced             |    16.6 |        87.9 |  5.3 |    1.19 |          3 |      1.5 | False |
| pdm                | tests              |    71.6 |       441.9 |  6.2 |    1.08 |          3 |     1.34 | False |
| tox                | check              |     1.4 |         0.7 |  0.5 |    0.08 |          2 |     1.21 | False |
| tox                | fix-certain        |     2.6 |         1.8 |  0.7 |    0.35 |          1 |     0.42 | False |
| tox                | fix-likely         |     6.4 |         5.2 |  0.8 |    0.38 |          1 |     0.44 | False |
| tox                | fix-unsafe         |     5.0 |         1.3 |  0.3 |    0.21 |          1 |     0.44 | False |
| tox                | infer-basedpyright |    14.4 |        50.9 |  3.5 |    2.48 |          3 |     3.02 | False |
| tox                | infer-ty           |    11.0 |        14.0 |  1.3 |    1.47 |          3 |     1.72 | False |
| tox                | infer-pyrefly      |     5.4 |        10.0 |  1.9 |    1.46 |          2 |     1.79 | False |
| tox                | census             |     1.0 |         0.7 |  0.7 |    0.06 |          2 |     1.21 | False |
| tox                | coverage           |     0.6 |         0.2 |  0.3 |    0.12 |          2 |     0.34 | False |
| tox                | timing             |     3.0 |         2.2 |  0.7 |    0.12 |         16 |     0.44 | False |
| tox                | traced             |    57.7 |       186.0 |  3.2 |    1.57 |          1 |     0.42 | False |
| tox                | tests              |   168.3 |       781.4 |  4.6 |    1.43 |          1 |     0.41 | False |
| sphinx             | check              |     0.4 |         0.3 |  0.7 |    0.06 |          7 |      2.5 | False |
| sphinx             | fix-certain        |     7.4 |        13.4 |  1.8 |     0.6 |          2 |     0.74 | False |
| sphinx             | fix-likely         |     7.8 |        16.3 |  2.1 |    0.83 |          2 |     0.72 | False |
| sphinx             | fix-unsafe         |     7.6 |        13.8 |  1.8 |    0.78 |          2 |     0.86 | False |
| sphinx             | infer-basedpyright |    24.0 |       109.1 |  4.5 |    4.47 |          4 |     5.46 | False |
| sphinx             | infer-ty           |    14.2 |        41.7 |  2.9 |    2.33 |          3 |     2.92 | False |
| sphinx             | infer-pyrefly      |     9.8 |        28.4 |  2.9 |    2.65 |          2 |      3.2 | False |
| sphinx             | census             |     3.6 |         5.2 |  1.4 |    0.54 |          7 |      2.5 | False |
| sphinx             | coverage           |     3.2 |         2.8 |  0.9 |    0.35 |          1 |     0.36 | False |
| sphinx             | timing             |     9.8 |         9.3 |  0.9 |    0.55 |         16 |     0.66 | False |
| sphinx             | traced             |    26.4 |       129.5 |  4.9 |    1.68 |          5 |      2.1 | False |
| sphinx             | tests              |    92.9 |       692.0 |  7.4 |    1.58 |          7 |     1.97 | False |
| sphinx             | types              |    46.9 |        42.6 |  0.9 |    0.39 |          1 |     0.37 | False |
| mkdocs             | check              |     1.2 |         0.4 |  0.3 |    0.06 |          2 |     1.05 | False |
| mkdocs             | fix-certain        |     2.6 |         1.6 |  0.6 |    0.35 |          1 |     0.42 | False |
| mkdocs             | fix-likely         |     3.0 |         1.7 |  0.6 |    0.56 |          1 |     0.44 | False |
| mkdocs             | fix-unsafe         |     2.8 |         1.4 |  0.5 |    0.33 |          1 |     0.42 | False |
| mkdocs             | infer-basedpyright |    15.1 |        30.7 |  2.0 |     1.6 |          2 |     2.01 | False |
| mkdocs             | infer-ty           |     6.0 |         6.2 |  1.0 |    0.98 |          1 |     1.26 | False |
| mkdocs             | infer-pyrefly      |     5.4 |         4.1 |  0.8 |    0.91 |          1 |      1.3 | False |
| mkdocs             | census             |     1.8 |         0.8 |  0.4 |    0.06 |          2 |     1.05 | False |
| mkdocs             | coverage           |     0.8 |         0.3 |  0.4 |    0.06 |          1 |      0.1 | False |
| mkdocs             | timing             |     2.6 |         1.9 |  0.7 |    0.09 |         16 |     0.42 | False |
| mkdocs             | traced             |    13.4 |         4.2 |  0.3 |    0.29 |          1 |     0.15 | False |
| mkdocs             | tests              |    58.7 |        13.0 |  0.2 |     0.1 |          1 |     0.12 | False |
| streamlink         | check              |     0.2 |         0.1 |  0.5 |    0.06 |          6 |     1.97 | False |
| streamlink         | fix-certain        |     4.2 |         3.8 |  0.9 |    0.64 |          2 |     0.54 | False |
| streamlink         | fix-likely         |    11.2 |        10.7 |  1.0 |    0.61 |          1 |     0.52 | False |
| streamlink         | fix-unsafe         |     3.2 |         2.3 |  0.7 |     0.4 |          1 |     0.52 | False |
| streamlink         | infer-basedpyright |    25.9 |        82.3 |  3.2 |    3.15 |          4 |     3.72 | False |
| streamlink         | infer-ty           |     8.4 |        19.4 |  2.3 |     1.7 |          2 |     2.05 | False |
| streamlink         | infer-pyrefly      |     6.8 |         8.6 |  1.3 |    1.63 |          2 |     2.24 | False |
| streamlink         | census             |     2.2 |         1.1 |  0.5 |    0.34 |          6 |     1.97 | False |
| streamlink         | coverage           |     0.6 |         0.2 |  0.3 |    0.06 |          1 |     0.09 | False |
| streamlink         | timing             |     5.6 |         4.2 |  0.8 |    0.38 |         16 |     0.22 | False |
| streamlink         | traced             |    19.8 |        15.1 |  0.8 |    0.35 |          1 |     0.51 | False |
| streamlink         | tests              |    75.9 |        63.2 |  0.8 |     0.2 |          1 |     0.25 | False |
| streamlink         | types              |    41.9 |        40.3 |  1.0 |    0.34 |          1 |     0.42 | False |
| mypy               | check              |     0.4 |         0.3 |  0.7 |    0.07 |          8 |     3.05 | False |
| mypy               | fix-certain        |    21.1 |        33.4 |  1.6 |    0.92 |          2 |     1.04 | False |
| mypy               | fix-likely         |    17.7 |        30.3 |  1.7 |    1.13 |          3 |     1.07 | False |
| mypy               | fix-unsafe         |    20.9 |        31.9 |  1.5 |    0.99 |          2 |      1.1 | False |
| mypy               | infer-basedpyright |    74.6 |       181.7 |  2.4 |    5.18 |          3 |     6.21 | False |
| mypy               | infer-ty           |    36.9 |        81.8 |  2.2 |     2.9 |          3 |     3.54 | False |
| mypy               | infer-pyrefly      |    29.3 |        56.0 |  1.9 |    3.25 |          3 |     3.95 | False |
| mypy               | census             |     7.8 |        12.6 |  1.6 |    0.62 |          8 |     3.05 | False |
| mypy               | coverage           |     2.0 |         2.8 |  1.4 |    0.41 |          1 |     0.41 | False |
| mypy               | timing             |    14.0 |        16.0 |  1.1 |    0.63 |         16 |     0.72 | False |
| mypy               | traced             |   314.2 |      2096.5 |  6.7 |    6.23 |          6 |     8.45 | False |
| mypy               | tests              |  2193.4 |     12229.3 |  5.6 |    6.43 |          3 |     8.25 | False |
| mypy               | types              |    68.9 |       173.8 |  2.5 |    0.68 |          2 |     0.85 | False |
| httpx              | check              |     1.0 |         0.5 |  0.5 |    0.06 |          4 |     1.24 | False |
| httpx              | fix-certain        |     1.8 |         0.8 |  0.4 |    0.06 |          1 |     0.14 | False |
| httpx              | fix-likely         |     2.2 |         0.9 |  0.4 |    0.13 |          1 |     0.37 | False |
| httpx              | fix-unsafe         |     2.0 |         0.9 |  0.5 |    0.06 |          1 |     0.41 | False |
| httpx              | infer-basedpyright |    12.0 |        13.1 |  1.1 |    0.78 |          1 |     1.06 | False |
| httpx              | infer-ty           |     3.6 |         3.2 |  0.9 |    0.26 |          1 |     0.76 | False |
| httpx              | infer-pyrefly      |     3.0 |         2.1 |  0.7 |    0.31 |          1 |      0.7 | False |
| httpx              | census             |     0.4 |         0.2 |  0.5 |    0.06 |          4 |     1.24 | False |
| httpx              | coverage           |     1.0 |         0.3 |  0.3 |    0.06 |          1 |     0.27 | False |
| httpx              | timing             |     1.4 |         0.9 |  0.6 |    0.06 |         16 |     0.11 | False |
| httpx              | traced             |     8.0 |         5.9 |  0.7 |    0.21 |          1 |     0.32 | False |
| httpx              | tests              |    28.3 |        21.5 |  0.8 |     0.2 |          1 |     0.17 | False |
| httpx              | types              |    57.5 |        54.0 |  0.9 |    0.33 |          1 |     0.27 | False |
| starlette          | check              |     0.4 |         0.2 |  0.5 |    0.06 |          3 |     1.02 | False |
| starlette          | fix-certain        |     1.8 |         0.9 |  0.5 |    0.49 |          1 |     0.37 | False |
| starlette          | fix-likely         |     2.2 |         1.5 |  0.7 |    0.33 |          1 |     0.37 | False |
| starlette          | fix-unsafe         |     2.0 |         0.8 |  0.4 |    0.07 |          1 |     0.24 | False |
| starlette          | infer-basedpyright |     7.4 |        16.1 |  2.2 |    1.28 |          2 |     1.04 | False |
| starlette          | infer-ty           |     3.8 |         3.9 |  1.0 |    0.63 |          1 |     0.94 | False |
| starlette          | infer-pyrefly      |     3.0 |         2.6 |  0.9 |    0.25 |          1 |     1.02 | False |
| starlette          | census             |     1.0 |         0.5 |  0.5 |    0.06 |          3 |     1.02 | False |
| starlette          | coverage           |     0.6 |         0.3 |  0.5 |    0.07 |          2 |     0.32 | False |
| starlette          | timing             |     1.6 |         1.0 |  0.6 |    0.06 |         16 |     0.09 | False |
| starlette          | traced             |    11.4 |         7.6 |  0.7 |    0.22 |          1 |     0.21 | False |
| starlette          | tests              |    37.9 |        29.1 |  0.8 |     0.2 |          1 |     0.19 | False |
| starlette          | types              |    10.6 |         9.7 |  0.9 |    0.31 |          1 |     0.21 | False |
| uvicorn            | check              |     0.2 |         0.2 |  1.0 |    0.06 |          2 |     1.11 | False |
| uvicorn            | fix-certain        |     3.2 |         0.9 |  0.3 |    0.19 |          1 |     0.34 | False |
| uvicorn            | fix-likely         |     4.0 |         1.8 |  0.5 |    0.34 |          1 |     0.36 | False |
| uvicorn            | fix-unsafe         |     3.0 |         0.9 |  0.3 |    0.27 |          1 |     0.34 | False |
| uvicorn            | infer-basedpyright |     9.4 |        18.8 |  2.0 |    1.26 |          2 |     1.56 | False |
| uvicorn            | infer-ty           |     3.4 |         3.8 |  1.1 |    0.81 |          2 |     1.01 | False |
| uvicorn            | infer-pyrefly      |     5.8 |         3.4 |  0.6 |    0.78 |          1 |     0.94 | False |
| uvicorn            | census             |     1.0 |         0.5 |  0.5 |    0.06 |          2 |     1.11 | False |
| uvicorn            | coverage           |     1.4 |         0.4 |  0.3 |    0.11 |          1 |     0.07 | False |
| uvicorn            | timing             |     1.6 |         1.1 |  0.7 |     0.1 |         16 |     0.12 | False |
| uvicorn            | traced             |    32.5 |        24.9 |  0.8 |    1.24 |          1 |     1.54 | False |
| uvicorn            | tests              |   208.8 |       110.9 |  0.5 |    1.13 |          1 |     1.45 | False |
| uvicorn            | types              |    11.0 |         9.8 |  0.9 |    0.26 |          1 |     0.21 | False |
| anyio              | check              |     0.4 |         0.2 |  0.5 |    0.06 |          3 |     1.39 | False |
| anyio              | fix-certain        |     4.2 |         1.1 |  0.3 |    0.16 |          1 |     0.31 | False |
| anyio              | fix-likely         |     5.6 |         1.2 |  0.2 |    0.29 |          1 |     0.39 | False |
| anyio              | fix-unsafe         |     4.0 |         1.6 |  0.4 |    0.52 |          1 |     0.34 | False |
| anyio              | infer-basedpyright |    28.7 |        31.0 |  1.1 |    1.28 |          2 |     1.61 | False |
| anyio              | infer-ty           |     9.8 |         8.2 |  0.8 |    0.98 |          1 |     1.21 | False |
| anyio              | infer-pyrefly      |     6.4 |         5.6 |  0.9 |    0.94 |          1 |     1.19 | False |
| anyio              | census             |     1.6 |         0.7 |  0.4 |    0.06 |          3 |     1.39 | False |
| anyio              | coverage           |     1.0 |         0.3 |  0.3 |    0.09 |          2 |      5.0 | False |
| anyio              | timing             |     2.2 |         1.5 |  0.7 |     0.1 |         16 |     0.11 | False |
| anyio              | traced             |   126.5 |        53.5 |  0.4 |    0.31 |          1 |      0.4 | False |
| anyio              | tests              |   620.1 |       262.5 |  0.4 |    0.28 |          1 |     0.35 | False |
| websockets         | check              |     1.8 |         1.2 |  0.7 |    0.31 |          1 |     1.04 | False |
| websockets         | fix-certain        |     4.2 |         2.0 |  0.5 |    0.32 |          1 |      0.3 | False |
| websockets         | fix-likely         |     4.6 |         2.9 |  0.6 |    0.34 |          1 |      0.3 | False |
| websockets         | fix-unsafe         |     4.2 |         2.5 |  0.6 |    0.32 |          1 |     0.32 | False |
| websockets         | infer-basedpyright |    19.3 |        27.7 |  1.4 |    1.31 |          2 |     1.61 | False |
| websockets         | infer-ty           |    11.0 |         9.7 |  0.9 |    0.94 |          1 |     1.14 | False |
| websockets         | infer-pyrefly      |     7.8 |         5.2 |  0.7 |    0.85 |          1 |     1.16 | False |
| websockets         | census             |     2.4 |         0.6 |  0.2 |    0.06 |          1 |     1.04 | False |
| websockets         | coverage           |     1.4 |         0.4 |  0.3 |    0.06 |          1 |      0.2 | False |
| websockets         | timing             |     2.0 |         1.4 |  0.7 |    0.08 |         16 |     0.26 | False |
| websockets         | traced             |    95.8 |         5.7 |  0.1 |    0.19 |          1 |     0.34 | False |
| websockets         | tests              |   558.9 |        18.7 |  0.0 |    0.17 |          1 |     0.21 | False |
| websockets         | types              |     4.4 |         3.9 |  0.9 |     0.2 |          1 |     0.19 | False |
| hypercorn          | check              |     0.6 |         0.4 |  0.7 |    0.27 |          3 |     1.12 | False |
| hypercorn          | fix-certain        |     1.2 |         0.6 |  0.5 |    0.06 |          1 |     0.32 | False |
| hypercorn          | fix-likely         |     1.2 |         0.6 |  0.5 |    0.06 |          1 |     0.32 | False |
| hypercorn          | fix-unsafe         |     1.2 |         0.6 |  0.5 |    0.06 |          1 |     0.34 | False |
| hypercorn          | infer-basedpyright |     5.6 |        13.4 |  2.4 |    1.09 |          1 |     1.25 | False |
| hypercorn          | infer-ty           |     2.2 |         2.8 |  1.3 |    0.52 |          1 |     0.22 | False |
| hypercorn          | infer-pyrefly      |     1.8 |         2.1 |  1.2 |    0.77 |          1 |     0.42 | False |
| hypercorn          | census             |     0.4 |         0.3 |  0.7 |    0.06 |          3 |     1.12 | False |
| hypercorn          | coverage           |     0.6 |         0.3 |  0.5 |    0.06 |          1 |      0.1 | False |
| hypercorn          | timing             |     1.2 |         0.9 |  0.8 |     0.1 |         16 |      5.0 | False |
| hypercorn          | traced             |     8.0 |         1.8 |  0.2 |    0.13 |          1 |     0.16 | False |
| hypercorn          | tests              |    38.6 |         4.8 |  0.1 |    0.12 |          1 |     0.15 | False |
| hypercorn          | types              |     5.4 |         4.8 |  0.9 |    0.25 |          1 |     0.19 | False |
| aiohttp            | check              |     0.2 |         0.1 |  0.5 |    0.06 |          3 |     1.52 | False |
| aiohttp            | fix-certain        |     5.2 |         1.7 |  0.3 |    0.47 |          1 |      0.4 | False |
| aiohttp            | fix-likely         |     7.2 |         8.3 |  1.2 |    0.51 |          1 |     0.36 | False |
| aiohttp            | fix-unsafe         |     5.4 |         4.7 |  0.9 |    0.58 |          1 |     0.42 | False |
| aiohttp            | infer-basedpyright |    20.5 |        43.9 |  2.1 |    1.84 |          2 |     2.41 | False |
| aiohttp            | infer-ty           |    11.7 |        14.4 |  1.2 |     1.2 |          2 |     1.51 | False |
| aiohttp            | infer-pyrefly      |     6.0 |         6.3 |  1.1 |    1.21 |          2 |     1.51 | False |
| aiohttp            | census             |     1.6 |         0.7 |  0.4 |    0.12 |          3 |     1.52 | False |
| aiohttp            | coverage           |     0.6 |         0.8 |  1.3 |     0.3 |          2 |      5.0 | False |
| aiohttp            | timing             |     3.4 |         2.5 |  0.7 |    0.12 |         16 |     0.16 | False |
| aiohttp            | traced             |    98.8 |       820.5 |  8.3 |    4.05 |          7 |     4.96 | False |
| aiohttp            | tests              |   433.6 |      3741.2 |  8.6 |    3.57 |          7 |      4.5 | False |
| fastapi            | check              |     0.2 |         0.2 |  1.0 |    0.06 |          2 |     1.39 | False |
| fastapi            | fix-certain        |     3.2 |         1.1 |  0.3 |    0.32 |          1 |     0.36 | False |
| fastapi            | fix-likely         |     4.6 |         1.9 |  0.4 |    0.35 |          1 |     0.37 | False |
| fastapi            | fix-unsafe         |     3.4 |         2.0 |  0.6 |    0.34 |          1 |     0.34 | False |
| fastapi            | infer-basedpyright |    13.4 |        26.4 |  2.0 |    1.42 |          2 |     1.72 | False |
| fastapi            | infer-ty           |     6.2 |         5.9 |  1.0 |    0.94 |          1 |     1.14 | False |
| fastapi            | infer-pyrefly      |     5.8 |         6.2 |  1.1 |    1.04 |          1 |     1.17 | False |
| fastapi            | census             |     2.2 |         0.7 |  0.3 |    0.14 |          2 |     1.39 | False |
| fastapi            | coverage           |     0.8 |         0.3 |  0.4 |    0.06 |          1 |     0.36 | False |
| fastapi            | timing             |     2.2 |         1.4 |  0.6 |    0.33 |         16 |     0.15 | False |
| fastapi            | traced             |    20.6 |       116.8 |  5.7 |    2.35 |          4 |     2.85 | False |
| fastapi            | tests              |   104.4 |       618.9 |  5.9 |    2.15 |          5 |     2.84 | False |
| textual            | check              |     0.4 |         0.3 |  0.7 |    0.06 |          5 |     2.11 | False |
| textual            | fix-certain        |     5.8 |         3.7 |  0.6 |    0.52 |          1 |     0.54 | False |
| textual            | fix-likely         |     7.2 |        10.8 |  1.5 |    0.68 |          2 |      0.6 | False |
| textual            | fix-unsafe         |     5.4 |         6.0 |  1.1 |    0.65 |          2 |     0.64 | False |
| textual            | infer-basedpyright |    27.7 |       108.3 |  3.9 |     3.8 |          4 |     4.62 | False |
| textual            | infer-ty           |    13.4 |        36.0 |  2.7 |    2.22 |          3 |     2.71 | False |
| textual            | infer-pyrefly      |    10.0 |        29.9 |  3.0 |    2.55 |          3 |     3.14 | False |
| textual            | census             |     4.2 |         3.2 |  0.8 |    0.43 |          5 |     2.11 | False |
| textual            | coverage           |     1.4 |         1.0 |  0.7 |     0.3 |          3 |     0.45 | False |
| textual            | timing             |     7.0 |         5.2 |  0.7 |    0.22 |         16 |     0.31 | False |
| mcp                | check              |     1.4 |         0.9 |  0.6 |    0.33 |          2 |      1.3 | False |
| mcp                | fix-certain        |     7.6 |         4.5 |  0.6 |    0.38 |          1 |     0.54 | False |
| mcp                | fix-likely         |     3.0 |         1.8 |  0.6 |    0.36 |          2 |     0.45 | False |
| mcp                | fix-unsafe         |     4.2 |         1.9 |  0.5 |    0.32 |          1 |     0.29 | False |
| mcp                | infer-basedpyright |    15.3 |        55.3 |  3.6 |    2.41 |          3 |     3.24 | False |
| mcp                | infer-ty           |     8.6 |        16.1 |  1.9 |    1.67 |          2 |     2.06 | False |
| mcp                | infer-pyrefly      |     6.2 |        12.5 |  2.0 |    1.78 |          2 |     2.25 | False |
| mcp                | census             |     0.6 |         0.6 |  1.0 |    0.06 |          2 |      1.3 | False |
| mcp                | coverage           |     2.8 |         1.4 |  0.5 |    0.29 |          1 |     0.05 | False |
| mcp                | timing             |     3.2 |         2.3 |  0.7 |    0.34 |         16 |     0.16 | False |
| mcp                | traced             |    19.8 |        89.6 |  4.5 |    2.51 |          5 |      3.2 | False |
| mcp                | tests              |   104.6 |       422.0 |  4.0 |    2.35 |          4 |     2.95 | False |
| mcp                | types              |   135.6 |       194.3 |  1.4 |    1.33 |          1 |     1.65 | False |
| pytest             | check              |     1.8 |         2.4 |  1.3 |    0.38 |          5 |     1.75 | False |
| pytest             | fix-certain        |     8.8 |         5.4 |  0.6 |    0.42 |          1 |     0.46 | False |
| pytest             | fix-likely         |    10.2 |         8.3 |  0.8 |     0.5 |          1 |      0.5 | False |
| pytest             | fix-unsafe         |     8.6 |         7.6 |  0.9 |    0.63 |          1 |     0.52 | False |
| pytest             | infer-basedpyright |    27.3 |        52.8 |  1.9 |    2.46 |          2 |     2.91 | False |
| pytest             | infer-ty           |    16.2 |        20.9 |  1.3 |    1.41 |          1 |      1.7 | False |
| pytest             | infer-pyrefly      |    13.6 |        13.8 |  1.0 |    1.44 |          1 |     1.79 | False |
| pytest             | census             |     1.0 |         0.8 |  0.8 |    0.06 |          5 |     1.75 | False |
| pytest             | coverage           |     0.8 |         1.0 |  1.2 |    0.31 |          2 |     0.39 | False |
| pytest             | timing             |     4.2 |         2.9 |  0.7 |    0.32 |         16 |     0.17 | False |
| pytest             | traced             |    54.9 |       339.9 |  6.2 |     2.0 |          6 |     2.34 | False |
| pytest             | tests              |   128.0 |       918.2 |  7.2 |    1.58 |          5 |     1.94 | False |
| attrs              | check              |     0.4 |         0.1 |  0.2 |    0.06 |          3 |     1.17 | False |
| attrs              | fix-certain        |     1.6 |         0.7 |  0.4 |    0.06 |          1 |     0.34 | False |
| attrs              | fix-likely         |     1.8 |         0.6 |  0.3 |    0.06 |          1 |     0.34 | False |
| attrs              | fix-unsafe         |     1.6 |         0.6 |  0.4 |    0.06 |          1 |     0.35 | False |
| attrs              | infer-basedpyright |     6.4 |         9.6 |  1.5 |    0.76 |          1 |     0.92 | False |
| attrs              | infer-ty           |     2.6 |         1.8 |  0.7 |    0.52 |          1 |     0.67 | False |
| attrs              | infer-pyrefly      |     2.6 |         1.3 |  0.5 |    0.31 |          1 |     0.39 | False |
| attrs              | census             |     0.6 |         0.3 |  0.5 |    0.12 |          3 |     1.17 | False |
| attrs              | coverage           |     0.4 |         0.2 |  0.5 |    0.06 |          1 |      0.3 | False |
| attrs              | timing             |     1.2 |         0.7 |  0.6 |    0.05 |         16 |     0.07 | False |
| attrs              | traced             |     6.0 |        23.6 |  3.9 |    0.97 |          3 |     0.97 | False |
| attrs              | tests              |    19.5 |       100.8 |  5.2 |    0.83 |          3 |     1.02 | False |
| werkzeug           | check              |     0.4 |         0.2 |  0.5 |    0.06 |          3 |     1.42 | False |
| werkzeug           | fix-certain        |     2.4 |         0.8 |  0.3 |    0.14 |          1 |      0.4 | False |
| werkzeug           | fix-likely         |     3.4 |         1.0 |  0.3 |    0.29 |          1 |     0.42 | False |
| werkzeug           | fix-unsafe         |     2.6 |         2.0 |  0.8 |    0.34 |          1 |     0.36 | False |
| werkzeug           | infer-basedpyright |    10.8 |        26.1 |  2.4 |    1.23 |          2 |     1.71 | False |
| werkzeug           | infer-ty           |     5.8 |         7.6 |  1.3 |    0.84 |          1 |     1.07 | False |
| werkzeug           | infer-pyrefly      |     5.2 |         4.0 |  0.8 |    0.83 |          1 |     1.07 | False |
| werkzeug           | census             |     2.2 |         0.8 |  0.4 |    0.11 |          3 |     1.42 | False |
| werkzeug           | coverage           |     0.8 |         0.3 |  0.4 |    0.06 |          1 |     0.05 | False |
| werkzeug           | timing             |     2.2 |         1.6 |  0.7 |     0.1 |         16 |     0.05 | False |
| werkzeug           | traced             |    11.6 |         8.8 |  0.8 |    0.32 |          1 |     0.44 | False |
| werkzeug           | tests              |    39.7 |        33.1 |  0.8 |    0.22 |          1 |     0.29 | False |
| werkzeug           | types              |     8.2 |         7.2 |  0.9 |    0.16 |          1 |     0.19 | False |
| cattrs             | check              |     0.6 |         0.1 |  0.2 |    0.06 |          4 |     1.29 | False |
| cattrs             | fix-certain        |     2.4 |         1.3 |  0.5 |    0.47 |          1 |     0.37 | False |
| cattrs             | fix-likely         |     4.0 |         1.2 |  0.3 |     0.3 |          1 |      0.1 | False |
| cattrs             | fix-unsafe         |     4.0 |         0.9 |  0.2 |    0.06 |          1 |     0.36 | False |
| cattrs             | infer-basedpyright |    17.7 |        21.2 |  1.2 |    1.16 |          1 |     1.21 | False |
| cattrs             | infer-ty           |     5.0 |         3.5 |  0.7 |    0.71 |          1 |     0.96 | False |
| cattrs             | infer-pyrefly      |     7.6 |         3.0 |  0.4 |    0.75 |          1 |      1.0 | False |
| cattrs             | census             |     0.8 |         0.3 |  0.4 |    0.06 |          4 |     1.29 | False |
| cattrs             | coverage           |     0.4 |         0.2 |  0.5 |    0.06 |          2 |      5.0 | False |
| cattrs             | timing             |     1.4 |         0.9 |  0.6 |    0.06 |         16 |      5.0 | False |
| cattrs             | traced             |    21.3 |       143.9 |  6.8 |    1.55 |          5 |     1.95 | False |
| cattrs             | tests              |   109.8 |       700.3 |  6.4 |    1.26 |          5 |     1.61 | False |
| structlog          | check              |     0.4 |         0.2 |  0.5 |    0.06 |          1 |     0.22 | False |
| structlog          | fix-certain        |     2.2 |         0.7 |  0.3 |    0.07 |          1 |     0.35 | False |
| structlog          | fix-likely         |     2.6 |         1.3 |  0.5 |     0.5 |          1 |     0.34 | False |
| structlog          | fix-unsafe         |     1.2 |         0.6 |  0.5 |    0.06 |          1 |     0.22 | False |
| structlog          | infer-basedpyright |     6.4 |        10.0 |  1.6 |    0.52 |          1 |     0.87 | False |
| structlog          | infer-ty           |     2.2 |         1.7 |  0.8 |    0.22 |          1 |     0.67 | False |
| structlog          | infer-pyrefly      |     2.0 |         1.4 |  0.7 |    0.22 |          1 |     0.66 | False |
| structlog          | census             |     1.0 |         0.5 |  0.5 |    0.12 |          1 |     0.22 | False |
| structlog          | coverage           |     0.8 |         0.4 |  0.5 |    0.13 |          1 |     0.04 | False |
| structlog          | timing             |     1.0 |         0.7 |  0.7 |    0.14 |         16 |     0.32 | False |
| structlog          | traced             |     4.6 |         3.0 |  0.7 |    0.11 |          1 |     0.14 | False |
| structlog          | tests              |     5.6 |         5.6 |  1.0 |     0.1 |          1 |     0.12 | False |
| structlog          | types              |     3.6 |         2.7 |  0.8 |    0.14 |          1 |     0.15 | False |
| xarray             | check              |     0.2 |         0.2 |  1.0 |    0.09 |          8 |     4.85 | False |
| xarray             | fix-certain        |    40.1 |        67.7 |  1.7 |    1.42 |          2 |     1.72 | False |
| xarray             | fix-likely         |    39.3 |        83.3 |  2.1 |    1.92 |          2 |     1.85 | False |
| xarray             | fix-unsafe         |    34.1 |        64.8 |  1.9 |    1.51 |          2 |     1.88 | False |
| xarray             | infer-basedpyright |   113.4 |       429.4 |  3.8 |   10.32 |          3 |    10.87 | False |
| xarray             | infer-ty           |    98.5 |       250.5 |  2.5 |    5.03 |          3 |     5.95 | False |
| xarray             | infer-pyrefly      |    64.8 |       120.8 |  1.9 |    5.45 |          2 |     6.99 | False |
| xarray             | census             |    17.2 |        29.9 |  1.7 |    0.99 |          8 |     4.85 | False |
| xarray             | coverage           |     2.4 |         1.3 |  0.5 |    0.33 |          3 |     0.74 | False |
| xarray             | timing             |    45.8 |        59.9 |  1.3 |     1.0 |         16 |     1.25 | False |
| xarray             | traced             |    65.7 |       219.9 |  3.3 |    2.39 |          3 |     2.97 | False |
| xarray             | tests              |   103.4 |       672.2 |  6.5 |    2.25 |          6 |     2.95 | False |
| networkx           | check              |     0.4 |         0.3 |  0.7 |    0.08 |          6 |     5.05 | False |
| networkx           | fix-certain        |    13.8 |        25.2 |  1.8 |    0.93 |          2 |      1.4 | False |
| networkx           | fix-likely         |    18.4 |        42.4 |  2.3 |    1.62 |          2 |     1.51 | False |
| networkx           | fix-unsafe         |    12.0 |        20.4 |  1.7 |    0.98 |          3 |     1.32 | False |
| networkx           | infer-basedpyright |    95.6 |       355.1 |  3.7 |     8.9 |          3 |    10.06 | False |
| networkx           | infer-ty           |    37.6 |        95.3 |  2.5 |    3.54 |          3 |     4.29 | False |
| networkx           | infer-pyrefly      |    42.2 |       133.2 |  3.2 |    5.24 |          3 |     6.04 | False |
| networkx           | census             |     9.6 |        15.3 |  1.6 |    0.79 |          6 |     5.05 | False |
| networkx           | coverage           |     1.6 |         0.2 |  0.1 |    0.06 |          2 |     0.52 | False |
| networkx           | timing             |    22.4 |        30.0 |  1.3 |    1.04 |         16 |     1.06 | False |
| networkx           | traced             |    49.3 |       301.6 |  6.1 |    3.07 |          6 |     3.74 | False |
| networkx           | tests              |   116.4 |      1195.4 | 10.3 |    2.71 |          8 |     3.46 | False |
| networkx           | types              |    25.7 |        24.4 |  0.9 |    0.47 |          1 |     0.42 | False |
| pint               | check              |     2.0 |         2.9 |  1.4 |    0.44 |          3 |     1.86 | False |
| pint               | fix-certain        |    10.6 |         8.4 |  0.8 |    0.57 |          1 |     0.59 | False |
| pint               | fix-likely         |     8.2 |         8.0 |  1.0 |    0.54 |          2 |     0.57 | False |
| pint               | fix-unsafe         |     9.6 |         5.0 |  0.5 |    0.39 |          1 |     0.59 | False |
| pint               | infer-basedpyright |    49.3 |       116.5 |  2.4 |    3.64 |          3 |     4.42 | False |
| pint               | infer-ty           |    34.3 |        51.5 |  1.5 |    2.84 |          2 |      3.6 | False |
| pint               | infer-pyrefly      |    18.3 |        22.1 |  1.2 |    1.98 |          2 |     2.37 | False |
| pint               | census             |     0.8 |         0.7 |  0.9 |    0.06 |          3 |     1.86 | False |
| pint               | coverage           |     1.8 |         0.6 |  0.3 |    0.26 |          1 |     0.14 | False |
| pint               | timing             |     4.8 |         3.2 |  0.7 |    0.41 |         16 |     0.51 | False |
| pint               | traced             |    42.3 |        34.0 |  0.8 |    0.57 |          1 |     0.52 | False |
| pint               | tests              |   166.5 |       154.1 |  0.9 |    0.17 |          1 |     0.21 | False |
| pint               | types              |    43.3 |        73.5 |  1.7 |    0.64 |          2 |     0.76 | False |
| dask               | check              |     0.4 |         0.2 |  0.5 |    0.08 |          7 |     6.01 | False |
| dask               | fix-certain        |    45.9 |        87.2 |  1.9 |    1.65 |          2 |     1.95 | False |
| dask               | fix-likely         |    79.8 |       134.4 |  1.7 |    2.29 |          2 |      2.0 | False |
| dask               | fix-unsafe         |    80.3 |       130.7 |  1.6 |    2.12 |          2 |     2.02 | False |
| dask               | infer-basedpyright |   238.5 |       690.6 |  2.9 |   12.01 |          3 |    15.06 | False |
| dask               | infer-ty           |   149.8 |       391.0 |  2.6 |    5.46 |          3 |      6.4 | False |
| dask               | infer-pyrefly      |    83.2 |       195.9 |  2.4 |    6.71 |          3 |      8.1 | False |
| dask               | census             |    13.8 |        25.9 |  1.9 |    1.23 |          7 |     6.01 | False |
| dask               | coverage           |     3.4 |         5.5 |  1.6 |    0.53 |          1 |     0.66 | False |
| dask               | timing             |    57.2 |        78.7 |  1.4 |    1.23 |         16 |     1.54 | False |
| dask               | traced             |   262.8 |      1361.3 |  5.2 |    6.62 |          5 |     7.77 | False |
| dask               | tests              |   913.8 |      7116.4 |  7.8 |    5.53 |          6 |     9.05 | False |
| zarr               | check              |     0.2 |         0.1 |  0.5 |    0.06 |          5 |     1.97 | False |
| zarr               | fix-certain        |     5.4 |         3.3 |  0.6 |    0.57 |          2 |     0.55 | False |
| zarr               | fix-likely         |     7.4 |         8.4 |  1.1 |    0.56 |          2 |     0.62 | False |
| zarr               | fix-unsafe         |     8.0 |         8.4 |  1.1 |    0.59 |          1 |     0.52 | False |
| zarr               | infer-basedpyright |    40.3 |        92.0 |  2.3 |     3.1 |          3 |      3.8 | False |
| zarr               | infer-ty           |    16.9 |        29.0 |  1.7 |    1.99 |          3 |     2.41 | False |
| zarr               | infer-pyrefly      |    10.2 |        13.1 |  1.3 |    1.89 |          2 |     2.47 | False |
| zarr               | census             |     1.2 |         0.6 |  0.5 |    0.06 |          5 |     1.97 | False |
| zarr               | coverage           |     1.6 |         0.3 |  0.2 |    0.06 |          1 |     0.34 | False |
| zarr               | timing             |     4.4 |         3.2 |  0.7 |    0.14 |         16 |     0.19 | False |
| zarr               | traced             |   105.4 |       179.5 |  1.7 |    2.54 |          2 |     3.15 | False |
| zarr               | tests              |   639.9 |      1175.8 |  1.8 |    2.44 |          2 |     4.76 | False |
| nibabel            | check              |     4.4 |         5.5 |  1.2 |    0.55 |          4 |     2.95 | False |
| nibabel            | fix-certain        |     8.2 |        15.2 |  1.9 |    0.62 |          2 |     0.79 | False |
| nibabel            | fix-likely         |    12.5 |        23.2 |  1.9 |    0.88 |          2 |     0.87 | False |
| nibabel            | fix-unsafe         |     9.7 |        13.7 |  1.4 |     0.7 |          2 |     0.79 | False |
| nibabel            | infer-basedpyright |    65.1 |       246.1 |  3.8 |    5.81 |          3 |     6.92 | False |
| nibabel            | infer-ty           |    56.7 |       181.5 |  3.2 |    2.89 |          3 |     3.56 | False |
| nibabel            | infer-pyrefly      |    16.3 |        41.6 |  2.6 |     3.0 |          3 |     3.76 | False |
| nibabel            | census             |     1.4 |         1.4 |  1.0 |    0.07 |          4 |     2.95 | False |
| nibabel            | coverage           |     0.8 |         0.2 |  0.2 |    0.06 |          2 |     0.45 | False |
| nibabel            | timing             |    12.2 |        13.1 |  1.1 |    0.55 |         16 |     0.61 | False |
| nibabel            | traced             |    30.3 |       105.2 |  3.5 |    1.41 |          3 |     1.77 | False |
| nibabel            | tests              |   235.9 |      1441.4 |  6.1 |    1.28 |          3 |     1.64 | False |
| nibabel            | types              |    17.4 |        14.8 |  0.9 |    0.33 |          1 |     0.25 | False |
| seaborn            | check              |     0.2 |         0.1 |  0.5 |    0.06 |          4 |     1.88 | False |
| seaborn            | fix-certain        |     3.6 |         1.7 |  0.5 |    0.39 |          2 |     0.61 | False |
| seaborn            | fix-likely         |     6.4 |         5.1 |  0.8 |    0.52 |          2 |     0.66 | False |
| seaborn            | fix-unsafe         |     5.8 |         6.8 |  1.2 |     0.5 |          2 |     0.61 | False |
| seaborn            | infer-basedpyright |    41.2 |        82.2 |  2.0 |    3.26 |          2 |     3.81 | False |
| seaborn            | infer-ty           |    11.6 |        21.3 |  1.8 |    1.34 |          2 |     1.71 | False |
| seaborn            | infer-pyrefly      |     9.0 |        18.3 |  2.0 |    1.68 |          2 |     2.07 | False |
| seaborn            | census             |     2.2 |         0.9 |  0.4 |    0.07 |          4 |     1.88 | False |
| seaborn            | coverage           |     2.0 |         0.4 |  0.2 |    0.06 |          1 |     0.39 | False |
| seaborn            | timing             |     6.4 |         4.4 |  0.7 |    0.17 |         16 |     0.22 | False |
| seaborn            | traced             |    69.0 |       576.7 |  8.4 |    5.68 |          8 |     5.26 | False |
| seaborn            | tests              |   289.4 |      3277.2 | 11.3 |     5.5 |          8 |     4.97 | False |
| seaborn            | types              |     7.4 |         6.3 |  0.9 |     0.3 |          1 |     0.09 | False |
| optuna             | check              |     3.6 |         2.8 |  0.8 |    0.63 |          6 |      4.0 | False |
| optuna             | fix-certain        |    10.2 |        15.2 |  1.5 |     0.8 |          2 |     1.41 | False |
| optuna             | fix-likely         |    34.3 |        40.7 |  1.2 |    2.08 |          2 |     1.41 | False |
| optuna             | fix-unsafe         |    10.6 |        13.1 |  1.2 |     0.8 |          2 |     1.41 | False |
| optuna             | infer-basedpyright |    64.4 |       153.8 |  2.4 |    4.78 |          4 |     6.07 | False |
| optuna             | infer-ty           |    23.9 |        61.5 |  2.6 |    2.91 |          3 |     3.59 | False |
| optuna             | infer-pyrefly      |    31.9 |        54.0 |  1.7 |    3.98 |          2 |     4.06 | False |
| optuna             | census             |     0.8 |         0.7 |  0.9 |    0.06 |          6 |      4.0 | False |
| optuna             | coverage           |     1.6 |         0.4 |  0.2 |    0.25 |          2 |      5.0 | False |
| optuna             | timing             |    10.0 |         7.6 |  0.8 |    0.36 |         16 |     0.34 | False |
| optuna             | traced             |   452.7 |      4210.6 |  9.3 |    6.56 |          8 |     7.95 | False |
| optuna             | tests              |  1153.4 |     10794.6 |  9.4 |    6.48 |          8 |     7.92 | False |
| optuna             | types              |    59.4 |        56.4 |  0.9 |    1.28 |          1 |     0.52 | False |
| altair             | check              |     0.2 |         0.2 |  1.0 |    0.06 |          4 |     2.34 | False |
| altair             | fix-certain        |    15.9 |        10.9 |  0.7 |     0.7 |          1 |     0.71 | False |
| altair             | fix-likely         |    18.6 |        14.0 |  0.8 |    0.88 |          1 |     0.69 | False |
| altair             | fix-unsafe         |    14.8 |        11.1 |  0.7 |    0.77 |          1 |      0.7 | False |
| altair             | infer-basedpyright |    26.1 |        51.4 |  2.0 |    2.81 |          2 |     3.52 | False |
| altair             | infer-ty           |    24.1 |        22.5 |  0.9 |    1.63 |          1 |     1.92 | False |
| altair             | infer-pyrefly      |    17.7 |        20.5 |  1.2 |    2.25 |          1 |     2.46 | False |
| altair             | census             |     3.6 |         2.8 |  0.8 |    0.49 |          4 |     2.34 | False |
| altair             | coverage           |     1.8 |         1.5 |  0.8 |    0.38 |          1 |     0.35 | False |
| altair             | timing             |     6.4 |         4.3 |  0.7 |    0.64 |         16 |     0.62 | False |
| altair             | traced             |    49.4 |       163.0 |  3.3 |    6.17 |          3 |      8.0 | False |
| altair             | tests              |   181.9 |      1100.2 |  6.0 |     6.2 |          5 |     8.19 | False |
| altair             | types              |    46.1 |        42.6 |  0.9 |    0.65 |          1 |      0.5 | False |
| stripe             | check              |     0.2 |         0.1 |  0.5 |    0.06 |          7 |     4.34 | False |
| stripe             | fix-certain        |    11.2 |        21.5 |  1.9 |    0.93 |          2 |     1.16 | False |
| stripe             | fix-likely         |    13.8 |        33.1 |  2.4 |    1.05 |          2 |     1.16 | False |
| stripe             | fix-unsafe         |    12.4 |        26.1 |  2.1 |    0.92 |          2 |     1.17 | False |
| stripe             | infer-basedpyright |   946.8 |      2474.4 |  2.6 |    4.85 |          3 |     5.71 | False |
| stripe             | infer-ty           |    22.7 |        63.6 |  2.8 |    2.65 |          2 |     3.36 | False |
| stripe             | infer-pyrefly      |    25.9 |        77.9 |  3.0 |    3.58 |          3 |     4.38 | False |
| stripe             | census             |     4.8 |         6.7 |  1.4 |    0.79 |          7 |     4.34 | False |
| stripe             | coverage           |     2.4 |         1.0 |  0.4 |    0.29 |          2 |     0.56 | False |
| stripe             | timing             |    20.0 |        22.1 |  1.1 |    0.86 |         16 |     1.05 | False |
| strawberry-graphql | check              |     0.4 |         0.2 |  0.5 |    0.06 |          3 |     1.85 | False |
| strawberry-graphql | fix-certain        |     3.4 |         2.3 |  0.7 |    0.42 |          2 |     0.67 | False |
| strawberry-graphql | fix-likely         |    10.6 |         9.5 |  0.9 |    0.62 |          1 |     0.67 | False |
| strawberry-graphql | fix-unsafe         |    10.2 |         7.9 |  0.8 |    0.56 |          1 |     0.67 | False |
| strawberry-graphql | infer-basedpyright |    15.6 |        73.5 |  4.7 |    3.18 |          3 |     4.21 | False |
| strawberry-graphql | infer-ty           |     7.0 |        15.7 |  2.2 |    1.67 |          2 |     2.26 | False |
| strawberry-graphql | infer-pyrefly      |     5.8 |        12.3 |  2.1 |    1.95 |          2 |     2.41 | False |
| strawberry-graphql | census             |     1.8 |         0.9 |  0.5 |    0.09 |          3 |     1.85 | False |
| strawberry-graphql | coverage           |     1.6 |         0.4 |  0.2 |    0.11 |          1 |     0.05 | False |
| strawberry-graphql | timing             |     4.4 |         3.3 |  0.7 |    0.16 |         16 |     0.17 | False |
| strawberry-graphql | traced             |    25.6 |       109.2 |  4.3 |    1.69 |          4 |     2.11 | False |
| strawberry-graphql | tests              |    93.8 |       519.3 |  5.5 |     1.5 |          5 |     1.92 | False |
| strawberry-graphql | types              |    17.2 |        15.1 |  0.9 |     0.4 |          1 |      0.3 | False |
| litestar           | check              |     0.2 |         0.1 |  0.5 |    0.06 |          3 |     2.17 | False |
| litestar           | fix-certain        |     6.4 |         6.4 |  1.0 |    0.53 |          1 |     0.66 | False |
| litestar           | fix-likely         |    15.8 |        14.0 |  0.9 |    0.97 |          1 |     0.65 | False |
| litestar           | fix-unsafe         |     4.4 |         3.6 |  0.8 |     0.5 |          2 |     0.94 | False |
| litestar           | infer-basedpyright |    35.5 |       114.6 |  3.2 |    3.71 |          2 |     4.42 | False |
| litestar           | infer-ty           |    18.4 |        34.0 |  1.8 |     2.2 |          1 |      2.7 | False |
| litestar           | infer-pyrefly      |     9.9 |        20.7 |  2.1 |    2.65 |          2 |     3.16 | False |
| litestar           | census             |     2.0 |         2.2 |  1.1 |    0.49 |          3 |     2.17 | False |
| litestar           | coverage           |     2.0 |         1.0 |  0.5 |    0.28 |          1 |     0.39 | False |
| litestar           | timing             |     5.8 |         4.5 |  0.8 |    0.21 |         16 |     0.25 | False |
| litestar           | traced             |    44.6 |       188.4 |  4.2 |    3.97 |          3 |     5.06 | False |
| litestar           | tests              |   335.5 |      1636.3 |  4.9 |    4.13 |          4 |     5.17 | False |
| litestar           | types              |   390.4 |       500.0 |  1.3 |    1.95 |          2 |     2.44 | False |
| narwhals           | check              |     1.2 |         0.4 |  0.3 |    0.08 |          4 |     2.15 | False |
| narwhals           | fix-certain        |     5.2 |         4.7 |  0.9 |    0.51 |          2 |     0.65 | False |
| narwhals           | fix-likely         |    19.5 |        20.0 |  1.0 |     1.1 |          1 |     0.61 | False |
| narwhals           | fix-unsafe         |    16.7 |        11.4 |  0.7 |    0.75 |          1 |     0.61 | False |
| narwhals           | infer-basedpyright |    45.7 |       105.3 |  2.3 |    3.98 |          4 |     4.69 | False |
| narwhals           | infer-ty           |    25.9 |        69.5 |  2.7 |    3.25 |          2 |     4.06 | False |
| narwhals           | infer-pyrefly      |    15.1 |        33.2 |  2.2 |    3.32 |          2 |     3.86 | False |
| narwhals           | census             |     0.6 |         0.5 |  0.8 |    0.06 |          4 |     2.15 | False |
| narwhals           | coverage           |     1.0 |         0.3 |  0.3 |    0.06 |          2 |     0.41 | False |
| narwhals           | timing             |     6.0 |         4.6 |  0.8 |    0.23 |         16 |     0.27 | False |
| narwhals           | traced             |    19.4 |       129.2 |  6.7 |    5.77 |          1 |     1.52 | False |
| narwhals           | tests              |   152.2 |       825.6 |  5.4 |    5.98 |          1 |     1.59 | False |
| narwhals           | types              |   220.7 |       415.9 |  1.9 |    2.02 |          2 |     2.22 | False |
| click              | check              |     0.8 |         0.3 |  0.4 |    0.06 |          1 |     1.02 | False |
| click              | fix-certain        |     1.4 |         0.7 |  0.5 |    0.06 |          1 |     0.26 | False |
| click              | fix-likely         |     1.6 |         0.6 |  0.4 |    0.06 |          1 |     0.37 | False |
| click              | fix-unsafe         |     1.8 |         1.0 |  0.6 |     0.3 |          1 |     0.39 | False |
| click              | infer-basedpyright |     9.4 |        13.8 |  1.5 |    0.78 |          1 |     0.99 | False |
| click              | infer-ty           |     3.2 |         2.6 |  0.8 |    0.58 |          1 |      0.4 | False |
| click              | infer-pyrefly      |     2.8 |         1.9 |  0.7 |    0.55 |          1 |     0.77 | False |
| click              | census             |     0.6 |         0.3 |  0.5 |    0.06 |          1 |     1.02 | False |
| click              | coverage           |     0.6 |         0.3 |  0.5 |    0.06 |          1 |     0.04 | False |
| click              | timing             |     1.6 |         1.0 |  0.6 |    0.06 |         16 |     0.12 | False |
| click              | traced             |     6.2 |         5.3 |  0.9 |     0.2 |          1 |     0.37 | False |
| click              | tests              |    30.7 |        28.4 |  0.9 |    0.18 |          1 |     0.22 | False |
| click              | types              |     4.6 |         3.7 |  0.8 |    0.12 |          1 |     0.16 | False |
| pygments           | check              |     0.2 |         0.1 |  0.5 |    0.06 |          5 |      2.0 | False |
| pygments           | fix-certain        |     5.4 |        10.3 |  1.9 |    0.51 |          2 |     0.59 | False |
| pygments           | fix-likely         |     5.6 |         4.6 |  0.8 |    0.46 |          2 |     0.61 | False |
| pygments           | fix-unsafe         |    13.0 |        12.2 |  0.9 |    0.59 |          1 |     0.57 | False |
| pygments           | infer-basedpyright |    37.9 |        99.5 |  2.6 |    3.36 |          3 |     4.39 | False |
| pygments           | infer-ty           |     9.6 |        27.1 |  2.8 |    1.76 |          3 |     2.24 | False |
| pygments           | infer-pyrefly      |     9.4 |        21.9 |  2.3 |    2.19 |          2 |     2.72 | False |
| pygments           | census             |     2.8 |         1.6 |  0.6 |    0.07 |          5 |      2.0 | False |
| pygments           | coverage           |     1.0 |         1.1 |  1.1 |    0.35 |          2 |     0.49 | False |
| pygments           | timing             |     7.2 |         5.4 |  0.8 |     0.4 |         16 |     0.32 | False |
| pygments           | traced             |    19.2 |        20.6 |  1.1 |     0.5 |          1 |      0.5 | False |
| pygments           | tests              |    86.2 |        77.8 |  0.9 |    0.25 |          1 |     0.31 | False |
| celery             | check              |     5.6 |         3.3 |  0.6 |    0.63 |          5 |     3.05 | False |
| celery             | fix-certain        |    14.0 |        13.1 |  0.9 |    0.86 |          1 |     0.81 | False |
| celery             | fix-likely         |    14.2 |        17.6 |  1.2 |    0.87 |          1 |     0.62 | False |
| celery             | fix-unsafe         |    15.1 |        12.5 |  0.8 |    0.88 |          1 |     0.81 | False |
| celery             | infer-basedpyright |    40.9 |       109.2 |  2.7 |    4.01 |          3 |     4.85 | False |
| celery             | infer-ty           |    14.3 |        24.8 |  1.7 |    2.04 |          2 |      2.4 | False |
| celery             | infer-pyrefly      |    12.4 |        21.5 |  1.7 |    2.23 |          2 |     2.64 | False |
| celery             | census             |     1.6 |         0.7 |  0.4 |    0.06 |          5 |     3.05 | False |
| celery             | coverage           |     1.4 |         0.3 |  0.2 |    0.06 |          1 |     0.11 | False |
| celery             | timing             |     7.4 |         5.5 |  0.7 |     0.5 |         16 |     0.26 | False |
| celery             | traced             |   133.6 |        46.2 |  0.3 |    5.89 |          1 |      7.3 | False |
| celery             | tests              |   845.3 |       306.7 |  0.4 |     4.7 |          1 |     5.86 | False |
| botocore           | check              |     0.2 |         0.1 |  0.5 |    0.06 |          4 |     1.72 | False |
| botocore           | fix-certain        |    10.4 |         9.2 |  0.9 |    0.52 |          1 |     0.56 | False |
| botocore           | fix-likely         |    12.8 |         9.6 |  0.7 |    0.51 |          1 |     0.57 | False |
| botocore           | fix-unsafe         |     4.6 |         3.7 |  0.8 |    0.54 |          2 |      0.6 | False |
| botocore           | infer-basedpyright |    19.8 |        49.6 |  2.5 |    2.47 |          3 |     3.01 | False |
| botocore           | infer-ty           |     5.2 |         8.4 |  1.6 |    1.32 |          2 |     1.74 | False |
| botocore           | infer-pyrefly      |     6.0 |        11.9 |  2.0 |    1.47 |          2 |     1.82 | False |
| botocore           | census             |     2.4 |         1.0 |  0.4 |    0.32 |          4 |     1.72 | False |
| botocore           | coverage           |     2.2 |         0.4 |  0.2 |    0.06 |          1 |     0.36 | False |
| botocore           | timing             |     5.6 |         4.0 |  0.7 |    0.29 |         16 |      0.2 | False |
| botocore           | traced             |    36.9 |       105.2 |  2.9 |    5.22 |          3 |     6.49 | False |
| botocore           | tests              |   171.1 |       529.2 |  3.1 |     5.0 |          3 |     6.26 | False |
| joblib             | check              |     1.6 |         0.1 |  0.1 |    0.06 |          3 |     1.54 | False |
| joblib             | fix-certain        |     6.6 |         4.1 |  0.6 |     0.4 |          1 |     0.42 | False |
| joblib             | fix-likely         |     7.0 |         5.0 |  0.7 |     0.4 |          1 |     0.41 | False |
| joblib             | fix-unsafe         |     6.0 |         2.2 |  0.4 |    0.34 |          2 |     0.54 | False |
| joblib             | infer-basedpyright |    12.4 |        40.6 |  3.3 |     2.7 |          3 |      3.4 | False |
| joblib             | infer-ty           |    15.6 |        20.0 |  1.3 |    1.49 |          2 |     1.84 | False |
| joblib             | infer-pyrefly      |     7.6 |        10.8 |  1.4 |    1.38 |          2 |     1.75 | False |
| joblib             | census             |     2.0 |         0.8 |  0.4 |    0.06 |          3 |     1.54 | False |
| joblib             | coverage           |     1.6 |         0.4 |  0.2 |    0.06 |          1 |     0.31 | False |
| joblib             | timing             |     3.8 |         2.5 |  0.7 |    0.14 |         16 |     0.15 | False |
| joblib             | traced             |   161.9 |       316.9 |  2.0 |    1.76 |          1 |     2.16 | False |
| joblib             | tests              |   841.0 |      1809.6 |  2.2 |    1.81 |          1 |     2.32 | False |

- xarray, mega+dev, infer-basedpyright: held 10.32 GB beside other steps
- networkx, mega+dev, infer-basedpyright: held 8.9 GB beside other steps
- dask, mega+dev, infer-basedpyright: held 12.01 GB beside other steps

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
