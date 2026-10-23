# shellcheck shell=bash
# This repo's half of ./check_tool_versions.sh, which sources it before any
# section runs (its header has the contract). Not run on its own.

# Pins written inline, one row each:
#   name|file-glob|sed-BRE-with-one-\(capture\)|check|tag-prefix
#
# actionlint, gitleaks, lychee  the release URL each workflow hands
#                               ./.github/actions/tool; its sha256 moves with it
# uv                            setup-uv's `version:` input, in the setup action
#                               and in the published action.yml - the action's
#                               SHA does not cover the binary it downloads
# shellcheck disable=SC2034 # read by check_tool_versions.sh
CI_WORKFLOW_ROSTER='actionlint|.github/workflows/*.yml|/rhysd/actionlint/releases/download/v\([0-9][0-9.]*\)/|github:rhysd/actionlint|
gitleaks|.github/workflows/*.yml|/gitleaks/gitleaks/releases/download/v\([0-9][0-9.]*\)/|github:gitleaks/gitleaks|
lychee|.github/workflows/*.yml|/lycheeverse/lychee/releases/download/lychee-v\([0-9][0-9.]*\)/|github:lycheeverse/lychee|lychee-v
uv (setup action)|.github/actions/setup/action.yml| version: "\([0-9][0-9.]*\)"|github:astral-sh/uv|
uv (action.yml)|action.yml| version: "\([0-9][0-9.]*\)"|github:astral-sh/uv|'

# No image is pinned here.
# shellcheck disable=SC2034 # read by check_tool_versions.sh
CI_IMAGE_GLOBS=''

# The Markdown tools' npm manifest and uv.lock's direct dependencies. django is
# held to its major: pyproject.toml's corpus group says why.
# shellcheck disable=SC2034 # read by check_tool_versions.sh
CI_MANIFESTS='npm|.github/package.json
uv|uv.lock|django@major'
