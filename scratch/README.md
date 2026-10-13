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
