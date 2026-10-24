#!/usr/bin/env bash
# Write a check's and `--fix` diffs' outputs on the standard library, pydantic and pandas into OUT, to
# compare two trees byte for byte (`cmp`) after a change meant to keep every output the same.
#
#   bash scratch/equivalence.sh OUT [JOBS=0]
#
# Run from the checkout whose `constricter` is to be measured: `python -m` imports the working
# directory's package first. pandas is checked in its suite's environment (`VIRTUAL_ENV`).
set -eu
out=$1 jobs=${2:-0}
root=$(pwd)
py=/workspace/personal/python-constricter/local/.venv/bin/python
lib="/workspace/personal/python-constricter/local/corpus-sources/standard library-3.14.7/Python-3.14.7/Lib"
pydantic=/workspace/personal/python-constricter/local/corpus-suites/pydantic-v2.14.0/pydantic
pandas=/workspace/personal/python-constricter/local/corpus-suites/pandas-v3.0.6/pandas
pandas_env=/workspace/personal/python-constricter/local/corpus-suites/pandas-v3.0.6/.venv
mkdir -p "$out"
check=(-m constricter "--jobs=$jobs" --level=suffocate --all-scopes --exit-zero --format=json --show-fixes)
# The standard library exits 2 whatever `--exit-zero` says: its tests have files that don't parse.
"$py" "${check[@]}" "$lib" >"$out/stdlib.json" 2>"$out/stdlib.err" || [ $? -eq 2 ]
"$py" "${check[@]}" "$pydantic" >"$out/pydantic.json"
"$py" -m constricter "--jobs=$jobs" --unsafe-fixes --extend-select LVA013 --format=json --show-fixes --exit-zero "$pydantic" >"$out/pydantic-unsafe.json"
VIRTUAL_ENV=$pandas_env "$py" "${check[@]}" "$pandas" >"$out/pandas.json"
echo "written to $out from $root"
