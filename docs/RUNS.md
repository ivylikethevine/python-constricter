# Corpus runs

What each constricter version found and fixed on the corpus: CPython's standard library and the
pinned `corpus` packages, at every level with `all-scopes`. Recorded by the corpus runner
(`tests/corpus/runs/release.toml`); a file per version, added when the version goes up (see
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

## Runs

- [Super corpora](runs/super-corpora.md)
- [Mega corpora](runs/mega-corpora.md)
- [Basic corpora](runs/basic-corpora.md)
- [constricter 0.2.2](runs/0.2.2.md)
- [constricter 0.2.3](runs/0.2.3.md)
- [constricter 0.2.4](runs/0.2.4.md)
- [constricter 0.2.5](runs/0.2.5.md)
- [constricter 0.2.6](runs/0.2.6.md)
- [constricter 0.2.7](runs/0.2.7.md)
- [constricter 0.2.8](runs/0.2.8.md)
- [constricter 0.2.9](runs/0.2.9.md)
- [constricter 0.3.1](runs/0.3.1.md)
- [constricter 0.3.6](runs/0.3.6.md)
- [constricter 0.4.0](runs/0.4.0.md)
- [constricter 0.4.3](runs/0.4.3.md)
