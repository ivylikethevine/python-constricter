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

**Read on the mega runs of 2026-10-29** (`mega-10-29-2026-1139` on `f7d53b2`, 89 minutes,
`mega-10-29-2026-1920` on `e793bc6`, 65 minutes, and `mega-10-29-2026-2241` on `d160aa8`, 76
minutes, all on 16CPU/60GB), against `mega-10-28-2026-0826` and each other by
`scratch/type_errors_diff.py` and `scratch/guess_report.py --from`:

- Bindings typed of 474,291 on `d160aa8`: `--fix` 164,036, `--likely` 217,161, `--unsafe-fixes`
  241,719 (161,113, 211,064 and 228,999 on 2026-10-28's `6b0ab18`); `infer-trace` 146,385 of
  292,568 (134,815). Bindings with no fix 232,959 from 245,708 on `f7d53b2`: pygments 2,313 from
  6,695, xarray 11,247 from 14,326, the standard library 62,138 from 63,071, sqlalchemy 9,662 from
  10,140, django 11,609 from 11,747, each item's own measure or within 30. The standard library's
  hinted steps move between runs with nothing changed in them: `infer-pyrefly` 60,720 on `f7d53b2`
  and `d160aa8`, 60,876 on `e793bc6`.
- New type errors 462 on `d160aa8`, 470 on `e793bc6`, 562 on `f7d53b2`, 428 on `6b0ab18`. Of
  `f7d53b2`'s 134 more, mcp's 60 and strawberry-graphql's 19 were a defaulted generic written bare
  by a `constructor` guess whose call passes the enclosing class's type variable, and pandas's 4
  certain fixes in each step numpy's `view` taking its first overload, a parameter declared alike in
  every overload read as taking anything; both mended on `e793bc6` (`doubts.binds_defaults`,
  `signatures._placed`). On `d160aa8` sqlalchemy's `_InternalEntityType` errors are gone (3 to 0)
  and nibabel's `documented` ones (5 to 0). Left: sqlalchemy's 12 `Enum` errors (below), optuna's 6
  (one fix's, in six steps: a copy of a name each branch binds, Small) and pint's 3 (`Quantity`
  depending on itself, as under the run-time types item, Large).
- Against [LIKELY.md](LIKELY.md)'s bars on `d160aa8`: `text` (241 guesses, 135 told, 99.3% held,
  none blamed) and `operand` (324, 192, 100%, none; its set `literal+operand` 127 with 64 told)
  pass; `constructor` 15 of 26,457 read blamed (0.06 in each 100), `method`'s set alone 2 of
  1,083 (0.18, the bar 0.1), as on 2026-10-27, when they were nibabel's `magic_number: bytes` and
  pandas's `subarr: Index` in a method returning `Self` (`core/indexes/datetimes.py`): to read
  before `method` is counted out; `reads` 68 guesses, 37 told, 94.6% held, short of
  the held bar; `named` 2.
- One problem on each of `e793bc6` and `d160aa8`: the standard library's second pass, `trace.py`'s
  `encoding` (Small), 1 line left. nibabel's randomised quaternion tests, `f7d53b2`'s other problem,
  are a `differs` entry since.
- basedpyright's servers aborted four times in dask's `infer-union` on `f7d53b2`, none on
  `e793bc6` (Small).

**Read on `mega-10-30-2026-0857`** (`a8de20a`, 70 minutes, 16CPU/60GB), against the 22:41 run by
`scratch/type_errors_diff.py` and `scratch/run_fixes_diff.py`: new type errors 461 from 462, none
gained (nibabel's `file_map`, below under the run-time types item). `type[T]` and a `@classmethod`'s
receiver hold, each below. New failures: sphinx's `test_html5_rubric` in 4 steps of 8 with its fixes
the same as the 22:41 run's, and nibabel's randomised `test_mult` and `test_euler_mat_2`, none blamed
on a fix; sqlalchemy's 4 `test_compare` and joblib's 1 are gone. Every corpus has records, so the run
leaves the planning of an unmeasured step ("A run with no earlier run, held to the solver's shortest")
ungated.

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
     witness agrees. Built on 2026-10-26: every class the file names is a candidate (another checked
     file's with its members typed or not, from the index's `bound`; an installed package's; a
     subclass's with its imported base's), and the standard library's where one class the tables
     hold is what every other with those members is under (`datetime.date` for `year` and
     `strftime`; not `pathlib.PurePath` for `stem` and `suffix`, which `zipfile.Path` has too),
     through an import added. On django
     (`scratch/signatures_measure.py django --modes unsafe --select LVA015`, one process on
     16CPU/60GB): `--fix --unsafe-fixes` 5,428 from 5,408 with the tables' classes (+20 bindings),
     and with `--extend-select LVA015` 537 parameters typed from 525 with the index's members (+12);
     pydantic not measured. `reads.members` keeps every module's attributes since, and each file's
     `Outside` the members of the classes it names: the check was last timed whole on 2026-10-27 ("A
     parallel check, past its longest chain"). On the mega run of 2026-10-26
     (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the signature codes in every fix step):
     `reads` 725 guesses, 21 told, 95.2% held, 44 of 450 read blamed (9.78 in each 100); `named`
     1,794, 6 told, 78 of 750 blamed (10.4): neither passes, both lose more than the index's members
     gained. On the mega run of 2026-10-27 (`mega-10-27-2026-0131`, 91 minutes on 16CPU/60GB, the
     signature codes out of the run files): `reads` 57 guesses, 26 told, 96.2% held, none of 19 read
     blamed, so it passes the bars as a mechanism, but no set of it has 20 guesses (`LIKELY` takes
     whole sets); `named` 2, none told.
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
     and the read (`narrowed.narrowed_to`). Of the 13,972 bindings with no fix that copy a name or
     an attribute in a function, 424 follow a test of what they copy: `is None` (159), `isinstance`
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
   own beside it (`tests/corpus/runs/mega-lva013.toml`: mega's corpora with
   `--extend-select LVA013`, no hints, census, timing or traced tests; 36 minutes on 16CPU/60GB):
   4,521 more `fix-likely` fixes and 5,093 more `fix-unsafe`, none certain; every suite's tests the
   same but nibabel's randomised ones; 6 new type errors (0.12 for each hundred fixes), pandas's 5
   from `self.index` stored after a test narrowed it (typed as the tests leave it since) and
   sqlalchemy's `self._dict: util.PopulateDict`, a generic class written bare. Its `fix-unsafe` left
   a second pass something on 22 corpora (mypy 228 lines): a guess one file declared reached the
   other files' reads only on the next run, and is checked again in the same run since. A generic
   class without its arguments is no LVA013 fix since, as it's none for a binding
   (`attributes.unannotated`). Traced on 2026-10-23 (`tests/corpus/runs/mega-lva013.toml`: the
   uncommitted tree past `15167da`, 51 minutes on 16CPU/60GB), held by
   `scratch/guess_report.py --from` on 42 packages: `assigned`, LVA013's kind, 4,703 guesses, 867 a
   test told of, 99.0% held and 2 blamed for an error (0.06 for each hundred), its set alone 3,147,
   134 told, 98.5% held and 1 blamed, so it passes [LIKELY.md](LIKELY.md)'s bars; `reads` 13, 5
   told, 2 held; `named` 6, none told. The two blamed: pydantic's
   `self.from_type: TypeForm[_FromTypeT]`, the method's own type variable, unbound where the
   attribute is declared; and werkzeug's `self.observer: Observer`, watchdog's `Observer` bound in
   its platform branches, which a checker reads as a variable (a local's constructor guess writes it
   too, `likely`). Its `fix-unsafe` left litestar 3 lines for a second pass, reads above the class
   whose attribute the file declared, which the run now checks again. sphinx's `test_html5_rubric`
   failed after `fix-likely`, both times, with a patch all but the earlier run's, which passed: it
   shares `markup-rubric`'s source directory with the man, LaTeX and texinfo tests on a pytest-xdist
   worker, and finds their pickled environment when one ran first there, so the directive's warning
   it asserts never comes (the suite's own order, a `differs` entry's to name). The two blamed
   fixes' causes are Small proposals of their own (an attribute typed with its method's type
   variable; a constructor guess of a class bound in branches). `named` and `reads` stay for now,
   though too few to read against the bars: on the 0.4.3-rc.5 mega run (`9892f71`) 49 and 45
   fixes over every fix step, as on rc.1, rc.7 and rc.8. They need more data before they're kept
   or dropped: more guesses a test tells of, from more corpora or a wider reach. Done when those are decided and a mega run
   covers the changes since. On the mega run of 2026-10-29 (`f7d53b2`): `reads` 68 guesses, 37
   told, 94.6% held, none of 30 read blamed; `named` 2. About 1 hour; coverage up to 6%, likely far
   less.

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
3. **A docstring's named return** (`documented`, a guess). The roadmap's "numpydoc Returns
   sections", built for builtin scalars alone: a numpydoc `Returns` section of one entry, a
   Google-style `Returns:` or a Sphinx `:rtype:` naming `int`, `float`, `bool`, `str`, `bytes` or
   `complex`, or one `or None`, types a plain unannotated function's calls where its `return`s
   decide nothing and none gives a value the type doesn't take (`fix/values/documented.py`). A
   method's fix names it in its kinds beside `returned`; what else a method's guess rests on stays
   out, as before. Reach: about 120 undecorated functions on the mega corpora's sources (nibabel
   32, networkx 29, botocore 25); networkx has 121 more under `@nx._dispatchable`, which no rule
   vouches gives its function back. nibabel (`scratch/fix_diff.py`, one process on 16CPU/60GB):
   2,427 to 2,448 fixes, 14 of them `documented`; networkx 1. Not read: a docstring naming a
   class (`NetworkX graph`, 391 of networkx's), a container (`dict`, `list of int`), several
   entries. basedpyright's errors after `--fix --unsafe-fixes` on nibabel, with every item here: 33
   new and 24 gone, five of the new from `documented` guesses naming `int` or `float` where numpy's
   own scalars come back (`_fread3`, `mask_volume`): `np.int64` is no `int` to a checker, which
   the witness tells of too. `offences.py` is one of the tables' inputs: `test_tables_current` waits on
   `python -m stdlib_tables --if-stale`. On the mega run of 2026-10-29 (`f7d53b2`) it missed every
   bar (27 guesses, 16 told, 62.5% held, 1 of 25 read blamed), its misses numpy's `int32` and
   `int64`: a module importing numpy has no `documented` number since (`documented.imports_numpy`).
   On `e793bc6` 14 guesses, 8 told, 87.5% held, 1 of 12 blamed: nibabel's `offset: int`, from a
   function ending `return None`, which the check records as of no known type; a `return None` or a
   bare `return` refuses a type without `None` since (`documented._gives_none`). On `d160aa8` 12 guesses,
   8 told, 87.5% held, none of 10 read blamed: too few to pass the bars (20 told) or fail them. Done
   when a mega run reads it against the bars on 20 told. Coverage under 0.1%.
4. **A call's type variable bound by a class passed as `type[T]`.** `query_one("#x", Static)`,
   declared `def query_one(self, selector: str, kind: type[T]) -> T`, had no fix: a checked file's
   function whose return names a type variable was never read, overloaded or not. Built: an
   undecorated function or method returning a name alone that a parameter's `type[...]` takes is
   read as its one signature (`declared._class_typed`), and a return that is a type variable a
   parameter binds to a class stays a template (`own_overloads._class_bound`), so the matcher writes
   the class as the call does, as for an installed package's: `query_one("#x", Static)` is a
   `Static` (certain), and an overload set with such a member, refused whole before, is matched
   (`query("#x")` a `Widget`). Not yet: a type variable another module defines (textual's
   `QueryType`), and a method on a receiver typed as a subclass (`self.query_one` in a `Widget`'s
   subclass). 98 such definitions on the mega corpora's sources (textual 18, cattrs 14, zarr 10,
   litestar 9). Done when a mega run has the fixes and no new error from them: on
   `mega-10-30-2026-0857` it has them (`--unsafe-fixes` 2 more on each of mkdocs, tox and werkzeug),
   with no error. Left: `_class_typed` also takes a concrete class (xarray's `def get_backend(engine:
str | type[BackendEntrypoint]) -> BackendEntrypoint`), so a call with a guessed argument loses its
   declared return: 6 certain fixes in `backends/api.py` are `--likely` since (reproduced by
   `scratch/fix_diff.py d160aa8`). Reading only a name the module binds as a type variable restores
   them.
5. **A run with no earlier run, held to the solver's shortest.** The runner's schedule is within a
   tenth of the solver's shortest for a super and a mega run sized by earlier runs
   ([COMPLETED.md](COMPLETED.md)). Left: a run with no earlier run under its output, whose steps,
   none measured, keep the rules (the longest chain first, `_PATIENCE`, backfilling) rather than
   the solver's plan; and a run in stages, each stage planning its own steps alone since
   (`planning.ranks`'s `chosen`), not yet run that way. Done when a run with a corpus new to its
   output takes within a tenth of the shortest schedule of its own records
   (`scratch/schedule_solve.py`). About 3 hours beside the runs; coverage unchanged. Every run
   file writes under `corpus-runs/`,
   whose committed reports keep each step's use, so a run meets none of its steps measured only
   under a new `output`; a new corpus or step is unmeasured within a measured run. Replayed on
   2026-10-30 (`scratch/schedule_sim.py --timing-beside --unmeasured`, 16 CPUs and 36 GB, each
   step's true seconds and use), the runner's rules with nothing measured, the waiting steps taken
   as they came, against its order on measured seconds (the longest chain first): the mega runs of
   2026-10-29 at 22:41, 19:20 and 11:39 in 75.3, 68.6 and 89.1 minutes against 65.0, 56.5 and 73.7
   (16% to 21% over), and 67.3, 57.7 and 75.2 with nothing kept waiting (`_PATIENCE` off): with no
   step's seconds known, a step kept waiting holds back every other, none ending soon enough to go
   beside it. The replay holds each step to what it used; the runner sizes an unmeasured one by
   its kind's defaults and then by what it's seen to use (`Plan.fitted`). Built on 2026-10-30: a
   step no run measured on its corpus is planned for the median seconds of the corpora that ran it
   in its corpus's set by size and time (`corpora.toml`'s `fast-small` to `slow-large`), or else of
   every one that did (`planning.like`); one no corpus ran keeps the rules, as does a run under a
   new `output`. Replayed with each of six large corpora new to the output (`--new CORPUS`, the
   order the longest chain first, the new corpus's steps after every ranked one or by its group's
   seconds), on the same three runs: 1,187 minutes over the 18 replays against 1,213 unranked,
   pandas on the 22:41 run 67.5 against 72.5, the standard library and mypy on the 11:39 run 73.4
   and 74.0 against 78.7 and 79.6, the most lost 0.8 (the standard library on the 19:20 run). Left:
   a run with a corpus new to its output, read against `scratch/schedule_solve.py` on its own
   records, which every corpus of `corpora.toml` having records under `corpus-runs/` leaves to the
   next corpus added (or a run under another `output` holding the others' records); and a run in
   stages, hours apart.

### Small: under 4 hours

1. **CI's tools and security workflows, the shared way.** Built: every CI tool installs from
   `.github/actions/setup-tool/tools.txt` (`setup-tools` for the Workflow audit's zizmor and
   actionlint, `setup-tool` for gitleaks, lychee and osv-scanner) and `actions/tool` is gone with
   `check_tool_versions.local.sh`'s three rows for it; `security.yml`'s own CodeQL and weekly
   link-check jobs are gone, `codeql.yml` and `link-check.yml` run both (the shared `codeql.yml`
   with `security-extended`, as the old job ran); the Dependency audit runs
   `osv-scanner scan source --recursive .` after pip-audit, which `tests/ci_local.py` runs too when
   osv-scanner is on `PATH`, and skips a `tools.txt` tool's step without the tool. osv-scanner's
   first local pass found virtualenv 21.14.12 (GHSA-cx6f-vjhg-g3cc, fixed in 21.14.13), which
   pip-audit had passed, so `uv.lock` moves to 21.14.13; the shared `osv-scanner.toml` drops its
   braces entry, withdrawn upstream. Left: a green run of every workflow on a pull request, each
   job's `allowed-endpoints` re-read from its audit (the Dependency audit's, Secrets' and the Docs
   job's were written from the Workflow audit's set, plus `api.osv.dev:443`), and `link-check.yml`
   and `tool-versions.yml` dispatched by hand once. About an hour; coverage unchanged.

2. **A checker's short name for a class the module defines another of** (a proposal: it withdraws
   fixes). basedpyright's hint `MappingProxyType[str, Enum]` means `enum.Enum`; written in
   sqlalchemy's `sqltypes.py`, which defines `class Enum(..., TypeEngine[...])`, it names that
   class, since the subscripted bases made the class plain (it was a generic written bare before,
   refused): 8 new type errors over the `infer-*` steps on `f7d53b2`, 12 on `e793bc6` and
   `d160aa8` (`_members: MappingProxyType[str, Enum]`, `objects: list[Enum]`). Built, and not
   enough: a hint whose edit writes a name the file binds, where a module it imports whole has a
   class of that name too, is no fix (`offers._ambiguous`); but `_ambiguous` judges a hint's edits
   alone, and `hinted.hinted` takes the checker's shown type first, whatever the edits say.
   Proposed: judge the shown type the same way (a name the file binds, of a class a module it
   imports whole has too) before it is spelled. It withdraws the fixes of every such hint, so it
   waits on a decision. Done when a mega run's `infer-*` steps have no such error. About an hour;
   coverage down by those fixes.
3. **No type naming a builtin the module binds itself** (a proposal: it withdraws fixes). A
   standard-library type is written with the builtins it names whatever the module binds:
   `pat: re.Pattern[str]` where `from .compat import str` (requests' Python 2 shim), which
   basedpyright reads as a variable ("Variable not allowed in type expression"). Tried: refuse a
   fix whose type names a builtin the module binds at its top level (`ImportPlan.defined`, in
   `doubts.corrected`). pip (`scratch/fix_diff.py`, `scratch/fix_errors.py`, one process on
   16CPU/60GB): 21 fixes withdrawn, basedpyright's errors 20 fewer, none new. Not kept: it narrows
   what `--fix` offers, so it waits on a decision. About an hour; coverage down by those fixes.
4. **An override exclusion for every plain class** (a proposal: it withdraws fixes). A class plain
   only by its inert marks, or a variable bound to `None`, has no variable typed where a class in
   its line defines the name (`classvars.unshadowed`); a class plain at HEAD keeps HEAD's fixes, so
   `_render_label_in_columns_clause: bool` under a subclass's `@memoized_attribute` of the name is
   still written (sqlalchemy's `reportIncompatibleVariableOverride` 110 after HEAD's
   `--fix --unsafe-fixes`, 103 before it). Applying the exclusion to every plain class withdraws
   those.
   Measure first: the fixes withdrawn and the errors gone on sqlalchemy and django. About an hour.
5. **An attribute typed with its method's type variable** (a proposal: it withdraws fixes). LVA013
   writes an attribute's type where a method first stores it, and a type variable that method's
   signature declares is unbound for the attribute, which the class holds: pydantic's
   `self.from_type: TypeForm[_FromTypeT]`, blamed for an error on the traced LVA013 run of
   2026-10-23. Proposed: an attribute's type naming a type variable its class doesn't bind is no
   fix. Measure first: the LVA013 fixes it withdraws on the mega corpora
   (`tests/corpus/runs/mega-lva013.toml`). About an hour.
6. **A constructor guess of a class bound in branches** (a proposal: it withdraws fixes).
   watchdog's `Observer` is bound in its platform branches, which a checker reads as a variable, so
   werkzeug's `self.observer: Observer` (LVA013's) is an error, blamed on the traced LVA013 run of
   2026-10-23; a local's constructor guess writes it too (`likely`). Proposed: a constructor guess
   of a name its installed module binds in branches is no fix. Measure first: the guesses it
   withdraws on the mega corpora, and the errors gone. About an hour.
7. **A hinted step's servers given what they held** (a proposal: it changes the runs' sizing).
   basedpyright's servers abort past their heap cap (`Checker.share`: nine tenths of a server's
   share, never under `Server.memory`'s 600 MB), and each abort is a core dump the desktop reports
   as a crash. On the mega run of 2026-10-29 (`f7d53b2`, 16CPU/60GB) four came in 90 seconds, all
   inside dask's `infer-union`, given 2.47 GB (a heap cap of about 2.1 GiB) where the step held
   4.5 GB; dask's `infer-basedpyright` held 7.6 GB that run. The first mega run of 2026-10-28 had
   three, its dask `infer-union` given 2.39 GB; the second gave it 5.5 GB and had none. The cause:
   a share comes from the per-byte estimate of one server (`Plan._hinted`: 600 MB and 130 bytes
   for each byte of source, 1.3 GiB for dask's 5.9 MB), which holds for sqlalchemy (1.2 GB for 8
   MB) and undershoots dask's by about three times. Proposed, in order: a measured step's servers
   given at least what the step held on its last run (`Before.memory`, beside the estimate in
   `Wanted.hinted`), which keeps dask's at 4.5 GB or more; and basedpyright's heap floor raised from
   the bare 600 MB to one server's estimate for the files it checks (`Checker.share`), which stops
   aborts on corpora the estimate fits but whose share is split among several servers. A restarted
   server asks its files one at a time, so the step takes longer as well. Unconfirmed: that each
   abort is the heap cap (the servers' standard error isn't kept); a run with the first change
   showing no dump on dask confirms it. The mega run of 2026-10-29 at 19:20 (`e793bc6`) had none,
   sized the same way. Measure first: the dumps and dask's `infer-union` seconds on a mega run with
   it. About 2 hours; coverage unchanged.

8. **A copy of a name each branch binds to another type** (a finding: changing it narrows
   fixes). `if flag: x = 1` / `else: x = "a"`, then `y = x`, gives `y: str` as a `--likely` guess
   (`copy`), the last branch's type; `d = date(...)` / `d = datetime(...)` then `return d` a
   `datetime` where a checker takes `date`. As at HEAD. A join of the branches' types (their union,
   or the one every value fits as `rebound` takes it) would type them as a checker does, and
   withdraw or change the fixes that rest on the last branch alone. The mega runs of 2026-10-29
   have one such fix, an error in each of six steps: optuna's `params: dict[str, int | float]`,
   filled from `param`, a `str` in its other branch. Measure first: how many `copy` guesses rest
   on such a read, and what the witness says of them. About 2 hours.
9. **A `str` literal's `split()`** (a finding: changing it withdraws or retypes certain fixes).
   `macros = """a b""".split()` is fixed `list[str]` (certain, `literal+method`), but typeshed's
   `LiteralString` overload gives a literal's `split()` `list[LiteralString]`, which basedpyright
   holds invariant: "`list[LiteralString]` is not assignable to declared type `list[str]`", in a
   function or a class body alike (5 of pygments' errors with the class variables,
   [COMPLETED.md](COMPLETED.md)). mypy reads `LiteralString` as `str` and takes it. Either write
   `list[LiteralString]` (a later `append` of a `str` then fails under pyright), or leave a literal
   receiver's `LiteralString` overloads' container returns unfixed. Measure first: how many certain
   fixes it is on the mega corpora. About 2 hours.
10. **A `with` target's members in the pass that types it** (a finding). The standard library's
    `trace.py` (`f: TextIO` written before `with tokenize.open(filename) as f:`) has
    `encoding = f.encoding` typed only by a second pass: on the standard-library corpus `TextIO` is
    the checked `typing.py`'s class, read once `f` is annotated. The one second-pass line on the
    mega runs of 2026-10-29. The type comes from the tables (`entered`, `__enter__`), so the file
    spells no `TextIO` until the fix imports it, and `crossed._take` reads only the members of
    classes it spells; a round checks a file again only for late kinds (`rounds._unsettled`).
    Proposed: check a file again where a fix imports a class from a checked module whose members
    the file reads of the fixed name. Checking again every file whose fix imports a checked
    module's class would add a round to most corpora's files. About 2 hours; coverage under 0.1%.

### Medium: 4 to 8 hours

1. **A check's peak, past the resumed files.** The standard library's check in one process
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
   caller types a parameter of, known once its callers are checked. Built on 2026-10-27, the
   latter's cheap half: a check is kept only for a module whose open functions a checked file
   calls, itself included (`callers.resumable`, once for the index; `Outside.resumable`), 556 of the
   standard library's 688 modules with one; its peak 2.06 GiB from 2.15 at 48s in one process on
   16CPU/60GB (the tree after the day's changes: 2.15 where 2.03 was measured on 10-24), the listing
   identical. What's left is the resume kept from less than the whole check. About 6 hours;
   coverage unchanged.
2. **Mutation testing.** Line coverage is held at 100% (`fail_under`), so it no longer says which
   lines run without a test checking what they do; a mutant the suite survives does. How: `mutmut`
   over `constricter/`, its tests run without the corpus suites, in a `scratch/` script with its
   output under `local/`; triage the survivors and write tests for those worth killing. Done when
   a full run's survivors are each killed or recorded as equivalent. Written, not yet run:
   `scratch/mutation.py` (mutmut 3.8 on a worktree of HEAD under `local/mutation/`, the unit tests
   alone, the lines they cover, `--only` for a first pass). About 6 hours beside the run; coverage
   unchanged.
3. **A parallel check, past its longest chain.** With every CPU the standard library checks in 13.5
   and 13.9s and in 47.6s in one process (2026-10-27, 16CPU/60GB), pandas in 11.3s and 50s; 29s in
   two processes, 18s in four, 13.7s and 12.9s in eight, so about 10s of each doesn't shorten with
   more (pandas's and the scaling timed before a method's lookups were kept for a run: time them
   again first). It isn't the main process (indexing, ordering and telling the workers take 2 to 3s)
   but the order: a file waits for those whose unannotated functions it calls, 29 deep in the
   standard library, and pandas's 217 files that call each other go round up to four times before
   the other 1,200 start. Most of those edges are by a method's name alone (`loose.needs`: 12,704 of
   the standard library's, to 3,400 by an imported function). Tried, and slower: a worker with
   nothing to do checking files ahead of their turn, each confirmed when its turn came (16.0s from
   14.4s: most are checked twice, and 25 of pandas's findings then differed). Left to try: an edge
   only where the receiver's class is known to be the other module's; and a file checked again from
   where its first check ended when what it imports returns anew, as it is when its parameters are
   typed. Done when the standard library checks in under 9s with every CPU, its findings the same.
   About 8 hours; coverage unchanged. Measured 2026-10-23 (`scratch/order_edges.py`, the check order
   rebuilt as `order.plan` builds it): the method-name edges make every long chain, pandas's 224
   files (39% of its bytes) and the standard library's 84, 6 and 14 without them; keeping one only
   where a class the file names has the method keeps 9,155 of pandas's 9,182 and 13,024 of the
   standard library's 13,091 (`import pkg` names every class of the package), and an edge by the
   receiver's class at check time can't keep the output the same. With the method-name edges dropped
   from the order the standard library checked in 11.4 and 11.6s on 2026-10-27, so the order holds
   2s of the 13.5, and the other 8.5 over the 3s of CPU time shared out are the main process (the
   index, 2 to 3s), the workers' start and the largest files; the 9s bar isn't the order's to meet.
   Tried on 2026-10-27, and no faster: those edges dropped with workers, and the files calling a
   method by its name checked again once the order was done, where what they import returned anew,
   then those reading what changed. The standard library's findings were the same as the ordered
   check's and one process's, but it took 13.3s against 13.4s with every CPU (16 workers, forked
   inside the sandbox, on 16CPU/60GB), and 13.0s with every file's check kept for a resume: the late
   rounds offered 1,255 files and checked 345 again, 2.4s, the order's 2s back, where 11 files'
   findings differ without the edges. What's left of that path is a recheck only where a binding
   with no fix waited on the method now known, which a check's results don't name: their reasons are
   kinds (`member`, `receiver`), not the class and method.

### Large: more than 8 hours

1. **Types observed at run time, past what a parameter gives.** `python -m constricter.trace`
   records what each binding of a function's locals held, by statement, through pytest-xdist's
   workers and django's `runtests.py`, and `--infer-from` takes it ([done](COMPLETED.md#--fix)) only
   for a local a statement binds to a value taken from a parameter no checker types, or from an
   attribute of `self` its class stores only such parameters in. Hints for every local brought 32
   new basedpyright errors with 127 fixes on pydantic (a checker types the value wider than the run
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
   the mega corpora's suites. About 10 hours; coverage down by the traced fixes withdrawn. On the
   mega run of 2026-10-29 at 22:41 (`d160aa8`) 6 of the 462 new type errors are a traced fix's, of
   3,206 such fixes: `fk` and `index` as above, pint's 2, and nibabel's 2; `loc` and altair's are
   gone. Built on 2026-10-30: a `@classmethod`'s first parameter is its class by any name
   (`traced._receivers`), so nibabel's `file_map = klass.filespec_to_file_map(filename)`, declared
   to return a `Mapping`, has no traced `dict[str, FileHolder]`: `mega-10-30-2026-0857`
   has 17 traced fixes fewer on nibabel, each in a `@classmethod` whose first parameter is `klass`, and
   that error gone, none new. Read by position, a plain method's first
   parameter would withdraw 9 of pygments' too, but a lexer's `analyse_text(text)` is made static by
   its metaclass, so `text` is a value like any other's. What's left, each a proposal, since it
   withdraws fixes:
   - **A union the function's tests exhaust**: nibabel's `value: ast.Constant | ast.UnaryOp`
     (`ascconv._get_value`), which tests `isinstance` against each member and raises past them, so
     its last test is always true to mypy (`redundant-expr`). Refuse a traced union where the
     function tests the name against every member: of 36 traced unions without `None`, this one
     brought an error.
   - **A class whose definition imports the fixed module**: pint's `quantity: Quantity`, imported
     for type checking into `numpy_func.py`, which `Quantity`'s own definition depends on through
     the numpy facet. Refuse an import added for a class whose module imports the fixed one; needs
     the index's import graph, and such cycles are common and mostly harmless.
   - **A declared type the run contradicts**: sqlalchemy's `fk: ForeignKey`, right by the run, but
     passed to `skip_fn`, declared `Callable[[ForeignKeyConstraint], bool]` where the docstring says
     each `ForeignKey` is passed. Refusing it means checking a fix against the parameter it's passed
     to, as LVA009 checks a value against its annotation.
   - `index: Index`, then `index.table`, a `Table | None` that `_verify_index_table` raises on,
     passed where a `FromClause` is declared: typing the local exposes what a body checked against
     `Any` let by, which no rule here avoids, as for a written return (the signatures item).
2. **Signatures from the project's own inference.** `returned` decides a function's return where its
   `return`s agree, `callers` an unannotated parameter every call passes one type and `fixture` a
   test's, but each types only the locals bound to them: no edit writes `-> T` on the def or `: T`
   on the parameter (`Edit` has `annotate`, `replace` and `declare`). `pyrefly infer` and
   `dmypy suggest` were measured for signatures ([done](COMPLETED.md#corpus)), never constricter's
   own certain returns written back, which turn every caller's `returned` guess in other files into
   a certain fix and give ruff's ANN201 a fix it lacks. An edit kind for the signature: `-> T` where
   the function's `return`s decide one type (a method's a guess: a subclass may return another),
   `-> None` where none returns a value, a parameter's by `callers` and `fixture` as the guesses
   they are; opt-in codes, as LVA012 is, since ruff's ANN reports the offences already. Done when
   the corpora's own type checkers find no new error after the returns alone, and `--fix` on pandas
   gains the callers' fixes the written returns make certain. Built in part, not yet run: LVA014
   (opt-in), a plain function's or method's missing return type, its fix `-> T` before the header's
   `:` (`Edit.SIGNATURE`, `rules/returning.py`) from `returned`'s types or `None`; the parameters
   (`callers`, `fixture`) still to do ([the signatures plan](plans/signatures.md) has the rest). On
   pydantic (2026-10-24, `--fix --unsafe-fixes --extend-select LVA014`): 34 functions reported, 31
   fixed (29 `-> None`, 2 `-> str`; 29 of them methods' guesses), the other 1,596 fixes the same,
   `pyright pydantic` 0 errors as without, and its 12,311 tests passing. Built on 2026-10-26: LVA015
   (opt-in), a parameter's `: T` from what typed it for the function's own check (`callers`,
   `reads`, `fixture`, `named`; `rules/parameters.py`), a guess resting on that mechanism; LVA014's
   fix a guess where the `return`s' values are guessed (`return Box()`), resting on their kinds,
   which `--likely` and `unsafe-fix-select` weigh (before, a module function's was written certain:
   `_lazy_re_compile`'s `-> SimpleLazyObject`, a `constructor`); and a signature written reaches the
   other files in the same run (`rounds._reaching`: the file indexed again, its callers checked
   again), so what a declared return makes certain needs no second pass. Measured on django
   (`scratch/signatures_measure.py django --select LVA014,LVA015 --modes certain,likely,unsafe,signed`:
   a copy fixed pass after pass until a pass fixes nothing, one process on 16CPU/60GB, 6 to 21s a
   pass; `--coverage`'s first bindings, of 17,181):

   | Mode                                                        | Plain | With the codes | Signatures written |
   | ----------------------------------------------------------- | ----: | -------------: | -----------------: |
   | `--fix`                                                     | 2,627 |          2,637 |                247 |
   | `--fix --likely`                                            | 3,273 |          3,414 |                557 |
   | `--fix --unsafe-fixes`                                      | 5,413 |          5,460 |        3,476 + 605 |
   | `--fix --unsafe-fixes --select LVA014,LVA015`, then `--fix` |     — |          2,956 |        3,467 + 467 |

   The last row is the workflow the codes are for: the signatures written first (every guess among
   them, 3,467 returns and 467 parameters, in one pass of 21s), plain `--fix` then types 2,956, 329
   more than without them (12.5% of its fixes), and a second pass finds nothing. `--likely` gains
   141 since LVA014's guesses carry their `return`s' kinds (`constructor+returned`, a likely set).
   Before the guess fix, `--fix` with LVA014 gave 2,737: 100 of them from a guessed return written
   as certain. Left: under `--unsafe-fixes` 138 of the parameter fixes come only on a second pass (a
   guess written on a caller's argument is a known type for `callers` on the next pass: the second
   row's pass 2 to 4, 150 fixes), which a recheck after writing guesses would bring in
   (`rounds._unsettled` does it with `--likely` alone). Read again on 2026-10-30 from that
   measurement's own listings (`--show-fixes`, each pass's, the tree of 2026-10-26): of
   the 135 LVA015 fixes its second `--unsafe-fixes` pass made, 128 are `named`, a name the first
   pass's own parameter fixes brought to `AGREED` annotations, and 7 `callers`. A recheck would
   have `named` count its own guesses as the project's annotations, so it isn't built, and 7
   `callers` fixes are too few to build one for. And LVA015's reach is the seeds', 1 of
   `--unsafe-fixes`' 5,408 binding fixes on django resting on one before the codes. The roadmap's 10
   hours spent; coverage: `--fix` +12.5% on django after a signatures pass, the `--unsafe-fixes` row
   under 1%. On the mega run of 2026-10-26 (`mega-10-26-2026-2120`, 98 minutes on 16CPU/60GB, the
   signature codes in every fix step): bindings typed, of 474,291, `--fix` 161,191 from 161,134,
   `--likely` 211,563 from 210,156, `--unsafe-fixes` 229,556 from 227,933; but the new type errors
   54,366 from the 0.4.3-rc.8 mega run's 403 (`--fix` 1,145 from 1, pandas 1,002; 25,063 untraced to
   a line with a fix, a signature written in another file), and the witness blames 893 certain fixes
   of 49,840 checked (1.79 in each 100; 1 of 42,073 before): a return written on the def constrains
   every caller and every override where a local's annotation constrained one binding, and mypy's
   incomplete-def check fires on sqlalchemy where a return is written on a function whose parameters
   stay bare. The signatures-first workflow stands for a project that reviews them; as a step of the
   fix runs they fail the bars, so the run files select them no more (the same day). Built the same
   day: a signature written whole or not at all (`rules/signatures.py`), a function's fixes held
   back until every parameter but its receiver and its return are annotated or fixed, which was most
   of the errors blamed on `reads` and `named` (mypy's incomplete-def check, overrides); what a
   return alone exposes in a body mypy didn't check (pandas's tests, `check_untyped_defs = false`
   there) no rule here avoids. Under it, django's signatures-first workflow writes 931 returns and
   81 parameters (from 3,467 and 467), and `--fix` then types 2,749 bindings from 2,627 (+122, from
   +329). Left: the codes' errors read on a run with them again, if they're to go back into one. On
   the mega run of 2026-10-27 (`mega-10-27-2026-0131`, 91 minutes on 16CPU/60GB, the signature codes
   out of the run files): bindings typed, of 474,291, `--fix` 161,111, `--likely` 210,548,
   `--unsafe-fixes` 229,024 (rc.8's 161,134, 210,156 and 227,933); new type errors 5,927, 5,516
   sqlalchemy's from `typing_extensions` read as an untyped package ([COMPLETED.md](COMPLETED.md)),
   411 elsewhere (rc.8's 403). The witness there: `constructor` fails the bars only through the
   cascade (183 of its 199 blamed errors sqlalchemy's); `method` 2 blamed of 1,047 (0.19 in each
   100, the bar 0.1), nibabel's as on rc.8 and pandas's new since (read under the built items).

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
2. **Two checkers agreeing, likely.** `checker` is one set to LIKELY.md's bars, by checker; a hint
   basedpyright, ty and pyrefly agree on (two of them, or all three) is a set of its own, measured
   the same way, and `--likely` applies it where one checker's hint alone doesn't pass. Done when
   the mechanisms table counts the agreeing sets. Built: where a later checker's usable hint gives
   the type the first usable one does, the fix rests on their agreement too (kind `agreed`, beside
   `checker`; `Scope.hint`), a set of its own in the mechanisms table; not in `--likely` until it
   passes the bars, and not what a guess rests on: `unsafe-fix-select` trusts it by `checker` as
   before. On the 0.4.3-rc.8 mega run (`7a075e4`, 16CPU/60GB, 70 minutes): 14,941 of `infer-union`'s
   26,590 checker fixes rest on an agreement, read from its records; the mechanisms table lists the
   union step's sets since the mega run of 2026-10-27 (`agreed+checker` 14,861). The bars can't be
   read from a run yet: the witness judges `fix-unsafe`'s fixes alone (`traced.verdicts.jsonl`) and
   no type check runs after `infer-union`. Held by name to what the trace saw instead
   (`scratch/agreed_seen.py`: every type seen named in the annotation), `agreed+checker` held 86.2%
   of the 9,635 the trace told of and `checker` alone 73.7% of 5,321, where the union's certain
   fixes held 90.2% by name (99.5% by the witness: a subclass or a protocol differs by name). Left:
   the witness judging the union's fixes too, and a type check after it, then the sets held to the
   bars. About 3 hours beside a run; coverage unchanged (`--likely` gains what passes).
3. **pyrefly's `stubgen` for untyped packages.** For an installed package with no types, pyrefly
   writes stubs from what it infers (experimental; `Incomplete` where it can't tell): the calls
   declared types would reach plus the returns no source declares (tlz, botocore, kombu), perhaps
   600 direct calls. Read as guesses, as an installed package's stubs are, held to the witness. Done
   when measured on dask's and xarray's environments against the installed stubs' baseline. Measured
   on 2026-10-28 (`scratch/stubgen_measure.py`, pyrefly 1.3.2, one process on 16CPU/60GB): each
   untyped package stubbed as a `-stubs` package (pandas 23,928 returns concrete and 1,176
   `Incomplete`, pyarrow 2,881 and 441, fsspec 596 and 266, toolz, tlz, yaml), and
   `--unsafe-fixes --show-fixes` listed with and without them. dask: 5,864 fixes from 5,815 (certain
   3,152 from 3,120, likely 1,867 from 1,769, guesses 845 from 926; 104 gained, 55 lost, 38
   changed), most `DataFrame` and fsspec's `OpenFiles`, the lost the `declared` guesses the stubs
   stand in for (`DatetimeIndex` 13). xarray, pandas and yaml stubbed: 6,999 from 7,018 (certain
   3,641 from 3,557, 67 of them `pd.MultiIndex`; guesses 261 from 384, 84 `DatetimeIndex`). Under 1%
   either way, and the certain ones rest on pyrefly's inference, which the index reads as a stub's
   declared types: built, they'd need a kind of their own, a guess. Against pandas-stubs on
   2026-10-28 ([COMPLETED.md](COMPLETED.md)), the generated stubs gained fewer certain fixes and
   lost fewer guesses. Left: whether to build it. About 3 hours spent; coverage under 1%.
4. **Framework plugins' types.** django-stubs' and pydantic's mypy plugins type what the frameworks
   make at run time (a model's fields, a manager's querysets), but only inside a mypy run. About 0
   calls in the corpora reach them. Done when measured on django's tests through mypy's
   `reveal_type` or a plugin's own output, or recorded as out of reach. About 3 hours; coverage
   unknown until measured.
5. **typeshed's third-party stubs, not installed.** basedpyright ships them
   (`typeshed-fallback/stubs`, 201 sets): 18 of the top 100 PyPI packages are typed only there
   (pyyaml, python-dateutil, six, protobuf, grpcio, jsonschema, tqdm, pytz, regex, ...). Certain
   where the installed version matches `METADATA.toml`'s, a guess where not. Its reach is users'
   code. Measured on the 0.4.3-rc.8 mega run's census (`scratch/typeshed_reach.py`): of 7,955
   third-party bindings with no fix, 137 at most call into a package a stub set covers (docutils 43,
   pywin32 35, PyYAML 13, python-dateutil 7), some of them where the stubs are installed already.
   Done when decided: built for users' code, or left at under 0.1% on the corpora. About 4 hours to
   build.
6. **numpydoc Returns sections.** Built for a builtin scalar alone as `documented` (above). A
   docstring's `Returns` section names what a function with no return annotation returns (docstub
   and docs2stubs read them): networkx has 2,301 such functions, 868 with a Returns section and 485
   naming one plain type; pandas 1,787 (360, 108), dask 3,912 (181, 56), xarray 1,088 (60, 38). Many
   names are vague (`dictionary`, `graph`), and `nx.path_graph`, the most called (460 calls), has
   none: under 1,000 usable. A guess, a docstring's name resolved where the module would resolve it,
   held to the witness. Done when measured on networkx and pandas. About 4 hours; coverage under
   0.5%.
7. **Types from a model.** Type4Py, TypeWriter, DLTPy, Typilus, HiTyper, TypeT5 and TypeGen predict
   types (TypyBench and TypeEvalPy score them), but none is deterministic, and each needs a model
   or an API. Only as a file `--infer-from` reads, through the hint filter and the witness, as any
   guess is. Done when one is measured on pydantic against the checkers' hints: the fixes, the new
   errors. About 6 hours; coverage unknown until measured.

## Ongoing

- **Revisit the [disabled rules](CONTRIBUTING.md#disabled-rules)** as tools change (last checked
  2026-10-28: `ossf/scorecard-action` v2.5.0 is taken, so zizmor's `self-repository` now waits on
  actionlint, whose newest, 1.7.12, rejects `$/`; harden-runner's block policy on macOS and Windows
  waits on the other repos' shared workflows, as one batch; astroid 4.3.4 still ships no `py.typed`,
  and fastjsonschema 2.22.2 and reuse 6.2.0 are as before). About an hour a pass.
