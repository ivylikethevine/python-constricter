#!/usr/bin/env bash
# The test suite on other Pythons, each in a venv of its own under VENVS, set up as CI's setup action
# sets one up (`uv sync --frozen --no-install-project --no-build --only-group GROUP`, then an editable
# install with no build isolation), one process at low priority. Never touches `.venv` or `local/.venv`.
#
#   scratch/pythons_suite.sh VENVS 3.11:dev 3.14t:test [-- PYTEST_ARGS...]
#
# A Python is a version uv finds (`uv python find`); GROUP is the dependency group CI's job installs
# (`dev`, or `test` where not every dev tool has a wheel). Each run's output goes to VENVS/NAME.log;
# the last lines are printed. Exits non-zero if any suite failed. Run from the repository's root.
set -u
venvs=$1
shift
specs=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do
  specs+=("$1")
  shift
done
[ "${1:-}" = "--" ] && shift
status=0
for spec in "${specs[@]}"; do
  version=${spec%%:*}
  group=${spec#*:}
  venv="$venvs/venv-$version"
  python=$(uv python find "$version") || {
    echo "== $version: no such Python"
    status=1
    continue
  }
  echo "== $version ($group): $python"
  UV_PROJECT_ENVIRONMENT=$venv nice -n 19 uv sync --frozen --no-install-project --no-build \
    --only-group "$group" --python "$python" --quiet || {
    status=1
    continue
  }
  nice -n 19 uv pip install --quiet --python "$venv" --no-deps --no-build-isolation -e . || {
    status=1
    continue
  }
  SETUPTOOLS_USE_DISTUTILS=stdlib nice -n 19 "$venv/bin/python" -m pytest -q -p no:xdist \
    "$@" >"$venvs/venv-$version.log" 2>&1 || status=1
  tail -n 3 "$venvs/venv-$version.log"
done
exit $status
