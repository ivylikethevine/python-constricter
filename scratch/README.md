# Scratch

One-off scripts that measured something once and may be worth running again. None is linted, typed
or tested; delete any freely. Each says in its docstring what it does and how to run it, from the
repository's root with `local/.venv/bin/python -m scratch.NAME`, outside a sandbox. What they write
goes under `local/scratch/`.

- `guess_report.py --from FOLDER`, a corpus run's folder with its `guesses.jsonl`: every guess the
  run made on the suites, by mechanism, with the type errors blamed on it and what its binding held
  at run time. `guess_report.py --likely` lists the sets that pass `docs/LIKELY.md`'s bars.
- `agreed_seen.py FOLDER`: a run's `infer-union` fixes held by name to the types its traced tests
  saw, by set of mechanisms, the certain fixes' share first; the witness judges `fix-unsafe` alone.
- `pack_run.py DEST FOLDER...`: archived run folders packed as `corpus-runs/` commits a run's: its
  report, tables and facts, and each listing gathered into one file, every text scrubbed.
- `typeshed_reach.py FOLDER`: a run's third-party bindings with no fix that call into a package
  typeshed's third-party stubs cover, by stub set and by the census's reason.
- `signatures_measure.py CORPUS [--modes certain,likely,unsafe,signed] [--select LVA014,LVA015]
  [--passes N] [--jobs N] [--label NAME]`: a copy of a corpus fixed pass after pass until a pass
  fixes nothing, each mode with and without the signature codes, and `signed` (the codes' fixes
  written first, then `--fix`): each pass's fixes split certain, likely and guess, the signatures
  written, and `--coverage` after; each pass's listing kept under `local/scratch/signatures/`.
- `fix_diff.py [REF]`: the fixes `--show-fixes --unsafe-fixes` lists on the installed pydantic by
  REF's code (HEAD) and by the working tree's, and those only one side has.
- `widen_pass.py`: what a second pass still fixes on each corpus after every `fix-widen` kind.
- `second_pass.py [CORPUS ...] [--likely | --certain]`: what a second pass still fixes on each
  corpus after `--fix --unsafe-fixes` (or `--likely`, or neither), as CI's `ci-fix` run counts it,
  each diff kept.
- `hinted_second_pass.py CHECKER CORPUS ...`: the same after a run's `infer-CHECKER` step, on a
  copy laid out as the corpus's checkout with its environment, the listing and the diff kept.
- `widen_suites.py`: each suite's tests as released and after every `fix-widen` kind.
- `widen_one.py`: one suite's tests after every `fix-widen` kind, their output and the diff kept.
- `witness_checkers.py`, with `typeguard` and `beartype` on `PYTHONPATH`: values held to annotations
  by the witness's `holds`, typeguard and beartype, where each differs from a type checker, whether
  it runs the value's own code, and what each costs.
- `timing_trial.py [CORPUS ...] [--runs N] [--jobs N]`: a corpus's check timed as the `timing` step
  times it, by `hyperfine` and by `pyperf command`, in one process and with `--jobs`: each method's
  medians and spread, and hyperfine's instruction counts.
- `timed_tail_trial.py [CORPUS ...] [--runs N] [--jobs N] [--cpus-each N]`: corpora timed as the
  `timing` step times them with no warm-up, each alone and then all at once on disjoint CPU sets
  (`taskset`): each way's runs, spread and first-run effect, and the side-by-side medians against the
  alone ones.
- `timing_noise.py FOLDER FOLDER`: two corpus runs' timing tables side by side, each corpus's change
  in seconds and instructions and the medians of them: the run-to-run noise a timing change has to
  clear.
- `worker_start.py [ROOT ...] [--jobs N] [--runs N]`: a `--jobs` check of one-line files, mostly its
  workers' start, as `python -m constricter` and as the `constricter` script, against `--jobs=1`, by
  `hyperfine`, for each checkout given.
- `module_outline.py PATH [--group NAME ...]`: a module's top-level definitions, each one's lines
  and which of the module's names it reads and is read by; with `--group`, what moves with those
  names and what outside them reads one. For choosing a split.
- `split_module.py SOURCE NEW DOCSTRING_FILE NAME ...`: move top-level definitions to a new module
  (or, with `-` for DOCSTRING_FILE, to one already there), making public what crosses the cut and
  importing it, refusing an import cycle; `--as` names a public name, `--ignore` a dependency given
  by hand. Prints the references elsewhere to fix.
- `retarget_imports.py OLD NEW NAME ...`: each `from OLD import ...` of a moved name, split to
  import it from NEW; a use through the module printed.
- `move_modules.py OLD.PACKAGE NEW.PACKAGE MODULE[=NEWNAME] ...`: `git mv` modules into a
  subpackage and retarget every import and dotted mention of them; path forms in pyproject.toml and
  the docs printed for a hand edit.
- `tables_unchanged.py`: the standard-library tables this checkout's generator writes, compared with
  `constricter/fix/tables/`, byte for byte (`source.json`'s stamp left out).
- `mypyc_trial.py [--opt 0] [--exclude PATH ...] [-- PYTEST_ARGS]`, with `local/.venv-mypyc`: a copy
  of `constricter` compiled as the compiled wheel is, quickly (a C file a module, every CPU), and
  the tests run against it.
- `compile_time.py [--python 3.12] [--fresh] [VARIANT ...]`: the compiled wheel's build from the
  sdist, timed, as it is (`single`), with `multi_file` and with `parallel` C compiles; `CC=clang`
  in the environment times clang's.
- `run_timeline.py FOLDER [--top N] [--every MINUTES]`: a corpus run's timeline from its records:
  the share of the machine's CPU seconds used, the CPUs busy and the steps running in each bucket,
  the longest steps and how long each waited, and the corpora that ended last.
- `rerun_census.py FOLDER`: a corpus run's fixed test runs that weren't the released tests': each
  one's counts, what was new or gone, whether it was calm, how many times it ran again and the
  samples the run had of the released tests. For checking what the `tests` step ran again, and why.
- `run_eta.py FOLDER REFERENCE [--err FILE]`: where a running corpus run is and when it should end,
  each step done weighted by the seconds the same step took in a finished run.
- `run_tick.sh HH:MM NAME.err NAME.out [SECONDS]`: wait for a run's next update mark, its end, a new
  `problem:` line or a cap, for a session's timed updates.
- `outside_size.py [CORPUS] [--top N]`: what a check knows of each file from outside it, by its
  pickled size: the total, the median, the largest files, and the fields that hold the most.
- `second_round.py [CORPUS ...]`: a check's second rounds, where a file is checked again knowing its
  parameters, timed against the first checks in one process, and split into their rounds and what
  follows them over the whole module.
- `compiled_compare.py SITE TREE ... [--runs N] [--jobs N] [--fix]`: a tree checked (or fixed) by
  this checkout and by a compiled wheel's install, their output compared and timed.
- `corpus_quadrants.py FOLDER ...`: each corpus's files and its steps' wall and CPU seconds in
  finished runs, and its size-and-time group at the medians.
- `schedule_sim.py FOLDER... [--cpus N] [--memory GB] [--given] [--sweep]`: finished runs' steps
  replayed under other queueing orders, beside each run's length and the least any schedule could
  take; `--sweep` searches the runner's order, `_PATIENCE` and `_BESIDE` for the fastest over them
  all.
- `compiled_venv.py`: builds the pure wheel and the compiled one (mypyc), each installed in a venv
  of its own beside the `corpus` group's packages (`local/.venv-pure`, `local/.venv-compiled`), for
  `tests/corpus/runs/compiled.toml`.
- `version_diff.py FOLDER [A B]`: two versions' findings and fixes in one run, corpus by corpus, and
  how much faster one is.
- `order_edges.py CORPUS` (with the corpus's `VIRTUAL_ENV`): the check order's edges by a method's
  name alone (`loose.needs`), against those only a class the file names (or a base of it in its
  module) gives, and none: each graph's edges, largest component and longest chain, in files and
  bytes.
- `schedule_solve.py FOLDER... [--given] [--seconds N] [--staged [--pauses SECONDS]]`: the shortest
  schedule of finished runs' steps by OR-Tools' CP-SAT, and the least it proves any can take;
  `--staged` holds the runner's stages one after another, as a run in stages does.
- `mutation.py [--children N] [--only PATTERN ...] [--keep]`: mutmut over `constricter/` on a
  worktree of HEAD under `local/mutation/`, the unit tests run for each mutant, the survivors
  written to `local/mutation/survivors-<date>.txt`. Hours of every CPU for a full pass; outside the
  sandbox (its workers fork).
- `peak_phases.py PATH [--no-index-trees] [--trace-check] [--trim] [-- OPTIONS]`, from the checkout: a
  one-process check's memory over time by phase (the index, its settling, each check round), with
  the index keeping no trees, what the first round still holds as it ends (tracemalloc), or, with
  `--trim` under `PYTHONMALLOC=malloc`, glibc's `malloc_trim` after each file's check.
- `stage_compare.py BEFORE AFTER [--stage tests] [--top N]`: one stage's steps in two runs, from
  their records: its wall time, step seconds, CPU seconds and waits, each corpus's seconds in both,
  and the steps whose seconds or waits changed most.
- `righttyper_measure.py CHECKOUT --source PKG (--module pytest | --script PATH) [--args "..."]
[--check "basedpyright PKG"]`: RightTyper over a suite's tests on a copy of its checkout, only the
  signatures it adds taken (`righttyper_added.py`), then `--fix` and the check on a plain copy and
  on that one: the fixes each got and the errors. Outside the sandbox.
- `righttyper_added.py ORIGINAL ANNOTATED OUT`: of RightTyper's rewritten source, only the
  parameter and return annotations the original lacked, with the imports they need under
  `TYPE_CHECKING`, onto the original's text: its signatures measured without its overwrites.
- `dmypy_suggest.py [CORPUS ...] [--sample N] [--daemons K]`: `dmypy suggest`'s signatures for a
  sample of each corpus's unannotated functions, written into a copy by daemons that start while the
  memory holds them, and `--fix`'s fixes and basedpyright's errors on it against a plain copy's. It
  counts `# type:` comments as no annotation, and writes mypy's `module:Name` spellings as given.
- `hint_errors.py FOLDER [--step STEP] [--corpus NAME] [--samples N]`: the new type errors a corpus
  run's hinted fixes caused, by step, corpus, checker code and fix kind, and the distinct blamed
  fixes by code with samples; every error as JSON lines for grouping by hand.
- `rebound_shapes.py FOLDER`: a run's `rebound` guesses by two shapes of the later binding (a loop's
  target bound again past the loop; a `None` filled in an `if` testing the name), each shape's
  guesses, errors and witness verdicts: a rule's cost before writing it.
- `rebound_census.py REPORT.json ROOT`: a tree's `rebound` guesses from a `--format=json` report,
  counted by whether an augmented assignment binds the name again later, each one listed.
- `widen_census.py [CORPUS ...]`: what `fix-widen` writes on a corpus as docs/FIXES.md reports it
  (the calls' kinds alone, every kind, every kind but the calls'): the bindings each kind marks, the
  share typed or widened after, a second pass's changes, and basedpyright's errors before and after,
  by rule.
- `pythons_suite.sh VENVS 3.11:dev 3.14t:test [-- PYTEST_ARGS]`: the test suite on other Pythons,
  each in a venv of its own under VENVS set up as CI's setup action sets one up, one process at low
  priority; each run's output in `VENVS/venv-VERSION.log`.
