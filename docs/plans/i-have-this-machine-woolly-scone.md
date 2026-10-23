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

## Verification

- After preparation: `local/.venv/bin/python -c "import constricter; print(constricter.__version__)"`
  shows `0.4.3.dev34+g264d149`, `pip list` matches the lock's certifi and virtualenv, and
  `pytest tests/fix/libraries/test_stdlib_tables.py::test_tables_current` passes.
- `local/.venv/bin/python -m tests.corpus local/runs/mega-lva013.toml --help`-free check: load the
  file with `run_config` (unknown keys error out) before the chain starts.
- Each run: `report.md` written and `runner.log` complete; mega's RUNS.md section is headed
  `0.4.3-rc.1` on commit 264d149.
