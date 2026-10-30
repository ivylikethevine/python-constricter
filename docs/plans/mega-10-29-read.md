# Read the mega run of 2026-10-29

## Context

`mega-10-29-2026-1139` ran on `f7d53b2` with the 13 items under "Built, waiting on a run" in
`docs/ROADMAP.md`. Only its headline is recorded. New type errors rose from 428 to 562, so an item
can't be recorded as done until the extra 134 are blamed. The run also reported two problems: the
standard library's `fix-certain` leaves 2 bindings for a second pass, and one nibabel test newly
fails after `fix-likely`. This plan reads the run and records what it shows. It does no new run and
no fix. Each fault it finds becomes a numbered finding for the user to pick.

## Steps

1. **Blame the new errors.** Use `scratch/guess_report.py --from corpus-runs/mega-10-29-2026-1139`
   and the same on `corpus-runs/mega-10-28-2026-0826`. Diff the blamed errors by mechanism, step and
   corpus, starting with mcp (+60), pandas (+42) and `constructor` (50 from 28). Name the built item
   behind each group. Read the run's `records/` and `report.json` for the errors the tables don't
   blame.
2. **Read each built item.** For items 1-13, check its own count in this run against what the item
   predicted. Record whether it passes LIKELY.md's bars where it is a guess, and its new errors.
   Each item goes to COMPLETED.md or stays with what's left, as the file's convention does.
3. **The two problems.**
   - Standard library: find the 2 bindings in the run's `fix-certain` second-pass record, and the
     mechanism that leaves them.
   - nibabel: find the test from the tests table under `tables/` and the fix on the lines it covers.
4. **Record as it goes.** Replace the headline block under "Built, waiting on a run" with the read.
   Faults become Small items, or findings in the reply.

## Files

- `docs/ROADMAP.md` and `docs/COMPLETED.md`, edited.
- `corpus-runs/mega-10-29-2026-1139/` and `corpus-runs/mega-10-28-2026-0826/`, read only.
- Scripts reused: `scratch/guess_report.py`, and `scratch/fixes_diff.py` where a fix's text is
  needed. A new comparison script goes in `scratch/` with a docstring.

## Verification

- prettier and markdownlint on the two docs.
- Every count is reproduced from the run folder by a command given in the record.
- No corpus run, suite or sync. If confirming a cause needs a run, give the user the command.
