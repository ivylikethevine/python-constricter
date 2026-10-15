# Scratch

One-off scripts that measured something once and may be worth running again. None is linted, typed
or tested; delete any freely. Each says in its docstring what it does and how to run it, from the
repository's root with `local/.venv/bin/python -m scratch.NAME`, outside a sandbox. What they write
goes under `local/scratch/`.

- `guess_report.py --from FOLDER`, a corpus run's folder with its `guesses.jsonl`: every guess the
  run made on the suites, by mechanism, with the type errors blamed on it and what its binding held
  at run time. `guess_report.py --likely` lists the sets that pass `docs/LIKELY.md`'s bars.
- `suite_memory.py`: one suite's released tests, once for each set of extra arguments, with the
  seconds, the CPU seconds and the most memory each run's processes held.
- `widen_pass.py`: what a second pass still fixes on each corpus after every `fix-widen` kind.
- `widen_suites.py`: each suite's tests as released and after every `fix-widen` kind.
- `widen_one.py`: one suite's tests after every `fix-widen` kind, their output and the diff kept.
- `typeshed_client_compare.py [MODULE ...]`, with `typeshed-client` on `PYTHONPATH`: where
  `stdlib_tables.stubs` and `typeshed-client` read a stub differently, for every module and
  configuration: whether it exists, its names, their kinds and exports, its `__all__`.
- `witness_checkers.py`, with `typeguard` and `beartype` on `PYTHONPATH`: values held to annotations
  by the witness's `holds`, typeguard and beartype, where each differs from a type checker, whether
  it runs the value's own code, and what each costs.
- `threads_probe.py DIR [THREADS ...]`: a directory's files checked in one process on each count of
  threads, with the seconds and how many files' findings differ from one thread's; for a
  free-threaded Python (`local/.venv-ft`).
- `timing_trial.py [CORPUS ...] [--runs N] [--jobs N]`: a corpus's check timed as the `timing` step
  times it, by `hyperfine` and by `pyperf command`, in one process and with `--jobs`: each method's
  medians and spread, and hyperfine's instruction counts.
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
- `tables_unchanged.py`: the standard-library tables this checkout's generator writes, compared with
  `constricter/fix/tables/`, byte for byte (`source.json`'s stamp left out).
- `mypyc_trial.py [--opt 0] [--exclude PATH ...] [-- PYTEST_ARGS]`, with `local/.venv-mypyc`: a copy
  of `constricter` compiled as the compiled wheel is, quickly (a C file a module, every CPU), and
  the tests run against it.
- `run_timeline.py FOLDER [--top N] [--every MINUTES]`: a corpus run's timeline from its records:
  the share of the machine's CPU seconds used, the CPUs busy and the steps running in each bucket,
  the longest steps and how long each waited, and the corpora that ended last.
- `compiled_compare.py SITE TREE ... [--runs N] [--jobs N] [--fix]`: a tree checked (or fixed) by
  this checkout and by a compiled wheel's install, their output compared and timed.
