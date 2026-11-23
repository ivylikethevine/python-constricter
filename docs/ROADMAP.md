# Roadmap

What's next. What's done, and what was measured on the way, is in [COMPLETED.md](COMPLETED.md).

By size (smallest first) and, within each, by value: the bindings with no fix an item could reach,
of the 140,562 on the seven corpora at 0.4.0, or of the 23,647 on pydantic, sqlalchemy and django
for an item that needs `--infer-with`; what only makes a run or a check faster comes last. An item's
size is the hours an Opus 5.5 agent would work on it, tests and docs included, apart from what it
waits on (a full corpus run, a package's suite): each ends with that estimate, after what it is,
why, how and when it's done, and with the coverage it's expected to add: its fixes as a share of the
252,637 offences the 0.4.0 run found on the seven corpora, a guess from the item's reach, not a
measurement. What an item cites from the census (`corpus_untyped`) is the 0.4.0 run's on the seven
corpora or the 0.4.0-rc.3 mega run's on all 47; its finer counts are as first measured. Where an
item cites a sample, it's 41 directories of the standard library, pandas, django and sqlalchemy,
each checked alone: 28,931 bindings with no fix. First what's built and waits on a run, last what to
measure before building.

## Where it stands

2026-11-22, at `28c1bb6` on `dev`, one commit past `b2fa80d` on `main` (tagged v0.4.7, the last
release), which holds the work for 3a, 3b, 12 and 13; no PR open, so CI hasn't run on it.

- The latest mega run is `mega-11-20-2026-1208` (`9ffc314`, 78 minutes on 16CPU/60GB, no step
  failed): the suites' new type errors 694 from 710, narwhals' 8 fewer in each of ty's and the
  union's steps, its fixes the same; agreement 13 blamed of 12,389, 0.105 per 100, one over its bar
  (10); sqlalchemy's four passed again (2); matplotlib's one fix after pyrefly's hints left (4);
  nibabel's one test failing in the union step, as on `mega-11-17-2026-1924`. Neither that run nor
  the two `mega-11-17` runs before it is yet in [COMPLETED.md](COMPLETED.md#corpus), where
  `mega-11-16-2026-1443` and every earlier run named here are read.
- Built 2026-11-20 (`3be4558`, in v0.4.7), each waiting on a run: pyrefly's servers started anew
  for each round after their first, leaving pip and matplotlib no second pass in one process (4, a
  mega run); a suite's unmeasured tests started once 2 CPUs are free, and an unmeasured hinted step
  sized by a fit to measured peaks that counts what the corpus imports (3, an `alt-fresh` run); a
  new type error naming an argument blamed on the fix of the name passed (10, a mega run). Since,
  in v0.4.7: a run file's `every-level` check, or another version's, checks the levels one after
  another, not four at once (`6599abc`: the standard library's 13.8 GB to 3.4, under CI's 16 GB
  runner); a run checking this checkout once is unchanged.
- Built 2026-11-22 (`28c1bb6`): `infer-fresh`, set in `alt-fresh.toml` (3a); a first run's
  unmeasured steps started by how many steps wait for each (3b). Read on
  `alt-fresh-11-22-2026-1703` (`28c1bb6`, 16CPU/60GB, no step failed), both bars met: no hinted
  round read from the store, the 24 hinted steps' peaks a median 0.92 of the fit, at most 1.90
  (matplotlib's basedpyright); 8.0 minutes to a proved 7.7, 4% over. urllib3's union step lists
  one new test error, its dummy server's `EADDRINUSE` retry leaking a socket, as `infer-ty`'s two
  that passed again. Proposed, not built, and not needed for the bar: trio's `at-once = 7` (3b).
  `schedule_solve.py --starts` looped on that run, its walk back from the last step going
  between urllib3's two 0.2s `tests-fix-*` on one checkout; fixed the same day (a step's
  predecessor starts strictly earlier), and both 11-20's and 11-22's lines now print.
- Verified: CI, CodeQL and Security green on `b2fa80d` (GitHub), the test matrix's Python 3.11 to
  3.14 included, and its Release run. On 16CPU/60GB, 2026-11-22 on `28c1bb6`'s tree:
  `tests/ci_local.py test lint` outside the sandbox (coverage 100%), only `uv lock --check`
  failing, which the global `exclude-newer` makes re-resolve here; `tests/corpus` on Python 3.11;
  the docs job, `reuse lint` outside the sandbox.
- What a run costs on 16CPU/60GB: the seven corpora's basic run 35 minutes
  (`basic-11-03-2026-2103`, [basic-corpora.md](runs/basic-corpora.md)); a mega run of all 55 78 to
  97 minutes; `mega-fixes` (`tests/corpus/runs/mega-fixes.toml`, the fix steps and type checks alone
  against the latest mega run's records, `scripts/scratch/run_fixes_diff.py`) 12 to 14 minutes,
  measuring none of the bars; an `alt-fresh` run of the 8 alt corpora about 7.
- Not done or not run: a staged run with hours between its stages (1); the mutation run (6); the
  peak and parallel timings again, which predate 2026-10-28 (7, 8).
- Open questions, not looked into: the rest of the 58 a second pass still fixes after the hints on
  `mega-11-20-2026-1208`, and twisted's 12 of `mega-11-16-2026-1443` (4); that run's matplotlib
  hinted steps' 99, 98 and 33 fewer fixes; nibabel's union step failing 2 tests where it failed 1.
- Waiting on a decision: trio's `at-once = 7` (3b); item 13's open questions (which operations,
  what's exempt, a fix or not). Items 9 and 11 are in Later.

## Order of work

- 3, 3a, 3b: bars met on `alt-fresh-11-22-2026-1703`; to move to COMPLETED.md. Trio's
  `at-once = 7` waits on a yes or no, no longer needed for the bar.
- 4, 10: the next mega run: matplotlib's 0 after pyrefly's hints; agreement read with errors
  blamed by the argument they name (0.105 blamed for under 0.1). 2: confirmed by a mega run where
  sqlalchemy's four fail.
- 1: an hour beside the next super run, made in stages hours apart.
- 6: the mutation run, then its survivors.
- 7, then 8: memory and speed, last by this file's rule; each timed again first.
- 13, on hold: once its open questions are answered.

## Now

### Built, waiting on a run

#### 1. Runs in stages

Built in `88e0dda`: a run's steps fall into stages run one at a time into one folder
(`tests/corpus/stages.py`): built in `fixes`, `traced`, `tests` and `timed`, regrouped by a run
file's `[stages]` table. `--stage NAME` runs that stage's steps alone, a step needing a stage still
to run left for it; the report is written from the records so far, naming the stages left, and
published once every stage is in. A stage on another commit, other uncommitted changes or another
run file than the folder's earlier stages is refused, naming both, unless `--join-anyway`, and the
report then gives each stage's commit. Done when a super run made in four stages at separate times
gives the report one sitting does. Coverage unchanged. Its timings are of 2026-10-22 and 10-24,
before the changes since. The 0.4.3-rc.3 super run (`ac48774`,
16CPU/60GB) ran its four stages back to back into one folder: `fixes` 17 minutes, `traced` 15,
`tests` 12, `timed` 4, 48 in all as rc.2's one sitting took; each joined, and the report and RUNS.md
were written once the last was in. The 0.4.3-rc.4 super run (`46bdc27`) ran them with 90s between:
`fixes` 16.5 minutes, `traced` 11, `tests` 20.5, `timed` 4, each exiting 0 and joining, the report
naming one commit for all four. Left: stages hours apart, with other work between. About an hour
beside the runs.

#### 2. sqlalchemy's four `test_compare` failures after `infer-union`

On `mega-11-10-2026-2235` sqlalchemy's suite fails four tests after `infer-union` and after no other
step: `test/sql/test_compare.py`'s `CacheKeyTest::test_cache_key`, and `CompareAndCopyTest`'s
`test_all_present`, `test_compare_labels` and `test_copy_internals`. They failed in that step on
`mega-10-29-2026-2241` and `mega-11-05-2026-0219` too, and passed in it on the seven mega runs since
2026-10-30 that aren't these, `mega-11-11-2026-1113` the latest, with 9, 13, 14 and 16 workers where
it failed with 10 and 11; they fail in it again on `mega-11-16-2026-1443`. Found 2026-11-11, and no
fix's: the suite's own order.
`test/sql/test_compare.py` registers `sqlite_foo` for `Insert` as it's imported
(`dml.Insert.argument_for("sqlite", "foo", None)`), in a registry the process shares, and
`test/sql/test_metadata.py`'s `DialectKWArgTest` clears that registry after each of its tests
(`Index._kw_registry.clear()`). Every worker imports both files to collect them, so a worker
pytest-xdist gives `test_metadata.py` before `test_compare.py` (`--dist loadfile`: by which is free)
refuses the argument in all four, as this run's one worker did: "Argument 'sqlite_foo' is not
accepted by dialect 'sqlite' on behalf of `Insert`", the message of 2026-11-05. On the checkout at
its tag, no fix applied, registering the argument, clearing the registry and building the statement
raises the same. In one process the suite's plugin sorts the tests, so `test_compare.py` always runs
first. It's the union's step each time because that one always runs: its tests stand for each fix's
where they're the released tests' (`suite_steps.union`), so the others ran only on the two of the
eight kept runs where its four failed. A fixed step's failures run again before they're called new
(`suite_steps.weighed`); the union's tests run once, so its report lists the four as new. Decided
2026-11-17: the four named in the catalog (`[corpus.sqlalchemy.suite.differs]`), with the
registry their order clears; the union's tests not run again. Built that day, by the names the runs
record them under; done when a mega run where they fail lists them apart, not as new (they passed
on `mega-11-17-2026-1924` and `mega-11-20-2026-1208`, so it's still to see). A quarter hour to read
the run that shows it; coverage unchanged.

#### 3. A run with no earlier run, held to the solver's shortest

A run whose steps are measured is at the solver's shortest, read against the waits the runner keeps
(`scripts/scratch/schedule_solve.py --given`): `alt-11-08-2026-1157` took 5.2 minutes to a proved
5.2 and `alt-11-08-2026-1213` 5.5 to 5.5 (16CPU/60GB; [COMPLETED.md](COMPLETED.md#corpus)). A first
run, none of its steps measured, isn't: `alt-11-08-2026-1133` took 7.2 to 6.0, its hinted steps
each holding a third of the run's memory (`sizing._UNSIZED_SHARE`) where trio's held 0.5 GB once
measured. Done when a first run of corpora no run measured takes within a tenth of its shortest:
`tests/corpus/runs/alt-fresh.toml` (the 8 alt corpora, 218 steps, 36 GB shared), its `output` a
folder no run has written. Each step below was approved the day it was built:

| Run                         | Took (min) | Proved shortest (min) | Over shortest (%) |
| --------------------------- | ---------: | --------------------: | ----------------: |
| `alt-first-11-17-2026-1623` |        7.6 |                   6.0 |                27 |
| `alt-fresh-11-17-2026-1912` |        7.0 |                   5.0 |                40 |
| `alt-fresh-11-20-2026-1800` |        7.4 |                   5.9 |                25 |

All on 16CPU/60GB, no step failed; each after, in turn, hinted steps sized by their servers'
measure, a fix or check by its corpus's bytes, and a suite's unmeasured tests on 2 CPUs. Built
2026-11-17: an unmeasured fix or check holds 0.3 GB and
450 bytes for each byte of the corpus's Python (250 for a check, the census or coverage), where it
held 1.25 GB for each of the run's jobs (`scripts/scratch/check_sizes.py`: fixes held up to 440 a
byte on the largest corpora); after it the released tests waited longest (`requests` 191 seconds,
`langchain-core` 184), each holding 8 CPUs and 8 GB for 0.7 to 1.4 used, and small steps 125 to 138
seconds behind them. Built 2026-11-20: a suite's tests no run has measured (`Plan._testing`) start
once `_STEP_CPUS` (2) are free, not half the machine's, and take as many more as are free then, a
worker each; measured ones, or ones whose record doesn't say how many workers ran, wait for half as
before. They then started within 8 to 24 seconds (`langchain-core`'s 140), but on 1 or 2 CPUs,
keeping those workers: trio's and urllib3's released tests took 71 seconds each on 1. The small
steps' waits moved to matplotlib's hinted steps, up to 225 seconds: they held 6.2 to 9.1 GB given
0.68 to 3.74. Built that evening, reversing 2026-11-17's decision not to count what a corpus
installs: an unmeasured hinted step holds its largest checker's fit (`tests/corpus/hinted_memory.py`:
a base, bytes for each byte of the corpus's Python, each server's again for basedpyright, and for
each byte of the packages its files import from its environment), `_MARGIN` over, where it held
that checker's server measure (`protocol.SERVERS`) and the corpus's check. Fitted to the 121 hinted
steps `mega-11-11-2026-1113` and `alt-fresh-11-20-2026-1800` asked afresh
(`scripts/scratch/hinted_sizes.py`): each held a median 0.9 to 1.0 of its fit, at most 1.8 to 2.7
(dask's, optuna's, pandas's), where the server measure gave a fifth to a tenth of the bytes for the
corpus's own files; imports add 0.02 to 0.04 GB a MB. matplotlib's three then estimate 4.9 to 6.7
GB. Read on `alt-fresh-11-20-2026-1845` (`3be4558`, 16CPU/60GB, no step failed): 6.8 minutes to a
proved 4.9, 39% over. Its hinted steps read their hints from the store the 18:00 run filled
(matplotlib's 3.5 to 3.7 GB in 96 to 102 seconds, from 6.2 to 9.1 in 123 to 169), so it doesn't test
the fit, and the runner has no way to ask afresh. What waited is CPUs, not memory: with small steps
waiting up to 133 seconds, all 16 CPUs were held and 16 GB free. So what's left is the order the
runner starts steps in against the solver's, on the same holds (3b), and a run file's way to ask
the checkers afresh, to read the fit on servers (3a). Not looked
into:
whether a step whose hints were read from the store should count as measured (on
`mega-11-11-2026-1113`, asked afresh after a run that read them from the store, pip's
`infer-basedpyright` held 4.1 GB given 0.64, and the run took 95 minutes for 80). Coverage unchanged.

#### 3a. A run file that asks the checkers afresh

A run's hinted steps read their hints from the store wherever an earlier run asked the same texts
(`constricter.cli.lsp.stored`), so their servers don't start: `alt-fresh-11-20-2026-1845`'s
matplotlib hinted steps held 3.5 to 3.7 GB where asking afresh they held 6.2 to 9.1, and no run
since `alt-fresh-11-20-2026-1800` can show whether the unmeasured hinted steps' fit
(`tests/corpus/hinted_memory.py`) holds on servers. Built 2026-11-22 (`28c1bb6`): `[steps]`'s
`infer-fresh = true` gives `--infer-fresh` to every step asking the checkers for hints, the union's and each fix's
second pass included, so none reads from or writes to the store; the run's facts and each hinted
step's `options` record it. Set in `tests/corpus/runs/alt-fresh.toml`, its `output` moved to a
folder no run has written (the old one holds the 18:45 run, which a run there would be planned
from). Done when an `alt-fresh` run with it (about 8 minutes on
16CPU/60GB) reads no round from the store (no hinted record has `stored`), and its hinted steps'
peaks set beside the fit (`scripts/scratch/hinted_sizes.py FOLDER`) fall within the 121 steps' range
it was fitted to (a median 0.9 to 1.0 of the fit, at most 2.7); or the fit is refitted with them.
Met on `alt-fresh-11-22-2026-1703` (`28c1bb6`, 16CPU/60GB): every hinted step's rounds `[0, 0]`,
its 24 peaks a median 0.92 of the fit, at most 1.90 (`scripts/scratch/hinted_sizes.py`).
Coverage unchanged.

#### 3b. A first run's start order against the solver's

With its memory sized, a first run waits on CPUs: on `alt-fresh-11-20-2026-1845` (16CPU/60GB) small
steps waited up to 133 seconds with all 16 CPUs held and 16 GB free, and the run took 6.8 minutes
where the solver, on the holds the runner gave each step (`scripts/scratch/schedule_solve.py
--given`), proved 4.9. The runner starts steps in the order `planning` solved before the run, from
what each took in earlier runs, an unmeasured step by its like corpora's median (`planning.like`);
of those that could start, the one ranked first, then the one lasting longest (`Slots.take`).

Found 2026-11-22 on that run (`scripts/scratch/schedule_solve.py --given --starts 15`, and
`scripts/scratch/start_order.py`, which replays a run's steps under the runner's holds in a given
order; seconds on 16CPU/60GB): its output held no earlier run, so nothing was ranked and every
step lasted 0, and the runner took them as their threads woke. The run ended on trio: its suite
runs in one process with no `at-once`, so its 7 fixed test runs go one after another on one
checkout, 32 seconds each on 1 CPU, and from 195 seconds to the end at 409 that line ran alone. It
started late: trio's `fix-unsafe` at 122 seconds where the schedule starts it at 0, its `traced` at
129 for 10. The solver's 4.9 is that line itself. Replayed (the run's own order 6.4 minutes against
6.8 recorded):

| Order                            | Trio as catalogued (min) | Trio 7 at once (min) |
| -------------------------------- | -----------------------: | -------------------: |
| As run                           |                      6.4 |                  4.2 |
| Longest line, measured           |                      4.8 |                  3.2 |
| Steps behind it                  |                      5.3 |                  3.7 |
| Corpus's set, then steps behind  |                      5.1 |                  4.2 |
| Solver's shortest (proved least) |                4.9 (4.9) |            3.2 (2.8) |

"Steps behind it" is what a first run knows: how many of its corpus's steps wait for a step, those
sharing its checkout counted one after another. Built that day (`28c1bb6`): of the steps
`planning` doesn't rank and as long as each other (none measured: 0), the one with the most behind it starts first
(`planning.behind`, `Slots.take`'s `after`), 8% over the shortest replayed; a measured run's order
is unchanged. Proposed, not built: trio's catalog entry given `at-once = 7`, as anyio's and pint's
have, its fixed test runs side by side on 7 checkouts: its line from 4.8 minutes to under 1, the
shortest to 3.2, and with this order 3.7 (16% over). Its tests are timing-sensitive (`--run-slow`),
so 7 beside the other steps may fail some that pass alone, which the reruns before a failure is
called new catch; 7 more checkouts to install. Done when a first run, its hinted steps asked afresh
(3a), takes within a tenth of its proved shortest: item 3's bar. Met on `alt-fresh-11-22-2026-1703`
(`28c1bb6`, 16CPU/60GB, no step failed): 8.0 minutes to a proved 7.7 (`schedule_solve.py --given`),
4% over; the shortest up from 4.9 with every hinted step's servers started. Coverage unchanged.

#### 4. The hinted steps' second pass

A run reports what a second pass would still fix after the certain fixes and the guesses
(`render._CONVERGING`). None is left since a module's stub is read in every check, but after a
checker's hints some long were; each is traced in one process with
`scripts/scratch/second_pass_copy.py` (a run's counts) and `scripts/scratch/hint_rounds.py` (each
round's hints and fixes in one file). Left after basedpyright's, ty's and pyrefly's hints:

| Run                    | basedpyright (fixes) | ty (fixes) | pyrefly (fixes) |
| ---------------------- | -------------------: | ---------: | --------------: |
| `mega-11-10-2026-1742` |                  102 |         76 |              84 |
| `mega-11-11-2026-1113` |                  142 |        116 |             227 |
| `mega-11-16-2026-1443` |                  138 |        108 |             197 |
| `mega-11-17-2026-1641` |                   17 |         20 |              27 |
| `mega-11-17-2026-1924` |                   12 |         11 |              28 |
| `mega-11-20-2026-1208` |                   12 |         20 |              26 |

Built 2026-11-17: with a checker's hints, as without, the files a round changed are indexed again
(`rounds.settled`'s `onward`), so the next round asks the checkers about every file and checks one
again where what it knows from outside changed; tested with a hint the fake server gives only once
another file annotates a name (`# once N: T`). matplotlib's, pandas's, pint's and most of pip's and
django's went then (matplotlib's `get_size_in_points` read from an index the round didn't rebuild;
17 of pandas's 28 a hint pyrefly gave only when asked again of the fixed tree). Each run since left
one of matplotlib's after pyrefly's hints, traced 2026-11-20: `fill_frames: str` in
`animation.py`, bound again to `_included_frames(...)`, which pyrefly types only once
`_animation_data.py`'s `INCLUDED_FRAMES: str` is written; a hint is refused while a later binding's
type is unknown (`rebinding`). A pyrefly server kept from round to round never typed that binding,
though its texts in the last round were the finished tree's, byte for byte; one started on that tree
did, and every text sent before any hint was asked changed nothing. pyrefly's alone (1.3.2), in one
process on 16CPU/60GB: on pip its servers kept left 32 (the 32 of `mega-11-16-2026-1443`), restarted
each round 0, 4,200 fixes from 4,168; ty's left 1 and basedpyright's 0 either way. Built that day:
a stale checker's servers (`Server.stale`, pyrefly's) are started anew for each round after their
first, as `--infer-in-turn` starts every checker's; matplotlib then leaves 0 (12,989 fixes), its
hinted fix 96s from 86s, pip's 21s from 18s (1 worker; a round read from the store starts no
server). Done when a mega run shows matplotlib's 0 after pyrefly's hints. Not looked into: the rest
of the 58 (the standard library's 4, 10 and 9, pip's 2, 7 and 3 the most), twisted's 12 of
`mega-11-16-2026-1443`, and what's as old as a corpus's first hinted run (the standard library's 39
after pyrefly's hints). A quarter hour to read the mega run. Coverage up by at most what a second
pass made after pyrefly's hints, 26 on `mega-11-20-2026-1208`.

### Medium: 4 to 8 hours

#### 6. Mutation testing

Line coverage is held at 100% (`fail_under`), so it no longer says which lines run without a test
checking what they do; a mutant the suite survives does. How: `mutmut` over `constricter/`, its
tests run without the corpus suites, in a `scripts/scratch/` script with its output under `local/`; triage
the survivors and write tests for those worth killing. Done when a full run's survivors are each
killed or recorded as equivalent. Written, not yet run: `scripts/scratch/mutation.py` (mutmut 3.8 on a
worktree of HEAD under `local/mutation/`, the unit tests alone, the lines they cover, `--only` for a
first pass). About 6 hours beside the run; coverage unchanged.

#### 7. A check's peak, past the resumed files

The standard library's check in one process (2026-10-24, 16CPU/60GB, `scripts/scratch/peak_rss.py`) peaked
at 2.65 GiB: every file's tree, and its whole finished check (scopes, bindings, inferences: 84,624
scopes), kept for a second round that resumes 242 of its 1,867 files. Both are now kept only for a
module with an open function, the only one a resume can start from (the others checked again, 33,
are parsed again), and a module's own node no longer keeps its tree in the shared walk: 2.03 GiB at
41.2s, from 40.5s, findings the same on the standard library, pydantic and pandas
(`scripts/scratch/equivalence.sh`). What's left, each weighed: no check kept at all, 1.97 GiB for 46.3s (the
resumed files start over); the index keeping only the resumable files' trees too, 2.00 GiB for 43.6s
(the peak is the index's end, 1.59 GiB of trees, and what the check frees is reused, not returned);
no tree kept anywhere, 3.43 GiB for 52.4s (each tree parsed again and the resumes lost). Also
weighed and left: `msgspec` or `orjson` for the pickled index, more `__slots__`, `sys.intern` of the
annotations' text. Measured by phase on 2026-10-24 (`scripts/scratch/peak_phases.py`, its memory sampled
each quarter second, one process beside a mega run, so its seconds don't count): the index ends at
1.59 GiB, the first check round at 2.00; with the index keeping no tree (`--no-index-trees`) the
index ends at 0.57 GiB, but the first round still reaches 2.02, with no resume kept. Of what the
first round allocates, 0.74 GiB is still held as it ends (`--trace-check`, tracemalloc): the index's
modules copied as each round links what its files return (`linked.with_returned`, 0.09), each file's
results and source text (0.10), the order's class edges (`loose.needs`, 0.06). The allocator isn't
what holds the rest: under `PYTHONMALLOC=malloc` with glibc's `malloc_trim` after each file's check
(`--trim`), which gives free pages back from anywhere, the peak is 2.19 GiB (2.20 untrimmed, 2.04
under pymalloc, 42s to 44s on a quiet 16CPU/60GB), so the memory is held, not freed. What holds it:
688 of the standard library's 1,862 modules (21 of its 35 MiB of source) have an open function and
keep their tree and whole first check for a resume, of which 242 resume. Under 1.5 GB then needs the
resume kept from less than the whole check (each function's scope rebuilt from its findings, the
tree parsed again), or kept only for a module some caller types a parameter of, known once its
callers are checked. Built on 2026-10-27, the latter's cheap half: a check is kept only for a module
whose open functions a checked file calls, itself included (`callers.resumable`, once for the index;
`Outside.resumable`), 556 of the standard library's 688 modules with one; its peak 2.06 GiB from
2.15 at 48s in one process on 16CPU/60GB (the tree after the day's changes: 2.15 where 2.03 was
measured on 10-24), the listing identical. What's left is the resume kept from less than the whole
check. Each timing here predates the changes since 2026-10-28: time it again first. About 6 hours;
coverage unchanged.

#### 8. A parallel check, past its longest chain

With every CPU the standard library checks in 13.5 and 13.9s and in 47.6s in one process
(2026-10-27, 16CPU/60GB), pandas in 11.3s and 50s; 29s in two processes, 18s in four, 13.7s and
12.9s in eight, so about 10s of each doesn't shorten with more (pandas's and the scaling timed
before a method's lookups were kept for a run: time them again first). It isn't the main process
(indexing, ordering and telling the workers take 2 to 3s) but the order: a file waits for those
whose unannotated functions it calls, 29 deep in the standard library, and pandas's 217 files that
call each other go round up to four times before the other 1,200 start. Most of those edges are by a
method's name alone (`loose.needs`: 12,704 of the standard library's, to 3,400 by an imported
function). Tried, and slower: a worker with nothing to do checking files ahead of their turn, each
confirmed when its turn came (16.0s from 14.4s: most are checked twice, and 25 of pandas's findings
then differed). Left to try: an edge only where the receiver's class is known to be the other
module's; and a file checked again from where its first check ended when what it imports returns
anew, as it is when its parameters are typed. Done when the standard library checks in under 9s with
every CPU, its findings the same. Measured 2026-10-23 (`scripts/scratch/order_edges.py`, the check order
rebuilt as `order.plan` builds it): the method-name edges make every long chain, pandas's 224 files
(39% of its bytes) and the standard library's 84, 6 and 14 without them; keeping one only where a
class the file names has the method keeps 9,155 of pandas's 9,182 and 13,024 of the standard
library's 13,091 (`import pkg` names every class of the package), and an edge by the receiver's
class at check time can't keep the output the same. With the method-name edges dropped from the
order the standard library checked in 11.4 and 11.6s on 2026-10-27, so the order holds 2s of the
13.5, and the other 8.5 over the 3s of CPU time shared out are the main process (the index, 2 to
3s), the workers' start and the largest files; the 9s bar isn't the order's to meet. Tried on
2026-10-27, and no faster: those edges dropped with workers, and the files calling a method by its
name checked again once the order was done, where what they import returned anew, then those reading
what changed. The standard library's findings were the same as the ordered check's and one
process's, but it took 13.3s against 13.4s with every CPU (16 workers, forked inside the sandbox, on
16CPU/60GB), and 13.0s with every file's check kept for a resume: the late rounds offered 1,255
files and checked 345 again, 2.4s, the order's 2s back, where 11 files' findings differ without the
edges. What's left of that path is a recheck only where a binding with no fix waited on the method
now known, which a check's results don't name: their reasons are kinds (`member`, `receiver`), not
the class and method. Each timing here predates the changes since 2026-10-28: time them again first.
About 8 hours; coverage unchanged.

### Measurement

#### 10. Two checkers' agreement, read again

A hint two checkers give alike is likely (`agreed+checker`): on `mega-11-06-2026-0441` it passed
[LIKELY.md](LIKELY.md)'s three bars, 97.9% of 9,149 told held and 8 of 10,081 read blamed (0.08 in
each 100). On `mega-11-11-2026-1113`, each checker reading the corpus's own settings and
environment, the suites' own checks blame 35 new errors on it, 14 on the run before (sphinx 7,
narwhals 5, httpx 4): the checkers agree more often, and on the same wrong name. On
`mega-11-16-2026-1443`, with a hint dropped where it names another thing than the file binds the
name to ([COMPLETED.md](COMPLETED.md#corpus)), they blame 20. Read on 2026-11-17
(`scripts/scratch/guess_report.py --from FOLDER --step infer-union`), it fails the blamed bar on both
later runs:

| Run                    | Guesses | Checked | Guesses blamed | Blamed per 100 |   Told | Held (%) |
| ---------------------- | ------: | ------: | -------------: | -------------: | -----: | -------: |
| `mega-11-06-2026-0441` |  14,445 |  10,081 |              8 |           0.08 |  9,149 |     97.9 |
| `mega-11-11-2026-1113` |  18,170 |  12,662 |             23 |           0.18 | 11,238 |     96.1 |
| `mega-11-16-2026-1443` |  18,144 |  12,659 |             17 |           0.13 | 11,226 |     96.1 |

The bars are 20 told, over 95% held and under 0.1 blamed per 100 checked. On the latest run the 17
blamed are spread over 11 corpora, narwhals' `default_col` three times (`_duckdb`, `_ibis`,
`_spark_like`), pandas' `creso_infer: int` in two tests; 5 fewer would pass the bar. Of the 436 a
traced value differed from, 318 are pandas's, about 230 of them a comparison's result hinted
`NotImplementedType` (`result = cat == cat`, a `Series` at run time), 33 on the 11-06 run: the
corpus's own environment gives both checkers the dunder's declared `NotImplementedType` arm. Without
them the held share would be about 98%. Decided 2026-11-17, both: `agreed` leaves the likely
fixes now; a checker's hint of `NotImplementedType` alone is refused (266 of the checkers'
differing hints on the latest run name it); and `agreed` is read again on the next mega run, to
come back once it passes all three bars (narwhals' three `default_col` blamed, if one cause, are
what keeps it over the blamed bar). Built that day: `agreed+checker` out of `offences.LIKELY`, and
`hinted._unimplemented` refusing a hint that's `NotImplementedType` alone; LIKELY.md, FIXES.md and
the changelog say so. Read on `mega-11-17-2026-1924` (`20d9297`, 79 minutes on 16CPU/60GB, no step
failed): `agreed+checker`, a guess, holds 98.4% of 10,968 told (from 96.1%; 177 differing, from
436, the `NotImplementedType` hints gone) but 17 of 12,390 checked are blamed, 0.14 in each 100, so
it stays out of the likely fixes; narwhals has 5 of the 17, pandas 3, litestar 2. The likely tier
holds 99.5% with 0.08 blamed, and the suites' new type errors are 710 as before, agreement's 20 now
a guess's. narwhals' five read 2026-11-18, two causes, neither the blamed fix's own. Four
(`default_col` in `_duckdb`, `_ibis` and `_spark_like`, `extra_kwargs` in `_polars/expr.py`) are
ty's hint `NO_DEFAULT: _NoDefault = _NoDefault.no_default` (`_utils.py:2232`, kind `checker`, no
error blamed on it): typed as its enum, the sentinel loses its literal, so pyright no longer
narrows `default is NO_DEFAULT` and reports the `default` each `replace_strict` passes on as still
possibly `Literal[_NoDefault.no_default]`; mypy narrows either way. Three more of ty's step's
errors, blamed on no fix (`_arrow/series.py`, `_dask/expr.py`, `expr.py`), are the same. The
fifth, `result: DataFrame | LazyFrame` (`_polars/namespace.py:172`), is mypy's on the next
statement's `pl.concat(..., how=_how)`, after `_how: str` (line 167, also `agreed+checker`) widened
a conditional of `Literal`s. An error is blamed on the fix at its line, not the one whose type it
names. Blamed on the hints that cause them, agreement keeps 13 of 12,390, 0.105 in each 100,
one over the bar. Two proposals, neither built: a hint refused that types a name bound to an enum
member as the enum (a sentinel `is` narrows against); and blame given to the fix whose name the
error's expression reads, where it isn't the line's. The first measured 2026-11-18 on
`mega-11-17-2026-1924` (`scripts/scratch/enum_sentinels.py`, seconds on 16CPU/60GB): 34 checker
hints type `NAME = E.member` as an enum `E` on 14 corpora, every one a single checker's (`checker`,
never `agreed`). 14 are a function's locals (black's `changed: Changed = Changed.NO`, rebound to
another member), where the enum is the right type. 20 are module constants bound once on 8 corpora
(websockets' 10 `Opcode`, `Side` and `State` members, attrs' `NOTHING`, dask's and xarray's
`no_default`, pytest's `HIDDEN_PARAM`, aiohttp's `sentinel` and two `WSMsgType`s), 17 compared
against somewhere. Only narwhals' brings errors: 8 in each of ty's and the union's steps, 7 naming
`Literal[_NoDefault.no_default]` and `extra_kwargs`', all pyright's. Of the other seven corpora
only websockets' suite runs a checker, mypy, which narrows by an enum-typed name too. Refusing a
module constant's hint bound once withdraws 20 fixes for narwhals' 8 in each step; a function's local isn't
a sentinel and keeps its hint. Decided 2026-11-18: such a constant declared `Final` rather than
refused, which pyright and mypy both keep the member's `Literal` for. Built that day
(`doubts.sentinel`): a module's constant its own scope binds once (`doubts.bound_once`: a class's
member of the same name, as websockets' `OPEN = State.OPEN`, isn't the module's), bound to a member
of an enum the module defines (`doubts.enums`: a class with a base named `...Enum` or `...Flag`, or
such a factory's call), hinted the enum, is declared `Final`, a guess resting on the hint, read as
the enum; an enum another module defines keeps its hint (aiohttp's two `WSMsgType`s). Measured the
same day, `_how`'s kind: a checker's `str` hint shown as string `Literal`s
(`scripts/scratch/literal_hints.py --store`, matching the hint store's texts, about two minutes on
16CPU/60GB) is 183 of the run's 3,218 checker `str` hints on 27 corpora (131 `agreed`), 65 passed to
a call in their scope, 97 told by a traced run and none differing; errors come from 2, nibabel's
`mode` (`memmap`'s `Literal` mode) and narwhals' `_how`, both `agreed`. Refusing them withdraws 183
fixes, or 65 if only those passed to a call, for those 2: not built. narwhals' `_time_unit`, `tu`
and `unit` are another kind, ty's `str` where the project's checker sees `Any`. Read on
`mega-11-20-2026-1208` (`9ffc314`, 78 minutes on 16CPU/60GB): with `Final` in, narwhals' new type
errors are 7 in ty's step and 12 in the union's, from 15 and 20, its fixes the same, and the
suites' 694 from 710; `agreed+checker` holds 98.4% of 10,983 told with 13 of 12,389 blamed, 0.105
per 100, one over the bar, as expected. Approved and built 2026-11-20 (`tests/corpus/blame.py`,
moved out of `corpus_suite`): an error naming the argument it's about (mypy's `Argument "how" to
"concat"` or `Argument 2 to "f"`, Pyright's `parameter "time_unit"`) is blamed, where a call on its
line passes that argument as a bare name, on that name's fix before it in its scope or the
module's, before the fix on its line; an argument that's an expression, follows an unpacking, or
isn't passed is blamed as before. narwhals' `_how` error then falls on `_how: str`, not `result`;
both are `agreed+checker`, so agreement's 13 blamed stand on that run. Left: agreement read again
on each mega run, with this blame, to come back once it passes, a quarter hour a run. Coverage
unchanged.

## On hold

### Waiting on a decision

#### 13. An opt-in code for a string literal used in an operation

An opt-in code, as `LVA012` to `LVA015` are: a string literal written as an operand (compared,
passed, subscripted with, joined) where it should be a name declared before it with a narrow type:
`ACTIVE: Final = "active"`, a `Literal["active"]`, an enum member. Wanted to keep a codebase's
strings named and typed once, as this project's own `Final` constants are. On hold for what to
decide first: which operations count (a comparison, a call's argument, a subscript, `+` and `%`, a
`return`), what's exempt (docstrings, annotations' strings, `__all__`, f-string parts, `""`), which
declarations satisfy it, and whether `--fix` makes the constant (it would have to name it) or the
code only reports. Done when the code reports, with `--explain`, the flake8, pylint and ruff wiring
and the README's rules table, and its count on the seven corpora and on constricter itself is in
COMPLETED.md. More than 8 hours: about 10 without a fix; coverage unchanged (a new code, not a fix).

## Later

### Large: more than 8 hours

#### 9. Types observed at run time, past what a parameter gives

`python -m constricter.trace` records what each binding of a function's locals held, by statement,
through pytest-xdist's workers and django's `runtests.py`, and `--infer-from` takes it
([done](COMPLETED.md#--fix)) only for a local a statement binds to a value taken from a parameter no
checker types, or from an attribute of `self` its class stores only such parameters in. Hints for
every local brought 32 new basedpyright errors with 127 fixes on pydantic (a checker types the value
wider than the run saw); under that rule none, and one fix there. Measured and not worth building:
the traced parameters' types as `callers`' seeds, for `--fix`'s own inference to type what's
computed from them (47 more fixes on pandas's `tests/frame/methods` and 125 more errors, a
parametrized `str` passed where pandas declares a `Literal`; a class's alone, 4 and 2). 79% of the
bindings with no fix are in functions with no annotations (in the 41 sampled directories, 13,992 of
28,931 are a method call, an attribute, a subscript or a copy of such a value). Left: no new error
at a traced binding. After the trace's fixes SQLAlchemy's mypy found 6 new errors and pandas's
checkers 3, three traced to a traced fix (`fk: ForeignKey`, passed where a `ForeignKeyConstraint` is
taken; `index: Index`; `loc: int`, then iterated): a local whose value a parameter gives, typed
narrower than its function uses it. On the mega corpora's suites they bring 4 more: 3 of pint's
(`quantity: Quantity` in `numpy_func.py`, "Class definition for "Quantity" depends on itself") and
one of altair's, blamed on a certain `call` fix (`normalized_engine: str`, `mimebundle.py`) that
brings none without the trace. Done when those aren't offered and none like them is left on the mega
corpora's suites. On the mega run of 2026-10-29 at 22:41 (`d160aa8`) 6 of the 462 new type errors
are a traced fix's, of 3,206 such fixes: `fk` and `index` as above, pint's 2, and nibabel's 2; `loc`
and altair's are gone. Built on 2026-10-30: a `@classmethod`'s first parameter is its class by any
name (`traced._receivers`), so nibabel's `file_map = klass.filespec_to_file_map(filename)`, declared
to return a `Mapping`, has no traced `dict[str, FileHolder]`: `mega-10-30-2026-0857` has 17 traced
fixes fewer on nibabel, each in a `@classmethod` whose first parameter is `klass`, and that error
gone, none new: 5 of its 461 new type errors are a traced fix's (`fk`, `index`, pint's 2, nibabel's
`value`); on `mega-11-05-2026-0219` the same 5 of 450. Read by position, a plain method's first
parameter would withdraw 9 of pygments' too, but a lexer's `analyse_text(text)` is made static by
its metaclass, so `text` is a value like any other's. About 10 hours; coverage down by the traced
fixes withdrawn. What's left, each a proposal, since it withdraws fixes; decided 2026-11-06, none
built for now, the first the one worth building:

- **A union the function's tests exhaust**: nibabel's `value: ast.Constant | ast.UnaryOp`
  (`ascconv._get_value`), which tests `isinstance` against each member and raises past them, so its
  last test is always true to mypy (`redundant-expr`). Refuse a traced union where the function
  tests the name against every member: of 36 traced unions without `None`, this one brought an
  error.
- **A class whose definition imports the fixed module**: pint's `quantity: Quantity`, imported for
  type checking into `numpy_func.py`, which `Quantity`'s own definition depends on through the numpy
  facet. Refuse an import added for a class whose module imports the fixed one; needs the index's
  import graph, and such cycles are common and mostly harmless.
- **A declared type the run contradicts**: sqlalchemy's `fk: ForeignKey`, right by the run, but
  passed to `skip_fn`, declared `Callable[[ForeignKeyConstraint], bool]` where the docstring says
  each `ForeignKey` is passed. Refusing it means checking a fix against the parameter it's passed
  to, as LVA009 checks a value against its annotation.
- `index: Index`, then `index.table`, a `Table | None` that `_verify_index_table` raises on, passed
  where a `FromClause` is declared: typing the local exposes what a body checked against `Any` let
  by, which no rule here avoids, as for a written return (the signature codes,
  [COMPLETED.md](COMPLETED.md#corpus)).

### To measure, some time

#### 11. Types from a model

Type4Py, TypeWriter, DLTPy, Typilus, HiTyper, TypeT5 and TypeGen predict types (TypyBench and
TypeEvalPy score them), but none is deterministic, and each needs a model or an API. Only as a file
`--infer-from` reads, through the hint filter and the witness, as any guess is. Done when one is
measured on pydantic against the checkers' hints: the fixes, the new errors. Not measured
2026-11-11, for want of a model: `type4py` isn't on PyPI (its model is a container's, or its hosted
API, which would be sent pydantic's source); HiTyper 1.0.3 installs, but its predictions are
Type4Py's, passed in, and what's left without them is static; TypeT5 is a checkout with torch and a
model to download, run on CPUs here. To decide first: which one, and whether a download of some
gigabytes or a hosted API is wanted for it. About 6 hours once one runs; coverage unknown until
measured.

### Ongoing

#### 12. Revisit the disabled rules

The [disabled rules](CONTRIBUTING.md#disabled-rules), as tools change (last checked 2026-11-22,
none to turn on: zizmor's `self-repository` still waits on actionlint, whose newest is still
1.7.12, rejecting `$/`; scorecard-action v2.6.0 (Scorecard 5.7.0) and zizmor 1.33.0 are out, the
repo on v2.5.0 and its batch's zizmor, and neither's notes touch the `$/` form; harden-runner's
block policy is proven in `build.yml`'s wheels, its run on `dev` of 2026-11-16 passing on every
macOS and Windows job; astroid 4.3.4, still the newest, ships no `py.typed`; fastjsonschema 2.22.3,
still the newest, ships one, locked, so mypy reads it, while basedpyright still allows it as
untyped, `validate`'s parameters being unannotated). About an hour a pass.

## Decisions

- `typeguard` only as an optional extra for `--check`: the package has no dependency (5, done).
- Weighed and left for a check's peak: `msgspec` or `orjson` for the pickled index, more
  `__slots__`, `sys.intern` of the annotations' text (7).
- Tried and dropped for a parallel check: a worker checking files ahead of their turn (slower), and
  the method-name edges dropped with late rechecks (no faster), both 2026-10-27 (8).
- Measured and not worth building: the traced parameters' types as `callers`' seeds (9).
- 2026-11-06: none of 9's four refusals built for now; the exhausted union first if any is (9).
  2026-11-17: kept so, the item moved to Later: 5 new errors in about 3,200 traced fixes.
- 2026-11-17: no model's types tried for now, the item in Later: none is deterministic, each needs a
  download of gigabytes or a hosted API sent the project's source, and the checkers' hints cover
  the ground; to revisit if those plateau (11).
- 2026-11-17: `agreed+checker` leaves the likely fixes, failing the blamed bar, until a run passes
  all three; a hint of `NotImplementedType` is refused (10).
- 2026-11-17: a first run's unmeasured hinted step isn't sized by its environment's packages:
  `Plan.fitted` corrects it as it runs (3). Reversed 2026-11-20, below.
- 2026-11-17: LVA016 stays a code; a cast that narrows a JSON document to the part a test uses is
  kept and marked `# noqa: LVA016`, not widened (5, done).
- 2026-11-17: the union step's tests aren't run again before their failures are called new: a
  suite's order-dependent tests are named in the catalog instead (2).
- 2026-11-18: a module constant bound once to a member of an enum the module defines, hinted the
  enum, is declared `Final` rather than its hint refused (10).
- 2026-11-18, measured and not built: refusing a checker's `str` hint shown as string `Literal`s,
  which withdraws 65 to 183 fixes for 2 errors (10).
- 2026-11-20: a stale checker's servers (pyrefly's) started anew each round; ty's and
  basedpyright's kept, their hints the same either way (4).
- 2026-11-20, approved: a suite's unmeasured tests start on a step's CPUs (3), and an error naming
  an argument is blamed on the fix of the name passed as it (10).
- 2026-11-20: an unmeasured hinted step is sized by a fit to measured peaks that counts what the
  corpus imports from its environment, kept apart from the servers' own measure, which caps a real
  server's heap (3).

## Done

In [COMPLETED.md](COMPLETED.md), what was built and measured, and [CHANGELOG.md](CHANGELOG.md), by
release.
