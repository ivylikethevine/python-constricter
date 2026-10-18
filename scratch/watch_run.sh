#!/usr/bin/env bash
# Wait on a corpus run until the next N-minute mark, a new failed step, or its report, then print
# its progress. For timed updates from a background call that must end within 10 minutes.
#
#   bash scratch/watch_run.sh RUN_FOLDER STDERR_LOG [MINUTES=10] [FAILURES_SEEN=0] [SINCE=0]
#
# SINCE: a `--resume`'s start (seconds since the epoch), so the stopped run's own `report.md` is no end.
#
# Exits 0 at the mark, 1 on a failure beyond FAILURES_SEEN, 2 once `report.md` is written, printing
# the closing summary's failed, problem and note lines.
set -u
run=$1 err=$2 every=${3:-10} seen=${4:-0} since=${5:-0}
now=$(date +%s)
mark=$(((now / (every * 60) + 1) * every * 60))
status=0 why=mark
while :; do
  if [ -e "$run/report.md" ] && [ "$(stat -c %Y "$run/report.md")" -ge "$since" ]; then
    status=2 why=done
    break
  fi
  failed=$(grep -E -c '(: [^:]* failed: |s, failed \(|: not found: )' "$err" 2>/dev/null)
  if [ "${failed:-0}" -gt "$seen" ]; then
    status=1 why=failed
    break
  fi
  [ "$(date +%s)" -ge "$mark" ] && break
  sleep 15
done
echo "why: $why at $(date +%H:%M)"
echo "steps finished: $(grep -c '^[^ ]* on .*: .*s, .* CPU seconds' "$err")"
echo "records: $(find "$run/records" -name '*.json' 2>/dev/null | wc -l)"
echo "failed: $(grep -E -c '(: [^:]* failed: |s, failed \(|: not found: )' "$err")"
grep -E '(: [^:]* failed: |s, failed \(|: not found: )' "$err" | tail -5
echo "queue: $(tail -1 "$run/queue.log" 2>/dev/null)"
echo "running for: $((($(date +%s) - $(stat -c %Y "$run/run.toml")) / 60)) minutes"
[ "$why" = done ] && grep -E "^(failed|problem|note): " "$err" | cut -c1-200
exit $status
