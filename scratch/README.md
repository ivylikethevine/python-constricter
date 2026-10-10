# Scratch

One-off scripts that measured something once and may be worth running again. None is linted, typed
or tested; delete any freely. Each says in its docstring what it does and how to run it, from the
repository's root with `local/.venv/bin/python -m scratch.NAME`, outside a sandbox. What they write
goes under `local/scratch/`.

- `guess_census.py`, then `guess_report.py`: every guess the last super and mega corpora runs made
  on the suites, by mechanism, with the type errors blamed on it and what its binding held at run
  time. `guess_report.py --likely` lists the sets that pass `docs/LIKELY.md`'s bars.
- `widen_pass.py`: what a second pass still fixes on each corpus after every `fix-widen` kind.
- `widen_suites.py`: each suite's tests as released and after every `fix-widen` kind.
- `widen_one.py`: one suite's tests after every `fix-widen` kind, their output and the diff kept.
