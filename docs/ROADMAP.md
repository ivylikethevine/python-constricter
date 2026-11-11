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

The latest run is `mega-11-11-2026-1113` (`855c719`, 95 minutes, 16CPU/60GB), read for the checkers'
hints by a copy's own settings and environment ([COMPLETED.md](COMPLETED.md#corpus)); before it
`mega-11-10-2026-2235` (`565ac6c`, 80 minutes), read for `echoed`, the hinted steps' fixes with a
corpus's stubs in the copy, and the suites' tests and checks, and `mega-11-10-2026-1742` (`d072990`,
82 minutes), for the hinted steps' servers alone. Before them `mega-11-06-2026-2039` (`edcaba3`, 87
minutes), read for `documented`'s bars and the `LiteralString` splits, with `vague-11-06-2026-2206`
beside it for the `vague = 0` census (both in [COMPLETED.md](COMPLETED.md#corpus)); before them
`mega-lva013-11-06-2026-1718` (`2843438`, 56 minutes) for LVA013; the latest read in full is
`mega-11-06-2026-0441` (`fa5cbd5`, 85 minutes; [COMPLETED.md](COMPLETED.md#corpus)). A basic run of
the seven corpora, `basic-11-03-2026-2103` (`8c3a756`, [basic-corpora.md](runs/basic-corpora.md)),
takes 35 minutes on 16CPU/60GB, from 0.3.8's 58; a mega run's 80 to 95 buys the other 48 corpora. A
change to what `--fix` offers or refuses is read on all 55 in 12 to 14 minutes by `mega-fixes`
(`tests/corpus/runs/mega-fixes.toml`: the fix steps and type checks alone, against the latest mega
run's records with `scratch/run_fixes_diff.py`, or the latest `alt` run's for its eight;
`mega-fixes-11-11-2026-1033`, 14 minutes), which measures none of the bars: a guess's bars and the
tests still wait on a mega run.

#### 1. Runs in stages

Built in `88e0dda`: a run's steps fall into stages run one at a time into one folder
(`tests/corpus/stages.py`): built in `fixes`, `traced`, `tests` and `timed`, regrouped by a run
file's `[stages]` table. `--stage NAME` runs that stage's steps alone, a step needing a stage still
to run left for it; the report is written from the records so far, naming the stages left, and
published once every stage is in. A stage on another commit, other uncommitted changes or another
run file than the folder's earlier stages is refused, naming both, unless `--join-anyway`, and the
report then gives each stage's commit. Done when a super run made in four stages at separate times
gives the report one sitting does. Coverage unchanged. The 0.4.3-rc.3 super run (`ac48774`,
16CPU/60GB) ran its four stages back to back into one folder: `fixes` 17 minutes, `traced` 15,
`tests` 12, `timed` 4, 48 in all as rc.2's one sitting took; each joined, and the report and RUNS.md
were written once the last was in. The 0.4.3-rc.4 super run (`46bdc27`) ran them with 90s between:
`fixes` 16.5 minutes, `traced` 11, `tests` 20.5, `timed` 4, each exiting 0 and joining, the report
naming one commit for all four. Left: stages hours apart, with other work between. About an hour
beside the runs.

#### 2. An environment of its own for a corpus with no checkout

The six corpora checked from an sdist (the standard library, twisted, pip, textual, stripe,
matplotlib) had no environment: constricter and the checkers `--infer-with` starts read the dev
venv's packages for them, which hold pandas, numpy, django and sqlalchemy and no Pillow, where a
suite's corpus reads its own ([COMPLETED.md](COMPLETED.md#corpus), a copy's checkers). Built
2026-11-11: each has a venv beside its unpacked source (`corpus_suite.own_environment`, made by
`trees.found`) with what its entry `requires` (`corpora.toml`): itself where it installs on this
Python (textual, stripe, matplotlib), which brings what it depends on; `zope.interface` for twisted,
whose 12.3.0 is Python 2's; nothing for pip, which vendors what it needs, or the standard library. A
copy of matplotlib fixed with guesses in one process (`scratch/second_pass_copy.py`, 61 seconds with
1 worker on 16CPU/60GB) has 10,287 fixes from 10,266, 4 gone and 25 new, the new ones by Pillow's
types (`im: Image.Image`, `img: ImageFile.ImageFile`), and leaves a second pass none; by
`scratch/checker_roots.py` ty reads each one's own environment. What a requirement brings isn't
pinned: an environment holds what resolved the day it was made. Waits on a mega run (95 minutes on
16CPU/60GB), read against `mega-11-11-2026-1113`: done when the six corpora's fixes, new errors and
second passes are recorded. Coverage: the six corpora's fixes move, by how much unknown until it
runs.

### Small: under 4 hours

#### 3. sqlalchemy's four `test_compare` failures after `infer-union`

On `mega-11-10-2026-2235` sqlalchemy's suite fails four tests after `infer-union` and after no other
step: `test/sql/test_compare.py`'s `CacheKeyTest::test_cache_key`, and `CompareAndCopyTest`'s
`test_all_present`, `test_compare_labels` and `test_copy_internals`. They failed in that step on
`mega-10-29-2026-2241` and `mega-11-05-2026-0219` too, and passed in it on the seven mega runs since
2026-10-30 that aren't these, `mega-11-11-2026-1113` the latest, with 9, 13, 14 and 16 workers where
it failed with 10 and 11. Found 2026-11-11, and no fix's: the suite's own order.
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
(`suite_steps.weighed`); the union's tests run once, so its report lists the four as new. Left, each
a proposal, since it changes what a run reports: the four named in the catalog
(`[corpus.sqlalchemy.suite.differs]`), or the union's tests run again as a fixed step's are. About
an hour for either; coverage unchanged.

#### 4. A generic alias hinted without its arguments

mcp's `outcome: ElicitationResult` and `dep_outcome: ElicitationResult`
(`server/mcpserver/resolve.py`, by pyrefly's hint) name a generic alias with no arguments, one made
by a call (`ElicitationResult = TypeAliasType("ElicitationResult", ..., type_params=(T,))`): its own
Pyright asks for them (`reportMissingTypeArgument`), 12 of mcp's 26 new type errors on
`mega-11-11-2026-1113`, where the run before had 10 in all. A generic class and a `type X[T] = ...`
alias aren't written bare (`Module.generics`, `modules._aliases`); an alias `TypeAliasType` makes
with `type_params` is read as a plain type (`modules._MAKERS`). Done when such an alias counts as
generic where a hint or a fix would write it bare: refused, or written with the arguments the
checker gives. About 2 hours; coverage unchanged.

#### 5. A hint's name, held to what the file binds it to

A checker's hint names a class by its bare name, and a fix writes that name where the file binds it,
to whatever. On `mega-11-11-2026-1113`, the first run whose checkers read each corpus's own
packages, sphinx's `img: Image` (`builders/_epub_base.py`) is the class `PIL.Image.Image` where the
file's `Image` is the module (`from PIL import Image`), and httpx's `resp: Response`
(`_transports/default.py`) httpcore's class where the file's `Response` is httpx's own: 24 of
sphinx's 37 new type errors and 12 of httpx's 16, by all three checkers, and likely where two agree
(`agreed`). A hint's name is to be the class the checker means, by where the hint says its type is
defined (`edits.offered`), before it's spelled for the file (`hinted._spelled`): refused where the
file binds the name to a module or to another class, or written by a name of the file's that is the
class (`Image.Image`). Done when neither hint is written as it is, and a mega run (95 minutes on
16CPU/60GB) shows those errors gone and no hint withdrawn that named its class. About 3 hours;
coverage unchanged, some dozens of guesses withdrawn or respelled.

#### 6. A run with no earlier run, held to the solver's shortest

A run whose steps are measured is at the solver's shortest, read against the waits the runner keeps:
`alt-11-08-2026-1157` took 5.2 minutes to a proved 5.2 and `alt-11-08-2026-1213` 5.5 to 5.5
(16CPU/60GB; [COMPLETED.md](COMPLETED.md#corpus)). `alt-11-08-2026-1133` (`19a3e9c`), the first run
of its seven corpora, none of its steps measured, took 7.2 minutes to a proved 6.0, 20% over, though
planned by its like corpora (`planning.like`). Its 72 seconds went to memory at the head of the
run's longest chain: trio's `infer-basedpyright` waited 65 seconds wanting 6.6 GB with 3.2 free,
each unmeasured hinted step holding a third of the run's memory between its CPUs
(`sizing._UNSIZED_SHARE`), where trio's held 0.5 GB once measured. Left, a proposal (it changes a
first run's sizing): an unmeasured hinted step sized by its checkers' servers' estimate for the
corpus's files (`Plan._hinted`'s, as a measured one's fewest CPUs are), then by what it's seen to
use (`Plan.fitted`). Done when a first run of corpora no run measured takes within a tenth of its
shortest (`scratch/schedule_solve.py --given`). A measured step can be as far off: on
`mega-11-11-2026-1113` every checker was asked afresh, each step sized by a run that read its hints
from the store, so pip's `infer-basedpyright` held 4.1 GB where it was given 0.64 and matplotlib's
8.8 where 4.28, the load 28 on 16 CPUs, and the run took 95 minutes for 80; no server passed its
heap's cap. Not looked into: whether a step whose hints were read from the store should count as
measured. About an hour beside the run; coverage unchanged.

### Medium: 4 to 8 hours

#### 7. The hinted steps' second pass

A run reports what a second pass would still fix after the certain fixes and the guesses
(`render._CONVERGING`), where no corpus is left any since a module's stub is read in every check,
not after a checker's hints, where it has long left some: 102, 76 and 84 fixes after
`infer-basedpyright`, `infer-ty` and `infer-pyrefly` on `mega-11-10-2026-1742`, and 142, 116 and 227
(180 after `infer-union`) on `mega-11-11-2026-1113`, the first with that and with each checker held
to the copy's own settings ([COMPLETED.md](COMPLETED.md#corpus)). Found 2026-11-11 on the run
between them, each in one process, which gives a run's counts (`scratch/second_pass_copy.py`).
matplotlib's, the stub's apart, rest on one fix, `get_size_in_points: Callable[..., float] =
get_size` in `font_manager.py`: the files calling it know its type only from an index read after
that fix, and with a checker's hints the files a round changed aren't indexed again
(`rounds.settled`'s `onward`); it leaves 8, 11 and 9 now. pandas has no stub beside a source (its 41
are compiled modules'). Its 29 after pyrefly's hints were 25 with eight rounds for `HINT_ROUNDS`'
four, so not the rounds' cap: 17 of the 28 fixes are a hint pyrefly gives only when asked again of
the fixed tree, where a round asks again only of the files it changed, and 11 rest on a method's
declared return or an attribute of a name such a hint typed (`DataFrameGroupBy.filter`); measured
before pyrefly read the copy's own settings, it leaves 24, 24 and 28 now. Not looked into: pyrefly's
46 on pint, 32 on pip and 25 on django, none on the run before, and what's as old as a corpus's
first hinted run (the standard library's 39 after pyrefly's hints, pint's 15 to 19 after the
others'). Left, a proposal, since it adds checks to every hinted run: the files a hinted round
changed indexed again, and every file asked of again while a round brings a new hint. Done when a
mega run (95 minutes on 16CPU/60GB) shows the hinted steps leaving matplotlib and pandas no more
than `mega-11-10-2026-1742` did (4, 6 and 0; 23, 21 and 25) and pyrefly's new ones are traced. About
4 hours; coverage unchanged.

#### 8. Annotations held to a run

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
OR-Tools' status enum cast to `int` (`planning.solved`). Traced, 8 more of the suite's tests fail
than untraced, the tracer's own among them, not looked into. Left: those 11, each widened or the
cast kept and the report given a way to pass one over, which is to decide; a `*args`' and a
`**kwargs`' elements, a coroutine's return, and a class's and a module's annotated variables; and
LVA016 named where the other codes are (`--explain`, the README's table) if it's to stay a code.
About 4 hours; coverage unchanged: it finds wrong annotations, not missing ones.

#### 9. Mutation testing

Line coverage is held at 100% (`fail_under`), so it no longer says which lines run without a test
checking what they do; a mutant the suite survives does. How: `mutmut` over `constricter/`, its
tests run without the corpus suites, in a `scratch/` script with its output under `local/`; triage
the survivors and write tests for those worth killing. Done when a full run's survivors are each
killed or recorded as equivalent. Written, not yet run: `scratch/mutation.py` (mutmut 3.8 on a
worktree of HEAD under `local/mutation/`, the unit tests alone, the lines they cover, `--only` for a
first pass). About 6 hours beside the run; coverage unchanged.

#### 10. A check's peak, past the resumed files

The standard library's check in one process (2026-10-24, 16CPU/60GB, `scratch/peak_rss.py`) peaked
at 2.65 GiB: every file's tree, and its whole finished check (scopes, bindings, inferences: 84,624
scopes), kept for a second round that resumes 242 of its 1,867 files. Both are now kept only for a
module with an open function, the only one a resume can start from (the others checked again, 33,
are parsed again), and a module's own node no longer keeps its tree in the shared walk: 2.03 GiB at
41.2s, from 40.5s, findings the same on the standard library, pydantic and pandas
(`scratch/equivalence.sh`). What's left, each weighed: no check kept at all, 1.97 GiB for 46.3s (the
resumed files start over); the index keeping only the resumable files' trees too, 2.00 GiB for 43.6s
(the peak is the index's end, 1.59 GiB of trees, and what the check frees is reused, not returned);
no tree kept anywhere, 3.43 GiB for 52.4s (each tree parsed again and the resumes lost). Also
weighed and left: `msgspec` or `orjson` for the pickled index, more `__slots__`, `sys.intern` of the
annotations' text. Measured by phase on 2026-10-24 (`scratch/peak_phases.py`, its memory sampled
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

#### 11. A parallel check, past its longest chain

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
every CPU, its findings the same. Measured 2026-10-23 (`scratch/order_edges.py`, the check order
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

### Large: more than 8 hours

#### 12. Types observed at run time, past what a parameter gives

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

What to measure before building, smallest first.

#### 13. Two checkers' agreement, read again

A hint two checkers give alike is likely (`agreed+checker`): on `mega-11-06-2026-0441` it passed
[LIKELY.md](LIKELY.md)'s three bars, 97.9% of 9,149 told held and 8 of 10,081 read blamed (0.08 in
each 100). On `mega-11-11-2026-1113`, each checker reading the corpus's own settings and
environment, the suites' own checks blame 35 new errors on it, 14 on the run before (sphinx 7,
narwhals 5, httpx 4): the checkers agree more often, and on the same wrong name ("A hint's name"
above). Done when its guesses are read against that run's verdicts and type checks
(`scratch/guess_report.py --step infer-union`): whether it still passes the bars, and with the two
names above set aside. About an hour; if it fails a bar, `agreed` leaves the likely fixes, which is
to decide.

#### 14. Types from a model

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

## Ongoing

- **Revisit the [disabled rules](CONTRIBUTING.md#disabled-rules)** as tools change (last checked
  2026-10-31: `ossf/scorecard-action` v2.5.0 is taken, so zizmor's `self-repository` now waits on
  actionlint, whose newest, 1.7.12, rejects `$/`; harden-runner's block policy on macOS and Windows
  is on in `ci.yml` and waits, for `build.yml`'s wheels, on a run outside a release; astroid 4.3.4
  still ships no `py.typed`, and fastjsonschema 2.22.2 is as before; reuse 6.3.0 ships a wheel at
  last, and `reuse lint` is back on). About an hour a pass.
