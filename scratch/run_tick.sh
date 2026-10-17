#!/bin/sh
# SPDX-License-Identifier: MIT
# Wait for a corpus run's next update mark, its end, or a new problem, whichever comes first.
#
#   scratch/run_tick.sh HH:MM local/runs/NAME.err local/runs/NAME.out [MAX_SECONDS]
#
# Exits 0 printing `mark` at HH:MM (today, local time), `ended` once the .out file has content (the
# runner lists its outputs only when it finishes; the sandbox's PID namespace hides the process),
# `died` when the .err file gains a `Traceback`, `problem` when it gains a `problem:` line, or `cap`
# after MAX_SECONDS (default 570, under a Bash tool call's 10-minute limit). For a mark over the cap
# away, relaunch on `cap`.
mark=$1
err=$2
out=$3
cap=${4:-570}
target=$(date -d "today $mark" +%s)
start=$(date +%s)
problems=$(grep -c "^problem:" "$err" 2>/dev/null); problems=${problems:-0}
while :; do
    now=$(date +%s)
    if [ "$now" -ge "$target" ]; then echo mark; exit 0; fi
    if [ $((now - start)) -ge "$cap" ]; then echo cap; exit 0; fi
    if [ -s "$out" ]; then echo ended; exit 0; fi
    if grep -q '^Traceback' "$err" 2>/dev/null; then echo died; exit 0; fi
    count=$(grep -c "^problem:" "$err" 2>/dev/null); count=${count:-0}
    if [ "$count" -gt "$problems" ]; then echo problem; exit 0; fi
    sleep 20
done
