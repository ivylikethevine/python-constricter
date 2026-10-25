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
     witness agrees. Left: the tables' and installed packages' classes as candidates.
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
   own beside it (`local/runs/mega-lva013.toml`: mega's corpora with `--extend-select LVA013`, no
   hints, census, timing or traced tests; 36 minutes on 16CPU/60GB): 4,521 more `fix-likely` fixes
   and 5,093 more `fix-unsafe`, none certain; every suite's tests the same but nibabel's randomised
   ones; 6 new type errors (0.12 for each hundred fixes), pandas's 5 from `self.index` stored after
   a test narrowed it (typed as the tests leave it since) and sqlalchemy's
   `self._dict: util.PopulateDict`, a generic class written bare. Its `fix-unsafe` left a second
   pass something on 22 corpora (mypy 228 lines): a guess one file declared reached the other files'
   reads only on the next run, and is checked again in the same run since. A generic class without
   its arguments is no LVA013 fix since, as it's none for a binding (`attributes.unannotated`).
   Traced on 2026-10-23 (`local/runs/mega-lva013.toml`: the uncommitted tree past `15167da`, 51
   minutes on 16CPU/60GB, `local/corpus-runs/mega-lva013-10-23-2026-1953`), held by
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
   45 fixes over every fix step, as on rc.1. They need more data before they're kept or dropped:
   more guesses a test tells of, from more corpora or a wider reach. Done when those are decided
   and a mega run covers the changes since. About 1 hour; coverage up to 6%, likely far less.

2. **The compiled wheels, a job each.** A `python` matrix of cp311 to cp314 beside `os` in
   `build.yml` (`CIBW_BUILD` set from it) builds the 20 wheels at once, each job's artifacts and
   attestation named by both (`compiled-<os>-<python>`, which `release.yml`'s `compiled-*` patterns
   take); not yet released. 0.4.2's, a job a platform, took 10 to 11 minutes each and 20 on
   `macos-15-intel`. Build run 61 by hand on `dev` (`15167da`, 2026-10-23): the 20 jobs took 2 to 5
   minutes each, `macos-15-intel`'s 3 to 5; one ARM job's artifact download was refused as
   harden-runner started (`ECONNREFUSED`, the 19 others alike passed) and built in 4 minutes on a
   rerun. Done when a release's 20 wheels and attestations are on PyPI and the GitHub release. Under an hour beside the release;
   coverage unchanged.
3. **Runs in stages.** Built in `88e0dda`: a run's steps fall into stages run one at a time into
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
4. **The hinted steps' servers, sized by the memory free.** On the 0.4.3-rc.2 super run (48
   minutes, 54% of its CPU seconds) memory, not CPUs, kept steps waiting: each `infer-*` step held 12
   to 18 GB, almost all the checkers' servers (up to four a checker, `Server.fitting`), and pandas's
   `infer-union`, all three checkers' at once, 28.5 GB for 10.5 minutes, with 2.5 to 7 CPUs busy from
   its 20th minute to its 35th; the standard library's three hinted steps waited 19 to 36 minutes to
   start. The union's rounds can't be read from its checkers' steps (`cli/lsp/stored.py`): only the
   first one or two are the same texts (pandas: 1 or 2 of 6). `--infer-in-turn` asks the checkers
   one after another, each one's servers shut down before the next's start, and the runner's
   `infer-union` asks so, an unmeasured one sized by its largest checker's step; a step measured
   before keeps its last run's hold for one run. On the 0.4.3-rc.3 super run (`ac48774`) pandas's
   `infer-union` held 14.5 GB for 267s, from 28.5 GB for 630s (given 31.5 GB, rc.2's hold), and
   django's 5.4 GB from 11.1; its hints not yet compared, and the run's 52% of its CPU seconds is
   short of 75%. pytest's stopped at a `ValueError`: a checker with no file to ask about in a round
   had no server to stop (`Checker.stop`, fixed since). A hinted step now starts with as few CPUs
   as hold, by their share of its memory, one server of each of its checkers for the corpus
   (`Plan._hinted`: basedpyright's 0.6 GB and 130 bytes a byte), and takes as many more as are
   free, as a suite's tests do; started short, its servers get that share of the 8 GB default
   (`--infer-memory`, `Wanted.hinted`), and given all it wants, the default as before. On the
   0.4.3-rc.4 super run (`46bdc27`, 16CPU/60GB) the hinted steps of its first 15 minutes waited 8
   to 334s, from rc.3's ~520s, and the standard library's `infer-basedpyright` 909s (18.2 GB
   wanted, ~29 GB to share, pandas's 13.8 GB running); pandas's `infer-union` held 14.5 GB for
   281s; the run used 53% of its CPU seconds (57% less its 4.5 minutes of pauses; rc.3 52%).
   pandas's `infer-basedpyright` took 856s from rc.2's 405s: sized from rc.3's crashed 76s and 5.9
   GB, it wanted 3 CPUs and started on 2, so 5.33 GiB, one server of pandas (3.25 GiB each) where
   8 GiB holds two, for its `--fix` (496s) and `--diff` (~360s) runs both. A short start's budget
   is since rounded up to whole servers of its largest checker, one a CPU held, as many as the
   default holds (`Wanted.server`). On the 0.4.3-rc.5 mega run (`9892f71`, 16CPU/60GB, 82 minutes) pandas's `infer-basedpyright` took 265s and 8.0 GB, from
   738s and 1,515s on rc.1's two, but the steps that started on one CPU ran far longer: stripe's
   2,167s (0.57 GB given, waited 1,408s; rc.1 1,068s and 1,236s on 3 CPUs), dask's 555s (137s and
   159s on 4), xarray's 404s (115s and 164s): a short start keeps its CPUs, and its servers, for
   the whole step, and stripe's 36 minutes on one held the run's end. The run used 73% of its CPU
   seconds (rc.1 76%). Only a hinted step whose last run took 300s at most starts short since
   (`sizing._BRIEF`): on the 0.4.3-rc.6 mega run (`c7f4db0`, 16CPU/60GB, 65 minutes) stripe's took 26s, dask's 66s, xarray's 63s, pandas's 246s, and
   pandas's `infer-union` held 14.3 GB; the run used 77% of its CPU seconds. Done when pandas's
   `infer-union` holds under 18 GB
   and a super run uses 75% of its CPU seconds, its hints the same. Coverage unchanged.
5. **basedpyright's heap, capped: in the tree, to measure.** Node 24's own cap was 4.2 GB whatever a
   server's share (basedpyright empties its caches near it, and says so: "Emptying type cache").
   Each server's heap is now capped at nine tenths of its share of the memory
   (`NODE_OPTIONS=--max-old-space-size`, `Checker.share`), and a capped server that exits is
   restarted and asked about its files alone, as a hung one is (`ExitedError`), a file it exits on
   again left without hints and not remembered. The hints on the standard library's `email` are the
   same as before. On the 0.4.3-rc.3 super run (`ac48774`) the standard library's
   `infer-basedpyright` took 490s and 14.6 GB, from 579s and 13.5 GB. pandas's stopped at a
   `KeyError`, its patch empty: a file a server hung on in an earlier run (`remembered`) was left
   out of every server's work with no entry in the answers (fixed since: `Session.hints` gives each
   abandoned file none). The runner recorded the step as made, and its 76s and 5.9 GB; a fix or
   census step whose constricter ends at an exception fails since (`pipeline._crashed`), its
   traceback in the step's log. On the 0.4.3-rc.4 super run (`46bdc27`) every stage exited 0, no
   hinted process crashed, and pandas's `infer-basedpyright` fixed 47,038 (rc.2 47,035), one file
   hung on twice (`tests/apply/test_series_apply.py`). Left: its hints against rc.2's.
6. **The witness, past a test's own classes.** The corpora runs hold a fixed binding's value to its
   annotation as its package's traced tests bind it (`tests/corpus/witness`). A value of a class a
   test module defines tells nothing of the annotation, as a mock or a `SimpleNamespace` doesn't,
   nor of an annotation naming a test's class outside the tests (django's `datetime`, patched to
   `MockDateTime`); a class a function defines again at each call is the annotation's by its module
   and qualified name, and a module's class imported anew is the one it names. On the 0.4.0-rc.3
   mega run 223 certain fixes differed (259 before these), 70 likely and 88 other guesses (102 and
   109). Most are the package's own declarations its tests contradict: a numpy scalar where `int` or
   `bool` is declared (pandas's `iloc`, `_has_infs`), `None` where it isn't (sphinx's C++ parser),
   `round_trip_pickle`'s `DataFrame | Series` for any value pickled, pytest's `FSHookProxy` for a
   `HookRelay`. Read through on 2026-10-21, all 223: the witness was wrong on 6, fixed in the tree
   (`typing.IO`'s classes, which nothing is an instance of, now take any value that reads, writes
   and closes: optuna's `NamedTemporaryFile` wrapper, 147 of its counts; a `StringIO` or `BytesIO`
   where `io`'s or `typing`'s file class is named is a test's stand-in, as a test's `open` or
   `io.TextIOWrapper` gives it: dask's, black's, celery's; and a package's `pytest` plugin module
   is a test module: pdm's `pdm.pytest.Distribution`). The other 217 are declarations the tests
   contradict: the package's own, or typeshed's (asyncio's `Server.sockets` as `socket.socket`,
   given `TransportSocket`; uvloop's `Server` and transports for asyncio's). On the 0.4.3-rc.1 mega
   run 225 certain fixes differed (`scratch/witness_diff.py`, against rc.3's): 179 of those 217; 7
   fixes rc.3 made the same and no test contradicted then (asyncio's `Transport` given uvloop's,
   sqlalchemy's `str` given `None`); 4 new fixes of declarations the tests contradict (sphinx's
   `self.names` given `None`, starlette's `path_params: dict[str, str]` given a `datetime` and an
   `int`, xarray's `Mapping[str, TreeNode]` given an `int` by a test of its `TypeError`); and one
   wrong fix: narwhals's `impl = self.implementation` typed `_Implementation`, a descriptor whose
   `__get__` gives an `Implementation` through an instance. Built, not yet run: an attribute a class
   body annotates with a descriptor class (its body defines `__get__`), the module's or another
   checked file's, is read through an instance as `__get__` declares it returns, and is no fix where
   `__get__` is overloaded (narwhals's 16, chosen by the instance's type), declares no return or
   names a type variable (`declarations.descriptors`, `members.through_instance`). Done when the
   next mega run's certain fixes that differ are declarations the tests contradict alone. Under an hour beside the
   run; coverage unchanged.

### Small: under 4 hours

1. **Ubuntu 26.04 runners, first.** Every Linux job runs on `ubuntu-latest`, and the release's ARM
   wheels on `ubuntu-24.04-arm`; GitHub moves `ubuntu-latest` to Ubuntu 26 from 2026-10-19, so
   jobs change image under a run (every Linux job carries the notice). Move them to `ubuntu-26.04`
   and `ubuntu-26.04-arm`, named, so an image change is a commit rather than the label moving under
   a release. The newer image brings newer compilers, Pythons and tools; the shared workflows move
   with every repository's at once. Done, not yet run: this repository's own workflows run on
   `ubuntu-26.04` (`.github/actionlint.yaml` names the label, which actionlint 1.7.12 doesn't know);
   the ARM wheels stay on `ubuntu-24.04-arm`, there being no 26.04 ARM image yet. Done when CI, Security, the other workflows and a release run
   (the Build workflow by hand) pass on it, harden-runner's allowlists unchanged or updated from an
   audit run. About 1 hour; coverage unchanged.
2. **The timed tail.** The timed checks run last, alone and one at a time: three corpora at once on
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
   steps 326s, from rc.1's 6.2 and 371s; rc.6's the same, 5.4 and 327s). About 1 hour beside the run;
   coverage unchanged.
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
   On the 0.4.3-rc.6 mega run (`c7f4db0`, 16CPU/60GB, 65 minutes): 64.3 against a shortest 55.6 (16% over). A stage plans its own steps alone since
   (`planning.ranks`'s `chosen`); not yet run in stages. A run's share of its CPU seconds isn't the measure
   (85% was the target before): memory and the timed tail bound it whatever the order, and the
   0.4.0-rc.1 mega run, within a tenth of its floor, used 77.5%. Done when a super and a mega run
   each take within a tenth of the solver's shortest schedule of their own steps, and one with no
   earlier run under its output takes within a tenth of one sized by its own. About 3 hours beside
   the runs; coverage unchanged.
4. **Signatures from a sampled run.** RightTyper runs a package's tests
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
   About 2 hours left; coverage unchanged.
5. **A check's peak, past the resumed files.** The standard library's check in one process
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
2. **Mutation testing.** Line coverage is held at 100% (`fail_under`), so it no longer says which
   lines run without a test checking what they do; a mutant the suite survives does. How: `mutmut`
   over `constricter/`, its tests run without the corpus suites, in a `scratch/` script with its
   output under `local/`; triage the survivors and write tests for those worth killing. Done when
   a full run's survivors are each killed or recorded as equivalent. Written, not yet run:
   `scratch/mutation.py` (mutmut 3.8 on a worktree of HEAD under `local/mutation/`, the unit tests
   alone, the lines they cover, `--only` for a first pass). About 6 hours beside the run; coverage
   unchanged.
3. **A parallel check, past its longest chain.** With every CPU the standard library checks in 12.9s
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
   still to do (`local/meanwhile/signatures-plan.md` has the rest). On pydantic (2026-10-24,
   `--fix --unsafe-fixes --extend-select LVA014`): 34 functions reported, 31 fixed (29 `-> None`, 2
   `-> str`; 29 of them methods' guesses), the other 1,596 fixes the same, `pyright pydantic` 0
   errors as without, and its 12,311 tests passing. About 10 hours; coverage unmeasured:
   it moves guesses to certain more than it adds fixes.
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
   test-level sampling or sharding would later need. Built, not yet run (2026-10-21): each part
   pytest runs writes a JUnit report (`--junitxml`, the `xunit1` family, whose `file` gives each
   test's node id back), read into `records/<corpus>/<version>/tests-<run>.tests.jsonl`, a line a
   test with its id, outcome, seconds and skip reason, and the failed tests are the reports' where
   every part wrote one; the counts stay the summary's (the reports don't tell an unexpected pass
   from a pass), and a suite unittest runs (django, mkdocs, twisted) is read as text still. The
   0.4.3-rc.1 mega run's records hold them (its first try took the ids from the reports' `file`,
   which pytest's cached rewritten modules keep from where a checkout was before: read from the
   class name since); its tests table still gives sqlalchemy's skips as a count, 973 (their flake's
   cause and fix: "sqlalchemy's tests in a fixed order"). Built, not yet run: each fixed run's record
   names the tests it skipped where the tests as released ran them, and those it ran they skipped
   (`skipped anew`, `skipped no more`, from both runs' tests, `suite_steps._skips`), and the tests
   table counts them. Done when the tests table reads sqlalchemy's skips by name. About an hour;
   coverage unchanged.
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
   the mechanisms table counts the agreeing sets. Built, not yet run: where a later checker's usable
   hint gives the type the first usable one does, the fix rests on their agreement too (kind
   `agreed`, beside `checker`; `Scope.hint`), a set of its own in the mechanisms table; not in
   `--likely` until it passes the bars, and not what a guess rests on: `unsafe-fix-select` trusts
   it by `checker` as before. On the 0.4.3-rc.7 mega run (`5674049`, 16CPU/60GB, 68 minutes): 14,936 of `infer-union`'s 26,589 checker
   fixes rest on an agreement, but the mechanisms table leaves the union step out, so counts none:
   it takes the union in next. About 3 hours; coverage unchanged (`--likely` gains what passes).
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
8. **One type at run time, no fix.** The traced suites already know what each binding held; for each
   binding with no fix, whether the run saw one type is both the upper bound of any inference and a
   bug finder. A table by shape in the `traced` step: bindings with no fix, those the run bound to
   one type, and the commonest sources. Built, not yet run: the `traced` step keeps the types the
   trace saw each of the package's bindings hold (`traced.seen.jsonl`), and the report holds the
   census's bindings with neither a fix nor a guess to them, by shape (`one-type.csv`). Done when the
   table is in a run's report: on the 0.4.3-rc.7 mega run (`5674049`, 16CPU/60GB, 68 minutes), of 162,001 bindings with neither fix nor guess, the
   traced tests reached 79,623 and saw 60,259 hold one type (`one-type.csv`, by shape). About 4
   hours; coverage unchanged.
9. **Declared types of installed packages with no `py.typed`, as guesses.** What pyright reads with
   `useLibraryCodeForTypes`, held to the source's own annotations (mypy reads such a package as
   `Any`): pandas/core declares 73% of its functions' returns, wheel 86%, setuptools 54%, grpc 51%.
   About 400 of the 822 untyped direct calls, and dask's and xarray's chains (2,314 and 1,078
   `receiver`/`member` calls, perhaps a third pandas values). A fix kind of its own, held to the
   witness. Done when measured against the installed stubs' baseline ("What stubs would add to the
   corpora"). About 4 hours; coverage up to 1%.
10. **typeshed's third-party stubs, not installed.** basedpyright ships them
    (`typeshed-fallback/stubs`, 201 sets): 18 of the top 100 PyPI packages are typed only there
    (pyyaml, python-dateutil, six, protobuf, grpcio, jsonschema, tqdm, pytz, regex, ...). Certain where
    the installed version matches `METADATA.toml`'s, a guess where not. About 60 to 100 calls in the
    corpora; its reach is users' code. Done when measured. About 4 hours; coverage under 0.1%.
11. **numpydoc Returns sections.** A docstring's `Returns` section names what a function with no
    return annotation returns (docstub and docs2stubs read them): networkx has 2,301 such
    functions, 868 with a Returns section and 485 naming one plain type; pandas 1,787 (360, 108),
    dask 3,912 (181, 56), xarray 1,088 (60, 38). Many names are vague (`dictionary`, `graph`), and
    `nx.path_graph`, the most called (460 calls), has none: under 1,000 usable. A guess, a
    docstring's name resolved where the module would resolve it, held to the witness. Done when
    measured on networkx and pandas. About 4 hours; coverage under 0.5%.
12. **Returns the trace records.** Of the 0.4.3-rc.1 mega run's 103,514 calls with no fix, the
    largest pool is a value a function returns: `member` 20,975, `untyped` 7,919, `local` 6,324
    (`local/research/type-sources-2026-10-23.md`). `constricter.trace` already follows the traced
    suites' lines; recording each function's return type too (`sys.monitoring`'s `PY_RETURN`, the
    type noted as a binding's is), for `--infer-from` to give a function with no return annotation
    one, is where the run-time pool would come from, rather than RightTyper ("Signatures from a
    sampled run") or MonkeyType
    (`sys.setprofile`, up to 270× slower). Held to the rule the trace's locals are (a return the
    checkers type wider than the run saw is no fix). Done when measured on pydantic and django: the
    fixes, the new errors and the `traced` step's time. About 6 hours; coverage unknown until
    measured.
13. **Types from a model.** Type4Py, TypeWriter, DLTPy, Typilus, HiTyper, TypeT5 and TypeGen predict
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
