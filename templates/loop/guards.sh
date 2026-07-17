#!/bin/bash
# guards.sh — loop guardrails as code. Source this from every loop entrypoint:
#
#   source "$(dirname "$0")/guards.sh"
#
# Lesson from val26 (July 2026): hooks, tool lists and model instructions are
# configuration, not enforcement. The ONLY thing that held was guards in code.
# This file is that code. See README.md in this directory for the guard
# catalog and the exit-code contract.
#
# Conventions:
# - Functions RETURN the contract codes below; callers decide task vs run fate.
#   Callers using `set -e` must call gates as: `if ! budget_gate 25; then ...`
# - Semantic codes (BUDGET/FAILCLOSED/SCOPE/TAMPER) must NEVER be treated as
#   retryable. retry_transient enforces this.

# ── Exit-code contract ────────────────────────────────────────
LOOP_EXIT_OK=0          # done / gate passed
LOOP_EXIT_BUDGET=3      # budget or wall-clock cap reached (semantic — never retry)
LOOP_EXIT_FAILCLOSED=4  # a guard could not measure (semantic — never retry)
LOOP_EXIT_TRANSIENT=5   # transient failure / usage limit (retryable with backoff)
LOOP_EXIT_SCOPE=6       # scope conflict escalation (semantic — never retry)
LOOP_EXIT_TAMPER=7      # git tamper detected & self-healed (2 per task => fail task)

# ── Environment pins ──────────────────────────────────────────
# Mandatory in all loop scripts: without it, large WebFetch calls trigger a
# 1M-context auto-upgrade that requires usage credits and 429s the run.
export CLAUDE_CODE_DISABLE_1M_CONTEXT=1

# ── Paths ─────────────────────────────────────────────────────
LOOP_GUARDS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOOP_LIB_JS="${LOOP_LIB_JS:-$LOOP_GUARDS_DIR/lib.js}"
LOOP_STATE_FILE="${LOOP_STATE_FILE:-.loop/state.json}"
LOOP_INCIDENT_LOG="${LOOP_INCIDENT_LOG:-.loop/incidents.log}"
export LOOP_STATE_FILE

lib() { node "$LOOP_LIB_JS" "$@"; }

_loop_incident() {
  # ALWAYS log incidents — tamper and escalations are non-fatal but never silent.
  mkdir -p "$(dirname "$LOOP_INCIDENT_LOG")"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOOP_INCIDENT_LOG"
}

# ── Gates ─────────────────────────────────────────────────────

budget_gate() {
  # budget_gate <budgetUsd> — check BEFORE every paid call, never after.
  local rc=0
  lib under-budget "$1" || rc=$?
  case "$rc" in
    0) return 0 ;;
    1) echo "GUARD budget: spent >= \$$1 — stopping." >&2; return "$LOOP_EXIT_BUDGET" ;;
    *) echo "GUARD budget: cannot measure spend — fail-closed." >&2; return "$LOOP_EXIT_FAILCLOSED" ;;
  esac
}

step_budget_gate() {
  # step_budget_gate <spentBeforeStepUsd> <stepCapUsd>
  # Per-step caps that sum to the task cap (val26 LOOP_BACKLOG: uncoordinated
  # caps let step A eat the whole task budget).
  local rc=0
  lib step-under-budget "$1" "$2" || rc=$?
  case "$rc" in
    0) return 0 ;;
    1) echo "GUARD step-budget: step spend >= \$$2 — stopping step." >&2; return "$LOOP_EXIT_BUDGET" ;;
    *) echo "GUARD step-budget: cannot measure — fail-closed." >&2; return "$LOOP_EXIT_FAILCLOSED" ;;
  esac
}

wall_clock_gate() {
  # wall_clock_gate <startEpoch> <maxSeconds>
  local now; now=$(date +%s)
  if (( now - $1 >= $2 )); then
    echo "GUARD wall-clock: ${2}s elapsed — stopping." >&2
    return "$LOOP_EXIT_BUDGET"
  fi
  return 0
}

iteration_gate() {
  # iteration_gate <iteration> <maxIters>
  if (( $1 > $2 )); then
    echo "GUARD iterations: cap $2 reached — stopping." >&2
    return "$LOOP_EXIT_BUDGET"
  fi
  return 0
}

branch_guard() {
  # branch_guard <expectedBranch> — loops never run on the wrong branch.
  local current; current=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || {
    echo "GUARD branch: not a git repo — fail-closed." >&2; return "$LOOP_EXIT_FAILCLOSED"; }
  if [[ "$current" != "$1" ]]; then
    echo "GUARD branch: on '$current', expected '$1' — fail-closed." >&2
    return "$LOOP_EXIT_FAILCLOSED"
  fi
  return 0
}

sandbox_check() {
  # Verified before every iteration that writes: inside a git work tree and
  # the state dir is writable.
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "GUARD sandbox: not inside a git work tree — fail-closed." >&2
    return "$LOOP_EXIT_FAILCLOSED"; }
  local dir; dir=$(dirname "$LOOP_STATE_FILE")
  mkdir -p "$dir" 2>/dev/null && [[ -w "$dir" ]] || {
    echo "GUARD sandbox: state dir '$dir' not writable — fail-closed." >&2
    return "$LOOP_EXIT_FAILCLOSED"; }
  return 0
}

# ── HEAD-guard (git tamper) ───────────────────────────────────
# Workers must never commit. Snapshot HEAD before the worker runs, enforce
# after. On tamper: soft-reset back, ALWAYS log an incident, count it.
# Caller redoes the step; if tamper_exceeded => fail the task (2 strikes).

head_guard_snapshot() { git rev-parse HEAD; }

head_guard_enforce() {
  # head_guard_enforce <expectedSha> <taskKey>
  local expected="$1" task_key="$2" actual count
  actual=$(git rev-parse HEAD)
  [[ "$actual" == "$expected" ]] && return 0
  count=$(lib get "tamper_${task_key}"); count=$(( ${count:-0} + 1 ))
  lib set "tamper_${task_key}=${count}"
  _loop_incident "TAMPER task=${task_key} expected=${expected} actual=${actual} event=${count} — soft-reset + retry"
  git reset --soft "$expected"
  echo "GUARD head: tamper detected (event ${count} for ${task_key}) — self-healed via soft-reset." >&2
  return "$LOOP_EXIT_TAMPER"
}

tamper_exceeded() {
  # tamper_exceeded <taskKey> — exit 0 if >= 2 tamper events for this task.
  local count; count=$(lib get "tamper_$1")
  [[ "${count:-0}" -ge 2 ]]
}

# ── Limit detection (mtime-scoped) ────────────────────────────
limit_detect() {
  # limit_detect <dir> <sinceEpoch> — exit 0 if a file MODIFIED AFTER
  # sinceEpoch mentions a usage/rate limit; exit 1 otherwise.
  # mtime-scoping is mandatory: greping old logs misclassifies semantic
  # stops as limits (val26 incident).
  local dir="$1" since="$2" pattern files
  pattern="${LOOP_LIMIT_PATTERN:-rate.?limit|usage limit|limit reached|too many requests|overloaded|429}"
  files=$(find "$dir" -type f -newermt "@${since}" 2>/dev/null)
  [[ -z "$files" ]] && return 1
  if echo "$files" | tr '\n' '\0' | xargs -0 grep -l -i -E "$pattern" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

# ── Retry (transient ONLY) ────────────────────────────────────
retry_transient() {
  # retry_transient <maxAttempts> <backoffSeconds> <cmd...>
  # Retries ONLY LOOP_EXIT_TRANSIENT (5). Semantic codes (3/4/6/7) and
  # unknown codes are returned immediately — budget/scope/tamper must never
  # be limit-classified.
  local max="$1" backoff="$2"; shift 2
  local attempt rc
  for (( attempt=1; attempt<=max; attempt++ )); do
    rc=0; "$@" || rc=$?
    [[ $rc -eq 0 ]] && return 0
    if [[ $rc -ne "$LOOP_EXIT_TRANSIENT" ]]; then
      echo "GUARD retry: exit $rc is not transient — not retrying." >&2
      return "$rc"
    fi
    if (( attempt < max )); then
      echo "GUARD retry: transient (attempt ${attempt}/${max}) — backoff ${backoff}s." >&2
      sleep "$backoff"
    fi
  done
  echo "GUARD retry: still transient after ${max} attempts." >&2
  return "$LOOP_EXIT_TRANSIENT"
}

# ── Resume guard ──────────────────────────────────────────────
resume_guard() {
  # Resume ONLY a run interrupted by usage limits. Anything else must be a
  # deliberate fresh start — resuming a budget/scope/tamper stop would
  # override a semantic decision.
  local status; status=$(lib get status)
  if [[ "$status" != "usage_interrupted" ]]; then
    echo "GUARD resume: status '${status:-<none>}' is not usage_interrupted — refusing to resume." >&2
    return "$LOOP_EXIT_FAILCLOSED"
  fi
  return 0
}

# ── Detached launch ───────────────────────────────────────────
detached_launch() {
  # detached_launch <script> <logFile> [taskName]
  # Long runs must survive their parent (val26: batch died twice as a child
  # of an interactive session). Windows/Git Bash: schtasks one-shot (parent
  # becomes svchost), fallback `cmd start /b`. Linux/WSL2/cloud: setsid,
  # fallback nohup+disown. Monitor with: tail -f <logFile>
  local script="$1" log="$2" task_name="${3:-loop-detached}"
  mkdir -p "$(dirname "$log")"
  # schtasks only from a real Windows bash (MINGW/MSYS/Cygwin) — WSL2 sees
  # schtasks.exe via interop but pwd -W/cygpath/// are Git Bash-only there.
  case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) local win_bash=1;; *) local win_bash=0;; esac
  if [[ "$win_bash" == 1 ]] && command -v schtasks.exe >/dev/null 2>&1; then
    local repo bash_exe inner
    repo="$(pwd -W 2>/dev/null || pwd)"
    bash_exe="$(cygpath -w "$(command -v bash)" 2>/dev/null || echo 'C:\Program Files\Git\bin\bash.exe')"
    inner="cd '$repo' && bash '$script' >> '$log' 2>&1"
    if schtasks.exe //Create //TN "$task_name" //TR "\"$bash_exe\" -lc \"$inner\"" //SC ONCE //ST 00:00 //F >/dev/null 2>&1 \
       && schtasks.exe //Run //TN "$task_name" >/dev/null 2>&1; then
      echo "detached: schtasks '$task_name' (survives terminal death)"
      return 0
    fi
    cmd.exe //c start //b "" "$bash_exe" -lc "$inner" && {
      echo "detached: cmd start /b (weaker than schtasks)"; return 0; }
    echo "GUARD detach: no Windows method worked — fail-closed." >&2
    return "$LOOP_EXIT_FAILCLOSED"
  elif command -v setsid >/dev/null 2>&1; then
    setsid bash "$script" >> "$log" 2>&1 < /dev/null &
    echo "detached: setsid pid $!"
    return 0
  else
    nohup bash "$script" >> "$log" 2>&1 < /dev/null &
    disown
    echo "detached: nohup+disown pid $!"
    return 0
  fi
}
