Run this from /claude/python-constricter in your own shell:

sh -c 'local/.venv/bin/python -m tests.corpus.mega_corpora 2>&1 >local/runs/mega-0.3.6-run2.out | tee local/runs/mega-0.3.6-run2.err; echo "finished $(date +%H:%M)" | tee -a local/runs/mega-0.3.6-run2.err'

- Progress: one line per finished step (mcp: tests: done, ... in 35s), about 400 in all, then a line for each thing a fix broke, then finished HH:MM.
- It will list failures at the end. black's formatting test differs after any fix, so that much is expected.
- Expect over an hour. Every traceable suite now runs its tests once more under the witness.
- Don't edit constricter/ or tests/corpus/ while it runs. The steps import the working tree, and a change starts a new run.
- If it stops, the same command resumes it.

A later session can read the results from:

- local/runs/mega-0.3.6-run2.err: the progress log and what broke.
- docs/RUNS.md: the ## Mega corpora section, rewritten in place.
- local/mega-corpora/0.3.6-<stamp>/: every step's kept result, which scratch/guess_census.py and scratch/guess_report.py read without re-running anything.


