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

The latest run is `mega-11-06-2026-2039` (`edcaba3`, 87 minutes, 16CPU/60GB), read for
`documented`'s bars and the `LiteralString` splits, with `vague-11-06-2026-2206` beside it for the
`vague = 0` census (both in [COMPLETED.md](COMPLETED.md#corpus)); before them
`mega-lva013-11-06-2026-1718` (`2843438`, 56 minutes) for LVA013; the latest read in full is
`mega-11-06-2026-0441` (`fa5cbd5`, 85 minutes;
[COMPLETED.md](COMPLETED.md#corpus)). A basic run of the seven corpora, `basic-11-03-2026-2103`
(`8c3a756`, [basic-corpora.md](runs/basic-corpora.md)), takes 35 minutes on 16CPU/60GB, from 0.3.8's
58; a mega run's 85 buys the other 40 corpora. A change to what `--fix` offers or refuses is read on
all 54 in 10 minutes by `mega-fixes` (`tests/corpus/runs/mega-fixes.toml`: the fix steps and type
checks alone, against the latest mega run's records with `scratch/run_fixes_diff.py`, or the latest
`alt` run's for its seven; `mega-fixes-11-08-2026-1251`, 10 minutes), which measures none of the bars: a guess's bars and the
tests still wait on a mega run.

1. **Runs in stages.** Built in `88e0dda`: a run's steps fall into stages run one at a time into
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
   stages hours apart, with other work between. About an hour beside the runs.
2. **A run with no earlier run, held to the solver's shortest.** The runner's schedule is within a
   tenth of the solver's shortest for a super and a mega run sized by earlier runs, and a step no run
   measured is planned by its like corpora (`planning.like`; both in [COMPLETED.md](COMPLETED.md#corpus)).
   Every run file writes under `corpus-runs/`, whose reports keep each step's use, so a run
   meets none of its steps measured only under a new `output`, and a new corpus or step is unmeasured
   within a measured run. Left: a run with a corpus new to its output, read against
   `scratch/schedule_solve.py` on its own records: the first run of `alt`
   (`tests/corpus/runs/alt.toml`) or the next super or mega run, which meets the seven corpora added
   unmeasured (requests, rich, trio, urllib3, langchain-core, sqlmodel and marshmallow, grouped by
   their files alone; their suites not yet run here). Done when it takes within a tenth of the
   shortest schedule of its own records. A run in stages plans each stage's steps alone since
   (`planning.ranks`'s `chosen`), read with "Runs in stages". About an hour beside the run; coverage
   unchanged.

### Small: under 4 hours

1. **A module's own class named as a typing generic** (a finding). numpy's `default_rng()` declares
   `-> Generator`, its own `numpy.random.Generator`, and gets no fix ("imported"): a bare
   `Generator` return is read as typing's, vague without its arguments (`source.annotations`), so
   `_generator.pyi` gives no return at all (`declarations.returns`). On `mega-11-06-2026-2039` 75
   `numpy.random.default_rng` bindings have no fix. Done when a return naming a class its module
   defines, or imports from outside `typing` and `collections.abc`, isn't read as the generic of
   that name. About 2 hours, for about 0.03%.
2. **A hinted step's servers given what they held** (a proposal: it changes the runs' sizing).
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
   sized the same way. Decided 2026-11-06: not built until a run dumps again; then measure the dumps
   and dask's `infer-union` seconds on a mega run with it. About 2 hours; coverage unchanged.
3. **A receiver typed in the same pass, its method's call left to a second** (a finding).
   `alt-11-08-2026-1133` (`fix-certain`): a second pass would still fix 4 in trio and 1 in rich. In
   trio's `_tests/test_highlevel_open_tcp_listeners.py`, the first pass declares
   `listener: trio.SocketListener = listeners[0]` (itself `listeners: list[trio.SocketListener]` that
   pass) but leaves `s1 = await listener.accept()`, which the second types `SocketStream`; in rich's
   `jupyter.py`, the loop target `style` of `for text, style, control in Segment.simplify(...)` is
   declared `Optional[Style]`, and only the second pass types `rule = style.get_html_style(theme)`
   under `if style:`. Each is a method's call on a receiver whose type the first pass found but no
   annotation yet stated; not yet traced (the rounds, `cli/rounds.py`, first). Done when one pass
   leaves nothing for a second on the `alt` corpora (the runner's "a second pass would still fix").
   About 3 hours; coverage about unchanged, its fixes made one pass sooner.

### Medium: 4 to 8 hours

1. **Mutation testing.** Line coverage is held at 100% (`fail_under`), so it no longer says which
   lines run without a test checking what they do; a mutant the suite survives does. How: `mutmut`
   over `constricter/`, its tests run without the corpus suites, in a `scratch/` script with its
   output under `local/`; triage the survivors and write tests for those worth killing. Done when
   a full run's survivors are each killed or recorded as equivalent. Written, not yet run:
   `scratch/mutation.py` (mutmut 3.8 on a worktree of HEAD under `local/mutation/`, the unit tests
   alone, the lines they cover, `--only` for a first pass). About 6 hours beside the run; coverage
   unchanged.
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
   caller types a parameter of, known once its callers are checked. Built on 2026-10-27, the
   latter's cheap half: a check is kept only for a module whose open functions a checked file
   calls, itself included (`callers.resumable`, once for the index; `Outside.resumable`), 556 of the
   standard library's 688 modules with one; its peak 2.06 GiB from 2.15 at 48s in one process on
   16CPU/60GB (the tree after the day's changes: 2.15 where 2.03 was measured on 10-24), the listing
   identical. What's left is the resume kept from less than the whole check. Each timing here predates the
   changes since 2026-10-28: time it again first. About 6 hours; coverage unchanged.
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
   Each timing here predates the changes since 2026-10-28: time them again first.
4. **A checked package's own stubs.** A package may ship a stub beside its source (`axes/_axes.pyi`
   beside `axes/_axes.py`), which a type checker reads for every importer, and a stub alone for each
   compiled module (`_path.pyi`). `--fix` reads stubs only for installed packages (stub before
   source, `stubs.installed`); in a checked tree it reads the `.py` alone and never the `.pyi`. In
   matplotlib 3.11.2's sdist (`scratch/stub_pairs.py`), 78 of its 179 modules (tests aside) have a
   stub beside them and 9 compiled ones a stub alone; the 4,325 functions of those 78 declare 2
   returns, and their stubs declare about 2,976 more by name. How: a checked module's stub taken
   before its source for its importers' returns, classes and methods (as an installed module's is),
   and the stub's declared returns read for the source's own calls, a lone stub as its compiled
   module. Done when matplotlib, added as a corpus (its sdist alone at first: its build needs meson
   and a C++ toolchain), types its importers' calls by its stubs and its fixes add no new type
   error. Measure first: matplotlib's bindings with no fix that call a function its stub declares.
   About 6 hours; coverage on the corpora small, its reach a stub-shipping package's users.

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
   that error gone, none new: 5 of its 461 new type errors are a traced fix's (`fk`, `index`, pint's 2,
   nibabel's `value`); on `mega-11-05-2026-0219` the same 5 of 450. Read by position, a plain method's first
   parameter would withdraw 9 of pygments' too, but a lexer's `analyse_text(text)` is made static by
   its metaclass, so `text` is a value like any other's. What's left, each a proposal, since it
   withdraws fixes; decided 2026-11-06, none built for now, the first the one worth building:
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
     `Any` let by, which no rule here avoids, as for a written return (the signature codes,
     [COMPLETED.md](COMPLETED.md#corpus)).
2. **A method's `return` of an untyped value.** Of the 11,959 `self.method()` bindings with no fix,
   5,617 call a method the class doesn't define itself, and 5,436 one whose `return` gives a value
   `--fix` can't type: a tuple (1,858), a call (1,455), a local or another name (1,396), a subscript
   or attribute (272). Only 137 return an unannotated parameter (26 nothing else), and in none of
   those classes does every `self.method(...)` call pass it a literal: typing a method's parameters
   by its callers, as `callers` types a plain top-level function's (3 fixes on pandas), reaches
   almost none of them. What's left is the values themselves: the tuple's parts, the call, the
   local. Done when a method returning its parameter types its calls. About 14 hours, for about 0.3%
   (some 800 guesses).
3. **Annotations held to a run.** The corpora's witness holds each fix to the values its package's
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

1. **Framework plugins' types.** django-stubs' and pydantic's mypy plugins type what the frameworks
   make at run time (a model's fields, a manager's querysets), but only inside a mypy run. About 0
   calls in the corpora reach them. Done when measured on django's tests through mypy's
   `reveal_type` or a plugin's own output, or recorded as out of reach. About 3 hours; coverage
   unknown until measured.
2. **Types from a model.** Type4Py, TypeWriter, DLTPy, Typilus, HiTyper, TypeT5 and TypeGen predict
   types (TypyBench and TypeEvalPy score them), but none is deterministic, and each needs a model
   or an API. Only as a file `--infer-from` reads, through the hint filter and the witness, as any
   guess is. Done when one is measured on pydantic against the checkers' hints: the fixes, the new
   errors. About 6 hours; coverage unknown until measured.

## Ongoing

- **Revisit the [disabled rules](CONTRIBUTING.md#disabled-rules)** as tools change (last checked
  2026-10-31: `ossf/scorecard-action` v2.5.0 is taken, so zizmor's `self-repository` now waits on
  actionlint, whose newest, 1.7.12, rejects `$/`; harden-runner's block policy on macOS and Windows
  waits on the other repos' shared workflows, as one batch; astroid 4.3.4 still ships no `py.typed`,
  and fastjsonschema 2.22.2 is as before; reuse 6.3.0 ships a wheel at last, and `reuse lint` is
  back on). About an hour a pass.
