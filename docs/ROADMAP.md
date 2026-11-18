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

2026-11-17, at `1763d4b` (v0.4.6; `dev` and `main` alike).

- The latest run is `mega-11-16-2026-1443` (`39de5e3`, 97 minutes on 16CPU/60GB, no step failed, no
  server hung), read in [COMPLETED.md](COMPLETED.md#corpus): the suites' own checks find 710 new
  errors from 802, every one gone a hinted step's; 20 from 35 are blamed on a hint two checkers
  agree on. Every earlier run named here is read there too.
- What a run costs on 16CPU/60GB: the seven corpora's basic run 35 minutes
  (`basic-11-03-2026-2103`, [basic-corpora.md](runs/basic-corpora.md)), a mega run of all 55 80 to 97. A change to what `--fix` offers or refuses is read on all 55 in 12 to 14 minutes by
  `mega-fixes` (`tests/corpus/runs/mega-fixes.toml`: the fix steps and type checks alone, against the
  latest mega run's records with `scripts/scratch/run_fixes_diff.py`, or the latest `alt` run's for
  its eight; `mega-fixes-11-11-2026-1033`, 14 minutes), which measures none of the bars: a guess's
  bars and the tests still wait on a mega run.
- `agreed+checker` fails the blamed bar on `mega-11-16-2026-1443` (0.13 per 100 for under 0.1; held
  96.1%), read 2026-11-17 (10).
- Built 2026-11-17: an unmeasured hinted step sized by its servers' estimate (3); every file asked
  about again after a hinted round that changed one (4), which on `mega-11-17-2026-1641` leaves a
  second pass 17, 20 and 27 fixes from 138, 108 and 197, matplotlib's one after pyrefly's hints
  over its bar; `--check`'s `*args`, `**kwargs`, coroutine returns and module and class variables
  (5), the suite passing with 100% coverage. fastjsonschema 2.22.3 is locked, and mypy reads its types (12).
- Item 3's first `alt` run (16:23 to 16:31, 2026-11-17) took 7.6 minutes to a proved 6.0, short of
  its bar (3); the standard-library tables were regenerated at 16:25 during it, so its fix counts
  aren't compared with other runs'. The 3.14 suite passes (`tests/ci_local.py test`, 100%
  coverage) and Python 3.11's, synced with `--frozen` and its tests run
  with `SETUPTOOLS_USE_DISTUTILS=stdlib` as CI's; `tests/ci_local.py interpreters` fails here at
  `uv sync --locked`, which the global `exclude-newer` makes re-resolve.
- Not done or not run: a staged run with hours between its stages (1); the mutation run (6); the
  peak and parallel timings again, which predate 2026-10-28 (7, 8).
- Open questions from `mega-11-16-2026-1443`, not looked into: twisted's 12 left for a second pass
  after basedpyright's hints, where it left none (4); matplotlib's hinted steps' 99, 98 and 33 fewer
  fixes; nibabel's union step failing 2 tests from 1.
- Decided 2026-11-17, to build: `agreed` out of the likely fixes and `NotImplementedType` hints
  refused (10); an unmeasured fix or check sized by its corpus's files (3); the three wrong casts
  corrected, the ten JSON views marked `# noqa: LVA016`, LVA016 named as a code (5); sqlalchemy's
  four named in the catalog (2). Items 9 and 11 moved to Later.

## Order of work

- 2, 10 and 3 built 2026-11-17 (5 done): an `alt` run into a fresh folder for 3, then one mega run
  for 10, 2 and 4.
- 4: matplotlib's one fix left after pyrefly's hints, then done.
- 1: an hour beside the next super run, made in stages hours apart.
- 6: the mutation run, then its survivors.
- 7, then 8: memory and speed, last by this file's rule; each timed again first.

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

#### 3. A run with no earlier run, held to the solver's shortest

A run whose steps are measured is at the solver's shortest, read against the waits the runner keeps:
`alt-11-08-2026-1157` took 5.2 minutes to a proved 5.2 and `alt-11-08-2026-1213` 5.5 to 5.5
(16CPU/60GB; [COMPLETED.md](COMPLETED.md#corpus)). `alt-11-08-2026-1133` (`19a3e9c`), the first run
of its seven corpora, none of its steps measured, took 7.2 minutes to a proved 6.0, 20% over, though
planned by its like corpora (`planning.like`). Its 72 seconds went to memory at the head of the
run's longest chain: trio's `infer-basedpyright` waited 65 seconds wanting 6.6 GB with 3.2 free,
each unmeasured hinted step holding a third of the run's memory between its CPUs
(`sizing._UNSIZED_SHARE`), where trio's held 0.5 GB once measured. Built 2026-11-17, approved that
day: an unmeasured `infer-CHECKER` step holds its largest checker's servers for the corpus's files,
a server a CPU up to the checker's most, `_MARGIN` over, and the corpus's `check` where measured
(`Plan._servers`), then follows what it's seen to use (`Plan.fitted`) as before; a suite's type
checks and `infer-trace` keep the third. The estimate counts the corpus's files alone, where a
server loads what they import too: on `mega-11-16-2026-1443` a hinted step's peak was 0.3 to 8.6
times one server's estimate (`scripts/scratch/hinted_sizes.py`), the most dask's, matplotlib's and
pandas's (9.2, 8.5 and 6.6 GB). Done when a first run of corpora no run measured takes within a
tenth of its shortest (`scripts/scratch/schedule_solve.py --given`): the `alt` run into an output
folder of its own. Not met by the first, `alt-first-11-17-2026-1623` (8 corpora with matplotlib,
218 steps, 16CPU/60GB, its memory 36 GB): 7.6 minutes to a proved 6.0, 27% over, no step failed.
The hinted steps no longer wait for a third of the memory: given 0.5 to 2.2 GB, they waited 0 to
110 seconds behind other unmeasured steps, a fix's or a check's held at `_JOB_MEMORY` for each of
the run's 4 jobs (5 GB, 0.2 to 0.5 used) and a suite's released tests at 8 (0.5 to 1.2 used:
`requests` waited 244 seconds, `langchain-core` 265). matplotlib's hinted steps held 6.4 to 7.2 GB
given 0.68 to 1.87, so the run's steps held 36.6 GB at once. Decided 2026-11-17: an unmeasured fix
or check sized by the corpus's files rather than its jobs, by a ratio of bytes held to source bytes
read from earlier runs, to build; an unmeasured hinted step's estimate counting what the corpus's
environment installs, not built (`Plan.fitted` corrects it as the step runs). Built that day: an
unmeasured step that's no hinted step, type check or suite's tests holds 0.3 GB and 450 bytes for
each byte of the corpus's Python for a fix, 250 for a check, the census or coverage, where it held
1.25 GB for each of the run's `--jobs` (`scripts/scratch/check_sizes.py` on `mega-11-17-2026-1641`:
fixes held up to 440 a byte on the largest corpora, the rest under 300, every one at most 0.3 GB on
the smallest). Its `alt` run into a fresh folder, `alt-fresh-11-17-2026-1912` (16CPU/60GB, 36 GB
shared, no step failed): 7.0 minutes to a proved 5.0, from 7.6 to 6.0, and none of the run's memory
held past the model's. Each check and fix started on 0.32 to 0.87 GB, matplotlib's fixes on 3.45
(3.0 to 3.4 held). What waits now is CPUs, not memory: 64 steps waited 30 seconds or more, the
longest the released tests (`requests` 191 seconds, `langchain-core` 184), each holding 8 CPUs and
8 GB for 0.7 to 1.4 used, and small steps 125 to 138 seconds behind them. Its hinted steps read
their hints from the store, so they took 2 to 3 seconds where they asked afresh before. Left, a
proposal: a suite's unmeasured tests started on fewer CPUs, as a hinted step is. A measured step
can be as far off: on `mega-11-11-2026-1113` every checker was
asked afresh, each step sized by a run that read its hints from the store, so pip's
`infer-basedpyright` held 4.1 GB where it was given 0.64 and matplotlib's 8.8 where 4.28, the load
28 on 16 CPUs, and the run took 95 minutes for 80; no server passed its heap's cap. Not looked
into: whether a step whose hints were read from the store should count as measured. Coverage
unchanged.

#### 4. The hinted steps' second pass

A run reports what a second pass would still fix after the certain fixes and the guesses
(`render._CONVERGING`), where no corpus is left any since a module's stub is read in every check,
not after a checker's hints, where it has long left some: 102, 76 and 84 fixes after
`infer-basedpyright`, `infer-ty` and `infer-pyrefly` on `mega-11-10-2026-1742`, 142, 116 and 227
(180 after `infer-union`) on `mega-11-11-2026-1113`, the first with that and with each checker held
to the copy's own settings ([COMPLETED.md](COMPLETED.md#corpus)), and 138, 108 and 197 on
`mega-11-16-2026-1443`, twisted's 12 after basedpyright's hints among them where it left none. Found
2026-11-11 on the run between them, each in one process, which gives a run's counts
(`scripts/scratch/second_pass_copy.py`).
matplotlib's, the stub's apart, rest on one fix, `get_size_in_points: Callable[..., float] =
get_size` in `font_manager.py`: the files calling it know its type only from an index read after
that fix, and with a checker's hints the files a round changed weren't indexed again; it left 8, 11
and 9 on `mega-11-11-2026-1113`. pandas has no stub beside a source (its 41 are compiled modules').
Its 29 after pyrefly's hints were 25 with eight rounds for `HINT_ROUNDS`' four, so not the rounds'
cap: 17 of the 28 fixes are a hint pyrefly gives only when asked again of the fixed tree, where a
round asked again only of the files it changed, and 11 rest on a method's declared return or an
attribute of a name such a hint typed (`DataFrameGroupBy.filter`); measured before pyrefly read the
copy's own settings, it left 24, 24 and 28 on `mega-11-11-2026-1113`. Built 2026-11-17, approved
that day: with a checker's hints, as without, the files a round changed are indexed again
(`rounds.settled`'s `onward`), so the next round asks the checkers about every file and checks one
again where what it knows from outside, its hints among it, changed; tested with a hint the fake
server gives only once another file annotates a name (`# once N: T`). A server learns of a file
another server has open only from the disk, which no test here covers. Not looked into: pyrefly's
46 on pint, 32 on pip and 25 on django, none on the run before; twisted's 12; and what's as old as
a corpus's first hinted run (the standard library's 39 after pyrefly's hints, pint's 15 to 19 after
the others'). Done when a mega run (95 minutes on 16CPU/60GB) shows the hinted steps leaving
matplotlib and pandas no more than `mega-11-10-2026-1742` did (4, 6 and 0; 23, 21 and 25) and
pyrefly's new ones are traced. Read on `mega-11-17-2026-1641` (95 minutes on 16CPU/60GB, as the
last; no step failed, no test fails anew, the suites' new type errors 710 as on
`mega-11-16-2026-1443`): a second pass would still fix 17, 20 and 27 after the three checkers'
hints, from 138, 108 and 197; matplotlib 0, 0 and 1, pandas 0, 3 and 3, pint none, pip 2, 7 and 3,
django 3 after pyrefly's; the rest the standard library's 4, 10 and 9, celery's 6 and dask's 5 and 5
after basedpyright's and pyrefly's. The hinted steps fix 239,137, 234,050 and 247,770 (239,086,
234,001 and 247,682). Left: matplotlib's one after pyrefly's hints, the bar's 0, and the 72 left
in all, not looked into. Coverage unchanged.

### Small: under 4 hours

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
record them under; done when a mega run where they fail lists them apart, not as new. Coverage
unchanged.

### Medium: 4 to 8 hours

#### 5. Annotations held to a run

The corpora's witness holds each fix to the values its package's tests bind
(`tests/corpus/witness/constricter_witness.py`): of the certain fixes a test could tell of, 99.4%
hold on the mega corpora's suites, and what differs is a declared type the tests contradict or a
test's stand-in. The same check of a project's own annotations, as `python -m constricter.trace
--check`: each annotated local, parameter and return held to what a run binds, and those a value
differs from reported as an offence with the type seen. It needs the witness in the package (tested
as the tracer is), a container's elements held to its arguments, and a protocol's members looked for
where `isinstance` can't. `typeguard` does the last two, as an optional extra there: the package has
no dependency. Done when a traced run of this project's own tests reports no annotation of its own.
Built 2026-11-11 (`constricter/witness.py`, `--check` in `constricter/trace.py`): the corpus
witness's `holds` is the package's, a protocol `isinstance` can't check held to its members' names
without `typeguard`, and each annotated parameter, each local declared `name: T` at every
statement that binds it and each `return` is held, a name the module imports under
`if TYPE_CHECKING:` imported for its annotation; a differing binding is listed as LVA016, the
report's own code, and the run exits 1. This project's suite traced (`python -m constricter.trace
--check -m pytest -n 8`, 35 seconds on 16CPU/60GB) holds 17,998 annotated bindings: the 3 that
differed in the package are corrected (`workers`' context is whichever one starts workers, not
`DefaultContext`; `walked._Value` lacked a constant's `...`, `bytes` and `float`), 101 can't be
told, and 11 differ in the tests and the corpus tools, each a narrower cast than the value: a JSON
document read as the part a test uses (`_Sarif`, `_Nested`, `_Sources`, `_Group`, `_Written`), and
OR-Tools' status enum cast to `int` (`planning._solved`). Traced, 8 more of the suite's tests fail
than untraced, the tracer's own among them, not looked into. Built 2026-11-17: a `*args: T` held as
a `tuple[T, ...]`, a `**kwargs: T` as a `dict[str, T]`, an `Unpack` of either as the whole; a
coroutine's return where `sys.monitoring` tells it from a suspension (Python 3.12); and, as the run
ends, each recorded module's and its top-level classes' annotated variables, by what they hold
then (`Witness.judged`), not an instance attribute declared alone, a descriptor or an enum's
member. This project's suite traced again (2026-11-17, 33 seconds on 16CPU/60GB): 20,486
annotated bindings held, 13 differing, the 11 and two more narrow casts of the same kind (`tables`
in `checker_settings.py`, a `tool` table a test makes an `int`; `sdist` in `corpus_sources.py`, its
`requires` a list), none a module's or a class's variable. Its 42 failing tests were the tracer's
own, a recorded function returning a class whose `__module__` is `None` (`test_trace.py`'s `Odd`):
reading it raised into the run. Traced again with a return that can't be read dropping its
function, as a binding's does: 2 of the tracer's own tests fail traced (a run of `-m` and a pytest
process under the trace), and the package's one annotation a value differed from was
`recording.named`'s `module: str`, `None` there: such a class is now spelled unknown, and the
tests' class that can't be read raises as its module is asked for. Traced once more: 20,576
held, none of the package's differing, the 13 alone. Decided 2026-11-17: the three that are wrong
corrected (`planning._solved`, `sdist`, `tables`); the ten JSON documents read as the part a test
uses kept, each marked `# noqa: LVA016`, which the trace's report honours as a check does; and
LVA016 stays a code, named in `--explain` and the README's table. Built that day: `_solved` a
`frozenset[CpSolverStatus]`, `sdist` a `TypedDict` with its `requires`, `tables` any TOML value;
the ten marked; the report passes over a binding whose line has a `# noqa` covering LVA016 and
counts those (`witness.report`); `--explain LVA016` and the README's table name it. Done
2026-11-17: the suite traced (`python -m constricter.trace --check -m pytest -n 8`, 16CPU/60GB)
holds 20,528 annotated bindings, none differing, the 10 marked passed over; 2 of the tracer's own
tests fail traced, a trace inside a trace. To move to COMPLETED.md at the next groom.
About 4 hours; coverage unchanged: it finds wrong annotations, not missing ones.

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
the changelog say so. Left: the mega run (95 minutes on 16CPU/60GB), read for `agreed`'s bars.

## On hold

Nothing waits on a decision.

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

### Measurement

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

The [disabled rules](CONTRIBUTING.md#disabled-rules), as tools change (last checked 2026-11-17:
zizmor's `self-repository` still waits on actionlint, whose newest is still 1.7.12, rejecting `$/`
(scorecard-action v2.5.0 and zizmor 1.32.0 the newest); harden-runner's block policy is proven in
`build.yml`'s wheels, its run on `dev` of 2026-11-16 passing on every macOS and Windows job; astroid
4.3.4 still ships no `py.typed`; fastjsonschema 2.22.3 ships one, now locked, so mypy reads it
(`untyped_calls_exclude` drops it, `tests/cli/test_output.py` clean), while basedpyright still
allows it as untyped, `validate`'s parameters being unannotated). About an hour a pass.

## Decisions

- `typeguard` only as an optional extra for `--check`: the package has no dependency (5).
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
  `Plan.fitted` corrects it as it runs (3).
- 2026-11-17: LVA016 stays a code; a cast that narrows a JSON document to the part a test uses is
  kept and marked `# noqa: LVA016`, not widened (5).
- 2026-11-17: the union step's tests aren't run again before their failures are called new: a
  suite's order-dependent tests are named in the catalog instead (2).

## Done

In [COMPLETED.md](COMPLETED.md), what was built and measured, and [CHANGELOG.md](CHANGELOG.md), by
release.
