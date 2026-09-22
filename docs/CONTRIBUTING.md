# Contributing

Bug reports and rule ideas go in an issue; vulnerabilities go through [SECURITY.md](SECURITY.md).

For a pull request, set up the environment and run the checks from the README's
[Development](../README.md#development) section: every one must pass, coverage stays at 100%, and
the project's own code passes `constricter --level=suffocate --all-scopes`. Keep changes small and
docs short, add tests for new behaviour, and note user-facing changes in
[CHANGELOG.md](CHANGELOG.md).

When bumping the version for a release, record it in [RUNS.md](RUNS.md): run
`tests/corpus_table.py --versions dev --write` (with the `corpus` group installed), which appends
this checkout's results under the new version, and commit it with the bump.
