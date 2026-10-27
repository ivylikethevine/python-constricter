# Roadmap

What's next. What's done, and what was measured on the way, is in [COMPLETED.md](COMPLETED.md).

## Next

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

### Built, waiting on a run

1. **Eight mechanisms, counted.** Built since the 0.4.0-rc.3 mega run, each with its tests:
   - **The text overload** (`text`, a guess): a standard-library function overloaded on `str`
     against `bytes` alone, with no argument's type known, takes its `str` signature's return
     (`os.path.join(root, name)` a `str`, `os.listdir(path)` a `list[str]`;
     `fix/libraries/overloads.py`). It reaches `os.path`'s 687 calls with no fix on the 47 corpora
     and `os`'s 246, about 0.3%; kept where the witness finds `bytes` under one in a hundred.
   - **An assignment's `# type:` comment as its fix** (`comment`, certain): with `type-comments`
     off, `x = v  # type: T` becomes `x: T = v`, and an unpacking's or a `with`'s names are declared
     before it, where `T` names only builtins and what the module binds (`rules/binding.py`). The
     census doesn't see comments; held to pip's modules without `__future__` imports keeping their
     comments' types.
   - **`defaultdict` and `Counter` through `filled`** (a guess): a local `Counter()`, or a
     `defaultdict` of `list`, `set`, `int`, `float` or `str`, typed by what its function adds at its
     keys (`fix/values/fills.py`). It reaches the 230 `collections.defaultdict(...)` calls with no
     fix, under 0.1%.
   - **Name consistency** (`named`, a guess): a parameter left unannotated with no default takes the
     one type the checked files annotate its name with, at least three times (`AGREED`), read
     through re-exports and never `Any` or `object` (`fix/index/consistent.py`). The names are
     concentrated (`result` 9,213, `expected` 3,609, `df` 663, `parser` 580 in the 2026-10-02 rows);
     kept if its sets pass [LIKELY.md](LIKELY.md)'s bars.
   - **A receiver by what's read of it** (`reads`, a guess): an unannotated parameter whose members
     read, two or more and no dunder, are all one class's, the module's own at its top level (a base
     where the classes under it have them too) or another checked file's, and not all of any builtin
     type's or standard-library class's; never one the function probes (`isinstance`, `hasattr`,
     `getattr`, `type`; `fix/values/reads.py`). 13,077 of the seven corpora's bindings with no fix
     copy, read a member of or call a method of an unannotated parameter: up to 5%. Kept where the
     witness agrees. Built on 2026-10-26: every class the file names is a candidate (another
     checked file's with its members typed or not, from the index's `bound`; an installed
     package's; a subclass's with its imported base's), and the standard library's where one class
     the tables hold is what every other with those members is under (`datetime.date` for `year`
     and `strftime`; not `pathlib.PurePath` for `stem` and `suffix`, which `zipfile.Path` has
     too), through an import added. On django (`scratch/signatures_measure.py django --modes unsafe
     --select LVA015`, one process on 16CPU/60GB): `--fix --unsafe-fixes` 5,428 from 5,408 with
     the tables' classes (+20 bindings), and with `--extend-select LVA015` 537 parameters typed
     from 525 with the index's members (+12); pydantic not measured. Left: the hold rate, read
     from the next mega run's witness (`reads` held 2 of 5 before); and the check's time, untimed
     since (`reads.members` keeps every module's attributes now, and each file's `Outside` carries
     the members of the classes it names: "The timed tail" named `reads.members` a hot spot).
     On the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step): `reads` 725 guesses, 21 told, 95.2% held, 44 of 450 read blamed (9.78 in each
     100); `named` 1,794, 6 told, 78 of 750 blamed (10.4): neither passes, both lose more than
     the index's members gained.
   - **Instance attributes, LVA013**: an attribute a plain class's method first stores unannotated,
     declared nowhere in the class (`rules/attributes.py`); opt-in as LVA012 is
     (`--extend-select LVA013`, pylint's `C9113`), an error from `strict` and counted by
     `--coverage` once selected. Its fix, a guess (`--likely` for a value of no guess of its own),
     writes the `assigned` type a read already takes (`self.count: int = 0`), or `T | None` for one
     stored `None` and else only a known `T`. 5,999 of the 47 corpora's bindings with no fix read a
     `self.x`, 1,660 of them in annotated functions; the stores themselves are offences of their
     own, outside the 252,637.

   - **Narrowed reads** (`tested`, certain): a name or attribute read where a test around it narrows
     its union is what the test leaves (`if self.conn is None: return`, then `conn = self.conn` a
     `Connection`; `isinstance`, truth tests, `not`, `and`, `or`), not past a store between the test
     and the read (`narrowed.narrowed_to`). Of the 13,972 bindings with no fix that copy a name or an
     attribute in a function, 424 follow a test of what they copy: `is None` (159), `isinstance`
     (148) or its truth (117), about 0.2%; held to the packages' checkers bringing no new error.

   - **The project's own generic classes** (`method` and `attribute`, certain; no kind of its own):
     a member of a checked file's generic class, its type parameters bound by the receiver's
     arguments (`rows.first()` on a `Result[Row]` a `Row | None`; `class C[T]`, `Generic[...]`, a
     subscripted base), through its generic bases and under a plain class given its arguments
     (`class Rows(Result[Row])`; `declarations.generic_members`, `members._own_generic`); another
     file's too, its bases not followed. sqlalchemy defines 101 generic classes (their subclasses
     included), pandas 30, pydantic 11: 75 bindings with no fix are a member of a name annotated
     with one, parameterised (74 of them sqlalchemy's), and 246 a member of `self` in one's own
     method (sqlalchemy 136, the standard library 77, pandas 30), about 0.1%. Left: `self` in the
     class's own methods is the class bare, so a member naming its parameters isn't typed there
     (it could be, written with the parameters, which the methods bind).

   Counted on the 0.4.3-rc.1 mega run (`tables/mechanisms.csv`, 47 corpora; held by
   `scratch/guess_report.py --from` on 42 packages): `text` 785 guesses, 136 a test told of, 99.3%
   held and none blamed for an error, so it passes; `comment` 31 certain; `tested` 66 certain;
   `filled` 575 likely and 580 guesses (`defaultdict` and `Counter` not told apart from the older
   fills); `named` 11 guesses, none told of; `reads` 10, 5 told of, 2 held. LVA013, in a run of its
   own beside it (`tests/corpus/runs/mega-lva013.toml`: mega's corpora with `--extend-select LVA013`, no
   hints, census, timing or traced tests; 36 minutes on 16CPU/60GB): 4,521 more `fix-likely` fixes
   and 5,093 more `fix-unsafe`, none certain; every suite's tests the same but nibabel's randomised
   ones; 6 new type errors (0.12 for each hundred fixes), pandas's 5 from `self.index` stored after
   a test narrowed it (typed as the tests leave it since) and sqlalchemy's
   `self._dict: util.PopulateDict`, a generic class written bare. Its `fix-unsafe` left a second
   pass something on 22 corpora (mypy 228 lines): a guess one file declared reached the other files'
   reads only on the next run, and is checked again in the same run since. A generic class without
   its arguments is no LVA013 fix since, as it's none for a binding (`attributes.unannotated`).
   Traced on 2026-10-23 (`tests/corpus/runs/mega-lva013.toml`: the uncommitted tree past `15167da`, 51
   minutes on 16CPU/60GB), held by
   `scratch/guess_report.py --from` on 42 packages: `assigned`, LVA013's kind, 4,703 guesses, 867 a
   test told of, 99.0% held and 2 blamed for an error (0.06 for each hundred), its set alone 3,147,
   134 told, 98.5% held and 1 blamed, so it passes [LIKELY.md](LIKELY.md)'s bars; `reads` 13, 5
   told, 2 held; `named` 6, none told. The two blamed: pydantic's
   `self.from_type: TypeForm[_FromTypeT]`, the method's own type variable, unbound where the
   attribute is declared; and werkzeug's `self.observer: Observer`, watchdog's `Observer` bound in
   its platform branches, which a checker reads as a variable (a local's constructor guess writes it
   too, `likely`). Its `fix-unsafe` left litestar 3 lines for a second pass, reads above the class
   whose attribute the file declared, which the run now checks again. sphinx's
   `test_html5_rubric` failed after `fix-likely`, both times, with a patch all but the earlier
   run's, which passed: it shares `markup-rubric`'s source directory with the man, LaTeX and texinfo
   tests on a pytest-xdist worker, and finds their pickled environment when one ran first there, so
   the directive's warning it asserts never comes (the suite's own order, a `differs` entry's to
   name). Left: whether an annotation naming a type variable, and a constructor guess of a name its
   installed module binds in branches, are no fix (each withdraws fixes). `named` and `reads` stay
   for now, though too few to read against the bars: on the 0.4.3-rc.5 mega run (`9892f71`) 49 and
   45 fixes over every fix step, as on rc.1, rc.7 and rc.8. They need more data before they're kept or dropped:
   more guesses a test tells of, from more corpora or a wider reach. Done when those are decided
   and a mega run covers the changes since. About 1 hour; coverage up to 6%, likely far less.

2. **Runs in stages.** Built in `88e0dda`: a run's steps fall into stages run one at a time into
   one folder (`tests/corpus/stages.py`): built in `fixes`, `traced`, `tests` and `timed`,
   regrouped by a run file's `[stages]` table. `--stage NAME` runs that stage's steps alone, a step
   needing a stage still to run left for it; the report is written from the records so far, naming
   the stages left, and published once every stage is in. A stage on another commit, other
   uncommitted changes or another run file than the folder's earlier stages is refused, naming
   both, unless `--join-anyway`, and the report then gives each stage's commit. Done when a super
   run made in four stages at separate times gives the report one sitting does. Coverage unchanged.
   The 0.4.3-rc.3 super run (`ac48774`, 16CPU/60GB) ran its four stages back to back into one
   folder: `fixes` 17 minutes, `traced` 15, `tests` 12, `timed` 4, 48 in all as rc.2's one sitting
   took; each joined, and the report and RUNS.md were written once the last was in. The 0.4.3-rc.4
   super run (`46bdc27`) ran them with 90s between: `fixes` 16.5 minutes, `traced` 11, `tests`
   20.5, `timed` 4, each exiting 0 and joining, the report naming one commit for all four. Left:
   stages hours apart, with other work between.

### Small: under 4 hours

1. **The timed tail.** The timed checks run last, alone and one at a time: three corpora at once on
   disjoint 5-CPU sets ran 4 to 5% slower in one process and 10 to 17% with jobs, their spread up
   from under 1% to 2 to 10% (`scratch/timed_tail_trial.py`), and with no warm-up the first run is
   within 0.8% of the rest, so hyperfine's `--warmup 1` is dropped. The 0.4.0-rc.2 mega run's tail
   took 5.3 minutes, from 10.5, and rc.3's 5.6 (4.4 for 46 corpora, pandas's 71s in a resume of its
   own). The instructions didn't move side by side (0.04 to 0.15%): the table could compare them
   across runs instead of seconds, which would free the tail to run beside other steps. The noise
   holds: the 0.4.3-rc.1 mega and mega-fast runs, at one commit, differ by a median 0.69% in seconds
   in one process and 0.00% with jobs, and 0.00% in instructions both ways
   (`scratch/timing_noise.py`; rc.2's and rc.3's, a code change apart, 4.3% and 7.6%). Their tails
   took 6.2 minutes each: the checks got slower, not the tail (the 47 timed steps sum to 371s, from
   rc.3's 334s: the standard library 62s to 73s, pandas 71s to 76s). Profiled on 2026-10-23 under
   `py-spy`, in one process on 16CPU/60GB (`scratch/profile_diff.py`): 54.3s at rc.3's `e8f67eb1e`,
   and the tree after it 65.5s under load but 52.4s on a quiet machine; what it added was
   `reads.members` (an `ast.walk` of every method of every class, each check and round), a
   function's body walked again for each parameter it might type, and `overloads._agreed`. Taken
   back, with the hot spots past them (one-process checks, the means of 3 on a quiet 16CPU/60GB,
   the same offences and fixes, `scratch/equivalence.sh`): the standard library 40.6s from 50.9s,
   pandas 46.9s from 57.5s. The 0.4.3-rc.3 super run's tail, a stage of its own, took 3.9 minutes,
   its 29 timed steps 210s (rc.2's 212s; the standard library 59s, pandas 65s), and rc.4's
   3.9 minutes too. Done when a mega
   run's tail is under 5 minutes with that noise unchanged (0.4.3-rc.5 mega run (`9892f71`, 16CPU/60GB, 82 minutes): 5.4 minutes, its 47 timed
   steps 326s, from rc.1's 6.2 and 371s; rc.6's and rc.7's the same, 5.4 and 327s; rc.8's 5.7 and 340s, its machine running other
   work). Built on 2026-10-26: `timing-beside` (a run file's `[steps]` key, set in `super.toml` and
   `mega.toml`) runs the timed checks beside the other steps, sized as measured, not alone at the
   end (`sizing.held_last`): their instructions compare across runs (0.00% noise with jobs, 0.04 to
   0.15% side by side), their seconds don't, which the timing table's `beside other steps` column
   and RUNS.md's intro say. Replayed on the super run of 2026-10-26 (`scratch/schedule_sim.py
   --timing-beside`, 16 CPUs and 36 GB): the runner's order 42.0 minutes from 43.5. Done when a
   mega run with it has no tail: its timed steps end with the rest. Done on the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step)): its 47 timed steps ran from 21:59 to 22:03 beside the suites, the run ending at
   22:58 with sqlalchemy's tests; the standard library's check took 682.4 G instructions in one
   process (rc.8's 588.8, +16%: the signature codes' work, since the run's options reach the timed
   check too). About 1 hour spent beside the run; coverage unchanged.
2. **Signatures from a sampled run.** RightTyper runs a package's tests
   (`python -m righttyper run -m pytest`) and annotates the parameters and returns of the functions
   they called, sampling with `sys.monitoring` at a fraction of a full trace's cost. The traced
   parameters' types as `callers`' seeds brought more errors than fixes (see the trace's item under
   Large), so what's new is the returns, written before `--fix` as `pyrefly infer`'s signatures
   were; its sampling is also a model for the next item. Measure on pydantic's and django's tests:
   the time against the `traced` step's, the fixes past the trace's, the new errors. Tried
   2026-10-21 (RightTyper 0.1.0 on pydantic 2.14.0's Python 3.14.7, one process on 16CPU/60GB):
   the run itself costs 17.7s against 9.8s plain (`tests/test_docs.py` left out: its 570 doc
   examples fail under RightTyper's `sys.monitoring` hooks), where the `traced` step took 84s on
   rc.3 for a 21s plain run; but it wrote no signature, crashing while reading pydantic's own
   annotations (a `ForwardRef` with no `__name__` on 3.14, patched past, then `ReprArgs`, a
   `TYPE_CHECKING`-only name, evaluated), and its post-processing wants a process pool (no
   `--no-use-multiprocessing` in `--help`). So the fixes and errors are unmeasured, and django
   wasn't run (its suite under RightTyper outruns a sandboxed call's 10 minutes). Next: a package
   whose annotations it can read (django's, which has none), or `--ignore-annotations` on pydantic
   with the overwritten signatures reverted. Measured on pydantic on 2026-10-24 (RightTyper 0.1.0,
   its only release since 2025-06, one process on 16CPU/60GB): `--ignore-annotations` on its
   tests (`tests/test_docs.py` and `tests/benchmarks` left out, `-W ignore::DeprecationWarning`
   since its own type lookups warn and pydantic's tests make warnings errors) ran 12,311 tests in
   25.9s, then crashed writing a test-local class's name (`<locals>.MyModel`; run past with that
   part dropped, from a patched copy). Of what it wrote, the 23 parameters and 22 returns pydantic
   left unannotated, in 16 files, were taken onto its own source (`scratch/righttyper_added.py`,
   the imports they need under `TYPE_CHECKING`): `--fix` made 3 more certain fixes (1,192 from
   1,191, `v1/main.py`; 2 others lost to the added imports), and `pyright pydantic` found 45 errors
   where it found none, the sampled types narrower than the functions take (`**kwargs: None`,
   `other: None` on `__or__`, `Self` in a metaclass). Not a corpus step on pydantic: more errors
   than fixes. Left: django, which annotates nothing (its suite under RightTyper in the background,
   one process), for whether the returns alone help where there are none. Done when django is
   measured too; a corpus step only if it brings more fixes than the trace for no more errors.
   Measured on django on 2026-10-26 (`scratch/righttyper_measure.py local/corpus-suites/django-5.2.18
   --source django --script tests/runtests.py --args=--parallel=1 --env
   DJANGO_SETTINGS_MODULE=test_sqlite`; RightTyper 0.1.0 patched three ways in the script's copy:
   a test-local class's name, a suite's nonzero exit before its post-processing, and its type
   finder reading a lazy object's class through `__getattribute__`, which raised while django's
   apps loaded; `--all-files`, since it records only the script's directory otherwise; one process
   on 16CPU/60GB): its whole suite, 18,191 tests in 336s, 31 erroring in RightTyper's hooks
   (`file_storage`, `migrations`) and 3 failing as under the tracer; 405 files annotated, 10,149
   parameters and 6,842 returns. Plain `--fix` on django then makes 4,293 certain fixes from
   2,622 (+1,697, 26 lost to the added imports), but basedpyright finds 12,879 errors where it
   found 4,007: 11,367 new (`reportArgumentType` 3,280, `reportUndefinedVariable` 3,127 from
   names it assumed imported, `reportAttributeAccessIssue` 1,442, `reportReturnType` 860), the
   sampled types too narrow (`bool | dict[Never, Never]` for a setting, `type[AppConfig] | None`
   for a class). Decided: not a corpus step, on django as on pydantic; the project's own tracer's
   returns ("Returns the trace records") are held to every way out of a function and bring none
   of this. Done; coverage unchanged.
3. **The runner's schedule, held to the solver's shortest.** Every corpus's steps wait for the
   machine alone, the one with the most seconds behind it first, and a running step's hold follows
   what it uses (`tests/corpus/sizing.py`): a step that can't start holds back none after it, a
   suite's measured tests hold the CPUs they kept busy with a margin over, an unmeasured part takes
   its kind's largest measured part, and an unmeasured `infer-union`, its checkers asked in turn,
   the largest checker's step's memory. `scratch/run_timeline.py` lays a run out from its records
   and `scratch/schedule_sim.py` replays it. The 0.4.0-rc.1 mega run took 134 minutes on 16CPU/60GB
   and used 77.5% of its CPU seconds (83.3% before its timed checks), within a tenth of the 123
   minutes no schedule of its steps goes under; with the union's steps 0.4.0-rc.2 took 91 minutes,
   and rc.3 105, its pandas steps resumed apart, so its share can't be read. The 0.4.3-rc.1 mega run
   took 95 minutes and used 76% (69,792 of 91,728 CPU seconds): its last 15 minutes ran at 8.2 and
   then 0.8 CPUs, the union's steps and then the timed tail. The 0.4.3-rc.3 super run, in stages,
   used 52% (23,773 of 46,106), rc.2's 54%: its steps waited 1,141 minutes in all for memory, the
   hinted steps of its first 15 minutes 8 to 16 minutes each. Replayed on 2026-10-24
   (`schedule_sim.py --sweep`, the rc.2 to rc.4 super runs on 16 CPUs and 29 GB, the memory rc.4's
   runner shared, no stages): the runner's order replays rc.4 in 38.5 minutes against its 51.8 in
   stages (pauses left out), so the stages' barriers, not the order, cost most; ordering by most CPU
   seconds with `_PATIENCE` 600s and `_BESIDE` 60s replays the three in 87.6 minutes summed, the
   runner's rules (300s, 300s) about 102. The rules order only the steps no run has measured, the
   planner the rest, so they're left as they are. No library runs subprocess steps in a graph under
   CPUs and memory as the runner does: Snakemake's scheduler comes nearest, choosing among its ready
   jobs as a knapsack, greedily or by PuLP's solver, but is a workflow engine whole, and Dask's and
   Ray's resources are their workers' Python tasks'. Where OR-Tools is installed, the runner plans
   its steps with CP-SAT before it starts (`tests/corpus/planning.py`: each step held to what the
   runner will hold for it, `sizing.Plan.wanted`, ports, each step after those it reads), and of the
   steps that could start, starts the one planned first; a step no run has measured keeps the rules
   (the longest chain first, `_PATIENCE`, backfilling). `scratch/schedule_solve.py` plans a finished
   run's steps the same way and proves how short any schedule of them can be: a mega run of 154
   minutes had a shortest schedule of 129 by the solver, 147 held to what the runner gave each, and
   a proved floor of 57. On the 0.4.3-rc.1 runs (16 CPUs and 36 GB to the solver), the mega run's
   95.2 minutes against a shortest 85.2 (11.7% over; 89.3 held to what the runner gave each step,
   6.6%), and mega-fast's 56.2 against 45.6 (23%). OR-Tools is in the `corpus` group, which CI's
   corpus setup installs, and `dev`. Read on 2026-10-24 (16 CPUs and 29 GB to the solver): the rc.2
   super run, in one sitting, 47.6 minutes against a shortest 47.7, its pandas `infer-union` of 630s
   the floor; rc.3 and rc.4, in stages, 47.7 and 51.8 (its 4.5 minutes of pauses left out) against
   30.5 and 35.7 with no stages, and 35.4 and 45.8 held to them (`schedule_solve.py --staged`): 35%
   and 13% over. A run in stages planned every stage's steps at once, ranking a stage's own by a
   schedule mixing them with the later stages'; on the 0.4.3-rc.5 mega run (`9892f71`, 16CPU/60GB, 82 minutes), in one sitting, 81.3 minutes against a
   shortest 66.0 with 36 GB (23% over; a proved floor of 41.6), stripe's one-CPU step its last.
   On the 0.4.3-rc.6 mega run (`c7f4db0`, 16CPU/60GB, 65 minutes): 64.3 against a shortest 55.6
   (16% over); rc.7 (`5674049`, 68 minutes) 67.7 against 57.9 (17%); rc.8 (`7a075e4`, 70 minutes,
   about 7 CPUs of other work at its start) 69.6 against 58.9 (18%); the super run of 2026-10-25
   (`1c29529`, 33 minutes, in one sitting) 33.2 against 27.0 (23%), all with 16 CPUs and 36 GB to
   the solver. A stage plans its own steps alone since
   (`planning.ranks`'s `chosen`); not yet run in stages. A run's share of its CPU seconds isn't the measure
   (85% was the target before): memory and the timed tail bound it whatever the order, and the
   0.4.0-rc.1 mega run, within a tenth of its floor, used 77.5%. Done when a super and a mega run
   each take within a tenth of the solver's shortest schedule of their own steps, and one with no
   earlier run under its output takes within a tenth of one sized by its own. Read on 2026-10-26
   (16 CPUs and 36 GB to the solver): the super run of 2026-10-26 (`b5f720c`, 42.1 minutes, in one
   sitting) against a solver's 43.2 in 60 seconds and 42.6 in 300 (proved at least 19.7): the run
   is at the shortest the solver finds, its waits memory's (`scratch/run_timeline.py`: its steps
   waited 3,791 minutes in all, the hinted steps holding 11 to 15 GB each). The timed tail was its
   last 2.5 minutes at under one CPU, gone with `timing-beside`. Done, for the super run, by the
   solver's measure; a mega run with `timing-beside` is still to read: the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step)) took 96.0 minutes by the solver's reading against a shortest 93.5 in 300 seconds (proved at
   least 56.0): within a tenth, as the super run. Done by the solver's measure for both; what's
   left is the third kind of run, one with no earlier run under its output. About 3 hours beside
   the runs; coverage unchanged.

### Medium: 4 to 8 hours

1. **CI's tools and security workflows, the shared way.** `security.yml` runs CodeQL and the weekly
   link check in jobs of its own, and every workflow that needs a binary (actionlint, gitleaks,
   lychee, twice) downloads it through `actions/tool` with the URL and sha256 written in the step,
   each a row of `check_tool_versions.local.sh`'s roster. The sibling repositories run the shared
   `codeql.yml` and `link-check.yml` instead, and install tools through the shared `setup-tool` and
   `setup-tools` actions from one roster beside them, `tools.txt` (name, version, archive type, URL
   template and checksum per tool), which `check_tool_versions.sh` reads on its own; the sync
   carries a workflow only where its actions already are, so this repository gets neither until the
   actions do. How: take the `setup-tool` and `setup-tools` actions and `apt/lib.sh` from the sync;
   write `tools.txt` with actionlint, gitleaks and lychee at today's pins; replace each
   `actions/tool` step (`ci.yml`'s offline lychee, `security.yml`'s three) with `setup-tools` and
   delete `actions/tool`; add `osv-scanner scan source --recursive .` to the Dependency audit job,
   from the shared roster's osv-scanner row and with `api.osv.dev:443` allowed, so it scans every
   lockfile as Scorecard's Vulnerabilities check does and `tests/ci_local.py` runs it before a push; drop the three rows from the local roster, keeping uv's; take `codeql.yml`
   (`language=python`) and `link-check.yml` from the sync and delete the `codeql` and `links` jobs
   from `security.yml`, which keeps zizmor, actionlint, the workflow conventions, pip-audit,
   dependency review and gitleaks; and re-read each job's `allowed-endpoints` from an audit run,
   since the download hosts move. The ruleset needs nothing: CodeQL is a code-scanning tool there,
   not a named check. Done when every workflow has one green run on a pull request, including a
   weekly `link-check.yml` by hand, `tool-versions.yml` reports the same four tools and osv-scanner
   from the new roster, the Dependency audit runs osv-scanner, and the sync has nothing left to send. About 5 hours; coverage unchanged.
2. **A check's peak, past the resumed files.** The standard library's check in one process
   (2026-10-24, 16CPU/60GB, `scratch/peak_rss.py`) peaked at 2.65 GiB: every file's tree, and its
   whole finished check (scopes, bindings, inferences: 84,624 scopes), kept for a second round that
   resumes 242 of its 1,867 files. Both are now kept only for a module with an open function, the
   only one a resume can start from (the others checked again, 33, are parsed again), and a module's
   own node no longer keeps its tree in the shared walk: 2.03 GiB at 41.2s, from 40.5s, findings the
   same on the standard library, pydantic and pandas (`scratch/equivalence.sh`). What's left, each
   weighed: no check kept at all, 1.97 GiB for 46.3s (the resumed files start over); the index
   keeping only the resumable files' trees too, 2.00 GiB for 43.6s (the peak is the index's end,
   1.59 GiB of trees, and what the check frees is reused, not returned); no tree kept anywhere,
   3.43 GiB for 52.4s (each tree parsed again and the resumes lost). Under 1.5 GB needs a resume
   from less than the whole check (its functions' scopes rebuilt from their findings), or the
   index's records without its trees. Also weighed and left: `msgspec` or `orjson` for the pickled
   index, more `__slots__`, `sys.intern` of the annotations' text. Measured by phase on 2026-10-24
   (`scratch/peak_phases.py`, its memory sampled each quarter second, one process beside a mega
   run, so its seconds don't count): the index ends at 1.59 GiB, the first check round at 2.00;
   with the index keeping no tree (`--no-index-trees`) the index ends at 0.57 GiB, but the first
   round still reaches 2.02, with no resume kept. Of what the first round allocates, 0.74 GiB is
   still held as it ends (`--trace-check`, tracemalloc): the index's modules copied as each round
   links what its files return (`linked.with_returned`, 0.09), each file's results and source
   text (0.10), the order's class edges (`loose.needs`, 0.06). The allocator isn't what holds
   the rest: under `PYTHONMALLOC=malloc` with glibc's `malloc_trim` after each file's check
   (`--trim`), which gives free pages back from anywhere, the peak is 2.19 GiB (2.20 untrimmed,
   2.04 under pymalloc, 42s to 44s on a quiet 16CPU/60GB), so the memory is held, not freed. What
   holds it: 688 of the standard library's 1,862 modules (21 of its 35 MiB of source) have an
   open function and keep their tree and whole first check for a resume, of which 242 resume.
   Under 1.5 GB then needs the resume kept from less than the whole check (each function's
   scope rebuilt from its findings, the tree parsed again), or kept only for a module some
   caller types a parameter of, known once its callers are checked. About 6 hours; coverage
   unchanged.
3. **Mutation testing.** Line coverage is held at 100% (`fail_under`), so it no longer says which
   lines run without a test checking what they do; a mutant the suite survives does. How: `mutmut`
   over `constricter/`, its tests run without the corpus suites, in a `scratch/` script with its
   output under `local/`; triage the survivors and write tests for those worth killing. Done when
   a full run's survivors are each killed or recorded as equivalent. Written, not yet run:
   `scratch/mutation.py` (mutmut 3.8 on a worktree of HEAD under `local/mutation/`, the unit tests
   alone, the lines they cover, `--only` for a first pass). About 6 hours beside the run; coverage
   unchanged.
4. **A parallel check, past its longest chain.** With every CPU the standard library checks in 12.9s
   and pandas in 11.3s: 46s and 50s in one process, 29s in two, 18s in four, 13.7s and 12.9s in
   eight, so about 10s of each doesn't shorten with more (timed before a method's lookups were kept
   for a run, which took one process from 53.7s to 43.0s on the standard library and 61.8s to 53.5s
   on pandas, 16CPU/60GB: time it again first). It isn't the main process (indexing, ordering and
   telling the workers take 2 to 3s) but the order: a file waits for those whose unannotated
   functions it calls, 29 deep in the standard library, and pandas's 217 files that call each other
   go round up to four times before the other 1,200 start. Most of those edges are by a method's
   name alone (`loose.needs`: 12,704 of the standard library's, to 3,400 by an imported function).
   Tried, and slower: a worker with nothing to do checking files ahead of their turn, each confirmed
   when its turn came (16.0s from 14.4s: most are checked twice, and 25 of pandas's findings then
   differed). Left to try: an edge only where the receiver's class is known to be the other
   module's; and a file checked again from where its first check ended when what it imports returns
   anew, as it is when its parameters are typed. Done when the standard library checks in under 9s
   with every CPU, its findings the same. About 8 hours; coverage unchanged. Measured 2026-10-23
   (`scratch/order_edges.py`, the check order rebuilt as `order.plan` builds it): the method-name
   edges make every long chain, pandas's 224 files (39% of its bytes) and the standard library's 84,
   6 and 14 without them; keeping one only where a class the file names has the method keeps 9,155
   of pandas's 9,182 and 13,024 of the standard library's 13,091 (`import pkg` names every class of
   the package), and an edge by the receiver's class at check time can't keep the output the same.

### Large: more than 8 hours

1. **Types observed at run time, past what a parameter gives.** `python -m constricter.trace`
   records what each binding of a function's locals held, by statement, through pytest-xdist's
   workers and django's `runtests.py`, and `--infer-from` takes it ([done](COMPLETED.md#--fix)) only for a local
   a statement binds to a value taken from a parameter no checker types, or from an attribute of
   `self` its class stores only such parameters in. Hints for every local brought 32 new
   basedpyright errors with 127 fixes on pydantic (a checker types the value wider than the run
   saw); under that rule none, and one fix there. Measured and not worth building: the traced
   parameters' types as `callers`' seeds, for `--fix`'s own inference to type what's computed from
   them (47 more fixes on pandas's `tests/frame/methods` and 125 more errors, a parametrized `str`
   passed where pandas declares a `Literal`; a class's alone, 4 and 2). 79% of the bindings with no
   fix are in functions with no annotations (in the 41 sampled directories, 13,992 of 28,931 are a
   method call, an attribute, a subscript or a copy of such a value). Left: no new error at a traced
   binding. After the trace's fixes SQLAlchemy's mypy found 6 new errors and pandas's checkers 3,
   three traced to a traced fix (`fk: ForeignKey`, passed where a `ForeignKeyConstraint` is taken;
   `index: Index`; `loc: int`, then iterated): a local whose value a parameter gives, typed narrower
   than its function uses it. On the mega corpora's suites they bring 4 more: 3 of pint's
   (`quantity: Quantity` in `numpy_func.py`, "Class definition for "Quantity" depends on itself")
   and one of altair's, blamed on a certain `call` fix (`normalized_engine: str`, `mimebundle.py`)
   that brings none without the trace. Done when those aren't offered and none like them is left on
   the mega corpora's suites. About 10 hours; coverage down by the traced fixes withdrawn.
2. **Signatures from the project's own inference.** `returned` decides a function's return where its
   `return`s agree, `callers` an unannotated parameter every call passes one type and `fixture` a
   test's, but each types only the locals bound to them: no edit writes `-> T` on the def or `: T`
   on the parameter (`Edit` has `annotate`, `replace` and `declare`). `pyrefly infer` and
   `dmypy suggest` were measured for signatures ([done](COMPLETED.md#corpus)), never constricter's own certain
   returns written back, which turn every caller's `returned` guess in other files into a certain
   fix and give ruff's ANN201 a fix it lacks. An edit kind for the signature: `-> T` where the
   function's `return`s decide one type (a method's a guess: a subclass may return another),
   `-> None` where none returns a value, a parameter's by `callers` and `fixture` as the guesses
   they are; opt-in codes, as LVA012 is, since ruff's ANN reports the offences already. Done when
   the corpora's own type checkers find no new error after the returns alone, and `--fix` on pandas
   gains the callers' fixes the written returns make certain. Built in part, not yet run: LVA014 (opt-in), a plain
   function's or method's missing return type, its fix `-> T` before the header's `:` (`Edit.SIGNATURE`,
   `rules/returning.py`) from `returned`'s types or `None`; the parameters (`callers`, `fixture`)
   still to do ([the signatures plan](plans/signatures.md) has the rest). On pydantic (2026-10-24,
   `--fix --unsafe-fixes --extend-select LVA014`): 34 functions reported, 31 fixed (29 `-> None`, 2
   `-> str`; 29 of them methods' guesses), the other 1,596 fixes the same, `pyright pydantic` 0
   errors as without, and its 12,311 tests passing. Built on 2026-10-26: LVA015 (opt-in), a
   parameter's `: T` from what typed it for the function's own check (`callers`, `reads`,
   `fixture`, `named`; `rules/parameters.py`), a guess resting on that mechanism; LVA014's fix a
   guess where the `return`s' values are guessed (`return Box()`), resting on their kinds, which
   `--likely` and `unsafe-fix-select` weigh (before, a module function's was written certain:
   `_lazy_re_compile`'s `-> SimpleLazyObject`, a `constructor`); and a signature written reaches
   the other files in the same run (`rounds._reaching`: the file indexed again, its callers
   checked again), so what a declared return makes certain needs no second pass. Measured on
   django (`scratch/signatures_measure.py django --select LVA014,LVA015 --modes
   certain,likely,unsafe,signed`: a copy fixed pass after pass until a pass fixes nothing, one
   process on 16CPU/60GB, 6 to 21s a pass; `--coverage`'s first bindings, of 17,181):

   | Mode                                                 | Plain | With the codes | Signatures written |
   | ---------------------------------------------------- | ----: | -------------: | -----------------: |
   | `--fix`                                              | 2,627 |          2,637 |                247 |
   | `--fix --likely`                                     | 3,273 |          3,414 |                557 |
   | `--fix --unsafe-fixes`                               | 5,413 |          5,460 |              3,476 + 605 |
   | `--fix --unsafe-fixes --select LVA014,LVA015`, then `--fix` |     — |          2,956 |              3,467 + 467 |

   The last row is the workflow the codes are for: the signatures written first (every guess among
   them, 3,467 returns and 467 parameters, in one pass of 21s), plain `--fix` then types 2,956,
   329 more than without them (12.5% of its fixes), and a second pass finds nothing. `--likely`
   gains 141 since LVA014's guesses carry their `return`s' kinds (`constructor+returned`, a likely
   set). Before the guess fix, `--fix` with LVA014 gave 2,737: 100 of them from a guessed return
   written as certain. Left: under `--unsafe-fixes` 138 of the parameter fixes come only on a
   second pass (a guess written on a caller's argument is a known type for `callers` on the next
   pass: the second row's pass 2 to 4, 150 fixes), which a recheck after writing guesses would
   bring in (`rounds._unsettled` does it with `--likely` alone); and LVA015's reach is the seeds',
   1 of `--unsafe-fixes`' 5,408 binding fixes on django resting on one before the codes. The
   roadmap's 10 hours spent; coverage: `--fix` +12.5% on django after a signatures pass, the
   `--unsafe-fixes` row under 1%. On the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step): bindings typed, of 474,291, `--fix` 161,191 from 161,134, `--likely` 211,563 from
   210,156, `--unsafe-fixes` 229,556 from 227,933; but the new type errors 54,366 from the
   0.4.3-rc.8 mega run's 403 (`--fix` 1,145 from 1, pandas 1,002; 25,063 untraced to a line
   with a fix, a signature written in another file), and the witness blames 893 certain fixes of
   49,840 checked (1.79 in each 100; 1 of 42,073 before): a return written on the def constrains
   every caller and every override where a local's annotation constrained one binding, and mypy's
   incomplete-def check fires on sqlalchemy where a return is written on a function whose
   parameters stay bare. The signatures-first workflow stands for a project that reviews them;
   as a step of the fix runs they fail the bars, so the run files select them no more (the same
   day). Built the same day: a signature written whole or not at all (`rules/signatures.py`), a
   function's fixes held back until every parameter but its receiver and its return are annotated
   or fixed, which was most of the errors blamed on `reads` and `named` (mypy's incomplete-def
   check, overrides); what a return alone exposes in a body mypy didn't check (pandas's tests,
   `check_untyped_defs = false` there) no rule here avoids. Under it, django's signatures-first
   workflow writes 931 returns and 81 parameters (from 3,467 and 467), and `--fix` then types
   2,749 bindings from 2,627 (+122, from +329). Left: the codes' errors read on a run with them
   again, if they're to go back into one.
3. **A method's `return` of an untyped value.** Of the 11,959 `self.method()` bindings with no fix,
   5,617 call a method the class doesn't define itself, and 5,436 one whose `return` gives a value
   `--fix` can't type: a tuple (1,858), a call (1,455), a local or another name (1,396), a subscript
   or attribute (272). Only 137 return an unannotated parameter (26 nothing else), and in none of
   those classes does every `self.method(...)` call pass it a literal: typing a method's parameters
   by its callers, as `callers` types a plain top-level function's (3 fixes on pandas), reaches
   almost none of them. What's left is the values themselves: the tuple's parts, the call, the
   local. Done when a method returning its parameter types its calls. About 14 hours, for about 0.3%
   (some 800 guesses).
4. **Annotations held to a run.** The corpora's witness holds each fix to the values its package's
   tests bind (`tests/corpus/witness/constricter_witness.py`): of the certain fixes a test could
   tell of, 99.4% hold on the mega corpora's suites, and what differs is a declared type the tests
   contradict or a test's stand-in. The same check of a project's own annotations, as
   `python -m constricter.trace --check`: each annotated local, parameter and return held to what a
   run binds, and those a value differs from reported as an offence with the type seen. It needs the
   witness in the package (tested as the tracer is), a container's elements held to its arguments,
   and a protocol's members looked for where `isinstance` can't. `typeguard` does the last two, as
   an optional extra there: the package has no dependency. Done when a traced run of this project's
   own tests reports no annotation of its own. About 14 hours; coverage unchanged: it finds wrong
   annotations, not missing ones.

### Measurement

What to measure before building, smallest first.

1. **A `vague = 0` run.** The runs use the default, no `Any` anywhere, which rejects `NDArray[Any]`,
   `dict[str, Any]`, `pickle.loads` and `json.loads`: `numpy` alone is 4,320 calls with no fix on
   the 47 corpora. One run at `vague = 0` says what the default costs on the scientific corpora
   (xarray, dask, networkx, pandas): a run file's `options = ["--vague", "0"]` gives it to every
   constricter command of the run (2026-10-21). Done when the census is read at both. About an
   hour beside the run; coverage unchanged.
2. **Test results as data.** A suite's tests are read from pytest's and unittest's text (`-rfE`
   lines, the summary), which misread sphinx's captured log lines as failures and spelled 4 suites'
   failure ids two ways between runs. pytest's `--junitxml` or `--report-log` (and unittest's
   verbose output, for django's runner) in `corpus_suite.tested` gives exact test and skip ids, skip
   reasons and per-test durations: sqlalchemy's skip-count flake by name, with no rerun, and what
   test-level sampling or sharding would later need. Built (2026-10-21): each part
   pytest runs writes a JUnit report (`--junitxml`, the `xunit1` family, whose `file` gives each
   test's node id back), read into `records/<corpus>/<version>/tests-<run>.tests.jsonl`, a line a
   test with its id, outcome, seconds and skip reason, and the failed tests are the reports' where
   every part wrote one; the counts stay the summary's (the reports don't tell an unexpected pass
   from a pass), and a suite unittest runs (django, mkdocs, twisted) is read as text still. The
   0.4.3-rc.1 mega run's records hold them (its first try took the ids from the reports' `file`,
   which pytest's cached rewritten modules keep from where a checkout was before: read from the
   class name since); its tests table still gives sqlalchemy's skips as a count, 973 (their flake's
   cause and fix: "sqlalchemy's tests in a fixed order"). Each fixed run's record names the tests it
   skipped where the tests as released ran them, and those it ran they skipped (`skipped anew`,
   `skipped no more`, from both runs' tests, `suite_steps._skips`), and the tests table counts them:
   on the 0.4.3-rc.7 and rc.8 mega runs none moved, but sqlalchemy's columns are blank, each fixed
   part implied by the union's, whose own part the table doesn't list. Built on 2026-10-26
   (`report_tables._tests`): the union's own run is a row of the tests table (`infer-union`, with
   its summary, new failures and skips), an implied part shows the skips of the run that stands for
   it, and the released tests are read from the earlier run's folder they were taken from (`from`)
   where this one's doesn't hold them. Done when the mega run of 2026-10-26's table shows
   sqlalchemy's columns filled. About an hour spent; coverage unchanged.
3. **What stubs would add to the corpora.** Of the 5,751 third-party `imported` calls with no fix
   on the 0.4.3-rc.1 mega run, 822 are into a package untyped in the corpus's environment (pandas in
   dask 297 and xarray 200, kombu 52, tlz 47, fsspec 40, scipy in networkx 39) and 978 into one not
   installed (pyarrow in pandas 137). Install pandas-stubs, scipy-stubs, pyarrow-stubs and
   types-PyYAML into dask's, xarray's, networkx's and pandas's environments (`corpora.toml`) and count
   the fixes and the chains they type. Done when measured. About 1 hour beside a run; coverage
   unchanged.
4. **Stubs generated for compiled code.** `stubgen --inspect-mode`, pybind11-stubgen, nanobind's
   and Cython's `embedsignature` signatures, mypy-protobuf, and `__text_signature__` give a
   compiled module's signatures, but few returns, and each needs the module imported. Next to no
   reach in the corpora: lxml 8 calls, grpc 3, greenlet 3. Done when a corpus that calls compiled
   code more is added, or measured as not worth it. About 2 hours to measure; coverage under 0.1%.
5. **Two checkers agreeing, likely.** `checker` is one set to LIKELY.md's bars, by checker; a hint
   basedpyright, ty and pyrefly agree on (two of them, or all three) is a set of its own, measured
   the same way, and `--likely` applies it where one checker's hint alone doesn't pass. Done when
   the mechanisms table counts the agreeing sets. Built: where a later checker's usable hint gives
   the type the first usable one does, the fix rests on their agreement too (kind `agreed`, beside
   `checker`; `Scope.hint`), a set of its own in the mechanisms table; not in `--likely` until it
   passes the bars, and not what a guess rests on: `unsafe-fix-select` trusts it by `checker` as
   before. On the 0.4.3-rc.8 mega run (`7a075e4`, 16CPU/60GB, 70 minutes): 14,941 of
   `infer-union`'s 26,590 checker fixes rest on an agreement, read from its records; the mechanisms
   table now lists the union step's sets, from the next run. The bars can't be read from a run yet:
   the witness judges `fix-unsafe`'s fixes alone (`traced.verdicts.jsonl`) and no type check runs
   after `infer-union`. Held by name to what the trace saw instead (`scratch/agreed_seen.py`: every
   type seen named in the annotation), `agreed+checker` held 86.2% of the 9,635 the trace told of
   and `checker` alone 73.7% of 5,321, where the union's certain fixes held 90.2% by name (99.5% by
   the witness: a subclass or a protocol differs by name). Left: the witness judging the union's
   fixes too, and a type check after it, then the sets held to the bars. About 3 hours beside a
   run; coverage unchanged (`--likely` gains what passes).
6. **pyrefly's `stubgen` for untyped packages.** For an installed package with no types, pyrefly
   writes stubs from what it infers (experimental; `Incomplete` where it can't tell): the calls
   declared types would reach plus the returns no source declares (tlz, botocore, kombu), perhaps
   600 direct calls. Read as guesses, as an installed package's stubs are, held to the witness. Done
   when measured on dask's and xarray's environments against the installed stubs' baseline. About 3
   hours; coverage unknown until measured.
7. **Framework plugins' types.** django-stubs' and pydantic's mypy plugins type what the frameworks
   make at run time (a model's fields, a manager's querysets), but only inside a mypy run. About 0
   calls in the corpora reach them. Done when measured on django's tests through mypy's `reveal_type`
   or a plugin's own output, or recorded as out of reach. About 3 hours; coverage unknown until
   measured.
8. **Declared types of installed packages with no `py.typed`, as guesses.** What pyright reads with
   `useLibraryCodeForTypes`, held to the source's own annotations (mypy reads such a package as
   `Any`): pandas/core declares 73% of its functions' returns, wheel 86%, setuptools 54%, grpc 51%.
   About 400 of the 822 untyped direct calls, and dask's and xarray's chains (2,314 and 1,078
   `receiver`/`member` calls, perhaps a third pandas values). A fix kind of its own, held to the
   witness. Built on 2026-10-26 (`installed.as_untyped`): such a package's modules join the index
   with their functions' and methods' declared returns as `returned` guesses resting on `declared`,
   followed through the package's re-exports (`pd.date_range`, which `spelling.spellings` follows
   for `returned` as for declared functions since); its classes' attributes, classmethods and
   overloads aren't offered, and its classes' bases still end a line of bases at the library class
   (`beyond`). A call to an unannotated function carries what its `return`s rest on in its fix's
   kinds since (`constructor+returned`), as a method's did. On dask (its environment's pandas
   3.0.6 untyped; one process on 16CPU/60GB, `--fix --unsafe-fixes` listing, old code against the
   tree): 5,788 fixes from 5,700 (+88 of 24,256 offences, 0.36%; 61 `declared`, `pd.DataFrame` 30,
   `DatetimeIndex` 13, `DataFrame` 8, the rest what they reach), likely 1,766 from 1,749 (the
   kinds change). Left: the hold rate from the next mega run's witness, and the stubs baseline
   ("What stubs would add to the corpora") for what pandas-stubs would add over this. About 4 hours
   spent; coverage 0.36% on dask. On the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step): `declared` 623 guesses on 5 packages, 387 told, 99.5% held, but 30 of the 432 a
   checker read blamed for 54 errors (6.94 in each 100 against the bar's 0.1): not likely as it
   stands; `declared+returned` 355, 179 told, 100% held, 9 of 211 blamed.
9. **typeshed's third-party stubs, not installed.** basedpyright ships them
   (`typeshed-fallback/stubs`, 201 sets): 18 of the top 100 PyPI packages are typed only there
   (pyyaml, python-dateutil, six, protobuf, grpcio, jsonschema, tqdm, pytz, regex, ...). Certain where
   the installed version matches `METADATA.toml`'s, a guess where not. Its reach is users' code.
   Measured on the 0.4.3-rc.8 mega run's census (`scratch/typeshed_reach.py`): of 7,955 third-party
   bindings with no fix, 137 at most call into a package a stub set covers (docutils 43, pywin32
   35, PyYAML 13, python-dateutil 7), some of them where the stubs are installed already. Done when
   decided: built for users' code, or left at under 0.1% on the corpora. About 4 hours to build.
10. **numpydoc Returns sections.** A docstring's `Returns` section names what a function with no
    return annotation returns (docstub and docs2stubs read them): networkx has 2,301 such
    functions, 868 with a Returns section and 485 naming one plain type; pandas 1,787 (360, 108),
    dask 3,912 (181, 56), xarray 1,088 (60, 38). Many names are vague (`dictionary`, `graph`), and
    `nx.path_graph`, the most called (460 calls), has none: under 1,000 usable. A guess, a
    docstring's name resolved where the module would resolve it, held to the witness. Done when
    measured on networkx and pandas. About 4 hours; coverage under 0.5%.
11. **Returns the trace records.** Of the 0.4.3-rc.1 mega run's 103,514 calls with no fix, the
    largest pool is a value a function returns: `member` 20,975, `untyped` 7,919, `local` 6,324
    ([type sources](research/type-sources.md)). `constricter.trace` already follows the traced
    suites' lines; recording each function's return type too (`sys.monitoring`'s `PY_RETURN`, the
    type noted as a binding's is), for `--infer-from` to give a function with no return annotation
    one, is where the run-time pool would come from, rather than RightTyper ("Signatures from a
    sampled run") or MonkeyType
    (`sys.setprofile`, up to 270× slower). Held to the rule the trace's locals are (a return the
    checkers type wider than the run saw is no fix). Built on 2026-10-26: the tracer records what
    each function returned at the line it returned from (`<return>`; a function binding no name
    too, its lines not followed; not a generator's), and `--infer-from` gives LVA014 a function's
    return where its own `return`s decide nothing (`traced.hints`, `Hints.returns`): a guess
    (`traced`), only where the run took every way out of the function (each `return` with a
    value, and its end where it can fall off it), up to three types' union, not a typing form
    (`Union` from an `__or__`). Measured on pydantic (its tests under the tracer in one process
    on 16CPU/60GB: 20.7s, 66 failing in the sandbox as released; 74 files, 1,386 return sites):
    `--fix --unsafe-fixes --extend-select LVA014` 1,617 fixes without the trace, 1,620 with it, 2
    returns from the trace (both `Union`, refused since) and 1 binding: pydantic annotates its
    returns, so there's nothing to add. On django, 10 of its test labels (`basic queries
    model_fields forms_tests template_tests many_to_one urlpatterns_reverse utils_tests
    db_functions expressions`: 4,994 of its 17,578 tests, 7.6s under the tracer in one process,
    258 of its 883 files reached, 9,035 return sites): `--fix --unsafe-fixes --extend-select
    LVA014` types 5,912 bindings from 5,445 (+467, 8.6%; 199 from the trace itself, the rest what
    they reach) and writes 4,122 signatures from 3,459, 625 from the trace (`str` 142, `bool` 56,
    `None` 44, `int` 31, `str | None` 30, `tuple[str, ...]` 15, `dict[str, str]` 14, ...). Left:
    its whole suite traced (about 10 minutes in one process on 16CPU/60GB, its traced step 98.7s on
    7 CPUs in the super run), and the new type errors, which django's CI has no checker for: read
    them from the next mega run's witness, which judges a traced return's fix as any guess's.
    About 6 hours spent; coverage: `--unsafe-fixes` +8.6% on django from a third of its tests. On
   the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step): the `infer-trace` step types 136,639 bindings of 292,568 from 133,865 (+2,774), 6,606
   fixes of kind `traced`; its new type errors share the signature codes' rise (10,531 from 32).
12. **Types from a model.** Type4Py, TypeWriter, DLTPy, Typilus, HiTyper, TypeT5 and TypeGen predict
    types (TypyBench and TypeEvalPy score them), but none is deterministic, and each needs a model
    or an API. Only as a file `--infer-from` reads, through the hint filter and the witness, as any
    guess is. Done when one is measured on pydantic against the checkers' hints: the fixes, the new
    errors. About 6 hours; coverage unknown until measured.

## Ongoing

- **Revisit the [disabled rules](CONTRIBUTING.md#disabled-rules)** as tools change (last checked
  2026-10-15: harden-runner's block policy now works on macOS and Windows, and zizmor's
  `self-repository` can come back once `ossf/scorecard-action` v2.5.0 is taken, both with the other
  repos' shared workflows; astroid 4.3, fastjsonschema 2.22 and reuse 6.2 still can't go). About an
  hour a pass.
