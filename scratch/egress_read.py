"""Compare a workflow job's `allowed-endpoints` with the hosts harden-runner saw it call, from its log.

  local/.venv/bin/python -m scratch.egress_read RUN:JOB [RUN:JOB ...]

For each job of a finished run (`gh pr checks` lists their URLs), reads `gh run view --job --log`:
harden-runner's agent logs each `endpoint called` at the job's end. Prints, for the job, the hosts
allowed and called, allowed and not called (each a candidate to drop, on this one run's evidence), and
called and not allowed (blocked, or the agent's own). Needs a read token; `XDG_CACHE_HOME` must be
writable, gh caching the logs there.
"""

import re
import subprocess
import sys

_ALLOWED = re.compile(r"allowed-endpoints: (.*)$", re.MULTILINE)
_CALLED = re.compile(r"endpoint called ip address:port \S+, domain: (\S+?)\.?, ")
_NAME = re.compile(r"^(.*?)\t", re.MULTILINE)


def main() -> int:
    for pair in sys.argv[1:]:
        run, job = pair.split(":")
        log = subprocess.run(
            ["gh", "run", "view", run, "--job", job, "--log"], capture_output=True, text=True, check=True
        ).stdout
        name = _NAME.match(log)
        found = _ALLOWED.search(log)
        allowed = {each.removesuffix(":443") for each in found.group(1).split()} if found else set()
        called = set(_CALLED.findall(log))
        print(f"{name.group(1) if name else job}:")
        print(f"  allowed, called:     {sorted(allowed & called)}")
        print(f"  allowed, not called: {sorted(allowed - called)}")
        print(f"  called, not allowed: {sorted(called - allowed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
