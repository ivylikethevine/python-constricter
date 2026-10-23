# Mega corpus run 0.4.3-rc.1

## Context

The machine is free for a mega run. Nine roadmap items under Next are built and wait on one (most
of "Built, waiting on a run", plus Medium 1, 2 and 6, Small 2 and 3, Measurement 3). Since the
0.4.0-rc.3 mega run (commit e8f67eb1e) the tree has added the unfixed reasons, generic members,
narrowed reads, the misplaced-hint fix and the witness's `IO` changes. Three runs go back to back,
at one commit, so that items needing a second run at the same tree close too:

1. `mega.toml --label 0.4.3-rc.1`: published as RUNS.md's Mega corpora section. Its rc.2 and rc.3
   runs took 91 and 105 minutes on this machine.
2. `mega-fast.toml`: the same commit again. Its first-round hints should come from the store the
   first run fills, and its timed tail gives the second timing at one commit. About 75 minutes:
   at 0.3.7-rc.1 it took 110 minutes to mega's 155 (its traced tests and released tests skipped).
3. `local/runs/mega-lva013.toml`: mega's corpora with `options = ["--extend-select", "LVA013"]`,
   not published, so the mega tables still compare with rc.3's. No `infer-with`, census, timing or
   traced tests: it only has to show LVA013's fixes and the suites after them. About 45 minutes.

## Preparation (Claude, once approved)

1. **Sync `local/.venv` to `uv.lock`.** It still has certifi 2026.7.22, virtualenv 21.14.5 and
   zizmor; the lock has certifi 2026.10.19 and virtualenv 21.14.12, and no zizmor. Run
   `UV_PROJECT_ENVIRONMENT=local/.venv uv sync --frozen --inexact --no-install-project --no-build --group dev --group corpus`.
   The checkers (basedpyright 1.40.2, ty 0.0.86, pyrefly 1.3.2) and ortools are already at the
   lock's pins.
2. **Reinstall the editable install** (`uv pip install --python local/.venv --no-deps --no-build-isolation -e .`).
   `constricter/_version.py` reads `0.4.3.dev11+g16360ffc8.d20261019`, and the run's `CHECKOUT`
   and RUNS.md header come from it. Afterwards it should read `0.4.3.dev34+g264d149`.
3. **`local/.venv/bin/python -m stdlib_tables --if-stale`**, so the tables match the tree.
4. **Check** that `pyvenv.cfg` still points at the source build with `test/`, that no `*.so` is under
   `constricter/`, that `git status` is clean, and that disk is free (105 GB; rc.3's folder is
   749 MB).
5. **Write `local/runs/mega-lva013.toml`** (from `mega-fast.toml`: label `mega-lva013`, the
   `options` above, `infer-with = []`, `census = false`, `timing = 0`, `profile = false`,
   `traced = false`, `tests-released = false`).
6. **Add a "Run log" section here** to hold the launch time, each run's folder, its end and its
   result as they happen.

## The user

- Optionally, first commit `local/corpus-runs/pandas-pyrefly-10-21-2026-1458` in the runs repo
  (it's untracked).
- Launch the chain from the repo root (sandboxed sessions can't). The runs are joined with `;`, so a
  run that exits 1 for something a fix broke doesn't stop the next one:

  ```sh
  ! setsid -f sh -c 'local/.venv/bin/python -m tests.corpus tests/corpus/runs/mega.toml --label 0.4.3-rc.1 > local/runs/mega-0.4.3-rc.1.out 2> local/runs/mega-0.4.3-rc.1.log; local/.venv/bin/python -m tests.corpus tests/corpus/runs/mega-fast.toml > local/runs/mega-fast-0.4.3-rc.1.out 2> local/runs/mega-fast-0.4.3-rc.1.log; local/.venv/bin/python -m tests.corpus local/runs/mega-lva013.toml > local/runs/mega-lva013.out 2> local/runs/mega-lva013.log' < /dev/null
  ```

## Watching

Background ticks of `scratch/run_tick.sh` (a step's traceback, a `problem:` line, a run's `.out`
filling) against each run's `.log`/`.out` in turn, and `scratch/run_eta.py` against rc.3's folder
for the ETA. An update goes out the moment each run ends, and every update ends with the ETA in
local time. A failed step is reported as soon as it fails.

## Afterwards: roadmap items, by what the runs decide

Closed by the runs alone, once read:

- **Built 4, Why a call has no fix**: done once mega's `census.md` has "Calls with no fix, by why".
  That then sizes Large 2 and 3 and the `vague = 0` run.
- **Measurement 3, Test results as data**: done if the records hold `tests-*.tests.jsonl` and the
  tests table reads sqlalchemy's skips by name.
- **Built 2, First-round hints from the store**: done if mega-fast's `infer-*` steps read their
  first round from the store and the hints match mega's. Mega itself misses the store, since
  `stored.key` hashes `connection.py` and `protocol.py`, both edited since rc.3.

Closed if the numbers clear the bar (about 1 to 3 hours of reading each):

- **Built 1, Eight mechanisms**: each kind counted, the guesses held to LIKELY.md's bars and the
  packages' checkers, and the suites the same after LVA013's fixes (the third run against mega's).
- **Medium 2, the witness**: done if the certain fixes that differ are only the 217 already read
  through.
- **Medium 1, What a hint breaks**: done if new errors are under 1 per 100 hint fixes on pandas,
  sqlalchemy (1.2 on rc.3) and pydantic.
- **Small 3, The timed tail**: done if mega's tail is under 5 minutes, with the noise read from mega
  and mega-fast at one commit (`scratch/timing_noise.py`).
- **Small 2, scheduling**: half of it, mega using 85% of its CPU seconds. The other half needs a run
  with no earlier run under its output, so it stays open.
- **Medium 6, the solver**: half of it, mega within a tenth of `scratch/schedule_solve.py`'s
  shortest schedule. A super run is still needed.

Not decided by these runs: Built 3 (a release's wheels), Small 1 and Medium 7 (CI), Medium 3, 4, 5,
8 and 9, Large 1 to 4, Measurement 1 (its own `vague = 0` run, next once Built 4 is read), 2 and 4.

Each result is written to its roadmap item as it's read: done items move to Done, and the cited
counts move from rc.3's to 0.4.3-rc.1's. After that, the run folders are committed to the runs repo
and RUNS.md's new section to `dev` (both by the user).

## Run log

Only the mega run for now; mega-fast and the LVA013 run wait for the go-ahead.
`local/runs/mega-lva013.toml` is written (21:0x) and parses with `run_config.read`.

- 2026-10-22 20:55: preparation done (certifi 2026.10.19 and virtualenv 21.14.12 synced, zizmor
  left in place by `--inexact`; the editable install reads `0.4.3.dev34+g264d149c7`; tables
  current, `test_tables_current` passes; no `*.so`; tree clean but this file). Mega started:
  `local/corpus-runs/0.4.3-rc.1-10-22-2026-2055`, progress in `local/runs/mega-0.4.3-rc.1.log`.
  ETA about 22:40 to 22:55. What wakes the session: a `scratch/watch_run.sh` tick on the folder and
  the log. When it ends: read `report.md`'s failures, then the items under "Afterwards".
- 22:10: the LVA013 run is queued behind mega: a detached shell polls every 30s for
  `local/runs/mega-0.4.3-rc.1.out` to fill, then runs `local/runs/mega-lva013.toml` (progress in
  `local/runs/mega-lva013.log`). If mega dies before writing its outputs, the shell waits forever
  and has to be killed by hand. Mega-fast is still held.
- 22:54: mega ended, 118 minutes, no failed step; it wrote `docs/RUNS.md`'s section. 151 problem
  lines: 145 "the tests differ after <fix>" on 21 suites (narwhals 972, optuna 279, strawberry 76,
  pydantic 65, pytest 47, ...), each the same count after every fix, and 3 "a second pass would
  still fix" (dask 3, textual 5). The test differences are the JUnit reader's ids, not the fixes:
  narwhals's released record (rc.3's, read from text) and its `tests-fix-certain` fail the same 972
  tests, but none of the ids match. `corpus_suite.junit_tests` takes the report's `file`, here
  `../../../../../python-constricter/local/corpus-suites/narwhals-v2.26.0-run0/tests/...`, so the
  classname's module isn't stripped:
  `<that path>::tests::dependencies::is_into_dataframe_test::test_is_into_dataframe[ibis]` against
  `tests/dependencies/is_into_dataframe_test.py::test_is_into_dataframe[ibis]`. RUNS.md's tests
  tables for this section are wrong until that's fixed and the tests are read again. The LVA013
  run started at 22:54 and its suite comparison has the same fault.
- Stopped the LVA013 run (its process group; nothing left). Fixed, uncommitted:
  - **JUnit ids** (`tests/corpus/corpus_suite.py`, `_located`): the report's `file` is the test
    function's own path, which pytest's cached rewritten modules (`*-pytest-9.1.1.pyc`) keep from
    when the checkouts lived elsewhere, and a base class's for an inherited method; the class name
    starts with the checkout's own path where pytest's rootdir is above it (nibabel, pygments). Ids
    are now relative to the checkout, from the class name. Against each suite's last report, 34 of
    the 40 with one match the released failures exactly; the rest differ only by the released
    records' spelling (rc.3's text: nibabel's rootdir prefix, strawberry's emoji prefix; this run's
    first JUnit read: litestar), plus black 1 and mcp 3 new failures to look at in the rerun.
  - **Reused records** (`corpus_suite.parser`): its hash didn't cover the JUnit reader, so rc.3's
    text-read released tests were reused; it does now, so the next run reruns the released tests.
  - **dask's second pass** (`constricter/fix/libraries/library.py`, `_imported`): a method on what
    a module bound by a call returns (`np = pytest.importorskip("numpy")`,
    `np.arange(24).reshape(4, 6)`) wasn't found until the `if TYPE_CHECKING:` import `--fix` adds
    for it was written. Now found in the first pass; dask's certain and unsafe fixes leave nothing.
  - **textual's second pass** (`constricter/fix/values/members.py`, `class_variable`): a class
    variable a generic base binds (`read1 = Read1` in `Parser(Generic[T])`) wasn't read through
    `self.read1` in a subclass given its arguments (`XTermParser(Parser[...])`). textual's unsafe
    fixes leave nothing.
  - **seaborn's undersized step** (`tests/corpus/sizing.py`, `before`): an implied part (one that
    read another's outcome in 0.2s) sized the step at 1 CPU and 0.04 GB; this run it ran the suite
    (560 CPU seconds, 4.9 GB). Implied records now size nothing, so the kind's largest part does.
  - Not changed: `ndarray.astype("f8")` is written `ndarray[tuple[int], dtype]`, a bare `dtype`,
    which LVA005 doesn't call vague either.
- Checked: the full suite passes (5,219 passed, 552 skipped, coverage 100%), and ruff, mypy,
  basedpyright, pylint and constricter's own check pass on the changed files. CHANGELOG has the
  three changes.
- Next: the fixes change the tree, so this run's section is for a tree that's gone. Commit, then
  rerun mega (it replaces the section) and the LVA013 run after it: about 120 and 50 minutes.
- 23:32: committed and pushed as aadbff0 (RUNS.md with the 22:54 section, which the rerun
  replaces). A first start was stopped after 8 seconds, as the editable install still read
  264d149; `local/corpus-runs/0.4.3-rc.1-10-22-2026-2332` is its partial folder, not a run.
  Reinstalled (`0.4.3.dev36+gaadbff007`) and started mega again, the LVA013 run chained after it:
  `local/corpus-runs/0.4.3-rc.1-10-22-2026-2332-2`, progress in `local/runs/mega-0.4.3-rc.1-b.log`;
  then `local/runs/mega-lva013-b.log`. ETA: mega about 01:30, LVA013 about 02:20. What wakes the
  session: a `scratch/watch_run.sh` tick on the folder and log.
- 2026-10-23 01:08: mega ended, 95 minutes on 16CPU/60GB (118 at 22:54), 1,190 steps, no failed
  step, no problem line: no suite's tests differ after a fix and no second pass finds more. It
  rewrote RUNS.md's Mega corpora section. Read so far:
  - Built 4 is done: `census.md` has "Calls with no fix, by why", 103,514 calls: `receiver`
    28,934, `member` 20,975, `imported` 18,601, `library` 11,562, `untyped` 7,919, `local`
    6,324, `declined` 5,597, `vague` 2,392, `other` 1,210.
  - Measurement 3, half: each part's `tests-*.tests.jsonl` is in the records (sqlalchemy's
    `tests-released` and `tests-infer-union`); the tests table still gives sqlalchemy's skips as
    a count (973), not by name, so that half is still to build.
  - Built 2 stays open: the `infer-*` steps asked anew in their first round (the store's key
    covers the edited `connection.py` and `protocol.py`); only later rounds, and `infer-union`'s
    reuse of each checker's rounds, came from the store. A mega-fast run at this commit settles it.
  - Not read yet: the witness's differing certain fixes (Medium 2), hinted errors per 100 fixes
    (Medium 1), each mechanism's counts against LIKELY.md's bars (Built 1), the timed tail and the
    CPU share (Small 3 and 2), the solver's bound (Medium 6).
- 01:08: the LVA013 run started (`local/corpus-runs/mega-lva013-10-23-2026-0108`), ETA 02:00.
- 01:44: the LVA013 run ended, 36 minutes, 523 steps, no failed step. Its suites' tests after each
  fix are the released tests' but for nibabel, whose 1 or 2 failures come and go both ways (its
  randomised quaternion tests): the LVA013 half of Built 1's done-when holds. New: `fix-unsafe`
  leaves fixes for a second pass on 22 of the 47 corpora with LVA013 selected (mypy 228, pdm 92,
  the standard library 68, sphinx 39, optuna 22, uvicorn 20, django 15, textual 13, twisted 12,
  litestar 12, sqlalchemy 11, httpx 9, tox 8, pytest 7, pandas 6, aiohttp 5, stripe 4, nibabel 3,
  mcp, streamlink and seaborn 2), none with `fix-certain` or `fix-likely`. Likely, not yet
  checked: an attribute LVA013's unsafe fix declares (`self.x: T`) makes reads of it fixable only
  on the next pass. Not read yet: that, and the type checkers' new errors after LVA013's fixes.
- 04:43: mega-fast started at aadbff0 (`local/corpus-runs/mega-fast-10-23-2026-0443`, progress in
  `local/runs/mega-fast-0.4.3-rc.1.log`), ETA about 06:00. What wakes the session: a
  `scratch/watch_run.sh` tick on the folder and log. When it ends: Built 2 (its `infer-*` records'
  `stored`), Small 3 (`scratch/timing_noise.py` on mega and mega-fast).
- LVA013's unsafe leftovers, confirmed on mypy (its unsafe patch applied to a copy, a second
  `--diff`): 190 lines, nearly all reads of `Options` attributes LVA013 declared in the first pass
  (`self.allow_redefinition: bool = False` in `options.py`, then `self.bind_all: bool =
options.allow_redefinition` in `binder.py`). Cause: `rounds.settled` indexes changed files again
  and checks the files reading them (`onward`) only with `--likely` alone (`Guesses.LIKELY`), so
  with `--unsafe-fixes` a guess one file declares reaches the others only on the next run. Fix,
  after mega-fast (the editable install is the run's code): let `onward` take `Guesses.ALL` too.
- Medium 2, the witness, read with `scratch/witness_diff.py` (rc.3's folder against mega's): 225
  certain fixes differ (rc.3 223), 191 bindings (189). Of rc.3's, 179 still differ and 10 don't
  (the 6 witness fixes, and 4 no test told of this time). 12 are new: 7 fixes rc.3 made the same
  and no test contradicted then (asyncio's `Transport` given uvloop's, sqlalchemy's `str` given
  `None`, ...), 4 new fixes of declarations the tests contradict (sphinx's `self.names` given
  `None` twice, starlette's `path_params: dict[str, str]` given `datetime` and `int`, xarray's
  `Mapping[str, TreeNode]` given an `int` by a test of its `TypeError`), and 1 wrong: narwhals's
  `impl = self.implementation` typed `_Implementation`, a descriptor whose `__get__` gives
  `Implementation`. Any descriptor annotated in a class body is read as itself through an
  instance, plain class or generic (a probe in the scratchpad: `plain: _Desc = self.impl`), so
  this predates the generic members, which only reached narwhals's. Not done: fix it after
  mega-fast (an annotated class variable whose class defines `__get__` is no fix through an
  instance), then the rest are declarations the tests contradict.
- Medium 1, what a hint breaks (`scratch/hint_errors.py`, rc.3's pandas 169 reproduced): 381 new
  errors (rc.3 458): pyrefly's 128, basedpyright's 110, ty's 107, the trace's 36; pandas 106, mypy
  80, narwhals 50, streamlink 24, sphinx 19. Per hundred hint fixes past `fix-unsafe`'s, every
  hinted step summed: pandas 0.54 (106 for 19,610), sqlalchemy 0.57 (12 for 2,092), pydantic 0.53
  (3 for 564), from 0.9, 1.2 and 0.5. Done.
- Built 1, each kind on mega's `fix-unsafe` (47 corpora, `tables/mechanisms.csv`) and held
  (`scratch/guess_report.py --from`, 42 packages): `text` 785 guesses, 136 told, 99.3% held, none
  blamed: passes. `comment` 31 certain (and 4 within guesses). `tested` 66 certain (and 17 within
  guesses). `filled` 575 likely and 580 guesses (`defaultdict` and `Counter` not told apart from
  the older fills). `named` 11 guesses, none in a traced package's told. `reads` 10 guesses, 5
  told, 2 held: too few for the bars, and under them. LVA013 (its own run against mega's): 4,521
  more `fix-likely` fixes and 5,093 more `fix-unsafe`, none `fix-certain`; the suites the same;
  6 new type errors (0.12 per hundred): pandas 5, all from `self.index: DatetimeIndex | None =
index` in `core/indexers/objects.py`, stored after `if not isinstance(index, DatetimeIndex):
raise` (the parameter's type, not the narrowed one); sqlalchemy 1, `self._dict:
util.PopulateDict`, a generic class bare (`type-arg`). Its guesses aren't held to a trace (its
  run had no traced step). Not done: LVA013's narrowed store and bare generic, a traced LVA013
  run, and `reads` and `named` are too few to read (whether they stay is the user's call).
- Small 2, the CPU share (`scratch/run_timeline.py`): mega used 76% of its CPU seconds (69,792 of
  91,728 in 96 minutes), under the 85% bar (0.4.0-rc.1 77.5%); the last 15 minutes ran at 8.2 and
  0.8 CPUs (the union steps, then the tail). Not done.
- Small 3, the timed tail: 6.2 minutes, the 47 timed steps one after another (rc.2's 5.3 read the
  same way), over the 5-minute bar. The checks got slower, not the tail: the timed steps sum to
  371s from rc.3's 334 (the standard library 62 to 73s, pandas 71 to 76s, dask 29 to 31s). The
  noise half waits for mega-fast's tail. Not done.
- Medium 6, the solver's bound: `scratch/schedule_solve.py` takes the machine's CPUs, so it runs
  after mega-fast.
- 04:50: mega-fast 58 steps in, no failure, ETA 05:46 to 06:00.
- 05:00: mega-fast 458 steps in, no failure, ETA 05:30 to 05:45.
- 05:10: mega-fast 736 steps in, no failure, ETA about 05:35.
- 05:20: mega-fast 869 steps in, no failure, ETA about 05:40.
- 05:30: mega-fast 912 steps in (its long hinted and suite steps), no failure, ETA 05:50 to 06:00.
- 05:40: mega-fast ended, 56 minutes, 1,040 steps, no failed step; its only problem lines are
  nibabel's tests (its randomised ones, 0 or 1 new). Read:
  - Built 2 is done: all 141 `infer-basedpyright`, `infer-ty` and `infer-pyrefly` steps read
    every round from the store, and each one's patch is byte for byte mega's.
  - Small 3, the noise at one commit (`scratch/timing_noise.py`, mega against mega-fast): seconds
    in one process a median 0.69% apart (largest 5.6%, hypercorn's 0.36s), with jobs 0.00% (3.9%);
    instructions 0.00% (1.1%) and 0.00% (2.4%). rc.2 against rc.3, a code change apart, was 4.3%
    and 7.6%. Mega-fast's tail 6.2 minutes, as mega's: the noise half holds, the 5 minutes don't.
  - Medium 6 (`scratch/schedule_solve.py`, 16 CPUs, 36 GB): mega 95.2 minutes, the solver's
    shortest 85.2 (proved at least 40.6), 11.7% over; held to what the runner gave each step,
    89.3, 6.6% over. Mega-fast 56.2 against 45.6, 23% over. Not done (the bar is a tenth, and a
    super run is still to come).
- The patch applied to the tree (`git apply`, index untouched); the worktrees removed. Full suite
  outside the sandbox (its `--jobs` tests need a unix socket): 5,222 passed, 552 skipped, coverage
  100%. ruff, mypy, basedpyright, pylint and constricter pass on the changed files. mypy's
  `fix-unsafe` at 3 jobs, before and after, one sample each: plain 5.1s and 4.9s, with LVA013
  7.2s and 6.5s, its second pass 190 lines and none: the rounds cost nothing measurable there.
- Meanwhile, in the same worktree (patch saved as `local/meanwhile/onward.patch`, both changes):
  LVA013's narrowed store. `recorded._recorded` types a stored or returned value as the tests
  before it leave it, through the scope's own `_tested` (`Scope.tested_read`), and keeps today's
  type where none narrows it; a test (`test_a_value_the_tests_narrow_is_stored_as_they_leave_it`)
  and a CHANGELOG line. Its test runs once mega-fast ends (a timed tail closes it).
- The descriptor fix's place: `members._declared` offers an attribute's annotation from
  `known.classes` as it is (`_attribute`). A descriptor's instance read is its class's `__get__`'s
  return (`known.methods`), and narwhals's `__get__` is overloaded (`None` gives the descriptor,
  an instance `Implementation`), so it needs the overloads read; where `__get__` can't be read,
  no fix is a narrowing, the user's call. Not started.
- LVA013's unsafe leftovers, fixed in a worktree (`local/worktrees/onward`, detached at aadbff0, so
  the run's editable install is untouched): `rounds.settled`'s `onward` takes any guesses
  (`is not Guesses.NONE`), its docstring, a test (`test_fix_unsafe_checks_again_what_reads_an_
attribute_another_file_declared`, failing on aadbff0) and a CHANGELOG line. mypy's copy, fixed
  with LVA013 by the worktree in one process, leaves a second pass nothing (190 lines before).
  After mega-fast: copy it into the tree, run the full suite and the linters, and time mypy's
  `fix-unsafe` before and after (the rounds took `fix-likely` to 1.47 to 1.84 times `fix-certain`).

## Verification

- After preparation: `local/.venv/bin/python -c "import constricter; print(constricter.__version__)"`
  shows `0.4.3.dev34+g264d149`, `pip list` matches the lock's certifi and virtualenv, and
  `pytest tests/fix/libraries/test_stdlib_tables.py::test_tables_current` passes.
- `local/.venv/bin/python -m tests.corpus local/runs/mega-lva013.toml --help`-free check: load the
  file with `run_config` (unknown keys error out) before the chain starts.
- Each run: `report.md` written and `runner.log` complete; mega's RUNS.md section is headed
  `0.4.3-rc.1` on commit 264d149.
