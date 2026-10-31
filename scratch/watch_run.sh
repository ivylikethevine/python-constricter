#!/usr/bin/env bash
# Wait on a corpus run until its next update mark, a new failure or problem, or its report, then
# print its progress. For timed updates from a background call that must end within 10 minutes.
#
#   bash scratch/watch_run.sh RUN_FOLDER STDERR_LOG [MARK=10] [FAILURES_SEEN=0] [SINCE=0] [CAP=570]
#
# MARK: the next N-minute mark, or HH:MM in local time (tomorrow's, once over 12 hours gone).
# SINCE: a `--resume`'s start (seconds since the epoch), so the stopped run's own `report.md` is no end.
# CAP: the seconds to wait at most, under a Bash tool call's limit; for a mark further off, relaunch.
#
# Exits 0 at the mark or the cap, 1 on a failure beyond FAILURES_SEEN, a `Traceback` or a new `problem:`
# line, 2 once `report.md` is written, printing the closing summary's failed, problem and note lines.
set -u
run=$1 err=$2 mark=${3:-10} seen=${4:-0} since=${5:-0} cap=${6:-570}
start=$(date +%s)
case $mark in
*:*)
  target=$(date -d "today $mark" +%s)
  [ "$target" -lt $((start - 43200)) ] && target=$((target + 86400))
  ;;
*) target=$(((start / (mark * 60) + 1) * mark * 60)) ;;
esac
problems=$(grep -c '^problem:' "$err" 2>/dev/null)
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
  if grep -q '^Traceback' "$err" 2>/dev/null; then
    status=1 why=died
    break
  fi
  count=$(grep -c '^problem:' "$err" 2>/dev/null)
  if [ "${count:-0}" -gt "${problems:-0}" ]; then
    status=1 why=problem
    break
  fi
  now=$(date +%s)
  [ "$now" -ge "$target" ] && break
  if [ $((now - start)) -ge "$cap" ]; then
    why=cap
    break
  fi
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
